#!/usr/bin/env python3
"""Release-specific validation for V23.6D.11."""
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
DOC="document-2026-aaro-classified-responsive-uap-uso-records"; NEWS="2026-10-05-black-vault-aaro-classified-responsive-records"
errors=[]
def need(v,m):
    if not v: errors.append(m)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
doc=load(ROOT/f"data/entities/{DOC}.json"); news=load(ROOT/f"data/news/{NEWS}.json")
need(doc.get("type")=="publication","FOIA record type missing")
need(news.get("newsStatus")=="current" and news.get("knowledgePermanence")=="permanent","lifecycle fields invalid")
need(news.get("visibility",{}).get("landmark") is False,"news must be non-landmark")
need(doc.get("foiaMetadata",{}).get("caseNumber")=="26-F-1892","FOIA case number missing")
need("5 U.S.C. § 552(b)(1)" in doc.get("foiaMetadata",{}).get("citedAuthority",[]),"FOIA exemption missing")
need(doc.get("foiaMetadata",{}).get("disposition")=="Withheld in full","withholding disposition missing")
need(load(ROOT/"data/news/index.json").get("records",[None])[0]==NEWS,"news index ordering missing")
need(load(ROOT/"data/research-library/index.json").get("records",[None])[0]==DOC,"research index ordering missing")
need('id="aaro-classified-responsive-records-2026-10-05"' in (ROOT/"categories/latest-uap-news.html").read_text(encoding="utf-8"),"news card missing")
need('id="aaro-five-case-classified-records"' in (ROOT/"categories/research-library.html").read_text(encoding="utf-8"),"research card missing")
need("v=23.6d11" in (ROOT/"entities/entity.html").read_text(encoding="utf-8"),"cache key missing")
incidents=["incident-wiley-2x-zinc-uap-uso-formation","incident-cactus-1x-uap-uso-submarine-2022-03-25","incident-jacker-2x-spherical-uap-over-water","incident-uscg-c144-tic-tac-ir-2024-04-24","incident-ufos-formation-persian-gulf-pr098"]
claims=["claim-congress-identified-five-uap-uso-cases","claim-greenewald-filed-five-case-aaro-foia","claim-aaro-located-responsive-records-five-cases","claim-aaro-withheld-five-case-records-in-full","claim-responsive-records-do-not-authenticate-incidents","claim-classification-does-not-establish-record-contents"]
for eid in incidents+claims+["john-greenewald-jr","the-black-vault"]: need((ROOT/f"data/entities/{eid}.json").exists(),f"record missing: {eid}")
targets={r.get("target") for r in doc.get("relationships",[])}
for eid in incidents+claims+["aaro","john-greenewald-jr","the-black-vault","house-oversight-committee","pursue"]: need(eid in targets,f"document relationship missing: {eid}")
need("not authentication" in doc.get("editorialNotes",{}).get("centralBoundary",""),"record/authentication boundary missing")
need("does not reveal" in doc.get("editorialNotes",{}).get("classificationBoundary",""),"classification boundary missing")
need(hashlib.sha256((ROOT/"assets/js/entity-engine.js").read_bytes()).hexdigest()=="895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0","V23.6D.1 runtime changed")
bad=[]
for p in ROOT.rglob("*.json"):
    try: load(p)
    except Exception as exc: bad.append(f"{p.relative_to(ROOT)}: {exc}")
need(not bad,"JSON parse failures: "+"; ".join(bad[:5]))
if errors:
    print("V23.6D.11 VALIDATION FAILED"); [print("- "+e) for e in errors]; raise SystemExit(1)
print("V23.6D.11 VALIDATION PASSED")
print("- Current / non-landmark news and permanent FOIA record verified")
print("- Five incident labels and six claims verified")
print("- Record existence, classification and case-authentication boundaries verified")
print(f"- {sum(1 for _ in ROOT.rglob('*.json'))} JSON files parse successfully")
print("- V23.6D.1 runtime preserved")
