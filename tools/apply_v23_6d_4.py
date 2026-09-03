#!/usr/bin/env python3
"""Apply V23.6D.4 AARO/private-archive cross-gateway ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data" / "entities"
NEWS_ID = "2026-09-02-defensescoop-aaro-nufohrc-access"
NOTICE_ID = "document-2026-aaro-nufohrc-sole-source-notice"
NOTICE_URL = "https://sam.gov/opp/a1b98934796e4bb3bb7215780ce82131/view"
ARTICLE_URL = "https://defensescoop.com/2026/09/02/pentagon-seeks-access-to-vast-private-ufo-records-collection/"
NUFOHRC_URL = "https://nufohrc.org/"
NARA_URL = "https://www.archives.gov/research/topics/uaps"

def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

entities = {
    "national-ufo-historical-records-center": {
        "id": "national-ufo-historical-records-center", "type": "organization",
        "name": "National UFO Historical Records Center", "entitySubtype": "Nonprofit Historical Archive",
        "summary": "New Mexico nonprofit organization that collects, preserves, digitizes, catalogs and works to provide access to historical UFO/UAP documents, media, case files and research collections.",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical", "isCanonical": True,
        "aliases": ["NUFOHRC", "National Unidentified Flying Object Historic Records Center"],
        "relationships": [
            {"type": "references_person", "target": "david-marler", "role": "founder and director"},
            {"type": "references_organization", "target": "aerial-phenomena-research-organization", "role": "preserves legacy collection", "context": "DefenseScoop reports that NUFOHRC took custody of the complete historical files of an early civilian scientific UFO research group; the APRO connection is represented as archive provenance."},
            {"type": "references_person", "target": "j-allen-hynek", "role": "preserves personal records", "context": "DefenseScoop reports that rare personal files formerly belonging to J. Allen Hynek are held within the archive."},
            {"type": "references_publication", "target": NOTICE_ID, "role": "intended subscription source"},
            {"type": "addresses_topic", "target": "government-transparency"}
        ],
        "officialLinks": [{"label": "National UFO Historical Records Center", "url": NUFOHRC_URL, "linkType": "official_website"}],
        "referenceSources": [{"label": "DefenseScoop archive and procurement report", "url": ARTICLE_URL, "sourceType": "news_report", "role": "secondary_reference"}],
        "archiveMetadata": {
            "mission": "Collect, preserve, digitize, catalog and provide access to historical UFO/UAP materials.",
            "location": "Rio Rancho, New Mexico",
            "organizationStatus": "501(c)(3) nonprofit corporation",
            "holdingsScope": "Historical documents, books, journals, newspapers, photographs, analog audio and video, case files and physical artifacts.",
            "scaleCaution": "Descriptions such as 'largest' and 'hundreds of thousands' are source-attributed claims, not independently audited GreyAlien measurements.",
            "evidenceCaution": "Archival custody preserves historical evidence and research provenance; it does not authenticate every claim contained in the records."
        }
    },
    "david-marler": {
        "id": "david-marler", "type": "person", "name": "David Marler", "entitySubtype": "UAP Historian and Archivist",
        "summary": "UAP historian, archival collector and founder of the National UFO Historical Records Center, associated with preserving major legacy collections of UFO/UAP documents and media.",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical",
        "relationships": [{"type": "affiliated_with", "target": "national-ufo-historical-records-center", "role": "founder and director"}],
        "officialLinks": [],
        "referenceSources": [
            {"label": "NUFOHRC official website", "url": NUFOHRC_URL, "sourceType": "organization_website", "role": "primary_reference"},
            {"label": "DefenseScoop archive report", "url": ARTICLE_URL, "sourceType": "news_report", "role": "secondary_reference"}
        ]
    },
    "aerial-phenomena-research-organization": {
        "id": "aerial-phenomena-research-organization", "type": "organization", "name": "Aerial Phenomena Research Organization", "entitySubtype": "Historical Civilian UFO Research Organization",
        "summary": "Civilian UFO research organization founded in the early 1950s, commonly known as APRO, whose historical files are reported among the legacy collections preserved by NUFOHRC.",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical", "aliases": ["APRO"],
        "relationships": [{"type": "references_organization", "target": "national-ufo-historical-records-center", "role": "legacy records preserved by", "context": "This relationship records archival custody, not organizational succession or endorsement."}],
        "officialLinks": [],
        "referenceSources": [{"label": "DefenseScoop archive report", "url": ARTICLE_URL, "sourceType": "news_report", "role": "archive_provenance"}],
        "editorialNotes": {"historicalTreatment": "The organization and its surviving records are represented historically; its case conclusions are not automatically treated as established facts."}
    },
    "record-group-615-uap-records-collection": {
        "id": "record-group-615-uap-records-collection", "type": "document", "name": "Record Group 615 — Unidentified Anomalous Phenomena Records Collection", "entitySubtype": "Government Records Collection",
        "summary": "National Archives collection established under sections 1841–1843 of the FY2024 National Defense Authorization Act to receive UAP records transferred by federal agencies on an ongoing basis.",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical",
        "relationships": [
            {"type": "held_by", "target": "national-archives", "context": "NARA established and maintains Record Group 615."},
            {"type": "addresses_topic", "target": "government-transparency"},
            {"type": "addresses_topic", "target": "uap-disclosure"},
            {"type": "references_organization", "target": "aaro", "role": "related federal historical-review context"}
        ],
        "officialLinks": [{"label": "National Archives — Record Group 615", "url": NARA_URL, "linkType": "government_record"}],
        "referenceSources": [],
        "recordsCollectionMetadata": {"authority": "FY2024 NDAA, Public Law 118-31, sections 1841–1843", "accessionStatus": "Rolling transfers from federal agencies", "distinction": "Federal records collection; separate from the privately held NUFOHRC archive."}
    },
    NOTICE_ID: {
        "id": NOTICE_ID, "type": "document", "name": "Notice of Intent to Sole Source: Historical UAP Data and Analysis Subscription", "entitySubtype": "Government Contracting Notice",
        "summary": "Washington Headquarters Services notice of intent to award a sole-source, firm-fixed-price subscription for AARO access to pre-1990 historical UAP data, metadata and analytical products associated with NUFOHRC. GreyAlien records this as a proposed procurement, not a verified completed award.",
        "date": "2026-07-31", "dateDisplay": "July 31, 2026", "eventCategory": "Government procurement notice",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical",
        "relationships": [
            {"type": "references_organization", "target": "aaro", "role": "requiring office"},
            {"type": "references_organization", "target": "department-of-defense", "role": "parent department"},
            {"type": "references_organization", "target": "national-ufo-historical-records-center", "role": "intended sole source"},
            {"type": "references_organization", "target": "national-archives", "role": "related federal records context"},
            {"type": "references_publication", "target": "record-group-615-uap-records-collection", "role": "complementary government archive"},
            {"type": "contains_claim", "target": "claim-aaro-seeks-nufohrc-pre-1990-access"},
            {"type": "contains_claim", "target": "claim-nufohrc-sole-source-justification"},
            {"type": "contains_claim", "target": "claim-private-archives-preserve-historical-context"}
        ],
        "officialLinks": [{"label": "SAM.gov opportunity a1b98934796e4bb3bb7215780ce82131", "url": NOTICE_URL, "linkType": "government_record"}],
        "referenceSources": [{"label": "DefenseScoop reporting", "url": ARTICLE_URL, "sourceType": "news_report", "role": "related_coverage"}],
        "procurementMetadata": {
            "noticeId": "NUFOHRC_20260731", "agency": "Washington Headquarters Services", "requiringOffice": "All-domain Anomaly Resolution Office",
            "noticeType": "Notice of intent to award sole source", "contractType": "Firm-fixed-price commercial data subscription",
            "postedDate": "July 31, 2026", "capabilityStatementDeadline": "August 17, 2026, 11:00 a.m. Eastern", "scheduledArchiveDate": "September 1, 2026",
            "periodOfPerformance": "One-year base period plus four one-year option periods",
            "scope": "Digital subscription access to proprietary pre-1990 historical UAP data, metadata and analytical products; not professional labor or advisory services.",
            "awardStatus": "No completed award independently verified by GreyAlien as of September 3, 2026",
            "ownershipCaution": "The contemplated transaction concerns subscription access, not government ownership or physical acquisition of the archive."
        },
        "researchLibraryMetadata": {"knowledgePermanence": "permanent", "recordClass": "Government procurement document", "primarySource": "SAM.gov", "relatedNewsId": NEWS_ID}
    },
    "claim-aaro-seeks-nufohrc-pre-1990-access": {
        "id": "claim-aaro-seeks-nufohrc-pre-1990-access", "type": "claim", "name": "AARO seeks subscription access to NUFOHRC’s pre-1990 historical records",
        "summary": "A Department of Defense notice states an intent to obtain commercial subscription access for AARO to pre-1990 historical UAP data, metadata and analytical products associated with NUFOHRC.",
        "claimStatus": "government_documented_proposed_action", "evidenceClass": "Government Record",
        "relationships": [{"type": "references_publication", "target": NOTICE_ID, "role": "primary evidence"}, {"type": "concerns", "target": "aaro"}, {"type": "concerns", "target": "national-ufo-historical-records-center"}],
        "officialLinks": [], "referenceSources": [{"label": "SAM.gov contracting notice", "url": NOTICE_URL, "sourceType": "government_record", "role": "primary_reference"}],
        "editorialNotes": {"statusCaution": "Seeking or intending to award is not equivalent to a completed contract award."}
    },
    "claim-nufohrc-sole-source-justification": {
        "id": "claim-nufohrc-sole-source-justification", "type": "claim", "name": "Government market research identified NUFOHRC as the only source meeting stated archive requirements",
        "summary": "The government’s stated sole-source rationale says market research found no other organization with the historical depth, volume of unique records and specialized analytical expertise needed to meet its minimum requirements.",
        "claimStatus": "government_stated_procurement_justification", "evidenceClass": "Government Record",
        "relationships": [{"type": "references_publication", "target": NOTICE_ID, "role": "primary evidence"}, {"type": "concerns", "target": "national-ufo-historical-records-center"}],
        "officialLinks": [], "referenceSources": [{"label": "SAM.gov contracting notice", "url": NOTICE_URL, "sourceType": "government_record", "role": "primary_reference"}],
        "editorialNotes": {"attribution": "This is the government's procurement justification, not an independently audited GreyAlien ranking of private archives."}
    },
    "claim-private-archives-preserve-historical-context": {
        "id": "claim-private-archives-preserve-historical-context", "type": "claim", "name": "Private civilian archives may preserve UAP records absent from government repositories",
        "summary": "Civilian researchers and organizations may retain historical UAP records or provenance that became fragmented, unindexed or unavailable through government repositories after official investigations ended.",
        "claimStatus": "supported_historical_research_rationale", "evidenceClass": "Contextual Inference",
        "relationships": [{"type": "references_publication", "target": NOTICE_ID, "role": "government rationale"}, {"type": "concerns", "target": "national-ufo-historical-records-center"}, {"type": "concerns", "target": "record-group-615-uap-records-collection"}],
        "officialLinks": [], "referenceSources": [
            {"label": "DefenseScoop historical archive report", "url": ARTICLE_URL, "sourceType": "news_report", "role": "secondary_reference"},
            {"label": "National Archives UAP records overview", "url": NARA_URL, "sourceType": "government_record", "role": "federal_archive_context"}
        ],
        "editorialNotes": {"caution": "This rationale does not establish that NUFOHRC holds undisclosed government secrets or that every archived report is authentic."}
    }
}

for eid, payload in entities.items():
    write_json(ENT / f"{eid}.json", payload)

# Enrich matched entities with bounded, reciprocal provenance relationships.
enrichments = {
    "aaro": [
        {"type": "references_publication", "target": NOTICE_ID, "role": "historical-data subscription notice"},
        {"type": "references_organization", "target": "national-ufo-historical-records-center", "role": "proposed subscription source"},
        {"type": "references_publication", "target": "record-group-615-uap-records-collection", "role": "related historical-record mandate"}
    ],
    "national-archives": [{"type": "references_publication", "target": "record-group-615-uap-records-collection", "role": "maintains federal UAP records collection"}],
    "j-allen-hynek": [
        {"type": "affiliated_with", "target": "project-blue-book", "role": "scientific consultant"},
        {"type": "references_organization", "target": "national-ufo-historical-records-center", "role": "personal records reportedly preserved by"}
    ],
    "project-blue-book": [{"type": "references_person", "target": "j-allen-hynek", "role": "scientific consultant"}]
}
for eid, additions in enrichments.items():
    path = ENT / f"{eid}.json"; obj = json.loads(path.read_text(encoding="utf-8")); rels = obj.setdefault("relationships", [])
    keys = {(r.get("type"), r.get("target"), r.get("role")) for r in rels}
    for rel in additions:
        if (rel.get("type"), rel.get("target"), rel.get("role")) not in keys: rels.append(rel)
    if eid == "national-archives":
        obj["referenceSources"] = [s for s in obj.setdefault("referenceSources", []) if s.get("url") != NARA_URL]
        obj["referenceSources"].append({"label": "NARA — UFO and UAP records", "url": NARA_URL, "sourceType": "government_record", "role": "primary_reference"})
    write_json(path, obj)

news = {
    "id": NEWS_ID, "recordType": "news_record", "contentType": "government_records_news",
    "title": "Pentagon seeks access to vast private UFO records collection", "source": "DefenseScoop", "author": "Brandi Vincent",
    "publicationDate": "2026-09-02", "publicationDateDisplay": "September 2, 2026", "originalUrl": ARTICLE_URL, "primarySourceUrl": NOTICE_URL,
    "summary": "DefenseScoop reports that AARO is moving toward a sole-source commercial subscription for digital access to pre-1990 historical UFO/UAP records held by the National UFO Historical Records Center. The proposed access could help AARO reconstruct government UAP history from 1945 onward, but it neither transfers ownership of the physical archive nor authenticates every claim in the preserved records.",
    "dateAdded": "2026-09-03", "newsStatus": "current", "knowledgePermanence": "permanent",
    "relatedEntityIds": [NOTICE_ID, "aaro", "national-ufo-historical-records-center", "david-marler", "record-group-615-uap-records-collection", "national-archives", "aerial-phenomena-research-organization", "j-allen-hynek", "project-blue-book", "government-transparency"],
    "relationships": [
        {"type": "surfaces_publication", "target": NOTICE_ID, "context": "The DefenseScoop article is the timely news surface; the SAM.gov notice remains the permanent government record."},
        {"type": "references_organization", "target": "aaro"}, {"type": "references_organization", "target": "national-ufo-historical-records-center"},
        {"type": "references_person", "target": "david-marler"}, {"type": "references_publication", "target": "record-group-615-uap-records-collection"},
        {"type": "references_organization", "target": "aerial-phenomena-research-organization"}, {"type": "references_person", "target": "j-allen-hynek"},
        {"type": "references_organization", "target": "project-blue-book"}
    ],
    "visibility": {"latestGateway": True, "publicEntityDirectory": False, "landmark": False},
    "lifecycle": {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False},
    "editorialNotes": {
        "sourceHierarchy": "The SAM.gov contracting notice is primary for procurement facts; DefenseScoop is the secondary news source.",
        "statusDiscipline": "The notice is represented as an intent to award. GreyAlien has not verified a completed award as of September 3, 2026.",
        "archiveDiscipline": "Government access to historical records does not validate every claim contained in those records.",
        "lifecyclePrinciple": "News can age; knowledge does not. Archiving this news record must not remove the notice, archive provenance, entities or graph relationships."
    }
}
write_json(ROOT / "data" / "news" / f"{NEWS_ID}.json", news)

# Index updates.
ni = ROOT / "data" / "news" / "index.json"; nidx = json.loads(ni.read_text(encoding="utf-8")); nidx["generatedBy"] = "V23.6D.4 AARO private-archive lifecycle ingestion"; nidx["records"] = [NEWS_ID] + [x for x in nidx["records"] if x != NEWS_ID]; write_json(ni, nidx)
ri = ROOT / "data" / "research-library" / "index.json"; ridx = json.loads(ri.read_text(encoding="utf-8")); ridx["generatedBy"] = "V23.6D.4 government records and historical archive ingestion"; ridx["records"] = [NOTICE_ID] + [x for x in ridx["records"] if x != NOTICE_ID]; write_json(ri, ridx)

# Latest News card, newest first.
news_html_path = ROOT / "categories" / "latest-uap-news.html"; html = news_html_path.read_text(encoding="utf-8")
marker = '          <article class="news-entry" id="vasco-scientific-challenge-2026-08-28"'
block = f'''          <article class="news-entry" id="aaro-nufohrc-access-2026-09-02" data-news-status="current" data-knowledge-permanence="permanent">\n            <h2><a href="{ARTICLE_URL}" target="_blank" rel="noopener noreferrer">Pentagon seeks access to vast private UFO records collection</a></h2>\n            <p class="news-meta">DefenseScoop / Brandi Vincent · September 2, 2026 · Government Records / Historical Archives</p>\n            <p>AARO is moving toward a proposed sole-source subscription for digital access to pre-1990 historical UFO/UAP records held by the National UFO Historical Records Center. The archive could supply context missing from fragmented government repositories, but the action concerns access—not ownership of the physical collection—and does not authenticate every claim in the records.</p>\n            <p><strong>Procurement status:</strong> The underlying government record is a notice of intent to award. GreyAlien has not independently verified a completed contract award as of September 3, 2026.</p>\n            <p class="news-source-link"><a href="{ARTICLE_URL}" target="_blank" rel="noopener noreferrer">Read Original Article →</a></p>\n            <div class="news-related" aria-label="Connected Records"><strong>Connected Records</strong><div class="topic-cloud">\n              <a class="topic-chip" href="../entities/entity.html?id={NOTICE_ID}">Government Contracting Notice</a>\n              <a class="topic-chip" href="../entities/entity.html?id=national-ufo-historical-records-center">NUFOHRC</a>\n              <a class="topic-chip" href="../entities/entity.html?id=aaro">AARO</a>\n              <a class="topic-chip" href="../entities/entity.html?id=david-marler">David Marler</a>\n              <a class="topic-chip" href="../entities/entity.html?id=record-group-615-uap-records-collection">Record Group 615</a>\n              <a class="topic-chip" href="../entities/entity.html?id=j-allen-hynek">J. Allen Hynek</a>\n              <a class="topic-chip" href="../entities/entity.html?id=project-blue-book">Project Blue Book</a>\n              <a class="topic-chip" href="../entities/entity.html?id=aerial-phenomena-research-organization">APRO</a>\n            </div></div>\n          </article>\n\n'''
if 'id="aaro-nufohrc-access-2026-09-02"' not in html:
    if marker not in html: raise SystemExit("Latest News insertion marker missing")
    html = html.replace(marker, block + marker)
news_html_path.write_text(html, encoding="utf-8")

# Permanent government document, newest first.
research_path = ROOT / "categories" / "research-library.html"; html = research_path.read_text(encoding="utf-8")
marker = '          <article class="research-entry" id="limits-velocity-recovery-pursue"'
block = f'''          <article class="research-entry" id="aaro-nufohrc-sole-source-notice" data-knowledge-permanence="permanent">\n            <p class="research-type">Government Document / Contracting Notice · Permanent</p>\n            <h2><a href="../entities/entity.html?id={NOTICE_ID}">Notice of Intent to Sole Source: Historical UAP Data and Analysis Subscription</a></h2>\n            <p class="research-meta">Washington Headquarters Services / AARO · Notice NUFOHRC_20260731 · Posted July 31, 2026</p>\n            <p>The notice describes an intended sole-source, firm-fixed-price commercial subscription providing AARO digital access to proprietary pre-1990 historical UAP data, metadata and analytical products associated with NUFOHRC. It describes a one-year base period with four possible one-year options and expressly distinguishes the subscription from professional labor or advisory services.</p>\n            <p><strong>Status:</strong> This is a notice of intent, not evidence that GreyAlien has verified a completed award. Subscription access would not transfer ownership of the physical archive.</p>\n            <p><strong>Historical significance:</strong> The proposed access connects AARO’s government historical review with major civilian collections reportedly preserved outside federal repositories, while remaining distinct from NARA’s Record Group 615.</p>\n            <p><strong>Evidence limitation:</strong> Preservation and government access do not authenticate every report or conclusion contained in the archive.</p>\n            <p class="research-source-link"><a href="{NOTICE_URL}" target="_blank" rel="noopener noreferrer">Read Government Notice →</a></p>\n            <div class="research-related" aria-label="Connected Records"><strong>Connected Records</strong><div class="topic-cloud">\n              <a class="topic-chip" href="../entities/entity.html?id=national-ufo-historical-records-center">NUFOHRC</a>\n              <a class="topic-chip" href="../entities/entity.html?id=aaro">AARO</a>\n              <a class="topic-chip" href="../entities/entity.html?id=david-marler">David Marler</a>\n              <a class="topic-chip" href="../entities/entity.html?id=record-group-615-uap-records-collection">Record Group 615</a>\n              <a class="topic-chip" href="../entities/entity.html?id=aerial-phenomena-research-organization">APRO</a>\n              <a class="topic-chip" href="../entities/entity.html?id=j-allen-hynek">J. Allen Hynek</a>\n              <a class="topic-chip" href="latest-uap-news.html#aaro-nufohrc-access-2026-09-02">Related News Coverage</a>\n            </div></div>\n          </article>\n\n'''
if 'id="aaro-nufohrc-sole-source-notice"' not in html:
    if marker not in html: raise SystemExit("Research Library insertion marker missing")
    html = html.replace(marker, block + marker)
research_path.write_text(html, encoding="utf-8")

# Advance shell cache key only; runtime code remains protected.
shell = ROOT / "entities" / "entity.html"; shell.write_text(shell.read_text(encoding="utf-8").replace("entity-engine.js?v=23.6d3", "entity-engine.js?v=23.6d4"), encoding="utf-8")
print("V23.6D.4 ingestion applied")
