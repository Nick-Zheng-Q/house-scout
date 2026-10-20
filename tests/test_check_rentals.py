import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("check_rentals", Path(__file__).resolve().parents[1] / "scripts" / "check_rentals.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CheckRentalsTests(unittest.TestCase):
    def test_unknown_required_fee_does_not_become_within_budget(self):
        data = {"hard_requirements": ["pets allowed"], "budgets": {"monthly_max": 3000}, "candidates": [{
            "id": "listing", "conditions": {"pets allowed": "met"}, "costs": [
                {"name": "monthly rent", "kind": "recurring", "amount": 2000},
                {"name": "utilities", "kind": "recurring", "amount": None},
            ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly"], 2000)
        self.assertEqual(row["monthly_budget_status"], "unknown")
        self.assertEqual(row["hard_condition_gate"], "pass")

    def test_conflict_requires_verification_and_unmet_rejects(self):
        data = {"hard_requirements": ["move-in date", "pets allowed"], "candidates": [
            {"id": "unit", "conditions": {"move-in date": "conflict", "pets allowed": "met"}},
            {"id": "no-pets-unit", "conditions": {"move-in date": "met", "pets allowed": "unmet"}},
        ]}
        rows = module.summarize(data)["candidates"]
        self.assertEqual([x["hard_condition_gate"] for x in rows], ["verify", "reject"])

    def test_deposit_separate_from_nonrefundable_and_no_discount(self):
        data = {"budgets": {"upfront_plus_deposit_max": 5000}, "candidates": [{"id": "unit", "costs": [
            {"name": "agency fee", "kind": "upfront", "amount": 1000},
            {"name": "deposit", "kind": "deposit", "amount": 5000},
            {"name": "possible rebate", "kind": "recurring", "amount": 1000, "required": False},
        ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_upfront_nonrefundable"], 1000)
        self.assertEqual(row["known_refundable_deposit"], 5000)
        self.assertEqual(row["upfront_budget_status"], "over")
        self.assertEqual(row["known_monthly"], 0)

    def test_missing_hard_condition_is_unknown_and_negative_amount_rejected(self):
        data = {"hard_requirements": ["pets allowed"], "candidates": [{"id": "unit"}]}
        self.assertEqual(module.summarize(data)["candidates"][0]["hard_condition_gate"], "verify")
        data["candidates"][0]["costs"] = [{"name": "rent", "kind": "recurring", "amount": -1}]
        with self.assertRaises(ValueError):
            module.summarize(data)

    def test_no_cost_data_is_not_reported_within_budget(self):
        data = {"budgets": {"monthly_max": 1000, "upfront_plus_deposit_max": 2000}, "candidates": [{"id": "unpriced"}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["monthly_budget_status"], "unknown")
        self.assertEqual(row["upfront_budget_status"], "unknown")

    def test_below_budget_requires_confirmed_cost_scope(self):
        data = {"budgets": {"monthly_max": 4500}, "candidates": [{"id": "apartment", "costs": [
            {"name": "monthly rent", "kind": "recurring", "amount": 3600},
        ]}]}
        self.assertEqual(module.summarize(data)["candidates"][0]["monthly_budget_status"], "unknown")
        data["candidates"][0]["required_costs_complete"] = True
        self.assertEqual(module.summarize(data)["candidates"][0]["monthly_budget_status"], "within_confirmed_scope")

    def test_omitted_upfront_categories_are_not_assumed_zero(self):
        data = {"budgets": {"upfront_plus_deposit_max": 1000}, "candidates": [{
            "id": "listing", "required_costs_complete": True,
            "costs": [{"name": "rent", "kind": "recurring", "amount": 500}],
        }]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["upfront_budget_status"], "unknown")
        data["candidates"][0]["costs"] += [
            {"name": "no agency fee confirmed", "kind": "upfront", "amount": 0},
            {"name": "no deposit confirmed", "kind": "deposit", "amount": 0},
        ]
        self.assertEqual(module.summarize(data)["candidates"][0]["upfront_budget_status"], "within_confirmed_scope")

    def test_free_rent_with_unknown_required_fee_is_not_zero_total(self):
        data = {"budgets": {"monthly_max": 1000}, "candidates": [{
            "id": "approved-free-listing", "required_costs_complete": True,
            "costs": [
                {"name": "rent", "kind": "recurring", "amount": 0},
                {"name": "utilities", "kind": "recurring", "amount": None},
            ],
        }]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly"], 0)
        self.assertEqual(row["monthly_budget_status"], "unknown")

    def test_rejects_non_object_input_and_invalid_currency(self):
        with self.assertRaises(ValueError):
            module.summarize([])
        with self.assertRaises(ValueError):
            module.summarize({"currency": None, "candidates": []})

    def test_signing_cash_includes_prepaid_rent_once(self):
        data = {"budgets": {"monthly_max": 6000, "upfront_plus_deposit_max": 12000, "signing_cash_max": 18000},
                "candidates": [{"id": "listing-123", "required_costs_complete": True, "signing_costs_complete": True,
                                "costs": [
                                    {"name": "rent", "kind": "recurring", "amount": 5000, "signing_amount": 10000},
                                    {"name": "utilities", "kind": "recurring", "amount": 500, "signing_amount": 0},
                                    {"name": "agency fee", "kind": "upfront", "amount": 2500, "signing_amount": 2500},
                                    {"name": "deposit", "kind": "deposit", "amount": 5000, "signing_amount": 5000},
                                ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly"], 5500)
        self.assertEqual(row["known_upfront_plus_deposit_excluding_first_month"], 7500)
        self.assertEqual(row["known_signing_cash"], 17500)
        self.assertEqual(row["signing_cash_budget_status"], "within_confirmed_scope")

    def test_unknown_signing_payment_is_not_treated_as_zero(self):
        data = {"budgets": {"signing_cash_max": 10000}, "candidates": [{
            "id": "unit", "signing_costs_complete": True,
            "costs": [
                {"name": "rent", "kind": "recurring", "amount": 4000},
                {"name": "fee", "kind": "upfront", "amount": 0, "signing_amount": 0},
                {"name": "deposit", "kind": "deposit", "amount": 4000, "signing_amount": 4000},
            ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_signing_cash"], 4000)
        self.assertEqual(row["signing_cash_budget_status"], "unknown")

    def test_case_a_known_signing_cash_exceeds_budget(self):
        data = {"budgets": {"monthly_max": 6200, "signing_cash_max": 18000},
                "candidates": [{"id": "jia-807", "signing_costs_complete": False,
                                "costs": [
                                    {"name": "rent", "kind": "recurring", "amount": 5200, "signing_amount": 10400},
                                    {"name": "property fee", "kind": "recurring", "amount": 300, "signing_amount": None},
                                    {"name": "agency fee", "kind": "upfront", "amount": 2600, "signing_amount": 2600},
                                    {"name": "deposit", "kind": "deposit", "amount": 5200, "signing_amount": 5200},
                                ]}]}
        row = module.summarize(data)["candidates"][0]
        self.assertEqual(row["known_monthly"], 5500)
        self.assertEqual(row["known_signing_cash"], 18200)
        self.assertEqual(row["signing_cash_budget_status"], "over")


if __name__ == "__main__":
    unittest.main()
