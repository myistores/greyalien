#!/usr/bin/env python3
"""Apply V23.6D.13 RFK Jr. attributed UAP-briefing statement ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
NEWS = "2026-10-09-rfk-jr-uap-briefing-statements"
RECORD = "record-2026-rfk-jr-luna-uap-briefing-discussion"
RFK = "robert-f-kennedy-jr"
SOURCE = "https://www.sentinel-news.org/p/rfk-jr-says-he-has-been-briefed-on"

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def rel(kind, target, **extra):
    return {"type": kind, "target": target, **extra}

def entity(obj):
    obj.setdefault("relationships", [])
    obj.setdefault("officialLinks", [])
    obj.setdefault("referenceSources", [])
    write(ENT / f"{obj['id']}.json", obj)

def enrich(eid, kind, role):
    path = ENT / f"{eid}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not any(r.get("type") == kind and r.get("target") == RECORD for r in data.get("relationships", [])):
        data.setdefault("relationships", []).append(rel(kind, RECORD, role=role))
    if not any(s.get("url") == SOURCE for s in data.get("referenceSources", [])):
        data.setdefault("referenceSources", []).append({
            "label": "Sentinel News — RFK Jr. UAP briefing statements",
            "url": SOURCE,
            "sourceType": "reporting_with_embedded_recording_and_transcript",
            "role": "connected_statement_source"
        })
    write(path, data)

entity({
    "id": RFK,
    "type": "person",
    "name": "Robert F. Kennedy Jr.",
    "summary": "U.S. secretary of health and human services who said in a recorded 2026 conversation that he had received UAP-related briefings during the presidential transition and after entering the administration.",
    "profileStatus": "Public official / recorded UAP statement participant",
    "profileSummary": "Kennedy's public statement is documented by the recording; the extraordinary activities he recounted remain independently unverified.",
    "destinationPage": True,
    "visibleInDirectory": True,
    "searchable": True,
    "taxonomyStatus": "canonical",
    "relationships": [rel("participated_in", RECORD, role="interview participant and source of attributed claims")],
    "referenceSources": [{"label": "Sentinel News report, transcript and embedded recording", "url": SOURCE, "sourceType": "recorded_public_statement", "role": "primary_statement_reference"}]
})

claims = [
    ("claim-rfk-transition-uap-approach", "Kennedy said a group approached him during the presidential transition", "Kennedy said that while living in Palm Beach during the presidential transition, a group approached him to discuss UAP.", "attributed_firsthand_statement", "The recording verifies the statement, not the identities or credentials of the alleged briefers."),
    ("claim-rfk-alleged-briefer-composition", "Kennedy described the group as including a NASA scientist and special-operations personnel", "Kennedy described the unnamed group as including a very high-level NASA scientist, Navy SEALs and Green Berets.", "attributed_identification_claim", "All alleged participants remain unnamed and independently unverified."),
    ("claim-rfk-alleged-recovery-team-participation", "Kennedy said some alleged briefers had served on recovery teams", "Kennedy said the Navy SEALs and Green Berets he described had been on recovery teams.", "attributed_operational_claim", "The statement does not establish that any military unit participated in UAP recovery operations."),
    ("claim-rfk-alleged-uap-calling-capability", "Kennedy recounted a claim that unidentified objects could be called in", "Kennedy said the group told him that personnel had figured out how to call some unidentified ships in.", "second_order_attributed_claim", "No method, date, location, personnel, data or independently authenticated event was supplied."),
    ("claim-rfk-alleged-destroy-recover-orders", "Kennedy recounted alleged orders to destroy and recover unidentified objects", "Kennedy said he was told that personnel were under orders to destroy the objects and recover them.", "second_order_attributed_operational_claim", "No issuing authority, written order, operation, object or recovered material was publicly identified."),
    ("claim-rfk-requested-public-disclosure", "Kennedy said the group wanted him to speak publicly", "Kennedy said the group wanted him to make its information public and that he declined at the time because of concerns about being associated with conspiracy theories.", "attributed_firsthand_statement", "The recording verifies Kennedy's account of the request, not the underlying information."),
    ("claim-rfk-later-administration-briefings", "Kennedy said he later received briefings after entering the administration", "Kennedy said that he had received briefings after entering the administration and characterized the material as really crazy.", "attributed_government_access_claim", "The source does not identify the briefing authority, classification, evidence, subject boundaries or relationship to Kennedy's HHS role.")
]

for eid, name, summary, classification, boundary in claims:
    entity({
        "id": eid,
        "type": "claim",
        "name": name,
        "summary": summary,
        "relationships": [rel("contained_in", RECORD, role="structured attributed claim")],
        "referenceSources": [{"label": "Recorded Kennedy–Luna discussion and Sentinel News transcript", "url": SOURCE, "sourceType": "recorded_public_statement", "role": "claim_source"}],
        "claimMetadata": {"classification": classification, "knowledgePermanence": "permanent", "verificationStatus": "Statement recorded; underlying allegation independently unverified", "evidenceBoundary": boundary}
    })

entity({
    "id": RECORD,
    "type": "document",
    "entitySubtype": "Recorded Interview / Attributed UAP Briefing Claims",
    "name": "Robert F. Kennedy Jr. Statements Concerning UAP Briefings and Alleged Recovery Operations",
    "summary": "Permanent record of Robert F. Kennedy Jr.'s recorded conversation with Representative Anna Paulina Luna in which he described a transition-period approach by unnamed individuals, extraordinary recovery-related allegations attributed to them, and later briefings after he entered the administration. The recording establishes what Kennedy said, not whether the underlying allegations are true.",
    "date": "2026-10-09",
    "dateDisplay": "Reported October 9, 2026; conversation timestamp approximately 18:41–20:22",
    "eventCategory": "Recorded public statement / attributed briefing claim",
    "destinationPage": True,
    "visibleInDirectory": True,
    "searchable": True,
    "taxonomyStatus": "canonical",
    "relationships": [
        rel("references_person", RFK, role="speaker"),
        rel("references_person", "anna-paulina-luna", role="interview participant"),
        rel("references_organization", "nasa", role="unnamed scientist affiliation alleged by Kennedy; not institutional confirmation"),
        rel("references_organization", "united-states-navy", role="Navy SEAL affiliation alleged by Kennedy; not institutional confirmation"),
        rel("references_organization", "united-states-army", role="Green Beret affiliation alleged by Kennedy; not institutional confirmation"),
        rel("references_organization", "white-house", role="presidential-transition and later-administration context only"),
        rel("references_topic", "crash-retrievals", role="allegation context; not confirmation"),
        rel("references_topic", "uap-disclosure", role="public-disclosure context"),
        rel("references_topic", "government-transparency", role="evidence and declassification context"),
        *[rel("contains_claim", eid) for eid, *_ in claims]
    ],
    "referenceSources": [{"label": "Sentinel News — report, full transcript and embedded recording", "url": SOURCE, "sourceType": "reporting_with_primary_recording", "role": "primary_public_source"}],
    "recordMetadata": {
        "participants": ["Robert F. Kennedy Jr.", "Anna Paulina Luna"],
        "relevantTimestampStart": "18:41",
        "relevantTimestampEnd": "20:22",
        "publicationDate": "October 9, 2026",
        "evidenceClass": "Recorded public statement",
        "underlyingAllegationsVerified": False,
        "namedBriefers": False,
        "supportingDocumentsReleased": False
    },
    "researchLibraryMetadata": {
        "knowledgePermanence": "permanent",
        "principalValue": "Preserves a precisely attributable public statement concerning alleged UAP briefings and recovery operations.",
        "limitations": "No briefer identities, briefing materials, operational orders, dates, locations, mission records, sensor data or recovered materials were released.",
        "researchImplication": "The account may guide future documentary research, but it does not independently authenticate the extraordinary operations described."
    },
    "editorialNotes": {
        "attributionRule": "The recording verifies that Kennedy made the statements; it does not verify the activities he recounted.",
        "institutionalBoundary": "NASA, the Navy, the Army, the White House and HHS are not represented as confirming the allegations.",
        "lifecyclePrinciple": "News can age; knowledge does not."
    },
    "relatedNewsId": NEWS
})

write(ROOT / f"data/news/{NEWS}.json", {
    "id": NEWS,
    "recordType": "news_record",
    "contentType": "recorded_public_statement_attributed_uap_claims_news",
    "title": "RFK Jr. Says He Received UAP Briefings During and After Presidential Transition",
    "source": "Sentinel News",
    "author": "Baptiste Friscourt",
    "publicationDate": "2026-10-09",
    "publicationDateDisplay": "October 9, 2026",
    "originalUrl": SOURCE,
    "primarySourceUrl": SOURCE,
    "summary": "Robert F. Kennedy Jr. said in a recorded conversation with Representative Anna Paulina Luna that unnamed individuals approached him during the presidential transition to discuss UAP and that he later received additional briefings after entering the administration. The recording verifies his public statements, while the recovery-related allegations he recounted remain independently unverified.",
    "dateAdded": "2026-10-13",
    "newsStatus": "current",
    "knowledgePermanence": "permanent",
    "image": {"src": "../assets/news/rfk-jr-uap-briefing-statements-2026-10.png", "alt": "Editorial illustration of a senior government official discussing UAP briefings during a recorded interview, with a redacted file, audio waveform and unidentified military figures in the background.", "caption": "GreyAlien editorial illustration—not documentary imagery of the interview or alleged briefings."},
    "relatedEntityIds": [RECORD, RFK, "anna-paulina-luna", "nasa", "united-states-navy", "united-states-army", "white-house", "crash-retrievals", "uap-disclosure", "government-transparency", *[eid for eid, *_ in claims]],
    "relationships": [rel("references_publication", RECORD, role="permanent recorded-statement record"), rel("references_person", RFK, role="speaker"), rel("references_person", "anna-paulina-luna", role="conversation participant")],
    "visibility": {"latestGateway": True, "publicEntityDirectory": False, "landmark": False},
    "lifecycle": {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False},
    "editorialNotes": {"sourceHierarchy": "The recorded conversation and transcript establish what was said; Sentinel News supplies reporting context.", "evidenceBoundary": "No underlying recovery operation, government program or institutional participation is independently verified by this source.", "lifecyclePrinciple": "News can age; knowledge does not."}
})

for eid, kind, role in [
    ("anna-paulina-luna", "participated_in", "conversation participant"),
    ("nasa", "discussed_in_interview", "unnamed affiliation alleged; no institutional confirmation"),
    ("united-states-navy", "discussed_in_interview", "alleged SEAL affiliation; no institutional confirmation"),
    ("united-states-army", "discussed_in_interview", "alleged Green Beret affiliation; no institutional confirmation"),
    ("white-house", "references_publication", "transition and administration context"),
    ("crash-retrievals", "references_publication", "attributed allegation context"),
    ("uap-disclosure", "references_publication", "public statement and disclosure context"),
    ("government-transparency", "references_publication", "evidence-verification context")
]:
    enrich(eid, kind, role)

for path, record, label in [
    (ROOT / "data/news/index.json", NEWS, "V23.6D.13 RFK Jr. recorded-statement news ingestion"),
    (ROOT / "data/research-library/index.json", RECORD, "V23.6D.13 permanent attributed-statement ingestion")
]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"] = [record] + [x for x in data.get("records", []) if x != record]
    data["generatedBy"] = label
    write(path, data)

news_path = ROOT / "categories/latest-uap-news.html"
html = news_path.read_text(encoding="utf-8")
anchor = '          <article class="news-entry" id="pursue-pr135-bird-analysis-2026-10-06"'
block = f'''          <article class="news-entry" id="rfk-jr-uap-briefings-2026-10-09" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{SOURCE}" target="_blank" rel="noopener noreferrer">RFK Jr. Says He Received UAP Briefings During and After Presidential Transition</a></h2>
            <p class="news-meta">Sentinel News / Baptiste Friscourt · October 9, 2026 · Recorded Statement / Attributed Claims</p>
            <figure class="news-image"><img src="../assets/news/rfk-jr-uap-briefing-statements-2026-10.png" alt="Editorial illustration of a senior government official discussing UAP briefings during a recorded interview, with a redacted file, audio waveform and unidentified military figures in the background." loading="lazy"><figcaption>Editorial illustration—not documentary imagery of the interview or alleged briefings. AI-generated for GreyAlien.</figcaption></figure>
            <p>Robert F. Kennedy Jr. said in a recorded conversation with Representative Anna Paulina Luna that unnamed individuals approached him during the presidential transition to discuss UAP. He described extraordinary recovery-related claims attributed to that group and said he later received additional briefings after entering the administration.</p>
            <p><strong>Evidence status:</strong> The recording verifies that Kennedy made these statements. It does not independently verify the unnamed briefers, their credentials, alleged recovery operations, standing orders or recovered objects.</p>
            <p class="news-source-link"><a href="{SOURCE}" target="_blank" rel="noopener noreferrer">Read the Report and Transcript →</a></p>
            <div class="news-related" aria-label="Connected Record"><strong>Connected Record</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id={RECORD}">Permanent Statement Record</a><a class="topic-chip" href="../entities/entity.html?id={RFK}">Robert F. Kennedy Jr.</a><a class="topic-chip" href="../entities/entity.html?id=anna-paulina-luna">Anna Paulina Luna</a><a class="topic-chip" href="../entities/entity.html?id=uap-disclosure">UAP Disclosure</a><a class="topic-chip" href="../entities/entity.html?id=crash-retrievals">Crash-Retrieval Claims</a></div></div>
          </article>

'''
if anchor not in html:
    raise SystemExit("D12 news anchor missing")
news_path.write_text(html.replace(anchor, block + anchor, 1), encoding="utf-8")

research_path = ROOT / "categories/research-library.html"
html = research_path.read_text(encoding="utf-8")
anchor = '          <article class="research-entry" id="pursue-pr135-six-object-bird-analysis"'
block = f'''          <article class="research-entry" id="rfk-jr-uap-briefing-statements" data-knowledge-permanence="permanent">
            <p class="research-type">Recorded Interview / Attributed UAP Briefing Claims · Permanent</p>
            <h2><a href="../entities/entity.html?id={RECORD}">Robert F. Kennedy Jr. Statements Concerning UAP Briefings and Alleged Recovery Operations</a></h2>
            <p class="research-meta">Robert F. Kennedy Jr. and Anna Paulina Luna · Reported October 9, 2026 · Relevant segment approximately 18:41–20:22</p>
            <p>The recorded conversation preserves Kennedy's account of a transition-period approach by unnamed individuals and his statement that he later received additional briefings after entering the administration.</p>
            <p><strong>Attribution boundary:</strong> Kennedy described an unnamed NASA scientist, Navy SEALs and Green Berets and recounted claims involving recovery teams, calling objects in, and destroy-and-recover orders. No identities, briefing materials, operational records or recovered materials were released.</p>
            <p><strong>Evidence status:</strong> The source establishes what Kennedy publicly said. It does not authenticate the alleged operations or institutional participation.</p>
            <p class="research-source-link"><a href="{SOURCE}" target="_blank" rel="noopener noreferrer">Review Recording and Transcript →</a></p>
            <div class="research-related" aria-label="Connected Claims"><strong>Connected Claims</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id=claim-rfk-transition-uap-approach">Transition Approach</a><a class="topic-chip" href="../entities/entity.html?id=claim-rfk-alleged-briefer-composition">Claimed Briefer Composition</a><a class="topic-chip" href="../entities/entity.html?id=claim-rfk-alleged-destroy-recover-orders">Alleged Orders</a><a class="topic-chip" href="../entities/entity.html?id=claim-rfk-later-administration-briefings">Later Briefings</a><a class="topic-chip" href="latest-uap-news.html#rfk-jr-uap-briefings-2026-10-09">Related News Coverage</a></div></div>
          </article>

'''
if anchor not in html:
    raise SystemExit("D12 research anchor missing")
research_path.write_text(html.replace(anchor, block + anchor, 1), encoding="utf-8")

shell = ROOT / "entities/entity.html"
shell.write_text(shell.read_text(encoding="utf-8").replace("v=23.6d12", "v=23.6d13"), encoding="utf-8")
print("V23.6D.13 ingestion applied")
