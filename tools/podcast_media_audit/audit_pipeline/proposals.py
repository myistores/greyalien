from __future__ import annotations
from .common import canonical_key,now_iso,stable_id
AUTO_ACTIONS={'upgrade_http_to_https','adopt_equivalent_canonical','retire_duplicate_tracking_wrapper','correct_platform','correct_label','suppress_duplicate','reclassify_archive','normalize_canonical_url'}

def proposal_for(job,result,known_verified=None):
 known_verified=known_verified or set(); status=result['finalValidationStatus']; ev=result.get('evidence',{}); ident=result.get('identityComparison',{}); original=job.get('initialUrl') or job.get('normalizedUrl'); final=result.get('finalUrl') or original
 findings=[]
 if original.startswith('http://') and final.startswith('https://') and canonical_key(original)==canonical_key(final):findings.append(('upgrade_http_to_https','http_redirected_to_equivalent_https','automatic',final))
 if ev.get('platform') and job.get('platform') and ev['platform'].lower()!=str(job['platform']).lower() and status not in {'network_unavailable','temporarily_unverifiable'}:findings.append(('correct_platform','captured_platform_differs','automatic',final))
 expected_direct=str(job.get('destinationType','')).lower() in {'episode','direct episode','hosted episode page'}
 actual_show=ev.get('destinationType')=='podcast series or show'
 if expected_direct and actual_show:findings.append(('research_official_episode_replacement','direct_episode_degraded_to_show_page','human_review_required',None))
 elif ev.get('destinationType') and job.get('destinationType') and ev['destinationType'].lower()!=str(job['destinationType']).lower():findings.append(('correct_destination_type','destination_type_differs','human_review_required',final))
 if status=='retired_tracking_wrapper':findings.append(('research_official_replacement','broken_tracking_wrapper','human_review_required',None))
 elif status=='validation_failed':findings.append(('research_or_deactivate_failed_destination','http_validation_failed','human_review_required',None))
 elif status=='identity_mismatch':findings.append(('replace_or_reclassify_identity_mismatch','episode_identity_mismatch','human_review_required',None))
 elif status=='soft_404':findings.append(('replace_or_deactivate_soft_404','soft_404_detected','human_review_required',None))
 elif status=='reachable_unconfirmed' and expected_direct:findings.append(('review_unconfirmed_episode_identity','episode_identity_unconfirmed','human_review_required',None))
 if not findings:return []
 automatic=all(x[2]=='automatic' for x in findings)
 primary=next((x for x in findings if x[2]!='automatic'),findings[0])
 replacements=[]
 for action,reason,approval,replacement in findings:
  if replacement and canonical_key(replacement)!=canonical_key(original) and all(canonical_key(x['url'])!=canonical_key(replacement) for x in replacements):replacements.append({'url':replacement,'action':action,'confidence':ident.get('identityScore',0)})
 reasons=[]
 for x in findings:
  if x[1] not in reasons:reasons.append(x[1])
 action=primary[0]; replacement=primary[3]
 key=stable_id('proposal',job['jobId'],canonical_key(original),canonical_key(replacement or ''),action)
 return [{'proposalId':key,'deduplicationKey':key,'jobId':job['jobId'],'affectedMediaRecord':job.get('sourceInventoryRecordIds',[]),'affectedEntities':[job.get('entityId')],'originalUrl':original,'currentUrl':original,'validatedFinalUrl':final,'replacementUrl':replacement,'replacementCandidates':replacements,'originalClassification':{'platform':job.get('platform'),'destinationType':job.get('destinationType')},'currentClassification':{'platform':ev.get('platform'),'destinationType':ev.get('destinationType')},'actualClassification':{'platform':ev.get('platform'),'destinationType':ev.get('destinationType')},'expectedClassification':{'platform':job.get('platform'),'destinationType':job.get('destinationType')},'expectedIdentity':ident.get('expected',{}),'capturedIdentity':ident.get('captured',{}),'identityFindings':ident,'supportingEvidence':{'httpStatus':result.get('httpStatus'),'redirectHistory':result.get('redirectHistory',[]),'evidenceSummary':result.get('evidenceSummary'),'identityStatus':ident.get('status'),'failureReason':result.get('failureReason')},'primaryReason':primary[1],'supportingReasons':reasons,'mergedProposalCount':len(findings),'mergedReasons':reasons,'proposedAction':action,'approvalCategory':'automatic' if automatic else 'human_review_required','approvalStatus':'pending','automaticallyApprovable':automatic,'confidence':ident.get('identityScore',0),'rollbackData':{'restoreUrl':original,'restorePlatform':job.get('platform'),'restoreDestinationType':job.get('destinationType'),'restoreLabel':job.get('label')},'reason':primary[1],'generationTimestamp':now_iso()}]

def consolidate_proposals(proposals):
 merged={}
 for p in proposals:
  key=p['deduplicationKey']
  if key not in merged:merged[key]=p;continue
  cur=merged[key];cur['mergedProposalCount']+=p.get('mergedProposalCount',1)
  for r in p.get('supportingReasons',[]):
   if r not in cur['supportingReasons']:cur['supportingReasons'].append(r)
  for c in p.get('replacementCandidates',[]):
   if all(canonical_key(c['url'])!=canonical_key(x['url']) for x in cur['replacementCandidates']):cur['replacementCandidates'].append(c)
 return list(merged.values())

def build_queues(proposals):return {'automatic':[p for p in proposals if p['approvalCategory']=='automatic'],'human':[p for p in proposals if p['approvalCategory']!='automatic']}
