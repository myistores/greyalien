#!/usr/bin/env python3
"""Validate V23.6D.8 PURSUE waiver ingestion and inherited behavior."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
def load(rel):
    try: return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{rel}: {exc}"); return {}
def require(value, message):
    if not value: errors.append(message)

news_id = "2026-09-14-department-war-pursue-uap-disclosure-waiver"
doc_id = "document-2026-pursue-uap-disclosure-legal-waiver"
news = load(f"data/news/{news_id}.json"); doc = load(f"data/entities/{doc_id}.json")
manifest = load("docs/ingestion/V23_6D_8_INGESTION_MANIFEST.json")
idx = load("data/entity-index.json"); relidx = load("data/relationship-index.json"); graph = load("data/graph-manifest.json")

require(news.get("newsStatus") == "current", "News must begin current")
require(news.get("knowledgePermanence") == "permanent", "Knowledge must be permanent")
require(news.get("visibility", {}).get("landmark") is False, "News must be non-Landmark")
require(news.get("lifecycle", {}).get("automaticAgingEnabled") is False, "Automatic aging must remain disabled")
require(any(r.get("target") == doc_id for r in news.get("relationships", [])), "News -> document path missing")
require("not unrestricted public disclosure" in news.get("editorialNotes", {}).get("channelLimitation", ""), "News public-disclosure limitation missing")
require("does not automatically declassify" in news.get("editorialNotes", {}).get("classificationDiscipline", ""), "News declassification limitation missing")

meta = doc.get("governmentDocumentMetadata", {}); notes = doc.get("editorialNotes", {})
require(doc.get("date") == "2026-09-14", "Government document date mismatch")
require(meta.get("authorizedRecipient") == "Designated PURSUE representatives.", "Authorized recipient mismatch")
require("NDAs and SAPIAs" in meta.get("legalEffect", ""), "Bounded NDA/SAPIA effect missing")
require("Unrestricted public disclosure" in meta.get("notAuthorized", []), "Public-disclosure exclusion missing")
require("Automatic declassification" in meta.get("notAuthorized", []), "Automatic-declassification exclusion missing")
require("does not itself declassify" in notes.get("classificationDiscipline", ""), "Document declassification caution missing")
require("does not authenticate" in notes.get("authenticationDiscipline", ""), "Authentication caution missing")
require(len(doc.get("processModel", [])) == 4, "Four-stage bounded process model missing")
claim_targets = {r.get("target") for r in doc.get("relationships", []) if r.get("type") == "contains_claim"}
require(len(claim_targets) == 7, "Seven structured claims required")

indexed = {e.get("id") for e in idx.get("entities", [])}
for eid in manifest.get("newEntities", []):
    require((ROOT / f"data/entities/{eid}.json").exists(), f"Missing entity: {eid}")
    require(eid in indexed, f"Entity omitted from index: {eid}")
    require((ROOT / f"entities/generated/{eid}.html").exists(), f"Generated page missing: {eid}")
    require(eid in relidx.get("incoming", {}), f"Reverse bucket missing: {eid}")
for eid in manifest.get("reusedEntities", []): require(eid in indexed, f"Reused entity missing: {eid}")

dept = load("data/entities/department-of-defense.json")
require("U.S. Department of War" in dept.get("aliases", []), "Department naming bridge missing")
require(not (ROOT / "data/entities/department-of-war.json").exists(), "Duplicate department entity created")
require(load("data/news/index.json").get("records", [None])[0] == news_id, "New news must lead news index")
require(load("data/research-library/index.json").get("records", [None])[0] == doc_id, "Waiver must lead research index")

news_html = (ROOT / "categories/latest-uap-news.html").read_text(encoding="utf-8")
research_html = (ROOT / "categories/research-library.html").read_text(encoding="utf-8")
require('id="pursue-disclosure-waiver-2026-09-14"' in news_html, "Latest News card missing")
require("not automatically declassify" in news_html, "News limitation not visible")
require('id="pursue-uap-disclosure-legal-waiver"' in research_html, "Research Library card missing")
require("does not authorize disclosure to the public" in research_html, "Research public-disclosure limitation missing")
require("Related News Coverage" in research_html, "Document -> News backlink missing")

for eid in ("publication-2026-slysh-haloes-cold-computing-technosignature", "publication-2026-micron-scale-technosignatures-lunar-regolith", "publication-2026-european-uap-barometer-2020-2025", "document-2026-aaro-nufohrc-sole-source-notice", "publication-2026-limits-velocity-recovery-pursue", "publication-2026-critical-evaluation-poss1e-technosignatures", "image-video-analysis"):
    require(eid in indexed, f"Inherited entity missing: {eid}")
for nid in ("2026-09-09-universe-today-slysh-haloes", "2026-09-08-avi-loeb-lunar-submicron-technosignatures", "2026-09-02-defensescoop-aaro-nufohrc-access"):
    require((ROOT / f"data/news/{nid}.json").exists(), f"Inherited news missing: {nid}")

shell = (ROOT / "entities/entity.html").read_text(encoding="utf-8")
engine_hash = hashlib.sha256((ROOT / "assets/js/entity-engine.js").read_bytes()).hexdigest()
require("entity-engine.js?v=23.6d8" in shell, "Cache key not advanced")
require(engine_hash == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 runtime changed")
require(graph.get("unresolvedRelationshipCount") == 56, "Inherited unresolved count changed")

if errors:
    print("V23.6D.8 VALIDATION FAILED")
    for error in errors: print("- " + error)
    sys.exit(1)
print("V23.6D.8 VALIDATION PASSED")
print(f"- {len(idx.get('entities', []))} indexed entities")
print(f"- {graph.get('relationshipCount')} resolved relationships")
print("- News <-> permanent government-document paths verified")
print("- channel, public-disclosure, declassification and authentication limits verified")
print("- PURSUE and department canonical entities reused")
print("- V23.6D.1 entity runtime preserved byte-for-byte")
