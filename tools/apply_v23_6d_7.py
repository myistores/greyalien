#!/usr/bin/env python3
"""Apply V23.6D.7 Slysh-halo cold-computing technosignature ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
ARXIV = "https://arxiv.org/abs/2608.31153"
NEWS_URL = "https://www.universetoday.com/articles/if-alien-civilizations-use-hyper-efficient-computers-they-will-have-a-distinct-energy-signal-we-can"
PUB = "publication-2026-slysh-haloes-cold-computing-technosignature"
NEWS = "2026-09-09-universe-today-slysh-haloes"
IMAGE = "../assets/news/slysh-haloes-cold-computing-2026-09.png"

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def entity(obj):
    obj.setdefault("relationships", [])
    obj.setdefault("officialLinks", [])
    obj.setdefault("referenceSources", [])
    write_json(ENT / f"{obj['id']}.json", obj)

def rel(kind, target, **extra):
    return {"type": kind, "target": target, **extra}

entity({
    "id": "michael-garrett", "type": "person", "entitySubtype": "Researcher", "name": "Michael Garrett",
    "summary": "Astronomer and author of the 2026 Slysh-halo preprint proposing a search for cold-computing waste heat at far-infrared and submillimetre wavelengths.",
    "relationships": [rel("authored", PUB), rel("references_topic", "technosignatures")],
    "referenceSources": [{"label": "Garrett — Slysh haloes", "url": ARXIV, "sourceType": "scientific_preprint", "role": "author_reference"}],
    "profileMetadata": {"scope": "This bounded record documents authorship and the affiliations stated with the paper; unrelated biography is deferred.", "affiliationsAsReported": ["University of Manchester", "Leiden University", "University of Malta"]}
})

topics = [
    ("slysh-halo", "Slysh Halo", "A hypothetical cold partial Dyson swarm whose distributed computing radiators would produce grey, line-free far-infrared or submillimetre waste-heat emission from the outer regions of a planetary system."),
    ("cold-computing", "Cold Computing", "The modeled use of very low operating temperatures to reduce the thermodynamic energy cost of irreversible computation; its application to extraterrestrial civilizations remains hypothetical."),
    ("waste-heat-technosignatures", "Waste-Heat Technosignatures", "Searches for thermal radiation that could result from technological energy use, including the cold far-infrared and submillimetre regime proposed for Slysh haloes.")
]
for eid, name, summary in topics:
    entity({
        "id": eid, "type": "topic", "entitySubtype": "Scientific Research Topic", "name": name, "summary": summary,
        "relationships": [rel("broader_topic", "technosignatures"), rel("references_publication", PUB), rel("associated_topic", "scientific-investigation")],
        "referenceSources": [{"label": "Garrett — Slysh haloes", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"}],
        "taxonomyStatus": "canonical", "destinationPage": True, "visibleInDirectory": True, "searchable": True,
        "editorialNotes": {"evidentiaryStatus": "Hypothetical, model-derived search concept; no Slysh halo has been detected."}
    })

claims = [
    ("claim-slysh-landauer-cold-computation", "Lower-temperature irreversible computation has a lower thermodynamic energy cost", "The paper applies Landauer scaling, in which the minimum energy cost of irreversible computation is proportional to operating temperature, as the physical motivation for cold computing.", "physical_principle_application"),
    ("claim-slysh-submillimetre-signature", "Distributed cold computing could produce a submillimetre waste-heat signature", "Garrett models a partial swarm of cold radiators whose aggregated grey, line-free thermal emission could appear in the far-infrared or submillimetre regime.", "modeled_technosignature"),
    ("claim-slysh-m-dwarf-suitability", "M-dwarf systems may be favorable modeled search targets", "The preprint identifies M dwarfs as especially favorable under its energetic, thermal and observational assumptions.", "modeled_target_selection"),
    ("claim-slysh-archival-survey-constraints", "Existing survey archives may constrain cold circumstellar dissipation", "The paper proposes reinterpreting DEBRIS, DUNES and SONS and using Planck, JCMT, ALMA and NOEMA archives to constrain or search for cold waste heat, including model-dependent sensitivity near 10^20 W.", "proposed_observational_method"),
    ("claim-slysh-natural-source-degeneracy", "Natural cold debris can imitate parts of a Slysh-halo signature", "Cold dust, debris structures, background galaxies, line-emitting sources and instrumental effects can produce confusing signals, so wavelength or excess emission alone is not technological evidence.", "alternative_explanation"),
    ("claim-slysh-null-result-value", "A systematic null search could constrain the modeled technosignature class", "The proposed three-tier search program could place limits on cold Dysonian waste heat even if it finds no qualifying candidates.", "conditional_null_result"),
    ("claim-no-slysh-halo-detection", "The Slysh-halo paper reports no extraterrestrial technology detection", "The publication introduces a theoretical object class, observational discriminants and a search program; it does not report an observed Slysh halo or extraterrestrial civilization.", "evidentiary_status_clarification")
]
for eid, name, summary, classification in claims:
    entity({
        "id": eid, "type": "claim", "name": name, "summary": summary,
        "relationships": [rel("references_publication", PUB, role="claim source"), rel("references_topic", "scientific-investigation")],
        "referenceSources": [{"label": "arXiv:2608.31153v1", "url": ARXIV, "sourceType": "scientific_preprint", "role": "claim_source"}],
        "claimMetadata": {"classification": classification, "knowledgePermanence": "permanent", "caution": "Records a physical principle, model, proposed method, alternative explanation or evidentiary clarification; not an independent detection claim."}
    })

entity({
    "id": PUB, "type": "publication", "entitySubtype": "Scientific Preprint",
    "name": "Slysh haloes: the waste heat of cold computing as a submillimetre technosignature",
    "summary": "Michael Garrett's preprint models cold, distributed computing radiators as a partial Dyson swarm and proposes archival and targeted searches for their far-infrared or submillimetre waste heat while emphasizing natural-source discrimination.",
    "date": "2026-08-31", "dateDisplay": "August 31, 2026", "eventCategory": "Cold-computing technosignature methodology",
    "relationships": [
        rel("references_person", "michael-garrett", role="author"), rel("addresses_topic", "slysh-halo"),
        rel("addresses_topic", "cold-computing"), rel("addresses_topic", "waste-heat-technosignatures"),
        rel("references_topic", "technosignatures"), rel("references_topic", "scientific-investigation"),
        rel("references_topic", "space-exploration", role="connected gateway research"),
        rel("references_publication", "publication-2026-micron-scale-technosignatures-lunar-regolith", role="complementary technosignature methodology"),
        *[rel("contains_claim", eid) for eid, _, _, _ in claims]
    ],
    "referenceSources": [
        {"label": "arXiv abstract and preprint — version 1", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"},
        {"label": "Universe Today — cold-computing technosignature coverage", "url": NEWS_URL, "sourceType": "secondary_reporting", "role": "related_news"}
    ],
    "publicationMetadata": {
        "authors": ["Michael Garrett"], "repository": "arXiv", "identifier": "arXiv:2608.31153", "version": "v1",
        "submitted": "August 31, 2026", "publicationStatus": "Scientific preprint submitted to MNRAS; peer review and acceptance not established",
        "validDoi": "10.48550/arXiv.2608.31153", "subjects": ["Instrumentation and Methods for Astrophysics", "Popular Physics"],
        "extent": "14 pages, 3 figures, 6 tables"
    },
    "researchLibraryMetadata": {
        "knowledgePermanence": "permanent",
        "methodology": "Combines Landauer scaling, thermal-equilibrium and radiator-area arguments with modeled spectral emission, archival survey sensitivity, six observational discriminants and a proposed three-tier search program.",
        "principalFindings": "Cold computing in the approximate 5–30 K regime could shift hypothetical waste heat into far-infrared and submillimetre bands. Archival nearby-star surveys may constrain cold circumstellar dissipation near 10^20 W under the model, with M dwarfs highlighted as favorable targets.",
        "limitations": "The architecture and civilization behavior are hypothetical; diffuse emission may be faint; detectability depends on temperature, luminosity, geometry, distance and instrument response; cold dust, debris, galaxies, spectral-line sources and instrumental effects can mimic parts of the signature.",
        "researchImplication": "Existing archives and targeted observations can test a colder region of Dysonian waste-heat parameter space, and null results can constrain the modeled class.",
        "relatedNewsId": NEWS
    },
    "evidenceRecords": [
        {"id": "evidence-slysh-landauer-scaling", "objectType": "physical_model", "finding": "The minimum energy cost of irreversible computation scales with temperature.", "promotedToEntity": False},
        {"id": "evidence-slysh-temperature-luminosity-phase-space", "objectType": "model", "finding": "Temperature, luminosity and radiator area define the predicted far-infrared/submillimetre phase space.", "promotedToEntity": False},
        {"id": "evidence-slysh-archival-surveys", "objectType": "proposed_data_reuse", "finding": "DEBRIS, DUNES, SONS, Planck, JCMT, ALMA and NOEMA observations are proposed as search or constraint resources.", "promotedToEntity": False},
        {"id": "evidence-slysh-six-discriminants", "objectType": "candidate_assessment_framework", "finding": "Six observational tests are assembled to separate modeled engineered radiators from natural cold sources.", "promotedToEntity": False},
        {"id": "evidence-slysh-three-tier-search", "objectType": "proposed_program", "finding": "The paper outlines survey reinterpretation, archival reprocessing and targeted follow-up as a staged search program.", "promotedToEntity": False}
    ],
    "searchResources": ["DEBRIS", "DUNES", "SONS", "Planck", "James Clerk Maxwell Telescope", "ALMA", "NOEMA"],
    "editorialNotes": {
        "noDetection": "No Slysh halo or extraterrestrial technology was detected or claimed.",
        "modelDiscipline": "The 5–30 K range, approximately 10^20 W archival sensitivity and example detectability distances are scenario-dependent model outputs, not universal thresholds.",
        "naturalAlternatives": "Cold circumstellar material and background or instrumental sources must be excluded before technological interpretation.",
        "publicationDiscipline": "MNRAS submission does not establish peer review, acceptance or journal publication."
    }
})

write_json(ROOT / f"data/news/{NEWS}.json", {
    "id": NEWS, "recordType": "news_record", "contentType": "space_science_research_news",
    "title": "Could Cold Alien Computing Produce a Detectable Submillimetre Signature?",
    "source": "Universe Today", "author": "Brian Koberlein", "publicationDate": "2026-09-09", "publicationDateDisplay": "September 9, 2026",
    "originalUrl": NEWS_URL, "primarySourceUrl": ARXIV,
    "summary": "Universe Today reports on Michael Garrett's preprint proposing that hypothetical distributed computers operating in cold outer planetary systems could radiate waste heat at far-infrared or submillimetre wavelengths. The paper offers a model and search framework, not a detection.",
    "dateAdded": "2026-09-12", "newsStatus": "current", "knowledgePermanence": "permanent",
    "image": {"path": "assets/news/slysh-haloes-cold-computing-2026-09.png", "alt": "Scientific editorial visualization of a hypothetical cold computational halo surrounding a dim red dwarf star.", "caption": "Concept visualization of a hypothetical Slysh halo; this is not telescope imagery or a detected system.", "credit": "AI-generated GreyAlien editorial illustration"},
    "relatedEntityIds": [PUB, "michael-garrett", "slysh-halo", "cold-computing", "waste-heat-technosignatures", "technosignatures", "scientific-investigation", "space-exploration", "publication-2026-micron-scale-technosignatures-lunar-regolith", *[eid for eid, _, _, _ in claims]],
    "relationships": [rel("references_publication", PUB, role="surfaces primary research"), rel("references_person", "michael-garrett", role="research author"), rel("references_topic", "technosignatures"), rel("references_topic", "space-exploration")],
    "visibility": {"latestGateway": True, "publicEntityDirectory": False, "landmark": False},
    "lifecycle": {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False},
    "editorialNotes": {"sourceHierarchy": "The arXiv preprint is primary for scientific claims; Universe Today is the news surface.", "noDetection": "Neither source reports detection of a Slysh halo.", "lifecyclePrinciple": "News can age; knowledge does not."}
})

for eid, role in {
    "technosignatures": "cold waste-heat research", "scientific-investigation": "falsifiable search methodology",
    "space-exploration": "featured observational SETI research", "publication-2026-micron-scale-technosignatures-lunar-regolith": "complementary physical-artifact search methodology"
}.items():
    path = ENT / f"{eid}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not any(r.get("target") == PUB for r in data.get("relationships", [])):
        data.setdefault("relationships", []).append(rel("references_publication", PUB, role=role))
    if not any(s.get("url") == ARXIV for s in data.get("referenceSources", [])):
        data.setdefault("referenceSources", []).append({"label": "Garrett — Slysh haloes", "url": ARXIV, "sourceType": "scientific_preprint", "role": "connected_research"})
    write_json(path, data)

for path, record, generated in [
    (ROOT / "data/news/index.json", NEWS, "V23.6D.7 Slysh-halo news lifecycle ingestion"),
    (ROOT / "data/research-library/index.json", PUB, "V23.6D.7 cold-computing technosignature research ingestion")
]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"] = [record] + [x for x in data.get("records", []) if x != record]
    data["generatedBy"] = generated
    write_json(path, data)

news_path = ROOT / "categories/latest-uap-news.html"
html = news_path.read_text(encoding="utf-8")
needle = '          <article class="news-entry" id="lunar-micron-technosignatures-2026-09-08"'
block = f'''          <article class="news-entry" id="slysh-haloes-2026-09-09" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{NEWS_URL}" target="_blank" rel="noopener noreferrer">Could Cold Alien Computing Produce a Detectable Submillimetre Signature?</a></h2>
            <p class="news-meta">Universe Today / Brian Koberlein · September 9, 2026 · Space Science / Technosignature Methodology</p>
            <figure class="news-image"><img src="{IMAGE}" alt="Scientific editorial visualization of a hypothetical cold computational halo surrounding a dim red dwarf star." loading="lazy"><figcaption>Concept visualization of a hypothetical Slysh halo—not telescope imagery or a detected system. AI-generated GreyAlien editorial illustration.</figcaption></figure>
            <p>Michael Garrett proposes that hypothetical distributed computers operating at very low temperatures in the outer regions of a planetary system could emit aggregated waste heat in far-infrared or submillimetre wavelengths. Existing survey archives may be able to test parts of this modeled parameter space.</p>
            <p><strong>Evidence status:</strong> The paper reports no Slysh halo or extraterrestrial technology detection. Cold dust, debris structures, background galaxies and instrumental effects can imitate parts of the proposed signature and require systematic exclusion.</p>
            <p class="news-source-link"><a href="{NEWS_URL}" target="_blank" rel="noopener noreferrer">Read Original Coverage →</a></p>
            <div class="news-related" aria-label="Connected Research"><strong>Connected Research</strong><div class="topic-cloud">
              <a class="topic-chip" href="../entities/entity.html?id={PUB}">Permanent Research Record</a><a class="topic-chip" href="../entities/entity.html?id=slysh-halo">Slysh Halo</a><a class="topic-chip" href="../entities/entity.html?id=cold-computing">Cold Computing</a><a class="topic-chip" href="../entities/entity.html?id=waste-heat-technosignatures">Waste-Heat Technosignatures</a><a class="topic-chip" href="../entities/entity.html?id=michael-garrett">Michael Garrett</a><a class="topic-chip" href="space-exploration.html#slysh-haloes-cold-computing">Space Exploration</a>
            </div></div>
          </article>

'''
if needle not in html: raise SystemExit("D6 news anchor missing")
news_path.write_text(html.replace(needle, block + needle, 1), encoding="utf-8")

research_path = ROOT / "categories/research-library.html"
html = research_path.read_text(encoding="utf-8")
needle = '          <article class="research-entry" id="micron-scale-technosignatures-lunar-regolith"'
block = f'''          <article class="research-entry" id="slysh-haloes-cold-computing" data-knowledge-permanence="permanent">
            <p class="research-type">Research / Scientific Preprint · Permanent</p>
            <h2><a href="../entities/entity.html?id={PUB}">Slysh haloes: the waste heat of cold computing as a submillimetre technosignature</a></h2>
            <p class="research-meta">Michael Garrett · arXiv:2608.31153v1 · August 31, 2026 · Submitted to MNRAS / acceptance not established</p>
            <p>The paper models cold distributed computing as a partial Dyson swarm whose unavoidable waste heat could appear at far-infrared or submillimetre wavelengths, and proposes archival plus targeted searches for the signature.</p>
            <p><strong>Observational discipline:</strong> Six discriminants and a three-tier search program are proposed because cold dust, debris, galaxies, line sources and instrumental effects can resemble parts of the signal.</p>
            <p><strong>Evidence status:</strong> This is a theoretical and observational-methodology preprint. It reports no detected Slysh halo or extraterrestrial civilization.</p>
            <p class="research-source-link"><a href="{ARXIV}" target="_blank" rel="noopener noreferrer">Read Primary Research →</a></p>
            <div class="research-related" aria-label="Connected Research"><strong>Connected Research</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id=slysh-halo">Slysh Halo</a><a class="topic-chip" href="../entities/entity.html?id=cold-computing">Cold Computing</a><a class="topic-chip" href="../entities/entity.html?id=waste-heat-technosignatures">Waste-Heat Technosignatures</a><a class="topic-chip" href="../entities/entity.html?id=claim-slysh-natural-source-degeneracy">Natural-Source Ambiguity</a><a class="topic-chip" href="latest-uap-news.html#slysh-haloes-2026-09-09">Related News Coverage</a><a class="topic-chip" href="space-exploration.html#slysh-haloes-cold-computing">Space Exploration</a></div></div>
          </article>

'''
if needle not in html: raise SystemExit("D6 research anchor missing")
research_path.write_text(html.replace(needle, block + needle, 1), encoding="utf-8")

space_path = ROOT / "categories/space-exploration.html"
html = space_path.read_text(encoding="utf-8")
needle = '          <article class="research-entry" id="lunar-micron-scale-technosignatures"'
block = f'''          <article class="research-entry" id="slysh-haloes-cold-computing" data-knowledge-permanence="permanent">
            <p class="research-type">Featured Research / Observational SETI · Permanent</p>
            <h2><a href="../entities/entity.html?id={PUB}">Searching for Cold-Computing Waste Heat</a></h2>
            <p>A scientific preprint proposes extending Dysonian searches into colder far-infrared and submillimetre regimes. It complements the lunar material search by testing a remote electromagnetic signature rather than a local physical artifact.</p>
            <div class="research-related" aria-label="Connected Technosignature Research"><strong>Connected Research</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id=slysh-halo">Slysh Halo</a><a class="topic-chip" href="../entities/entity.html?id=waste-heat-technosignatures">Waste-Heat Technosignatures</a><a class="topic-chip" href="research-library.html#slysh-haloes-cold-computing">Research Library Record</a><a class="topic-chip" href="../entities/entity.html?id=publication-2026-micron-scale-technosignatures-lunar-regolith">Lunar Material Search</a></div></div>
          </article>

'''
if needle not in html: raise SystemExit("D6 space anchor missing")
space_path.write_text(html.replace(needle, block + needle, 1), encoding="utf-8")

shell = ROOT / "entities/entity.html"
shell.write_text(shell.read_text(encoding="utf-8").replace("v=23.6d6", "v=23.6d7"), encoding="utf-8")
print("V23.6D.7 ingestion applied")
