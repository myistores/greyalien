# GreyAlien Science Research Packet — S&T-001A

## Image & Video Analysis
**Gateway collection:** Scientific Methods  
**Repository baseline:** V23.6D.1  
**Research cycle status:** COMPLETE — HUMAN REVIEW REQUIRED BEFORE INGESTION  
**Entity decision:** CREATE  
**Science Seed Score:** 30/30 — Tier 1

## 1. Research definition

Image & Video Analysis is the disciplined examination of still imagery and motion imagery to determine what information the recording can reliably support. For GreyAlien, the subject should cover provenance, authentication, metadata, frame timing, resolution, field of view, focal length, camera/sensor geometry, perspective, parallax, motion estimation, image enhancement, compression, stabilization, artifacts, and uncertainty.

The entity should explicitly distinguish what an image depicts from what can be inferred about an object's size, range, speed, acceleration, shape, temperature, or origin.

## 2. Why this subject matters to GreyAlien

V23.6D.1 contains 1,611 production entities and 3,590 declared relationships (3,534 resolved plus 56 unresolved in the graph manifest). The repository includes numerous UAP cases, claims, congressional records, and podcast episodes centered on recorded imagery. Image & Video Analysis therefore functions as a methodological bridge connecting existing evidence-oriented content to the Science & Technology Gateway.

The repository preflight found no existing topic that adequately represents image/video analysis. The closest broad topics are `scientific-evidence`, `scientific-investigation`, and `military-sensor-data`; none is a substitute for a dedicated image-analysis method entity.

## 3. Established scientific/technical foundation

### 3.1 Provenance and authentication
Image/video analysis should begin by establishing the source, history, and integrity of the media. Authentication can evaluate whether imagery is consistent with its claimed origin or whether it has been altered, but authentication alone does not establish the identity or nature of an object shown.

### 3.2 Native media and metadata
Original/native files are preferred. Converting, transcoding, exporting, or screen-capturing video can alter visual properties and strip metadata. Relevant metadata can include frame timing, resolution, sensor/camera information, time of acquisition, location, observing mode, and other contextual fields.

### 3.3 Frame timing and motion analysis
Speed or direction estimates require reliable frame timing and suitable geometric information. A visual impression of rapid motion is not equivalent to a measured physical speed.

### 3.4 Camera and sensor geometry
Focal length, field of view, camera position/orientation, range, lens distortion, and image dimensions affect quantitative interpretation. Photogrammetric measurement requires calibrated or otherwise known camera geometry and sufficient reference information.

### 3.5 Perspective and parallax
Motion of the observer and unknown target range can create large apparent motion against a distant background. Forced perspective can also cause large errors in perceived size and distance.

### 3.6 Image enhancement and processing
Stabilization, sharpening, contrast adjustment, frame averaging, interpolation, noise reduction, zooming, and other processing can aid inspection, but processing should be documented and reproducible. Enhancement can also introduce artifacts or remove detail.

### 3.7 Compression and derived copies
Lossy compression and repeated conversion can obscure or create visual features. Analysis should preserve the original bitstream when possible and record any differences between source and processed copies.

### 3.8 UAP-specific data quality
NASA's UAP Independent Study emphasized calibration, multiple measurements, and sensor metadata. It noted that limited high-quality observations currently prevent firm scientific conclusions about UAP nature and that some apparent anomalies can be sensor artifacts when calibration and metadata are examined.

AARO's GoFast methodology provides a concrete UAP example: the public video lacked a complete data set needed to uniquely solve range, speed, and heading, so AARO reconstructed possible geometries and explicitly modeled uncertainty and parallax.

## 4. Evidence-separation rules for this entity

- **ESTABLISHED_SCIENCE:** imaging principles, perspective, parallax, compression, calibration, metadata, photogrammetry.
- **DOCUMENTED_FACT:** who recorded a video, which agency released it, dates, platform or sensor modality when confirmed by an authoritative source.
- **REPORTED_OBSERVATION:** what an observer reported seeing.
- **WITNESS_CLAIM:** claims about extraordinary behavior or classified evidence.
- **ANALYTICAL_INTERPRETATION:** a technical conclusion derived from imagery or other data.
- **HYPOTHESIS:** a proposed explanation awaiting adequate testing.
- **SPECULATION:** conclusions not supported by sufficient evidence.
- **DISPUTED:** competing analyses reach materially different conclusions.
- **UNKNOWN:** insufficient information.

