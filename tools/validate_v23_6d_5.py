#!/usr/bin/env python3
"""Validate V23.6D.5 European UAP Barometer cross-gateway ingestion."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
def load(rel):
    try: return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{rel}: {exc}"); return {}
def require(value, message):
    if not value: errors.append(message)

news_id = "2026-09-02-uapcheck-european-uap-barometer"
pub_id = "publication-2026-european-uap-barometer-2020-2025"
prior_id = "publication-2025-european-uap-barometer-2019-2024"
news = load(f"data/news/{news_id}.json")
pub = load(f"data/entities/{pub_id}.json")
manifest = load("docs/ingestion/V23_6D_5_INGESTION_MANIFEST.json")
idx = load("data/entity-index.json"); relidx = load("data/relationship-index.json"); graph = load("data/graph-manifest.json")

require(news.get("newsStatus") == "current", "News record must begin current")
require(news.get("knowledgePermanence") == "permanent", "Extracted knowledge must be permanent")
require(news.get("visibility", {}).get("landmark") is False, "News record must be non-Landmark")
require(news.get("lifecycle", {}).get("automaticAgingEnabled") is False, "Automatic news aging must remain disabled")
require(any(r.get("type") == "surfaces_publication" and r.get("target") == pub_id for r in news.get("relationships", [])), "News -> research path missing")

pm = pub.get("publicationMetadata", {})
rm = pub.get("researchLibraryMetadata", {})
require(pm.get("version") == "1.0", "Research version mismatch")
require("peer review not established" in pm.get("publicationStatus", "").lower(), "Publication-status caution missing")
require(rm.get("knowledgePermanence") == "permanent", "Research record must be permanent")
require(rm.get("relatedNewsId") == news_id, "Research -> news metadata path missing")
require(any(r.get("type") == "references_publication" and r.get("target") == prior_id and r.get("role") == "updates" for r in pub.get("relationships", [])), "Current -> prior Barometer path missing")

totals = pub.get("annualReportingTotals", [])
require([r.get("total") for r in totals] == [6867, 4996, 6018, 6404, 6938, 7193], "Annual totals do not match the primary report")
require(sum(r.get("total", 0) for r in totals) == 38416, "Six-year aggregate total mismatch")
require(totals[-1].get("nationalOrganizations") == 4480 and totals[-1].get("mufon") == 586 and totals[-1].get("nuforc") == 492 and totals[-1].get("enigma") == 1635, "2025 source-category totals mismatch")
require("not confirmed anomalous" in pub.get("editorialNotes", {}).get("eventStatus", ""), "Event-status caution missing")
require("do not necessarily mean" in pub.get("editorialNotes", {}).get("centralCaution", ""), "Central reporting/incidence caution missing")

indexed = {e.get("id") for e in idx.get("entities", [])}
for eid in manifest.get("newEntities", []):
    require((ROOT / f"data/entities/{eid}.json").exists(), f"Missing entity JSON: {eid}")
    require(eid in indexed, f"Entity omitted from compact index: {eid}")
    require((ROOT / f"entities/generated/{eid}.html").exists(), f"Generated entity page missing: {eid}")
    require(eid in relidx.get("incoming", {}), f"Reverse-relationship bucket missing: {eid}")
for eid in manifest.get("reusedEntities", []): require(eid in indexed, f"Expected reused entity missing: {eid}")

nidx = load("data/news/index.json"); ridx = load("data/research-library/index.json")
require(nidx.get("records", [None])[0] == news_id, "Barometer news must lead the news index")
require(ridx.get("records", [None])[0] == pub_id, "Barometer report must lead the Research Library index")

news_html = (ROOT / "categories/latest-uap-news.html").read_text(encoding="utf-8")
research_html = (ROOT / "categories/research-library.html").read_text(encoding="utf-8")
require('id="european-uap-barometer-2026-09-02"' in news_html, "Latest News card missing")
require("Permanent Research Record" in news_html, "News -> Research UI path missing")
require('id="european-uap-barometer-2020-2025"' in research_html, "Research Library card missing")
require("Related News Coverage" in research_html, "Research -> News backlink missing")
require("not 7,193 confirmed anomalous" in news_html, "News statistical caution is not visible")
require("not a measurement of actual anomalous activity" in research_html, "Research statistical caution is not visible")

# Regression checks for all prior V23.6D feature releases.
for eid in ("publication-2026-limits-velocity-recovery-pursue", "image-video-analysis", "document-2026-aaro-nufohrc-sole-source-notice", "record-group-615-uap-records-collection", "publication-2026-critical-evaluation-poss1e-technosignatures"):
    require(eid in indexed, f"Inherited entity missing: {eid}")
require((ROOT / "data/news/2026-09-02-defensescoop-aaro-nufohrc-access.json").exists(), "Inherited V23.6D.4 news missing")
require((ROOT / "data/news/2026-08-20-debrief-pursue-video-analysis.json").exists(), "Inherited V23.6D.3 news missing")

shell = (ROOT / "entities/entity.html").read_text(encoding="utf-8")
engine_hash = hashlib.sha256((ROOT / "assets/js/entity-engine.js").read_bytes()).hexdigest()
require("entity-engine.js?v=23.6d5" in shell, "Entity-shell cache key not advanced")
require(engine_hash == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 runtime changed")
require(graph.get("unresolvedRelationshipCount") == 56, "Inherited unresolved relationship count changed")

if errors:
    print("V23.6D.5 VALIDATION FAILED")
    for error in errors: print("- " + error)
    sys.exit(1)
print("V23.6D.5 VALIDATION PASSED")
print(f"- {len(idx.get('entities', []))} indexed entities")
print(f"- {graph.get('relationshipCount')} resolved relationships")
print("- News <-> Research Library paths verified")
print("- annual/source totals and reporting-incidence cautions verified")
print("- publication status and prior-edition relationship verified")
print("- V23.6D.1 entity runtime preserved byte-for-byte")
