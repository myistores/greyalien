#!/usr/bin/env python3
"""Release-specific validation for V23.6D.9."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
COLL = "collection-2026-pursue-release-06"
NEWS = "2026-09-18-department-war-pursue-release-06"
errors = []
def require(value, message):
    if not value: errors.append(message)
def load(path): return json.loads(path.read_text(encoding="utf-8"))

collection = load(ROOT/f"data/entities/{COLL}.json")
news = load(ROOT/f"data/news/{NEWS}.json")
news_index = load(ROOT/"data/news/index.json")
research_index = load(ROOT/"data/research-library/index.json")
news_html = (ROOT/"categories/latest-uap-news.html").read_text(encoding="utf-8")
research_html = (ROOT/"categories/research-library.html").read_text(encoding="utf-8")
shell = (ROOT/"entities/entity.html").read_text(encoding="utf-8")

require(news.get("newsStatus") == "current", "news lifecycle is not current")
require(news.get("knowledgePermanence") == "permanent", "news knowledge is not permanent")
require(news.get("visibility", {}).get("landmark") is False, "news must be non-landmark")
require(news_index.get("records", [None])[0] == NEWS, "news index ordering missing")
require(research_index.get("records", [None])[0] == COLL, "research index ordering missing")
require('id="pursue-release-06-2026-09-18"' in news_html, "Latest News card missing")
require('id="pursue-release-06"' in research_html, "Research Library card missing")
require("v=23.6d9" in shell, "entity shell cache key not advanced")
manifest = collection.get("manifestSnapshot", {})
require(manifest.get("itemCount") == 75, "manifest item count mismatch")
require(sum(manifest.get("fileTypes", {}).values()) == 75, "manifest file-type count mismatch")
require(sum(manifest.get("sourceOrganizations", {}).values()) == 75, "manifest source count mismatch")
require(manifest.get("snapshotDate") == "2026-09-30", "manifest verification date missing")
targets = {r.get("target") for r in collection.get("relationships", [])}
for eid in ["pursue", "department-of-defense", "aaro", "aawsap", "defense-intelligence-agency", "record-group-615-uap-records-collection", "document-2026-pursue-uap-disclosure-legal-waiver"]:
    require(eid in targets, f"collection relationship missing: {eid}")
for suffix in ["sixth-tranche", "declassified-historical", "official-custody", "rolling-process", "next-release", "publication-not-authentication", "file-specific-review"]:
    require((ROOT/f"data/entities/claim-pursue-release-06-{suffix}.json").exists(), f"claim missing: {suffix}")
require("Official publication is not wholesale authentication" in collection.get("editorialNotes", {}).get("authenticationDiscipline", ""), "authentication caution missing")
require("no individual Release 06 file" in collection.get("editorialNotes", {}).get("waiverSequence", ""), "waiver causation boundary missing")

runtime_hash = hashlib.sha256((ROOT/"assets/js/entity-engine.js").read_bytes()).hexdigest()
require(runtime_hash == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 runtime files changed")

bad_json = []
for path in ROOT.rglob("*.json"):
    try: load(path)
    except Exception as exc: bad_json.append(f"{path.relative_to(ROOT)}: {exc}")
require(not bad_json, "JSON parse failures: " + "; ".join(bad_json[:5]))

if errors:
    print("V23.6D.9 VALIDATION FAILED")
    for error in errors: print(f"- {error}")
    raise SystemExit(1)
print("V23.6D.9 VALIDATION PASSED")
print("- Current / non-landmark news record and permanent collection verified")
print("- 75-item dated manifest reconciles across type and source counts")
print("- Seven structured claims and provenance limits verified")
print("- D.8 waiver sequence connected without file-level causal attribution")
print("- Existing PURSUE, Department, AARO, AAWSAP, DIA and RG615 entities reused")
print(f"- {sum(1 for _ in ROOT.rglob('*.json'))} JSON files parse successfully")
print("- V23.6D.1 runtime preserved")
