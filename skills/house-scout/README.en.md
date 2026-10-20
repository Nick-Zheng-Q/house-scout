# House Scout — v1.0.0 distribution package

[中文](README.md) · [Chinese entry](SKILL.md) · [English entry](SKILL.en.md)

Helps an agent choose market-specific listing platforms and searches, then assess layout, costs, dated commutes and named amenities. It is not a live listing database or a global routing guarantee. Read the [validation scope](references/validation-status.en.md). Keep complete transit plans, station schedules, access models, current fares and unknowns separate; walking never passes a transit requirement.

## Install and update

After extraction, run `sh install.sh` from this directory. Default destination: `~/.agents/skills/house-scout`. Choose another with `sh install.sh --dest-dir /path/to/skills`. Installation refuses to overwrite an existing installation. Use `sh update.sh` with the same location option to update, with an automatic backup. These operations use local files only, without dependency downloads or host-configuration changes.

The host needs existing Python 3.9+ and authorized web/map tools. Some network helpers support macOS/Linux only. Browser/API access depends on existing host capabilities, not automatic skill permission. Invoke `$house-scout` explicitly or let a supporting host select it. English requests have complete English instructions; automatic triggering is not independently validated.

## Data and action boundaries

No automatic contact, booking, private-record submission, accounts, payments or signing. Obtain authorization before sending private addresses to a map; public tests do not grant permission for real user addresses. Recheck future fares, schedules and construction. Unknown return time supports conditional monthly scenarios only, not a verified bill.

This archive contains runtime files, installers, bilingual guidance and checksums—not test caches, raw websites, cookies, keys, large GTFS files or research reports. Evidence and its retention notes stay in the source repository. `release-manifest.json` checks content integrity; it is not an author signature or platform approval.

## License and publication

[PolyForm Shield License 1.0.0](LICENSE), with retained upstream Required Notices; this is not an OSI open-source license. Dayweaver attribution is confirmed. Public distribution still requires the owner’s approval and platform checks. Building this package does not publish it.
