# Phase 4 — Automation

GreyAlien V17.3 connects the Core Framework, Podcast Engine, and Import System through one authoritative automation pipeline.

## One-command build

From the website root, run:

```bash
python tools/automate_site.py
```

The command performs these steps in order:

1. Rebuild the universal entity index and graph manifest.
2. Rebuild podcast-series and episode indexes.
3. Generate `Referenced In` and related-episode recommendations.
4. Regenerate stable entity entry pages.
5. Update the homepage Latest Additions from structured release data.
6. Rebuild the sitemap.
7. Validate the universal graph.
8. Validate podcast records.
9. Create a deployment report.

The command stops immediately if any required step fails.

## Generated automation assets

- `data/related-content.json`
- `data/automation/last-run.json`
- `data/automation/reports/latest.json`
- `data/automation/reports/latest.md`
- Updated `data/entity-index.json`
- Updated `data/graph-manifest.json`
- Updated `data/podcasts/`
- Updated `entities/generated/`
- Updated `index.html`
- Updated `sitemap.xml`

## Podcast-page automation

Podcast episode pages now display a Related Episodes section when other researched episodes share connected entities. Entity pages can also display a Referenced In section showing podcast or media records that point to the entity.

## Imports

`tools/import_batch.py` now invokes the same generated assets and validation steps used by the one-command automation pipeline. This prevents ordinary rebuilds and imports from producing different site states.

## Recommended testing sequence

```bash
python tools/automate_site.py
python tools/import_batch.py data/imports/examples --dry-run
```

Review:

- `data/automation/reports/latest.md`
- the homepage Latest Additions panel
- one podcast episode page with Related Episodes
- a person or claim page with Referenced In media
