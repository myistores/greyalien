# V23.5B — Existing Podcast Official Media Migration

## Objective
Migrates WEAPONIZED, Need to Know, MERGED, and Somewhere in the Skies from legacy podcast media fields into the V23.5A universal `officialMedia` collection while retaining every legacy field for compatibility and rollback.

## Coverage
- Podcast series entities migrated: 4
- Episode entities migrated: 257
- Legacy URL occurrences inventoried: 958
- Canonical official-media records created: 491
- Duplicate legacy URL occurrences suppressed: 467
- Direct episode records: 222
- Series archive records: 189
- Playlist records: 76
- Channel records: 4
- Episode records using a series-level fallback: 41
- Unauthorized non-media changes: 0

## Methodology
The transactional migration inventories `mediaLinks`, `officialLinks`, and `referenceSources`; classifies each URL using repository evidence; canonicalizes and deduplicates equivalent destinations; writes approved `officialMedia` collections; records deterministic preferred destinations; and retains all legacy fields unchanged.

## Podcast outcomes
- **WEAPONIZED:** 123 episodes plus the canonical series entity migrated. Existing hosted episode pages remain preferred where present.
- **Need to Know:** 75 episodes plus the canonical series entity migrated. Direct YouTube destinations remain preferred, including the corrected Episode 13 (`HRCT_ddq39U`) and Episode 14 (`YOjSBPfmoIM`) records.
- **MERGED:** 19 episodes plus the canonical series entity migrated. Existing direct YouTube/hosted destinations are distinguished from series fallbacks.
- **Somewhere in the Skies:** 40 unique 2017 episodes plus the canonical series entity migrated. V23.4 direct-link versus Apple/Spotify archive-fallback distinctions are preserved; retired Acast destinations are not reactivated.

## Compatibility and rendering
The V23.5A renderer becomes authoritative whenever `officialMedia` is present. Legacy fields remain available for rollback and existing tooling. Canonical URL suppression prevents duplicate controls across migrated and legacy representations. Series, playlist, channel, and feed records receive destination-accurate labels.

## Validation and safeguards
`tools/validate_v23_5b_migration.py` verifies migration coverage, schema conformance, canonical URL uniqueness, fallback labeling, Need to Know corrections, Somewhere in the Skies count preservation, retired-domain suppression, rollback metadata, and zero unauthorized non-media changes.

## Rollback
Remove `officialMedia` and `mediaMigration` from the 261 migrated entities. Because legacy media fields were not edited or deleted, this deterministically restores V23.5A public compatibility behavior. The entity list is recorded in `data/migration/v23.5b/rollback-manifest.json`.

## V23.5C readiness
The repository is ready for a dedicated live media audit and repair release. V23.5B intentionally does not perform broad URL discovery or platform replacement.
