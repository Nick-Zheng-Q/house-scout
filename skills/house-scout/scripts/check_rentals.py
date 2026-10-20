#!/usr/bin/env python3
"""Summarize known costs and hard-condition status for rental listings."""

import argparse
import json
import math
import sys
from pathlib import Path


KINDS = {"recurring", "upfront", "deposit"}
STATUSES = {"met", "unmet", "unknown", "conflict"}


def number(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{where} must be a non-negative finite number")
    return value


def summarize(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    requirements = data.get("hard_requirements", [])
    if not isinstance(requirements, list) or not all(isinstance(x, str) and x for x in requirements) or len(set(requirements)) != len(requirements):
        raise ValueError("hard_requirements must be a list of unique non-empty strings")
    budgets = data.get("budgets", {})
    if not isinstance(budgets, dict):
        raise ValueError("budgets must be an object")
    for key in ("monthly_max", "upfront_plus_deposit_max", "signing_cash_max"):
        if key in budgets:
            number(budgets[key], f"budgets.{key}")
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    currency = data.get("currency", "CNY")
    if not isinstance(currency, str) or not currency:
        raise ValueError("currency must be a non-empty string")
    result = {"currency": currency, "candidates": []}
    ids = set()
    for i, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise ValueError(f"candidates[{i}] must be an object")
        cid = candidate.get("id")
        if not isinstance(cid, str) or not cid or cid in ids:
            raise ValueError(f"candidates[{i}].id must be a unique non-empty string")
        ids.add(cid)
        conditions = candidate.get("conditions", {})
        if not isinstance(conditions, dict):
            raise ValueError(f"{cid}.conditions must be an object")
        states = {name: conditions.get(name, "unknown") for name in requirements}
        for name, status in states.items():
            if status not in STATUSES:
                raise ValueError(f"{cid}.conditions[{name!r}] has invalid status")
        gate = "reject" if "unmet" in states.values() else "verify" if any(s in {"unknown", "conflict"} for s in states.values()) else "pass"
        costs = candidate.get("costs", [])
        if not isinstance(costs, list):
            raise ValueError(f"{cid}.costs must be a list")
        costs_complete = candidate.get("required_costs_complete", False)
        if not isinstance(costs_complete, bool):
            raise ValueError(f"{cid}.required_costs_complete must be boolean")
        signing_complete = candidate.get("signing_costs_complete", False)
        if not isinstance(signing_complete, bool):
            raise ValueError(f"{cid}.signing_costs_complete must be boolean")
        totals = {kind: 0 for kind in KINDS}
        unknown = {kind: [] for kind in KINDS}
        signing_known = 0
        signing_unknown = []
        required_kinds_seen = set()
        for j, item in enumerate(costs):
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]:
                raise ValueError(f"{cid}.costs[{j}] needs a name")
            kind = item.get("kind")
            if kind not in KINDS:
                raise ValueError(f"{cid}.costs[{j}] has invalid kind")
            required = item.get("required", True)
            if not isinstance(required, bool):
                raise ValueError(f"{cid}.costs[{j}].required must be boolean")
            amount = item.get("amount")
            quantity = number(item.get("quantity", 1), f"{cid}.costs[{j}].quantity")
            if amount is not None:
                number(amount, f"{cid}.costs[{j}].amount")
            signing_amount = item.get("signing_amount")
            if signing_amount is not None:
                number(signing_amount, f"{cid}.costs[{j}].signing_amount")
            if required:
                required_kinds_seen.add(kind)
                if amount is None:
                    unknown[kind].append(item["name"])
                else:
                    totals[kind] += amount * quantity
                if signing_amount is None:
                    signing_unknown.append(item["name"])
                else:
                    signing_known += signing_amount
        # A completeness flag is an assertion by the caller, not evidence that an
        # omitted charge category is zero. Require an explicit zero row instead.
        for kind in KINDS - required_kinds_seen:
            unknown[kind].append(f"no {kind} cost supplied")
            signing_unknown.append(f"no {kind} cost supplied")
        initial_known = totals["upfront"] + totals["deposit"]
        initial_unknown = unknown["upfront"] + unknown["deposit"]

        def budget_status(known, missing, limit):
            if limit is None:
                return "not_set"
            if known > limit:
                return "over"
            return "unknown" if missing or not costs_complete else "within_confirmed_scope"

        result["candidates"].append({
            "id": cid,
            "hard_condition_gate": gate,
            "hard_conditions": states,
            "known_monthly": round(totals["recurring"], 2),
            "known_upfront_nonrefundable": round(totals["upfront"], 2),
            "known_refundable_deposit": round(totals["deposit"], 2),
            "known_upfront_plus_deposit_excluding_first_month": round(initial_known, 2),
            "known_signing_cash": round(signing_known, 2),
            "required_costs_complete": costs_complete,
            "signing_costs_complete": signing_complete,
            "unknown_required_costs": unknown,
            "unknown_signing_cash_items": signing_unknown,
            "monthly_budget_status": budget_status(totals["recurring"], unknown["recurring"], budgets.get("monthly_max")),
            "upfront_budget_status": budget_status(initial_known, initial_unknown, budgets.get("upfront_plus_deposit_max")),
            "signing_cash_budget_status": "not_set" if budgets.get("signing_cash_max") is None else
                "over" if signing_known > budgets["signing_cash_max"] else
                "unknown" if signing_unknown or not signing_complete else "within_confirmed_scope",
        })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        output = summarize(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
