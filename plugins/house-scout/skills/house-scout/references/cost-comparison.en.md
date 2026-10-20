# Comparable costs: periods, upfront cash, transport, and purchase scenarios

Use after selecting the [market](international-markets.en.md) (or [mainland China](platforms.en.md)). Keep currency code, original amount/period, included items, refundability, payment dates, source and date for each figure. Local fee categories are **questions to verify**, not amounts to assume.

## 1. Normalize recurring quotes without changing the payment schedule

For a budget comparison on an explicitly stated **52-week annualized basis**:

| Quoted period | Monthly equivalent |
| --- | --- |
| week / pw | amount × 52 ÷ 12 |
| fortnight / two weeks | amount × 26 ÷ 12 |
| month / pcm | amount |
| quarter | amount × 4 ÷ 12 |
| year | amount ÷ 12 |

This is a comparison convention, not a legal calendar-day accrual method. Actual leases can bill by calendar dates, have 53 weekly due dates in a selected interval, use specific prorating rules, or renew at another rate. Never use this conversion to invent the cash due on a particular signing date. Daily or irregular quotes need actual dates and contract rules; do not assume 30 days/month.

`python3 scripts/normalize_costs.py input.json --pretty` converts entered recurring rows using the table. It rejects missing periods, negative/nonfinite amounts and mixed currencies; null stays unknown. It does not find fees, validate lawful charges, apply exchange rates, or calculate signing cash. Input example:

```json
{"currency":"AUD","costs":[
  {"name":"rent","amount":650,"period":"week"},
  {"name":"internet","amount":60,"period":"month"},
  {"name":"electricity","amount":null,"period":"quarter"}
]}
```

Rent becomes AUD2,816.67/month, known subtotal AUD2,876.67; electricity and the completeness of necessary housing costs remain unknown. Transfer normalized recurring rows to [rental checker input](check-input.en.md) **without** treating its rounded output as evidence of completeness. The normalizer uses Decimal, sums unrounded monthly values, then rounds to two decimals for display; preserve source precision and use the lease/local currency's settlement rounding for actual payment.

For concessions, show contractual regular payment and a separate effective-rent scenario over the **same intended term**: `(sum of actual rent payable − confirmed rent credits) / occupied months`. Do not subtract a credit twice if already in actual payments. A “free month” in a 12-month offer is not a discount for a six-month stay unless its conditions permit it. Deposits and prepaid rent are not concessions.

## 2. Separate cost from tied-up cash

- Necessary monthly housing = normalized rent + necessary recurring charges **not already included**. German Warmmiete/ French CC/ bills-included rent require scope checks; add only excluded charges. Unknown utilities remain unknown or an explicitly sourced range.
- Nonrefundable initial fees + refundable deposit, **excluding prepaid rent**, measure fees plus cash tied up; they are not monthly rent.
- Signing/move-in cash = sum of all amounts actually due by that date: rent in advance + deposits + due fees/taxes/other payments, less only confirmed credits already paid toward those items. A holding payment credited to rent must not be counted again as an extra fee. Keep later invoices separately.
- Optional stay-cost scenario = recurring payments during the chosen stay + nonrefundable one-time charges. Do not count a fully refundable deposit as consumption; show tied-up cash and potential documented deductions separately. Do not spread upfront fees over months and hide the original signing-cash requirement.

**Fictional Australian example:** AUD650/week, AUD60/month internet, electricity unknown; expressly quoted bond2,600 + two weeks' rent1,300 due at signing, no other payment due confirmed. Rent/internet known monthly subtotal2,876.67; signing cash3,900 only if the complete due-now list is evidenced. The bond multiple is an invented input, **not a statement of state law**. A monthly housing cap3,000 is still unknown because electricity is missing.

## 3. Transport and monthly household burden

Door-to-door minutes = entrance walking/access + waiting + travel + transfers + final access, including steps/lifts relevant to the user. If the planner already gives a total including those components, **do not add walking again**. Query actual local weekday, desired arrival and return departure separately; line distance is not travel time.

Per-destination monthly pay-as-you-go scenario = actual visits × (outbound fare + return fare) + necessary extras. A transfer-inclusive journey fare is not the sum of separately advertised leg fares. Compare passes/caps only with current route/zone/mode/time eligibility; shared passes cover multiple destinations once, not once per destination. A single household has multiple riders—check rider counts instead of silently multiplying an adult fare for everyone.

For [commute checker](commute-input.en.md), enter one chosen mode per destination. If using one pass across destinations, set covered incremental trip fares to confirmed zero, assign the pass to one route's `extra_monthly_cost`, and explain that allocation; uncovered journeys retain their fares. Do not add pass cost to every route or combine alternative modes. The script does not itself optimize passes or apply fare caps. Missing return fare stays null.

Combined monthly household burden = necessary monthly housing + transport on the **same currency, month, household and trip basis**. If either is incomplete, report a known subtotal, not an affordable complete total. For cross-currency comparisons keep native figures; any converted scenario needs dated FX source, direction, fees and rounding. Do not mix nominal dollar amounts from different countries.

## 4. Buying: cash and monthly financing are separate scenarios

Get jurisdiction-specific transaction taxes/fees from current official calculators/rules for the property and buyer, not a global percentage. For the US, [CFPB home-buying resources](https://www.consumerfinance.gov/owning-a-home/) explain lender estimates/closing documents; other markets need their actual lenders and official authorities.

- Total own funds toward price = agreed price − funds actually available from financing. Total acquisition cash additionally includes applicable taxes, legal/notary/registry/agent fees, repairs and settlement adjustments. A deposit credited to the price is already part of own funds, not an additional purchase price.
- Remaining cash at completion = evidenced remaining price/charges − completion financing − credited amounts already paid; show earlier deposits and later costs separately. Do not subtract the same credit twice.
- For a fully amortizing loan with fixed monthly rate `r`, principal `L` and remaining `n` monthly payments: `payment = L*r / (1-(1+r)^(-n))`; if `r=0`, `L/n`. Obtain the **actual monthly rate convention**; annual nominal rate/12 only where the loan specifies it. Effective annual rates, Canadian nominal semiannual compounding, reset/interest-only/balloon loans need their actual convention. APR is not automatically the payment interest rate.
- Monthly ownership cash flow also needs property taxes, insurance, HOA/strata/management/service charges, maintenance assumptions and utilities, avoiding items already in escrow or another total. This is not a complete rent-versus-buy economic comparison: principal repayment, resale/exit costs and capital risk differ.

The rental and period-normalization scripts **do not calculate purchase eligibility, transaction tax or mortgage approval**. Until price, financing and due dates are evidenced, label calculations as scenarios rather than budget clearance.
