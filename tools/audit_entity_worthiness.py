#!/usr/bin/env python3
"""V23.5E Entity Worthiness Audit (analysis only, read-only)."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,zipfile
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from xml.sax.saxutils import escape

RELEASE='V23.5E.1'; BASE='V23.5E'
CURATOR_APPROVED_TYPES={
 'podcast_series','podcast_episode','hearing','case','witness_profile','whistleblower_profile',
 'research_document','government_report','research_paper','book','documentary_film','legislation'
}
TYPE_ALIASES={
 'historical_ufo_case':'case','congressional_hearing':'hearing','witness':'witness_profile',
 'whistleblower':'whistleblower_profile','report':'government_report','paper':'research_paper',
 'documentary':'documentary_film','film':'documentary_film'
}
TYPE_PRIOR={'case':20,'person':17,'witness_profile':18,'whistleblower_profile':18,'hearing':18,'legislation':20,'research_document':16,'government_report':19,'research_paper':17,'book':14,'documentary_film':13,'document':15,'topic':13,'organization':10,'publication':9,'podcast_series':10,'interview':8,'podcast_episode':7,'timeline_event':5,'claim':2}
SCORING_PROFILES={
 'person':{'independent':.12,'convergence':.24,'significance':.24,'educational':.08,'uniqueness':.12,'demand':.20},
 'witness_profile':{'independent':.13,'convergence':.22,'significance':.23,'educational':.10,'uniqueness':.14,'demand':.18},
 'whistleblower_profile':{'independent':.13,'convergence':.22,'significance':.23,'educational':.10,'uniqueness':.14,'demand':.18},
 'podcast_episode':{'independent':.22,'convergence':.18,'significance':.13,'educational':.18,'uniqueness':.17,'demand':.12},
 'research_paper':{'independent':.22,'convergence':.12,'significance':.23,'educational':.13,'uniqueness':.20,'demand':.10},
 'government_report':{'independent':.18,'convergence':.15,'significance':.25,'educational':.12,'uniqueness':.15,'demand':.15},
 'organization':{'independent':.12,'convergence':.23,'significance':.25,'educational':.08,'uniqueness':.12,'demand':.20},
 'default':{'independent':.18,'convergence':.19,'significance':.21,'educational':.12,'uniqueness':.16,'demand':.14}
}
GENERIC_TERMS=re.compile(r'\b(platform|hosting|hosted|distribution|publisher|network|news outlet|website|service|administrative|category)\b',re.I)
SIGNIFICANCE=re.compile(r'\b(historic|landmark|official|congress|government|military|scientific|investigation|report|act|hearing|incident|case|witness|whistleblower|research|evidence|disclosure|uap|ufo)\b',re.I)
WEAK_SUMMARY=re.compile(r'knowledge.graph entity referenced|claim or editorial framing presented|was published\.?$',re.I)

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def clean(v): return str(v or '').strip()
def title(e): return clean(e.get('name') or e.get('title') or e.get('id'))
def digest(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def rels(e): return [r for r in e.get('relationships',[]) if isinstance(r,dict) and r.get('target')]
def evidence_count(e): return len(e.get('referenceSources') or [])+len(e.get('officialLinks') or [])
def norm_type(e):
 t=clean(e.get('type')).lower() or 'unknown'
 return TYPE_ALIASES.get(t,t)

def clamp(n): return max(0,min(100,int(round(n))))

def snapshot(root):
 paths=[]
 for raw in ('data/entities','entities/generated','data/knowledge-graph-schema.json','data/related-content.json'):
  p=root/raw
  if p.is_file(): paths.append(p)
  elif p.exists(): paths.extend(x for x in p.rglob('*') if x.is_file())
 return {str(p.relative_to(root)):digest(p) for p in sorted(paths)}

def test(label,score,positive,negative):
 return {'test':label,'score':clamp(score),'result':'pass' if score>=65 else ('borderline' if score>=45 else 'fail'),'assessment':positive if score>=65 else negative}

def evaluate(e,byid,outgoing,incoming):
 eid=e['id']; typ=norm_type(e); name=title(e); summary=clean(e.get('summary'))
 out=outgoing.get(eid,[]); inc=incoming.get(eid,[]); all_edges=out+inc
 unique_neighbors={x['other'] for x in all_edges}; edge_types={x['type'] for x in all_edges}
 inbound=len(inc); outbound=len(out); refs=evidence_count(e)
 text=' '.join([name,summary,clean(e.get('status')),clean(e.get('eventCategory')),clean(e.get('profileStatus'))])
 weak=bool(WEAK_SUMMARY.search(summary)); generic=bool(GENERIC_TERMS.search(text))
 independent=clamp(20+min(len(summary),300)/5+refs*7+min(outbound,8)*3-(25 if weak else 0))
 convergence=clamp(10+min(len(unique_neighbors),20)*3+min(len(edge_types),8)*5+min(inbound,20)*2)
 significance=clamp(TYPE_PRIOR.get(typ,5)*2+(20 if SIGNIFICANCE.search(text) else 0)+min(inbound,10)*2+(10 if refs>=2 else 0)-(18 if generic else 0))
 educational=clamp(15+min(len(summary),350)/5+(15 if refs else 0)+(10 if outbound>=2 else 0)-(20 if weak else 0))
 uniqueness=clamp(25+TYPE_PRIOR.get(typ,5)*2+(10 if inbound>=2 else 0)+(10 if outbound>=2 else 0)-(25 if generic else 0))
 demand=clamp(20+min(inbound,15)*4+TYPE_PRIOR.get(typ,5)*2)
 profile=SCORING_PROFILES.get(typ,SCORING_PROFILES['default'])
 score=clamp(independent*profile['independent']+convergence*profile['convergence']+significance*profile['significance']+educational*profile['educational']+uniqueness*profile['uniqueness']+demand*profile['demand'])
 if weak: score=clamp(score-5)
 if generic: score=clamp(score-8)
 approved=typ in CURATOR_APPROVED_TYPES
 destination_eligibility='Qualifies as a destination' if approved or score>=55 else 'Better represented as supporting knowledge or metadata'
 evidence={
  'summaryLength':len(summary),'outgoingRelationships':outbound,'incomingRelationships':inbound,
  'uniqueRelatedEntities':len(unique_neighbors),'relationshipTypes':sorted(edge_types),'referenceSourceCount':refs,
  'officialLinkCount':len(e.get('officialLinks') or []),'weakSummaryPattern':weak,'genericInfrastructureSignal':generic,
  'sampleRelatedEntities':[{'id':x,'name':title(byid[x]),'type':norm_type(byid[x])} for x in sorted(unique_neighbors)[:8] if x in byid]
 }
 narrative=(f"{name} is evaluated against the {typ} baseline. It has {len(unique_neighbors)} related entities, "
            f"{len(edge_types)} relationship types, {refs} source or official-link references, and a type-weighted score of {score}/100.")
 if approved: narrative += ' Its entity type is curator-approved, so destination eligibility is retained and the audit evaluates quality, tier, and prominence only.'
 elif destination_eligibility.startswith('Better'): narrative += ' Current evidence does not yet establish sufficient independent destination value.'
 return {
  'entityId':eid,'entityName':name,'entityType':typ,'curatorApprovedEntityType':approved,
  'destinationEligibility':destination_eligibility,'entityTypeBaseline':typ,
  'scoreComponents':{'independentResearchDepth':independent,'relationshipConvergence':convergence,'longTermSignificance':significance,'educationalValue':educational,'knowledgeUniqueness':uniqueness,'researchDemand':demand},
  'scoringProfile':profile,'entityWorthinessScore':score,'entityTypePercentile':None,
  'destinationTier':None,'navigationProminence':None,'researchValueNarrative':narrative,
  'supportingEvidence':evidence,'justification':narrative,'humanRecommendation':'pending','humanDecision':'pending'
 }

def assign_percentiles_and_governance(rows):
 groups=defaultdict(list)
 for r in rows: groups[r['entityType']].append(r)
 for typ,rs in groups.items():
  ordered=sorted(rs,key=lambda x:(x['entityWorthinessScore'],x['entityName'].lower()))
  n=len(ordered)
  for i,r in enumerate(ordered):
   r['entityTypePercentile']=100.0 if n==1 else round(i/(n-1)*100,1)
  for r in rs:
   p=r['entityTypePercentile']; score=r['entityWorthinessScore']; approved=r['curatorApprovedEntityType']; eligible=r['destinationEligibility'].startswith('Qualifies')
   if eligible and ((p>=92 and score>=72) or (typ in {'case','hearing','person','government_report','legislation'} and p>=85 and score>=68)):
    tier='Tier 1 — Core Research Destination'
   elif eligible:
    tier='Tier 2 — Research Destination'
   elif score>=35 and not r['supportingEvidence']['genericInfrastructureSignal']:
    tier='Tier 3 — Supporting Knowledge Object'
   else:
    tier='Tier 4 — Contextual Metadata'
   r['destinationTier']=tier
   if tier.startswith('Tier 1'):
    nav='Core Navigation' if p>=97 and score>=80 else 'Featured Research Gateway'
   elif tier.startswith('Tier 2'):
    nav='Frequently Recommended' if p>=70 else 'Search-Driven Discovery'
   elif tier.startswith('Tier 3'):
    nav='Contextual Discovery'
   else:
    nav='Contextual Discovery'
   r['navigationProminence']=nav
   if approved:
    r['humanRecommendation']='Retain destination; review tier, prominence, completeness, and relationship quality'
   elif tier.startswith(('Tier 1','Tier 2')):
    r['humanRecommendation']='Recommend destination status'
   elif tier.startswith('Tier 3'):
    r['humanRecommendation']='Review as supporting knowledge object'
   else:
    r['humanRecommendation']='Review as contextual metadata'

def xcol(n):
 s=''
 while n: s=chr(65+(n-1)%26)+s; n=(n-1)//26
 return s

def make_xlsx(path,sheets):
 """Dependency-free review workbook for GitHub Actions."""
 now=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
 ct=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
 for i in range(len(sheets)): ct.append(f'<Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
 ct.append('</Types>')
 wb=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>']; rel=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
 for i,(name,_) in enumerate(sheets,1): wb.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>'); rel.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
 wb.append('</sheets></workbook>'); rel.append(f'<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
 styles='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="10"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="10"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/></patternFill></fill></fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FFD9E2F3"/></left><right style="thin"><color rgb="FFD9E2F3"/></right><top style="thin"><color rgb="FFD9E2F3"/></top><bottom style="thin"><color rgb="FFD9E2F3"/></bottom><diagonal/></border></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="3"><xf/><xf fontId="1" fillId="2" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="center"/></xf><xf borderId="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0"/></cellStyles></styleSheet>'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml',''.join(ct)); z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'); z.writestr('xl/workbook.xml',''.join(wb)); z.writestr('xl/_rels/workbook.xml.rels',''.join(rel)); z.writestr('xl/styles.xml',styles)
  for si,(name,rows) in enumerate(sheets,1):
   maxc=max(len(r) for r in rows); widths=[min(42,max(10,max(len(clean(r[c])) for r in rows if c<len(r))+2)) for c in range(maxc)]
   xml=['<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>']
   for c,w in enumerate(widths,1): xml.append(f'<col min="{c}" max="{c}" width="{w}" customWidth="1"/>')
   xml.append('</cols><sheetData>')
   for ri,row in enumerate(rows,1):
    xml.append(f'<row r="{ri}" ht="{28 if ri==1 else 42}" customHeight="1">')
    for ci,val in enumerate(row,1):
     ref=f'{xcol(ci)}{ri}'; style=1 if ri==1 else 2
     if isinstance(val,(int,float)) and not isinstance(val,bool): xml.append(f'<c r="{ref}" s="{style}"><v>{val}</v></c>')
     else: xml.append(f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{escape(clean(val))}</t></is></c>')
    xml.append('</row>')
   end=f'{xcol(maxc)}{len(rows)}'; xml.append(f'</sheetData><autoFilter ref="A1:{end}"/></worksheet>'); z.writestr(f'xl/worksheets/sheet{si}.xml',''.join(xml))

def write_md(path,title_text,rows):
 lines=[f'# {title_text}','', '> **Analysis only. Every recommendation is pending human review.**','',f'Entities: **{len(rows)}**','', '| Entity | Type | Approved | Score | Percentile | Tier | Navigation |','|---|---|---|---:|---:|---|---|']
 for r in rows: lines.append(f"| {r['entityName'].replace('|','\\|')} | {r['entityType']} | {'Yes' if r['curatorApprovedEntityType'] else 'No'} | {r['entityWorthinessScore']} | {r['entityTypePercentile']} | {r['destinationTier']} | {r['navigationProminence']} |")
 path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--output-dir',default='reports/v23-5e-1'); args=ap.parse_args(); root=Path(args.root).resolve(); outdir=root/args.output_dir; outdir.mkdir(parents=True,exist_ok=True)
 before=snapshot(root)
 entities=[]
 for p in sorted((root/'data/entities').glob('*.json')):
  d=load(p)
  if d.get('id') and d.get('type'): entities.append(d)
 byid={e['id']:e for e in entities}; outgoing=defaultdict(list); incoming=defaultdict(list)
 for e in entities:
  for r in rels(e):
   edge={'other':r['target'],'type':clean(r.get('type') or 'related_to')}; outgoing[e['id']].append(edge); incoming[r['target']].append({'other':e['id'],'type':edge['type']})
 rows=[evaluate(e,byid,outgoing,incoming) for e in entities]; assign_percentiles_and_governance(rows); rows.sort(key=lambda r:(r['entityType'],r['entityName'].lower()))
 hierarchy={f'tier{i}':[] for i in range(1,5)}
 for r in rows: hierarchy['tier'+r['destinationTier'][5]].append(r)
 governance={t:{'curatorApproved':t in CURATOR_APPROVED_TYPES,'evaluationMode':'quality-and-placement' if t in CURATOR_APPROVED_TYPES else 'full-destination-worthiness'} for t in sorted({r['entityType'] for r in rows})}
 nav=defaultdict(list)
 for r in rows: nav[r['navigationProminence']].append(r)
 category={}
 for typ in sorted({r['entityType'] for r in rows}):
  rs=[r for r in rows if r['entityType']==typ]; tiers=Counter(r['destinationTier'].split(' — ')[0] for r in rs); navs=Counter(r['navigationProminence'] for r in rs)
  category[typ]={'entityCount':len(rs),'automaticallyAcceptedDestinationEntities':sum(r['curatorApprovedEntityType'] for r in rs),'fullyAuditedEntities':sum(not r['curatorApprovedEntityType'] for r in rs),'tier1':tiers['Tier 1'],'tier2':tiers['Tier 2'],'tier3':tiers['Tier 3'],'tier4':tiers['Tier 4'],'averageScore':round(sum(r['entityWorthinessScore'] for r in rs)/len(rs),1),'averagePercentile':round(sum(r['entityTypePercentile'] for r in rs)/len(rs),1),'navigationRecommendations':dict(navs)}
 after=snapshot(root); changed=before!=after
 result={'release':RELEASE,'baseRepository':BASE,'productionType':'Knowledge Graph Governance Refinement (analysis only)','generatedAt':datetime.now(timezone.utc).isoformat(),'humanReviewRequired':True,'repositoryMutationDetected':changed,'philosophy':{'destinationEligibilitySeparateFromNavigationProminence':True,'fourTierDestinationHierarchy':True,'entityTypeGovernance':True,'entityTypeBaselines':True},'inventory':{'entitiesEvaluated':len(rows),'entityTypes':dict(Counter(r['entityType'] for r in rows))},'results':rows,'categoryAnalysis':category}
 (outdir/'entity-worthiness-philosophy-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 (outdir/'destination-hierarchy-report.json').write_text(json.dumps(hierarchy,indent=2)+'\n',encoding='utf-8')
 (outdir/'entity-type-governance-report.json').write_text(json.dumps(governance,indent=2)+'\n',encoding='utf-8')
 (outdir/'navigation-prominence-report.json').write_text(json.dumps(dict(nav),indent=2)+'\n',encoding='utf-8')
 (outdir/'entity-type-baseline-analysis.json').write_text(json.dumps(category,indent=2)+'\n',encoding='utf-8')
 write_md(outdir/'DESTINATION_HIERARCHY_REPORT.md','V23.5E.1 — Destination Hierarchy Report',rows)
 write_md(outdir/'NAVIGATION_PROMINENCE_REPORT.md','V23.5E.1 — Navigation Prominence Report',rows)
 headers=['Entity Name','Entity ID','Entity Type','Curator-Approved Entity Type','Destination Eligibility','Destination Tier','Navigation Prominence','Entity-Type Baseline','Entity Worthiness Score','Entity-Type Percentile','Research Value Narrative','Supporting Evidence','Justification','Human Recommendation','Human Decision']
 table=[]
 for r in rows:
  ev=r['supportingEvidence']; table.append([r['entityName'],r['entityId'],r['entityType'],'Yes' if r['curatorApprovedEntityType'] else 'No',r['destinationEligibility'],r['destinationTier'],r['navigationProminence'],r['entityTypeBaseline'],r['entityWorthinessScore'],r['entityTypePercentile'],r['researchValueNarrative'],f"{ev['incomingRelationships']} inbound; {ev['outgoingRelationships']} outbound; {ev['uniqueRelatedEntities']} related entities; {ev['referenceSourceCount']} references",r['justification'],r['humanRecommendation'],'pending'])
 with (outdir/'enhanced-human-review-workbook.csv').open('w',newline='',encoding='utf-8-sig') as f: csv.writer(f).writerows([headers]+table)
 summary_rows=[['Entity Type','Count','Auto Accepted','Fully Audited','Tier 1','Tier 2','Tier 3','Tier 4','Average Score','Average Percentile','Navigation Recommendations']]+[[t,v['entityCount'],v['automaticallyAcceptedDestinationEntities'],v['fullyAuditedEntities'],v['tier1'],v['tier2'],v['tier3'],v['tier4'],v['averageScore'],v['averagePercentile'],json.dumps(v['navigationRecommendations'],sort_keys=True)] for t,v in category.items()]
 guide=[['Field','Meaning'],['Destination Eligibility','Binary destination decision; curator-approved types automatically qualify.'],['Destination Tier','Four-tier research role, independent of page existence.'],['Navigation Prominence','Discoverability recommendation only.'],['Entity-Type Percentile','Relative standing only among entities of the same type.'],['Human Decision','Always pending; the audit performs no graph changes.']]
 make_xlsx(outdir/'enhanced-human-review-workbook.xlsx',[('Entity Review',[headers]+table),('Category Analysis',summary_rows),('Review Guide',guide)])
 validation={'release':RELEASE,'baseRepository':BASE,'repositoryUnchanged':not changed,'entityJsonUnchanged':not changed,'relationshipsUnchanged':not changed,'renderedPagesUnchanged':not changed,'schemasUnchanged':not changed,'classificationsUnchanged':not changed,'recommendationEngineUnchanged':not changed,'destinationHierarchyAdvisoryOnly':not changed,'entityTypeGovernanceAdvisoryOnly':not changed,'auditReadOnly':not changed,'allHumanDecisionsPending':all(r['humanDecision']=='pending' for r in rows),'entitiesEvaluated':len(rows)}
 (outdir/'validation-summary.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'release':RELEASE,'entitiesEvaluated':len(rows),'tier1':len(hierarchy['tier1']),'tier2':len(hierarchy['tier2']),'tier3':len(hierarchy['tier3']),'tier4':len(hierarchy['tier4']),'repositoryMutationDetected':changed},indent=2))
 if changed: raise SystemExit('Protected repository content changed during audit')

if __name__=='__main__': main()
