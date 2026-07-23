# V20.5 — Knowledge Graph Enrichment, Batch B

## Scope

This content-only enrichment pass audited the existing canonical person entities for Ryan Graves, Christopher Mellon, and Karl Nell. It added only direct, materially useful relationships supported by authoritative source records and repaired two inaccurate legacy claimant edges. No architecture, schema, rendering, template, navigation, routing, UI, or styling changes were made.

## Ryan Graves

Added a direct claimant relationship to:

- `claim-navy-uap-aviation-safety` — Graves’s source-supported position that recurring military UAP encounters present an unresolved aviation-safety concern.

Existing links to the July 26, 2023 House hearing, his written testimony, Americans for Safe Aerospace, the Merged podcast, the 2014–2015 East Coast Navy encounters, and the 2019 New York Times report were preserved.

## Christopher Mellon

The audit found that Mellon’s person record still declared him as a claimant for `claim-secret-uap-programs`, even though V20.4 correctly established that canonical claim as David Grusch’s allegation. The inaccurate Mellon-side edge was removed.

No replacement relationship was added merely to increase Mellon’s count. His existing Department of Defense, Senate Intelligence Committee, To The Stars Academy, 2017 New York Times, and congressional-assessment advocacy connections already capture the strongest supported graph relationships represented in the repository.

## Karl Nell

Removed the inaccurate person-side claimant edge to `claim-crash-retrieval-program`, which is the repository’s David Grusch-specific canonical allegation.

Added direct relationships to:

- `timeline-2021-2022-karl-nell-uaptf-support` — participant.
- `timeline-2024-05-21-karl-nell-salt-uap-presentation` — speaker.
- `timeline-2023-11-17-sol-inaugural-symposium` — participant.
- `sol-foundation` — white-paper author and symposium contributor.

## Relevance exclusions

The audit did not add incidental podcast mentions, broad disclosure-topic links, person-to-person associations inferred from shared events, unsupported legislation advocacy edges, or duplicate claim attributions. Potential standalone records for Mellon-authored commentary and Nell’s Sol white paper remain future enrichment opportunities if canonical document or publication entities are created through a separately scoped content pass.

## Source basis

- Ryan Graves’s official written testimony and the official July 2023 House hearing record.
- Christopher Mellon’s official biography and published congressional-oversight commentary.
- The Sol Foundation’s official Karl Nell paper and symposium records.
- SALT’s official Karl Nell speaker profile and 2024 agenda.

## Validation requirements

- Reciprocal discovery regenerated from all retained and new edges.
- Unique connection counts rebuilt from the graph.
- Duplicate-card suppression retained.
- No duplicate entities created.
- All existing valid content and unrelated relationships preserved.
