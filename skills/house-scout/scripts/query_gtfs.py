#!/usr/bin/env python3
"""Find exact direct scheduled trips in a local, authorized GTFS ZIP.

This is a stop-to-stop timetable lookup, NOT a door-to-door journey planner.
No network, guessed headways, interpolated times, transfers or automatic fares.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import zipfile
from zoneinfo import ZoneInfo


def rows(z, name):
    candidates=[n for n in z.namelist() if n.rsplit('/',1)[-1]==name]
    if not candidates:return []
    if len(candidates)!=1:raise ValueError(f'ambiguous GTFS member: {name}')
    member=z.getinfo(candidates[0])
    if member.file_size>1_500_000_000:raise ValueError('GTFS member too large')
    return csv.DictReader(io.TextIOWrapper(z.open(member),encoding='utf-8-sig',newline=''))


def seconds(value):
    h,m,s=map(int,value.split(':'))
    if h<0 or not 0<=m<60 or not 0<=s<60:raise ValueError('invalid GTFS time')
    return h*3600+m*60+s


def services(z, day):
    stamp=day.strftime('%Y%m%d');weekday=day.strftime('%A').lower();active=set()
    for r in rows(z,'calendar.txt'):
        if r['start_date']<=stamp<=r['end_date'] and r.get(weekday)=='1':active.add(r['service_id'])
    for r in rows(z,'calendar_dates.txt'):
        if r['date']==stamp:
            if r['exception_type']=='1':active.add(r['service_id'])
            elif r['exception_type']=='2':active.discard(r['service_id'])
    return active


def lookup(path, from_stop, to_stop, arrival, timezone, window_minutes=120):
    target=dt.datetime.fromisoformat(arrival.replace('Z','+00:00'))
    tz=ZoneInfo(timezone)
    if target.tzinfo is None:raise ValueError('arrival requires an explicit UTC offset')
    if target.utcoffset()!=target.astimezone(tz).utcoffset():raise ValueError('arrival offset does not match agency timezone at that date')
    target=target.astimezone(tz)
    if not 1<=window_minutes<=720:raise ValueError('window must be 1..720 minutes')
    with zipfile.ZipFile(path) as z:
        timezones={r['agency_timezone'] for r in rows(z,'agency.txt')}
        if timezones!={timezone}:raise ValueError('supply the single agency_timezone from this feed; mixed timezones unsupported')
        stops={r['stop_id']:r for r in rows(z,'stops.txt')}
        def expand(s):
            if s not in stops:raise ValueError(f'unknown stop ID: {s}')
            # Parent stations expand only to their actual children; no nearby-stop guess.
            return {s}|{k for k,v in stops.items() if v.get('parent_station')==s}
        origins=expand(from_stop);destinations=expand(to_stop)
        routes={r['route_id']:r for r in rows(z,'routes.txt')}
        if not routes:raise ValueError('GTFS routes.txt is empty; cannot establish transit line identity')
        frequency={r['trip_id'] for r in rows(z,'frequencies.txt')}
        info=list(rows(z,'feed_info.txt'))
        days=[target.date(),target.date()-dt.timedelta(days=1)]
        active={day:services(z,day) for day in days}
        all_active=set().union(*active.values())
        trips={r['trip_id']:r for r in rows(z,'trips.txt') if r['service_id'] in all_active and r['trip_id'] not in frequency}
        selected={}
        for r in rows(z,'stop_times.txt'):
            if r['trip_id'] in trips and r['stop_id'] in origins|destinations:
                selected.setdefault(r['trip_id'],[]).append(r)
        found=[]
        for day in days:
            # GTFS time is elapsed time from local noon minus12h, including DST days.
            base=dt.datetime.combine(day,dt.time(12),tzinfo=tz).timestamp()-43200
            for tid,events in selected.items():
                trip=trips[tid]
                if trip['service_id'] not in active[day]:continue
                for board in events:
                    if board['stop_id'] not in origins or board.get('pickup_type','0') not in ('','0'):continue
                    if not board.get('departure_time'):continue
                    for alight in events:
                        if alight['stop_id'] not in destinations or alight.get('drop_off_type','0') not in ('','0'):continue
                        if int(alight['stop_sequence'])<=int(board['stop_sequence']) or not alight.get('arrival_time'):continue
                        first=dt.datetime.fromtimestamp(base+seconds(board['departure_time']),tz)
                        last=dt.datetime.fromtimestamp(base+seconds(alight['arrival_time']),tz)
                        if last<first or last>target or first<target-dt.timedelta(minutes=window_minutes):continue
                        if first.date()!=target.date():continue  # this CLI's daytime window, no silent prior-evening commute
                        route=routes[trip['route_id']]
                        found.append({'service_date':day.isoformat(),'service_id':trip['service_id'],'trip_id':tid,
                          'route_id':trip['route_id'],'route_short_name':route.get('route_short_name'),'route_long_name':route.get('route_long_name'),
                          'route_type':route.get('route_type'),'headsign':trip.get('trip_headsign'),
                          'origin_stop':stops[board['stop_id']],'destination_stop':stops[alight['stop_id']],
                          'departure':first.isoformat(),'arrival':last.isoformat(),'ride_minutes':round((last-first).total_seconds()/60,2),
                          'board_stop_time':board,'alight_stop_time':alight,'transfers':0,
                          'publisher_estimated_stop_times':any(r.get('timepoint','1')=='0' for r in [board,alight])})
        found.sort(key=lambda r:r['departure'],reverse=True)
    return {'source_kind':'local_gtfs_exact_direct_timetable','feed_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
       'feed_info':info,'agency_timezone':timezone,'requested_arrival':target.isoformat(),
       'active_services_on_requested_date':len(active[target.date()]),'from_stop_id':from_stop,'to_stop_id':to_stop,
       'trips':found[:10],'fare':None,'door_to_door_complete':False,
       'limitations':['Stop-to-stop exact published timetable, not observed punctuality or a door-to-door planner.',
         'No fare, access/egress, platform paths, alerts or transfer planning. Query each transfer leg separately with sourced connector time.',
         'All frequency-based trip templates excluded, including exact_times=1, rather than inventing dated departures.',
         'No result is not proof no service exists; check feed date coverage, selected stop IDs, modes and excluded frequency trips.']}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('zip',type=Path);p.add_argument('--from-stop',required=True);p.add_argument('--to-stop',required=True)
    p.add_argument('--arrival',required=True);p.add_argument('--timezone',required=True);p.add_argument('--window-minutes',type=int,default=120)
    p.add_argument('--output',type=Path)
    a=p.parse_args(argv)
    try:result=lookup(a.zip,a.from_stop,a.to_stop,a.arrival,a.timezone,a.window_minutes)
    except (ValueError,OSError,KeyError,zipfile.BadZipFile) as e:p.error(str(e))
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
    print(text);return 0

if __name__=='__main__':raise SystemExit(main())
