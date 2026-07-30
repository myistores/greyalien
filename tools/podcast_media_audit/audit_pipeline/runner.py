from __future__ import annotations
import logging
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from .common import now_iso,read_json,write_json
from .detection import detect_platform,detect_destination_type
from .http_client import FetchConfig,fetch
from .metadata import extract
from .identity import compare_identity
from .proposals import proposal_for,consolidate_proposals,build_queues
LOG=logging.getLogger('greyalien.audit')

def classify(job,response,transport,evidence,identity,retry_exhausted):
 h=(urlsplit(job.get('initialUrl','')).hostname or '').lower()
 if transport:return ('retired_tracking_wrapper' if h=='link.chtbl.com' else 'network_unavailable',transport,'temporarily_unavailable')
 if response.status_code==429 and retry_exhausted=='rate_limit_exhausted':return ('temporarily_unverifiable','youtube_rate_limit_exhausted','temporarily_unavailable')
 if response.status_code==404:return ('validation_failed','http_404','validation_failed')
 if response.status_code>=400:return ('validation_failed',f'http_{response.status_code}','validation_failed')
 if evidence.get('soft404'):return ('soft_404','soft_404_detected','validation_failed')
 expected_direct=str(job.get('destinationType','')).lower() in {'episode','direct episode','hosted episode page'}
 if expected_direct and evidence.get('destinationType')=='podcast series or show':return ('reachable_unconfirmed','direct_episode_degraded_to_show_page','degraded_destination')
 if identity.get('status')=='mismatch':return ('identity_mismatch','episode_identity_mismatch','identity_mismatch')
 if identity.get('status')=='confirmed':return ('verified','confirmed_identity','validated')
 return ('reachable_unconfirmed','identity_not_confirmed','reachable_unconfirmed')

def run_one(job,cfg):
 url=job.get('normalizedUrl') or job.get('initialUrl'); response,attempts,transport=fetch(url,cfg)
 redirects=[]; evidence={}; identity={'status':'insufficient_evidence','expected':{},'captured':{}}
 if response is not None:
  setattr(response,'requested_url',url)
  redirects=[{'status':r.status_code,'url':r.url,'location':r.headers.get('Location')} for r in response.history]
  evidence=extract(response); identity=compare_identity(job,evidence)
 status,reason,outcome=classify(job,response,transport,evidence,identity,'rate_limit_exhausted' if response is not None and response.status_code==429 else None)
 return {'schemaVersion':'2.0.0','jobId':job['jobId'],'validationTimestamp':now_iso(),'validatorVersion':'23.5C.2B.2','networkEnvironment':'github-actions-compatible','requestedUrl':url,'initialUrl':job.get('initialUrl'),'httpStatus':response.status_code if response is not None else None,'redirectHistory':redirects,'finalUrl':response.url if response is not None else None,'responseTimestamp':now_iso(),'attempts':attempts,'finalValidationStatus':status,'validationOutcome':outcome,'failureReason':reason,'platform':evidence.get('platform') or detect_platform(url),'contentType':evidence.get('contentType'),'destinationType':evidence.get('destinationType') or detect_destination_type(url,detect_platform(url)),'evidence':evidence,'identityComparison':identity,'associatedSeries':job.get('podcastSeries'),'associatedEpisodes':[job.get('entityId')],'repairEligibility':status in {'validation_failed','retired_tracking_wrapper','identity_mismatch','soft_404','reachable_unconfirmed'},'evidenceSummary':f"{outcome}: HTTP {response.status_code if response is not None else 'transport failure'}; identity={identity.get('status')}"}

def summary(results,proposals):
 c=Counter(r['finalValidationStatus'] for r in results); affected=len({p['jobId'] for p in proposals}); candidates=sum(len(p.get('replacementCandidates',[])) for p in proposals)
 return {'schemaVersion':'2.0.0','generatedAt':now_iso(),'totalJobs':len(results),'statuses':dict(c),'platformDistribution':dict(Counter(r.get('platform') for r in results)),'contentTypeDistribution':dict(Counter(r.get('destinationType') for r in results)),'affectedJobs':affected,'uniqueRepairProposals':len(proposals),'replacementCandidates':candidates,'repairProposals':len(proposals),'automaticApprovals':sum(p['approvalCategory']=='automatic' for p in proposals),'humanReviewItems':sum(p['approvalCategory']!='automatic' for p in proposals)}

