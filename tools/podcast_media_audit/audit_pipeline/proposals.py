from __future__ import annotations
from collections import defaultdict
from .common import canonical_key,now_iso,stable_id
AUTO_ACTIONS={'upgrade_http_to_https','adopt_equivalent_canonical','retire_duplicate_tracking_wrapper','correct_platform','correct_label','suppress_duplicate','reclassify_archive','normalize_canonical_url'}

def proposal_for(job,result,known_verified=None):
 known_verified=known_verified or set(); status=result['finalValidationStatus']; ev=result.get('evidence',{}); ident=result.get('identityComparison',{}); proposals=[]
 def add(action,actual,approval='human_review_required',replacement=None,reason=None):
  original=job.get('initialUrl') or job.get('normalizedUrl'); pid=stable_id('repair',job['jobId'],action,replacement or result.get('finalUrl'))
  proposals.append({'proposalId':pid,'jobId':job['jobId'],'affectedMediaRecord':job.get('sourceInventoryRecordIds',[]),'affectedEntities':[job.get('entityId')],'originalUrl':original,'validatedFinalUrl':result.get('finalUrl'),'replacementUrl':replacement,'originalClassification':{'platform':job.get('platform'),'destinationType':job.get('destinationType')},'actualClassification':actual,'expectedIdentity':ident.get('expected',{}),'capturedIdentity':ident.get('captured',{}),'supportingEvidence':{'httpStatus':result.get('httpStatus'),'redirectHistory':result.get('redirectHistory',[]),'evidenceSummary':result.get('evidenceSummary'),'identityStatus':ident.get('status'),'failureReason':result.get('failureReason')},'proposedAction':action,'approvalCategory':approval,'automaticallyApprovable':approval=='automatic','rollbackData':{'restoreUrl':original,'restorePlatform':job.get('platform'),'restoreDestinationType':job.get('destinationType'),'restoreLabel':job.get('label')},'reason':reason,'generationTimestamp':now_iso()})
 original=job.get('initialUrl',''); final=result.get('finalUrl') or original
 if original.startswith('http://') and final.startswith('https://') and canonical_key(original)==canonical_key(final): add('upgrade_http_to_https',{'platform':ev.get('platform'),'destinationType':ev.get('destinationType')},'automatic',final)
 if ev.get('platform') and job.get('platform') and ev['platform'].lower()!=str(job['platform']).lower() and status not in {'network_unavailable','temporarily_unverifiable'}: add('correct_platform',{'platform':ev['platform'],'destinationType':ev.get('destinationType')},'automatic',final)
 if ev.get('destinationType') and job.get('destinationType') and ev['destinationType'].lower()!=str(job['destinationType']).lower():
  safe=ev['destinationType'] in {'series archive','podcast series or show'} and str(job.get('destinationType')).lower() in {'episode','direct episode'} and ident.get('status')!='confirmed'
  add('reclassify_archive' if safe else 'correct_destination_type',{'platform':ev.get('platform'),'destinationType':ev['destinationType']},'automatic' if safe else 'human_review_required',final)
 if status=='retired_tracking_wrapper':
  duplicate=any(canonical_key(x)==canonical_key(final) for x in known_verified if x)
  add('retire_duplicate_tracking_wrapper' if duplicate else 'research_official_replacement',{'platform':'tracking or redirect wrapper','destinationType':'tracking wrapper'},'automatic' if duplicate else 'human_review_required',None,'Broken link.chtbl.com wrapper is not proof the episode is unavailable.')
 elif status=='validation_failed': add('research_or_deactivate_failed_destination',{'platform':ev.get('platform') or job.get('platform'),'destinationType':ev.get('destinationType') or job.get('destinationType')},'human_review_required')
 elif status=='identity_mismatch': add('replace_or_reclassify_identity_mismatch',{'platform':ev.get('platform'),'destinationType':ev.get('destinationType')},'human_review_required',None,'Expected and captured episode identity do not match.')
 elif status=='soft_404': add('replace_or_deactivate_soft_404',{'platform':ev.get('platform'),'destinationType':'unavailable media'},'human_review_required')
 return proposals

def build_queues(proposals):
 auto=[p for p in proposals if p['approvalCategory']=='automatic']; human=[p for p in proposals if p['approvalCategory']!='automatic']
 return {'automatic':auto,'human':human}
