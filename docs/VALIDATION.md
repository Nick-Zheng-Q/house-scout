# Public validation summary · 2026-10-20

This is a concise project-authored summary, not raw third-party evidence. A full local audit archive remains private because it includes web responses, mapped addresses and browser/request data.

- 24 public transit scenarios across 12 markets, original date 2026-12-01 local arrive-by09:00. No walking-only transit passes.
- Independently complete current-priced planned/modelled public-address/building entrance→original station public street entrance: Munich (08:19–08:49:04,EUR4.20), Eindhoven (08:24–08:51,EUR1.88), Osaka (08:43–08:54,bus36,JPY210), Boston (07:34–08:08,bus68,USD1.70).
- This round reviewed the other22cases and ran4fresh focused evaluations. Osaka/Boston passed; Melbourne remained partial; Amsterdam’s initial pass was downgraded after offline audit (backing house74 versus original198). Final total4/24, not5. All future-fare flags remainfalse. No verified reverse journeys inferred.
- Other20cases include two short trips returning no suitable transit, street-only origins, publication-horizon limits, unresolved connectors/address conflicts and legal/technical access gaps. Those outcomes are not the same as “no public transport exists”.
- Original broad research never fully cleared cross-market actual rental availability/budgets/terms. Do not present these commute benchmarks as recommended available homes, legal approval, physical surveys, accessibility or punctuality guarantees.
- Pre-release audit reran69existing Python tests, installer/update/rollback and skill structure checks. Added distribution/demo checks are reported separately in the versioned verification file; arithmetic tests are not new live behavioral tests.

Public evidence paths: [runtime limits](../references/validation-status.en.md), [reproducible cases](../demos/README.md), and [version verification](../release/v1.0.0/verification.json). Summaries/URLs can be rechecked; local raw archives and personal paths are deliberately not published.