def _apple_record(job,result):
 ev=result.get('evidence',{}); ident=result.get('identityComparison',{})
 return {'jobId':job['jobId'],'originalUrl':result.get('initialUrl'),'finalUrl':result.get('finalUrl'),'canonicalUrl':ev.get('canonicalUrl'),'showId':ev.get('showId'),'episodeId':ev.get('episodeId'),'showTitle':ev.get('showTitle'),'episodeTitle':ev.get('episodeTitle'),'destinationType':ev.get('destinationType'),'metadataSources':ev.get('metadataSources',{}),'metadataSourceSelected':ev.get('metadataSourceSelected'),'rejectedMetadataCandidates':ev.get('rejectedMetadataCandidates',[]),'confidenceScore':ev.get('confidenceScore'),'finalSelectedSeries':ev.get('finalSelectedSeries'),'finalSelectedEpisode':ev.get('finalSelectedEpisode'),'parserDecisionPath':ev.get('parserDecisionPath',[]),'repositorySeries':job.get('podcastSeries'),'repositoryEpisodeTitle':job.get('episodeTitle'),'seriesMatch':ident.get('seriesMatch'),'episodeTitleMatch':ident.get('episodeTitleMatch'),'episodeNumberMatch':ident.get('episodeNumberMatch'),'dateMatch':ident.get('publicationDateMatch'),'identityScore':ident.get('identityScore',0),'validationStatus':result.get('validationOutcome'),'reviewReasons':list(dict.fromkeys((ev.get('reviewReasons') or [])+(ident.get('warnings') or [])))}

def run_inventory(jobs_path,out_dir,limit=None):
 doc=read_json(jobs_path); jobs=doc.get('jobs',doc if isinstance(doc,list) else []); selected=jobs[:limit] if limit else jobs; out=Path(out_dir); out.mkdir(parents=True,exist_ok=True); results=[]; cfg=FetchConfig()
 for i,job in enumerate(selected,1):LOG.info('job %s/%s %s',i,len(selected),job['jobId']);results.append(run_one(job,cfg))
 verified={r.get('finalUrl') for r in results if r['finalValidationStatus']=='verified'}; raw=[];byid={j['jobId']:j for j in selected}
 for r in results:raw.extend(proposal_for(byid[r['jobId']],r,verified))
 proposals=consolidate_proposals(raw);queues=build_queues(proposals);apple=[_apple_record(byid[r['jobId']],r) for r in results if r.get('platform')=='Apple Podcasts']
 write_json(out/'live_validation_results.json',{'schemaVersion':'2.0.0','inventoryVersion':doc.get('version'),'inventoryGeneratedAt':doc.get('generatedAt'),'results':results});write_json(out/'live_validation_summary.json',summary(results,proposals));write_json(out/'repair_proposals.json',{'schemaVersion':'1.0.0','proposals':proposals});write_json(out/'automatic_approval_queue.json',{'schemaVersion':'1.0.0','proposals':queues['automatic']});write_json(out/'human_review_queue.json',{'schemaVersion':'1.0.0','proposals':queues['human']});write_json(out/'apple_metadata_extraction_report.json',{'generatedAt':now_iso(),'records':apple});write_json(out/'apple_identity_comparison_report.json',{'generatedAt':now_iso(),'records':apple});write_json(out/'repair_proposal_deduplication_report.json',{'generatedAt':now_iso(),'affectedJobs':len({p['jobId'] for p in proposals}),'rawFindings':sum(p.get('mergedProposalCount',1) for p in proposals),'uniqueRepairProposals':len(proposals),'replacementCandidates':sum(len(p.get('replacementCandidates',[])) for p in proposals),'duplicatesCollapsed':sum(max(0,p.get('mergedProposalCount',1)-1) for p in proposals)});return results,proposals
