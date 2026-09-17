#!/usr/bin/env python3
"""Apply V23.6D.8 PURSUE protected-disclosure waiver ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
OFFICIAL = "https://www.war.gov/News/Releases/Release/Article/4600020/department-of-war-issues-legal-waiver-to-authorize-unidentified-anomalous-pheno/"
PURSUE_URL = "https://www.war.gov/ufo/"
DEFENSESCOOP = "https://defensescoop.com/2026/09/14/pentagon-legal-relief-uap-whistleblowers-trump-project/"
DOC = "document-2026-pursue-uap-disclosure-legal-waiver"
NEWS = "2026-09-14-department-war-pursue-uap-disclosure-waiver"

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def rel(kind, target, **extra):
    return {"type": kind, "target": target, **extra}

def entity(obj):
    obj.setdefault("relationships", [])
    obj.setdefault("officialLinks", [])
    obj.setdefault("referenceSources", [])
    write_json(ENT / f"{obj['id']}.json", obj)

topics = [
    ("protected-uap-disclosures", "Protected UAP Disclosures", "Authorized reporting of UAP-related protected information through designated government recipients under specified legal and security controls."),
    ("nondisclosure-agreements", "Nondisclosure Agreements", "Agreements restricting disclosure of protected information; the September 2026 waiver affects specified civil and administrative enforcement provisions only for covered communications to PURSUE."),
    ("special-access-program-indoctrination-agreements", "Special Access Program Indoctrination Agreements", "Security agreements associated with access to Special Access Programs; the September 2026 waiver is narrowly limited to covered communications directed to PURSUE.")
]
for eid, name, summary in topics:
    entity({
        "id": eid, "type": "topic", "entitySubtype": "Government Policy Topic", "name": name, "summary": summary,
        "relationships": [rel("broader_topic", "government-transparency"), rel("references_publication", DOC), rel("associated_topic", "uap-disclosure")],
        "referenceSources": [{"label": "Official September 14 PURSUE waiver announcement", "url": OFFICIAL, "sourceType": "government_source", "role": "primary_reference"}],
        "taxonomyStatus": "canonical", "destinationPage": True, "visibleInDirectory": True, "searchable": True,
        "editorialNotes": {"scope": "This record does not create public-disclosure authority, automatic declassification or authentication of submitted claims."}
    })

claims = [
    ("claim-pursue-waiver-authorized-disclosure-mechanism", "The government established an authorized UAP disclosure mechanism through PURSUE", "The September 14 announcement establishes a legally protected route for covered current and former personnel to provide UAP-related National Defense Information directly to designated PURSUE representatives.", "government_policy_action"),
    ("claim-pursue-waiver-nda-protection", "Covered PURSUE communications receive specified NDA enforcement protection", "For covered disclosures to PURSUE, the waiver supersedes specified civil and administrative enforcement provisions in applicable nondisclosure agreements.", "bounded_legal_protection"),
    ("claim-pursue-waiver-sapia-protection", "Covered PURSUE communications receive specified SAPIA enforcement protection", "The waiver extends its bounded protection to specified civil and administrative enforcement provisions in applicable Special Access Program Indoctrination Agreements executed within the stated jurisdiction.", "bounded_legal_protection"),
    ("claim-pursue-waiver-channel-limitation", "The waiver is limited to communications directed to designated PURSUE representatives", "The announced protection is channel-specific and does not extend automatically to communications with the public, journalists, private organizations or unauthorized recipients.", "scope_limitation"),
    ("claim-pursue-waiver-no-public-disclosure-authority", "The waiver does not authorize unrestricted public disclosure", "Nothing in the announced waiver is represented as permission to publish or otherwise release classified or protected information publicly.", "evidentiary_and_legal_clarification"),
    ("claim-pursue-waiver-no-automatic-declassification", "Submission through PURSUE does not automatically declassify information", "Authorized receipt by PURSUE and declassification are separate actions; covered information may remain classified after submission.", "classification_clarification"),
    ("claim-pursue-waiver-review-potential-release", "PURSUE submissions may enter review for possible declassification or release", "The process can support secure review and potential declassification or public release, but the announcement does not guarantee either outcome for any submission.", "conditional_process_outcome")
]
for eid, name, summary, classification in claims:
    entity({
        "id": eid, "type": "claim", "name": name, "summary": summary,
        "relationships": [rel("references_publication", DOC, role="claim source"), rel("references_topic", "protected-uap-disclosures")],
        "referenceSources": [{"label": "Official September 14 PURSUE waiver announcement", "url": OFFICIAL, "sourceType": "government_source", "role": "claim_source"}],
        "claimMetadata": {"classification": classification, "knowledgePermanence": "permanent", "caution": "This record represents the bounded policy described by the government source and is not independent legal advice."}
    })

entity({
    "id": DOC, "type": "publication", "entitySubtype": "Government Document / Protected Disclosure Policy",
    "name": "Department of War Legal Waiver for UAP Disclosures to PURSUE",
    "summary": "September 14, 2026 government announcement establishing a channel-specific legal waiver for covered current and former personnel to provide UAP-related National Defense Information to designated PURSUE representatives without triggering specified civil or administrative NDA and SAPIA enforcement provisions.",
    "date": "2026-09-14", "dateDisplay": "September 14, 2026", "eventCategory": "Government protected-disclosure policy",
    "relationships": [
        rel("published_by", "department-of-defense", role="issuing department; official release uses Department of War"),
        rel("applies_to", "pursue", role="authorized recipient channel"),
        rel("addresses_topic", "protected-uap-disclosures"), rel("addresses_topic", "nondisclosure-agreements"),
        rel("addresses_topic", "special-access-program-indoctrination-agreements"),
        rel("references_topic", "uap-disclosure"), rel("references_topic", "government-transparency"),
        rel("references_organization", "aaro", role="related authorized UAP reporting and historical-review office"),
        rel("references_publication", "document-2026-aaro-nufohrc-sole-source-notice", role="related historical-record integration"),
        rel("references_publication", "record-group-615-uap-records-collection", role="related federal historical-record collection"),
        *[rel("contains_claim", eid) for eid, _, _, _ in claims]
    ],
    "officialLinks": [{"label": "Official Department release", "url": OFFICIAL, "linkType": "government_source"}, {"label": "Official PURSUE portal", "url": PURSUE_URL, "linkType": "government_source"}],
    "referenceSources": [
        {"label": "DefenseScoop — targeted legal relief explanation", "url": DEFENSESCOOP, "sourceType": "secondary_reporting", "role": "context"}
    ],
    "governmentDocumentMetadata": {
        "issuingAuthority": "U.S. Department of War (official release terminology; matched to GreyAlien's canonical U.S. Department of Defense entity)",
        "publicationDate": "September 14, 2026", "documentStatus": "Official government policy announcement",
        "coveredPopulation": "Covered current and former service members, civilian personnel and contractors with current or prior access to UAP-related National Defense Information, subject to the authoritative terms.",
        "coveredInformation": "UAP-related National Defense Information within the scope of the waiver.",
        "authorizedRecipient": "Designated PURSUE representatives.",
        "legalEffect": "Supersedes specified civil and administrative enforcement provisions in covered NDAs and SAPIAs for authorized communications directed to PURSUE.",
        "jurisdictionCaution": "The announcement describes agreements executed within the United States; implementation must follow the controlling text.",
        "notAuthorized": ["Unrestricted public disclosure", "Disclosure to unauthorized recipients", "Automatic declassification", "Automatic public release", "Authentication of submitted claims"],
        "relatedNewsId": NEWS
    },
    "processModel": [
        {"step": 1, "name": "Covered individual", "status": "Eligibility and information scope governed by authoritative terms"},
        {"step": 2, "name": "Authorized communication", "status": "Directed to designated PURSUE representative"},
        {"step": 3, "name": "Secure handling and review", "status": "Classification, security and legal controls remain applicable"},
        {"step": 4, "name": "Potential declassification or release", "status": "Possible outcome; not automatic or guaranteed"}
    ],
    "editorialNotes": {
        "channelLimitation": "Protected disclosure to designated PURSUE representatives is not public disclosure.",
        "classificationDiscipline": "Authorized submission does not itself declassify the information.",
        "authenticationDiscipline": "Government receipt or preservation does not authenticate a submitted allegation.",
        "legalLanguage": "GreyAlien describes the government policy and does not provide legal advice or expand its protections.",
        "departmentMatching": "The official release uses Department of War; the repository reuses the canonical Department of Defense entity rather than creating a disconnected duplicate."
    }
})

write_json(ROOT / f"data/news/{NEWS}.json", {
    "id": NEWS, "recordType": "news_record", "contentType": "government_policy_news",
    "title": "Department Establishes Protected Channel for UAP Disclosures to PURSUE",
    "source": "U.S. Department of War", "author": "U.S. Department of War", "publicationDate": "2026-09-14", "publicationDateDisplay": "September 14, 2026",
    "originalUrl": OFFICIAL, "primarySourceUrl": OFFICIAL,
    "summary": "The Department announced a channel-specific legal waiver allowing covered current and former personnel to provide UAP-related National Defense Information directly to designated PURSUE representatives without triggering specified civil or administrative NDA and SAPIA enforcement provisions. It is not authorization for public disclosure or automatic declassification.",
    "dateAdded": "2026-09-17", "newsStatus": "current", "knowledgePermanence": "permanent",
    "relatedEntityIds": [DOC, "pursue", "department-of-defense", "aaro", "protected-uap-disclosures", "nondisclosure-agreements", "special-access-program-indoctrination-agreements", "uap-disclosure", "government-transparency", "document-2026-aaro-nufohrc-sole-source-notice", "record-group-615-uap-records-collection", *[eid for eid, _, _, _ in claims]],
    "relationships": [rel("references_publication", DOC, role="permanent government-policy object"), rel("references_organization", "department-of-defense", role="issuing department"), rel("references_organization", "pursue", role="authorized recipient channel"), rel("references_topic", "protected-uap-disclosures")],
    "visibility": {"latestGateway": True, "publicEntityDirectory": False, "landmark": False},
    "lifecycle": {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False},
    "editorialNotes": {"sourceHierarchy": "The official September 14 release is primary; secondary reporting is contextual only.", "channelLimitation": "The waiver protects covered communications to designated PURSUE representatives, not unrestricted public disclosure.", "classificationDiscipline": "Submission does not automatically declassify information.", "authenticationDiscipline": "Receipt does not authenticate a submitted claim.", "lifecyclePrinciple": "News can age; knowledge does not."}
})

enrichments = {
    "pursue": ("references_publication", "authorized disclosure-channel policy"),
    "department-of-defense": ("produced_document", "issuing department; official release uses Department of War"),
    "aaro": ("references_publication", "related authorized UAP reporting and historical-review context"),
    "government-transparency": ("references_publication", "protected government reporting mechanism"),
    "uap-disclosure": ("references_publication", "channel-specific disclosure policy"),
    "document-2026-aaro-nufohrc-sole-source-notice": ("references_publication", "related historical-record integration"),
    "record-group-615-uap-records-collection": ("references_publication", "related federal historical-record collection")
}
for eid, (kind, role) in enrichments.items():
    path = ENT / f"{eid}.json"; data = json.loads(path.read_text(encoding="utf-8"))
    if not any(r.get("target") == DOC for r in data.get("relationships", [])):
        data.setdefault("relationships", []).append(rel(kind, DOC, role=role))
    if not any(s.get("url") == OFFICIAL for s in data.get("referenceSources", [])):
        data.setdefault("referenceSources", []).append({"label": "Official PURSUE legal-waiver announcement", "url": OFFICIAL, "sourceType": "government_source", "role": "connected_policy"})
    if eid == "department-of-defense":
        aliases = data.setdefault("aliases", [])
        if "U.S. Department of War" not in aliases: aliases.append("U.S. Department of War")
    write_json(path, data)

for path, record, generated in [
    (ROOT / "data/news/index.json", NEWS, "V23.6D.8 PURSUE waiver news lifecycle ingestion"),
    (ROOT / "data/research-library/index.json", DOC, "V23.6D.8 protected government disclosure policy ingestion")
]:
    data = json.loads(path.read_text(encoding="utf-8")); data["records"] = [record] + [x for x in data.get("records", []) if x != record]; data["generatedBy"] = generated; write_json(path, data)

news_path = ROOT / "categories/latest-uap-news.html"; html = news_path.read_text(encoding="utf-8")
needle = '          <article class="news-entry" id="slysh-haloes-2026-09-09"'
block = f'''          <article class="news-entry" id="pursue-disclosure-waiver-2026-09-14" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{OFFICIAL}" target="_blank" rel="noopener noreferrer">Department Establishes Protected Channel for UAP Disclosures to PURSUE</a></h2>
            <p class="news-meta">U.S. Department of War · September 14, 2026 · Government Policy / Protected Disclosure</p>
            <p>The Department announced a legal waiver allowing covered current and former personnel to provide UAP-related National Defense Information directly to designated PURSUE representatives without triggering specified civil or administrative enforcement provisions in applicable NDAs and Special Access Program Indoctrination Agreements.</p>
            <p><strong>Important limitation:</strong> This is a protected government reporting channel—not permission for unrestricted public disclosure. Submission to PURSUE does not automatically declassify information, guarantee public release or authenticate the underlying claim.</p>
            <p class="news-source-link"><a href="{OFFICIAL}" target="_blank" rel="noopener noreferrer">Read Official Government Release →</a></p>
            <div class="news-related" aria-label="Connected Government Records"><strong>Connected Records</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id={DOC}">Permanent Waiver Record</a><a class="topic-chip" href="../entities/entity.html?id=pursue">PURSUE</a><a class="topic-chip" href="../entities/entity.html?id=protected-uap-disclosures">Protected UAP Disclosures</a><a class="topic-chip" href="../entities/entity.html?id=nondisclosure-agreements">Nondisclosure Agreements</a><a class="topic-chip" href="../entities/entity.html?id=special-access-program-indoctrination-agreements">SAPIAs</a><a class="topic-chip" href="../entities/entity.html?id=government-transparency">Government Transparency</a></div></div>
          </article>

'''
if needle not in html: raise SystemExit("D7 news anchor missing")
news_path.write_text(html.replace(needle, block + needle, 1), encoding="utf-8")

research_path = ROOT / "categories/research-library.html"; html = research_path.read_text(encoding="utf-8")
needle = '          <article class="research-entry" id="slysh-haloes-cold-computing"'
block = f'''          <article class="research-entry" id="pursue-uap-disclosure-legal-waiver" data-knowledge-permanence="permanent">
            <p class="research-type">Government Document / Protected Disclosure Policy · Permanent</p>
            <h2><a href="../entities/entity.html?id={DOC}">Department of War Legal Waiver for UAP Disclosures to PURSUE</a></h2>
            <p class="research-meta">U.S. Department of War · September 14, 2026 · Official government policy announcement</p>
            <p>The waiver establishes an authorized route for covered current and former personnel to provide UAP-related National Defense Information to designated PURSUE representatives and supersedes specified civil and administrative enforcement provisions in applicable NDAs and SAPIAs for those communications.</p>
            <p><strong>Scope:</strong> The protection is channel-specific. It does not authorize disclosure to the public or unauthorized recipients, cancel every secrecy obligation, automatically declassify information or guarantee that a submission will be released.</p>
            <p><strong>Evidence discipline:</strong> Government receipt, review or preservation does not authenticate every allegation submitted through the process.</p>
            <p class="research-source-link"><a href="{OFFICIAL}" target="_blank" rel="noopener noreferrer">Read Official Government Source →</a></p>
            <div class="research-related" aria-label="Connected Government Policy"><strong>Connected Records</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id=pursue">PURSUE</a><a class="topic-chip" href="../entities/entity.html?id=aaro">AARO</a><a class="topic-chip" href="../entities/entity.html?id=claim-pursue-waiver-channel-limitation">Channel Limitation</a><a class="topic-chip" href="../entities/entity.html?id=claim-pursue-waiver-no-public-disclosure-authority">No Public-Disclosure Authority</a><a class="topic-chip" href="../entities/entity.html?id=claim-pursue-waiver-no-automatic-declassification">No Automatic Declassification</a><a class="topic-chip" href="latest-uap-news.html#pursue-disclosure-waiver-2026-09-14">Related News Coverage</a></div></div>
          </article>

'''
if needle not in html: raise SystemExit("D7 research anchor missing")
research_path.write_text(html.replace(needle, block + needle, 1), encoding="utf-8")

shell = ROOT / "entities/entity.html"; shell.write_text(shell.read_text(encoding="utf-8").replace("v=23.6d7", "v=23.6d8"), encoding="utf-8")
print("V23.6D.8 ingestion applied")
