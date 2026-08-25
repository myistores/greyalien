# V23.6D.1 — Entity Page Loading Reliability & Graph Fetch Optimization

**Base Repository:** V23.6D (deployed)  
**Production Type:** Core Reliability / Performance Patch  
**Repository Impact:** Entity Page Runtime + Knowledge Graph Fetching — Bounded

## Production Result

V23.6D.1 removes the entity renderer's dependency on downloading every searchable entity JSON record before a page can display its connected research. The public entity UI and knowledge meaning are unchanged.

## Implementation

- `tools/build_graph.py` now generates `data/relationship-index.json`, a deterministic incoming/reverse-relationship lookup keyed by entity ID.
- `data/entity-index.json` remains the compact display lookup and now includes precomputed internal identity/canonical scores needed by existing duplicate-suppression rules.
- `assets/js/entity-engine.js` loads the requested entity, entity index, relationship index, vocabulary/rendering/timeline metadata, then constructs only that entity's outgoing and incoming edge set.
- The runtime no longer contains the legacy `idx.entities.map(...fetch(data/entities/...))` full-graph request sweep.
- `entities/entity.html` cache-busts the updated entity runtime as `entity-engine.js?v=23.6d.1`.
- Entity load failures now render a visible retry state and log diagnostic information to the browser console.

## Relationship Preservation

The generated reverse index is derived from the same indexed entity population used by the prior browser scan. Each resolved relationship retains its original `source`, `type`, and complete relationship metadata. Outgoing relationships continue to come directly from the requested entity record.

No entity, relationship, taxonomy, description, source, podcast, gateway, or news content was changed.

## Request Reduction

For a normal indexed entity page:

- V23.6D: approximately 1,602 entity JSON requests (requested entity + 1,601 indexed entity records).
- V23.6D.1: 1 entity JSON request (the requested entity only).
- V23.6D: approximately 1,606 core JSON requests before other static/media assets.
- V23.6D.1: 6 core JSON requests before other static/media assets.

The new relationship index contains 3,534 resolved indexed relationships in one static file.

## Failure Behavior

If a required entity/index/schema file fails to load, the page no longer remains indefinitely on “Loading connected record…”. It displays **Unable to load this record** with a **Retry** action and writes a diagnostic console error.

## Scope Protection

- Permanent entity files: 1,611 before / 1,611 after.
- Permanent entity JSON: byte-for-byte unchanged.
- Latest UAP News records: unchanged.
- Research Library content: unchanged.
- Podcast records/media: unchanged.
- Gateway/homepage content: unchanged.
