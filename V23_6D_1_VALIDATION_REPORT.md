# V23.6D.1 — Validation Report

## Result

**PASS**

## Reliability / Fetch Architecture

- Legacy full-graph entity fetch loop removed from `assets/js/entity-engine.js`.
- Precomputed `data/relationship-index.json` is loaded by the entity runtime.
- Relationship index contains 3,534 resolved indexed relationship entries.
- Every relationship-index source and target resolves to the compact entity index.
- Generated incoming relationship sets are equivalent to the reverse relationships that the legacy full-graph browser scan would discover.
- Explicit failure state and Retry action are present.
- Updated runtime is cache-busted in `entities/entity.html`.

## Request Reduction

- Approximate V23.6D entity JSON requests per normal indexed entity page: **1,602**.
- V23.6D.1 entity JSON requests per normal indexed entity page: **1**.
- Approximate V23.6D core JSON requests before other assets/media: **1,606**.
- V23.6D.1 core JSON requests before other assets/media: **6**.

These figures are derived directly from the before/after runtime request paths.

## Graph / Content Protection

- Permanent entity files: **1,611**, unchanged.
- All permanent entity JSON files are byte-for-byte unchanged from V23.6D.
- Searchable entity population remains unchanged.
- No new entities, relationships, taxonomy changes, descriptions, or content were introduced.

## Regression Coverage

Relationship lookup presence and graph equivalence were checked for the entire indexed graph, including representative direct destinations:

- Marco Rubio — Person
- David Grusch — Person / high-connectivity record
- The Sol Foundation — Organization
- The Civilizational Risks of a UAP Technology Arms Race — Publication / Research Library
- MERGED Episode #18 — Podcast Episode

## Standard Validators

- `tools/validate_graph.py`: PASS (56 inherited unresolved legacy-target warnings remain).
- `tools/validate_podcasts.py`: PASS (4 inherited recommended-field warnings remain).
- `tools/validate_rendering_rules.py`: PASS.
- `tools/validate_timeline_normalization.py`: PASS.
- `tools/validate_sources.py`: PASS (24 inherited no-official-link warnings remain).
- `tools/validate_visual_identity.py`: PASS.
- `tools/validate_research_accelerator.py`: PASS.
- `tools/validate_v23_6d.py`: PASS.
- `tools/validate_v23_6d_1.py`: PASS.

## Known Boundary

The optimization deliberately remains within GreyAlien's static-site architecture. The compact entity and relationship indexes are still required files for connected rendering, but a failed required file now produces a visible retry state instead of an indefinite loading screen.
