# Commute cost checker input

`python3 scripts/check_commutes.py input.json --pretty` checks routes **already researched and entered**. It does not query maps, infer fares, select the fastest route, or prove reliability. For each unit, query from the building entrance to each destination at the specified weekday/weekend and arrival/departure time; record route link, source and date in the candidate record. Enter one planned mode per destination for each candidate; narrate alternatives separately rather than summing them.

```json
{
  "currency": "CNY",
  "transport_monthly_max": 500,
  "destinations": [
    {"id": "office-a", "visits_per_month": 20},
    {"id": "office-b", "visits_per_month": 12}
  ],
  "candidates": [{"id": "north-unit-805", "routes": [
    {"destination": "office-a", "mode": "metro", "outbound_minutes": 47,
     "return_minutes": null, "outbound_cost": 5, "return_cost": null,
     "extra_monthly_cost": 0, "cost_scope_confirmed": false},
    {"destination": "office-b", "mode": "bus", "outbound_minutes": 38,
     "return_minutes": null, "outbound_cost": 3, "return_cost": null,
     "extra_monthly_cost": 0, "cost_scope_confirmed": false}
  ]}]
}
```

Per-route monthly cost = `visits_per_month × (outbound_cost + return_cost) + extra_monthly_cost`; the example provides outbound fares only, so its known subtotal is `20×5+12×3=136`, with total cost unknown. **Only if return fares are separately confirmed as 5 and 3 and all relevant charges are covered**, the round-trip scenario becomes `20×(5+5)+12×(3+3)=272`. Amounts and minutes must be nonnegative. Unknown ⇒ `null` or omitted; confirmed no extra monthly charge ⇒ explicit `0`. `cost_scope_confirmed` should be true only when necessary fare, transfer, pass, parking, toll and energy components relevant to that mode are covered. Dynamic ride-hail prices are query-time estimates. A known subtotal above budget is `over`; otherwise missing routes/charges or incomplete scope stay `unknown`.

Return routes and fares may differ; never assume symmetry. A morning-only query can support its own outbound door-to-door time, but return time remains unknown—do not double one-way minutes. Add housing and travel monthly figures only on the same currency, occupancy and trip-count basis, and only as a **known subtotal** while any necessary cost is missing. Confirm whether the user's budget includes travel. This script does not calculate mortgage or tax.
