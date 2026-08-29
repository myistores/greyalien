# V23.6D.2 — VASCO Scientific Challenge + News Lifecycle & Permanent Research Ingestion

**Base Repository:** V23.6E — Science & Technology First Live Research Topic  
**Feature Lineage:** V23.6D — Latest UAP News + Research Library  
**Production Type:** Cross-Gateway Research / News Lifecycle Enhancement  
**Primary Gateway:** Latest UAP News  
**Permanent Destination:** Research Library + Knowledge Graph  
**News Classification:** Current / non-Landmark  
**Knowledge Classification:** Permanent

## Production Summary

V23.6D.2 implements the scoped objectives 1–25 using the VASCO/POSS1 scientific dispute as the first explicit lifecycle case. The August 28, 2026 International Business Times UK report is retained as the timely secondary news surface. The peer-reviewed accepted manuscript by Wesley Andrés Watters, Laura Dominé, Sarah Little, Cameron Pratt, Kevin H. Knuth and Matthew Szenher, published online by Cambridge University Press for the *Publications of the Astronomical Society of Australia* on July 23, 2026 (DOI 10.1017/pasa.2026.10230), is the permanent Research Library object.

The release deliberately rejects categorical secondary-headline framing. GreyAlien records the PASA paper as a methodological challenge and separately preserves VASCO rebuttal/replication context.

## Core Architectural Advancement

**News can age; knowledge does not.**

The News Record now supports independent lifecycle and knowledge-permanence state:

- `newsStatus`: `current`, `archived`, or `landmark`
- `knowledgePermanence`: `permanent` or `transient`

The VASCO news record begins as `current`, is explicitly non-Landmark, is archive-eligible, and has automatic aging disabled. Its extracted publication, claims, entities and graph relationships are permanent.

## Ingestion Manifest

### News
- `2026-08-28-ibtimes-vasco-nuclear-test-challenge`

### Permanent Research
- `publication-2026-critical-evaluation-poss1e-technosignatures`

### Claims
- `claim-vasco-transients-nuclear-test-correlation` — original reported correlation, status: disputed
- `claim-watters-vasco-methodological-challenge` — peer-reviewed methodological challenge, preserved as a research finding under active dispute

### New Knowledge-Graph Entities
- `vasco-project`
- `beatriz-villarroel`
- `wesley-watters`
- `kevin-knuth`
- `technosignatures`
- `palomar-observatory`

### Reused Existing Entities
- `galileo-project`
- `scientific-investigation`
- `nuclear-facility-uap-incursions`

## Source Hierarchy

1. Cambridge/PASA accepted manuscript — primary scientific source.
2. VASCO project response/replication summary — competing research context.
3. International Business Times UK — timely secondary news surface.

## Research Integrity

The permanent research record includes methodology, principal findings, limitations and research implications. It states that the critique evaluates previously published datasets closely related to those used in the VASCO studies and does not establish the nature of every historical plate feature. The original correlation claim remains visible as a disputed claim rather than being overwritten.

## UI / Cross-Gateway Behavior

- Latest UAP News exposes the August 28 news article and a **Permanent Research Record** link.
- Research Library exposes the PASA paper as a permanent peer-reviewed accepted manuscript.
- Research Library links back to the related news coverage.
- Entity pages expose publication, researcher, project, facility, topic and claim connections through the existing graph runtime.
- No automatic archive threshold, bulk historical VASCO ingestion, broad taxonomy redesign or unrelated cleanup is introduced.

## Compatibility Protection

The V23.6E Image & Video Analysis research topic, Science & Technology gateway, scientific-methods collection, entity runtime JavaScript, graph core and V23.6D.1 runtime reliability code are protected byte-for-byte. Existing five news JSON records are also protected byte-for-byte. Only the entity-shell cache-bust query is updated to V23.6D.2.
