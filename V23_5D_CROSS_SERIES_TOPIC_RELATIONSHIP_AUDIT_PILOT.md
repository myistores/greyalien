# V23.5D — Cross-Series Topic Relationship Audit (Pilot)

**Base Repository:** V23.5C.4 (deployed)  
**Production Type:** Knowledge-graph audit (analysis only)  
**Repository mutation:** None

## Production Objective

Audit the existing knowledge graph for the topics UFO History, Historical UFO Cases, and Witness Accounts across every previously ingested episode of WEAPONIZED, Need to Know, MERGED, and Somewhere in the Skies.

This release creates a reproducible audit runner, machine-readable results, a human-readable review report, and a validation gate. It does not modify entity JSON, relationships, schemas, rendering, classifications, pages, or knowledge-graph content.

## Added Files

- `tools/audit_cross_series_topics.py` — deterministic, read-only audit runner.
- `tools/validate_v23_5d.py` — release validator and repository-mutation guard.
- `data/audits/v23-5d/audit_config.json` — topic definitions and bounded pilot candidate set.
- `reports/v23-5d/V23_5D_CROSS_SERIES_TOPIC_RELATIONSHIP_AUDIT.md` — human review report.
- `reports/v23-5d/audit-results.json` — machine-readable findings and inventory.
- `reports/v23-5d/candidate-decisions.csv` — proposed and rejected candidate review sheet.
- `validation/v23_5d_tests.log` — validation evidence.

## Run Commands

```bash
python tools/audit_cross_series_topics.py
python tools/validate_v23_5d.py
```

## Human Review Gate

All proposed relationships remain unapproved. A separate bounded implementation release is required after line-by-line human review. V23.5D contains no relationship-writing or import path.
