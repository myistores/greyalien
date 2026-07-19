# GreyAlien Import System

Phase 3 adds transactional single-record and batch ingestion.

## Safe workflow

1. Place one or more completed entity JSON files in a staging folder.
2. Validate without changing the site:
   `python tools/validate_import_record.py path/to/staging-folder`
3. Test the complete build transaction:
   `python tools/import_batch.py path/to/staging-folder --dry-run`
4. Commit a clean batch:
   `python tools/import_batch.py path/to/staging-folder`
5. Use `--replace` only when intentionally updating an existing entity.

Every attempt writes a machine-readable report to `data/imports/reports/`. The live site is changed only after the staged copy passes graph, podcast, page, and sitemap builds plus all validators.

## Generated outputs

- `data/entity-index.json`
- `data/graph-manifest.json`
- `data/podcasts/*.json`
- `entities/generated/*.html`
- `sitemap.xml`

The source of truth remains `data/entities/*.json`.
