## V23.5B production migration

The universal official-media model is active for all currently ingested production podcast records. Legacy fields remain compatibility-only inputs and rollback sources; migrated `officialMedia` collections are authoritative for rendering and preferred-link resolution.

# V17.1 — Phase 2: Podcast Engine

## Purpose
Phase 2 converts podcast additions from manual page construction into structured entity ingestion. It is intentionally deterministic: research and editorial judgment remain human-controlled, while repetitive indexing, connection counts, directory updates, sitemap changes, and validation are automated.

## Components
- `data/schema/podcast-series-schema-v1.json`
- `data/schema/podcast-episode-schema-v1.json`
- `data/podcasts/ingestion-package-template/`
- `tools/ingest_podcast_episode.py`
- `tools/build_podcasts.py`
- `tools/validate_podcasts.py`
- `tools/build_sitemap.py`
- generated `podcast-index.json`, `episode-index.json`, and `podcast-manifest.json`

## Editorial methodology
1. Confirm the official episode source and publication date.
2. Identify hosts, actual guests, and primary subjects separately.
3. Write a neutral summary describing the episode's contribution.
4. Capture only material graph relationships.
5. Apply the 3–7 principal-claims standard when claims are central.
6. Distinguish a claim being presented from independent corroboration.
7. Run ingestion and review the rendered episode and connected pages.

## One-command workflow
`python tools/ingest_podcast_episode.py research/episode.json`

The command copies the entity, rebuilds the universal graph and podcast assets, rebuilds the sitemap, and runs graph and podcast validation.

## V23.5A media collection extension
The podcast engine supports an optional `officialMedia` collection plus runtime adapters for `mediaLinks`, `officialLinks`, and `referenceSources`. Existing records require no migration.

## Universal media-audit engine

V23.5C.1 adds deterministic inventory, URL normalization, validation-job generation, identity expectations, external result import, repair proposals, and rollback reporting. Offline preparation never promotes a destination to live-verified status.
