import importlib.util
import unittest
from pathlib import Path
import urllib.parse
import tempfile
from unittest.mock import patch
import contextlib
import io

SPEC=importlib.util.spec_from_file_location('query_transit',Path(__file__).resolve().parents[1]/'scripts/query_transit.py')
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)

class TransitQueryTests(unittest.TestCase):
    def efa(self,arrival='08:55:00',day='01.12.2026',walking=False):
        return {'trips':[{'interchange':'0','itdFare':{'fareAdult':'4.20'},'legs':[{'points':[{'name':'start','dateTime':{'date':day,'timeSec':'08:30:00'}},{'name':'end','dateTime':{'date':day,'timeSec':arrival}}],'mode':{'type':'100' if walking else '1','name':'U3'}}]}],'itdMessageList':[{'warning':'keep'}]}
    def test_efa_endpoint_coordinate_order_and_arriveby(self):
        u=m.request_url('mvv',origin='48.1,11.5',destination='48.2,11.6',arrival='2026-12-01T09:00:00+01:00');p=urllib.parse.parse_qs(urllib.parse.urlsplit(u).query)
        self.assertIn('/ng/XML_TRIP_REQUEST2?',u);self.assertEqual(p['name_origin'],['11.5:48.1:WGS84[DD.ddddd]']);self.assertEqual(p['itdTripDateTimeDepArr'],['arr'])
    def test_efa_checks_actual_returned_deadline_and_date(self):
        for clock,day,expected in [('08:55:00','01.12.2026',True),('09:01:30','01.12.2026',False),('08:55:00','30.11.2026',False)]:
            with self.subTest(clock=clock,day=day):self.assertEqual(m.summarize_mvv(self.efa(clock,day),'2026-12-01T09:00:00+01:00')['trips'][0]['requested_date_and_deadline_match'],expected)
    def test_walk_only_response_is_never_transit_pass(self):
        r=m.summarize_mvv(self.efa(walking=True),'2026-12-01T09:00:00+01:00');self.assertFalse(r['trips'][0]['requested_date_and_deadline_match'])
    def test_nonwalking_unknown_or_car_mode_is_not_transit(self):
        d=self.efa();d['trips'][0]['legs'][0]['mode']['type']='105';r=m.summarize_mvv(d,'2026-12-01T09:00:00+01:00');self.assertFalse(r['trips'][0]['contains_transit']);self.assertFalse(r['trips'][0]['requested_date_and_deadline_match'])
    def test_fares_messages_and_endpoints_preserved(self):
        r=m.summarize_mvv(self.efa(),'2026-12-01T09:00:00+01:00');self.assertEqual(r['messages_as_returned'],[{'warning':'keep'}]);self.assertEqual(r['trips'][0]['fare_as_returned']['fareAdult'],'4.20')
    def test_timezone_offset_mismatch_rejected(self):
        with self.assertRaises(ValueError):m.local_target('2026-12-01T09:00:00+02:00','Europe/Berlin')
    def mbta(self):
        def row(stop,seq,clock,trip):return {'type':'schedule','id':stop,'attributes':{'departure_time':f'2026-12-01T{clock}-05:00','arrival_time':f'2026-12-01T{clock}-05:00','stop_sequence':seq,'pickup_type':0,'drop_off_type':0,'timepoint':False},'relationships':{'trip':{'data':{'id':trip}},'route':{'data':{'id':'Red'}},'stop':{'data':{'id':stop}}}}
        return {'data':[row('a',1,'08:40:00','t'),row('b',2,'08:50:00','t')],'links':{}}
    def test_mbta_same_trip_only_and_no_invented_fare_or_doors(self):
        d=self.mbta();r=m.summarize_mbta(d,'2026-12-01T09:00:00-05:00','a','b');self.assertEqual(len(r['trips']),1);self.assertTrue(r['trips'][0]['publisher_estimated_stop_times']);self.assertIsNone(r['fare']);self.assertFalse(r['door_to_door_complete'])
        d['data'][1]['relationships']['trip']['data']['id']='other';self.assertEqual(m.summarize_mbta(d,'2026-12-01T09:00:00-05:00','a','b')['trips'],[])
    def test_mbta_pickup_and_partial_pagination_not_hidden(self):
        d=self.mbta();d['links']['next']='https://api-v3.mbta.com/schedules?page[offset]=100';r=m.summarize_mbta(d,'2026-12-01T09:00:00-05:00','a','b');self.assertFalse(r['response_complete']);d['data'][0]['attributes']['pickup_type']=1;self.assertEqual(m.summarize_mbta(d,'2026-12-01T09:00:00-05:00','a','b')['trips'],[])
    def test_cli_isolated_cache_is_forwarded_without_changing_global_pacing(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(m.net, 'fetch_json', return_value={'response': self.mbta(), 'cache_hit': False}) as fetch:
                with contextlib.redirect_stdout(io.StringIO()):
                    code=m.main(['--public-locations','--cache-dir',directory,'mbta','--from-stop','a','--to-stop','b','--route','Red','--direction','0','--arrival','2026-12-01T09:00:00-05:00'])
                self.assertEqual(code,0)
                self.assertEqual(fetch.call_args.args[2],Path(directory))

    def test_mbta_null_parent_does_not_become_unrelated_parent(self):
        d=self.mbta();d['included']=[{'type':'stop','id':'a','relationships':{'parent_station':{'data':None}}}];self.assertEqual(m.summarize_mbta(d,'2026-12-01T09:00:00-05:00','parent','b')['trips'],[])

if __name__=='__main__':unittest.main()