The research packet must never convert one category into another silently.

## 5. Authoritative source ledger

| ID | Grade | Source | Role in packet |
|---|---|---|---|
| S01 | Tier S | NIST — Digital and Multimedia Evidence | Establishes digital images/video as evidence requiring measurement methods and standards. |
| S02 | Tier S | NIST/OSAC — Standard Guide for Forensic Digital Video Examination Workflow | Supports structured examination workflow. |
| S03 | Tier S | SWGDE — Best Practices for Digital Forensic Video Analysis | Metadata, native media, frame timing, clarification, stabilization, compression, reproducibility and limitations. |
| S04 | Tier S | SWGDE — Best Practices for Image Authentication | Authentication methodology and limitations; authentication is not object identification. |
| S05 | Tier S | NISTIR 8325 — Media Forensics Challenge Image Provenance | Supports provenance analysis and importance of manipulation history/metadata. |
| S06 | Tier S | USGS Technical Methods — Structure-from-motion aided photogrammetry | Camera calibration, focal length, geometry, distortion and measurement foundations. |
| S07 | Tier S | NGA Motion Imagery Standards Board | Motion imagery integrity, metadata, interoperability and technical standards. |
| A01 | Tier A | NASA UAP Independent Study Team Final Report | Calibration, metadata, multisensor collection, evidence thresholds and UAP data-quality limitations. |
| A02 | Tier A | AARO — Effect of Forced Perspective and Parallax View on UAP Observations | UAP-specific explanation of perspective/parallax effects. |
| A03 | Tier A | AARO — GoFast Case Resolution Methodology | Demonstrates geometry, uncertainty, missing metadata and parallax in quantitative UAP video analysis. |
| A04 | Tier A | DoD — Release of Historical Navy Videos | Official provenance for the 2004 and 2015 Navy videos. |
| A05 | Tier A | AARO — AARO and the Declassification Process | Explains why released imagery may omit resolution/metadata and other sensor-capability information. |
| A06 | Tier A | AARO — DOW-UAP-PR051 "Syrian UAP instant acceleration" | Official 2026 provenance/handling description; states the received video had been digitally altered before upload and describes the apparent rapid exit in relation to sensor tracking. |

### Source URLs
- S01: https://www.nist.gov/forensic-science/digital-and-multimedia-evidence
- S02: https://www.nist.gov/standard/951
- S03: https://www.swgde.org/documents/published-complete-listing/18-v-001-2-0/
- S04: https://www.swgde.org/documents/published-complete-listing/18-i-001-best-practices-for-image-authentication/
- S05: https://www.nist.gov/publications/media-forensics-challenge-image-provenance-evaluation-and-state-art-analysis-large
- S06: https://pubs.usgs.gov/publication/tm11C11/full
- S07: https://gwg.nga.mil/gwg/focus-groups/Motion_Imagery_Standards_Board_%28MISB%29.html
- A01: https://smd-cms.nasa.gov/wp-content/uploads/2023/09/uap-independent-study-team-final-report.pdf
- A02: https://www.aaro.mil/Portals/136/PDFs/Information%20Papers/AARO_Effect_of_Forced_Perspective_and_Parallax_View_on_UAP_Observations_2024.pdf
- A03: https://www.aaro.mil/Portals/136/PDFs/case_resolution_reports/AARO_GoFast_Case_Resolution_Card_Methodology_Final.pdf
- A04: https://www.defense.gov/News/Releases/release/article/2165713/statement-by-the-department-of-defense-on-the-release-of-historical-navy-videos/
- A05: https://www.aaro.mil/Portals/136/PDFs/Information%20Papers/AARO_Declassification_Info_Paper_2025.pdf
- A06: https://www.aaro.mil/Next-AARO-Home-redesign/Next-Parent/Presidential-UAP-Transparency-Initiative/videoid/1007707/dvpcc/false/

## 6. Repository relationship matrix

Scoring formula: Source Authority 30 + Directness 25 + Repository Corroboration 15 + Semantic Precision 15 + Independent Corroboration 10 + Context Consistency 5 = 100.

