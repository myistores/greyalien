from __future__ import annotations
import copy, os
from pathlib import Path
from .common import now_iso,read_json,write_json,sha256_file,stable_id
PERMITTED={'url','normalizedUrl','canonicalUrl','platform','destinationType','label','verificationStatus','validationTimestamp','preferred','preferredRank','preferredDestinationEligibility','duplicateSuppressed'}

def _entity_files(repo:Path, proposal:dict):
 files=[]
 for eid in proposal.get('affectedEntities',[]):
  p=repo/'data/entities'/f'{eid}.json'
  if p.exists(): files.append(p)
 return files

def preview(repo_root,proposals_path,approval_path,out_dir):
 repo=Path(repo_root).resolve(); pdoc=read_json(proposals_path); proposals={p['proposalId']:p for p in pdoc['proposals']}; approvals=read_json(approval_path)
 approved=set(approvals.get('approvedProposalIds',[])); unknown=approved-set(proposals)
 if unknown: raise ValueError('Unknown approved proposal IDs: '+', '.join(sorted(unknown)))
 selected=[proposals[x] for x in sorted(approved)]
 manifest={'schemaVersion':'1.0.0','transactionId':stable_id('tx',now_iso(),len(selected)),'createdAt':now_iso(),'repositoryRoot':str(repo),'repositoryRevision':os.getenv('GITHUB_SHA') or 'local-uncommitted','approvedProposalIds':sorted(approved),'proposalDocumentHash':sha256_file(Path(proposals_path)),'approvalDocumentHash':sha256_file(Path(approval_path)),'changes':[],'sourceFiles':[],'permittedFields':sorted(PERMITTED),'status':'preview','partialImportAuthorized':False}
 seen=set()
 for p in selected:
  for f in _entity_files(repo,p):
   key=str(f.relative_to(repo))
   if key not in seen: manifest['sourceFiles'].append({'path':key,'sha256Before':sha256_file(f)}); seen.add(key)
  for target in p.get('affectedMediaRecord',[]):
   manifest['changes'].append({'proposalId':p['proposalId'],'recordId':target,'entityIds':p.get('affectedEntities',[]),'action':p['proposedAction'],'replacementUrl':p.get('replacementUrl') or p.get('validatedFinalUrl'),'actualClassification':p.get('actualClassification',{}),'rollbackData':p.get('rollbackData'),'permittedFieldsOnly':True})
 out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
 write_json(out/'transaction_preview.json',manifest)
 write_json(out/'rollback_snapshot.json',{'schemaVersion':'1.0.0','transactionId':manifest['transactionId'],'createdAt':now_iso(),'repositoryRevision':manifest['repositoryRevision'],'sourceFiles':manifest['sourceFiles'],'records':[c['rollbackData'] for c in manifest['changes']],'completeTransactionRollbackRequired':True})
 return manifest

def apply_media_json(media_file,manifest_path,output_file):
 src=read_json(media_file); before=copy.deepcopy(src); manifest=read_json(manifest_path); by_id={}
 def walk(x):
  if isinstance(x,dict):
   rid=x.get('id') or x.get('mediaId') or x.get('recordId')
   if rid:by_id[str(rid)]=x
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(src)
 try:
  for change in manifest['changes']:
   rec=by_id.get(str(change['recordId']))
   if rec is None: raise KeyError(f"media record not found: {change['recordId']}")
   action=change['action']; replacement=change.get('replacementUrl'); actual=change.get('actualClassification') or {}
   if action in {'upgrade_http_to_https','adopt_equivalent_canonical','normalize_canonical_url'} and replacement: rec.update({'url':replacement,'normalizedUrl':replacement,'canonicalUrl':replacement})
   elif action=='correct_platform': rec['platform']=actual.get('platform',rec.get('platform'))
   elif action=='correct_label': rec['label']=actual.get('label',rec.get('label'))
   elif action=='reclassify_archive': rec['destinationType']='series'
   elif action in {'retire_duplicate_tracking_wrapper','suppress_duplicate'}: rec['duplicateSuppressed']=True; rec['preferredDestinationEligibility']=False
   else: raise ValueError(f"action requires human implementation: {action}")
  write_json(output_file,src)
 except Exception:
  write_json(output_file,before); raise
 return {'applied':len(manifest['changes']),'output':str(output_file),'sha256Before':sha256_file(Path(media_file)),'sha256After':sha256_file(Path(output_file))}
