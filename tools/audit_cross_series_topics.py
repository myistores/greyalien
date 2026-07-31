#!/usr/bin/env python3
"""V23.5D.1 analysis-only cross-series topic relationship audit.

Reads repository entities, traverses the existing knowledge graph, and writes
review artifacts only. It never edits entity JSON, relationships, schemas,
pages, classifications, recommendation logic, or generated graph content.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from collections import Counter, defaultdict, deque
from pathlib import Path

RELEASE = "V23.5D.1"
SERIES = {
    "weaponized-podcast": "WEAPONIZED",
    "need-to-know-podcast": "Need to Know",
    "merged-podcast": "MERGED",
    "somewhere-in-the-skies-podcast": "Somewhere in the Skies",
}
TOPIC_NAMES = {
    "ufo-history": "UFO History",
    "historical-ufo-cases": "Historical UFO Cases",
    "witness-accounts": "Witness Accounts",
}
CASE_TYPES = {"case", "incident", "historical_incident", "encounter", "investigation"}
CASE_RELATIONSHIP_HINTS = {
    "case", "incident", "encounter", "investigation", "event", "occurred_at",
    "witnessed", "investigated", "associated_with", "subject_of", "documents",
}
SIGNALS = {
 "ufo-history": [r"\bhistor(?:y|ical|iography)\b", r"project blue book", r"classic ufo investigators", r"early (?:air force|ufo|investigation)", r"flying.saucer", r"ufology", r"soviet ufo", r"roswell"],
 "historical-ufo-cases": [r"\broswell\b", r"\bnimitz\b", r"varginha", r"trinity", r"andreasson", r"skinwalker", r"dugway", r"montauk", r"chestnut ridge", r"37th parallel", r"named case", r"incident", r"encounter", r"investigation"],
 "witness-accounts": [r"\bwitness(?:es)?\b", r"\beyewitness\b", r"firsthand", r"recounts?", r"describes? .*encounter", r"personal .*sighting", r"pilot testimony", r"account", r"speaks for first time"]
}

def load_json(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def digest(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()
def clean(v): return str(v or "").strip()
def entity_title(e): return clean(e.get("name") or e.get("title") or e.get("episodeTitle") or e.get("id"))
def relationships(e): return [r for r in e.get("relationships",[]) if isinstance(r,dict) and r.get("target")]

def evidence_text(e):
    rels=" ".join(f"{r.get('type','')} {r.get('target','')} {r.get('context','')}" for r in relationships(e))
    fields=[e.get('name',''),e.get('episodeTitle',''),e.get('summary',''),json.dumps(e.get('mediaSubjects',[])),json.dumps(e.get('primaryTopics',[])),json.dumps(e.get('secondaryTopics',[])),json.dumps(e.get('principalClaims',[])),rels]
    return " ".join(map(str,fields))

def graph_indexes(entities):
    outgoing=defaultdict(list); incoming=defaultdict(list)
    for e in entities:
        eid=e.get('id')
        if not eid: continue
        for r in relationships(e):
            edge={"source":eid,"target":r['target'],"type":r.get('type','related_to'),"context":r.get('context','')}
            outgoing[eid].append(edge); incoming[r['target']].append(edge)
    return outgoing,incoming

def is_case_entity(e):
    if not e: return False
    typ=clean(e.get('type')).lower()
    if typ in CASE_TYPES: return True
    cls=" ".join(map(str,[e.get('entityClass',''),e.get('contentClass',''),e.get('category','')])).lower()
    return bool(re.search(r"\b(case|incident|encounter|investigation)\b",cls))

def case_paths(start_id, byid, outgoing, incoming, max_depth=2):
    """Return unique graph paths from an episode to recognized Case entities.

    Traversal is bidirectional because repository relationships are not uniformly
    oriented across ingestion generations. Paths are capped at two edges to
    retain explainability and avoid weak graph-proximity claims.
    """
    found={}; q=deque([(start_id,[])])
    seen={(start_id,0)}
    while q:
        node,path=q.popleft()
        if len(path)>=max_depth: continue
        edges=[]
        edges += [(x['target'],x,False) for x in outgoing.get(node,[])]
        edges += [(x['source'],x,True) for x in incoming.get(node,[])]
        for nxt,edge,reverse in edges:
            if nxt==start_id: continue
            step={"from":node,"to":nxt,"relationshipType":edge['type'],"direction":"incoming" if reverse else "outgoing","context":edge.get('context','')}
            newpath=path+[step]
            ent=byid.get(nxt)
            if is_case_entity(ent):
                key=nxt
                if key not in found or len(newpath)<len(found[key]): found[key]=newpath
                continue
            # Two-edge inheritance is intentionally limited to the entity routes
            # named in the production scope. Generic Topic, series, claim, and
            # timeline proximity must not be treated as Case inheritance.
            allowed_intermediaries={"person","document","organization"}
            if len(newpath)==1 and clean((ent or {}).get("type")).lower() not in allowed_intermediaries:
                continue
            state=(nxt,len(newpath))
            if state not in seen:
                seen.add(state); q.append((nxt,newpath))
    return [{"caseId":cid,"caseName":entity_title(byid[cid]),"path":path,"pathText":format_path(start_id,path,byid)} for cid,path in sorted(found.items())]

def format_path(start,path,byid):
    parts=[entity_title(byid.get(start,{"id":start}))]
    for step in path:
        arrow="←" if step['direction']=='incoming' else "→"
        parts.append(f"{arrow}[{step['relationshipType']}]→ {entity_title(byid.get(step['to'],{'id':step['to']}))}")
    return " ".join(parts)

def matched_signals(e,topic):
    text=evidence_text(e)
    return [p for p in SIGNALS[topic] if re.search(p,text,re.I)]

def subject_test(e,topic,case_info):
    text=evidence_text(e); hits=matched_signals(e,topic)
    summary=clean(e.get('summary')); title=clean(e.get('episodeTitle') or e.get('name'))
    structured=set(e.get('mediaSubjects',[])+e.get('primaryTopics',[])+e.get('secondaryTopics',[]))
    already=any(r.get('target')==topic for r in relationships(e))
    strong = topic in structured or already or len(hits)>=2
    if topic=='historical-ufo-cases' and case_info and (hits or re.search(r"case|incident|encounter|investigation",title+" "+summary,re.I)): strong=True
    generic='source-grounded topics and direct archive references' in summary
    result="pass" if strong else "fail"
    rationale=("The title, summary, structured topic fields, or multiple independent signals show substantive treatment." if strong else "Evidence is limited to an isolated or incidental signal and does not establish substantive discussion.")
    if generic and len(hits)<2 and topic not in structured and not already:
        result="needs_review"; rationale="The archive-grounded summary is concise; metadata supports relevance, but substantive depth requires human confirmation."
    return {"result":result,"rationale":rationale,"signals":[p.replace('\\b','') for p in hits[:5]]}

def research_value_test(e,topic,case_info,coverage):
    series=SERIES[e['seriesId']]; title=clean(e.get('episodeTitle') or e.get('name'))
    case_ids={c['caseId'] for c in case_info}
    novelty=[]
    if series not in coverage['series']: novelty.append("adds cross-series coverage")
    unseen=case_ids-coverage['cases']
    if unseen: novelty.append("adds case coverage: "+", ".join(sorted(unseen)))
    if len(clean(e.get('summary')))>180: novelty.append("provides detailed research context")
    if re.search(r"archive|document|investigat|witness|firsthand|histor",evidence_text(e),re.I): novelty.append("adds documentary, witness, or historical context")
    duplicate_key=re.sub(r"\W+"," ",title.lower()).strip()
    duplicate=duplicate_key in coverage['titles']
    if duplicate and not unseen and series in coverage['series']:
        return {"result":"fail","rationale":"The episode appears to duplicate already represented coverage without a distinct case, series, or research contribution.","valueFactors":[]}
    if novelty:
        return {"result":"pass","rationale":"This relationship would materially improve researcher usefulness because it "+"; ".join(novelty)+".","valueFactors":novelty}
    return {"result":"needs_review","rationale":"Relevance is plausible, but the machine-readable record does not establish a clearly distinct contribution beyond existing coverage.","valueFactors":[]}

def inheritance_test(topic,case_info):
    if topic!='historical-ufo-cases':
        return {"result":"not_applicable","rationale":"Case inheritance is only a gating discovery test for the Historical UFO Cases umbrella topic."}
    if case_info:
        return {"result":"pass","rationale":"The episode has an explainable existing graph path to one or more recognized Case entities."}
    return {"result":"fail","rationale":"No existing graph path to a recognized Historical UFO Case entity was found within two edges."}

def discovery_method(e,topic,case_info):
    metadata=bool(matched_signals(e,topic) or topic in set(e.get('mediaSubjects',[])+e.get('primaryTopics',[])+e.get('secondaryTopics',[])))
    graph=bool(case_info) if topic=='historical-ufo-cases' else False
    if metadata and graph: return "Hybrid Discovery"
    if graph: return "Knowledge Graph Discovery"
    return "Metadata Discovery"

def confidence(subject,research,inheritance,method):
    vals=[subject['result'],research['result']]
    if inheritance['result']!='not_applicable': vals.append(inheritance['result'])
    if all(v=='pass' for v in vals): return "high" if method=='Hybrid Discovery' else "medium"
    if 'fail' in vals: return "low"
    return "medium"

def recommendation(subject,research,inheritance):
    required=[subject['result'],research['result']]
    if inheritance['result']!='not_applicable': required.append(inheritance['result'])
    if all(x=='pass' for x in required): return "recommend_approval"
    if 'fail' in required: return "do_not_recommend"
    return "human_review_needed"

def explanation(e,topic,case_info,subject,research):
    t=TOPIC_NAMES[topic]
    if topic=='historical-ufo-cases' and case_info:
        cases=", ".join(c['caseName'] for c in case_info[:2])
        return f"This episode is already connected to {cases} and its substantive discussion would strengthen the {t} topic page for researchers."
    return f"This episode substantively addresses {t} and offers a distinct research contribution through its series perspective, evidence, or educational context."

def md_table(rows,cols):
    if not rows:return "_None._\n"
    out=["| "+" | ".join(c[0] for c in cols)+" |","|"+"|".join(["---"]*len(cols))+"|"]
    for r in rows:
        out.append("| "+" | ".join(str(r.get(k,'')).replace('|','\\|').replace('\n',' ') for _,k in cols)+" |")
    return "\n".join(out)+"\n"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--config',default='data/audits/v23-5d/audit_config.json'); ap.add_argument('--output-dir',default='reports/v23-5d-1'); args=ap.parse_args()
    root=Path(args.root).resolve(); cfg=load_json(root/args.config); outdir=root/args.output_dir; outdir.mkdir(parents=True,exist_ok=True)
    protected=[]
    for base in ('data/entities','entities/generated'):
        protected += sorted((root/base).glob('**/*')) if (root/base).exists() else []
    protected=[p for p in protected if p.is_file()]
    before={str(p.relative_to(root)):digest(p) for p in protected}
    entities=[]
    for p in sorted((root/'data/entities').glob('*.json')):
        try:e=load_json(p)
        except Exception:continue
        e['_path']=str(p.relative_to(root)); entities.append(e)
    byid={e.get('id'):e for e in entities if e.get('id')}; outgoing,incoming=graph_indexes(entities)
    episodes=[e for e in entities if e.get('type')=='podcast_episode' and e.get('seriesId') in SERIES]
    inventory=Counter(SERIES[e['seriesId']] for e in episodes)
    case_cache={e['id']:case_paths(e['id'],byid,outgoing,incoming) for e in episodes}
    topic_results={}; all_rows=[]
    for tid,tname in TOPIC_NAMES.items():
        existing=[e for e in episodes if any(r.get('target')==tid for r in relationships(e))]
        coverage={'series':{SERIES[e['seriesId']] for e in existing},'titles':{re.sub(r"\W+"," ",clean(e.get('episodeTitle') or e.get('name')).lower()).strip() for e in existing},'cases':set()}
        for e in existing: coverage['cases'].update(c['caseId'] for c in case_cache[e['id']])
        configured=set(cfg.get('approvedCandidateIds',{}).get(tid,[]))
        discovered=set(configured)
        if tid=='historical-ufo-cases': discovered.update(e['id'] for e in episodes if case_cache[e['id']])
        else: discovered.update(e['id'] for e in episodes if matched_signals(e,tid))
        rows=[]
        for eid in sorted(discovered):
            e=byid.get(eid)
            if not e or e.get('type')!='podcast_episode' or e.get('seriesId') not in SERIES: continue
            cases=case_cache[eid]; subject=subject_test(e,tid,cases); research=research_value_test(e,tid,cases,coverage); inheritance=inheritance_test(tid,cases); method=discovery_method(e,tid,cases)
            rec=recommendation(subject,research,inheritance); conf=confidence(subject,research,inheritance,method)
            existing_topics=sorted({r['target'] for r in relationships(e) if byid.get(r['target'],{}).get('type')=='topic'})
            row={
                "episodeId":eid,"podcastSeries":SERIES[e['seriesId']],"episodeNumber":e.get('episodeNumber',''),"episodeTitle":clean(e.get('episodeTitle') or e.get('name')),"proposedTopic":tname,"proposedTopicId":tid,
                "discoveryMethod":method,"existingCaseRelationships":[{"caseId":c['caseId'],"caseName":c['caseName']} for c in cases],"existingTopicRelationships":existing_topics,
                "missingUmbrellaTopicRelationship":tid not in existing_topics,"potentialRedundantRelationship":tid in existing_topics,"existingRelationshipPaths":[c['pathText'] for c in cases],
                "subjectRelevanceTest":subject,"researchValueTest":research,"caseInheritanceTest":inheritance,"supportingEvidence":clean(e.get('summary')) or clean(e.get('episodeTitle')),
                "confidenceLevel":conf,"approvalRecommendation":rec,"relationshipExplanation":explanation(e,tid,cases,subject,research),"humanDecision":"pending","reviewerNotes":""
            }
            rows.append(row); all_rows.append(row)
            if rec=='recommend_approval':
                coverage['series'].add(SERIES[e['seriesId']]); coverage['titles'].add(re.sub(r"\W+"," ",row['episodeTitle'].lower()).strip()); coverage['cases'].update(c['caseId'] for c in cases)
        topic_results[tid]={"topic":tname,"definition":cfg['topics'][tid]['definition'],"candidates":rows,"counts":dict(Counter(r['approvalRecommendation'] for r in rows))}
    consistency=[]
    case_series=defaultdict(lambda:defaultdict(list))
    for e in episodes:
        for c in case_cache[e['id']]: case_series[c['caseId']][SERIES[e['seriesId']]].append(e['id'])
    for cid,series_map in sorted(case_series.items()):
        linked=[]; missing=[]
        for series,eids in sorted(series_map.items()):
            has=[eid for eid in eids if any(r.get('target')=='historical-ufo-cases' for r in relationships(byid[eid]))]
            (linked if has else missing).append({"series":series,"episodeIds":eids})
        consistency.append({"caseId":cid,"caseName":entity_title(byid.get(cid,{})),"seriesCoverage":dict(series_map),"umbrellaLinked":linked,"umbrellaMissing":missing,"inconsistent":bool(linked and missing)})
    after={str(p.relative_to(root)):digest(p) for p in protected}; changed=sorted(p for p in before if before[p]!=after.get(p))
    result={"release":RELEASE,"baseRepository":"V23.5D","productionType":"knowledge_graph_audit_enhancement_analysis_only","humanReviewRequired":True,"repositoryMutationDetected":bool(changed),"changedProtectedFiles":changed,"inventory":{"podcastEpisodes":len(episodes),"episodesBySeries":dict(inventory),"recognizedCaseEntities":sum(is_case_entity(e) for e in entities),"episodesWithCasePaths":sum(bool(v) for v in case_cache.values())},"topics":topic_results,"graphConsistency":consistency}
    (outdir/'audit-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding='utf-8')
    flat=[]
    for r in all_rows:
        flat.append({"podcastSeries":r['podcastSeries'],"episodeNumber":r['episodeNumber'],"episodeTitle":r['episodeTitle'],"episodeId":r['episodeId'],"proposedTopic":r['proposedTopic'],"discoveryMethod":r['discoveryMethod'],"existingCaseRelationships":"; ".join(x['caseName'] for x in r['existingCaseRelationships']),"subjectRelevanceTest":r['subjectRelevanceTest']['result'],"researchValueTest":r['researchValueTest']['result'],"caseInheritanceTest":r['caseInheritanceTest']['result'],"supportingEvidence":r['supportingEvidence'],"confidenceLevel":r['confidenceLevel'],"approvalRecommendation":r['approvalRecommendation'],"relationshipExplanation":r['relationshipExplanation'],"humanDecision":r['humanDecision'],"reviewerNotes":r['reviewerNotes']})
    fields=list(flat[0]) if flat else []
    with (outdir/'human-approval-worksheet.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(flat)
    (outdir/'candidate-relationship-report.json').write_text(json.dumps(all_rows,indent=2,ensure_ascii=False)+"\n",encoding='utf-8')
    (outdir/'graph-consistency-report.json').write_text(json.dumps(consistency,indent=2,ensure_ascii=False)+"\n",encoding='utf-8')
    case_analysis=[r for r in all_rows if r['proposedTopicId']=='historical-ufo-cases']
    (outdir/'case-inheritance-analysis.json').write_text(json.dumps(case_analysis,indent=2,ensure_ascii=False)+"\n",encoding='utf-8')
    lines=["# V23.5D.1 — Cross-Series Topic Relationship Audit Enhancement","","> **Analysis only. Human approval is required. No repository relationships or content were modified.**","","## Validation Summary","",f"- Podcast episodes audited: **{len(episodes)}**",f"- Recognized Case entities: **{result['inventory']['recognizedCaseEntities']}**",f"- Episodes with explainable Case paths: **{result['inventory']['episodesWithCasePaths']}**",f"- Protected-file mutation detected: **{'YES' if changed else 'No'}**","- Candidate origin is classified as Metadata Discovery, Knowledge Graph Discovery, or Hybrid Discovery.","- Every candidate is evaluated with Subject Relevance, Research Value, and Case Inheritance tests.",""]
    for tid,t in topic_results.items():
        lines += [f"## {t['topic']}","",f"**Definition:** {t['definition']}","",md_table(t['candidates'],[("Series","podcastSeries"),("Ep.","episodeNumber"),("Episode","episodeTitle"),("Discovery","discoveryMethod"),("Subject","subjectRelevanceTest.result"),("Research value","researchValueTest.result"),("Case inheritance","caseInheritanceTest.result"),("Recommendation","approvalRecommendation")])]
        # custom concise table because nested keys are not resolved by md_table
        view=[]
        for r in t['candidates']:
            view.append({"series":r['podcastSeries'],"ep":r['episodeNumber'],"title":r['episodeTitle'],"method":r['discoveryMethod'],"subject":r['subjectRelevanceTest']['result'],"research":r['researchValueTest']['result'],"inheritance":r['caseInheritanceTest']['result'],"recommendation":r['approvalRecommendation']})
        lines[-1]=md_table(view,[("Series","series"),("Ep.","ep"),("Episode","title"),("Discovery","method"),("Subject","subject"),("Research value","research"),("Case inheritance","inheritance"),("Recommendation","recommendation")])
    inconsistent=sum(x['inconsistent'] for x in consistency)
    lines += ["## Graph Consistency Analysis","",f"- Case entities represented across audited episodes: **{len(consistency)}**",f"- Cross-series cases with inconsistent umbrella-topic treatment: **{inconsistent}**","- Detailed existing paths, current topic links, missing umbrella links, and redundant-link flags are available in the machine-readable reports.","","## Human Review Gate","","Every worksheet row remains `pending`. A separate bounded data release is required after explicit approval. This audit does not authorize or perform relationship changes.",""]
    (outdir/'V23_5D_1_CROSS_SERIES_TOPIC_RELATIONSHIP_AUDIT.md').write_text("\n".join(lines),encoding='utf-8')
    print(json.dumps({"release":RELEASE,"episodes":len(episodes),"casePathEpisodes":result['inventory']['episodesWithCasePaths'],"candidates":{k:len(v['candidates']) for k,v in topic_results.items()},"mutation":bool(changed)},indent=2))
    if changed: raise SystemExit(2)
if __name__=='__main__': main()
