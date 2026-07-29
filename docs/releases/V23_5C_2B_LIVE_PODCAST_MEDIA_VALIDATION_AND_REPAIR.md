# V23.5C.2B — Live Podcast Media Validation and Repair

## Purpose

V23.5C.2B performs the first network-backed validation of the 491 deterministic podcast-media jobs prepared by V23.5C.1. The workflow validates live destinations, records redirects and metadata, checks episode identity, classifies failures, and produces approval-gated repair proposals.

## Running the production workflow

1. Push this repository to GitHub.
2. Open **Actions**.
3. Select **V23.5C.2B Live Podcast Media Validation**.
4. Choose **Run workflow**.
5. Leave `job_limit` blank to process all 491 jobs.
6. Download the artifact named `V23.5C.2B-live-podcast-media-validation-evidence` after the run completes.

A small integer in `job_limit` may be used for a bounded connectivity test before the full run.

## Evidence generated

The workflow produces live validation results, summary statistics, automatic and human-review queues, repair proposals, series reports, transaction preview, rollback snapshot, logs, unit-test output, and the exact repository revision used for the run.

## Approval boundary

The live-validation workflow does not silently alter production media. Repair proposals remain approval-gated. The no-repair approval file is used during the evidence run to prove that transaction preview and rollback generation function without importing unreviewed changes.

## Repair methodology

Repairs must be supported by live evidence and episode-identity comparison. Direct official episode destinations outrank archives, RSS feeds, playlists, channels, show pages, and homepages. Unofficial uploads, mirrors, clips, and excerpts are ineligible.

## Knowledge-graph protection

The workflow reads the prepared podcast media inventory and entity metadata but does not modify entities, relationships, topics, summaries, timelines, claims, canonical IDs, classifications, or routing.

## Required follow-up

After the evidence artifact is reviewed, approved proposal IDs must be recorded in a dedicated approvals document. Approved changes can then be imported transactionally, followed by preferred-media regeneration, page rebuilding, and repository-wide validation.
