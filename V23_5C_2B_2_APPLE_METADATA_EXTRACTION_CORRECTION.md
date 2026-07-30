# V23.5C.2B.2 — Apple Metadata Extraction Correction

## Scope
Corrective parser-only release based on V23.5C.2B.1. No podcast content, official-media collections, rendered HTML, entity relationships, or knowledge-graph data are changed.

## Root cause
V23.5C.2B.1 rejected Apple branding only in a limited Open Graph path. Other candidate paths—embedded JSON, JSON-LD, Twitter metadata, canonical/title fallbacks, and generic evidence initialization—did not share a single branding-rejection rule. A high-confidence but semantically invalid value could therefore become `showTitle`.

## Deterministic series-title precedence
1. Apple structured metadata (`podcastName`, `collectionName`, `showName`)
2. Embedded Apple JSON
3. JSON-LD (`PodcastEpisode.partOfSeries`, `PodcastSeries.name`)
4. Apple storefront metadata
5. Open Graph metadata
6. Twitter Card metadata
7. Canonical URL show slug
8. HTML document title

Every candidate is evaluated by the same branding filter before selection. `Apple Podcasts`, `Apple Podcasts Preview`, `Listen on Apple Podcasts`, and equivalent platform labels are rejected as `platform_branding` and retained only in diagnostics.

## Diagnostics
The Apple extraction report now records selected metadata source, all candidates, rejected candidates and reasons, confidence score, selected series and episode, and the parser decision path.

## Regression protection
Tests cover direct episodes, series pages, regional storefronts, canonical episode identifiers, Apple-brand rejection, structured JSON/JSON-LD precedence, Open Graph fallback, HTML/canonical fallback, destination classification, identity matching, proposal deduplication, and existing non-Apple pipeline behavior.

## Validation command
```bash
cd tools/podcast_media_audit
PYTHONPATH=. python -m unittest discover -s tests -v
```

## GitHub Actions production validation
Run the existing `V23.5C.2B Live Podcast Media Validation` workflow with `job_limit = 10`. The workflow file is intentionally unchanged. Download the resulting artifact and confirm that Apple records contain the real podcast series and never use Apple platform branding as `showTitle`.
