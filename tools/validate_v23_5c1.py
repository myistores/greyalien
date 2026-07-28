#!/usr/bin/env python3
import json,sys,hashlib,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'data/media-audit/v23.5c.1'
def load(p):return json.loads(p.read_text())
errs=[]
inv=load(A/'inventory/media_inventory.json')['records']; jobs=load(A/'jobs/validation_jobs.json')['jobs']; meta=load(A/'validator_metadata.json')
if meta['networkValidation']!='not_run':errs.append('network status must be not_run')
if any(j.get('networkStatus')!='not_run' for j in jobs):errs.append('job falsely reports live status')
if len(inv)!=meta['inventoryRecords'] or len(jobs)!=meta['uniqueJobs']:errs.append('reconciliation mismatch')
ids=[j['jobId'] for j in jobs]
if len(ids)!=len(set(ids)):errs.append('duplicate job IDs')
for j in jobs:
 expected='media-audit-'+hashlib.sha256((j['entityId']+'|'+j['normalizedUrl']).encode()).hexdigest()[:16]
 if j['jobId']!=expected:errs.append('non-deterministic job id '+j['jobId'])
 if j['destinationType']=='episode' and 'episodeIdentity' not in j['checks']:errs.append('episode job missing identity check')
 if j['destinationType']=='feed' and 'feedParse' not in j['checks']:errs.append('feed job missing parse check')
# regression checks
for ep,vid in [(13,'HRCT_ddq39U'),(14,'YOjSBPfmoIM')]:
 matches=[j for j in jobs if j['seriesId']=='need-to-know-podcast' and j.get('episodeNumber')==ep and vid in j['normalizedUrl']]
 if not matches:errs.append(f'Need to Know Episode {ep} regression URL missing')
# Acast remains flagged and not altered
for r in inv:
 if 'acast.com' in r['originalUrl'] and not r['retiredDomainIndicator']:errs.append('Acast URL not flagged retired')
# result schema statuses
schema=load(A/'schema/validation_result.schema.json')
allowed=schema['properties']['finalValidationStatus']['enum']
for x in ('passed','failed','network_unavailable','not_run','human_review_required'):
 if x not in allowed:errs.append('missing result status '+x)
# deterministic regeneration
before=(A/'jobs/validation_jobs.json').read_bytes();subprocess.run([sys.executable,str(ROOT/'tools/audit_podcast_media.py'),'--prepare-jobs'],check=True,stdout=subprocess.DEVNULL);after=(A/'jobs/validation_jobs.json').read_bytes()
if before!=after:errs.append('job generation not deterministic')
print('V23.5C.1 validation:', 'PASS' if not errs else 'FAIL')
for e in errs:print(' -',e)
sys.exit(1 if errs else 0)
