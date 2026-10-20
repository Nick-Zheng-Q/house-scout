import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC=importlib.util.spec_from_file_location('query_routes',Path(__file__).resolve().parents[1]/'scripts/query_routes.py')
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)

class RouteQueryTests(unittest.TestCase):
    def test_foot_backend_and_coordinate_order(self):
        service,url=m.request_url('walk',origin='51.5,-0.1',destination='51.6,-0.2')
        self.assertEqual(service,'foot')
        self.assertIn('/routed-foot/route/v1/foot/-0.1,51.5;-0.2,51.6?',url)

    def test_invalid_coordinates_rejected_before_network(self):
        for value in ['100,0','0,190','NaN,1','51.2','x,y']:
            with self.subTest(value=value),self.assertRaises(ValueError):m.coordinate(value)

    def test_geocoder_does_not_choose_first_candidate(self):
        result=m.summarize('geocode',{'features':[{'properties':{'name':'Old Shoreditch Station','osm_value':'building'},'geometry':{'coordinates':[-0.07,51.52]}}]})
        self.assertFalse(result['automatically_selected'])
        self.assertEqual(result['candidates'][0]['properties']['osm_value'],'building')

    def test_walk_metrics_are_untimed_and_zero_is_ticket_only(self):
        result=m.summarize('walk',{'code':'Ok','routes':[{'duration':771.7,'distance':965.1,'legs':[]}],'waypoints':[]})
        self.assertEqual(result['model_minutes'],12.86)
        self.assertIn('untimed',result['time_scope'])
        self.assertEqual(result['ticket_fare'],0)
        self.assertIn('no paid-transit',result['fare_scope'])

    def test_missing_or_invalid_route_fails(self):
        for data in [{'code':'NoRoute'},{'code':'Ok','routes':[]},{'code':'Ok','routes':[{'duration':-1,'distance':4}]}]:
            with self.subTest(data=data),self.assertRaises(ValueError):m.summarize('walk',data)

    def test_pois_have_no_inferred_access_time(self):
        data={'elements':[{'type':'node','id':1,'lat':51.5,'lon':-0.1,'tags':{'name':'Named pharmacy','amenity':'pharmacy'}}]}
        result=m.summarize('pois',data,origin='51.5,-0.1')
        self.assertIsNone(result['places'][0]['access_time_minutes'])
        self.assertEqual(result['places'][0]['straight_line_m_for_sort_only'],0)
        self.assertEqual(result['places'][0]['osm_url'],'https://www.openstreetmap.org/node/1')

    def test_poi_radius_is_bounded(self):
        with self.assertRaises(ValueError):m.request_url('pois',origin='51.5,-0.1',radius=50000)

    def test_timed_plan_needs_explicit_timezone(self):
        with self.assertRaises(ValueError):m.request_url('vbb',origin='52.5,13.4',destination='52.6,13.3',arrival='2026-12-01T09:00:00')
        service,url=m.request_url('vbb',origin='52.5,13.4',destination='52.6,13.3',arrival='2026-12-01T09:00:00+01:00')
        self.assertEqual(service,'vbb');self.assertIn('arrival=2026-12-01T09%3A00%3A00%2B01%3A00',url)

    def test_wrong_date_or_late_arrival_not_accepted(self):
        for arrival,match in [('2026-12-01T08:55:00+01:00',True),('2026-12-01T09:05:00+01:00',False),('2026-11-30T08:55:00+01:00',False)]:
            data={'journeys':[{'legs':[{'departure':arrival[:11]+'08:00:00+01:00','arrival':arrival}]}]}
            result=m.summarize('vbb',data,arrival='2026-12-01T09:00:00+01:00')
            self.assertEqual(result['journeys'][0]['requested_arrival_date_and_deadline_match'],match)
            self.assertIsNone(result['journeys'][0]['price_as_returned'])

    def test_network_error_writes_failure_not_fake_success(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'failure.json'
            with patch.object(m,'fetch_json',side_effect=m.urllib.error.URLError('DNS denied')):
                with patch('builtins.print'):
                    code=m.main(['--public-locations','--output',str(path),'walk','--origin=51.5,-0.1','--destination=51.6,-0.2'])
            import json
            result=json.loads(path.read_text())
            self.assertEqual(code,2);self.assertFalse(result['ok']);self.assertNotIn('summary',result)

if __name__=='__main__':unittest.main()
