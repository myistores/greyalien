#!/usr/bin/env python3
"""Validate V23.6D.3 PURSUE cross-gateway and S&T integration."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
def load(rel):
    try: return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{rel}: {exc}"); return {}
def require(value, message):
    if not value: errors.append(message)

paper_id = "publication-2026-limits-velocity-recovery-pursue"
news_id = "2026-08-20-debrief-pursue-video-analysis"
paper = load(f"data/entities/{paper_id}.json")
news = load(f"data/news/{news_id}.json")
iva = load("data/entities/image-video-analysis.json")
entity_index = load("data/entity-index.json")
rel_index = load("data/relationship-index.json")
graph = load("data/graph-manifest.json")
research_index = load("data/research-library/index.json")
manifest = load("docs/ingestion/V23_6D_3_INGESTION_MANIFEST.json")

require(paper.get("name") == "Limits on Velocity Recovery from the PURSUE Sensor Videos", "Authoritative arXiv title mismatch")
require(paper.get("publicationMetadata", {}).get("version") == "v1", "arXiv version must be v1")
require("peer review not established" in paper.get("publicationMetadata", {}).get("publicationStatus", ""), "Preprint status is not explicit")
require(paper.get("researchLibraryMetadata", {}).get("knowledgePermanence") == "permanent", "Paper must be permanent")
require(len(paper.get("evidenceRecords", [])) == 2, "PR113 and PR149 evidence records missing")
require(all(not e.get("promotedToEntity") for e in paper.get("evidenceRecords", [])), "PR113/PR149 must not be standalone entities")

require(news.get("newsStatus") == "current", "PURSUE news must be current")
require(news.get("knowledgePermanence") == "permanent", "Extracted PURSUE knowledge must be permanent")
require(news.get("visibility", {}).get("landmark") is False, "PURSUE news must be non-landmark")
require(news.get("lifecycle", {}).get("automaticAgingEnabled") is False, "Automatic aging must remain disabled")
require(any(r.get("type") == "surfaces_publication" and r.get("target") == paper_id for r in news.get("relationships", [])), "News -> Research path missing")

require(any(r.get("target") == "image-video-analysis" for r in paper.get("relationships", [])), "Research -> Image & Video Analysis missing")
require(any(r.get("target") == paper_id for r in iva.get("relationships", [])), "Image & Video Analysis -> Research missing")
require(research_index.get("records", [None])[0] == paper_id, "PURSUE paper must lead Research Library index")

new_ids = manifest.get("newEntities", [])
indexed = {e.get("id") for e in entity_index.get("entities", [])}
for eid in new_ids:
    require((ROOT / f"data/entities/{eid}.json").exists(), f"Missing entity JSON: {eid}")
    require(eid in indexed, f"Entity missing from compact index: {eid}")
    require((ROOT / f"entities/generated/{eid}.html").exists(), f"Generated page missing: {eid}")
    require(eid in rel_index.get("incoming", {}), f"Reverse-relationship bucket missing: {eid}")

for target in ("image-video-analysis", "department-of-defense", "nasa", "galileo-project"):
    require(target in indexed, f"Expected reused entity missing: {target}")

news_html = (ROOT / "categories/latest-uap-news.html").read_text(encoding="utf-8")
research_html = (ROOT / "categories/research-library.html").read_text(encoding="utf-8")
require('id="pursue-kinematic-inference-2026-08-20"' in news_html, "PURSUE news anchor missing")
require('data-news-status="current"' in news_html and 'data-knowledge-permanence="permanent"' in news_html, "Lifecycle HTML markers missing")
require("Permanent Research Record" in news_html, "News -> Research UI path missing")
require('id="limits-velocity-recovery-pursue"' in research_html, "Research Library entry missing")
require("Related News Coverage" in research_html, "Research -> News UI path missing")
require("Image &amp; Video Analysis" in research_html, "Research -> S&T UI path missing")

shell = (ROOT / "entities/entity.html").read_text(encoding="utf-8")
engine_hash = hashlib.sha256((ROOT / "assets/js/entity-engine.js").read_bytes()).hexdigest()
require("entity-engine.js?v=23.6d3" in shell, "Entity-shell cache key not advanced")
require(engine_hash == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 entity runtime changed")
require(graph.get("unresolvedRelationshipCount") == 56, "Inherited unresolved relationship count changed")

if errors:
    print("V23.6D.3 VALIDATION FAILED")
    for error in errors: print("- " + error)
    sys.exit(1)
print("V23.6D.3 VALIDATION PASSED")
print(f"- {len(entity_index.get('entities', []))} indexed entities")
print(f"- {graph.get('relationshipCount')} resolved relationships")
print("- News <-> Research and Research <-> Image & Video Analysis paths verified")
print("- current/non-landmark lifecycle and permanent knowledge verified")
print("- PR113/PR149 remain structured evidence, not standalone entities")
print("- V23.6D.1 entity runtime preserved byte-for-byte")
