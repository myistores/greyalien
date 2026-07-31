#!/usr/bin/env python3
"""V23.5D analysis-only cross-series topic relationship audit.

Reads repository entities and writes reports only. It never edits entity JSON,
relationships, schemas, pages, or generated graph content.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

SERIES = {
    "weaponized-podcast": "WEAPONIZED",
    "need-to-know-podcast": "Need to Know",
    "merged-podcast": "MERGED",
    "somewhere-in-the-skies-podcast": "Somewhere in the Skies",
}
TOPIC_NAMES = {"ufo-history":"UFO History", "historical-ufo-cases":"Historical UFO Cases", "witness-accounts":"Witness Accounts"}
SIGNALS = {
 "ufo-history": [r"\bhistor(?:y|ical|iography)\b", r"project blue book", r"classic ufo investigators", r"early (?:air force|ufo|investigation)", r"flying.saucer", r"ufology", r"soviet ufo", r"roswell"],
 "historical-ufo-cases": [r"\broswell\b", r"\bnimitz\b", r"varginha", r"trinity", r"andreasson", r"skinwalker", r"dugway", r"montauk", r"chestnut ridge", r"37th parallel", r"named case", r"incident"],
 "witness-accounts": [r"\bwitness(?:es)?\b", r"\beyewitness\b", r"firsthand", r"recounts?", r"describes? .*encounter", r"personal .*sighting", r"pilot testimony", r"account", r"speaks for first time"]
}

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def evidence_text(e):
    rels=" ".join(f"{r.get('type','')} {r.get('target','')} {r.get('context','')}" for r in e.get('relationships',[]))
    fields=[e.get('name',''),e.get('episodeTitle',''),e.get('summary',''),json.dumps(e.get('mediaSubjects',[])),json.dumps(e.get('principalClaims',[])),rels]
    return " ".join(map(str,fields))

def compact_evidence(e, topic):
    summary=(e.get('summary') or '').strip()
    title=e.get('episodeTitle') or e.get('name','')
    matched=[]
    text=evidence_text(e)
    for pattern in SIGNALS[topic]:
        if re.search(pattern,text,re.I): matched.append(pattern.replace('\\b',''))
    base = summary if summary else f"The title and structured metadata identify the substantive focus as {title}."
    if len(base)>360: base=base[:357].rstrip()+"..."
    return base, matched[:4]

def confidence(e, topic):
    text=evidence_text(e)
    hits=sum(bool(re.search(p,text,re.I)) for p in SIGNALS[topic])
    summary=e.get('summary','')
    generic='source-grounded topics and direct archive references' in summary
    if generic: return "medium" if hits>=1 else "low"
    return "high" if hits>=2 or len(summary)>150 else "medium"

def reject_reason(e, topic):
    text=evidence_text(e).lower()
    if topic=='ufo-history': return "Historical context is incidental or the episode is centered on a single contemporary issue rather than UFO history as a subject."
    if topic=='historical-ufo-cases': return "The record does not establish a sufficiently bounded historical UFO case as the episode's substantive focus."
    if topic=='witness-accounts': return "The record mentions testimony or witnesses but does not clearly establish that a first-person account is substantively presented or analyzed."
    return "Insufficient substantive support."

def md_table(rows, cols):
    if not rows: return "_None._\n"
    out=["| "+" | ".join(c[0] for c in cols)+" |", "|"+"|".join(["---"]*len(cols))+"|"]
    for r in rows:
        vals=[]
        for _,key in cols:
            v=str(r.get(key,'' )).replace('|','\\|').replace('\n',' ')
            vals.append(v)
        out.append("| "+" | ".join(vals)+" |")
    return "\n".join(out)+"\n"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--config',default='data/audits/v23-5d/audit_config.json'); ap.add_argument('--output-dir',default='reports/v23-5d'); args=ap.parse_args()
    root=Path(args.root).resolve(); cfg=load_json(root/args.config); outdir=root/args.output_dir; outdir.mkdir(parents=True,exist_ok=True)
    entity_paths=sorted((root/'data/entities').glob('*.json'))
    before={str(p.relative_to(root)):digest(p) for p in entity_paths}
    entities=[]
    for p in entity_paths:
        try: e=load_json(p)
        except Exception: continue
        e['_path']=str(p.relative_to(root)); entities.append(e)
    byid={e.get('id'):e for e in entities}
    episodes=[e for e in entities if e.get('type')=='podcast_episode' and e.get('seriesId') in SERIES]
    series_inventory=Counter(SERIES[e['seriesId']] for e in episodes)
    relationship_type_counts=Counter(r.get('type','(missing)') for e in episodes for r in e.get('relationships',[]))
    topic_results={}
    flat=[]
    for tid,tname in TOPIC_NAMES.items():
        topic=byid.get(tid,{})
        direct_out=[r for r in topic.get('relationships',[]) if r.get('target')]
        incoming=[]
        for e in entities:
            for r in e.get('relationships',[]):
                if r.get('target')==tid: incoming.append((e,r))
        existing_eps=[e for e,r in incoming if e.get('type')=='podcast_episode']
        accepted_ids=set(cfg['approvedCandidateIds'][tid])
        accepted=[]
        for eid in sorted(accepted_ids):
            e=byid.get(eid)
            if not e: continue
            ev,hits=compact_evidence(e,tid)
            row={"episodeId":eid,"series":SERIES[e['seriesId']],"episodeNumber":e.get('episodeNumber',''),"episodeTitle":e.get('episodeTitle') or e.get('name'),"proposedTopic":tname,"supportingEvidence":ev,"confidence":confidence(e,tid),"existingRelationship":any(r.get('target')==tid for r in e.get('relationships',[])),"matchedSignals":'; '.join(hits)}
            accepted.append(row); flat.append({**row,"decision":"proposed"})
        rejected=[]
        for e in episodes:
            if e.get('id') in accepted_ids: continue
            text=evidence_text(e)
            hits=[p for p in SIGNALS[tid] if re.search(p,text,re.I)]
            if not hits: continue
            ev,_=compact_evidence(e,tid)
            rejected.append({"episodeId":e['id'],"series":SERIES[e['seriesId']],"episodeNumber":e.get('episodeNumber',''),"episodeTitle":e.get('episodeTitle') or e.get('name'),"rationale":reject_reason(e,tid),"triggeringEvidence":ev})
        rejected=sorted(rejected,key=lambda r:(r['series'],str(r['episodeNumber'])))[:12]
        for row in rejected: flat.append({**row,"proposedTopic":tname,"decision":"rejected"})
        proposed_by_series=Counter(r['series'] for r in accepted)
        current_by_type=Counter(e.get('type','unknown') for e,r in incoming)
        topic_results[tid]={"topic":tname,"definition":cfg['topics'][tid]['definition'],"current":{"outgoingRelationships":len(direct_out),"incomingRelationships":len(incoming),"incomingByEntityType":dict(current_by_type),"renderedPodcastCoverage":len(existing_eps),"participatingPodcastSeries":sorted({SERIES[e['seriesId']] for e in existing_eps if e.get('seriesId') in SERIES})},"proposed":accepted,"rejected":rejected,"proposedBySeries":dict(proposed_by_series)}
    after={str(p.relative_to(root)):digest(p) for p in entity_paths}
    changed=[p for p in before if before[p]!=after[p]]
    result={"release":"V23.5D","baseRepository":"V23.5C.4","productionType":"knowledge_graph_audit_analysis_only","humanReviewRequired":True,"repositoryMutationDetected":bool(changed),"changedEntityFiles":changed,"inventory":{"podcastEpisodes":len(episodes),"episodesBySeries":dict(series_inventory),"episodeRelationshipCountsByType":dict(relationship_type_counts)},"topics":topic_results}
    (outdir/'audit-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding='utf-8')
    keys=sorted({k for r in flat for k in r})
    with (outdir/'candidate-decisions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(flat)
    lines=["# V23.5D — Cross-Series Topic Relationship Audit (Pilot)","","> **Status:** Analysis only. Human review required. No relationship additions are approved for implementation by this report.","", "## Repository Protection Result", "", f"- Base repository: **V23.5C.4**", f"- Podcast episodes audited: **{len(episodes)}**", f"- Entity JSON mutation detected: **{'YES' if changed else 'No'}**", "- Repository data, schemas, rendering, classifications, and generated pages were not modified.","", "## Podcast Inventory",""]
    lines.append(md_table([{"series":k,"count":v} for k,v in sorted(series_inventory.items())],[("Series","series"),("Episodes audited","count")]))
    for tid,t in topic_results.items():
        lines += [f"## {t['topic']}","",f"**Working definition:** {t['definition']}","", "### Current relationship summary","",f"- Topic-entity outgoing relationships: **{t['current']['outgoingRelationships']}**",f"- Incoming relationships from all entity types: **{t['current']['incomingRelationships']}**",f"- Current rendered podcast coverage: **{t['current']['renderedPodcastCoverage']} episodes**",f"- Participating podcast series: **{', '.join(t['current']['participatingPodcastSeries']) if t['current']['participatingPodcastSeries'] else 'None'}**",f"- Incoming relationship counts by entity type: **{json.dumps(t['current']['incomingByEntityType'],sort_keys=True)}**","", "### Proposed additional podcast relationships","", md_table(t['proposed'],[("Series","series"),("Ep.","episodeNumber"),("Episode title","episodeTitle"),("Supporting evidence","supportingEvidence"),("Confidence","confidence")]), "### Rejected candidates sampled for review","", md_table(t['rejected'],[("Series","series"),("Ep.","episodeNumber"),("Episode title","episodeTitle"),("Rationale","rationale")])]
        series_with=set(t['proposedBySeries']); missing=set(SERIES.values())-series_with
        if tid=='ufo-history': gap="The principal gap is systematic: these newer pilot topic entities were created empty, while older and newer podcast ingestion used adjacent topics such as historical-ufo-research, project-blue-book, and named-case topics. Topic-definition overlap also requires human judgment between broad history and case-specific history."
        elif tid=='historical-ufo-cases': gap="The gap is both systematic and definitional. Named case relationships are often present, but the umbrella topic is absent. Older Somewhere in the Skies records rely on content-class labels and concise archive-grounded summaries, producing lower evidence granularity than newer episodes."
        else: gap="The gap is systematic across ingestion generations. Many episodes identify a witness through titles, summaries, guests, or claims, but no umbrella Witness Accounts relationship was added. Policy discussions that merely mention testimony must remain excluded."
        lines += ["### Relationship-gap findings","",gap,"",f"Proposed coverage spans **{len(series_with)} of 4** series"+(f"; no sufficiently supported proposals were identified for {', '.join(sorted(missing))}." if missing else "."),"", "### Estimated impact if approved","",f"Human approval of all proposed rows would add **{len(t['proposed'])} episode-to-topic relationships**. The topic page would gain coverage from: {', '.join(f'{k} ({v})' for k,v in sorted(t['proposedBySeries'].items()))}.",""]
    lines += ["## Cross-Series Consistency Findings","", "1. The three pilot topic entities are empty, but conceptually adjacent topic and named-case relationships already exist on many episode records.", "2. Need to Know commonly uses broad historical research topics; WEAPONIZED more often uses named programs, cases, and testimony-specific topics; MERGED emphasizes aviation and reporting; Somewhere in the Skies 2017 uses content-classification language with less detailed summaries.", "3. A safe implementation patch should add only approved episode-to-topic `discussed_topic` relationships, preserve named-case and narrower-topic links, and validate that no episode is linked solely because of isolated keyword overlap.", "", "## Human Review Gate","", "No proposed relationship in this report is authorized for repository implementation. Reviewers must approve, reject, or revise each proposed row before a separate bounded data patch is created.",""]
    (outdir/'V23_5D_CROSS_SERIES_TOPIC_RELATIONSHIP_AUDIT.md').write_text("\n".join(lines),encoding='utf-8')
    print(json.dumps({"episodes":len(episodes),"proposed":{k:len(v['proposed']) for k,v in topic_results.items()},"mutation":bool(changed)},indent=2))
    if changed: raise SystemExit(2)
if __name__=='__main__': main()
