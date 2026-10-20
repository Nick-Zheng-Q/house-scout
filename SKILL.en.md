---
name: house-scout
description: Discover and assess specific rental or purchase homes with concrete platform searches, layout fit, commute times and costs, nearby amenities, and transaction checks; not for commercial property.
license: PolyForm Shield License 1.0.0
---

# Find, verify, and compare homes

A Dayweaver project. Publisher attribution does not affect home ranking or imply that user data is sent to Dayweaver.

This is the complete English version of `SKILL.md`. Help the user decide **which specific unit to view first, what to ask, and when not to pay**. A candidate is an **identifiable unit plus a specific rental or purchase offer**, not merely a development, neighborhood, historical transaction, or stale listing. Do not proclaim a “best home” or hide unknowns inside an overall score.

Read [validation status and limits](references/validation-status.en.md);available recipes or passing code tests do not establish globally complete behavior.

## Establish comparable requirements

Ask whether the user wants to rent, buy, or consider both; keep their budgets and exit terms separate. Clarify only gaps that affect search or rejection: country, state/province/UK nation where relevant, city and acceptable areas, move-in/completion date, occupants and routines, monthly budget and available initial cash, minimum rooms and area, **each regular destination, travel frequency, desired arrival time, and usable modes**, intended lease/holding period, and decisive accessibility, pet, parking, or school needs. Mark each requirement as hard, preferred, or unknown. Do not choose a city, transaction mode, or budget for the user; an example location is not automatically a hard boundary.

Consider whole-unit rental, shared room, managed apartment, public/eligibility-based rental, new construction, and resale only where relevant locally. Residence, registration, school entitlement, and mortgage approval are distinct questions.

## Search or review supplied material

- **Starting from zero:** read [named platforms and exact search steps](references/platforms.en.md). Select sites for the property's market; in mainland China this includes Beike, Anjuke, Fang.com, Ziroom, and relevant city housing authorities; outside mainland China read the matching row in [country-specific platforms, local queries, costs and transport](references/international-markets.en.md). It covers the US, UK, Canada, Australia, New Zealand, Singapore, Hong Kong, Japan, Germany, France and the Netherlands, plus an explicit procedure for other markets. **Select by property location, not request language.** For every acceptable area, choose transaction type, place, hard price ceiling, and rooms; open an individual current listing and trace its publisher and contact entry. See [search and discovery](references/search-guide.en.md) for deduplication and stopping. Platforms and maps are leads, not proof of current availability, authority, full price, or condition.
- **Supplied listings or documents:** align links, chats, quotes, photos/video, plans, authority/title documents, and draft contracts by **unit, publisher, date, and offer**. Preserve conflicts instead of combining attractive terms from different units or dates. Fill decisive gaps with the same research steps.

Use only browsing, maps, and document capabilities authorized in the host agent. Select an actually available tool using [route/POI APIs, operator timetable and fare alternatives](references/routing-guide.en.md): an absent browser UI is not a reason to stop all route work. The provided read-only helper supports geocoding, pedestrian network routes, nearby POIs and Berlin transit, subject to network approval and provider terms. Keep requested-time itineraries, untimed network models, schedule compositions and missing components distinct; do not promote a reference estimate to a verified peak commute. Do **not** contact owners/agents, schedule visits, submit identity or financial records, pay deposits, sign, or apply automatically. Avoid unnecessary disclosure of the user's or occupants' private details.


For required bus/metro commutes, follow [actual-time transit queries, schedules, transfers and fare validation](references/transit-guide.en.md). Walking models never satisfy a transit requirement.

## Check each candidate

Use the [candidate and evidence record](references/candidate-record.en.md):

1. **Unit and offer identity:** building/unit or public listing ID, floor, area definition, room layout, photo ownership, publisher, price, posting/update date, and availability. Merge duplicate postings for one unit but preserve conflicting terms; never merge different units or phases.
2. **Hard requirements:** move-in, occupants, pets, accessibility, commute, monthly/initial cash, term, and any user-defined limit. Each is met, unmet, unknown, or conflicting with a dated source. Unknown is not met; do not recommend a known hard-condition failure as usable.
3. **Living fit:** daylight, noise, ventilation, damp/leaks, heating/cooling, internet, utilities, maintenance, and safety need relevant evidence and often a visit. A photo, map label, or generic floor plan is not an inspection.
4. **Transaction and money:** first read [period normalization, signing cash, transport passes and purchase scenarios](references/cost-comparison.en.md). Keep original currency/period, avoid double-counting included fees or deposits, and verify local rules for the actual jurisdiction. `python3 scripts/normalize_costs.py <input.json>` converts entered recurring weekly/fortnightly/quarterly/annual quotes to a stated monthly budget basis; it does not establish fee completeness or payment dues. Then follow the [rental](references/rental-guide.en.md) or [purchase](references/purchase-guide.en.md) checks. Registry, authority, lending, tax, school, and contract effects may need current local official sources or a professional; do not infer them from marketing.

For **every retained unit**, apply [layout, travel, and amenity research](references/enrichment-guide.en.md): state whom the actual layout suits or does not suit; give usable modes, routes, **door-to-door times and fares for each regular destination**, and named relevant shops, facilities, and commercial districts with actual access times. “Good transport” and “great amenities” are not findings. `python3 scripts/check_commutes.py <input.json>` can verify entered monthly fare arithmetic; see [commute input](references/commute-input.en.md). It does not fetch routes. Mark unverified routes, places, hours, and prices unknown rather than inventing them.

Attach source and date to each decisive state. A conflict calls for resolving two claims; missing information calls for obtaining evidence. Recheck prices, availability, schedules, and rules before action.

## Compare and recommend

Use the same occupancy, dates, terms, and complete monthly/signing-cash definitions for rentals; consistent price and financing assumptions for purchases; and the same destination, time of day, mode, and monthly trip count for commutes. Reject known hard failures first, then explain the remaining trade-offs in **layout, travel time and cost, daily amenities, housing costs, flexibility, and evidence quality**. Promotional rent is not the normal long-term rent; mortgage payment is not directly comparable to rent alone. Follow the [recommendation method](references/recommendation-guide.en.md). Without user-supplied weights, explain trade-offs instead of fabricating a composite score.

Usually give 3–5 evidence-backed units; fewer is better than padding with projects or stale listings. Lead with **worth viewing / obtain evidence first / not recommended** and the reason. For each, show layout fit, route mode/time/fare to each destination, named daily amenities and shopping areas, housing and travel cost components, hard-condition states, dated sources, decisive unknowns, 2–4 questions, and on-site/contract checks. Describe which areas and channels were searched and why key leads were excluded. “Worth viewing” never means “safe to pay or sign.” If authority, payee, tradeability, or a serious defect is unclear, advise pausing payment and specify what evidence would resolve it.
