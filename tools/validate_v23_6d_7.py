#!/usr/bin/env python3
"""Validate V23.6D.7 Slysh-halo ingestion and inherited behavior."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
def load(rel):
    try: return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{rel}: {exc}"); return {}
def require(value, message):
    if not value: errors.append(message)

news_id = "2026-09-09-universe-today-slysh-haloes"
pub_id = "publication-2026-slysh-haloes-cold-computing-technosignature"
news = load(f"data/news/{news_id}.json"); pub = load(f"data/entities/{pub_id}.json")
manifest = load("docs/ingestion/V23_6D_7_INGESTION_MANIFEST.json")
idx = load("data/entity-index.json"); relidx = load("data/relationship-index.json"); graph = load("data/graph-manifest.json")

require(news.get("newsStatus") == "current", "News must begin current")
require(news.get("knowledgePermanence") == "permanent", "Knowledge must be permanent")
require(news.get("visibility", {}).get("landmark") is False, "News must be non-Landmark")
require(news.get("lifecycle", {}).get("automaticAgingEnabled") is False, "Automatic aging must remain disabled")
require(any(r.get("target") == pub_id for r in news.get("relationships", [])), "News -> research path missing")
require(news.get("image", {}).get("path") == manifest.get("companionImage"), "Image metadata mismatch")
require((ROOT / manifest.get("companionImage", "missing")).exists(), "Companion image missing")

pm = pub.get("publicationMetadata", {}); rm = pub.get("researchLibraryMetadata", {}); notes = pub.get("editorialNotes", {})
require(pm.get("identifier") == "arXiv:2608.31153", "arXiv identifier mismatch")
require(pm.get("version") == "v1", "Current version must be v1")
require(pm.get("submitted") == "August 31, 2026", "Submission date mismatch")
require(pm.get("validDoi") == "10.48550/arXiv.2608.31153", "arXiv DOI mismatch")
require("acceptance not established" in pm.get("publicationStatus", "").lower(), "Publication-status caution missing")
require(rm.get("knowledgePermanence") == "permanent", "Research must be permanent")
require("5–30 K" in rm.get("principalFindings", ""), "Cold-computing temperature range missing")
require("10^20 W" in rm.get("principalFindings", ""), "Conditional archival sensitivity missing")
require("No Slysh halo" in notes.get("noDetection", ""), "No-detection clarification missing")
require("Cold circumstellar" in notes.get("naturalAlternatives", ""), "Natural-source caution missing")
authors = {r.get("target") for r in pub.get("relationships", []) if r.get("role") == "author"}
require(authors == {"michael-garrett"}, "Single-author relationship mismatch")
claim_targets = {r.get("target") for r in pub.get("relationships", []) if r.get("type") == "contains_claim"}
require(len(claim_targets) == 7 and "claim-no-slysh-halo-detection" in claim_targets, "Structured claim set incomplete")

indexed = {e.get("id") for e in idx.get("entities", [])}
for eid in manifest.get("newEntities", []):
    require((ROOT / f"data/entities/{eid}.json").exists(), f"Missing entity: {eid}")
    require(eid in indexed, f"Entity omitted from index: {eid}")
    require((ROOT / f"entities/generated/{eid}.html").exists(), f"Generated page missing: {eid}")
    require(eid in relidx.get("incoming", {}), f"Reverse bucket missing: {eid}")
for eid in manifest.get("reusedEntities", []): require(eid in indexed, f"Reused entity missing: {eid}")

require(load("data/news/index.json").get("records", [None])[0] == news_id, "New news must lead news index")
require(load("data/research-library/index.json").get("records", [None])[0] == pub_id, "New paper must lead research index")
news_html = (ROOT / "categories/latest-uap-news.html").read_text(encoding="utf-8")
research_html = (ROOT / "categories/research-library.html").read_text(encoding="utf-8")
space_html = (ROOT / "categories/space-exploration.html").read_text(encoding="utf-8")
require('id="slysh-haloes-2026-09-09"' in news_html, "News card missing")
require(manifest.get("companionImage") in news_html, "Image not rendered in news gateway")
require("not telescope imagery or a detected system" in news_html, "Image disclosure missing")
require('id="slysh-haloes-cold-computing"' in research_html, "Research card missing")
require("Related News Coverage" in research_html, "Research -> News path missing")
require('id="slysh-haloes-cold-computing"' in space_html, "Space Exploration feature missing")
require("Lunar Material Search" in space_html, "D6/D7 methodology connection missing")

for eid in ("publication-2026-micron-scale-technosignatures-lunar-regolith", "publication-2026-european-uap-barometer-2020-2025", "document-2026-aaro-nufohrc-sole-source-notice", "publication-2026-limits-velocity-recovery-pursue", "publication-2026-critical-evaluation-poss1e-technosignatures", "image-video-analysis"):
    require(eid in indexed, f"Inherited entity missing: {eid}")
for nid in ("2026-09-08-avi-loeb-lunar-submicron-technosignatures", "2026-09-02-uapcheck-european-uap-barometer", "2026-09-02-defensescoop-aaro-nufohrc-access"):
    require((ROOT / f"data/news/{nid}.json").exists(), f"Inherited news missing: {nid}")

shell = (ROOT / "entities/entity.html").read_text(encoding="utf-8")
engine_hash = hashlib.sha256((ROOT / "assets/js/entity-engine.js").read_bytes()).hexdigest()
require("entity-engine.js?v=23.6d7" in shell, "Cache key not advanced")
require(engine_hash == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 runtime changed")
require(graph.get("unresolvedRelationshipCount") == 56, "Inherited unresolved count changed")

if errors:
    print("V23.6D.7 VALIDATION FAILED")
    for error in errors: print("- " + error)
    sys.exit(1)
print("V23.6D.7 VALIDATION PASSED")
print(f"- {len(idx.get('entities', []))} indexed entities")
print(f"- {graph.get('relationshipCount')} resolved relationships")
print("- News <-> Research <-> Space Exploration paths and image verified")
print("- v1 metadata, DOI, model limits and natural alternatives verified")
print("- no-detection and publication-status distinctions verified")
print("- V23.6D.1 entity runtime preserved byte-for-byte")
