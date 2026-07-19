# V17.2 — Phase 3 Import System

Phase 3 turns the Phase 2 episode importer into a general, transactional import pipeline for podcast episodes and every other GreyAlien entity type.

## Capabilities

- Single-file or folder-based batch imports
- Validation before any deployable file changes
- Dry-run mode
- Conflict protection and explicit replacement mode
- Cross-record relationship resolution within the same batch
- Full staged graph, podcast, sitemap, and entity-page builds
- Roll-forward commit only after every validator passes
- Machine-readable import reports
- Stable generated HTML entry points for all entities

## Commands

```text
python tools/validate_import_record.py staging-folder
python tools/import_batch.py staging-folder --dry-run
python tools/import_batch.py staging-folder
python tools/import_batch.py staging-folder --replace
```

## Important design rule

Structured JSON remains the source of truth. Generated HTML, indexes, counts, and sitemaps are disposable build products and should never be edited manually.
