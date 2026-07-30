# V23.5C.2B.1 — Apple Podcasts Identity and Proposal Deduplication

This corrective audit-engine release improves Apple Podcasts episode/show classification, metadata provenance, identity scoring, and repair-proposal consolidation. It changes no production podcast media data, preferred destinations, rendered pages, or knowledge-graph records.

## Apple URL anatomy

Apple show IDs are read from `/id<showId>`. Direct episode IDs are read from the `i=<episodeId>` query parameter. Episode identifiers are preserved through URL normalization, storefront redirects, and canonicalization. A show ID without an episode ID is classified as a show page.

## Metadata extraction

Apple metadata is extracted in descending-confidence order from embedded JSON and JSON-LD, Open Graph metadata, standard metadata, canonical links, and document titles. `Apple Podcasts` is treated as platform branding, not as the show title. Each extracted field records its source and confidence.

## Identity verification

The validator compares the repository series, episode title, episode number, publication date, and available Apple identifiers. Conflicting series or episode numbers force a mismatch. Apple episode IDs establish episode-level destination type but do not alone prove episode identity.

## Proposal consolidation

Each affected validation job produces one corrective proposal per genuinely distinct action. Related findings are retained as `supportingReasons`; distinct replacement URLs are retained as nested `replacementCandidates`. Reports distinguish affected jobs, unique proposals, candidates, and collapsed findings.

## Operator verification

Run the V23.5C.2B workflow with `job_limit` set to `10`. Confirm ten effective jobs and ten results, correct Apple show-title extraction, retained episode IDs, show-page degradation detection, and noninflated proposal totals. Leave all approvals empty. Only after that confirmation should the full 491-job run be executed.