| Existing entity | Type | Proposed relationship | Score | Grade | Decision | Rationale |
|---|---|---|---:|---|---|---|
| 2004 Nimitz Encounter | case | associated_topic → Image & Video Analysis | 96 | A | APPROVE | Recorded Navy imagery is an established component of the event; DoD officially released the 2004 Navy video. |
| 2016 Mosul Orb Incident | case | associated_topic → Image & Video Analysis | 94 | A | APPROVE | Repository defines the case by surveillance recording; analysis/provenance is central to research value. |
| 2017 Iraq Jellyfish UAP Incident | case | associated_topic → Image & Video Analysis | 97 | A | APPROVE | Repository explicitly identifies thermal-imaging footage and an episode evaluating that video. |
| Large Disc UAP Video | case | associated_topic → Image & Video Analysis | 93 | A | APPROVE | Entity is explicitly a military sensor video. |
| 2025 Yemen Hellfire UAP Video | case | associated_topic → Image & Video Analysis | 92 | A | APPROVE | Entity is explicitly military imagery shown during congressional proceedings. |
| Syria UAP 2021 | case | associated_topic → Image & Video Analysis | 99 | A | APPROVE | Repository/podcast content plus AARO PR051 make provenance, alteration, tracking and interpretation central to the case. |
| March 31, 2026 Congressional Request for UAP Video Records | document | references_topic → Image & Video Analysis | 88 | B | APPROVE | The document's subject matter is a defined corpus of military UAP video records; methodological relevance is strong but indirect. |
| WEAPONIZED #108 — Syria UAP Video | podcast_episode | discussed_topic → Image & Video Analysis | 99 | A | APPROVE | Episode explicitly analyzes footage frame behavior and competing interpretations. |
| WEAPONIZED #81 — Full Mosul Orb Video | podcast_episode | discussed_topic → Image & Video Analysis | 97 | A | APPROVE | Episode centers on release/provenance of video evidence. |
| WEAPONIZED #47 — Jellyfish UAP Investigation | podcast_episode | discussed_topic → Image & Video Analysis | 98 | A | APPROVE | Episode explicitly evaluates thermal video and proposed explanations. |
| WEAPONIZED #79 — Large Disc UAP Video | podcast_episode | discussed_topic → Image & Video Analysis | 96 | A | APPROVE | Episode explicitly presents/discusses military sensor video. |
| WEAPONIZED #89 — 2025 UAP Hearing | podcast_episode | discussed_topic → Image & Video Analysis | 92 | A | APPROVE | Episode discusses military video presented at hearing. |
| WEAPONIZED #8 — Baghdad Phantom Analysis | podcast_episode | discussed_topic → Image & Video Analysis | 91 | A | APPROVE | Episode explicitly concerns analysis of imagery and competing interpretations. |
| WEAPONIZED #72 — USS Jackson Tic Tac Video | podcast_episode | discussed_topic → Image & Video Analysis | 88 | B | APPROVE | Video is central to episode, but scientific analysis is less explicit than Tier-A relationships above. |
| Claim: Context is required to interpret released UAP videos | claim | concerns → Image & Video Analysis | 98 | A | APPROVE | Direct methodological claim about interpretation of video evidence. |
| Claim: Released footage warrants frame-by-frame technical review | claim | concerns → Image & Video Analysis | 99 | A | APPROVE | Directly concerns the proposed scientific method. |
| Claim: Independent experts require direct and transparent access | claim | concerns → Image & Video Analysis | 91 | A | APPROVE | Repository summary explicitly cites provenance, imaging and reproducible analysis. |
| Chad Underwood | person | [no suitable production relationship] | 97 | A evidence | HOLD | Strong conceptual connection, but current vocabulary lacks a precise Person ↔ scientific-method relationship. |
| 2014–2015 East Coast Navy Encounters | case | associated_topic → Image & Video Analysis | 84 | B | HOLD | The broader encounter series is linked historically to 2015 Navy videos, but repository entity does not itself clearly define the imagery relationship. Add after case-specific source mapping. |
| Claim: Object appears to accelerate abruptly after sensor lock | claim | concerns → Image & Video Analysis | 95 | A | APPROVE WITH CONTEXT | It is a source-attributed analytical claim; AARO PR051 now provides authoritative contrary/contextual information about alteration and tracking behavior. |

## 7. Human-review flags

### HR-01 — Person-to-science relationship vocabulary gap
The current vocabulary does not provide a semantically precise relationship for a person whose work, testimony, or instrument operation directly relates to a scientific method. Do not misuse `associated_topic`, whose reverse label is "Associated case."

