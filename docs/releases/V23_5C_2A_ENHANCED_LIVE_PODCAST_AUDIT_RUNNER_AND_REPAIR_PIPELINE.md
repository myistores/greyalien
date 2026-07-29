# V23.5C.2A — Enhanced Live Podcast Audit Runner and Repair Pipeline

## Purpose

V23.5C.2A converts the V23.5C.1 connectivity runner into a controlled evidence and repair-preparation system for WEAPONIZED, Need to Know, MERGED, and Somewhere in the Skies.

## HTTP classification

HTTP responses are application-level results. HTTP 404 is `validation_failed`; other 4xx/5xx responses are also validation failures unless a platform-specific temporary state applies. `network_unavailable` is limited to DNS, timeout, TLS, refusal, unreachable-host, and routing failures.

## YouTube rate limits

YouTube requests use a two-request semaphore. HTTP 429 responses are retried up to three times. The runner honors `Retry-After`; otherwise it uses exponential backoff plus randomized jitter. Every attempt and wait is recorded. Exhausted 429s become `temporarily_unverifiable`, never proof of removal.

## `link.chtbl.com`

The hostname is classified as a tracking wrapper. A failed wrapper becomes `retired_tracking_wrapper`; this does not imply the underlying episode is unavailable. Wrapper retirement is automatically approvable only when an identical verified official destination exists. Otherwise official replacement research is required.

## Evidence and metadata

Reachable responses preserve bounded evidence: HTTP status, redirect chain, final URL, page and HTML titles, canonical URL, Open Graph values, description, publisher/show identity, episode title/number/date, duration, platform, media identifier, availability, content type, RSS parse state, soft-404 result, and retrieval timestamp. Full page copies are not retained.

## Platform and content type

The final destination determines actual platform. The runner distinguishes YouTube videos/playlists/channels, Apple episode/show pages, Spotify episode/show pages, hosted pages, archives, generic homepages, RSS feeds, unavailable media, and tracking wrappers.

## Identity comparison

Expected and captured text are normalized for case, punctuation, typographic marks, common platform words, episode prefixes, and number formatting. Identity outcomes are `confirmed`, `probable_match`, `mismatch`, or `insufficient_evidence`. An explicit episode-number conflict always produces a mismatch. Only confirmed destinations can become verified direct episodes.

Need to Know Episodes 13 and 14 are protected by the same explicit number comparison. The test suite contains an off-by-one regression test.

## Repair approvals

Automatic approval is limited to safe equivalence changes: HTTP-to-HTTPS, equivalent canonical destinations, duplicate wrapper retirement, platform/label correction, duplicate suppression, archive reclassification, and canonical normalization. Identity conflicts, removed/private media, unofficial replacements, unrelated redirects, ambiguous archives, and different identifiers require human review.

## Human review

The artifact includes `human_review_queue.json` and `human_review_report.md`. Each item identifies the failure, evidence, proposed action, alternatives, and required reviewer decision.

## Transaction and rollback

Approved proposal IDs are imported from a separate approval document. The transaction preview records affected media records, proposed changes, permitted fields, and rollback values. Public content fields are outside the permitted field list. The application helper writes all approved changes to a new output and restores the original data if any operation fails.

Repository deployments should additionally snapshot the complete media tree and record SHA-256 hashes before replacing source files. The evidence workflow intentionally generates an empty no-repair transaction preview.

## Preferred destinations and rendering

The transaction layer is prepared to modify only media URL/classification/verification/preference fields. After approved changes are applied, the deployed V23.5A resolver and existing repository regeneration commands should be run so hosted episode, YouTube, Apple, Spotify, other episode, archive, and RSS priorities are recalculated. Failed, temporary, channel, playlist, and retired-wrapper records are ineligible for promotion.

## GitHub Actions

The workflow validates the inventory, installs pinned dependencies, runs controlled live validation and retries, generates evidence and reports, generates transaction and rollback previews, validates schemas and completeness, runs tests, records the repository revision, and uploads the complete artifact. It has read-only repository permissions and never commits or deploys.

## Known platform limitations

Some platforms serve consent, bot-protection, regional, JavaScript-only, private, or age-restricted responses that do not expose enough metadata. These remain `reachable_unconfirmed` or `temporarily_unverifiable` and require review. No ambiguous result is automatically applied.
