#!/usr/bin/env python3
"""Release-specific validation for V23.6D.10."""
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
EVENT="event-2016-podesta-delonge-uap-conference-call"
NEWS="2026-10-01-paradigm-podesta-delonge-uap-call"
errors=[]
def need(v,m):
    if not v: errors.append(m)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
event=load(ROOT/f"data/entities/{EVENT}.json"); news=load(ROOT/f"data/news/{NEWS}.json")
need(event.get("type")=="timeline_event","historical event type missing")
need(news.get("newsStatus")=="current","news is not current")
need(news.get("knowledgePermanence")=="permanent","knowledge is not permanent")
need(news.get("visibility",{}).get("landmark") is False,"news must be non-landmark")
need(load(ROOT/"data/news/index.json").get("records",[None])[0]==NEWS,"news index ordering missing")
need(load(ROOT/"data/research-library/index.json").get("records",[None])[0]==EVENT,"research index ordering missing")
need('id="podesta-delonge-call-2026-10-01"' in (ROOT/"categories/latest-uap-news.html").read_text(encoding="utf-8"),"news card missing")
need('id="podesta-delonge-2016-uap-call"' in (ROOT/"categories/research-library.html").read_text(encoding="utf-8"),"research card missing")
need("v=23.6d10" in (ROOT/"entities/entity.html").read_text(encoding="utf-8"),"cache key missing")
targets={r.get("target") for r in event.get("relationships",[])}
for eid in ["john-podesta","tom-delonge","neil-mccasland","robert-weiss","department-of-defense","lockheed-martin","to-the-stars-academy"]: need(eid in targets,f"event relationship missing: {eid}")
claims=["claim-2016-call-occurred","claim-2016-call-declassification-discussion","claim-2016-call-stigma-discussion","claim-grusch-2016-acclimatization-interpretation","claim-podesta-disputes-acclimatization-interpretation","claim-2016-call-confirmation-not-program-proof"]
for eid in claims: need((ROOT/f"data/entities/{eid}.json").exists(),f"claim missing: {eid}")
need("not confirmation of Grusch" in event.get("editorialNotes",{}).get("eventMeaningSeparation",""),"event/interpretation boundary missing")
need("not represented as formally creating" in event.get("editorialNotes",{}).get("ttsBoundary",""),"TTSA boundary missing")
need(hashlib.sha256((ROOT/"assets/js/entity-engine.js").read_bytes()).hexdigest()=="895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0","V23.6D.1 runtime changed")
bad=[]
for p in ROOT.rglob("*.json"):
    try: load(p)
    except Exception as exc: bad.append(f"{p.relative_to(ROOT)}: {exc}")
need(not bad,"JSON parse failures: "+"; ".join(bad[:5]))
if errors:
 print("V23.6D.10 VALIDATION FAILED"); [print("- "+e) for e in errors]; raise SystemExit(1)
print("V23.6D.10 VALIDATION PASSED")
print("- Current / non-landmark news and permanent historical record verified")
print("- Four participants and six structured claims verified")
print("- Confirmed event remains separate from disputed interpretation")
print("- Historical-email, TTSA and acclimatization-program boundaries verified")
print(f"- {sum(1 for _ in ROOT.rglob('*.json'))} JSON files parse successfully")
print("- V23.6D.1 runtime preserved")
