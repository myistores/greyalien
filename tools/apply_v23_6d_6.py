#!/usr/bin/env python3
"""Apply V23.6D.6 lunar micron-scale technosignature ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
ARXIV = "https://arxiv.org/abs/2606.24028"
MEDIUM = "https://avi-loeb.medium.com/can-we-detect-alien-tech-in-the-form-of-sub-micron-dust-on-the-moon-ae14cf86fa76"
PUB = "publication-2026-micron-scale-technosignatures-lunar-regolith"
NEWS = "2026-09-08-avi-loeb-lunar-submicron-technosignatures"

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def entity(obj):
    obj.setdefault("relationships", [])
    obj.setdefault("officialLinks", [])
    obj.setdefault("referenceSources", [])
    write_json(ENT / f"{obj['id']}.json", obj)

def rel(kind, target, **extra):
    return {"type": kind, "target": target, **extra}

authors = [
    ("lewis-j-pinault", "Lewis J. Pinault", "Lead-listed and corresponding author of the 2026 arXiv preprint proposing a quantitative search for micron-scale technosignatures in lunar regolith."),
    ("brian-c-lacki", "Brian C. Lacki", "Co-author of the 2026 arXiv preprint modeling interstellar transport, lunar accumulation and detectability of hypothetical micron-scale technological material."),
    ("ian-a-crawford", "Ian A. Crawford", "Co-author of the 2026 arXiv preprint examining lunar regolith as a long-duration archive for possible micron-scale technosignatures."),
    ("andrew-p-v-siemion", "Andrew P. V. Siemion", "Co-author of the 2026 arXiv preprint proposing a machine-assisted and laboratory-forensic search for micron-scale technosignatures in lunar material."),
]
for eid, name, summary in authors:
    entity({
        "id": eid, "type": "person", "entitySubtype": "Researcher", "name": name, "summary": summary,
        "relationships": [rel("authored", PUB), rel("references_topic", "technosignatures")],
        "referenceSources": [{"label": "arXiv:2606.24028v4", "url": ARXIV, "sourceType": "scientific_preprint", "role": "author_reference"}],
        "profileMetadata": {"scope": "This bounded record documents authorship of the ingested paper; unrelated biographical or institutional claims are deferred unless independently verified."}
    })

entity({
    "id": "micron-scale-technosignatures", "type": "topic", "entitySubtype": "Scientific Research Topic",
    "name": "Micron-Scale Technosignatures",
    "summary": "Hypothetical microscopic engineered particles or technological debris considered as material technosignatures; the 2026 lunar-regolith preprint evaluates their transport, accumulation and detectability without reporting a detection.",
    "relationships": [rel("broader_topic", "technosignatures"), rel("associated_topic", "exo-archaeology"), rel("references_publication", PUB)],
    "referenceSources": [{"label": "Pinault et al. — Micron-Scale Technosignatures", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"}],
    "taxonomyStatus": "canonical", "destinationPage": True, "visibleInDirectory": True, "searchable": True,
    "editorialNotes": {"evidentiaryStatus": "Research concept and search target; no extraterrestrial technological particle has been detected."}
})

entity({
    "id": "exo-archaeology", "type": "topic", "entitySubtype": "Scientific Research Topic",
    "name": "Exo-Archaeology",
    "aliases": ["Interstellar archaeology", "Extraterrestrial artifact search"],
    "summary": "Search for durable physical evidence that could constrain or reveal past extraterrestrial technological activity, including material technosignatures preserved on Solar System bodies.",
    "relationships": [rel("associated_topic", "technosignatures"), rel("associated_topic", "scientific-investigation"), rel("references_publication", PUB)],
    "referenceSources": [{"label": "Pinault et al. — particulate technosignatures as exo-archaeology", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"}],
    "taxonomyStatus": "canonical", "destinationPage": True, "visibleInDirectory": True, "searchable": True,
    "editorialNotes": {"neutrality": "The research domain is a search framework, not evidence that extraterrestrial artifacts exist in the Solar System."}
})

entity({
    "id": "lunar-regolith", "type": "topic", "entitySubtype": "Planetary Science Research Object",
    "name": "Lunar Regolith",
    "summary": "The Moon's fragmented surface material, considered in the ingested study as a long-duration collector whose mixing, impact history, natural dust background and human contamination shape any search for microscopic technosignatures.",
    "relationships": [rel("associated_topic", "space-exploration"), rel("references_publication", PUB), rel("associated_topic", "micron-scale-technosignatures")],
    "referenceSources": [{"label": "Pinault et al. — lunar regolith search proposal", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"}],
    "taxonomyStatus": "canonical", "destinationPage": True, "visibleInDirectory": True, "searchable": True,
    "researchMetadata": {"role": "Modeled sample environment; no cubic-meter sample was collected or analyzed by this study.", "limitations": "Regolith gardening, impact processing, natural dust backgrounds, sample provenance and human contamination complicate interpretation."}
})

claims = [
    ("claim-micron-grain-interstellar-transport-feasibility", "Certain refractory micron-scale grains may survive modeled interstellar transport", "The v4 preprint reports that refractory grains with characteristic radii around 0.3 microns may traverse kiloparsec scales over residence times of roughly 0.1–1 Gyr under its gas-drag, sputtering and interstellar-medium assumptions.", "model_derived_physical_feasibility"),
    ("claim-lunar-regolith-technosignature-preservation", "Lunar regolith may preserve material relevant to long-timescale technosignature searches", "The authors identify the Moon as a potentially useful collector because of its airless surface, long exposure and limited geological reworking, while accounting for impact processing and regolith mixing.", "target_selection_rationale"),
    ("claim-lunar-technosignature-null-result-constraint", "A one-cubic-metre null result could constrain specified undirected technomaterial scenarios", "Under the v4 model, a null detection in about one cubic metre of characterized lunar regolith would exclude scenarios in which Solar-type stars typically disperse more than approximately 0.10 Earth-mass equivalents of long-lived artificial particulate debris over Galactic history.", "conditional_quantitative_finding"),
    ("claim-directed-technoparticle-delivery-regime", "Deliberately targeted particulate systems define a separate modeled detection regime", "The paper considers deliberately targeted artificial particulate matter separately from randomly dispersed debris and reports that some directed scenarios could yield substantially higher detection probabilities, subject to stronger assumptions.", "speculative_modeled_scenario"),
    ("claim-multimodal-technograin-screening", "Machine-vision triage and laboratory forensics could screen candidate anomalous grains", "The preprint outlines a multi-modal detection strategy that combines machine-vision triage with laboratory forensic analysis against a well-characterized natural background.", "proposed_research_methodology"),
    ("claim-no-lunar-technosignature-detection", "The lunar-regolith study proposes a search and reports no extraterrestrial technology detection", "The paper is a feasibility and constraint study. It does not report collection of the modeled cubic-metre sample or discovery of an extraterrestrial technological particle.", "evidentiary_status_clarification"),
]
for eid, name, summary, classification in claims:
    entity({
        "id": eid, "type": "claim", "name": name, "summary": summary,
        "relationships": [rel("references_publication", PUB, role="claim source"), rel("references_topic", "scientific-investigation")],
        "referenceSources": [{"label": "arXiv:2606.24028v4", "url": ARXIV, "sourceType": "scientific_preprint", "role": "claim_source"}],
        "claimMetadata": {"classification": classification, "knowledgePermanence": "permanent", "caution": "This claim records the authors' model, proposal or evidentiary clarification; it is not an independent GreyAlien detection claim."}
    })

relationships = [
    *[rel("references_person", eid, role="author") for eid, _, _ in authors],
    rel("addresses_topic", "micron-scale-technosignatures"),
    rel("addresses_topic", "exo-archaeology"),
    rel("applies_to", "lunar-regolith", role="modeled sample environment"),
    rel("references_topic", "technosignatures"),
    rel("references_topic", "scientific-investigation"),
    rel("references_topic", "space-exploration", role="connected gateway research"),
    *[rel("contains_claim", eid) for eid, _, _, _ in claims]
]

entity({
    "id": PUB, "type": "publication", "entitySubtype": "Scientific Preprint",
    "name": "Micron-Scale Technosignatures: How a Cubic Metre of Lunar Regolith May Begin to Constrain the Number of Past Technological Civilisations in the Galaxy",
    "summary": "Revised preprint by Lewis J. Pinault, Brian C. Lacki, Ian A. Crawford and Andrew P. V. Siemion modeling whether microscopic engineered particulate material could survive interstellar transport, accumulate in lunar regolith and be sought through machine-assisted and laboratory analysis.",
    "date": "2026-08-18", "dateDisplay": "August 18, 2026", "eventCategory": "Lunar material technosignature methodology",
    "relationships": relationships,
    "referenceSources": [
        {"label": "arXiv abstract and paper — version 4", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"},
        {"label": "Avi Loeb — lunar sub-micron technosignature commentary", "url": MEDIUM, "sourceType": "secondary_commentary", "role": "related_news"}
    ],
    "publicationMetadata": {
        "authors": [name for _, name, _ in authors],
        "repository": "arXiv", "identifier": "arXiv:2606.24028", "version": "v4",
        "initialSubmission": "June 23, 2026", "lastRevised": "August 18, 2026",
        "journalSubmissionHistory": "Originally submitted to the International Journal of Astrobiology on March 10, 2026; revised version 4 resubmitted August 17, 2026 in response to reviewer comments.",
        "publicationStatus": "Revised scientific preprint and journal resubmission; acceptance and formal publication not established",
        "validDoi": "10.48550/arXiv.2606.24028",
        "placeholderJournalDoiIngested": False,
        "subject": "Earth and Planetary Astrophysics"
    },
    "researchLibraryMetadata": {
        "knowledgePermanence": "permanent",
        "methodology": "Models gas drag, sputtering, interstellar-medium phase-dependent survival, radiation pressure, heliospheric filtering, lunar impact survival, regolith accumulation and mixing; then outlines machine-vision triage and laboratory forensic screening against natural backgrounds.",
        "sampleConcept": "Approximately one cubic metre of suitably characterized lunar regolith; modeled research scale, not a sample collected or analyzed in this study.",
        "principalFindings": "Refractory grains near 0.3 microns may survive modeled kiloparsec-scale transport over 0.1–1 Gyr. Under the undirected-debris model, a null result from roughly one cubic metre could constrain scenarios above approximately 0.10 Earth masses of cumulative long-lived particulate output per Solar-type star.",
        "limitations": "Results depend on uncertain assumptions about technological output, grain composition and size, transport and destruction, heliospheric entry, impact survival, lunar accumulation and mixing, sampling representativeness, contamination and the ability to distinguish engineered material from natural grains.",
        "researchImplication": "Lunar material could support a falsifiable exo-archaeology search in which both candidate detections and carefully characterized null results have scientific value.",
        "relatedNewsId": NEWS
    },
    "particleClasses": [
        {"name": "Arkhipov Particles", "scenario": "Undirected or passively transported technogenic debris", "status": "Hypothetical; not detected"},
        {"name": "Bracewell Particles", "scenario": "Deliberately dispatched microscopic technological systems", "status": "More speculative hypothetical regime; not detected"}
    ],
    "evidenceRecords": [
        {"id": "evidence-technograin-transport-survival", "objectType": "model", "finding": "Gas drag, sputtering and ISM-phase calculations define conditions under which refractory grains around 0.3 microns could survive long-distance transport.", "promotedToEntity": False},
        {"id": "evidence-heliospheric-slow-arrival-channel", "objectType": "model", "finding": "Solar radiation pressure and heliospheric filtering define a limited arrival channel compatible with some grains surviving lunar impact.", "promotedToEntity": False},
        {"id": "evidence-one-cubic-metre-null-model", "objectType": "conditional_constraint", "finding": "A modeled null result constrains specified high-output undirected-dispersal scenarios; no physical sample was examined.", "promotedToEntity": False},
        {"id": "evidence-lunar-backgrounds-contamination", "objectType": "background_control", "finding": "Natural lunar, interplanetary and interstellar grains plus human-introduced material must be distinguished from any candidate technosignature.", "promotedToEntity": False},
        {"id": "evidence-multimodal-grain-screening", "objectType": "proposed_method", "finding": "Machine-vision triage and laboratory forensic methods are proposed for candidate selection and escalation.", "promotedToEntity": False}
    ],
    "editorialNotes": {
        "noDetection": "No extraterrestrial technological particle was detected or claimed by the authors.",
        "sampleStatus": "The cubic-metre quantity is a modeled sampling concept, not a completed collection or experiment.",
        "constraintDiscipline": "The approximately 0.10-Earth-mass threshold is conditional on the v4 undirected-dispersal model and does not estimate actual civilization prevalence or output.",
        "authorship": "Avi Loeb wrote the news commentary but is not an author of the underlying preprint.",
        "publicationDiscipline": "Reviewer comments and journal resubmission do not establish acceptance, journal publication or completed peer review."
    }
})

write_json(ROOT / f"data/news/{NEWS}.json", {
    "id": NEWS, "recordType": "news_record", "contentType": "space_science_research_news",
    "title": "Scientists Propose Searching Lunar Dust for Microscopic Technosignatures",
    "source": "Avi Loeb / Medium", "author": "Avi Loeb", "publicationDate": "2026-09-08", "publicationDateDisplay": "September 8, 2026",
    "originalUrl": MEDIUM, "primarySourceUrl": ARXIV,
    "summary": "Avi Loeb highlights a revised preprint proposing that approximately one cubic metre of characterized lunar regolith could be screened for hypothetical micron-scale technological material. The paper models transport, survival, accumulation and conditional null-result constraints; it does not report finding alien technology or analyzing the proposed sample.",
    "dateAdded": "2026-09-10", "newsStatus": "current", "knowledgePermanence": "permanent",
    "relatedEntityIds": [PUB, "avi-loeb", "micron-scale-technosignatures", "exo-archaeology", "lunar-regolith", "technosignatures", "scientific-investigation", "space-exploration", "galileo-project", *[eid for eid, _, _ in authors]],
    "relationships": [
        rel("references_publication", PUB, role="surfaces primary research", context="The Medium article is the timely commentary surface; the v4 arXiv preprint is the permanent scientific object."),
        rel("references_person", "avi-loeb", role="commentary author"),
        rel("references_topic", "technosignatures"), rel("references_topic", "space-exploration"),
        rel("references_organization", "galileo-project", role="author context only")
    ],
    "visibility": {"latestGateway": True, "publicEntityDirectory": False, "landmark": False},
    "lifecycle": {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False},
    "editorialNotes": {
        "sourceHierarchy": "The arXiv v4 preprint is primary for scientific claims; Avi Loeb's Medium article is secondary commentary.",
        "noDetection": "Neither source reports detection of an extraterrestrial technological particle.",
        "authorship": "Avi Loeb is not listed as an author of arXiv:2606.24028.",
        "lifecyclePrinciple": "News can age; knowledge does not."
    }
})

# Enrich reused permanent entities with bounded reciprocal research paths.
enrichments = {
    "avi-loeb": rel("references_publication", PUB, role="commentary on research", context="Loeb's September 8 Medium article discusses the preprint; he is not one of its authors."),
    "technosignatures": rel("references_publication", PUB, role="material technosignature methodology"),
    "scientific-investigation": rel("references_publication", PUB, role="model-based, testable search proposal"),
    "space-exploration": rel("references_publication", PUB, role="featured lunar research", context="The paper proposes using characterized lunar regolith as a long-duration material archive for technosignature searches.")
}
for eid, relationship in enrichments.items():
    path = ENT / f"{eid}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not any(r.get("target") == PUB for r in data.get("relationships", [])):
        data.setdefault("relationships", []).append(relationship)
    if not any(s.get("url") == ARXIV for s in data.get("referenceSources", [])):
        data.setdefault("referenceSources", []).append({"label": "Pinault et al. — Micron-Scale Technosignatures", "url": ARXIV, "sourceType": "scientific_preprint", "role": "connected_research"})
    write_json(path, data)

# Gateway indexes.
for path, record, generated in [
    (ROOT / "data/news/index.json", NEWS, "V23.6D.6 lunar technosignature lifecycle ingestion"),
    (ROOT / "data/research-library/index.json", PUB, "V23.6D.6 lunar micron-scale technosignature research ingestion")
]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"] = [record] + [x for x in data.get("records", []) if x != record]
    data["generatedBy"] = generated
    write_json(path, data)

news_path = ROOT / "categories/latest-uap-news.html"
news_html = news_path.read_text(encoding="utf-8")
needle = '          <article class="news-entry" id="european-uap-barometer-2026-09-02"'
block = f'''          <article class="news-entry" id="lunar-micron-technosignatures-2026-09-08" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{MEDIUM}" target="_blank" rel="noopener noreferrer">Scientists Propose Searching Lunar Dust for Microscopic Technosignatures</a></h2>
            <p class="news-meta">Avi Loeb / Medium · September 8, 2026 · Space Science / Technosignature Methodology</p>
            <p>Avi Loeb highlights a revised scientific preprint proposing that approximately one cubic metre of characterized lunar regolith could be screened for hypothetical microscopic technological material. The authors model whether refractory grains might survive interstellar transport and lunar impact and show how a carefully controlled null result could constrain specified high-output scenarios.</p>
            <p><strong>Evidence status:</strong> No extraterrestrial technological particle has been detected, and the modeled cubic-metre sample has not been collected or analyzed. Avi Loeb wrote the commentary but is not an author of the underlying preprint.</p>
            <p class="news-source-link"><a href="{MEDIUM}" target="_blank" rel="noopener noreferrer">Read Original Article →</a></p>
            <div class="news-related" aria-label="Connected Research"><strong>Connected Research</strong><div class="topic-cloud">
              <a class="topic-chip" href="../entities/entity.html?id={PUB}">Permanent Research Record</a>
              <a class="topic-chip" href="../entities/entity.html?id=micron-scale-technosignatures">Micron-Scale Technosignatures</a>
              <a class="topic-chip" href="../entities/entity.html?id=exo-archaeology">Exo-Archaeology</a>
              <a class="topic-chip" href="../entities/entity.html?id=lunar-regolith">Lunar Regolith</a>
              <a class="topic-chip" href="../entities/entity.html?id=technosignatures">Technosignatures</a>
              <a class="topic-chip" href="space-exploration.html#lunar-micron-scale-technosignatures">Space Exploration</a>
              <a class="topic-chip" href="../entities/entity.html?id=avi-loeb">Avi Loeb</a>
            </div></div>
          </article>

'''
if needle not in news_html:
    raise SystemExit("Expected V23.6D.5 leading news card not found")
news_path.write_text(news_html.replace(needle, block + needle, 1), encoding="utf-8")

research_path = ROOT / "categories/research-library.html"
research_html = research_path.read_text(encoding="utf-8")
needle = '          <article class="research-entry" id="european-uap-barometer-2020-2025"'
block = f'''          <article class="research-entry" id="micron-scale-technosignatures-lunar-regolith" data-knowledge-permanence="permanent">
            <p class="research-type">Research / Revised Scientific Preprint · Permanent</p>
            <h2><a href="../entities/entity.html?id={PUB}">Micron-Scale Technosignatures: How a Cubic Metre of Lunar Regolith May Begin to Constrain the Number of Past Technological Civilisations in the Galaxy</a></h2>
            <p class="research-meta">Lewis J. Pinault, Brian C. Lacki, Ian A. Crawford &amp; Andrew P. V. Siemion · arXiv:2606.24028v4 · Revised August 18, 2026 · Journal resubmission / acceptance not established</p>
            <p>The authors model whether refractory particles near 0.3 microns could survive kiloparsec-scale interstellar transport over roughly 0.1–1 billion years, enter the Earth–Moon system and leave detectable material in lunar regolith.</p>
            <p><strong>Conditional constraint:</strong> Under the v4 undirected-debris model, a null result in approximately one cubic metre of characterized regolith could exclude scenarios in which Solar-type stars typically disperse more than about 0.10 Earth-mass equivalents of long-lived artificial particulate debris. This is a model-dependent limit—not an estimate of actual technological output.</p>
            <p><strong>Proposed method:</strong> Machine-vision triage and laboratory forensic analysis would screen grains against natural lunar, interplanetary and interstellar backgrounds while controlling sample provenance and human contamination.</p>
            <p><strong>Evidence status:</strong> The paper proposes a search and feasibility framework. It reports no extraterrestrial technology detection and did not collect or analyze the modeled cubic-metre sample.</p>
            <p class="research-source-link"><a href="{ARXIV}" target="_blank" rel="noopener noreferrer">Read Primary Research →</a></p>
            <div class="research-related" aria-label="Connected Research"><strong>Connected Research</strong><div class="topic-cloud">
              <a class="topic-chip" href="../entities/entity.html?id=micron-scale-technosignatures">Micron-Scale Technosignatures</a>
              <a class="topic-chip" href="../entities/entity.html?id=exo-archaeology">Exo-Archaeology</a>
              <a class="topic-chip" href="../entities/entity.html?id=lunar-regolith">Lunar Regolith</a>
              <a class="topic-chip" href="../entities/entity.html?id=claim-lunar-technosignature-null-result-constraint">Conditional Null-Result Constraint</a>
              <a class="topic-chip" href="../entities/entity.html?id=claim-no-lunar-technosignature-detection">No-Detection Clarification</a>
              <a class="topic-chip" href="space-exploration.html#lunar-micron-scale-technosignatures">Space Exploration</a>
              <a class="topic-chip" href="latest-uap-news.html#lunar-micron-technosignatures-2026-09-08">Related News Coverage</a>
            </div></div>
          </article>

'''
if needle not in research_html:
    raise SystemExit("Expected V23.6D.5 leading research card not found")
research_path.write_text(research_html.replace(needle, block + needle, 1), encoding="utf-8")

space_path = ROOT / "categories/space-exploration.html"
space_html = space_path.read_text(encoding="utf-8")
old = '''          <h2>Foundation structure</h2>
          <p>This section is ready to grow as a connected collection. Pages added here will link to related people, events, interviews, media, cases, research and official documents.</p>
          <h2>First content coming next</h2>
          <p>GreyAlien Version 2 establishes the structure. The first cornerstone pages will be added next.</p>'''
new = f'''          <article class="research-entry" id="lunar-micron-scale-technosignatures" data-knowledge-permanence="permanent">
            <p class="research-type">Featured Research / Lunar Science · Permanent</p>
            <h2><a href="../entities/entity.html?id={PUB}">Searching Lunar Regolith for Micron-Scale Technosignatures</a></h2>
            <p>A revised scientific preprint evaluates the Moon as a long-duration material archive and proposes screening characterized regolith for hypothetical microscopic engineered particles. The work connects lunar exploration, planetary materials, SETI and exo-archaeology while reporting no detection.</p>
            <div class="research-related" aria-label="Connected Lunar Research"><strong>Connected Research</strong><div class="topic-cloud">
              <a class="topic-chip" href="../entities/entity.html?id=lunar-regolith">Lunar Regolith</a>
              <a class="topic-chip" href="../entities/entity.html?id=micron-scale-technosignatures">Micron-Scale Technosignatures</a>
              <a class="topic-chip" href="../entities/entity.html?id=exo-archaeology">Exo-Archaeology</a>
              <a class="topic-chip" href="research-library.html#micron-scale-technosignatures-lunar-regolith">Research Library Record</a>
            </div></div>
          </article>'''
if old not in space_html:
    raise SystemExit("Expected Space Exploration placeholder not found")
space_path.write_text(space_html.replace(old, new, 1), encoding="utf-8")

# Advance only the entity shell cache key; runtime implementation remains unchanged.
shell = ROOT / "entities/entity.html"
text = shell.read_text(encoding="utf-8")
text = text.replace("entity-engine.js?v=23.6d5", "entity-engine.js?v=23.6d6")
shell.write_text(text, encoding="utf-8")

print("Applied V23.6D.6 lunar micron-scale technosignature ingestion.")
