#!/usr/bin/env python3
"""Small public-transport queries: Munich MVV planner or MBTA dated stop pairs.

Use transit-guide; not a global provider or automatic door/fare verification.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import urllib.parse
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parent))
import query_routes as net

net.SERVICES.update(mvv='https://efa.mvv-muenchen.de',mbta='https://api-v3.mbta.com')


def local_target(value, zone):
    t=net.aware_time(value);local=t.astimezone(ZoneInfo(zone))
    if local.utcoffset()!=t.utcoffset():raise ValueError('arrival offset does not match provider timezone on that date')
    return local


def request_url(provider, **v):
    if provider=='mvv':
        t=local_target(v['arrival'],'Europe/Berlin');a=net.coordinate(v['origin']);b=net.coordinate(v['destination'])
        q={'outputFormat':'JSON','language':'en','stateless':1,'coordOutputFormat':'WGS84[DD.ddddd]',
           'type_origin':'coord','name_origin':f'{a[1]}:{a[0]}:WGS84[DD.ddddd]',
           'type_destination':'coord','name_destination':f'{b[1]}:{b[0]}:WGS84[DD.ddddd]',
           'itdDate':t.strftime('%Y%m%d'),'itdTime':t.strftime('%H%M'),'itdTripDateTimeDepArr':'arr','calcNumberOfTrips':2,'useRealtime':0}
        return net.SERVICES['mvv']+'/ng/XML_TRIP_REQUEST2?'+urllib.parse.urlencode(q)
    t=local_target(v['arrival'],'America/New_York');start=t-dt.timedelta(minutes=90)
    if start.date()!=t.date():raise ValueError('MBTA lookup window crosses midnight; use local GTFS service-day lookup instead')
    q={'filter[date]':t.date().isoformat(),'filter[stop]':v['from_stop']+','+v['to_stop'],'filter[route]':v['route'],
       'filter[direction_id]':v['direction'],'filter[min_time]':start.strftime('%H:%M'),'filter[max_time]':t.strftime('%H:%M'),
       'page[limit]':100,'include':'trip,stop','sort':'departure_time'}
    return net.SERVICES['mbta']+'/schedules?'+urllib.parse.urlencode(q)


def efa_time(point):
    x=point['dateTime'];value=x['date']+' '+(x.get('timeSec') or x['time']+':00')
    return dt.datetime.strptime(value,'%d.%m.%Y %H:%M:%S').replace(tzinfo=ZoneInfo('Europe/Berlin'))


def summarize_mvv(data, arrival):
    target=local_target(arrival,'Europe/Berlin');trips=[]
    for trip in data.get('trips',[]):
        legs=[]
        for raw in trip.get('legs',[]):
            points=raw.get('points',[])
            if len(points)<2:raise ValueError('incomplete MVV leg endpoints')
            a,b=points[0],points[-1];first,last=efa_time(a),efa_time(b);mode=raw.get('mode',{})
            walking=str(mode.get('type'))=='100'
            kind='walk' if walking else ('transit' if str(mode.get('type')) in {str(x) for x in range(11)} else 'other_or_unrecognized')
            legs.append({'origin':a,'destination':b,'departure':first.isoformat(),'arrival':last.isoformat(),
                         'walking':walking,'travel_kind':kind,'mode':mode,'minutes':round((last-first).total_seconds()/60,2),
                         'reported_transfer_footpath':raw.get('footpath'),'hints':raw.get('hints'),'infos':raw.get('infos')})
        if not legs:continue
        first=dt.datetime.fromisoformat(legs[0]['departure']);last=dt.datetime.fromisoformat(legs[-1]['arrival'])
        chronological=all(x['minutes']>=0 for x in legs) and all(dt.datetime.fromisoformat(b['departure'])>=dt.datetime.fromisoformat(a['arrival']) for a,b in zip(legs,legs[1:]))
        transit=any(x['travel_kind']=='transit' for x in legs)
        trips.append({'departure':first.isoformat(),'arrival':last.isoformat(),'duration_minutes':round((last-first).total_seconds()/60,2),
            'requested_date_and_deadline_match':last.date()==target.date() and last<=target and chronological and transit,
            'contains_transit':transit,'chronologically_connected':chronological,'interchanges_as_returned':trip.get('interchange'),
            'fare_as_returned':trip.get('itdFare'),'legs':legs})
    return {'provider':'MVV public web EFA planner, normal /ng endpoint; interface may change',
       'requested_arrival':target.isoformat(),'returned_date_range':data.get('dateTime'),'origin_as_resolved':data.get('origin'),
       'destination_as_resolved':data.get('destination'),'messages_as_returned':data.get('itdMessageList'),'trips':trips,
       'limitations':['Check all resolved points, platforms, messages and fare products; matching clock does not survey apartment doors.',
          'Scheduled predictions, not punctuality guarantees. Out-of-deadline alternatives stay visible but are not accepted.',
          'Raw distance is omitted from summary because its field scope is not established.']}


def summarize_mbta(data, arrival, from_stop, to_stop):
    target=local_target(arrival,'America/New_York');included={(x['type'],x['id']):x for x in data.get('included',[])}
    def belongs(stop,requested):
        if stop==requested:return True
        return (included.get(('stop',stop),{}).get('relationships',{}).get('parent_station',{}).get('data') or {}).get('id')==requested
    grouped={}
    for row in data.get('data',[]):
        rel=row['relationships'];tid=rel['trip']['data']['id'];grouped.setdefault(tid,[]).append(row)
    trips=[]
    for tid,events in grouped.items():
        for a in events:
            ar=a['relationships'];aa=a['attributes']
            if not belongs(ar['stop']['data']['id'],from_stop) or aa.get('pickup_type',0)!=0:continue
            for b in events:
                br=b['relationships'];ba=b['attributes']
                if not belongs(br['stop']['data']['id'],to_stop) or ba.get('drop_off_type',0)!=0:continue
                if ba['stop_sequence']<=aa['stop_sequence'] or not aa.get('departure_time') or not ba.get('arrival_time'):continue
                first=net.aware_time(aa['departure_time']);last=net.aware_time(ba['arrival_time'])
                trips.append({'trip_id':tid,'route_id':ar['route']['data']['id'],'departure':first.isoformat(),'arrival':last.isoformat(),
                   'requested_date_and_deadline_match':first<=last<=target and last.astimezone(target.tzinfo).date()==target.date(),
                   'ride_minutes':round((last-first).total_seconds()/60,2),'interchanges':0,
                   'publisher_estimated_stop_times':not aa.get('timepoint',True) or not ba.get('timepoint',True),
                   'board_schedule':a,'alight_schedule':b,'trip_as_returned':included.get(('trip',tid))})
    trips.sort(key=lambda x:x['departure'],reverse=True)
    return {'provider':'MBTA official V3 schedules, direct stop-pair lookup','requested_arrival':target.isoformat(),'trips':trips,
       'response_complete':not bool(data.get('links',{}).get('next')),'next_page_as_returned':data.get('links',{}).get('next'),
       'fare':None,'door_to_door_complete':False,
       'limitations':['Stop-pair published schedules, not a home-to-destination planner, live prediction or fare quote.',
         'Incomplete pagination is explicit; never claim latest/optimal trip from a truncated response.',
         'Match official fare, access/egress, platforms, service alerts and return separately.']}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--public-locations',action='store_true');p.add_argument('--output',type=Path)
    p.add_argument('--cache-dir',type=Path,default=Path(net.tempfile.gettempdir())/'house-scout-route-cache',help='response cache directory; use a fresh isolated directory for independent evaluations (global service pacing still shared)')
    sub=p.add_subparsers(dest='provider',required=True)
    m=sub.add_parser('mvv');m.add_argument('--origin',required=True);m.add_argument('--destination',required=True);m.add_argument('--arrival',required=True)
    b=sub.add_parser('mbta');b.add_argument('--from-stop',required=True);b.add_argument('--to-stop',required=True);b.add_argument('--route',required=True);b.add_argument('--direction',choices=['0','1'],required=True);b.add_argument('--arrival',required=True)
    a=p.parse_args(argv)
    if not a.public_locations:p.error('public test locations / authorized disclosure required; read transit-guide and routing-guide policies')
    v=vars(a);result={};url=None
    try:
        url=request_url(a.provider,**{k:x for k,x in v.items() if k!='provider'})
        record=net.fetch_json(a.provider,url,a.cache_dir)
        summary=summarize_mvv(record['response'],a.arrival) if a.provider=='mvv' else summarize_mbta(record['response'],a.arrival,a.from_stop,a.to_stop)
        result={**record,'ok':True,'summary':summary}
    except (ValueError,OSError,KeyError,TypeError,net.urllib.error.URLError) as e:result={'ok':False,'request_url':url,'error':str(e),'guidance':'Do not evade401/403/429. Missing/empty results do not validate transit.'}
    out=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(out)
    print(json.dumps({k:v for k,v in result.items() if k!='response'},ensure_ascii=False,indent=2));return 0 if result['ok'] else 2

if __name__=='__main__':raise SystemExit(main())
