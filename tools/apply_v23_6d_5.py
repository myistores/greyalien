#!/usr/bin/env python3
"""Apply V23.6D.5 European UAP Barometer cross-gateway ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
SOURCE = "https://www.uapcheck.com/news/updating-the-european-uap-barometer-reporting-trends-and-new-data-sources-2020-2025/3496/"
PRIOR_SOURCE = "https://www.uapcheck.com/news/european-uap-sightings-in-2019-2024-towards-a-broader-and-more-inclusive-euro-ufo-barometer/3239/"
PUB = "publication-2026-european-uap-barometer-2020-2025"
PRIOR = "publication-2025-european-uap-barometer-2019-2024"
NEWS = "2026-09-02-uapcheck-european-uap-barometer"

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def entity(obj):
    obj.setdefault("relationships", [])
    obj.setdefault("officialLinks", [])
    obj.setdefault("referenceSources", [])
    write_json(ENT / f"{obj['id']}.json", obj)

def rel(t, target, **extra):
    return {"type": t, "target": target, **extra}

entity({
    "id": "philippe-ailleris", "type": "person", "entitySubtype": "UAP Researcher",
    "name": "Philippe Ailleris",
    "summary": "European UAP researcher and author of the European UAP Barometer, whose work emphasizes structured observation reporting, comparative data analysis and the methodological limits of heterogeneous reporting systems.",
    "relationships": [rel("authored", PUB), rel("authored", PRIOR), rel("references_topic", "scientific-investigation")],
    "officialLinks": [],
    "referenceSources": [{"label": "European UAP Barometer 2020–2025", "url": SOURCE, "sourceType": "research_report", "role": "primary_reference"}],
    "profileMetadata": {"institutionalContext": "European Space Agency professional affiliation is biographical context; the Barometer is not represented as an ESA publication or agency finding."}
})

entity({
    "id": "uap-check", "type": "organization", "entitySubtype": "Research and Information Organization",
    "name": "UAP Check", "summary": "European UAP research and information organization that publishes scientific, methodological and policy-oriented material, including the European UAP Barometer.",
    "relationships": [rel("references_publication", PUB, role="publisher"), rel("references_publication", PRIOR, role="publisher")],
    "officialLinks": [{"label": "UAP Check", "url": "https://www.uapcheck.com/", "linkType": "official_website"}],
    "referenceSources": [{"label": "UAP Check — European UAP Barometer", "url": SOURCE, "sourceType": "publisher_page", "role": "primary_reference"}]
})

orgs = [
    ("mutual-ufo-network", "Mutual UFO Network", "MUFON", "International civilian organization that collects and investigates UFO/UAP reports; its European submissions are used as a complementary international reporting channel in the Barometer.", "https://mufon.com/"),
    ("national-ufo-reporting-center", "National UFO Reporting Center", "NUFORC", "Civilian reporting center whose public database includes European submissions used as a complementary reporting channel in the Barometer, subject to processing and publication discontinuities around 2023.", "https://nuforc.org/"),
    ("enigma-labs", "Enigma Labs", "Enigma", "Mobile application-based UAP reporting platform whose European data add a distinct digital reporting pathway to the Barometer for 2023–2025.", "https://enigmalabs.io/"),
    ("geipan", "GEIPAN", "GEIPAN", "French official unit for collecting, analyzing and publishing information about unidentified aerospace phenomena; used in the Barometer to illustrate how intake, investigation and publication stages produce different totals.", "https://www.cnes-geipan.fr/"),
]
for eid, name, alias, summary, url in orgs:
    entity({
        "id": eid, "type": "organization", "name": name, "aliases": [alias], "summary": summary,
        "relationships": [rel("references_publication", PUB, role="data provider", context="The organization or platform is an identified data source in the 2020–2025 European UAP Barometer.")],
        "officialLinks": [{"label": f"{name} official website", "url": url, "linkType": "official_website"}],
        "referenceSources": [{"label": "European UAP Barometer 2020–2025", "url": SOURCE, "sourceType": "research_report", "role": "data_source_documentation"}]
    })

entity({
    "id": "european-uap-barometer", "type": "research_project", "entitySubtype": "Comparative Reporting Framework",
    "name": "European UAP Barometer",
    "summary": "Collaborative research framework for documenting and comparing the European UAP reporting landscape while separating reporting-channel activity from the underlying incidence of anomalous phenomena.",
    "relationships": [rel("references_publication", PUB, role="2025 update"), rel("references_publication", PRIOR, role="previous edition"), rel("references_person", "philippe-ailleris", role="author"), rel("references_topic", "scientific-investigation")],
    "officialLinks": [],
    "referenceSources": [{"label": "UAP Check — Version 1.0", "url": SOURCE, "sourceType": "primary_research", "role": "primary_reference"}],
    "methodologyMetadata": {"coreDistinction": "Reporting totals measure activity in available reporting channels, not the true frequency of unusual aerial phenomena."}
})

entity({
    "id": PRIOR, "type": "publication", "entitySubtype": "Research Report",
    "name": "European UAP Sightings in 2019–2024: Towards a Broader and More Inclusive Euro UFO Barometer",
    "summary": "Previous European UAP Barometer edition providing the historical and methodological foundation updated by the 2020–2025 Version 1.0 report.",
    "relationships": [rel("references_person", "philippe-ailleris", role="author"), rel("published_by", "uap-check"), rel("references_publication", PUB, role="updated by")],
    "officialLinks": [],
    "referenceSources": [{"label": "UAP Check — 2019–2024 Barometer", "url": PRIOR_SOURCE, "sourceType": "research_report", "role": "primary_reference"}],
    "researchLibraryMetadata": {"knowledgePermanence": "permanent", "recordClass": "Prior research edition", "listingStatus": "Supporting connected research; not added as a separate gateway card in this release"}
})

claims = [
    ("claim-european-barometer-2025-total", "Included reporting channels recorded 7,193 European events for 2025", "The Barometer aggregates 7,193 reports for 2025 across national organizations, MUFON, NUFORC and Enigma Labs. This is a reporting-channel total, not a count of confirmed anomalous or unexplained events.", "descriptive_statistical_finding"),
    ("claim-european-barometer-infrastructure-effect", "Reporting infrastructure materially affects apparent UAP-report trends", "The report finds that platform adoption, contributor continuity, publication practices, language, public awareness and reporting access can alter visible totals without establishing a change in underlying UAP incidence.", "methodological_finding"),
    ("claim-european-barometer-uneven-coverage", "European UAP reporting coverage remains geographically uneven", "Countries with established organizations or visible platforms tend to produce more accessible reports, while low totals may reflect limited infrastructure or missing inputs rather than fewer observations.", "dataset_limitation"),
    ("claim-european-barometer-source-nonequivalence", "European UAP reporting sources are not methodologically equivalent", "National organizations, international databases, mobile applications and special-purpose systems use different intake, review, classification and publication practices and should not be treated as one homogeneous dataset.", "methodological_limitation"),
    ("claim-european-barometer-unresolved-outcomes", "Outcome-based unresolved-case tracking may be more informative than report totals alone", "The report proposes developing harmonized outcome indicators while treating its initial unresolved-case inventory as an incomplete proof of concept rather than a comprehensive European catalogue.", "research_recommendation"),
]
for eid, name, summary, classification in claims:
    entity({
        "id": eid, "type": "claim", "name": name, "summary": summary,
        "relationships": [rel("references_publication", PUB, role="claim source"), rel("references_topic", "scientific-investigation")],
        "officialLinks": [],
        "referenceSources": [{"label": "European UAP Barometer 2020–2025", "url": SOURCE, "sourceType": "primary_research", "role": "claim_source"}],
        "claimMetadata": {"classification": classification, "knowledgePermanence": "permanent", "caution": "The claim is attributed to the report and must retain its stated qualifications."}
    })

publication_relationships = [
    rel("references_person", "philippe-ailleris", role="author"),
    rel("published_by", "uap-check"),
    rel("references_publication", PRIOR, role="updates", context="Version 1.0 extends the previous 2019–2024 Barometer with 2025 data, new reporting channels and a pilot unresolved-case inventory."),
    rel("concerns", "european-uap-barometer", role="current edition"),
    rel("references_organization", "mutual-ufo-network", role="data source"), rel("references_organization", "national-ufo-reporting-center", role="data source"),
    rel("references_organization", "enigma-labs", role="data source"), rel("references_organization", "geipan", role="data source"),
    rel("references_topic", "scientific-investigation", role="methodological research"),
] + [rel("contains_claim", c[0]) for c in claims]

entity({
    "id": PUB, "type": "publication", "entitySubtype": "Research Report",
    "name": "Updating the European UAP Barometer: Reporting Trends and New Data Sources, 2020–2025",
    "summary": "Philippe Ailleris's Version 1.0 update aggregates European UAP reporting data for 2020–2025 across national organizations, MUFON, NUFORC and Enigma Labs while emphasizing that report counts measure reporting-system activity rather than the true frequency of anomalous phenomena.",
    "date": "2026-09-02", "dateDisplay": "September 2, 2026", "eventCategory": "European UAP reporting methodology",
    "relationships": publication_relationships,
    "officialLinks": [],
    "referenceSources": [{"label": "UAP Check — European UAP Barometer Version 1.0", "url": SOURCE, "sourceType": "research_report", "role": "primary_reference"}],
    "publicationMetadata": {"author": "Philippe Ailleris", "publisher": "UAP Check", "version": "1.0", "published": "September 2, 2026", "publicationStatus": "Publisher-hosted research report; formal journal peer review not established", "studyPeriod": "2020–2025"},
    "researchLibraryMetadata": {
        "knowledgePermanence": "permanent",
        "methodology": "Aggregates annual and country-level data from national civilian or official organizations, MUFON, NUFORC and Enigma Labs while analyzing each source category separately and documenting changes in coverage, processing and publication.",
        "dataset": "38,416 aggregated reports across the six-year study period, including 7,193 reports for 2025. Counts represent available reporting-channel records and are not asserted to be independent, investigated or unexplained cases.",
        "principalFindings": "European reporting is uneven and strongly shaped by reporting infrastructure. The addition of mobile-app and retrospective national data changes the composition and visibility of the dataset; a pilot inventory suggests future value in tracking investigation outcomes separately from submission totals.",
        "limitations": "Heterogeneous source methods, possible cross-platform overlap, a NUFORC processing/publication discontinuity around March 2023, missing or partial national inputs, changing contributor coverage and non-harmonized unresolved-case classifications limit direct comparison.",
        "researchImplication": "Source-aware and outcome-aware indicators are necessary before report volumes can support meaningful geographic or temporal interpretation.",
        "relatedNewsId": NEWS
    },
    "annualReportingTotals": [
        {"year": 2020, "nationalOrganizations": 6042, "mufon": 707, "nuforc": 118, "enigma": None, "total": 6867},
        {"year": 2021, "nationalOrganizations": 4325, "mufon": 578, "nuforc": 93, "enigma": None, "total": 4996},
        {"year": 2022, "nationalOrganizations": 5010, "mufon": 731, "nuforc": 277, "enigma": None, "total": 6018},
        {"year": 2023, "nationalOrganizations": 4595, "mufon": 718, "nuforc": 262, "enigma": 829, "total": 6404},
        {"year": 2024, "nationalOrganizations": 4446, "mufon": 449, "nuforc": 336, "enigma": 1707, "total": 6938},
        {"year": 2025, "nationalOrganizations": 4480, "mufon": 586, "nuforc": 492, "enigma": 1635, "total": 7193}
    ],
    "evidenceRecords": [
        {"id": "evidence-barometer-annual-source-totals", "objectType": "aggregate_table", "finding": "Annual totals by source category for 2020–2025.", "promotedToEntity": False},
        {"id": "evidence-barometer-nuforc-2023-break", "objectType": "methodological_discontinuity", "finding": "NUFORC processing, grading and posting practices make comparisons across March 2023 uncertain.", "promotedToEntity": False},
        {"id": "evidence-barometer-enigma-channel", "objectType": "new_reporting_channel", "finding": "Enigma Labs adds a mobile-app reporting layer beginning in 2023.", "promotedToEntity": False},
        {"id": "evidence-barometer-missing-national-inputs", "objectType": "coverage_limitation", "finding": "Important national inputs remain missing or partial, including UK, Italian and Romanian contributions.", "promotedToEntity": False},
        {"id": "evidence-barometer-unresolved-pilot", "objectType": "pilot_inventory", "finding": "The unresolved-case inventory is incomplete and uses non-harmonized classifications.", "promotedToEntity": False}
    ],
    "editorialNotes": {
        "centralCaution": "More recorded reports do not necessarily mean more UAP activity.",
        "eventStatus": "Reported events are not confirmed anomalous, independent, investigated or unresolved events.",
        "peerReview": "Acknowledged manuscript review is not represented as formal journal peer review.",
        "versioning": "Version 1.0 is preserved as a permanent historical research object; later revisions should be linked rather than silently overwriting its published claims."
    }
})

write_json(ROOT / f"data/news/{NEWS}.json", {
    "id": NEWS, "recordType": "news_record", "contentType": "research_methodology_news",
    "title": "European UAP Report Records 7,193 Events in 2025—but Warns That Reporting Growth Is Not Increased UAP Activity",
    "source": "UAP Check", "author": "Philippe Ailleris", "publicationDate": "2026-09-02", "publicationDateDisplay": "September 2, 2026",
    "originalUrl": SOURCE, "primarySourceUrl": SOURCE,
    "summary": "Philippe Ailleris's European UAP Barometer update records 7,193 reports across included European reporting channels for 2025, while warning that infrastructure, platform adoption, publication practices and missing national data prevent those totals from being interpreted as the true frequency of anomalous phenomena.",
    "dateAdded": "2026-09-07", "newsStatus": "current", "knowledgePermanence": "permanent",
    "relatedEntityIds": [PUB, "philippe-ailleris", "european-uap-barometer", "uap-check", "mutual-ufo-network", "national-ufo-reporting-center", "enigma-labs", "geipan", "scientific-investigation"],
    "relationships": [rel("surfaces_publication", PUB, context="The UAP Check publication is the timely news surface and the permanent research object represented in the Research Library."), rel("references_person", "philippe-ailleris"), rel("references_organization", "uap-check"), rel("references_topic", "scientific-investigation")],
    "visibility": {"latestGateway": True, "publicEntityDirectory": False, "landmark": False},
    "lifecycle": {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False},
    "editorialNotes": {"sourceHierarchy": "The UAP Check Version 1.0 report is both the original publication and primary research source.", "statisticalDiscipline": "Aggregated report totals are not presented as confirmed UAPs, unresolved cases or true UAP incidence.", "publicationStatus": "Publisher-hosted report; formal journal peer review not established.", "lifecyclePrinciple": "News can age; knowledge does not."}
})

# Add reciprocal connection to the existing methodology topic.
sci_path = ENT / "scientific-investigation.json"
sci = json.loads(sci_path.read_text(encoding="utf-8"))
if not any(r.get("target") == PUB for r in sci.get("relationships", [])):
    sci.setdefault("relationships", []).append(rel("references_publication", PUB, role="reporting-data methodology", context="The Barometer demonstrates why reporting pathways and data-processing practices must be understood before aggregate UAP counts are interpreted."))
write_json(sci_path, sci)

# Gateway indexes.
for path, record, generated in [
    (ROOT / "data/news/index.json", NEWS, "V23.6D.5 European UAP Barometer lifecycle ingestion"),
    (ROOT / "data/research-library/index.json", PUB, "V23.6D.5 European reporting-data methodology ingestion")
]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"] = [record] + [x for x in data.get("records", []) if x != record]
    data["generatedBy"] = generated
    write_json(path, data)

news_path = ROOT / "categories/latest-uap-news.html"
news_html = news_path.read_text(encoding="utf-8")
needle = '          <article class="news-entry" id="aaro-nufohrc-access-2026-09-02"'
block = f'''          <article class="news-entry" id="european-uap-barometer-2026-09-02" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{SOURCE}" target="_blank" rel="noopener noreferrer">European UAP Report Records 7,193 Events in 2025—but Warns That Reporting Growth Is Not Increased UAP Activity</a></h2>
            <p class="news-meta">UAP Check / Philippe Ailleris · September 2, 2026 · Research / Reporting-Data Methodology</p>
            <p>The Version 1.0 European UAP Barometer combines national reporting data with European submissions to MUFON, NUFORC and Enigma Labs. It records 7,193 reports for 2025, but emphasizes that reporting infrastructure, app adoption, screening, publication practices and missing inputs can change the visible totals without demonstrating a change in the underlying frequency of unusual aerial observations.</p>
            <p><strong>Statistical caution:</strong> These are aggregated reporting-channel events—not 7,193 confirmed anomalous, independent, investigated or unexplained cases.</p>
            <p class="news-source-link"><a href="{SOURCE}" target="_blank" rel="noopener noreferrer">Read Original Research →</a></p>
            <div class="news-related" aria-label="Connected Research"><strong>Connected Research</strong><div class="topic-cloud">
              <a class="topic-chip" href="../entities/entity.html?id={PUB}">Permanent Research Record</a>
              <a class="topic-chip" href="../entities/entity.html?id=philippe-ailleris">Philippe Ailleris</a>
              <a class="topic-chip" href="../entities/entity.html?id=european-uap-barometer">European UAP Barometer</a>
              <a class="topic-chip" href="../entities/entity.html?id=mutual-ufo-network">MUFON</a>
              <a class="topic-chip" href="../entities/entity.html?id=national-ufo-reporting-center">NUFORC</a>
              <a class="topic-chip" href="../entities/entity.html?id=enigma-labs">Enigma Labs</a>
              <a class="topic-chip" href="../entities/entity.html?id=geipan">GEIPAN</a>
            </div></div>
          </article>

'''
if needle not in news_html:
    raise SystemExit("Expected leading V23.6D.4 news block not found")
news_path.write_text(news_html.replace(needle, block + needle, 1), encoding="utf-8")

research_path = ROOT / "categories/research-library.html"
research_html = research_path.read_text(encoding="utf-8")
needle = '          <article class="research-entry" id="aaro-nufohrc-sole-source-notice"'
block = f'''          <article class="research-entry" id="european-uap-barometer-2020-2025" data-knowledge-permanence="permanent">
            <p class="research-type">Research / Statistical Methodology Report · Permanent</p>
            <h2><a href="../entities/entity.html?id={PUB}">Updating the European UAP Barometer: Reporting Trends and New Data Sources, 2020–2025</a></h2>
            <p class="research-meta">Philippe Ailleris · UAP Check · Version 1.0 · September 2, 2026 · Publisher-hosted report / formal journal peer review not established</p>
            <p>The report aggregates European UAP submissions across national organizations, MUFON, NUFORC and Enigma Labs. It documents 38,416 available reports across 2020–2025, including 7,193 in 2025. These reporting-channel totals are not a measurement of actual anomalous activity.</p>
            <p><strong>Methodology:</strong> Annual and country-level totals are separated by source category so changes in platform adoption, national coverage, processing and publication can be examined before geographic or temporal comparisons are made.</p>
            <p><strong>Limitations:</strong> Sources are not methodologically equivalent; reports may overlap; NUFORC has a processing discontinuity around March 2023; important national inputs remain incomplete; and unresolved-case classifications are not harmonized.</p>
            <p><strong>Research direction:</strong> The pilot unresolved-case inventory points toward separating submission volume from investigation outcomes, but it is not a comprehensive European catalogue.</p>
            <p class="research-source-link"><a href="{SOURCE}" target="_blank" rel="noopener noreferrer">Read Primary Research →</a></p>
            <div class="research-related" aria-label="Connected Research"><strong>Connected Research</strong><div class="topic-cloud">
              <a class="topic-chip" href="../entities/entity.html?id=european-uap-barometer">European UAP Barometer</a>
              <a class="topic-chip" href="../entities/entity.html?id=philippe-ailleris">Philippe Ailleris</a>
              <a class="topic-chip" href="../entities/entity.html?id=claim-european-barometer-2025-total">2025 Aggregate Total</a>
              <a class="topic-chip" href="../entities/entity.html?id=claim-european-barometer-infrastructure-effect">Infrastructure Effect</a>
              <a class="topic-chip" href="../entities/entity.html?id=claim-european-barometer-source-nonequivalence">Source Non-Equivalence</a>
              <a class="topic-chip" href="../entities/entity.html?id=claim-european-barometer-unresolved-outcomes">Unresolved-Case Direction</a>
              <a class="topic-chip" href="latest-uap-news.html#european-uap-barometer-2026-09-02">Related News Coverage</a>
            </div></div>
          </article>

'''
if needle not in research_html:
    raise SystemExit("Expected leading V23.6D.4 research block not found")
research_path.write_text(research_html.replace(needle, block + needle, 1), encoding="utf-8")

# Advance only the shell cache key; runtime implementation remains unchanged.
shell = ROOT / "entities/entity.html"
shell_text = shell.read_text(encoding="utf-8")
shell_text = shell_text.replace("entity-engine.js?v=23.6d4", "entity-engine.js?v=23.6d5")
shell.write_text(shell_text, encoding="utf-8")

print("Applied V23.6D.5 European UAP Barometer ingestion.")
