# V17.0 Phase 1 — Core Framework

## What changed
- Added a universal JSON Schema (`data/schema/entity-schema-v2.json`).
- Added reusable browser graph utilities (`assets/js/graph-core.js`).
- Added a generic entity starter template (`data/templates/entity-template.json`).
- Added deterministic graph/index generation (`tools/build_graph.py`).
- Added computed graph statistics (`data/graph-manifest.json`).
- Expanded validation to enforce IDs, required fields, entity types, and relationship vocabulary.

## Content workflow
1. Create or edit entity JSON in `data/entities/`.
2. Run `python tools/build_graph.py`.
3. Run `python tools/validate_graph.py`.
4. Preview through `entities/entity.html?id=ENTITY-ID`.

This phase changes the internal foundation only. Existing public pages and current content remain intact.
