# V20.6 — Knowledge Graph Enrichment, Batch C

## Scope

This content-only enrichment pass audited the canonical Jeremy Corbell and George Knapp person entities and their existing reciprocal graph neighborhoods. It added only direct, materially useful relationships supported by official reporting, filmography, and hearing-support records. No architecture, schema, rendering, template, navigation, routing, UI, or styling changes were made.

## Jeremy Corbell

Added direct relationships to:

- `2017-iraq-jellyfish-uap` — co-investigator and publisher of the military-recorded footage.
- `skinwalker-ranch` — documentary filmmaker whose investigative film work examined the ranch and its research history.
- `2024-11-13-house-oversight-uap` — evidence contributor who supplied witness material and documents, including delivery of the authorized Immaculate Constellation report for the Congressional Record.

Existing WEAPONIZED co-host, Bob Lazar documentary creator, Episode #115, and publication-timeline relationships were preserved.

## George Knapp

Added direct relationships to:

- `2017-iraq-jellyfish-uap` — co-investigator and publisher of the military-recorded footage.
- `skinwalker-ranch` — investigative journalist with long-running reporting and public presentation of the ranch’s private and government research history.
- `2024-11-13-house-oversight-uap` — evidence contributor who supplied witness statements, documents, and source material supporting the hearing.

Existing KLAS Bob Lazar interview, WEAPONIZED co-host, September 2025 hearing, Episode #115, and publication-timeline relationships were preserved.

## Relevance exclusions

The audit did not add every WEAPONIZED host appearance to the person records because reciprocal episode relationships already provide that discovery path. It also excluded broad disclosure-topic links, person-to-person associations inferred from collaboration, claims merely discussed by the hosts, and unsupported creator or producer credits for media records not represented canonically in the repository.

Potential standalone records for *Hunt for the Skinwalker*, *Patient Seventeen*, *UFO Revolution*, and *Investigation Alien* remain future content opportunities. They were not created during this relationship-only enrichment batch.

## Source basis

- Official WEAPONIZED Jellyfish UAP reporting.
- Jeremy Corbell’s official Extraordinary Beliefs filmography.
- Official Skinwalker Ranch presentation record featuring George Knapp.
- Official WEAPONIZED reporting on the Immaculate Constellation submission and hearing support.

## Validation requirements

- Reciprocal discovery regenerated from all retained and new edges.
- Unique connection counts rebuilt from the graph.
- Duplicate-card suppression retained.
- No duplicate entities created.
- All existing valid content and unrelated relationships preserved.
