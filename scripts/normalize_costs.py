#!/usr/bin/env python3
"""Convert entered recurring costs to monthly budget equivalents, not payment dues."""
import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path


PER_YEAR = {"week": 52, "fortnight": 26, "month": 12, "quarter": 4, "year": 1}


def money(value):
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def normalize(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    currency = data.get("currency")
    if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("currency must be a three-letter uppercase code")
    costs = data.get("costs")
    if not isinstance(costs, list) or not costs:
        raise ValueError("costs must be a nonempty list of recurring charges")
    rows, unknown, names = [], [], set()
    with localcontext() as context:
        context.prec = 50
        total = Decimal(0)
        for row in costs:
            if not isinstance(row, dict):
                raise ValueError("each cost must be an object")
            name = row.get("name")
            if not isinstance(name, str) or not name.strip() or name in names:
                raise ValueError("each cost needs a nonempty unique name")
            names.add(name)
            if row.get("currency", currency) != currency:
                raise ValueError("mixed currencies need separately sourced FX; not supported")
            period = row.get("period")
            if not isinstance(period, str) or period not in PER_YEAR:
                raise ValueError(f"{name}: period must be one of {', '.join(PER_YEAR)}")
            raw = row.get("amount")
            monthly = None
            if raw is None:
                unknown.append(name)
            else:
                if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
                    raise ValueError(f"{name}: amount must be a nonnegative finite number or null")
                try:
                    amount = Decimal(str(raw))
                except InvalidOperation:
                    raise ValueError(f"{name}: invalid amount") from None
                if not amount.is_finite() or amount < 0 or amount > Decimal("1e18"):
                    raise ValueError(f"{name}: amount must be finite and between 0 and 1e18")
                monthly = amount * PER_YEAR[period] / 12
                total += monthly
            rows.append({"name": name, "period": period, "amount": raw,
                         "monthly_equivalent": None if monthly is None else money(monthly)})
        return {"currency": currency, "basis": "52_week_annualized_budget_equivalent",
                "costs": rows, "known_monthly_subtotal": money(total),
                "unknown_costs": unknown,
                "entered_amounts_status": "unknown" if unknown else "known_for_entered_rows",
                "necessary_cost_scope": "not_verified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        result = normalize(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False,
                     indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
