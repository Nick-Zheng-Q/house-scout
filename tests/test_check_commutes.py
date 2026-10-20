import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "check_commutes", Path(__file__).resolve().parents[1] / "scripts" / "check_commutes.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CheckCommutesTests(unittest.TestCase):
    def test_confirmed_return_fare_scenario_cost_272(self):
        data = {"transport_monthly_max": 300,
                "destinations": [{"id": "office-a", "visits_per_month": 20},
                                 {"id": "office-b", "visits_per_month": 12}],
                "candidates": [{"id": "north-805", "routes": [
                    {"destination": "office-a", "mode": "metro", "outbound_minutes": 47,
                     "outbound_cost": 5, "return_cost": 5, "extra_monthly_cost": 0,
                     "cost_scope_confirmed": True},
                    {"destination": "office-b", "mode": "bus", "outbound_minutes": 38,
                     "outbound_cost": 3, "return_cost": 3, "extra_monthly_cost": 0,
                     "cost_scope_confirmed": True},
                ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly_transport"], 272)
        self.assertEqual(row["monthly_budget_status"], "within_confirmed_scope")
        self.assertEqual(row["unknown_time_destinations"], ["office-a", "office-b"])

    def test_case_e_outbound_only_does_not_invent_return_fares(self):
        # Synthetic arithmetic fixture: no dependency on private research results.
        data = {"currency": "CNY", "transport_monthly_max": 500,
                "destinations": [{"id": "office-a", "visits_per_month": 20},
                                 {"id": "hospital-b", "visits_per_month": 12}],
                "candidates": [{"id": "example-unit", "routes": [
                    {"destination": "office-a", "mode": "metro", "outbound_minutes": 47,
                     "outbound_cost": 5, "return_cost": None, "extra_monthly_cost": 0,
                     "cost_scope_confirmed": False},
                    {"destination": "hospital-b", "mode": "bus", "outbound_minutes": 38,
                     "outbound_cost": 3, "return_cost": None, "extra_monthly_cost": 0,
                     "cost_scope_confirmed": False},
                ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly_transport"], 136)
        self.assertEqual(row["monthly_budget_status"], "unknown")
        self.assertEqual(row["unknown_cost_destinations"], ["office-a", "hospital-b"])

    def test_missing_fare_or_route_remains_unknown(self):
        data = {"transport_monthly_max": 300,
                "destinations": [{"id": "work", "visits_per_month": 20},
                                 {"id": "care", "visits_per_month": 5}],
                "candidates": [{"id": "unit", "routes": [
                    {"destination": "work", "mode": "metro", "outbound_cost": 5,
                     "extra_monthly_cost": 0, "cost_scope_confirmed": True},
                ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly_transport"], 100)
        self.assertEqual(row["unknown_cost_destinations"], ["work", "care"])
        self.assertEqual(row["monthly_budget_status"], "unknown")

    def test_known_partial_cost_over_budget_is_over(self):
        data = {"transport_monthly_max": 100,
                "destinations": [{"id": "work", "visits_per_month": 20}],
                "candidates": [{"id": "unit", "routes": [
                    {"destination": "work", "mode": "bus", "outbound_cost": 3,
                     "return_cost": 3, "extra_monthly_cost": None},
                ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly_transport"], 120)
        self.assertEqual(row["monthly_budget_status"], "over")

    def test_duplicate_route_and_invalid_cost_rejected(self):
        base = {"destinations": [{"id": "work", "visits_per_month": 20}],
                "candidates": [{"id": "unit", "routes": [
                    {"destination": "work", "mode": "metro", "outbound_cost": 5},
                    {"destination": "work", "mode": "bus", "outbound_cost": 3},
                ]}]}
        with self.assertRaises(ValueError):
            module.summarize(base)
        base["candidates"][0]["routes"].pop()
        base["candidates"][0]["routes"][0]["outbound_cost"] = -1
        with self.assertRaises(ValueError):
            module.summarize(base)


if __name__ == "__main__":
    unittest.main()
