#!/usr/bin/env python3
"""V23.5C.1 offline podcast media audit engine and future live-job runner."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,sys,time,urllib.request,urllib.error
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode

ROOT=Path(__file__).resolve().parents[1]
ENTITIES=ROOT/'data/entities'; AUDIT=ROOT/'data/media-audit/v23.5c.1'
VERSION='23.5C.1-1.0.0'; GENERATED='2026-07-28T00:00:00Z'
SERIES={'weaponized-podcast':'WEAPONIZED','need-to-know-podcast':'Need to Know','merged-podcast':'MERGED','somewhere-in-the-skies-podcast':'Somewhere in the Skies'}
TRACK={'fbclid','gclid','mc_cid','mc_eid','si','feature','pp','ref','source'}
FIELDS=('officialMedia','mediaLinks','officialLinks','referenceSources')

def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def norm(url):
 s=urlsplit((url or '').strip()); host=(s.hostname or '').lower()
 if host.startswith('www.'):host=host[4:]
 if host in {'m.youtube.com','music.youtube.com'}:host='youtube.com'
 path=re.sub('/+','/',s.path or '/')
 q=parse_qsl(s.query,keep_blank_values=True)
 if host=='youtu.be':
  vid=path.strip('/').split('/')[0]; host='youtube.com'; path='/watch'; q=[('v',vid)]
 if host=='youtube.com' and (path.startswith('/embed/') or path.startswith('/shorts/')):
  vid=path.split('/')[2]; path='/watch'; q=[('v',vid)]
 out=[]
 for k,v in q:
  lk=k.lower()
  if lk.startswith('utm_') or lk in TRACK:continue
  if host=='youtube.com' and path=='/watch' and lk not in {'v','list'}:continue
  out.append((k,v))
 out.sort(); path=path.rstrip('/') or '/'
 return urlunsplit(('https',host,path,urlencode(out),'')).rstrip('/')
def platform(url,label=''):
 h=urlsplit(url).hostname or ''; t=(h+' '+label).lower()
 if 'youtube' in t or 'youtu.be' in t:return 'YouTube'
 if 'podcasts.apple.com' in t:return 'Apple Podcasts'
 if 'spotify' in t:return 'Spotify'
 if any(x in t for x in ('rss','feed','xml')):return 'RSS'
 if 'weaponizedpodcast.com' in t:return 'WEAPONIZED website'
 return h.removeprefix('www.') or 'Official media'
def infer_dest(url,label='',existing=None):
 if existing in {'episode','series','playlist','channel','feed'}:return existing
 u=url.lower(); t=label.lower()
 if u.endswith(('.rss','.xml')) or '/feed' in u or 'rss' in t:return 'feed'
 if 'playlist' in u or 'playlist' in t:return 'playlist'
 if '/channel/' in u or re.search(r'youtube\.com/@[^/]+/?$',u):return 'channel'
 if 'watch?v=' in u or '/episode' in u or 'episode' in t:return 'episode'
 return 'series'
def media_type(p,d):
 if d=='feed':return 'feed'
 if p=='YouTube':return 'video'
 if p in {'Apple Podcasts','Spotify'}:return 'audio'
 return 'web_page'
def series_id(d):
 sid=d.get('seriesId') or d.get('podcastSeriesId')
 if sid in SERIES:return sid
 eid=d.get('id','')
 for s in SERIES:
  token=s.replace('-podcast','')
  if token in eid:return s
 return d.get('id') if d.get('id') in SERIES else None
def episode_no(d): return d.get('episodeNumber') or d.get('episode') or d.get('number')
def title(d): return d.get('title') or d.get('name') or d.get('episodeTitle') or d.get('id')
def urls_from(d):
 for f in FIELDS:
  val=d.get(f,[]) or []
  if not isinstance(val,list):continue
  for i,x in enumerate(val):
   if isinstance(x,str):yield f,i,{'url':x,'label':''}
   elif isinstance(x,dict) and x.get('url'):yield f,i,x

def build():
 AUDIT.mkdir(parents=True,exist_ok=True)
 docs=[]
 for p in sorted(ENTITIES.glob('*.json')):
  try:d=load(p)
  except Exception:continue
  sid=series_id(d)
  if sid in SERIES and (d.get('type') in {'podcast_episode','podcast_series'} or d.get('officialMedia') is not None): docs.append((p,d,sid))
 by_sid=defaultdict(list)
 for p,d,sid in docs:
  if d.get('type')=='podcast_episode':by_sid[sid].append(d)
 for sid in by_sid:by_sid[sid].sort(key=lambda d:(episode_no(d) or 9999,d.get('date','')))
 neigh={}
 for sid,arr in by_sid.items():
  for i,d in enumerate(arr):
   neigh[d['id']]={'previous': {'number':episode_no(arr[i-1]),'title':title(arr[i-1])} if i else None,'next': {'number':episode_no(arr[i+1]),'title':title(arr[i+1])} if i+1<len(arr) else None}
 inv=[]; n=0
 for p,d,sid in docs:
  for f,i,x in urls_from(d):
   n+=1; u=x['url']; nu=norm(u); lab=x.get('label',''); plat=x.get('platform') or platform(u,lab); dest=infer_dest(u,lab,x.get('destinationType'))
   rec={'inventoryId':f'inv-{n:05d}','seriesId':sid,'podcastSeries':SERIES[sid],'entityId':d.get('id'),'entityType':d.get('type'),'episodeNumber':episode_no(d),'episodeTitle':title(d),'publicationDate':d.get('date') or d.get('publicationDate'),'originalField':f,'originalFieldIndex':i,'originalLabel':lab,'originalUrl':u,'normalizedUrl':nu,'canonicalUrlKey':hashlib.sha256(nu.encode()).hexdigest()[:20],'platform':plat,'destinationType':dest,'mediaType':x.get('mediaType') or media_type(plat,dest),'official':bool(x.get('official',f!='referenceSources')),'existingVerificationStatus':x.get('verificationStatus') or x.get('validationStatus') or 'legacy_unspecified','existingApprovalState':'approved' if x.get('approved',True) else 'unapproved','existingPreferredRank':x.get('preferredRank'),'existingPreferred':bool(x.get('preferred',False)),'migrationProvenance':x.get('migrationProvenance') or {'legacyField':f,'legacyIndex':i},'retiredDomainIndicator':bool(re.search(r'(^|\.)acast\.com$',urlsplit(u).hostname or '',re.I)),'reviewRequirement':'network_check_pending','inventoryTimestamp':GENERATED,'inventoryGeneratorVersion':VERSION}
   inv.append(rec)
 groups=defaultdict(list)
 for r in inv:groups[(r['entityId'],r['normalizedUrl'])].append(r)
 for j,(_,arr) in enumerate(sorted(groups.items()),1):
  gid=f'dup-{j:05d}' if len(arr)>1 else None
  for k,r in enumerate(arr):r['duplicateGroup']=gid;r['duplicateStatus']='authoritative' if k==0 and gid else ('duplicate' if gid else 'unique')
 jobs=[]
 for (eid,nu),arr in sorted(groups.items()):
  r=next((x for x in arr if x['originalField']=='officialMedia'),arr[0]); jid='media-audit-'+hashlib.sha256((eid+'|'+nu).encode()).hexdigest()[:16]
  checks=['http','redirect','soft404','platformIdentity','seriesIdentity']
  if r['destinationType']=='episode':checks+=['episodeIdentity','episodeNumber','title','publicationDate','offByOne']
  if r['destinationType']=='feed':checks+=['feedParse','episodePresence']
  job={'jobId':jid,'sourceInventoryRecordIds':[x['inventoryId'] for x in arr],'seriesId':r['seriesId'],'podcastSeries':r['podcastSeries'],'entityId':eid,'entityType':r['entityType'],'episodeNumber':r['episodeNumber'],'episodeTitle':r['episodeTitle'],'publicationDate':r['publicationDate'],'expectedGuests':[],'neighbors':neigh.get(eid),'platform':r['platform'],'destinationType':r['destinationType'],'mediaType':r['mediaType'],'initialUrl':r['originalUrl'],'normalizedUrl':nu,'canonicalUrlKey':r['canonicalUrlKey'],'expectedAuthorityType':'official','expectedPodcast':r['podcastSeries'],'checks':checks,'retryPolicy':{'maxAttempts':3,'backoffSeconds':[2,5]},'timeoutPolicy':{'seconds':20},'requestMethodPolicy':['HEAD','GET'],'resultSchemaVersion':'1.0','validatorVersion':VERSION,'jobCreatedAt':GENERATED,'networkStatus':'not_run'}
  jobs.append(job)
  for x in arr:x['validationJobId']=jid
 identities=[{k:j.get(k) for k in ('jobId','seriesId','entityId','episodeNumber','episodeTitle','publicationDate','expectedGuests','neighbors','expectedPodcast')} for j in jobs if j['destinationType']=='episode']
 dups=[{'duplicateGroup':a[0]['duplicateGroup'],'entityId':a[0]['entityId'],'normalizedUrl':a[0]['normalizedUrl'],'inventoryIds':[x['inventoryId'] for x in a]} for a in groups.values() if len(a)>1]
 dump(AUDIT/'inventory/media_inventory.json',{'version':VERSION,'generatedAt':GENERATED,'networkValidation':'not_run','records':inv})
 with (AUDIT/'inventory/media_inventory.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=[k for k,v in inv[0].items() if not isinstance(v,(dict,list))]);w.writeheader();w.writerows([{k:v for k,v in r.items() if not isinstance(v,(dict,list))} for r in inv])
 dump(AUDIT/'inventory/duplicate_groups.json',{'groups':dups})
 dump(AUDIT/'jobs/validation_jobs.json',{'version':VERSION,'generatedAt':GENERATED,'networkValidation':'not_run','jobs':jobs})
 dump(AUDIT/'identity/expected_episode_identity.json',{'records':identities})
 dump(AUDIT/'results/validation_results.json',{'schemaVersion':'1.0','networkValidation':'not_run','results':[]})
 dump(AUDIT/'repairs/repair_proposals.json',{'version':VERSION,'status':'not_generated','proposals':[]})
 dump(AUDIT/'preferred/preferred_resolution_preview.json',{'status':'preview_only','records':[{'entityId':j['entityId'],'currentUrl':j['initialUrl'],'ifPass':j['normalizedUrl'],'ifFail':'resolver_fallback_pending_live_results'} for j in jobs]})
 dump(AUDIT/'rollback/rollback_manifest.json',{'release':'V23.5C.1','base':'V23.5B','removePaths':['data/media-audit/v23.5c.1','tools/audit_podcast_media.py','tools/validate_v23_5c1.py'],'mediaRecordsChanged':False,'publicPreferredDestinationsChanged':False})
 schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Podcast media live-validation result','type':'object','required':['jobId','validationTimestamp','validatorVersion','initialUrl','finalValidationStatus'],'properties':{'jobId':{'type':'string'},'validationTimestamp':{'type':'string'},'validatorVersion':{'type':'string'},'networkEnvironment':{'type':'string'},'initialUrl':{'type':'string'},'httpStatus':{'type':['integer','null']},'redirectChain':{'type':'array'},'finalUrl':{'type':['string','null']},'soft404Result':{'enum':['passed','failed','not_run','human_review_required']},'finalValidationStatus':{'enum':['passed','failed','network_unavailable','not_run','human_review_required']},'failureReason':{'type':['string','null']}}}
 dump(AUDIT/'schema/validation_result.schema.json',schema)
 dump(AUDIT/'schema/repair_proposal.schema.json',{'type':'object','required':['jobId','action','approvalStatus'],'properties':{'jobId':{'type':'string'},'action':{'enum':['keep_verified','update_canonical_url','reclassify','deactivate','retire','reject','select_existing_fallback','research_required','human_review']},'approvalStatus':{'enum':['pending','approved','rejected']}}})
 meta={'auditEngineVersion':VERSION,'release':'V23.5C.1','base':'V23.5B','generatedAt':GENERATED,'networkValidation':'not_run','inventoryRecords':len(inv),'uniqueJobs':len(jobs),'duplicateOccurrences':sum(len(a)-1 for a in groups.values()),'entityCount':len(docs)};dump(AUDIT/'validator_metadata.json',meta)
 # reports
 stats={}
 for sid,name in SERIES.items():
  rr=[r for r in inv if r['seriesId']==sid]; jj=[j for j in jobs if j['seriesId']==sid]; ents={r['entityId']:r['entityType'] for r in rr}
  s={'podcastSeries':name,'seriesEntities':sum(v=='podcast_series' for v in ents.values()),'episodeEntities':sum(v=='podcast_episode' for v in ents.values()),'mediaOccurrences':len(rr),'uniqueCanonicalUrls':len(jj),'validationJobs':len(jj),'destinationTypes':dict(Counter(r['destinationType'] for r in rr)),'platforms':dict(Counter(r['platform'] for r in rr)),'duplicateOccurrences':len(rr)-len(jj),'retiredDomainIndicators':sum(r['retiredDomainIndicator'] for r in rr),'networkValidation':'not_run','offlinePreparation':'complete','v23_5c_2Readiness':'ready'};stats[sid]=s;dump(AUDIT/f'reports/{sid}.json',s)
  lines=[f'# {name} V23.5C.1 Audit Preparation Report','',f'- Episode entities inventoried: {s["episodeEntities"]}',f'- Series entities inventoried: {s["seriesEntities"]}',f'- Media occurrences: {s["mediaOccurrences"]}',f'- Unique validation jobs: {s["validationJobs"]}',f'- Duplicate occurrences: {s["duplicateOccurrences"]}',f'- Retired-domain indicators: {s["retiredDomainIndicators"]}',f'- Network validation: **not run**',f'- V23.5C.2 readiness: **ready**'];(AUDIT/f'reports/{sid}.md').write_text('\n'.join(lines)+'\n')
 combined={'version':VERSION,'generatedAt':GENERATED,'networkValidation':'not_run','totals':{'entities':len(docs),'inventoryRecords':len(inv),'validationJobs':len(jobs),'duplicateOccurrences':len(inv)-len(jobs)},'series':stats,'byPlatform':dict(Counter(r['platform'] for r in inv)),'byDestinationType':dict(Counter(r['destinationType'] for r in inv))};dump(AUDIT/'reports/combined_report.json',combined)
 (AUDIT/'reports/combined_report.md').write_text(f"# V23.5C.1 Combined Audit Preparation Report\n\n- Entities inventoried: {len(docs)}\n- Media occurrences: {len(inv)}\n- Unique validation jobs: {len(jobs)}\n- Duplicate occurrences suppressed from repeated jobs: {len(inv)-len(jobs)}\n- Production network validation: **not run**\n- Offline preparation: **complete**\n\nNo destination received a new live-verification result in V23.5C.1.\n")
 return meta

def import_results(path):
 jobs={j['jobId']:j for j in load(AUDIT/'jobs/validation_jobs.json')['jobs']}; data=load(Path(path)); results=data.get('results',data if isinstance(data,list) else [])
 bad=[]
 for r in results:
  j=jobs.get(r.get('jobId'))
  if not j or norm(r.get('initialUrl',''))!=j['normalizedUrl']:bad.append(r.get('jobId'))
 if bad:raise SystemExit('Rejected unknown, stale, or URL-mismatched results: '+','.join(map(str,bad)))
 dump(AUDIT/'results/imported_validation_results.json',{'importedAt':datetime.now(timezone.utc).isoformat(),'results':results});print(f'Imported {len(results)} result(s) for review; no media data changed.')
def live(jobfile):
 jobs=load(Path(jobfile) if jobfile else AUDIT/'jobs/validation_jobs.json')['jobs']; out=[]
 for j in jobs:
  try:
   req=urllib.request.Request(j['initialUrl'],headers={'User-Agent':'GreyAlienMediaAuditor/1.0'})
   with urllib.request.urlopen(req,timeout=20) as r: status=r.status; final=r.geturl(); body=r.read(200000).decode('utf-8','ignore').lower()
   soft=any(x in body for x in ('page not found','video unavailable','content is not available','private video'))
   fs='failed' if status>=400 or soft else 'human_review_required'
   out.append({'jobId':j['jobId'],'validationTimestamp':datetime.now(timezone.utc).isoformat(),'validatorVersion':VERSION,'networkEnvironment':'external','initialUrl':j['initialUrl'],'httpStatus':status,'redirectChain':[],'finalUrl':final,'soft404Result':'failed' if soft else 'passed','finalValidationStatus':fs,'failureReason':'soft_404' if soft else None})
  except Exception as e:out.append({'jobId':j['jobId'],'validationTimestamp':datetime.now(timezone.utc).isoformat(),'validatorVersion':VERSION,'networkEnvironment':'external','initialUrl':j['initialUrl'],'httpStatus':None,'redirectChain':[],'finalUrl':None,'soft404Result':'not_run','finalValidationStatus':'network_unavailable','failureReason':str(e)})
 dump(AUDIT/'results/live_validation_results.json',{'schemaVersion':'1.0','results':out})

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--inventory',action='store_true');ap.add_argument('--prepare-jobs',action='store_true');ap.add_argument('--report',action='store_true');ap.add_argument('--live',action='store_true');ap.add_argument('--job-file');ap.add_argument('--import-results');ap.add_argument('--propose-repairs',action='store_true');a=ap.parse_args()
 if a.import_results:return import_results(a.import_results)
 if a.live:return live(a.job_file)
 m=build();print(json.dumps(m,indent=2))
if __name__=='__main__':main()
