# House Scout · v1.0.0

[中文](README.md) · [English skill](SKILL.en.md) · [License](LICENSE)

A Dayweaver research skill for comparing specific rental or purchase homes: concrete local listing searches, layout fit, full-cost questions, dated transit evidence and named daily amenities. Source-available under PolyForm Shield 1.0.0—not OSI open source. No account or bundled MCP server is required. Existing authorized browsing/map capabilities are required for live research; Python 3.9+ is needed for packaged helpers, some of which require macOS/Linux.

## Install

After the approved GitHub release is public:

```sh
DISABLE_TELEMETRY=1 npx skills@1.7.4 add https://github.com/Nick-Zheng-Q/house-scout/tree/v1.0.0/skills/house-scout --skill house-scout
```

This targets the clean skill directory, not the development repository root. The pinned CLI is tested locally; public URL installation/indexing remains unverified until publication. Or extract the skill ZIP and run `sh install.sh --dest-dir /path/to/skills`; update with `sh update.sh` using the same location. Installation does not download dependencies or alter host permissions.

Claude Code, once public:

```text
/plugin marketplace add Nick-Zheng-Q/house-scout
/plugin install house-scout@house-scout-marketplace
```

[OpenAI and Claude package details](docs/DISTRIBUTION.md). A skills-only plugin does not supply a web tool or execute a remote service. The OpenAI package declares desktop/local execution for its Python workflows; directory submission, review and availability are separate states, not assumed approval.

## Try a real problem

> Compare these rental offers for one person. Keep layout, all-in monthly cost, signing cash, morning transit to work and groceries separate. Show unknowns before recommending a viewing; do not contact anyone or pay.

Start at [SKILL.en.md](SKILL.en.md), or run the [three reproducible cases](demos/README.md). Demo personas/budgets are illustrative; property and route facts are dated public evidence, not fictional customer success stories. Offline replay checks entered facts; it is not a new live search or an assurance of current vacancy.

## What has actually been tested

The October 2026 benchmark examined 24 public commute scenarios across 12 markets. Four complete original-date current-priced plans were independently established: Munich, Eindhoven, Osaka and Boston. The remaining 20 have explicit gaps or no suitable transit returned. Amsterdam's initial pass was withdrawn after a house-number conflict. Walking never substitutes for transit. These are map/timetable-based plans, not observed journeys, platform deadlines, accessibility guarantees or fixed future fares. No complete cross-market vacancy/terms-cleared rental/purchase workflow or automatic-trigger effectiveness is claimed. [Public validation summary](docs/VALIDATION.md) · [Runtime boundaries](references/validation-status.en.md).

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
sh tests/test_install.sh
python3 demos/replay.py --check
python3 scripts/package_v100.py --output /tmp/house-scout-build
```

## Privacy, third-party data and action limits

[Privacy](PRIVACY.md) · [Third-party sources](THIRD_PARTY.md). The plugin has no telemetry, hooks, background monitoring, automatic registration, messaging, booking, payment or signing. Authorized map queries send their endpoints to the chosen provider; request permission for private addresses. Do not bypass access restrictions. Demo data omits user records and raw third-party pages/photos. Public donated APIs are low-volume research aids, not a guaranteed production backend.

## Dayweaver

House Scout is a Dayweaver project. If housing choices also raise questions about longer-term spending and life plans, you can optionally explore [Dayweaver](https://dayweaver.site/). This is a disclosed publisher link, not a condition of using this skill. It does not affect recommendations, register users or transmit housing data. Plugin instructions do not require promotional messages in answers.

Support: [GitHub issues](https://github.com/Nick-Zheng-Q/house-scout/issues). The URL becomes usable only after the repository is published. Do not post private addresses, identity/financial records or keys in public issues.
