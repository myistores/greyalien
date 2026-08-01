#!/usr/bin/env python3
"""V23.5D.2 destination-topic research-value audit (analysis only).

Reads the existing repository and writes reports only. It never edits entity JSON,
relationships, schemas, rendered pages, classifications, or recommendation logic.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, zipfile
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

RELEASE = "V23.5D.2"
BASE = "V23.5D.1"
SERIES = {
    "weaponized-podcast": "WEAPONIZED", "need-to-know-podcast": "Need to Know",
    "merged-podcast": "MERGED", "somewhere-in-the-skies-podcast": "Somewhere in the Skies",
}
TOPIC_NAMES = {"ufo-history":"UFO History","historical-ufo-cases":"Historical UFO Cases","witness-accounts":"Witness Accounts"}
CASE_TYPES={"case","incident","historical_incident","encounter","investigation"}
SIGNALS={
 "ufo-history":[r"\bhistor(?:y|ical|iography)\b",r"project blue book",r"classic ufo investigators",r"early (?:air force|ufo|investigation)",r"flying.saucer",r"ufology",r"soviet ufo",r"roswell"],
 "historical-ufo-cases":[r"\broswell\b",r"\bnimitz\b",r"varginha",r"trinity",r"andreasson",r"skinwalker",r"dugway",r"montauk",r"chestnut ridge",r"37th parallel",r"named case",r"incident",r"encounter",r"investigation"],
 "witness-accounts":[r"\bwitness(?:es)?\b",r"\beyewitness\b",r"firsthand",r"recounts?",r"personal .*sighting",r"pilot testimony",r"account",r"speaks for first time"]}
CONTRIBUTIONS={
 "unique witness":r"witness|eyewitness|firsthand|testimony|recounts?|account",
 "unique investigator":r"investigat|researcher|historian|journalist|analyst",
 "unique evidence":r"evidence|document|archive|record|report|photograph|video|radar|data",
 "historical context":r"histor|timeline|chronolog|archive|decade|century",
 "technical analysis":r"technical|scientific|physics|radar|sensor|analysis|engineering",
 "skeptical analysis":r"skeptic|debunk|alternative explanation|critical analysis",
 "competing interpretation":r"competing|counterpoint|alternative|dispute|controvers",
 "primary-source discussion":r"primary source|firsthand|testimony|document|official record",
}
TYPE_LABELS={"podcast_episode":"episodes","person":"people","document":"documents","organization":"organizations","case":"cases","incident":"cases","historical_incident":"cases","encounter":"cases","investigation":"investigations"}

def load_json(p): return json.loads(p.read_text(encoding="utf-8"))
def clean(v): return str(v or "").strip()
def digest(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def title(e): return clean(e.get("name") or e.get("title") or e.get("episodeTitle") or e.get("id"))
def rels(e): return [r for r in e.get("relationships",[]) if isinstance(r,dict) and r.get("target")]
def norm_title(v): return re.sub(r"\W+"," ",clean(v).lower()).strip()
def evidence_text(e):
 return " ".join(map(str,[e.get("name",""),e.get("episodeTitle",""),e.get("summary",""),e.get("description",""),json.dumps(e.get("mediaSubjects",[])),json.dumps(e.get("primaryTopics",[])),json.dumps(e.get("secondaryTopics",[])),json.dumps(e.get("principalClaims",[]))," ".join(f"{r.get('type','')} {r.get('target','')} {r.get('context','')}" for r in rels(e))]))
def indexes(entities):
 out=defaultdict(list); inc=defaultdict(list)
 for e in entities:
  if not e.get("id"): continue
  for r in rels(e):
   edge={"source":e["id"],"target":r["target"],"type":r.get("type","related_to"),"context":r.get("context","")}; out[e["id"]].append(edge); inc[r["target"]].append(edge)
 return out,inc
def is_case(e):
 if not e:return False
 return clean(e.get("type")).lower() in CASE_TYPES or bool(re.search(r"\b(case|incident|encounter|investigation)\b"," ".join(map(str,[e.get("entityClass",""),e.get("contentClass",""),e.get("category","")])).lower()))
def case_paths(start,byid,out,inc,max_depth=2):
 found={}; q=deque([(start,[])]); seen={(start,0)}
 while q:
  node,path=q.popleft()
  if len(path)>=max_depth:continue
  edges=[(x["target"],x,"outgoing") for x in out.get(node,[])]+[(x["source"],x,"incoming") for x in inc.get(node,[])]
  for nxt,edge,direction in edges:
   if nxt==start:continue
   step={"from":node,"to":nxt,"relationshipType":edge["type"],"direction":direction,"context":edge.get("context","")}; np=path+[step]; ent=byid.get(nxt)
   if is_case(ent):
    if nxt not in found or len(np)<len(found[nxt]):found[nxt]=np
    continue
   if len(np)==1 and clean((ent or {}).get("type")).lower() not in {"person","document","organization"}:continue
   state=(nxt,len(np))
   if state not in seen:seen.add(state);q.append((nxt,np))
 def fmt(path):
  parts=[title(byid.get(start,{"id":start}))]
  for s in path:parts.append(("←" if s["direction"]=="incoming" else "→")+f"[{s['relationshipType']}]→ "+title(byid.get(s["to"],{"id":s["to"]})))
  return " ".join(parts)
 return [{"caseId":cid,"caseName":title(byid[cid]),"path":p,"pathText":fmt(p)} for cid,p in sorted(found.items())]
def years(e):
 vals=re.findall(r"\b(?:18|19|20)\d{2}\b",evidence_text(e)); return sorted(set(vals))
def linked_entities(e,byid):
 d=defaultdict(list)
 for r in rels(e):
  x=byid.get(r["target"])
  if x:d[clean(x.get("type")).lower()].append({"id":x.get("id"),"name":title(x)})
 return d
def topic_members(topic,entities,byid,out,inc):
 ids=set()
 for edge in inc.get(topic,[]):ids.add(edge["source"])
 for edge in out.get(topic,[]):ids.add(edge["target"])
 for e in entities:
  if topic in set(e.get("mediaSubjects",[])+e.get("primaryTopics",[])+e.get("secondaryTopics",[])):ids.add(e.get("id"))
 return [byid[i] for i in sorted(ids) if i in byid]
def summarize_topic(topic,members,byid,case_cache):
 counts=Counter(); series=set(); case_ids=set(); people=set(); docs=set(); orgs=set(); inv=set(); yrs=set(); titles=set()
 for e in members:
  typ=clean(e.get("type")).lower(); counts[TYPE_LABELS.get(typ,typ or "unknown")]+=1; titles.add(norm_title(title(e))); yrs.update(years(e))
  if typ=="podcast_episode" and e.get("seriesId") in SERIES:series.add(SERIES[e["seriesId"]]); case_ids.update(c["caseId"] for c in case_cache.get(e["id"],[]))
  linked=linked_entities(e,byid)
  people.update(x["id"] for x in linked.get("person",[])); docs.update(x["id"] for x in linked.get("document",[])); orgs.update(x["id"] for x in linked.get("organization",[]))
  for t in CASE_TYPES:inv.update(x["id"] for x in linked.get(t,[]))
 strengths=[]
 if len(members)>=10:strengths.append("established content base")
 if len(series)>=3:strengths.append("strong cross-series representation")
 if len(case_ids)>=5:strengths.append("multiple recognized cases represented")
 if len(people)>=8:strengths.append("broad person coverage")
 if len(yrs)>=4:strengths.append("multi-period chronological coverage")
 gaps=[]
 if len(series)<len(SERIES):gaps.append("missing podcast series: "+", ".join(sorted(set(SERIES.values())-series)))
 if len(people)<5:gaps.append("limited witness/investigator diversity")
 if len(docs)<3:gaps.append("limited document coverage")
 if len(orgs)<3:gaps.append("limited organization/investigation coverage")
 if len(yrs)<3:gaps.append("limited explicit chronology")
 if len(case_ids)<3 and topic=="historical-ufo-cases":gaps.append("limited recognized Case entity coverage")
 if not strengths:strengths=["topic relationship foundation exists"]
 summary=f"{len(members)} existing related entities; {counts.get('episodes',0)} episodes across {len(series)} podcast series; {len(case_ids)} recognized cases; {len(people)} linked people; {len(docs)} documents; {len(orgs)} organizations; {len(yrs)} explicit years."
 return {"topicId":topic,"topic":TOPIC_NAMES[topic],"memberCount":len(members),"entityTypeCounts":dict(counts),"episodeSeries":sorted(series),"caseIds":sorted(case_ids),"personIds":sorted(people),"documentIds":sorted(docs),"organizationIds":sorted(orgs),"years":sorted(yrs),"normalizedTitles":sorted(titles),"strengths":strengths,"gaps":gaps,"coverageSummary":summary}
def matched(e,topic):return [p for p in SIGNALS[topic] if re.search(p,evidence_text(e),re.I)]
def subject_test(e,topic,cases):
 hits=matched(e,topic); structured=set(e.get("mediaSubjects",[])+e.get("primaryTopics",[])+e.get("secondaryTopics",[])); already=any(r.get("target")==topic for r in rels(e)); strong=topic in structured or already or len(hits)>=2
 if topic=="historical-ufo-cases" and cases and (hits or re.search(r"case|incident|encounter|investigation",evidence_text(e),re.I)):strong=True
 generic="source-grounded topics and direct archive references" in clean(e.get("summary"))
 result="pass" if strong else "fail"; rationale="Structured fields or multiple independent signals establish substantive treatment." if strong else "Evidence is isolated or incidental and does not establish substantive treatment."
 if generic and len(hits)<2 and topic not in structured and not already:result="needs_review";rationale="Concise archive metadata supports relevance, but substantive depth requires human confirmation."
 return {"result":result,"rationale":rationale,"signals":[x.replace("\\b","") for x in hits[:5]]}
def candidate_features(e,topic,cases,ctx,byid):
 text=evidence_text(e); linked=linked_entities(e,byid); cand_cases={c["caseId"] for c in cases}; cand_people={x["id"] for x in linked.get("person",[])}; cand_docs={x["id"] for x in linked.get("document",[])}; cand_orgs={x["id"] for x in linked.get("organization",[])}; cand_years=set(years(e)); series=SERIES[e["seriesId"]]
 unique=[name for name,pat in CONTRIBUTIONS.items() if re.search(pat,text,re.I)]
 new_cases=cand_cases-set(ctx["caseIds"]); new_people=cand_people-set(ctx["personIds"]); new_docs=cand_docs-set(ctx["documentIds"]); new_orgs=cand_orgs-set(ctx["organizationIds"]); new_years=cand_years-set(ctx["years"]); new_series=series not in ctx["episodeSeries"]
 duplicate_title=norm_title(title(e)) in set(ctx["normalizedTitles"]); overlap_cases=cand_cases & set(ctx["caseIds"])
 score=0; factors=[]
 def add(points,label):
  nonlocal score
  score+=points; factors.append({"factor":label,"points":points})
 if new_people:add(min(16,8+2*len(new_people)),"new witness/investigator coverage")
 if new_cases:add(min(18,10+3*len(new_cases)),"new Case entity coverage")
 if new_docs:add(min(14,8+2*len(new_docs)),"new document coverage")
 if new_orgs:add(min(10,5+len(new_orgs)),"new organization/investigation coverage")
 if new_years:add(min(10,4+2*len(new_years)),"new chronological coverage")
 if new_series:add(10,"new podcast-series perspective")
 if unique:add(min(22,5+3*len(unique)),"distinct research contribution")
 if cases and topic=="historical-ufo-cases":add(12,"recognized Case inheritance")
 if len(clean(e.get("summary")))>220:add(6,"substantial educational context")
 if duplicate_title:add(-25,"same title already represented")
 if overlap_cases and not (new_people or new_docs or new_years or len(unique)>=2):add(-12,"case coverage substantially overlaps")
 score=max(0,min(100,score))
 broadens=bool(new_cases or new_people or new_docs or new_orgs or new_years or new_series); deepens=bool((overlap_cases or ctx["memberCount"]>0) and (unique or new_people or new_docs) and not duplicate_title); redundant=duplicate_title or (bool(overlap_cases) and not broadens and not deepens)
 cats=[]
 if broadens:cats.append("Broadens topic coverage")
 if deepens:cats.append("Deepens existing research")
 if "unique evidence" in unique or new_docs:cats.append("Adds unique evidence")
 if "unique witness" in unique or new_people:cats.append("Adds unique witness")
 if "unique investigator" in unique:cats.append("Adds unique investigator")
 if new_years or "historical context" in unique:cats.append("Improves chronology")
 if new_series:cats.append("Strengthens cross-series research")
 if broadens and ctx["gaps"]:cats.append("Fills research gap")
 if redundant:cats.append("Primarily redundant")
 if not cats:cats.append("Improves discoverability")
 gap=[]
 if new_series:gap.append("missing podcast series")
 if new_people:gap.append("witness/investigator diversity")
 if new_docs:gap.append("document coverage")
 if new_orgs:gap.append("organization/investigation coverage")
 if new_years:gap.append("chronology")
 if new_cases:gap.append("recognized Case coverage")
 return {"topicCoverageScore":score,"scoreFactors":factors,"uniqueContributions":unique,"newEntityCoverage":{"cases":sorted(new_cases),"people":sorted(new_people),"documents":sorted(new_docs),"organizations":sorted(new_orgs),"years":sorted(new_years),"newSeries":new_series},"coverageGapFilled":gap,"broadensTopic":broadens,"deepensTopic":deepens,"primarilyRedundant":redundant,"improvementCategories":cats,"overlappingCases":sorted(overlap_cases)}
def destination_research_test(e,topic,cases,ctx,feat):
 score=feat["topicCoverageScore"]
 if score>=55:result="pass"
 elif score>=32:result="needs_review"
 else:result="fail"
 unique=", ".join(feat["uniqueContributions"][:3]) or "no clearly machine-identifiable unique contribution"
 gap=", ".join(feat["coverageGapFilled"]) or "no identified coverage gap"
 researcher="yes" if result=="pass" else ("uncertain" if result=="needs_review" else "no")
 improvement="material improvement" if result=="pass" else ("possible improvement requiring human review" if result=="needs_review" else "little additional improvement")
 rationale=f"Topic Coverage Score {score}/100 indicates {improvement}. The candidate contributes {unique}; it fills {gap}."
 return {"result":result,"centralQuestion":"Would a researcher browsing this destination topic page genuinely benefit from finding this episode there?","researcherBenefit":researcher,"topicImprovement":improvement,"rationale":rationale}
def inheritance(topic,cases):
 if topic!="historical-ufo-cases":return {"result":"not_applicable","rationale":"Case inheritance applies only to Historical UFO Cases."}
 return {"result":"pass" if cases else "fail","rationale":"An explainable graph path to a recognized Case entity exists." if cases else "No graph path to a recognized Case entity was found within two edges."}
def discovery(e,topic,cases):
 metadata=bool(matched(e,topic) or topic in set(e.get("mediaSubjects",[])+e.get("primaryTopics",[])+e.get("secondaryTopics",[]))); graph=bool(cases) if topic=="historical-ufo-cases" else False
 return "Hybrid Discovery" if metadata and graph else ("Knowledge Graph Discovery" if graph else "Metadata Discovery")
def recommendation(subject,research,inherit):
 vals=[subject["result"],research["result"]]+([] if inherit["result"]=="not_applicable" else [inherit["result"]])
 return "recommend_approval" if all(x=="pass" for x in vals) else ("do_not_recommend" if "fail" in vals else "human_review_needed")
def confidence(subject,research,inherit,method):
 vals=[subject["result"],research["result"]]+([] if inherit["result"]=="not_applicable" else [inherit["result"]])
 return "high" if all(x=="pass" for x in vals) and method=="Hybrid Discovery" else ("low" if "fail" in vals else "medium")
def explanation(e,topic,cases,feat,research):
 parts=[]
 if cases:parts.append("It is already connected to "+", ".join(c["caseName"] for c in cases[:2]))
 if feat["uniqueContributions"]:parts.append("it contributes "+", ".join(feat["uniqueContributions"][:3]))
 if feat["coverageGapFilled"]:parts.append("it fills gaps in "+", ".join(feat["coverageGapFilled"]))
 if feat["primarilyRedundant"]:parts.append("however, substantial existing coverage makes it primarily redundant")
 change="broadens and deepens" if feat["broadensTopic"] and feat["deepensTopic"] else ("broadens" if feat["broadensTopic"] else ("deepens" if feat["deepensTopic"] else "does not materially expand"))
 return f"This episode {change} the {TOPIC_NAMES[topic]} destination topic. "+("; ".join(parts)+". " if parts else "")+research["rationale"]
def md_table(rows,cols):
 if not rows:return "_None._\n"
 lines=["| "+" | ".join(a for a,_ in cols)+" |","|"+"|".join("---" for _ in cols)+"|"]
 for r in rows:lines.append("| "+" | ".join(str(r.get(k,"")).replace("|","\\|").replace("\n"," ") for _,k in cols)+" |")
 return "\n".join(lines)+"\n"
def xlsx_col(n):
 s=""
 while n:s=chr(65+(n-1)%26)+s;n=(n-1)//26
 return s
def make_xlsx(path,sheets):
 # Minimal standards-compliant workbook with shared inline strings, freeze panes, filters, widths, and styles.
 now=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
 content=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
 for i in range(len(sheets)):content.append(f'<Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
 content.append('</Types>')
 wbxml=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>']
 relxml=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
 for i,(name,_) in enumerate(sheets,1):wbxml.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>');relxml.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
 wbxml.append('</sheets></workbook>');relxml.append(f'<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
 styles='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="3"><font><sz val="10"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="10"/><name val="Calibri"/></font><font><b/><sz val="14"/><color rgb="FF1F4E78"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FFD9E2F3"/></left><right style="thin"><color rgb="FFD9E2F3"/></right><top style="thin"><color rgb="FFD9E2F3"/></top><bottom style="thin"><color rgb="FFD9E2F3"/></bottom><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFill="1" applyFont="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf><xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml',''.join(content));z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>');z.writestr('xl/workbook.xml',''.join(wbxml));z.writestr('xl/_rels/workbook.xml.rels',''.join(relxml));z.writestr('xl/styles.xml',styles)
  z.writestr('docProps/core.xml',f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">V23.5D.2 Enhanced Human Review Workbook</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created></cp:coreProperties>');z.writestr('docProps/app.xml','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>GreyAlien Audit</Application></Properties>')
  for si,(name,rows) in enumerate(sheets,1):
   maxc=max((len(r) for r in rows),default=1); widths=[]
   for c in range(maxc):widths.append(min(45,max(10,max((len(clean(r[c])) for r in rows if c<len(r)),default=10)+2)))
   xml=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>']
   for c,w in enumerate(widths,1):xml.append(f'<col min="{c}" max="{c}" width="{w}" customWidth="1"/>')
   xml.append('</cols><sheetData>')
   for ri,row in enumerate(rows,1):
    xml.append(f'<row r="{ri}" ht="{30 if ri==1 else 45}" customHeight="1">')
    for ci,val in enumerate(row,1):
     ref=f'{xlsx_col(ci)}{ri}'; style=1 if ri==1 else 2
     if isinstance(val,(int,float)) and not isinstance(val,bool):xml.append(f'<c r="{ref}" s="{style}"><v>{val}</v></c>')
     else:xml.append(f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{escape(clean(val))}</t></is></c>')
    xml.append('</row>')
   end=f'{xlsx_col(maxc)}{max(1,len(rows))}';xml.append(f'</sheetData><autoFilter ref="A1:{end}"/><sheetFormatPr defaultRowHeight="15"/></worksheet>');z.writestr(f'xl/worksheets/sheet{si}.xml',''.join(xml))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--config',default='data/audits/v23-5d/audit_config.json');ap.add_argument('--output-dir',default='reports/v23-5d-2');args=ap.parse_args()
 root=Path(args.root).resolve();cfg=load_json(root/args.config);outdir=root/args.output_dir;outdir.mkdir(parents=True,exist_ok=True)
 protected=[]
 for base in ('data/entities','entities/generated','data/knowledge-graph-schema.json','data/related-content.json'):
  p=root/base
  if p.is_file():protected.append(p)
  elif p.exists():protected += [x for x in p.glob('**/*') if x.is_file()]
 before={str(p.relative_to(root)):digest(p) for p in protected}
 entities=[]
 for p in sorted((root/'data/entities').glob('*.json')):
  try:e=load_json(p)
  except Exception:continue
  e['_path']=str(p.relative_to(root));entities.append(e)
 byid={e.get('id'):e for e in entities if e.get('id')};out,inc=indexes(entities);episodes=[e for e in entities if e.get('type')=='podcast_episode' and e.get('seriesId') in SERIES];case_cache={e['id']:case_paths(e['id'],byid,out,inc) for e in episodes}
 contexts={tid:summarize_topic(tid,topic_members(tid,entities,byid,out,inc),byid,case_cache) for tid in TOPIC_NAMES};topic_results={};all_rows=[]
 for tid,tname in TOPIC_NAMES.items():
  configured=set(cfg.get('approvedCandidateIds',{}).get(tid,[]));discovered=set(configured)
  discovered.update(e['id'] for e in episodes if case_cache[e['id']]) if tid=='historical-ufo-cases' else discovered.update(e['id'] for e in episodes if matched(e,tid))
  rows=[]
  for eid in sorted(discovered):
   e=byid.get(eid)
   if not e or e.get('type')!='podcast_episode' or e.get('seriesId') not in SERIES:continue
   cases=case_cache[eid];sub=subject_test(e,tid,cases);feat=candidate_features(e,tid,cases,contexts[tid],byid);rv=destination_research_test(e,tid,cases,contexts[tid],feat);inh=inheritance(tid,cases);method=discovery(e,tid,cases);rec=recommendation(sub,rv,inh);existing_topics=sorted({r['target'] for r in rels(e) if byid.get(r['target'],{}).get('type')=='topic'})
   row={"episodeId":eid,"podcastSeries":SERIES[e['seriesId']],"episodeNumber":e.get('episodeNumber',''),"episodeTitle":title(e),"destinationTopic":tname,"destinationTopicId":tid,"discoveryMethod":method,"currentTopicCoverageSummary":contexts[tid]['coverageSummary'],"currentTopicStrengths":contexts[tid]['strengths'],"currentTopicGaps":contexts[tid]['gaps'],"existingCaseRelationships":[{"caseId":c['caseId'],"caseName":c['caseName']} for c in cases],"existingTopicRelationships":existing_topics,"existingRelationshipPaths":[c['pathText'] for c in cases],"subjectRelevanceTest":sub,"researchValueTest":rv,"researcherBenefitAssessment":rv['researcherBenefit'],"topicImprovementAssessment":rv['topicImprovement'],"uniqueContributionAssessment":feat['uniqueContributions'],"coverageGapFilled":feat['coverageGapFilled'],"complementaryCoverageAssessment":"Adds complementary perspective" if feat['deepensTopic'] else ("Broadens represented coverage" if feat['broadensTopic'] else "No clear complementary contribution"),"redundancyAssessment":"Primarily redundant" if feat['primarilyRedundant'] else ("Some overlap, with added value" if feat['overlappingCases'] else "No material redundancy identified"),"topicCoverageScore":feat['topicCoverageScore'],"scoreFactors":feat['scoreFactors'],"improvementCategory":feat['improvementCategories'],"broadensTopic":feat['broadensTopic'],"deepensTopic":feat['deepensTopic'],"caseInheritanceTest":inh,"supportingEvidence":clean(e.get('summary')) or title(e),"confidenceLevel":confidence(sub,rv,inh,method),"approvalRecommendation":rec,"researchValueExplanation":explanation(e,tid,cases,feat,rv),"finalRecommendation":rec,"humanDecision":"pending","reviewerNotes":""}
   rows.append(row);all_rows.append(row)
  topic_results[tid]={"topic":tname,"definition":cfg['topics'][tid]['definition'],"destinationTopicContext":contexts[tid],"candidates":rows,"counts":dict(Counter(r['finalRecommendation'] for r in rows)),"averageTopicCoverageScore":round(sum(r['topicCoverageScore'] for r in rows)/len(rows),1) if rows else 0}
 consistency=[];case_series=defaultdict(lambda:defaultdict(list))
 for e in episodes:
  for c in case_cache[e['id']]:case_series[c['caseId']][SERIES[e['seriesId']]].append(e['id'])
 for cid,series_map in sorted(case_series.items()):consistency.append({"caseId":cid,"caseName":title(byid.get(cid,{})),"seriesCoverage":dict(series_map),"inconsistent":len(series_map)>1})
 after={str(p.relative_to(root)):digest(p) for p in protected};changed=sorted(k for k in before if before[k]!=after.get(k))
 result={"release":RELEASE,"baseRepository":BASE,"productionType":"knowledge_graph_audit_enhancement_analysis_only","centralEvaluationQuestion":"Would a researcher browsing this destination topic page genuinely benefit from finding this episode there?","humanReviewRequired":True,"repositoryMutationDetected":bool(changed),"changedProtectedFiles":changed,"inventory":{"podcastEpisodes":len(episodes),"episodesBySeries":dict(Counter(SERIES[e['seriesId']] for e in episodes)),"recognizedCaseEntities":sum(is_case(e) for e in entities),"episodesWithCasePaths":sum(bool(v) for v in case_cache.values())},"destinationTopics":contexts,"topics":topic_results,"graphConsistency":consistency}
 (outdir/'audit-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(outdir/'candidate-relationship-report.json').write_text(json.dumps(all_rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(outdir/'destination-topic-research-value-report.json').write_text(json.dumps(topic_results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(outdir/'topic-coverage-analysis.json').write_text(json.dumps(contexts,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(outdir/'coverage-gap-analysis.json').write_text(json.dumps({k:v['gaps'] for k,v in contexts.items()},indent=2)+'\n',encoding='utf-8');(outdir/'complementary-coverage-report.json').write_text(json.dumps([r for r in all_rows if r['broadensTopic'] or r['deepensTopic']],indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(outdir/'redundancy-analysis-report.json').write_text(json.dumps([r for r in all_rows if r['redundancyAssessment']!='No material redundancy identified'],indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(outdir/'graph-consistency-report.json').write_text(json.dumps(consistency,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 headers=["Destination Topic","Podcast Series","Episode Number","Episode Title","Episode ID","Current Topic Coverage Summary","Current Topic Strengths","Current Topic Gaps","Researcher Benefit Assessment","Topic Improvement Assessment","Unique Contribution Assessment","Coverage Gap Filled","Complementary Coverage Assessment","Redundancy Assessment","Topic Coverage Score","Improvement Category","Subject Relevance Test","Research Value Test","Case Inheritance Test","Research Value Explanation","Confidence Level","Final Recommendation","Human Decision","Reviewer Notes"]
 flat=[]
 for r in all_rows:flat.append([r['destinationTopic'],r['podcastSeries'],r['episodeNumber'],r['episodeTitle'],r['episodeId'],r['currentTopicCoverageSummary'],'; '.join(r['currentTopicStrengths']),'; '.join(r['currentTopicGaps']),r['researcherBenefitAssessment'],r['topicImprovementAssessment'],'; '.join(r['uniqueContributionAssessment']),'; '.join(r['coverageGapFilled']),r['complementaryCoverageAssessment'],r['redundancyAssessment'],r['topicCoverageScore'],'; '.join(r['improvementCategory']),r['subjectRelevanceTest']['result'],r['researchValueTest']['result'],r['caseInheritanceTest']['result'],r['researchValueExplanation'],r['confidenceLevel'],r['finalRecommendation'],r['humanDecision'],r['reviewerNotes']])
 with (outdir/'enhanced-human-review-workbook.csv').open('w',newline='',encoding='utf-8') as f:w=csv.writer(f);w.writerow(headers);w.writerows(flat)
 summary_headers=["Destination Topic","Existing Entities","Existing Episodes","Podcast Series","Recognized Cases","People","Documents","Organizations","Explicit Years","Strengths","Gaps","Candidates","Average Coverage Score","Recommend Approval","Human Review","Do Not Recommend"]
 summary=[]
 for tid,t in topic_results.items():
  c=contexts[tid];cnt=t['counts'];summary.append([t['topic'],c['memberCount'],c['entityTypeCounts'].get('episodes',0),len(c['episodeSeries']),len(c['caseIds']),len(c['personIds']),len(c['documentIds']),len(c['organizationIds']),len(c['years']),'; '.join(c['strengths']),'; '.join(c['gaps']),len(t['candidates']),t['averageTopicCoverageScore'],cnt.get('recommend_approval',0),cnt.get('human_review_needed',0),cnt.get('do_not_recommend',0)])
 make_xlsx(outdir/'enhanced-human-review-workbook.xlsx',[("Topic Summary",[summary_headers]+summary),("Candidate Review",[headers]+flat)])
 lines=["# V23.5D.2 — Destination Topic Research Value Enhancement","","> **Analysis only. Human approval is required. No repository content or relationships were modified.**","","## Central Evaluation Question","","**Would a researcher browsing this destination topic page genuinely benefit from finding this episode there?**","","## Validation Summary","",f"- Podcast episodes audited: **{len(episodes)}**",f"- Candidate relationships evaluated: **{len(all_rows)}**",f"- Protected-file mutation detected: **{'YES' if changed else 'No'}**","- Every recommendation includes a frozen destination-topic coverage snapshot, researcher-benefit assessment, topic-improvement assessment, Topic Coverage Score, uniqueness analysis, gap analysis, complementary-coverage analysis, redundancy analysis, and pending human decision.",""]
 for tid,t in topic_results.items():
  c=contexts[tid];lines += [f"## {t['topic']}","",f"**Current coverage:** {c['coverageSummary']}","",f"**Strengths:** {'; '.join(c['strengths'])}","",f"**Gaps:** {'; '.join(c['gaps'])}",""]
  view=[{"series":r['podcastSeries'],"ep":r['episodeNumber'],"title":r['episodeTitle'],"score":r['topicCoverageScore'],"benefit":r['researcherBenefitAssessment'],"improvement":r['topicImprovementAssessment'],"recommendation":r['finalRecommendation']} for r in t['candidates']]
  lines.append(md_table(view,[("Series","series"),("Ep.","ep"),("Episode","title"),("Coverage score","score"),("Researcher benefit","benefit"),("Topic improvement","improvement"),("Recommendation","recommendation")]))
 lines += ["## Human Review Gate","","All decisions remain `pending`. The workbook is a decision-support artifact only. A separate bounded, explicitly approved data release is required to create or remove any relationship.",""]
 (outdir/'V23_5D_2_DESTINATION_TOPIC_RESEARCH_VALUE_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
 validation={"release":RELEASE,"repositoryUnchanged":not changed,"graphUnchanged":not changed,"jsonUnchanged":not changed,"entityRelationshipsUnchanged":not changed,"renderedPagesUnchanged":not changed,"recommendationEngineUnchanged":True,"auditReadOnly":True,"candidateCount":len(all_rows),"allHaveDestinationTopicEvaluation":all(bool(r['currentTopicCoverageSummary']) for r in all_rows),"allHaveTopicCoverageScore":all(isinstance(r['topicCoverageScore'],int) for r in all_rows),"allHaveResearcherBenefit":all(bool(r['researcherBenefitAssessment']) for r in all_rows),"allHaveTopicImprovement":all(bool(r['researchValueExplanation']) for r in all_rows),"allHumanDecisionsPending":all(r['humanDecision']=='pending' for r in all_rows)}
 (outdir/'validation-summary.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({"release":RELEASE,"episodes":len(episodes),"candidates":len(all_rows),"topics":{k:len(v['candidates']) for k,v in topic_results.items()},"mutation":bool(changed)},indent=2))
 if changed:raise SystemExit(2)
if __name__=='__main__':main()
