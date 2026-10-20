#!/usr/bin/env python3
"""Check entered door-to-door routes and monthly travel costs; do not fetch routes."""

import argparse
import json
import math
import sys
from pathlib import Path


def amount(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{where} must be a non-negative finite number")
    return value


def identifier(value, where):
    if not isinstance(value, str) or not value:
        raise ValueError(f"{where} must be a non-empty string")
    return value


def summarize(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    currency = identifier(data.get("currency", "CNY"), "currency")
    budget = data.get("transport_monthly_max")
    if budget is not None:
        amount(budget, "transport_monthly_max")
    destinations = data.get("destinations")
    if not isinstance(destinations, list) or not destinations:
        raise ValueError("destinations must be a non-empty list")
    visits = {}
    for i, item in enumerate(destinations):
        if not isinstance(item, dict):
            raise ValueError(f"destinations[{i}] must be an object")
        key = identifier(item.get("id"), f"destinations[{i}].id")
        count = item.get("visits_per_month")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"destinations[{i}].visits_per_month must be a non-negative integer")
        if key in visits:
            raise ValueError(f"duplicate destination: {key}")
        visits[key] = count
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    rows = []
    seen_ids = set()
    for i, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise ValueError(f"candidates[{i}] must be an object")
        cid = identifier(candidate.get("id"), f"candidates[{i}].id")
        if cid in seen_ids:
            raise ValueError(f"duplicate candidate: {cid}")
        seen_ids.add(cid)
        routes = candidate.get("routes", [])
        if not isinstance(routes, list):
            raise ValueError(f"{cid}.routes must be a list")
        route_by_destination = {}
        for j, route in enumerate(routes):
            if not isinstance(route, dict):
                raise ValueError(f"{cid}.routes[{j}] must be an object")
            dest = identifier(route.get("destination"), f"{cid}.routes[{j}].destination")
            if dest not in visits or dest in route_by_destination:
                raise ValueError(f"{cid}.routes[{j}] has unknown or duplicate destination")
            identifier(route.get("mode"), f"{cid}.routes[{j}].mode")
            for key in ("outbound_minutes", "return_minutes", "outbound_cost", "return_cost", "extra_monthly_cost"):
                if route.get(key) is not None:
                    amount(route[key], f"{cid}.routes[{j}].{key}")
            complete = route.get("cost_scope_confirmed", False)
            if not isinstance(complete, bool):
                raise ValueError(f"{cid}.routes[{j}].cost_scope_confirmed must be boolean")
            route_by_destination[dest] = route
        total = 0
        unknown_cost = []
        unknown_time = []
        route_rows = []
        for dest, count in visits.items():
            route = route_by_destination.get(dest)
            if route is None:
                unknown_cost.append(dest)
                unknown_time.append(dest)
                route_rows.append({"destination": dest, "status": "missing_route"})
                continue
            components = (route.get("outbound_cost"), route.get("return_cost"), route.get("extra_monthly_cost"))
            known = sum(x or 0 for x in components[:2]) * count + (components[2] or 0)
            total += known
            complete = all(x is not None for x in components) and route.get("cost_scope_confirmed", False)
            if not complete:
                unknown_cost.append(dest)
            if route.get("outbound_minutes") is None or route.get("return_minutes") is None:
                unknown_time.append(dest)
            route_rows.append({
                "destination": dest,
                "mode": route["mode"],
                "visits_per_month": count,
                "outbound_minutes": route.get("outbound_minutes"),
                "return_minutes": route.get("return_minutes"),
                "known_monthly_cost": round(known, 2),
                "cost_status": "known_for_confirmed_scope" if complete else "unknown",
            })
        status = "not_set" if budget is None else "over" if total > budget else (
            "unknown" if unknown_cost else "within_confirmed_scope")
        rows.append({
            "id": cid,
            "routes": route_rows,
            "known_monthly_transport": round(total, 2),
            "unknown_cost_destinations": unknown_cost,
            "unknown_time_destinations": unknown_time,
            "monthly_budget_status": status,
        })
    return {"currency": currency, "candidates": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        output = summarize(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
