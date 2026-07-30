from __future__ import annotations
import json,sys
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator
from .common import read_json,normalize_url

def validate_schema(doc_path,schema_path):
 doc=read_json(doc_path); schema=read_json(schema_path); errors=sorted(Draft202012Validator(schema).iter_errors(doc),key=lambda e:list(e.path))
 if errors: raise ValueError('\n'.join(f"{list(e.path)}: {e.message}" for e in errors[:25]))
def validate_jobs_results(jobs_path,results_path):
 jobs=read_json(jobs_path); results=read_json(results_path); jl=jobs.get('jobs',jobs); rl=results.get('results',results)
 jids=[j['jobId'] for j in jl]; rids=[r['jobId'] for r in rl]
 assert len(jids)==len(set(jids)),'duplicate job IDs'; assert len(rids)==len(set(rids)),'duplicate result IDs'; assert set(jids)==set(rids),'job/result completeness mismatch'
 by={j['jobId']:j for j in jl}
 for r in rl:
  j=by[r['jobId']]; assert r.get('initialUrl')==j.get('initialUrl'),'URL mismatch'; assert r.get('finalValidationStatus') in {'verified','reachable_unconfirmed','identity_mismatch','validation_failed','network_unavailable','temporarily_unverifiable','retired_tracking_wrapper','soft_404'}
  if r.get('httpStatus')==404: assert r['finalValidationStatus']=='validation_failed'
  if r.get('httpStatus') is not None: assert r['finalValidationStatus']!='network_unavailable'
  if 'link.chtbl.com' in (r.get('initialUrl') or '') and r.get('failureReason') in {'dns_resolution_failure','temporary_routing_failure','unreachable_host'}: assert r['finalValidationStatus']=='retired_tracking_wrapper'
  assert normalize_url(j.get('normalizedUrl') or j.get('initialUrl'))
def validate_proposals(path):
 ps=read_json(path)['proposals']; ids=[p['proposalId'] for p in ps]; assert len(ids)==len(set(ids))
 for p in ps:
  assert p['approvalCategory'] in {'automatic','human_review_required'}
  if p['approvalCategory']=='automatic': assert p['proposedAction'] in {'upgrade_http_to_https','adopt_equivalent_canonical','retire_duplicate_tracking_wrapper','correct_platform','correct_label','suppress_duplicate','reclassify_archive','normalize_canonical_url'}
def validate_outputs(root):
 root=Path(root); required=['live_validation_results.json','live_validation_summary.json','repair_proposals.json','automatic_approval_queue.json','human_review_queue.json','human_review_report.md','cross_series_live_audit_report.json','transaction_preview.json','rollback_snapshot.json','apple_metadata_extraction_report.json','apple_identity_comparison_report.json','repair_proposal_deduplication_report.json']
 missing=[x for x in required if not (root/x).exists()]
 if missing: raise FileNotFoundError(f'missing outputs: {missing}')
 for p in root.rglob('*.json'): json.loads(p.read_text(encoding='utf-8'))
