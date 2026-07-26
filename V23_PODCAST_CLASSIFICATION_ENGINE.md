# V23 — Podcast Classification Engine

## Base repository
V22.1.1 — Somewhere in the Skies Gateway

## Objective
Add an internal production/ingestion classifier that scales large podcast archives without changing the visitor experience.

## Classification output
Every new podcast draft receives a non-rendered `classification` object containing:

- Content Class: `research`, `standard`, or `catalog`
- Episode Type
- Primary Topics
- Secondary Topics
- Research Accelerator depth: `full`, `standard`, or `catalog`
- Existing canonical entity IDs proposed for reuse
- Candidate names requiring review
- Entity types appropriate for extraction
- Confidence, scoring reasons, warnings, and review status

## Safety and quality controls

- The engine creates drafts only and never publishes.
- It never creates canonical entities automatically.
- It never promotes a draft while `reviewRequired` is true.
- Human review is mandatory for classification, topic assignment, entity roles, and new entity creation.
- New podcast imports must contain an approved classification object.
- Existing podcast records remain valid and are not retroactively modified.
- Classification metadata is internal and is not rendered on public pages.

## Workflow

```bash
python tools/research_accelerator.py path/to/manifest.json --no-network
# Review and edit the generated draft and review files.
python tools/approve_podcast_classification.py path/to/draft.json --out-dir approved --reviewer "Reviewer Name"
python tools/validate_import_record.py approved
python tools/import_batch.py approved --dry-run
python tools/import_batch.py approved
```

## Files

- `tools/podcast_classification_engine.py`
- `tools/approve_podcast_classification.py`
- `tools/validate_podcast_classification.py`
- `data/podcast-classification-config.json`
- `data/podcast-classification-schema.json`

## Compatibility
No architecture, navigation, routing, template, styling, or public rendering changes were introduced.