### HR-02 — Syria UAP entity is under-enriched
`syria-uap-2021` is currently a placeholder-style case with no sources. AARO PR051 now provides an authoritative primary source and materially important provenance/processing information.

Recommended new summary:
"2021 U.S. military infrared-sensor footage from the U.S. Central Command area of responsibility later uploaded to a classified network and publicly released by AARO in 2026. AARO states that the media had been digitally altered before upload and describes the apparent rapid exit from frame as occurring when the sensor stopped tracking the area of contrast."

The summary should remain neutral and avoid treating AARO's description as proof of the object's identity.

### HR-03 — Existing acceleration claim needs contextual counter-evidence
The claim `claim-the-object-appears-to-accelerate-abruptly-after-sensor-lock` is correctly stored as a claim. It should not be deleted merely because AARO later supplied a different analysis. GreyAlien should preserve the claim while adding authoritative contextual sourcing and, if a suitable AARO document entity is later created, a `contradicted_by` or equivalent evidence relationship.

### HR-04 — Do not infer sensor modality
A military video, sensor video, or ISR recording is not automatically FLIR/infrared. S&T-001A may link imagery regardless of modality; S&T-001C must verify modality separately.

### HR-05 — Avoid link saturation
The repository scan produced hundreds of textual image/video candidates. The initial production entity should begin with a small, high-value set of relationships, not every entity containing visual-media vocabulary.

## 8. Missing entity candidates discovered

1. **AARO DOW-UAP-PR051 — Syrian UAP Instant Acceleration** (document) — HIGH research value; recommended for future Research Library ingestion or same-release creation only if cross-gateway scope is explicitly approved.
2. **GoFast Case Resolution / Methodology** (document/publication) — HIGH research value for future Image & Video Analysis and Parallax pages.
3. **Image Provenance & Authentication** (possible child scientific method) — MEDIUM; defer until parent entity is established.
4. **Photogrammetry** (possible child scientific method) — HIGH future value.
5. **Parallax & Apparent Motion** — HIGH; already selected for later Science seed work.
6. **Video Compression & Processing Artifacts** — HIGH future child topic.

## 9. Production entity recommendation

### CREATE
**ID:** `image-video-analysis`  
**Name:** Image & Video Analysis  
**Type:** `topic`  
**Science Gateway collection:** Scientific Methods  
**Taxonomy status:** canonical

### Proposed concise entity summary
"Scientific methods for evaluating recorded imagery, including provenance, metadata, camera geometry, frame timing, perspective, parallax, motion analysis, enhancement, compression artifacts and uncertainty."

### Proposed researcher-facing profile copy
"Image and video recordings can provide valuable evidence, but what they show depends on the recording system, geometry, metadata, processing history and available context. GreyAlien uses this topic to connect UAP imagery with established methods for evaluating provenance, frame timing, sensor and camera geometry, apparent motion, image processing, compression and analytical uncertainty. A visual impression alone does not establish an object's distance, size, speed, acceleration or origin."

## 10. Ingestion recommendation

**Status:** APPROVE WITH CHANGES

Recommended first release:
- Create `image-video-analysis`.
- Add the 18 approved high-confidence relationships listed in the ingestion manifest.
- Enrich `syria-uap-2021` with AARO PR051 as an authoritative reference and replace its placeholder summary with neutral factual language.
- Preserve source-attributed acceleration claims as claims; do not rewrite them as facts.
- Hold person-to-science links until relationship vocabulary is deliberately expanded.
- Hold the broad East Coast Navy case link until the case-to-video mapping is verified at the same standard used here.
- Do not yet create the child topics; record them in the Science backlog.

## 11. Final research-cycle conclusion

S&T-001A passes the Science Research Agent threshold at 30/30. It has substantial existing GreyAlien graph value and a strong external scientific foundation. The most important new finding from the fresh research cycle is the 2026 AARO treatment of the Syria video: GreyAlien currently preserves source-attributed claims of apparent instantaneous acceleration, while AARO's primary record states that the received media had been digitally altered before upload and describes the apparent rapid frame exit as coinciding with loss of sensor tracking. GreyAlien should preserve both the historical claim and the later authoritative analysis, clearly separated by evidence class.

This is the intended behavior of the Science Research Agent: connect claims to scientific methods and primary evidence without silently adjudicating contested conclusions.
