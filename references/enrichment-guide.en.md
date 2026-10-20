# Layout fit, routes, and nearby amenities

When transit is required, read [actual-time public transport queries](transit-guide.en.md): walking-only routes cannot meet that requirement. Report original-date transit, exact-date references, access and matched fares separately.

For the relevant jurisdiction and native terms, read [market guidance](international-markets.en.md); for period conversion, cash, transport passes and financing assumptions read [cost calculations](cost-comparison.en.md). Mainland China platform steps remain in [platforms](platforms.en.md).

Enrich each **specific retained unit**, not just its neighborhood. If destinations, usable modes, or daily-life needs are missing, ask only for the information that changes the selection.

## Layout and suitability

From a plan or material tied to the target unit, record independent bedrooms and bathrooms, gross versus internal/usable area, living/kitchen space, floor and lift, step-free path, orientation/daylight, balcony/storage, heating/cooling, furniture, and completion condition. A show flat, another unit, or a “two-bed” marketing label does not prove that this unit has two usable windowed bedrooms or is accessible throughout. Explain **who/what household routine it suits, what it compromises, and what to verify at a viewing**. Match occupants, working from home, children/older people, pets, and storage needs.

## Door-to-door travel

For **every regular destination**, obtain the origin at the building entrance and the actual destination, travel frequency, weekday/weekend, required arrival or departure time, and usable modes. Use Amap/Baidu Maps in mainland China, Google Maps or an appropriate local planner elsewhere, and transit-operator fare/timetable sources when necessary. Save source/route link and query date. If only a compound centroid is known, disclose the entrance error.

| What to report | Include |
| --- | --- |
| Mode and route | Walking, transit, cycling, driving, or ride-hail only if available to the user; line/transfers, access walk and wait |
| Time | **Door-to-door** estimated minutes/range at the requested period; separate outbound peak and return/night trips when relevant |
| Money | One-way and return fare/estimate, parking/tolls/energy where relevant, plus monthly formula using the user's trip count |
| Reliability | Headways, last service, congestion, weather constraints, and unknowns |

Do not derive fare from straight-line distance. Dynamic ride-hail price is a query-time estimate. Do not call driving costs “total” if fuel, charging, parking, or tolls are missing. Compare candidates with the **same destination, time, mode feasibility, and monthly frequency**. For many destinations, calculate each separately; `python3 scripts/check_commutes.py <input.json>` checks entered arithmetic ([input rules](commute-input.en.md)), not actual routes or fares.

## Daily amenities and commercial areas

Use the user's priorities—groceries/market, pharmacy, healthcare, school/childcare, restaurants, park/fitness, parcels, parking, malls or business districts. For every decision-relevant category, identify a **named place**, function, actual walking/cycling/transit route time or distance, opening/service hours if verified, source, and date. A nearby place behind a major road, closed at needed hours, or appointment-only may not be useful. A nearby school or hospital does not imply admission or access rights. Map entries and reviews may be stale; confirm decisive facilities on the visit or on the institution's own page.

Do not pad with unrelated shops or claim a missing search result proves absence. Record “not verified” with the search area. Note potential noise/traffic isolation as an on-site question rather than an unverified verdict. Present each unit with the same layout, destination×mode×time×fare, and named amenity×access-time fields, without inventing a numeric score.

## Execute alternatives instead of stopping at a map shell

Read [tools, API commands, timetable alternatives and shop routing](routing-guide.en.md). Use authorized browser interaction if available; otherwise query pedestrian-network/POI APIs with the provided helper, operator timetables and exact-pair reference routes. A blocked text-reader map URL does not block all HTTP sources. Report untimed walking models or sourced schedule compositions as such, not as requested-time itineraries. Do not abandon named businesses and access estimates merely because a full transit planner fails.
