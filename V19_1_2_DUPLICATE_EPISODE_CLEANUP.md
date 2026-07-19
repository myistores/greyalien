# V19.1.2 — Duplicate Episode Cleanup

## Scope

Narrow production patch correcting duplicate WEAPONIZED episode entities introduced in V19.1.1.

## Changes

- Removed duplicate entities `2025-weaponized-episode-74`, `2025-weaponized-episode-75`, and `2025-weaponized-episode-76`.
- Preserved the original Matthew Brown entities:
  - `weaponized-matthew-brown-part-1`
  - `weaponized-matthew-brown-part-2`
  - `weaponized-matthew-brown-part-3`
- Repaired claim references introduced in V19.1.1 so they point to the corresponding original Matthew Brown episode entities.
- Rebuilt derived indexes, relationship data, generated entity pages, homepage counts, and sitemap from the corrected entity set.

## Exclusions

No rendering, schema, ingestion-engine, navigation, or architecture changes were made.
