# V23.5A — Universal Podcast Official Media Architecture and Rendering

## Release summary
V23.5A adds an opt-in `officialMedia` collection, a legacy compatibility adapter, canonical URL deduplication, preferred-link resolution, compact Official Media rendering, approval-aware publication safeguards, structural validators, live-capable validation, and twelve test fixtures. Existing podcast entity data is unchanged.

## Model
Each record supports `platform`, `url`, `destinationType`, `mediaType`, `official`, `verified`, `verificationStatus`, `preferredRank`, and `label`, plus optional approval, publication, review, and verification metadata. Controlled destination values are `episode`, `series`, `playlist`, `channel`, and `feed`; media values are `audio`, `video`, `web_page`, and `feed`.

## Preferred hierarchy
1. Official hosted episode page
2. Official YouTube episode
3. Apple Podcasts episode
4. Spotify episode
5. Other verified official episode platform
6. Official series archive, playlist, or channel
7. Official RSS feed

Direct verified episode records outrank fallbacks. Pending, unavailable, retired, rejected, unapproved, or unpublished records cannot become preferred. Per-series overrides are reserved in `data/podcast-official-media-config.json`.

## Compatibility behavior
When `officialMedia` is absent, the adapter derives an in-memory collection from `mediaLinks`, `officialLinks`, and `referenceSources`. It never writes the derived collection to entity files. The resolver preserves the first existing `mediaLinks` destination as the legacy primary action, preventing architecture-only link changes.

## Rendering
`assets/js/podcast-official-media.js` supplies a compact renderer. It activates only for entities that explicitly contain `officialMedia`; all current entities continue through legacy panels. Canonically equivalent URLs are suppressed, internal review metadata is not rendered, and destination labels distinguish episodes, archives, playlists, channels, and feeds.

## Validation
`tools/validate_podcast_official_media.py` validates explicit collections and compatibility fixtures. `--live` performs optional HTTP checks, follows redirects, records final destinations and HTTP errors, and reports `network_validation_unavailable` rather than a false pass when networking fails. Production audits must invoke `--live` explicitly.

## Approval gate
Records with `approved: false` or `published: false` remain internal and cannot render or become preferred. URLs are never generated from titles or slugs. Ambiguous matches remain pending review.

## Test coverage
Twelve fixtures cover hosted pages, multiple platforms, archive and RSS fallback, misclassification, cross-field duplication, retired and pending records, playlist misuse, equivalent YouTube URLs, unchanged legacy behavior, and series archives.

## Scope boundary and V23.5B readiness
No existing media URL, episode, classification, relationship, chronology, gateway count, or routing record was migrated or changed. V23.5B can populate `officialMedia` incrementally using this stable model.

## Data-preservation fingerprint
Pre-build podcast entity corpus SHA-256: `1220b3eede19fcbce5a9e6c40e7e5486ae308e18c49e725df150aa5a39fe7629`. The same fingerprint is verified during release validation.
