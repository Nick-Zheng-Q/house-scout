import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "normalize_costs", Path(__file__).resolve().parents[1] / "scripts/normalize_costs.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class NormalizeCostsTests(unittest.TestCase):
    def run_costs(self, costs):
        return module.normalize({"currency": "AUD", "costs": costs})

    def test_australia_weekly_with_unknown_electricity(self):
        result = self.run_costs([
            {"name": "rent", "amount": 650, "period": "week"},
            {"name": "internet", "amount": 60, "period": "month"},
            {"name": "electricity", "amount": None, "period": "quarter"},
        ])
        self.assertEqual(result["costs"][0]["monthly_equivalent"], 2816.67)
        self.assertEqual(result["known_monthly_subtotal"], 2876.67)
        self.assertEqual(result["unknown_costs"], ["electricity"])
        self.assertEqual(result["entered_amounts_status"], "unknown")
        self.assertEqual(result["necessary_cost_scope"], "not_verified")

    def test_all_supported_periods(self):
        for period, amount, expected in [
            ("week", 600, 2600), ("fortnight", 1200, 2600),
            ("month", 2600, 2600), ("quarter", 7800, 2600),
            ("year", 31200, 2600),
        ]:
            with self.subTest(period=period):
                result = self.run_costs([{"name": "rent", "amount": amount, "period": period}])
                self.assertEqual(result["known_monthly_subtotal"], expected)

    def test_sum_before_rounding(self):
        result = self.run_costs([
            {"name": str(i), "amount": "0.01", "period": "week"} for i in range(3)
        ])
        self.assertEqual(result["known_monthly_subtotal"], 0.13)

    def test_zero_is_known_but_missing_amount_is_unknown(self):
        result = self.run_costs([
            {"name": "confirmed free internet", "amount": 0, "period": "month"},
            {"name": "unknown water", "period": "month"},
        ])
        self.assertEqual(result["unknown_costs"], ["unknown water"])
        self.assertEqual(result["costs"][0]["monthly_equivalent"], 0)

    def test_reject_invalid_amount_period_and_currency(self):
        for amount in [-1, True, "NaN", float("inf"), "bad", "1e100", {}]:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.run_costs([{"name": "rent", "amount": amount, "period": "week"}])
        for period in [None, "day", "upfront", "deposit", []]:
            with self.subTest(period=period), self.assertRaises(ValueError):
                self.run_costs([{"name": "rent", "amount": 1, "period": period}])
        with self.assertRaises(ValueError):
            self.run_costs([{"name": "rent", "amount": 1, "period": "week", "currency": "USD"}])

    def test_known_rows_do_not_assert_complete_housing_scope(self):
        result = self.run_costs([{"name": "rent", "amount": 1000, "period": "month"}])
        self.assertEqual(result["entered_amounts_status"], "known_for_entered_rows")
        self.assertEqual(result["necessary_cost_scope"], "not_verified")

    def test_reject_bad_input_and_duplicate_names(self):
        for data in [[], {}, {"currency": "aud", "costs": [{}]},
                     {"currency": "AUD", "costs": []},
                     {"currency": "AUD", "costs": ["bad"]}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                module.normalize(data)
        with self.assertRaises(ValueError):
            self.run_costs([{"name": "same", "period": "month"}] * 2)


if __name__ == "__main__":
    unittest.main()
