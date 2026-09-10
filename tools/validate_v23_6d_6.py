#!/usr/bin/env python3
"""Validate V23.6D.6 lunar micron-scale technosignature ingestion."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
def load(rel):
    try: return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{rel}: {exc}"); return {}
def require(value, message):
    if not value: errors.append(message)

news_id = "2026-09-08-avi-loeb-lunar-submicron-technosignatures"
pub_id = "publication-2026-micron-scale-technosignatures-lunar-regolith"
news = load(f"data/news/{news_id}.json")
pub = load(f"data/entities/{pub_id}.json")
manifest = load("docs/ingestion/V23_6D_6_INGESTION_MANIFEST.json")
idx = load("data/entity-index.json"); relidx = load("data/relationship-index.json"); graph = load("data/graph-manifest.json")

require(news.get("newsStatus") == "current", "News record must begin current")
require(news.get("knowledgePermanence") == "permanent", "Extracted knowledge must be permanent")
require(news.get("visibility", {}).get("landmark") is False, "News must be non-Landmark")
require(news.get("lifecycle", {}).get("automaticAgingEnabled") is False, "Automatic news aging must remain disabled")
require(any(r.get("target") == pub_id for r in news.get("relationships", [])), "News -> research path missing")
require("Avi Loeb is not" in news.get("editorialNotes", {}).get("authorship", ""), "Commentary/preprint authorship distinction missing")

pm = pub.get("publicationMetadata", {}); rm = pub.get("researchLibraryMetadata", {}); notes = pub.get("editorialNotes", {})
require(pm.get("identifier") == "arXiv:2606.24028", "arXiv identifier mismatch")
require(pm.get("version") == "v4", "Current arXiv version must be v4")
require(pm.get("lastRevised") == "August 18, 2026", "Revision date mismatch")
require("acceptance" in pm.get("publicationStatus", "").lower() and "not established" in pm.get("publicationStatus", "").lower(), "Acceptance/publication caution missing")
require(pm.get("validDoi") == "10.48550/arXiv.2606.24028", "Valid arXiv DOI missing")
require(pm.get("placeholderJournalDoiIngested") is False, "Placeholder journal DOI must not be ingested")
require(rm.get("knowledgePermanence") == "permanent", "Research must be permanent")
require("0.10 Earth" in rm.get("principalFindings", ""), "v4 0.10-Earth-mass threshold missing")
require("not a sample collected" in rm.get("sampleConcept", ""), "Modeled-sample distinction missing")
require("No extraterrestrial" in notes.get("noDetection", ""), "No-detection clarification missing")
require("not an author" in notes.get("authorship", ""), "Avi Loeb authorship distinction missing")
require([x.get("name") for x in pub.get("particleClasses", [])] == ["Arkhipov Particles", "Bracewell Particles"], "Particle regimes missing or reordered")
require(all("not detected" in x.get("status", "").lower() for x in pub.get("particleClasses", [])), "Particle regimes must remain hypothetical")

author_ids = {r.get("target") for r in pub.get("relationships", []) if r.get("role") == "author"}
require(author_ids == {"lewis-j-pinault", "brian-c-lacki", "ian-a-crawford", "andrew-p-v-siemion"}, "Preprint author set mismatch")
require("avi-loeb" not in author_ids, "Avi Loeb must not be represented as a preprint author")

indexed = {e.get("id") for e in idx.get("entities", [])}
for eid in manifest.get("newEntities", []):
    require((ROOT / f"data/entities/{eid}.json").exists(), f"Missing entity JSON: {eid}")
    require(eid in indexed, f"Entity omitted from compact index: {eid}")
    require((ROOT / f"entities/generated/{eid}.html").exists(), f"Generated entity page missing: {eid}")
    require(eid in relidx.get("incoming", {}), f"Reverse-relationship bucket missing: {eid}")
for eid in manifest.get("reusedEntities", []): require(eid in indexed, f"Expected reused entity missing: {eid}")

nidx = load("data/news/index.json"); ridx = load("data/research-library/index.json")
require(nidx.get("records", [None])[0] == news_id, "Lunar research news must lead news index")
require(ridx.get("records", [None])[0] == pub_id, "Lunar preprint must lead Research Library index")

news_html = (ROOT / "categories/latest-uap-news.html").read_text(encoding="utf-8")
research_html = (ROOT / "categories/research-library.html").read_text(encoding="utf-8")
space_html = (ROOT / "categories/space-exploration.html").read_text(encoding="utf-8")
require('id="lunar-micron-technosignatures-2026-09-08"' in news_html, "Latest News card missing")
require("Permanent Research Record" in news_html, "News -> Research UI path missing")
require("No extraterrestrial technological particle has been detected" in news_html, "News no-detection caution missing")
require('id="micron-scale-technosignatures-lunar-regolith"' in research_html, "Research Library card missing")
require("Related News Coverage" in research_html, "Research -> News backlink missing")
require("0.10 Earth-mass" in research_html, "Current v4 threshold not visible")
require("did not collect or analyze" in research_html, "Research sample-status caution missing")
require('id="lunar-micron-scale-technosignatures"' in space_html, "Space Exploration feature missing")
require("research-library.html#micron-scale-technosignatures-lunar-regolith" in space_html, "Space Exploration -> Research path missing")

# Prior-release regression checks.
for eid in ("publication-2026-european-uap-barometer-2020-2025", "document-2026-aaro-nufohrc-sole-source-notice", "publication-2026-limits-velocity-recovery-pursue", "publication-2026-critical-evaluation-poss1e-technosignatures", "image-video-analysis"):
    require(eid in indexed, f"Inherited entity missing: {eid}")
for nid in ("2026-09-02-uapcheck-european-uap-barometer", "2026-09-02-defensescoop-aaro-nufohrc-access", "2026-08-20-debrief-pursue-video-analysis"):
    require((ROOT / f"data/news/{nid}.json").exists(), f"Inherited news missing: {nid}")

shell = (ROOT / "entities/entity.html").read_text(encoding="utf-8")
engine_hash = hashlib.sha256((ROOT / "assets/js/entity-engine.js").read_bytes()).hexdigest()
require("entity-engine.js?v=23.6d6" in shell, "Entity-shell cache key not advanced")
require(engine_hash == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 runtime changed")
require(graph.get("unresolvedRelationshipCount") == 56, "Inherited unresolved relationship count changed")

if errors:
    print("V23.6D.6 VALIDATION FAILED")
    for error in errors: print("- " + error)
    sys.exit(1)
print("V23.6D.6 VALIDATION PASSED")
print(f"- {len(idx.get('entities', []))} indexed entities")
print(f"- {graph.get('relationshipCount')} resolved relationships")
print("- News <-> Research <-> Space Exploration paths verified")
print("- v4 metadata, DOI and 0.10-Earth-mass conditional threshold verified")
print("- no-detection, sample-status and authorship distinctions verified")
print("- V23.6D.1 entity runtime preserved byte-for-byte")
