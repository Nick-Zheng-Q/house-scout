# Three real housing questions / 三个真实选址问题

Source snapshot:2026-10-20. Personas/budgets are **illustrative conditions**, not real clients or testimonials. Facts concern actual public unit offers; no independent current-vacancy, landlord authority, inspection or payment safety guarantee. [Dated sources and minimal facts](facts.json).

1. **Cambridge Unit21: rent below budget is not all-in affordability.** One bedroom/592sqft, advertisedUSD2700/month, move-in claim November1. Example all-in cap3000 and signing cash6000. Utilities/deposit/terms remainunknown: obtain evidence first, do not pay. HarvardSquare is a named commercial district, not a verified walking-time result.
2. **Osaka1105: zero deposits do not erase recurring charges.** Actual2K/31.77sqm:98,000rent+12,000common fees=110,000JPY, alreadyover an example100,000cap. Initial guarantor33,660 conflicts with30% of110,000=33,000; do not invent the extra base. Do not mix this unit with an older anonymous1K listing. Life Taiyuji is a sourced nearby business; no verified access minutes claimed.
3. **Eindhoven15B: two rooms is not two bedrooms, and initial cash matters.** Actual55sqm/one bedroom/max2people:1495rent+2990deposit=4485EUR before other costs. Example two-bedroom need fails;4000initial cash is at least485short if those amounts are due. Service table0 conflicts with the text excluding service/utilities, so complete monthly cost staysunknown. AlbertHeijn Roostenlaan112 is named, not a complete amenity-access validation.

```sh
python3 demos/replay.py --check
```

Replay uses only bundled minimal facts and the unchanged rental arithmetic helper. It performs no network calls and never upgrades missing evidence to met. `inputs.json` contains explicit unknowns; expected statuses are verify/reject/reject. Figures are one currency per case, no invented FX conversion. Transit case research is separately described in [validation](../docs/VALIDATION.md); it is not newly validated by this replay and does not make these listings safe to rent. Recheck live sources before action. No third-party photos/pages are bundled.
