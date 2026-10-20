# Rental cost checker input

Run `python3 scripts/check_rentals.py input.json --pretty`. This checks entered arithmetic and hard-condition states only; it does **not** verify the listing, source, authority, or fee completeness. Use one currency and convert recurring costs to the user's monthly usage basis.

```json
{
  "currency": "CNY",
  "hard_requirements": ["pets allowed", "November move-in"],
  "budgets": {"monthly_max": 6000, "upfront_plus_deposit_max": 12000, "signing_cash_max": 18000},
  "candidates": [{
    "id": "listing-123",
    "required_costs_complete": false,
    "signing_costs_complete": false,
    "conditions": {"pets allowed": "unknown", "November move-in": "met"},
    "costs": [
      {"name": "rent", "kind": "recurring", "amount": 5000, "signing_amount": 10000},
      {"name": "utilities", "kind": "recurring", "amount": null, "signing_amount": 0},
      {"name": "agent fee", "kind": "upfront", "amount": 2500, "signing_amount": 2500},
      {"name": "deposit", "kind": "deposit", "amount": 5000, "signing_amount": 5000}
    ]
  }]
}
```

`kind` is `recurring` (monthly), `upfront` (nonrefundable initial) or `deposit` (refundable). `amount` is a nonnegative unit amount; use `null` for unknown and optional `quantity` (default 1). `required:false` is excluded from base totals; do not enter a possible discount as a negative charge. Hard states: `met`, `unmet`, `unknown`, `conflict`; omitted hard requirements are unknown. Any unmet ⇒ `reject`; otherwise unknown/conflict ⇒ `verify`; all met ⇒ `pass`. Carry the same evidenced hard-condition states from the written comparison into `conditions`; do not leave the object empty “to be conservative” when the current advertised offer already has a known failure. A possible future renegotiation does not erase the current failure; record it as a separate conditional offer.

Set `required_costs_complete` true **only with evidence** that all necessary charges are covered. Each of the three kinds needs a required row, including explicit zero if none. Known amounts above a cap can be `over`; lower amounts with missing charges or incomplete scope remain `unknown`. `upfront_plus_deposit_max` **excludes prepaid rent** and is not signing cash.

`signing_amount` is the total **actually due at signing** for that item, not a unit rate times `quantity`; two prepaid months of 5000 rent means 10000. Enter explicit 0 if confirmed not due then; omit/use null if unknown. Set `signing_costs_complete` true only when all necessary signing charges and timing are evidenced. The script is not a purchase calculator.


`known_refundable_deposit` is the script's deposit-category subtotal, not a guarantee of full recovery. If the offer discloses fixed deductions, Japanese shikibiki/amortization or conditional retention, separately record the deposit payable, known deductions and whether the recoverable portion is established. The script does not model deductions; do not present the original deposit as confirmed recoverable cash.
