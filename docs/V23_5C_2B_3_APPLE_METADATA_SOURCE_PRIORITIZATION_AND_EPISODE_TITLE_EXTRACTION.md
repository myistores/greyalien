# V23.5C.2B.3 — Apple Metadata Source Prioritization and Episode Title Extraction

## Production objective

This focused corrective patch prevents Apple platform branding and generic interface controls from being selected as podcast identity metadata. It is limited to the Apple Podcasts parser, focused regression fixtures, tests, and release documentation.

## Corrected defects

- `@ApplePodcasts` and normalized Apple Podcasts branding variants are rejected for both show and episode identity fields.
- Generic interface values such as `Play`, `Listen Now`, and `Preview` are rejected as episode titles when they are exact control labels.
- Legitimate titles containing `Apple`, `Play`, or `Preview` remain valid.
- Candidate selection now evaluates validity before confidence and applies deterministic source priority as a tie-breaker.
- Structured Apple/JSON metadata cannot be displaced by Twitter Card or DOM control text.
- Branding-only pages return no show title and record `insufficient_metadata:showTitle`.

## Diagnostics

Existing candidate and decision-path structures are preserved. Rejected candidates record the field, source, confidence, value, and one of these reasons:

- `platform_branding`
- `generic_ui_label`
- `social_media_handle`

Final accepted values continue to record their source and confidence.

## Regression coverage

Permanent fixtures cover Twitter branding, branding-only fallback, generic Play controls, embedded structured precedence, JSON-LD fallback, valid titles containing Play, valid podcast names containing Apple, Open Graph fallback when Twitter is branding, and repeated Play UI text alongside structured metadata.

## Architecture boundary

No workflow, schema, proposal, transaction, production podcast data, generated HTML, media collection, preferred destination, entity, relationship, or knowledge-graph file is changed.

## Validation

- `python -m compileall tools/podcast_media_audit`
- `PYTHONPATH=tools/podcast_media_audit python -m unittest discover -s tools/podcast_media_audit/tests -v`

All 28 tests pass.
