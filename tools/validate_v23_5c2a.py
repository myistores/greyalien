#!/usr/bin/env python3
"""Repository-level structural validation for V23.5C.2A."""
from __future__ import annotations
import json, py_compile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errs=[]
required=[
 '.github/workflows/live-podcast-media-audit.yml',
 'tools/podcast_media_audit/run_enhanced_audit.py',
 'tools/podcast_media_audit/audit_pipeline/http_client.py',
 'tools/podcast_media_audit/audit_pipeline/identity.py',
 'tools/podcast_media_audit/audit_pipeline/proposals.py',
 'tools/podcast_media_audit/audit_pipeline/transaction.py',
 'tools/podcast_media_audit/schema/enhanced_validation_result.schema.json',
 'tools/podcast_media_audit/schema/repair_proposal.schema.json',
 'docs/releases/V23_5C_2A_ENHANCED_LIVE_PODCAST_AUDIT_RUNNER_AND_REPAIR_PIPELINE.md',
 'data/media-audit/v23.5c.1/jobs/validation_jobs.json'
]
for rel in required:
 if not (ROOT/rel).exists(): errs.append('missing '+rel)
for p in (ROOT/'tools/podcast_media_audit').rglob('*.py'):
 try: py_compile.compile(str(p),doraise=True)
 except Exception as e: errs.append(f'compile {p.relative_to(ROOT)}: {e}')
try:
 jobs=json.loads((ROOT/'data/media-audit/v23.5c.1/jobs/validation_jobs.json').read_text())['jobs']
 if len(jobs)!=491: errs.append(f'unexpected job count {len(jobs)}')
 for ep,vid in ((13,'HRCT_ddq39U'),(14,'YOjSBPfmoIM')):
  if not any(j.get('seriesId')=='need-to-know-podcast' and j.get('episodeNumber')==ep and vid in j.get('normalizedUrl','') for j in jobs): errs.append(f'Need to Know {ep} fixture missing')
except Exception as e: errs.append('inventory: '+str(e))
wf=(ROOT/'.github/workflows/live-podcast-media-audit.yml').read_text()
for token in ('data/media-audit/v23.5c.1/jobs/validation_jobs.json','upload-artifact@v4','transaction-preview','human_review_report.md'):
 if token not in wf: errs.append('workflow missing '+token)
print('V23.5C.2A repository validation:', 'PASS' if not errs else 'FAIL')
for e in errs: print(' -',e)
sys.exit(1 if errs else 0)
