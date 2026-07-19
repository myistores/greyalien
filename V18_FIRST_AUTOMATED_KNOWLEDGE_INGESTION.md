# V18.0 — First Automated Knowledge Ingestion

V18.0 validates the complete GreyAlien ingestion workflow using a real WEAPONIZED episode.

## Imported records

- `2023-weaponized-episode-42` — WEAPONIZED Episode #42
- `joe-murgia` — citizen journalist and episode guest

## Research methodology

The official WEAPONIZED Episode #42 page is the primary source. The episode is represented as a discussion of:

- the inaugural Sol Foundation symposium;
- David Grusch's recent public comments;
- congressional pressure surrounding the UAP Disclosure Act of 2023;
- the Syria “Dome” UAP photograph.

Garry Nolan is represented as a discussed subject and co-host of the Sol Foundation symposium, not as an episode guest. Joe Murgia is represented as the episode guest.

## Automated workflow tested

1. Validate both records as one batch.
2. Resolve relationships across records in the batch.
3. Stage the complete site.
4. Rebuild the graph and timeline normalization.
5. Rebuild podcast and related-content indexes.
6. Generate entity pages and homepage updates.
7. Rebuild the sitemap.
8. Run all graph, podcast, rendering, and timeline validators.
9. Commit only after all checks pass.

## Import-system correction

The Phase 3 importer was updated to include the rendering-rule and timeline-normalization builders and validators introduced in V17.4 and V17.5. This ensures imports and ordinary automation runs use the same authoritative pipeline.
