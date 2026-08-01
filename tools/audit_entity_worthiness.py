#!/usr/bin/env python3
"""V23.5E Entity Worthiness Audit (analysis only, read-only)."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,zipfile
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from xml.sax.saxutils import escape

RELEASE='V23.5E'; BASE='V23.5D.2'
DESTINATION_TYPES={'person','case','organization','hearing','legislation','document','topic'}
SUPPORTING_TYPES={'podcast_episode','interview','publication','timeline_event','claim','podcast_series'}
TYPE_PRIOR={'case':20,'person':17,'hearing':18,'legislation':20,'document':15,'topic':13,'organization':10,'publication':9,'podcast_series':8,'interview':7,'podcast_episode':5,'timeline_event':3,'claim':1}
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
def norm_type(e): return clean(e.get('type')).lower() or 'unknown'
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
 independent=min(100,20+min(len(summary),300)/5+refs*7+min(outbound,8)*3-(25 if weak else 0))
 convergence=min(100,10+min(len(unique_neighbors),20)*3+min(len(edge_types),8)*5+min(inbound,20)*2)
 significance=min(100,TYPE_PRIOR.get(typ,5)*2+(20 if SIGNIFICANCE.search(text) else 0)+min(inbound,10)*2+(10 if refs>=2 else 0)-(18 if generic else 0))
 educational=min(100,15+min(len(summary),350)/5+(15 if refs else 0)+(10 if outbound>=2 else 0)-(20 if weak else 0))
 uniqueness=min(100,25+TYPE_PRIOR.get(typ,5)*2+(10 if inbound>=2 else 0)+(10 if outbound>=2 else 0)-(25 if generic else 0))
 demand=min(100,20+min(inbound,15)*4+TYPE_PRIOR.get(typ,5)*2)
 destination=min(100,(independent*.22+convergence*.18+significance*.20+educational*.12+uniqueness*.16+demand*.12))
 if typ in {'claim','timeline_event'}: destination-=12
 if typ=='podcast_episode': destination-=7
 if typ in {'case','hearing','legislation'}: destination+=8
 if weak: destination-=8
 if generic: destination-=10
 destination=clamp(destination)
 # Better-parent inference is explainable and recommendation-only.
 parent=[]
 parent_types={'episode_of','featured_in_media','event_for','published_by','part_of','interview_of','references_document','discussed_case'}
 for edge in out:
  if edge['type'] in parent_types and edge['other'] in byid: parent.append({'id':edge['other'],'name':title(byid[edge['other']]),'relationship':edge['type']})
 better_parent_score=20 if not parent else min(95,45+len(parent)*15+(15 if typ in {'claim','timeline_event','podcast_episode'} else 0))
 if destination>=70: role='Destination Entity'; recommendation='Recommend destination status'
 elif destination>=50:
  role='Supporting Entity' if typ in SUPPORTING_TYPES or parent else 'Destination Entity'
  recommendation='Human review required'
 else:
  role='Contextual Metadata' if generic or typ in {'claim','timeline_event'} else 'Supporting Entity'
  recommendation='Recommend reduced destination prominence'
 borderline=45<=destination<70
 reasons=[]
 if convergence>=65: reasons.append(f'{len(unique_neighbors)} meaningful neighboring entities and {len(edge_types)} relationship types converge here')
 else: reasons.append(f'only {len(unique_neighbors)} neighboring entities and {len(edge_types)} relationship types currently converge here')
 if independent>=65: reasons.append('the entity has enough descriptive and sourced material to support standalone research')
 else: reasons.append('the current record has limited independent research depth')
 if significance>=65: reasons.append('its subject appears durable and significant within UAP research')
 else: reasons.append('its long-term significance is not yet strongly demonstrated')
 if parent: reasons.append('its information may be naturally encountered beneath '+', '.join(p['name'] for p in parent[:3]))
 justification=f"{name} scores {destination}/100. " + '; '.join(reasons)+'.'
 evidence={
  'summaryLength':len(summary),'outgoingRelationships':outbound,'incomingRelationships':inbound,
  'uniqueRelatedEntities':len(unique_neighbors),'relationshipTypes':sorted(edge_types),'referenceSourceCount':refs,
  'officialLinkCount':len(e.get('officialLinks') or []),'weakSummaryPattern':weak,'genericInfrastructureSignal':generic,
  'sampleRelatedEntities':[{'id':x,'name':title(byid[x]),'type':norm_type(byid[x])} for x in sorted(unique_neighbors)[:8] if x in byid]
 }
 return {
  'entityId':eid,'entityName':name,'entityType':typ,
  'researchDestinationTest':test('Research Destination',destination,'A serious researcher could intentionally browse to this subject.','Direct researcher demand is uncertain or weak.'),
  'independentKnowledgeTest':test('Independent Knowledge',independent,'The record can support meaningful standalone research.','The record is primarily supporting information or lacks depth.'),
  'relationshipConvergenceTest':test('Relationship Convergence',convergence,'Meaningful relationships naturally converge around this entity.','Relationship quantity or diversity is limited.'),
  'longTermSignificanceTest':test('Long-Term Significance',significance,'The subject is likely to remain important over time.','Current relevance may be isolated, temporary, or insufficiently established.'),
  'betterParentTest':{'score':clamp(better_parent_score),'result':'yes' if better_parent_score>=65 else ('possible' if better_parent_score>=45 else 'no'),'assessment':'A stronger parent destination may organize this information more naturally.' if parent else 'No clear better parent was identified from current relationships.','candidateParents':parent[:5]},
  'scoreFactors':{'researchDestinationValue':destination,'independentResearchDepth':clamp(independent),'relationshipConvergence':clamp(convergence),'longTermSignificance':clamp(significance),'educationalValue':clamp(educational),'historicalSignificance':clamp(significance),'crossDomainImportance':clamp((len(edge_types)*9)+TYPE_PRIOR.get(typ,5)*2),'citationFrequency':clamp(refs*15+inbound*3),'knowledgeUniqueness':clamp(uniqueness),'researchDemand':clamp(demand)},
  'entityWorthinessScore':destination,'recommendedKnowledgeRole':role,'supportingEvidence':evidence,'justification':justification,
  'borderline':borderline,'finalRecommendation':recommendation,'humanDecision':'pending'
 }

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
 lines=[f'# {title_text}','', '> **Analysis only. Every recommendation is pending human review.**','',f'Entities: **{len(rows)}**','', '| Entity | Type | Score | Role | Recommendation |','|---|---|---:|---|---|']
 for r in rows: lines.append(f"| {r['entityName'].replace('|','\\|')} | {r['entityType']} | {r['entityWorthinessScore']} | {r['recommendedKnowledgeRole']} | {r['finalRecommendation']} |")
 path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--output-dir',default='reports/v23-5e'); args=ap.parse_args(); root=Path(args.root).resolve(); outdir=root/args.output_dir; outdir.mkdir(parents=True,exist_ok=True)
 before=snapshot(root)
 entities=[]
 for p in sorted((root/'data/entities').glob('*.json')):
  d=load(p)
  if d.get('id') and d.get('type'): entities.append(d)
 byid={e['id']:e for e in entities}; outgoing=defaultdict(list); incoming=defaultdict(list)
 for e in entities:
  for r in rels(e):
   edge={'other':r['target'],'type':clean(r.get('type') or 'related_to')}; outgoing[e['id']].append(edge); incoming[r['target']].append({'other':e['id'],'type':edge['type']})
 rows=[evaluate(e,byid,outgoing,incoming) for e in entities]; rows.sort(key=lambda r:(r['entityType'],r['entityName'].lower()))
 destination=[r for r in rows if r['entityWorthinessScore']>=70]; borderline=[r for r in rows if r['borderline']]; metadata=[r for r in rows if r['recommendedKnowledgeRole']=='Contextual Metadata']
 category={}
 for typ in sorted({r['entityType'] for r in rows}):
  rs=[r for r in rows if r['entityType']==typ]; roles=Counter(r['recommendedKnowledgeRole'] for r in rs); recs=Counter(r['finalRecommendation'] for r in rs)
  category[typ]={'entityCount':len(rs),'averageWorthinessScore':round(sum(r['entityWorthinessScore'] for r in rs)/len(rs),1),'destinationWorthy':sum(r['entityWorthinessScore']>=70 for r in rs),'borderline':sum(r['borderline'] for r in rs),'metadataCandidates':roles['Contextual Metadata'],'recommendedRoles':dict(roles),'recommendations':dict(recs)}
 after=snapshot(root); changed=before!=after
 result={'release':RELEASE,'baseRepository':BASE,'productionType':'Knowledge-graph architecture audit (analysis only)','centralQuestion':'Does this subject deserve to be a destination within GreyAlien?','generatedAt':datetime.now(timezone.utc).isoformat(),'humanReviewRequired':True,'repositoryMutationDetected':changed,'inventory':{'entitiesEvaluated':len(rows),'entityTypes':dict(Counter(r['entityType'] for r in rows))},'thresholds':{'destination':70,'borderlineMinimum':45,'borderlineMaximumExclusive':70},'results':rows,'categoryAnalysis':category}
 (outdir/'entity-worthiness-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 (outdir/'destination-entity-report.json').write_text(json.dumps(destination,indent=2)+'\n',encoding='utf-8'); (outdir/'borderline-entity-report.json').write_text(json.dumps(borderline,indent=2)+'\n',encoding='utf-8'); (outdir/'contextual-metadata-candidates-report.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8'); (outdir/'category-quality-analysis.json').write_text(json.dumps(category,indent=2)+'\n',encoding='utf-8')
 write_md(outdir/'ENTITY_WORTHINESS_REPORT.md','V23.5E — Entity Worthiness Report',rows); write_md(outdir/'DESTINATION_ENTITY_REPORT.md','Destination Entity Report',destination); write_md(outdir/'BORDERLINE_ENTITY_REPORT.md','Borderline Entity Report',borderline); write_md(outdir/'CONTEXTUAL_METADATA_CANDIDATES_REPORT.md','Contextual Metadata Candidates Report',metadata)
 headers=['Entity Name','Entity ID','Entity Type','Research Destination Test','Independent Knowledge Test','Relationship Convergence','Long-Term Significance','Better Parent Assessment','Entity Worthiness Score','Recommended Knowledge Role','Supporting Evidence','Justification','Final Recommendation','Human Decision']
 table=[]
 for r in rows:
  ev=r['supportingEvidence']; table.append([r['entityName'],r['entityId'],r['entityType'],r['researchDestinationTest']['result'],r['independentKnowledgeTest']['result'],r['relationshipConvergenceTest']['result'],r['longTermSignificanceTest']['result'],r['betterParentTest']['result'],r['entityWorthinessScore'],r['recommendedKnowledgeRole'],f"{ev['incomingRelationships']} inbound; {ev['outgoingRelationships']} outbound; {ev['uniqueRelatedEntities']} related entities; {ev['referenceSourceCount']} references",r['justification'],r['finalRecommendation'],'pending'])
 with (outdir/'enhanced-human-review-workbook.csv').open('w',newline='',encoding='utf-8-sig') as f: csv.writer(f).writerows([headers]+table)
 summary_rows=[['Entity Type','Count','Average Score','Destination-worthy','Borderline','Metadata candidates']]+[[t,v['entityCount'],v['averageWorthinessScore'],v['destinationWorthy'],v['borderline'],v['metadataCandidates']] for t,v in category.items()]
 guide=[['Field','Meaning'],['Entity Worthiness Score','0–100 recommendation metric; 70+ destination-worthy; 45–69 borderline.'],['Recommended Knowledge Role','Destination Entity, Supporting Entity, or Contextual Metadata.'],['Human Decision','Always pending; the audit performs no graph changes.'],['Delete/Merge','Not recommended by this release; V23.5E is qualification analysis only.']]
 make_xlsx(outdir/'enhanced-human-review-workbook.xlsx',[('Entity Review',[headers]+table),('Category Analysis',summary_rows),('Review Guide',guide)])
 validation={'release':RELEASE,'baseRepository':BASE,'repositoryUnchanged':not changed,'entityJsonUnchanged':not changed,'relationshipsUnchanged':not changed,'renderedPagesUnchanged':not changed,'schemasUnchanged':not changed,'recommendationEngineUnchanged':not changed,'classificationsUnchanged':not changed,'auditReadOnly':not changed,'allHumanDecisionsPending':all(r['humanDecision']=='pending' for r in rows),'entitiesEvaluated':len(rows)}
 (outdir/'validation-summary.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'release':RELEASE,'entitiesEvaluated':len(rows),'destinationWorthy':len(destination),'borderline':len(borderline),'metadataCandidates':len(metadata),'repositoryMutationDetected':changed},indent=2))
 if changed: raise SystemExit('Protected repository content changed during audit')
if __name__=='__main__': main()
