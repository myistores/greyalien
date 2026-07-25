# V21.4 — Need to Know Official Media Validation

Production-only media validation patch against V21.3.

## Scope completed

- Audited all 21 currently ingested Need to Know records.
- Verified that each primary media link and the matching `Official Need to Know Episode` reference source resolve to the same official media URL.
- Confirmed that Episodes #1–#12 and #15–#21 use unique direct official video URLs.
- Confirmed that the official Need to Know collection remains the secondary media resource on every episode.
- Confirmed that no generic archive-page URL remains as a primary episode media link.
- Added no entities, relationships, schema fields, rendering logic, routes, navigation, UI, or knowledge-graph behavior.

## Publisher numbering exception

The official publisher sources contain one irreconcilable numbering inconsistency:

- The official Stellar Productions YouTube upload for the May 17, 2022 Elizondo hearing discussion is titled `NTK/13`.
- The official Need to Know archive lists that same release as `Episode #14`.
- No separate official `NTK/14` YouTube upload was found.
- `A Profane Rant about Modern Ufology` is an official unnumbered Bryce Zabel special, not a numbered Need to Know episode upload.

V21.4 preserves stable repository entity identifiers and all knowledge-graph relationships, as required by the production-patch constraints. It corrects the misleading media labels, explicitly identifies the unnumbered special, and discloses the archive/YouTube numbering discrepancy instead of assigning an unrelated video or duplicating a YouTube ID.

## Validation result

- 21 Need to Know records audited.
- 21 primary official media URLs present.
- 21 matching primary reference-source URLs present.
- 21 official collection links retained.
- 21 unique primary media URLs.
- Zero archive-page URLs used as primary episode media.
- Zero duplicate YouTube video IDs.
- Zero architecture, rendering, schema, UI, routing, navigation, or knowledge-graph changes.
