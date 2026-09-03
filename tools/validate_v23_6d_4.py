#!/usr/bin/env python3
"""Validate V23.6D.4 archive/procurement cross-gateway ingestion."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
def load(rel):
    try: return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{rel}: {exc}"); return {}
def require(value, message):
    if not value: errors.append(message)

news_id = "2026-09-02-defensescoop-aaro-nufohrc-access"
notice_id = "document-2026-aaro-nufohrc-sole-source-notice"
news = load(f"data/news/{news_id}.json")
notice = load(f"data/entities/{notice_id}.json")
nufohrc = load("data/entities/national-ufo-historical-records-center.json")
rg615 = load("data/entities/record-group-615-uap-records-collection.json")
manifest = load("docs/ingestion/V23_6D_4_INGESTION_MANIFEST.json")
idx = load("data/entity-index.json"); relidx = load("data/relationship-index.json"); graph = load("data/graph-manifest.json")

require(news.get("newsStatus") == "current", "News record must begin current")
require(news.get("knowledgePermanence") == "permanent", "Extracted knowledge must be permanent")
require(news.get("visibility", {}).get("landmark") is False, "News record must be non-Landmark")
require(news.get("lifecycle", {}).get("automaticAgingEnabled") is False, "Automatic news aging must remain disabled")
require(any(r.get("type") == "surfaces_publication" and r.get("target") == notice_id for r in news.get("relationships", [])), "News -> government-document path missing")

pm = notice.get("procurementMetadata", {})
require(pm.get("noticeId") == "NUFOHRC_20260731", "Notice identifier mismatch")
require("intent" in pm.get("noticeType", "").lower(), "Notice must remain proposed/intended")
require("no completed award" in pm.get("awardStatus", "").lower() and "independently verified" in pm.get("awardStatus", "").lower(), "Award-status caution missing")
require("subscription" in pm.get("ownershipCaution", "").lower() and "ownership" in pm.get("ownershipCaution", "").lower(), "Subscription/ownership distinction missing")
require(notice.get("researchLibraryMetadata", {}).get("knowledgePermanence") == "permanent", "Government notice must be permanent")

require(nufohrc.get("name") == "National UFO Historical Records Center", "Official organization name mismatch")
require("NUFOHRC" in nufohrc.get("aliases", []), "NUFOHRC alias missing")
require("does not authenticate" in nufohrc.get("archiveMetadata", {}).get("evidenceCaution", ""), "Archive/evidence caution missing")
require("separate" in rg615.get("recordsCollectionMetadata", {}).get("distinction", ""), "NUFOHRC / Record Group 615 distinction missing")

indexed = {e.get("id") for e in idx.get("entities", [])}
for eid in manifest.get("newEntities", []):
    require((ROOT / f"data/entities/{eid}.json").exists(), f"Missing entity JSON: {eid}")
    require(eid in indexed, f"Entity omitted from compact index: {eid}")
    require((ROOT / f"entities/generated/{eid}.html").exists(), f"Generated entity page missing: {eid}")
    require(eid in relidx.get("incoming", {}), f"Reverse-relationship bucket missing: {eid}")
for eid in manifest.get("reusedEntities", []): require(eid in indexed, f"Expected reused entity missing: {eid}")

# V23.6D.3 regression checks without imposing its release-specific index ordering/cache key.
for eid in ("publication-2026-limits-velocity-recovery-pursue", "pursue", "jacob-haqq-misra", "ravi-kopparapu", "image-video-analysis"):
    require(eid in indexed, f"Inherited V23.6D.3 entity missing: {eid}")
require((ROOT / "data/news/2026-08-20-debrief-pursue-video-analysis.json").exists(), "Inherited PURSUE news record missing")
iva = load("data/entities/image-video-analysis.json")
require(any(r.get("target") == "publication-2026-limits-velocity-recovery-pursue" for r in iva.get("relationships", [])), "Inherited PURSUE S&T integration missing")

nidx = load("data/news/index.json"); ridx = load("data/research-library/index.json")
require(nidx.get("records", [None])[0] == news_id, "DefenseScoop news must lead the news index")
require(ridx.get("records", [None])[0] == notice_id, "Government notice must lead the Research Library index")

news_html = (ROOT / "categories/latest-uap-news.html").read_text(encoding="utf-8")
research_html = (ROOT / "categories/research-library.html").read_text(encoding="utf-8")
require('id="aaro-nufohrc-access-2026-09-02"' in news_html, "Latest News card missing")
require('data-news-status="current"' in news_html and 'data-knowledge-permanence="permanent"' in news_html, "News lifecycle markers missing")
require("Government Contracting Notice" in news_html, "News -> document UI path missing")
require('id="aaro-nufohrc-sole-source-notice"' in research_html, "Research Library government record missing")
require("Related News Coverage" in research_html, "Government document -> News backlink missing")
require("notice of intent" in research_html.lower(), "Procurement status is not visible")
require("do not authenticate" in research_html.lower(), "Archive evidence limitation is not visible")

shell = (ROOT / "entities/entity.html").read_text(encoding="utf-8")
engine_hash = hashlib.sha256((ROOT / "assets/js/entity-engine.js").read_bytes()).hexdigest()
require("entity-engine.js?v=23.6d4" in shell, "Entity-shell cache key not advanced")
require(engine_hash == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 runtime changed")
require(graph.get("unresolvedRelationshipCount") == 56, "Inherited unresolved relationship count changed")

if errors:
    print("V23.6D.4 VALIDATION FAILED")
    for error in errors: print("- " + error)
    sys.exit(1)
print("V23.6D.4 VALIDATION PASSED")
print(f"- {len(idx.get('entities', []))} indexed entities")
print(f"- {graph.get('relationshipCount')} resolved relationships")
print("- News <-> Government Document paths verified")
print("- intent-to-award status and ownership/authentication cautions verified")
print("- NUFOHRC / Record Group 615 distinction verified")
print("- V23.6D.1 entity runtime preserved byte-for-byte")
