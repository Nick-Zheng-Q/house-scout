#!/usr/bin/env python3
"""Read-only, low-volume public-location geocoding, walking, POI and VBB queries.

No API keys; no Nominatim default; no browser automation. See routing-guide.md.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = 'HouseScoutManualResearch/1.0 (small user-directed public-location queries)'
SERVICES = {'photon': 'https://photon.komoot.io',
            'foot': 'https://routing.openstreetmap.de',
            'overpass': 'https://overpass-api.de',
            'vbb': 'https://v6.vbb.transport.rest'}


def coordinate(value):
    try:
        lat, lon = map(float, value.split(','))
    except (ValueError, AttributeError):
        raise ValueError('coordinate must be WGS84 latitude,longitude') from None
    if not all(map(math.isfinite, (lat, lon))) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('WGS84 coordinate out of range')
    return lat, lon


def aware_time(value):
    try:
        date = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('arrival must be ISO8601 with an explicit UTC offset') from None
    if date.tzinfo is None or date.utcoffset() is None:
        raise ValueError('arrival needs the location timezone offset, not a naive time')
    return date


def great_circle(a, b):
    x, y = map(math.radians, a); u, v = map(math.radians, b)
    h = math.sin((u-x)/2)**2 + math.cos(x)*math.cos(u)*math.sin((v-y)/2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(h)))


def request_url(command, **values):
    if command == 'geocode':
        q = values['query'].strip()
        if not q or len(q) > 300:
            raise ValueError('query must be 1..300 characters')
        params = {'q': q, 'limit': 5}
        if values.get('tag'): params['osm_tag'] = values['tag']
        return 'photon', SERVICES['photon']+'/api/?'+urllib.parse.urlencode(params)
    start = coordinate(values['origin'])
    if command == 'pois':
        radius = int(values.get('radius', 600))
        if not 50 <= radius <= 1200:
            raise ValueError('POI radius must be 50..1200m; do not scrape a city')
        around = f'around:{radius},{start[0]},{start[1]}'
        query = ('[out:json][timeout:15];('
                 f'nwr({around})["shop"~"^(supermarket|convenience|mall)$"];'
                 f'nwr({around})["amenity"="pharmacy"];);out center meta;')
        return 'overpass', SERVICES['overpass']+'/api/interpreter?'+urllib.parse.urlencode({'data': query})
    end = coordinate(values['destination'])
    if command == 'walk':
        coords = f'{start[1]},{start[0]};{end[1]},{end[0]}'
        return 'foot', SERVICES['foot']+'/routed-foot/route/v1/foot/'+coords+'?steps=true&overview=false'
    if command == 'vbb':
        arrival = aware_time(values['arrival'])
        params = {'from.latitude':start[0], 'from.longitude':start[1], 'from.address':values.get('origin_label', 'public origin'),
                  'to.latitude':end[0], 'to.longitude':end[1], 'to.address':values.get('destination_label', 'public destination'),
                  'arrival':arrival.isoformat(), 'results':2, 'stopovers':'false', 'remarks':'true'}
        return 'vbb', SERVICES['vbb']+'/journeys?'+urllib.parse.urlencode(params)
    raise ValueError('unsupported command')


def fetch_json(service, url, cache_dir, timeout=35):
    """Cache successes for one hour; one shared lock and >=1.2s between requests.

    No auto retries or endpoint rotation on a denial. Failures are not cached.
    """
    directory = Path(cache_dir); directory.mkdir(parents=True, exist_ok=True)
    path = directory/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    import fcntl  # macOS/Linux; unsupported hosts fail rather than parallelizing.
    lock_dir = Path(tempfile.gettempdir())/'house-scout-public-services'
    lock_dir.mkdir(exist_ok=True)
    with (lock_dir/'request.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists() and time.time()-path.stat().st_mtime < 3600:
            cached = json.loads(path.read_text()); cached['cache_hit'] = True
            return cached
        stamp = lock_dir/'last-request'
        if stamp.exists():
            try: delay = 1.2-(time.time()-float(stamp.read_text()))
            except ValueError: delay = 1.2
            if delay > 0: time.sleep(delay)
        stamp.write_text(str(time.time()))
        request = urllib.request.Request(url, headers={'User-Agent':USER_AGENT, 'Accept':'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                final = response.geturl()
                if (urllib.parse.urlsplit(final).scheme != 'https' or
                    urllib.parse.urlsplit(final).hostname != urllib.parse.urlsplit(SERVICES[service]).hostname):
                    raise ValueError('unexpected redirect; inspect it, do not continue automatically')
                payload = response.read(4_000_001)
                if len(payload) > 4_000_000: raise ValueError('response too large; narrow the query')
                data = json.loads(payload)
        except urllib.error.HTTPError as error:
            raise ValueError(f'HTTP {error.code}; Retry-After={error.headers.get("Retry-After", "not supplied")}; do not evade rate/access limits') from None
        record = {'service':service, 'request_url':url,
                  'fetched_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                  'cache_hit':False, 'response':data}
        temp = path.with_suffix(f'.{os.getpid()}.tmp');temp.write_text(json.dumps(record,ensure_ascii=False));temp.replace(path)
        return record


def summarize(command, data, **values):
    attribution = {'data':'© OpenStreetMap contributors (ODbL)',
                   'attribution_url':'https://www.openstreetmap.org/copyright',
                   'fix_map_url':'https://www.openstreetmap.org/'}
    if command == 'geocode':
        features=[]
        for item in data.get('features', []):
            props=item.get('properties', {}); coords=item.get('geometry', {}).get('coordinates', [])
            features.append({'properties':props, 'longitude_latitude':coords,
                             'selection':'candidate_only; verify full address, city/country and object type'})
        return {'candidates':features, 'automatically_selected':False, 'attribution':attribution}
    if command == 'walk':
        if data.get('code') != 'Ok' or not data.get('routes'):
            raise ValueError('no usable pedestrian route returned')
        route=data['routes'][0]
        seconds=float(route['duration']);distance=float(route['distance'])
        if not math.isfinite(seconds) or not math.isfinite(distance) or seconds < 0 or distance < 0:
            raise ValueError('invalid route metrics')
        return {'mode':'walking', 'route_distance_m':distance, 'model_minutes':round(seconds/60,2),
                'time_scope':'untimed pedestrian-network model; not a submitted weekday/arrival-time itinerary',
                'ticket_fare':0, 'fare_scope':'walking ticket only; no paid-transit fallback or other household trips',
                'waypoints':[{k:w.get(k) for k in ['location','name','distance']} for w in data.get('waypoints', [])],
                'legs':[{'distance':leg.get('distance'),'duration':leg.get('duration'),'summary':leg.get('summary'),
                         'steps':[{'name':step.get('name'),'distance':step.get('distance'),'duration':step.get('duration'),
                                   'maneuver':step.get('maneuver',{}).get('type')} for step in leg.get('steps',[])]}
                        for leg in route.get('legs', [])],
                'limitations':['Check snapped endpoints and entrance precision; model excludes indoor access, signals and live closures.',
                               'Not proof of a step-free/safe route; query return separately.'], 'attribution':attribution}
    if command == 'pois':
        start=coordinate(values['origin']);places=[]
        for item in data.get('elements', []):
            tags=item.get('tags', {});name=tags.get('name') or tags.get('brand')
            location=item.get('center', item)
            if not name or 'lat' not in location or 'lon' not in location:continue
            places.append({'name':name,'tags':tags,'latitude':location['lat'],'longitude':location['lon'],
                           'osm_url':f'https://www.openstreetmap.org/{item["type"]}/{item["id"]}',
                           'osm_edit_timestamp':item.get('timestamp'),
                           'straight_line_m_for_sort_only':round(great_circle(start,(location['lat'],location['lon']))),
                           'access_time_minutes':None,
                           'evidence':'mapped POI; verify on business locator and query pedestrian route separately'})
        return {'places':sorted(places,key=lambda p:p['straight_line_m_for_sort_only'])[:20], 'attribution':attribution}
    journeys=[];target=aware_time(values['arrival'])
    for item in data.get('journeys', []):
        legs=item.get('legs', [])
        if not legs:continue
        departure=legs[0].get('departure') or legs[0].get('plannedDeparture')
        arrival=legs[-1].get('arrival') or legs[-1].get('plannedArrival')
        duration=None;matches=False
        if departure and arrival:
            first=aware_time(departure);last=aware_time(arrival)
            duration=round((last-first).total_seconds()/60,2)
            local=last.astimezone(target.tzinfo)
            matches=local.date()==target.date() and local<=target and duration>=0
        journeys.append({'departure':departure,'arrival':arrival,'duration_minutes':duration,
                         'requested_arrival_date_and_deadline_match':matches,
                         'price_as_returned':item.get('price'),
                         'legs':[{k:leg.get(k) for k in ['origin','destination','departure','arrival','walking','distance','line','remarks']} for leg in legs]})
    return {'provider':'v6.vbb.transport.rest, community wrapper of VBB data, not official VBB service',
            'requested_arrival':target.isoformat(),'journeys':journeys,
            'fare_scope':'Use only returned route/rider price or separately verified VBB fare rules; absent price is unknown.',
            'limitations':['Only Berlin/Brandenburg coverage. Check all access legs, alerts, returned date/time and fares.',
                           'Timetable prediction is not a live punctuality guarantee.']}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-locations',action='store_true',help='acknowledge public test locations / authorized disclosure only and provider policies')
    parser.add_argument('--cache-dir',default=str(Path(tempfile.gettempdir())/'house-scout-route-cache'))
    parser.add_argument('--output',type=Path,help='save raw response, request URL and summary as JSON')
    sub=parser.add_subparsers(dest='command',required=True)
    geo=sub.add_parser('geocode');geo.add_argument('query');geo.add_argument('--tag')
    pois=sub.add_parser('pois');pois.add_argument('--origin',required=True);pois.add_argument('--radius',type=int,default=600)
    for name in ['walk','vbb']:
        command=sub.add_parser(name);command.add_argument('--origin',required=True);command.add_argument('--destination',required=True)
        if name=='vbb':
            command.add_argument('--arrival',required=True);command.add_argument('--origin-label',default='public origin');command.add_argument('--destination-label',default='public destination')
    args=parser.parse_args(argv);values=vars(args).copy();command=values.pop('command')
    if not args.public_locations:parser.error('read provider policies in routing-guide; --public-locations required. Never transmit private locations without authorization.')
    result={'ok':False};record={};url=None
    try:
        service,url=request_url(command,**values)
        record=fetch_json(service,url,args.cache_dir)
        result={**record,'ok':True,'summary':summarize(command,record['response'],**values)}
    except (ValueError,urllib.error.URLError,OSError,json.JSONDecodeError) as error:
        result={**record,'ok':False,'command':command,'request_url':url,'error':str(error),
                'guidance':'DNS/network sandbox failure needs approved network execution; 401/403/429 needs permission/key/backoff, never evasion.'}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='response'},ensure_ascii=False,indent=2))
    return 0 if result['ok'] else 2


if __name__=='__main__':raise SystemExit(main())
