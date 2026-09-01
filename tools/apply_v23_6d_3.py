#!/usr/bin/env python3
"""Apply the bounded V23.6D.3 PURSUE cross-gateway research ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data" / "entities"


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


ARXIV = "https://arxiv.org/abs/2608.12445"
PAPER = "publication-2026-limits-velocity-recovery-pursue"
NEWS = "2026-08-20-debrief-pursue-video-analysis"

entities = {
    "pursue": {
        "id": "pursue", "type": "program", "entitySubtype": "Government UAP Records Initiative",
        "name": "PURSUE",
        "summary": "Presidential Unsealing and Reporting System for UAP Encounters (PURSUE), a U.S. government initiative through which five tranches of UAP records—including 112 airborne sensor videos—were released between late 2025 and mid-2026.",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical",
        "relationships": [
            {"type": "references_organization", "target": "department-of-defense", "context": "The official PURSUE records and videos were released by the U.S. government through Department of Defense channels."},
            {"type": "references_publication", "target": PAPER, "context": "The Haqq-Misra and Kopparapu preprint reviews all 112 released PURSUE sensor videos for kinematic observability."}
        ],
        "officialLinks": [{"label": "AARO — PURSUE", "url": "https://www.aaro.mil/", "linkType": "government_source"}],
        "referenceSources": [
            {"label": "AARO — Official UAP Imagery", "url": "https://www.aaro.mil/uap-cases/official-uap-imagery/", "sourceType": "government_source", "role": "dataset_source"},
            {"label": "arXiv:2608.12445", "url": ARXIV, "sourceType": "scientific_preprint", "role": "dataset_catalog_reference"}
        ],
        "editorialNotes": {"acronymHandling": "Expanded only as stated by the authoritative government and primary-paper sources."}
    },
    "jacob-haqq-misra": {
        "id": "jacob-haqq-misra", "type": "person", "entitySubtype": "Research Scientist",
        "name": "Jacob Haqq-Misra",
        "summary": "Research scientist at Blue Marble Space Institute of Science whose work includes astrobiology, planetary habitability, technosignatures and scientific analysis of UAP data; corresponding author of the 2026 PURSUE kinematics preprint.",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical",
        "relationships": [{"type": "authored", "target": PAPER, "role": "corresponding author"}],
        "officialLinks": [{"label": "NASA Astrobiology — Ask an Astrobiologist", "url": "https://astrobiology.nasa.gov/ask-an-astrobiologist/episodes/41/", "linkType": "institutional_profile"}],
        "referenceSources": [{"label": "arXiv author metadata", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"}]
    },
    "ravi-kopparapu": {
        "id": "ravi-kopparapu", "type": "person", "entitySubtype": "Planetary Scientist",
        "name": "Ravi Kopparapu",
        "summary": "Planetary scientist at NASA Goddard Space Flight Center whose research includes exoplanet habitability and technosignatures; co-author of the 2026 PURSUE kinematics preprint in an independent research capacity.",
        "destinationPage": True, "visibleInDirectory": True, "searchable": True, "taxonomyStatus": "canonical",
        "relationships": [
            {"type": "authored", "target": PAPER, "role": "co-author"},
            {"type": "affiliated_with", "target": "nasa", "context": "NASA Goddard affiliation; the paper is represented as independent scholarly work rather than an agency finding."}
        ],
        "officialLinks": [{"label": "NASA Goddard biography", "url": "https://science.gsfc.nasa.gov/sci/bio/ravikumar.kopparapu", "linkType": "institutional_profile"}],
        "referenceSources": [{"label": "arXiv author metadata", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"}]
    },
    "claim-pursue-corpus-insufficient-kinematics": {
        "id": "claim-pursue-corpus-insufficient-kinematics", "type": "claim",
        "name": "Released PURSUE videos do not provide complete information for velocity recovery",
        "summary": "Haqq-Misra and Kopparapu report that none of the 112 released PURSUE sensor videos contains the complete range, platform-motion, aspect/range-rate and sensor-scale information needed to recover physical velocity.",
        "claimStatus": "research_finding", "evidenceClass": "Analytical Interpretation",
        "relationships": [{"type": "references_publication", "target": PAPER, "role": "primary evidence"}, {"type": "concerns", "target": "pursue"}, {"type": "references_topic", "target": "image-video-analysis", "researchPacket": "S&T-001A", "confidenceGrade": "A", "confidenceScore": 99}],
        "officialLinks": [], "referenceSources": [{"label": "arXiv:2608.12445v1", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"}],
        "editorialNotes": {"caution": "This finding neither identifies the objects nor demonstrates or excludes anomalous kinematics."}
    },
    "claim-pr113-kinematic-degeneracy": {
        "id": "claim-pr113-kinematic-degeneracy", "type": "claim",
        "name": "PR113 permits radically different size, range and velocity interpretations",
        "summary": "The paper uses PR113 to show that visible angular scale alone cannot distinguish a small nearby bird-like object from a much larger, faster and more distant object when range and platform data are missing.",
        "claimStatus": "research_finding", "evidenceClass": "Analytical Interpretation",
        "relationships": [{"type": "references_publication", "target": PAPER, "role": "primary evidence"}, {"type": "concerns", "target": "pursue", "role": "case study"}, {"type": "references_topic", "target": "image-video-analysis", "researchPacket": "S&T-001A", "confidenceGrade": "A", "confidenceScore": 99}],
        "officialLinks": [], "referenceSources": [{"label": "arXiv:2608.12445v1 — PR113 analysis", "url": "https://arxiv.org/html/2608.12445v1#S4", "sourceType": "scientific_preprint", "role": "primary_reference"}],
        "editorialNotes": {"caution": "The Mach 5 example illustrates inference degeneracy; it is not a claim that PR113 depicts a Mach 5 craft."}
    },
    "claim-pr149-relative-velocity-bound": {
        "id": "claim-pr149-relative-velocity-bound", "type": "claim",
        "name": "PR149 supports an upper bound near Mach 0.4 on relative velocity",
        "summary": "Using a vessel of known size as an in-frame reference, the paper derives an upper bound of approximately Mach 0.4 for the object's relative velocity in PR149 while leaving its identity and exact velocity unresolved.",
        "claimStatus": "research_finding", "evidenceClass": "Analytical Interpretation",
        "relationships": [{"type": "references_publication", "target": PAPER, "role": "primary evidence"}, {"type": "concerns", "target": "pursue", "role": "case study"}, {"type": "references_topic", "target": "image-video-analysis", "researchPacket": "S&T-001A", "confidenceGrade": "A", "confidenceScore": 99}],
        "officialLinks": [], "referenceSources": [{"label": "arXiv:2608.12445v1 — PR149 analysis", "url": "https://arxiv.org/html/2608.12445v1#S5", "sourceType": "scientific_preprint", "role": "primary_reference"}],
        "editorialNotes": {"caution": "The bound concerns relative velocity under the authors' geometry; it does not identify the object."}
    }
}

entities[PAPER] = {
    "id": PAPER, "type": "publication", "entitySubtype": "Scientific Preprint",
    "name": "Limits on Velocity Recovery from the PURSUE Sensor Videos",
    "summary": "Scientific preprint by Jacob Haqq-Misra and Ravi Kopparapu analyzing all 112 released PURSUE airborne sensor videos. The authors find that no clip contains the complete information needed to recover physical velocity and use PR113 and PR149 to demonstrate both inference degeneracy and a bounded case.",
    "date": "2026-08-12", "dateDisplay": "August 12, 2026", "eventCategory": "UAP sensor-video methodology",
    "relationships": [
        {"type": "references_person", "target": "jacob-haqq-misra", "role": "corresponding author"},
        {"type": "references_person", "target": "ravi-kopparapu", "role": "co-author"},
        {"type": "references_organization", "target": "pursue", "role": "dataset analyzed", "context": "The paper reviews all 112 videos in the five released PURSUE tranches."},
        {"type": "references_topic", "target": "image-video-analysis", "role": "foundational related research", "context": "The paper demonstrates why apparent image motion does not uniquely determine physical velocity without range, platform motion, aspect/range-rate and sensor scale.", "researchPacket": "S&T-001A", "confidenceGrade": "A", "confidenceScore": 100},
        {"type": "references_organization", "target": "department-of-defense", "role": "dataset source"},
        {"type": "references_organization", "target": "galileo-project", "role": "multi-sensor comparison"},
        {"type": "contains_claim", "target": "claim-pursue-corpus-insufficient-kinematics"},
        {"type": "contains_claim", "target": "claim-pr113-kinematic-degeneracy"},
        {"type": "contains_claim", "target": "claim-pr149-relative-velocity-bound"}
    ],
    "officialLinks": [],
    "referenceSources": [
        {"label": "arXiv abstract and paper — version 1", "url": ARXIV, "sourceType": "scientific_preprint", "role": "primary_reference"},
        {"label": "AARO — Official UAP Imagery", "url": "https://www.aaro.mil/uap-cases/official-uap-imagery/", "sourceType": "government_source", "role": "dataset_source"}
    ],
    "publicationMetadata": {
        "authors": ["Jacob Haqq-Misra", "Ravi Kopparapu"], "repository": "arXiv", "identifier": "arXiv:2608.12445",
        "version": "v1", "submitted": "August 12, 2026", "publicationStatus": "Scientific preprint; peer review not established",
        "subjects": ["Popular Physics", "Earth and Planetary Astrophysics", "Instrumentation and Methods for Astrophysics"]
    },
    "researchLibraryMetadata": {
        "knowledgePermanence": "permanent",
        "methodology": "Reviews every released PURSUE video for measurable kinematic variables, derives the velocity-observability equations, classifies the 112 clips by tracked/transit behavior, and applies constrained analyses to PR113 and PR149.",
        "dataset": "112 infrared and electro-optical airborne sensor videos released in five PURSUE tranches between late 2025 and mid-2026.",
        "principalFindings": "No released clip provides the full set of information needed to recover physical velocity. PR113 demonstrates that widely different range-size-speed scenarios remain compatible with the pixels, while PR149 permits an upper relative-velocity bound near Mach 0.4 by using a vessel of known size as a reference.",
        "limitations": "The analysis is limited to public, redacted video products. Missing platform velocity, sensor field-angle/pointing metadata, range or range-rate histories and corroborating tracks prevent stronger kinematic conclusions.",
        "researchImplication": "Unredacted telemetry, flight logs, sensor metadata, range records or correlated radar observations are needed to test claims of anomalous motion; apparent image motion alone is not physical velocity."
    },
    "evidenceRecords": [
        {"id": "evidence-pr113", "label": "DOW-UAP-PR113", "objectType": "case_study", "finding": "Visible angular graticule constrains camera scale, but absent range and platform data leave size and velocity degenerate.", "promotedToEntity": False},
        {"id": "evidence-pr149", "label": "DOW-UAP-PR149", "objectType": "case_study", "finding": "A vessel of known size supplies an in-frame reference and supports an upper bound near Mach 0.4 on relative velocity.", "promotedToEntity": False}
    ],
    "editorialNotes": {
        "neutrality": "The paper neither identifies the depicted objects nor demonstrates or excludes anomalous kinematics.",
        "titleVerification": "The authoritative arXiv v1 title is used; the release's working scope title is not substituted for the publication title.",
        "nasaHandling": "Ravi Kopparapu's NASA Goddard affiliation is recorded, but the preprint is not represented as a NASA agency finding."
    }
}

for eid, payload in entities.items():
    write_json(ENT / f"{eid}.json", payload)

# Upgrade the existing Debrief record into the reusable lifecycle/cross-gateway model.
news_path = ROOT / "data" / "news" / f"{NEWS}.json"
news = json.loads(news_path.read_text(encoding="utf-8"))
news.update({"contentType": "scientific_research_news", "publicationDateDisplay": "August 20, 2026", "primarySourceUrl": ARXIV,
             "newsStatus": "current", "knowledgePermanence": "permanent"})
news["relatedEntityIds"] = [PAPER, "pursue", "jacob-haqq-misra", "ravi-kopparapu", "image-video-analysis", "department-of-defense", "galileo-project",
                            "claim-pursue-corpus-insufficient-kinematics", "claim-pr113-kinematic-degeneracy", "claim-pr149-relative-velocity-bound"]
news["relationships"] = [
    {"type": "surfaces_publication", "target": PAPER, "context": "The Debrief article is the timely news surface; the arXiv preprint is the permanent research object."},
    {"type": "references_program", "target": "pursue"},
    {"type": "references_person", "target": "jacob-haqq-misra"},
    {"type": "references_person", "target": "ravi-kopparapu"},
    {"type": "related_topic", "target": "image-video-analysis"},
    {"type": "references_organization", "target": "department-of-defense"},
    {"type": "references_research_project", "target": "galileo-project"}
]
news["visibility"].update({"latestGateway": True, "landmark": False})
news["lifecycle"] = {"status": "current", "archiveEligible": True, "automaticAgingEnabled": False, "landmark": False}
news["editorialNotes"]["lifecyclePrinciple"] = "News can age; knowledge does not. Archiving this coverage must not remove the permanent paper, claims, evidence or graph relationships."
news["editorialNotes"]["sourceHierarchy"] = "The arXiv preprint is primary for scientific claims; The Debrief is the secondary news source."
write_json(news_path, news)

# Make Image & Video Analysis reciprocally surface the permanent paper.
iva_path = ENT / "image-video-analysis.json"
iva = json.loads(iva_path.read_text(encoding="utf-8"))
iva["relationships"] = [r for r in iva.setdefault("relationships", []) if r.get("target") != PAPER]
iva["relationships"].append({"type": "references_publication", "target": PAPER, "role": "foundational kinematic observability study",
    "context": "The PURSUE paper operationalizes the topic's key principle that apparent image motion is not automatically physical velocity."})
iva.setdefault("scienceResearch", {})["relatedResearch"] = [
    {"id": PAPER, "title": "Limits on Velocity Recovery from the PURSUE Sensor Videos", "publicationStatus": "arXiv preprint",
     "relevance": "Dataset-wide demonstration of the metadata and geometry required for physical velocity inference from airborne sensor video."}
] + iva.get("scienceResearch", {}).get("relatedResearch", [])
iva["referenceSources"] = [s for s in iva.get("referenceSources", []) if s.get("url") != ARXIV]
iva["referenceSources"].append({"label": "Haqq-Misra & Kopparapu — PURSUE velocity recovery preprint", "url": ARXIV,
    "sourceType": "scientific_preprint", "role": "related_research"})
write_json(iva_path, iva)

# Research and news indexes.
ri_path = ROOT / "data" / "research-library" / "index.json"
ri = json.loads(ri_path.read_text(encoding="utf-8")); ri["generatedBy"] = "V23.6D.3 PURSUE permanent research ingestion"
ri["records"] = [PAPER] + [x for x in ri["records"] if x != PAPER]; write_json(ri_path, ri)
ni_path = ROOT / "data" / "news" / "index.json"
ni = json.loads(ni_path.read_text(encoding="utf-8")); ni["generatedBy"] = "V23.6D.3 PURSUE cross-gateway lifecycle integration"; write_json(ni_path, ni)

# Bounded gateway HTML modifications: enrich the existing news card and add permanent research first.
news_html_path = ROOT / "categories" / "latest-uap-news.html"
html = news_html_path.read_text(encoding="utf-8")
html = html.replace('<article class="news-entry">\n            <h2><a href="https://thedebrief.org/scientists-just-analyzed-more-than-100-uap-videos-released-by-the-pentagons-pursue-program-this-is-what-they-learned/"',
                    '<article class="news-entry" id="pursue-kinematic-inference-2026-08-20" data-news-status="current" data-knowledge-permanence="permanent">\n            <h2><a href="https://thedebrief.org/scientists-just-analyzed-more-than-100-uap-videos-released-by-the-pentagons-pursue-program-this-is-what-they-learned/"')
old_chips = '''<a class="topic-chip" href="../entities/entity.html?id=department-of-defense">U.S. Department of Defense</a>\n                <a class="topic-chip" href="../entities/entity.html?id=scientific-investigation">Scientific Investigation</a>\n                <a class="topic-chip" href="../entities/entity.html?id=uap-science-advisory-council">UAP Science Advisory Council</a>\n                <a class="topic-chip" href="../entities/entity.html?id=galileo-project">The Galileo Project</a>'''
new_chips = '''<a class="topic-chip" href="../entities/entity.html?id=publication-2026-limits-velocity-recovery-pursue">Permanent Research Record</a>\n                <a class="topic-chip" href="../entities/entity.html?id=pursue">PURSUE</a>\n                <a class="topic-chip" href="../entities/entity.html?id=jacob-haqq-misra">Jacob Haqq-Misra</a>\n                <a class="topic-chip" href="../entities/entity.html?id=ravi-kopparapu">Ravi Kopparapu</a>\n                <a class="topic-chip" href="../entities/entity.html?id=image-video-analysis">Image &amp; Video Analysis</a>\n                <a class="topic-chip" href="../entities/entity.html?id=department-of-defense">U.S. Department of Defense</a>'''
if old_chips in html:
    html = html.replace(old_chips, new_chips)
elif "Permanent Research Record" not in html or "pursue-kinematic-inference-2026-08-20" not in html:
    raise SystemExit("Expected PURSUE news-chip block not found")
news_html_path.write_text(html, encoding="utf-8")

research_path = ROOT / "categories" / "research-library.html"
research_html = research_path.read_text(encoding="utf-8")
marker = '          <article class="research-entry" id="critical-evaluation-poss1e-technosignatures">'
block = '''          <article class="research-entry" id="limits-velocity-recovery-pursue" data-knowledge-permanence="permanent">\n            <p class="research-type">Research / Scientific Preprint · Permanent</p>\n            <h2><a href="../entities/entity.html?id=publication-2026-limits-velocity-recovery-pursue">Limits on Velocity Recovery from the PURSUE Sensor Videos</a></h2>\n            <p class="research-meta">Jacob Haqq-Misra &amp; Ravi Kopparapu · arXiv:2608.12445v1 · Submitted August 12, 2026 · Preprint / peer review not established</p>\n            <p>The authors reviewed all 112 released PURSUE airborne sensor videos and found that none provides the complete range, aircraft-motion, viewing-geometry and sensor-scale information needed to recover physical velocity. The result is a limit on what the public data can establish—not an identification of the objects and not evidence for or against anomalous craft.</p>\n            <p><strong>PR113:</strong> A visible angular graticule constrains camera scale, but missing range and platform data allow radically different size and velocity scenarios. The paper's Mach 5 example illustrates this degeneracy; it is not a claim that the video shows a Mach 5 object.</p>\n            <p><strong>PR149:</strong> A vessel of known size provides an in-frame reference, supporting an upper bound near Mach 0.4 on relative velocity while leaving the object's exact speed and identity unresolved.</p>\n            <p><strong>Research implication:</strong> Unredacted telemetry, flight logs, camera metadata, range histories or correlated radar tracks are needed before claims of anomalous physical speed can be evaluated reliably.</p>\n            <p class="research-source-link"><a href="https://arxiv.org/abs/2608.12445" target="_blank" rel="noopener noreferrer">Read Primary Research →</a></p>\n            <div class="research-related" aria-label="Connected Research"><strong>Connected Research</strong><div class="topic-cloud">\n              <a class="topic-chip" href="../entities/entity.html?id=pursue">PURSUE</a>\n              <a class="topic-chip" href="../entities/entity.html?id=image-video-analysis">Image &amp; Video Analysis</a>\n              <a class="topic-chip" href="../entities/entity.html?id=claim-pursue-corpus-insufficient-kinematics">Dataset-Level Finding</a>\n              <a class="topic-chip" href="../entities/entity.html?id=claim-pr113-kinematic-degeneracy">PR113 Constraint</a>\n              <a class="topic-chip" href="../entities/entity.html?id=claim-pr149-relative-velocity-bound">PR149 Constraint</a>\n              <a class="topic-chip" href="latest-uap-news.html#pursue-kinematic-inference-2026-08-20">Related News Coverage</a>\n            </div></div>\n          </article>\n\n'''
if 'id="limits-velocity-recovery-pursue"' not in research_html:
    if marker not in research_html: raise SystemExit("Research insertion marker not found")
    research_html = research_html.replace(marker, block + marker)
research_path.write_text(research_html, encoding="utf-8")

# Advance only the entity-shell cache key; preserve the reliability runtime itself.
shell = ROOT / "entities" / "entity.html"
shell.write_text(shell.read_text(encoding="utf-8").replace("entity-engine.js?v=23.6d2", "entity-engine.js?v=23.6d3"), encoding="utf-8")

print("V23.6D.3 ingestion applied")
