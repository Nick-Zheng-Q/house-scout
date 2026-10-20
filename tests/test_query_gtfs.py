import importlib.util
import io
import csv
import tempfile
import unittest
import zipfile
from pathlib import Path

SPEC=importlib.util.spec_from_file_location('query_gtfs',Path(__file__).resolve().parents[1]/'scripts/query_gtfs.py')
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)

class GtfsLookupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'gtfs.zip'
        self.tables={
          'agency.txt':[{'agency_id':'a','agency_timezone':'America/New_York'}],
          'stops.txt':[{'stop_id':'parent','stop_name':'Parent'},{'stop_id':'x','stop_name':'Start','parent_station':'parent'},{'stop_id':'y','stop_name':'End'}],
          'routes.txt':[{'route_id':'r','route_type':'1','route_short_name':'Red'}],
          'trips.txt':[{'route_id':'r','service_id':'s','trip_id':'t'}],
          'calendar.txt':[{'service_id':'s','start_date':'20261001','end_date':'20261231',**{x:'1' for x in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']}}],
          'stop_times.txt':[{'trip_id':'t','stop_id':'x','stop_sequence':'1','departure_time':'08:30:00','arrival_time':'08:30:00'}, {'trip_id':'t','stop_id':'y','stop_sequence':'2','departure_time':'08:45:00','arrival_time':'08:45:00'}]}
    def tearDown(self):self.tmp.cleanup()
    def run_feed(self,**kw):
        with zipfile.ZipFile(self.path,'w') as z:
            for name,rs in self.tables.items():
                out=io.StringIO();keys=list(dict.fromkeys(k for r in rs for k in r));writer=csv.DictWriter(out,fieldnames=keys);writer.writeheader();writer.writerows(rs);z.writestr(name,out.getvalue())
        return m.lookup(self.path,kw.get('origin','x'),'y',kw.get('arrival','2026-12-01T09:00:00-05:00'),'America/New_York')
    def test_dated_direct_trip_is_not_door_to_door_or_fare(self):
        r=self.run_feed();self.assertEqual(r['trips'][0]['departure'],'2026-12-01T08:30:00-05:00');self.assertEqual(r['trips'][0]['ride_minutes'],15);self.assertFalse(r['door_to_door_complete']);self.assertIsNone(r['fare'])
    def test_parent_expands_only_real_children(self):self.assertEqual(len(self.run_feed(origin='parent')['trips']),1)
    def test_removed_service_is_not_reused(self):
        self.tables['calendar_dates.txt']=[{'service_id':'s','date':'20261201','exception_type':'2'}];self.assertEqual(self.run_feed()['trips'],[])
    def test_added_exception_without_calendar(self):
        del self.tables['calendar.txt'];self.tables['calendar_dates.txt']=[{'service_id':'s','date':'20261201','exception_type':'1'}];self.assertEqual(len(self.run_feed()['trips']),1)
    def test_outside_date_coverage_no_fabricated_trip(self):self.assertEqual(self.run_feed(arrival='2027-01-05T09:00:00-05:00')['trips'],[])
    def test_headway_template_not_exact_departure(self):
        self.tables['frequencies.txt']=[{'trip_id':'t','start_time':'08:00:00','end_time':'09:00:00','headway_secs':'300','exact_times':'0'}];self.assertEqual(self.run_feed()['trips'],[])
    def test_pickup_permission_is_respected(self):
        self.tables['stop_times.txt'][0]['pickup_type']='1';self.assertEqual(self.run_feed()['trips'],[])
    def test_dropoff_permission_is_respected(self):
        self.tables['stop_times.txt'][1]['drop_off_type']='1';self.assertEqual(self.run_feed()['trips'],[])
    def test_reversed_sequence_not_route(self):
        self.tables['stop_times.txt'][1]['stop_sequence']='0';self.assertEqual(self.run_feed()['trips'],[])
    def test_missing_time_not_interpolated(self):
        self.tables['stop_times.txt'][1]['arrival_time']='';self.assertEqual(self.run_feed()['trips'],[])
    def test_previous_service_day_25_hour(self):
        self.tables['stop_times.txt'][0]['departure_time']='25:00:00';self.tables['stop_times.txt'][1]['arrival_time']='25:15:00';r=self.run_feed(arrival='2026-12-01T01:30:00-05:00');self.assertEqual(r['trips'][0]['service_date'],'2026-11-30');self.assertEqual(r['trips'][0]['arrival'],'2026-12-01T01:15:00-05:00')
    def test_offset_mismatch_rejected(self):
        with self.assertRaises(ValueError):self.run_feed(arrival='2026-12-01T09:00:00-04:00')
    def test_publisher_estimated_stop_time_remains_labeled(self):
        self.tables['stop_times.txt'][0]['timepoint']='0';self.assertTrue(self.run_feed()['trips'][0]['publisher_estimated_stop_times'])
    def test_empty_routes_is_not_a_valid_transit_feed(self):
        self.tables['routes.txt']=[]
        with self.assertRaisesRegex(ValueError,'routes.txt is empty'):self.run_feed()
    def test_naive_arrival_rejected(self):
        with self.assertRaises(ValueError):self.run_feed(arrival='2026-12-01T09:00:00')

if __name__=='__main__':unittest.main()
