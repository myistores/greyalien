# V23.6D.2 Validation Report

**Release:** V23.6D.2 — VASCO Scientific Challenge + News Lifecycle & Permanent Research Ingestion  
**Base:** V23.6E

## Validation Results

- `tools/validate_v23_6d_2.py` — **PASS**
- `tools/validate_graph.py` — **PASS**
- `tools/validate_sources.py` — **0 errors** (24 inherited-style warnings for organizations without verified official links)
- Graph: **1,621 entity files / 3,635 declared relationships**
- Existing unresolved legacy graph targets: **56 warnings**, tolerated by the production graph validator and not introduced as release-blocking errors.

## Scope Validation

- August 28, 2026 IBTimes UK VASCO article present in Latest UAP News.
- News classification is `current`, non-Landmark, archive-eligible, with automatic aging disabled.
- Knowledge classification is `permanent` and independent of news lifecycle state.
- Cambridge/PASA paper is the permanent Research Library object.
- DOI and accepted-manuscript status are preserved.
- Original VASCO nuclear-test timing correlation and Watters et al. methodological challenge are separate claim records.
- VASCO rebuttal/replication context is preserved as competing research context.
- Latest UAP News → permanent publication and Research Library → related news navigation paths are present.
- Palomar Observatory plate provenance is represented through a permanent facility entity.
- Existing Galileo Project entity is reused; no duplicate Galileo entity created.

## Regression Protection

The V23.6D.2 validator confirms byte-for-byte protection of:

- V23.6E `image-video-analysis` entity.
- Science & Technology gateway and Scientific Methods collection.
- V23.6D.1/V23.6E `entity-engine.js`, `graph-core.js`, and `automation-enhancements.js` runtime files.
- All five pre-existing Latest UAP News JSON records.

Only the entity-shell cache-bust query was changed to `v=23.6d2`; the runtime JavaScript itself is unchanged.

## Version-Specific Validator Note

Older V23.6A/V23.6D/V23.6E validators contain hard-coded historical record counts, ordering, and cache-bust expectations. They are expected to report failures after a legitimate later ingestion and are superseded for this release by `tools/validate_v23_6d_2.py`. Their failures are not runtime or data-integrity failures.

## Architectural Result

**News can age; knowledge does not.**
