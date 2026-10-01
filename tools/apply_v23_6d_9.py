#!/usr/bin/env python3
"""Apply V23.6D.9 PURSUE Release 06 records-provenance ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
COLL = "collection-2026-pursue-release-06"
NEWS = "2026-09-18-department-war-pursue-release-06"
RELEASE = "https://www.war.gov/News/Releases/Release/Article/4604795/department-of-war-publishes-sixth-release-of-unidentified-anomalous-phenomena-f/"
PORTAL = "https://www.war.gov/UFO/release/06/"

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def rel(kind, target, **extra):
    return {"type": kind, "target": target, **extra}

def add_rel(eid, kind, role):
    path = ENT / f"{eid}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not any(r.get("target") == COLL for r in data.get("relationships", [])):
        data.setdefault("relationships", []).append(rel(kind, COLL, role=role))
    if not any(s.get("url") == RELEASE for s in data.get("referenceSources", [])):
        data.setdefault("referenceSources", []).append({"label": "Official PURSUE Release 06 announcement", "url": RELEASE, "sourceType": "government_source", "role": "connected_release"})
    write(path, data)

claims = [
    ("claim-pursue-release-06-sixth-tranche", "Release 06 is PURSUE's sixth official records tranche", "The Department's September 18 announcement identifies this publication as the sixth release under PURSUE.", "government_release_fact"),
    ("claim-pursue-release-06-declassified-historical", "Release 06 contains declassified and historical UAP files", "The issuing Department describes the tranche as a release of declassified and historical UAP files; this collection-level description does not resolve the origin or accuracy of every embedded assertion.", "collection_description"),
    ("claim-pursue-release-06-official-custody", "Release 06 is maintained through the official WAR.GOV/UFO portal", "The government announcement directs users to the official PURSUE portal, which provides custody and publication provenance for the released files.", "provenance_fact"),
    ("claim-pursue-release-06-rolling-process", "PURSUE uses a rolling-release process", "The Department states that additional files are to be released on a rolling basis.", "government_process_fact"),
    ("claim-pursue-release-06-next-release", "The Department and partner agencies were preparing a subsequent release", "The September 18 statement says the Department and agency partners were actively working on the next release.", "time_bounded_government_statement"),
    ("claim-pursue-release-06-publication-not-authentication", "Official publication does not authenticate every claim inside a released file", "Government custody, declassification or publication establishes provenance and availability, not the truth of every historical, technical or witness assertion contained in a file.", "evidentiary_limitation"),
    ("claim-pursue-release-06-file-specific-review", "Release 06 files require source- and file-specific assessment", "Each document, image, audio item or video must be evaluated according to its authorship, date, purpose, chain of custody and evidentiary quality rather than inheriting a single collection-wide credibility judgment.", "methodological_requirement")
]
for eid, name, summary, classification in claims:
    write(ENT / f"{eid}.json", {
        "id": eid, "type": "claim", "name": name, "summary": summary,
        "relationships": [rel("references_publication", COLL, role="claim source")],
        "referenceSources": [{"label": "Official PURSUE Release 06 announcement", "url": RELEASE, "sourceType": "government_source", "role": "claim_source"}],
        "claimMetadata": {"classification": classification, "knowledgePermanence": "permanent", "assessment": "Supported at the collection level; embedded files retain independent evidentiary status."}
    })

manifest = {
    "snapshotDate": "2026-09-30", "snapshotTimezone": "America/New_York",
    "source": PORTAL, "releaseLabel": "Release 06", "releaseDate": "2026-09-18",
    "itemCount": 75, "fileTypes": {"documents": 59, "videos": 15, "audio": 1},
    "sourceOrganizations": {"Department of War": 67, "Local Law Enforcement": 8},
    "contentGroups": [
        {"name": "AAWSAP and Defense Intelligence Agency material", "treatment": "Commissioned literature reviews, technical hypotheses, contract records and program material remain distinct; inclusion does not establish operational capability."},
        {"name": "Tremonton historical case material", "treatment": "Film, case documentation, photographic analysis and personnel material are retained as historical records with file-specific provenance."},
        {"name": "Contemporary airborne sensor media", "treatment": "Videos and associated mission-report records are linked where the manifest supports a pairing; imagery alone is not treated as sufficient for physical identification."},
        {"name": "Local law-enforcement records", "treatment": "Records are preserved under their stated originating organization and are not reattributed to the Department merely because they are hosted in PURSUE."}
    ],
    "changePolicy": "This is a dated manifest snapshot. Later additions, replacements or metadata corrections on the live portal do not silently rewrite this record."
}

write(ENT / f"{COLL}.json", {
    "id": COLL, "type": "publication", "entitySubtype": "Government Records Collection / Declassification Tranche",
    "name": "PURSUE Release 06 — Declassified and Historical UAP Files",
    "summary": "The sixth official PURSUE tranche, published September 18, 2026, combining declassified and historical UAP documents and media under a government-hosted provenance container. Publication establishes custody and availability, not authentication of every embedded claim.",
    "date": "2026-09-18", "dateDisplay": "September 18, 2026", "eventCategory": "Government records release",
    "relationships": [
        rel("published_by", "department-of-defense", role="issuing department; official release uses Department of War"),
        rel("contained_in", "pursue", role="sixth release tranche"),
        rel("references_organization", "aaro", role="related government UAP records and historical-review context"),
        rel("references_organization", "defense-intelligence-agency", role="source context for AAWSAP materials"),
        rel("references_organization", "aawsap", role="program represented in released records"),
        rel("references_publication", "document-2026-pursue-uap-disclosure-legal-waiver", role="preceding protected-disclosure policy; no file-level causation asserted"),
        rel("references_publication", "record-group-615-uap-records-collection", role="related federal historical-record collection"),
        rel("references_publication", "document-2026-aaro-nufohrc-sole-source-notice", role="related historical-record integration"),
        rel("references_topic", "uap-disclosure"), rel("references_topic", "government-transparency"),
        *[rel("contains_claim", eid) for eid, *_ in claims]
    ],
    "officialLinks": [{"label": "Official Release 06 announcement", "url": RELEASE, "linkType": "government_source"}, {"label": "Official Release 06 portal", "url": PORTAL, "linkType": "government_records_collection"}],
    "referenceSources": [], "manifestSnapshot": manifest,
    "governmentCollectionMetadata": {
        "issuingAuthority": "U.S. Department of War (matched to GreyAlien's canonical U.S. Department of Defense entity)",
        "releaseNumber": 6, "publicationDate": "September 18, 2026", "status": "Official government records release",
        "classificationLanguage": "The Department describes the collection as declassified and historical UAP files.",
        "provenanceRule": "Portal publication establishes official custody and release provenance; each embedded file retains its own origin, purpose and evidentiary status.",
        "relatedNewsId": NEWS
    },
    "editorialNotes": {
        "authenticationDiscipline": "Official publication is not wholesale authentication of embedded claims.",
        "declassificationDiscipline": "Declassification permits release; it does not establish factual accuracy, completeness or extraordinary origin.",
        "aawsapDiscipline": "Commissioned review, technical hypothesis, contractual deliverable, original research and demonstrated capability are not interchangeable categories.",
        "waiverSequence": "The September 14 waiver precedes Release 06, but no individual Release 06 file is attributed to the waiver without file-level provenance.",
        "lifecyclePrinciple": "News can age; knowledge does not."
    }
})

write(ROOT / f"data/news/{NEWS}.json", {
    "id": NEWS, "recordType": "news_record", "contentType": "government_records_release_news",
    "title": "Department Publishes Sixth PURSUE Release of UAP Files",
    "source": "U.S. Department of War / PURSUE", "author": "U.S. Department of War", "publicationDate": "2026-09-18", "publicationDateDisplay": "September 18, 2026",
    "originalUrl": RELEASE, "primarySourceUrl": RELEASE,
    "summary": "The Department published the sixth PURSUE tranche of declassified and historical UAP records on WAR.GOV/UFO and said additional releases would continue on a rolling basis. GreyAlien preserves the tranche as an official provenance collection while assessing each embedded file independently.",
    "dateAdded": "2026-09-30", "newsStatus": "current", "knowledgePermanence": "permanent",
    "relatedEntityIds": [COLL, "pursue", "department-of-defense", "aaro", "aawsap", "defense-intelligence-agency", "document-2026-pursue-uap-disclosure-legal-waiver", "record-group-615-uap-records-collection", "uap-disclosure", "government-transparency", *[eid for eid, *_ in claims]],
    "relationships": [rel("references_publication", COLL, role="permanent government-records collection"), rel("references_organization", "department-of-defense", role="issuing department"), rel("references_organization", "pursue", role="release program")],
    "visibility": {"latestGateway": True, "publicEntityDirectory": False, "landmark": False},
    "lifecycle": {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False},
    "editorialNotes": {"sourceHierarchy": "Official Department release and portal are primary.", "authenticationDiscipline": "Publication does not authenticate every embedded assertion.", "lifecyclePrinciple": "News can age; knowledge does not."}
})

for eid, kind, role in [
    ("pursue", "references_publication", "sixth official release tranche"),
    ("department-of-defense", "produced_document", "issuing department"),
    ("aaro", "references_publication", "related historical-review context"),
    ("aawsap", "references_publication", "released program records"),
    ("defense-intelligence-agency", "references_publication", "AAWSAP source context"),
    ("record-group-615-uap-records-collection", "references_publication", "related government UAP archive"),
    ("document-2026-pursue-uap-disclosure-legal-waiver", "references_publication", "subsequent PURSUE publication event; no file-level causal claim"),
    ("document-2026-aaro-nufohrc-sole-source-notice", "references_publication", "related historical-record integration"),
    ("uap-disclosure", "references_publication", "official records publication"),
    ("government-transparency", "references_publication", "official records publication")
]: add_rel(eid, kind, role)

for index, record, label in [(ROOT/"data/news/index.json", NEWS, "V23.6D.9 Release 06 news ingestion"), (ROOT/"data/research-library/index.json", COLL, "V23.6D.9 Release 06 permanent collection ingestion")]:
    data = json.loads(index.read_text(encoding="utf-8")); data["records"] = [record] + [x for x in data.get("records", []) if x != record]; data["generatedBy"] = label; write(index, data)

news = ROOT / "categories/latest-uap-news.html"; html = news.read_text(encoding="utf-8")
anchor = '          <article class="news-entry" id="pursue-disclosure-waiver-2026-09-14"'
block = f'''          <article class="news-entry" id="pursue-release-06-2026-09-18" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{RELEASE}" target="_blank" rel="noopener noreferrer">Department Publishes Sixth PURSUE Release of UAP Files</a></h2>
            <p class="news-meta">U.S. Department of War / PURSUE · September 18, 2026 · Government Records Release</p>
            <p>The Department published the sixth PURSUE tranche of declassified and historical UAP files and said releases would continue on a rolling basis. The permanent GreyAlien record preserves the official collection, its dated manifest and its relationships to earlier government-records work.</p>
            <p><strong>Evidence discipline:</strong> Official custody, declassification and publication establish provenance and public availability—not the accuracy of every embedded claim or an extraordinary explanation for any media.</p>
            <p class="news-source-link"><a href="{RELEASE}" target="_blank" rel="noopener noreferrer">Read Official Government Release →</a></p>
            <div class="news-related" aria-label="Connected Government Records"><strong>Connected Records</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id={COLL}">Permanent Release 06 Collection</a><a class="topic-chip" href="../entities/entity.html?id=pursue">PURSUE</a><a class="topic-chip" href="../entities/entity.html?id=document-2026-pursue-uap-disclosure-legal-waiver">Disclosure Waiver</a><a class="topic-chip" href="../entities/entity.html?id=aawsap">AAWSAP</a><a class="topic-chip" href="../entities/entity.html?id=record-group-615-uap-records-collection">Record Group 615</a></div></div>
          </article>

'''
if anchor not in html: raise SystemExit("D8 news anchor missing")
news.write_text(html.replace(anchor, block + anchor, 1), encoding="utf-8")

research = ROOT / "categories/research-library.html"; html = research.read_text(encoding="utf-8")
anchor = '          <article class="research-entry" id="pursue-uap-disclosure-legal-waiver"'
block = f'''          <article class="research-entry" id="pursue-release-06" data-knowledge-permanence="permanent">
            <p class="research-type">Government Records Collection / Declassification Tranche · Permanent</p>
            <h2><a href="../entities/entity.html?id={COLL}">PURSUE Release 06 — Declassified and Historical UAP Files</a></h2>
            <p class="research-meta">U.S. Department of War / PURSUE · September 18, 2026 · Official government collection</p>
            <p>The sixth PURSUE tranche is represented as a collection-level provenance container with a dated manifest covering documents, videos and audio from Department and local law-enforcement sources. AAWSAP material, historical-case records and contemporary sensor media retain distinct source and evidence classifications.</p>
            <p><strong>Research caution:</strong> Declassification and official publication do not authenticate every embedded claim. Each file requires assessment of authorship, purpose, custody, metadata and corroboration.</p>
            <p class="research-source-link"><a href="{PORTAL}" target="_blank" rel="noopener noreferrer">Explore Official Release 06 Collection →</a></p>
            <div class="research-related" aria-label="Connected Government Records"><strong>Connected Records</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id=pursue">PURSUE</a><a class="topic-chip" href="../entities/entity.html?id=document-2026-pursue-uap-disclosure-legal-waiver">September 14 Waiver</a><a class="topic-chip" href="../entities/entity.html?id=aawsap">AAWSAP</a><a class="topic-chip" href="../entities/entity.html?id=defense-intelligence-agency">DIA</a><a class="topic-chip" href="latest-uap-news.html#pursue-release-06-2026-09-18">Related News Coverage</a></div></div>
          </article>

'''
if anchor not in html: raise SystemExit("D8 research anchor missing")
research.write_text(html.replace(anchor, block + anchor, 1), encoding="utf-8")

shell = ROOT / "entities/entity.html"; shell.write_text(shell.read_text(encoding="utf-8").replace("v=23.6d8", "v=23.6d9"), encoding="utf-8")
print("V23.6D.9 ingestion applied")
