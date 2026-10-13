#!/usr/bin/env python3
"""Release-specific validation for V23.6D.13."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
NEWS = "2026-10-09-rfk-jr-uap-briefing-statements"
RECORD = "record-2026-rfk-jr-luna-uap-briefing-discussion"
RFK = "robert-f-kennedy-jr"
CLAIMS = [
    "claim-rfk-transition-uap-approach", "claim-rfk-alleged-briefer-composition",
    "claim-rfk-alleged-recovery-team-participation", "claim-rfk-alleged-uap-calling-capability",
    "claim-rfk-alleged-destroy-recover-orders", "claim-rfk-requested-public-disclosure",
    "claim-rfk-later-administration-briefings"
]
errors = []

def need(value, message):
    if not value: errors.append(message)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

news = load(ROOT / f"data/news/{NEWS}.json")
record = load(ROOT / f"data/entities/{RECORD}.json")
need(news.get("newsStatus") == "current" and news.get("knowledgePermanence") == "permanent", "news lifecycle invalid")
need(news.get("visibility", {}).get("landmark") is False, "news must be non-landmark")
need(record.get("recordMetadata", {}).get("underlyingAllegationsVerified") is False, "verification boundary missing")
need(record.get("recordMetadata", {}).get("namedBriefers") is False, "unnamed-briefer boundary missing")
need(record.get("recordMetadata", {}).get("supportingDocumentsReleased") is False, "document boundary missing")
need((ROOT / "assets/news/rfk-jr-uap-briefing-statements-2026-10.png").exists(), "companion image missing")
need(load(ROOT / "data/news/index.json").get("records", [None])[0] == NEWS, "news index ordering missing")
need(load(ROOT / "data/research-library/index.json").get("records", [None])[0] == RECORD, "research index ordering missing")
need('id="rfk-jr-uap-briefings-2026-10-09"' in (ROOT / "categories/latest-uap-news.html").read_text(encoding="utf-8"), "news card missing")
need('id="rfk-jr-uap-briefing-statements"' in (ROOT / "categories/research-library.html").read_text(encoding="utf-8"), "research card missing")
need("v=23.6d13" in (ROOT / "entities/entity.html").read_text(encoding="utf-8"), "cache key missing")
for eid in [RFK, RECORD, *CLAIMS]:
    need((ROOT / f"data/entities/{eid}.json").exists(), f"missing record: {eid}")
targets = {r.get("target") for r in record.get("relationships", [])}
for eid in [RFK, "anna-paulina-luna", "nasa", "united-states-navy", "united-states-army", "white-house", "crash-retrievals", "uap-disclosure", "government-transparency", *CLAIMS]:
    need(eid in targets, f"statement relationship missing: {eid}")
for eid in CLAIMS:
    claim = load(ROOT / f"data/entities/{eid}.json")
    need("independently unverified" in claim.get("claimMetadata", {}).get("verificationStatus", ""), f"claim verification boundary missing: {eid}")
need(hashlib.sha256((ROOT / "assets/js/entity-engine.js").read_bytes()).hexdigest() == "895c140cff5b2dab5e322068eea31be216529373b3b64cf002504c324bcd2be0", "V23.6D.1 runtime changed")
bad = []
for path in ROOT.rglob("*.json"):
    try: load(path)
    except Exception as exc: bad.append(f"{path.relative_to(ROOT)}: {exc}")
need(not bad, "JSON parse failures: " + "; ".join(bad[:5]))
if errors:
    print("V23.6D.13 VALIDATION FAILED")
    for error in errors: print("- " + error)
    raise SystemExit(1)
print("V23.6D.13 VALIDATION PASSED")
print("- Current / non-landmark news and permanent statement record verified")
print("- One participant entity and seven structured attributed claims verified")
print("- NASA and military references remain allegation-level, not institutional confirmation")
print(f'- {sum(1 for _ in ROOT.rglob("*.json"))} JSON files parse successfully')
print("- Companion image and V23.6D.1 runtime verified")
