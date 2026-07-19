# V18.4 — Research Accelerator

V18.4 adds a local, review-first production tool that converts official podcast episode pages, saved HTML, and optional transcripts into structured GreyAlien ingestion drafts.

## Purpose

The accelerator reduces repetitive research formatting while preserving editorial control. It does not publish and does not write to `data/entities`.

## Workflow

1. Copy `data/research-accelerator/templates/batch-manifest.json`.
2. Add five or more official episode URLs.
3. Optionally save official HTML pages or transcripts locally.
4. Run:

```bash
python tools/research_accelerator.py path/to/batch-manifest.json
```

5. Review each Markdown checklist and JSON review report.
6. Correct titles, dates, summaries, guest/subject roles, new entities, and claims.
7. Copy only approved JSON records into a clean batch folder.
8. Dry-run and import through the existing transactional system.

```bash
python tools/import_batch.py path/to/approved-batch --dry-run
python tools/import_batch.py path/to/approved-batch
```

## Accelerator outputs

Each run creates:

- `drafts/` — structured episode JSON drafts
- `reviews/` — machine-readable and human-readable review reports
- `raw/` — fetched official HTML when network access is used
- `run-report.json` — batch metrics and warnings

## Safety rules

- Human review is mandatory.
- Automatically matched people default to `referenced_subject`, never guest.
- Official episode pages remain Reference Sources, not Official Links for unrelated entities.
- Claims are not generated automatically without explicit source-grounded review.
- The accelerator does not modify the live graph.
