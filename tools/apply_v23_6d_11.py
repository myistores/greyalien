#!/usr/bin/env python3
"""Apply V23.6D.11 AARO classified-responsive-records ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
DOC = "document-2026-aaro-classified-responsive-uap-uso-records"
NEWS = "2026-10-05-black-vault-aaro-classified-responsive-records"
ARTICLE = "https://www.theblackvault.com/documentarchive/aaro-says-it-found-records-on-uap-uso-cases-requested-by-congress-withholds-them-in-their-entirety-as-classified/"
HOUSE = "https://oversight.house.gov/wp-content/uploads/2026/03/UAP-Request-Letter-FINAL.pdf"
AARO = "https://www.aaro.mil/Next-AARO-Home-redesign/Next-Parent/Next-UAP-Report-Documents/poster/"

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
def rel(kind, target, **extra): return {"type": kind, "target": target, **extra}
def entity(obj):
    obj.setdefault("relationships", []); obj.setdefault("officialLinks", []); obj.setdefault("referenceSources", [])
    write(ENT / f"{obj['id']}.json", obj)
def enrich(eid, kind, role):
    p = ENT / f"{eid}.json"; d = json.loads(p.read_text(encoding="utf-8"))
    if not any(r.get("target") == DOC for r in d.get("relationships", [])):
        d.setdefault("relationships", []).append(rel(kind, DOC, role=role))
    if not any(s.get("url") == ARTICLE for s in d.get("referenceSources", [])):
        d.setdefault("referenceSources", []).append({"label":"The Black Vault — AARO classified responsive-records report","url":ARTICLE,"sourceType":"investigative_reporting_with_agency_correspondence","role":"connected_record_source"})
    write(p, d)

entity({"id":"john-greenewald-jr","type":"person","name":"John Greenewald Jr.","summary":"Freedom of Information Act researcher and founder of The Black Vault who requested contextual AARO records associated with five congressionally identified UAP/USO incident labels.","profileStatus":"FOIA researcher and archival publisher","profileSummary":"FOIA researcher and founder of The Black Vault.","destinationPage":True,"visibleInDirectory":True,"searchable":True,"taxonomyStatus":"canonical","relationships":[rel("references_publication",DOC,role="FOIA requester")],"officialLinks":[{"label":"The Black Vault","url":"https://www.theblackvault.com/","linkType":"official_website"}],"referenceSources":[{"label":"The Black Vault report","url":ARTICLE,"sourceType":"first_party_requester_reporting","role":"primary_reporting"}]})
entity({"id":"the-black-vault","type":"organization","name":"The Black Vault","summary":"Independent government-document archive founded by John Greenewald Jr., publishing records obtained through the Freedom of Information Act and other public-records processes.","organizationPurpose":"Government-records research, archiving and publication.","destinationPage":True,"visibleInDirectory":True,"searchable":True,"taxonomyStatus":"canonical","relationships":[rel("documented_by",DOC,role="FOIA determination and records-access context"),rel("affiliated_with","john-greenewald-jr",role="founder")],"officialLinks":[{"label":"Official website","url":"https://www.theblackvault.com/","linkType":"official_website"}],"referenceSources":[{"label":"The Black Vault report","url":ARTICLE,"sourceType":"publisher_page","role":"primary_reporting"}]})

incidents = [
    ("incident-wiley-2x-zinc-uap-uso-formation","Wiley 2X Zinc UAP/USO Formation","Source-attributed incident label appearing in the March 2026 congressional request and Greenewald's five-case FOIA reporting; the label is not an independently authenticated description."),
    ("incident-cactus-1x-uap-uso-submarine-2022-03-25","Cactus 1X UAP/USO Near Submarine — March 25, 2022","Source-attributed label describing multiple spherical UAP/USO near a submarine and reportedly entering and exiting water; the description is not independently authenticated by the withheld records."),
    ("incident-jacker-2x-spherical-uap-over-water","Jacker 2X Spherical UAP Over Water","Source-attributed incident label describing a spherical UAP pulsing over water; the description is not independently authenticated by the withheld records."),
    ("incident-uscg-c144-tic-tac-ir-2024-04-24","USCG C-144 ‘Tic Tac’ IR Record — April 24, 2024","Source-attributed label for an infrared record associated with a U.S. Coast Guard C-144; the nickname and description do not establish object identity or extraordinary performance."),
    ("incident-ufos-formation-persian-gulf-pr098","‘UFOs in Formation over Persian Gulf?’ — PR098","Uploader-defined title for PURSUE record PR098. AARO describes likely infrared imagery from a U.S. military platform in the CENTCOM area and notes an unsubstantiated chain of custody; the title is not an AARO validation of a physical formation.")
]
for eid, name, summary in incidents:
    entity({"id":eid,"type":"case","entitySubtype":"Source-Attributed UAP/USO Incident Label","name":name,"summary":summary,"destinationPage":True,"visibleInDirectory":True,"searchable":True,"taxonomyStatus":"canonical","relationships":[rel("documented_by",DOC,role="one of five FOIA subjects"),rel("references_organization","house-oversight-committee",role="March 31, 2026 video-record request")],"referenceSources":[{"label":"House Oversight — March 31, 2026 UAP records request","url":HOUSE,"sourceType":"primary_government_document","role":"incident_label_source"},{"label":"The Black Vault — five-case FOIA report","url":ARTICLE,"sourceType":"requester_reporting","role":"withholding_context"}],"evidenceMetadata":{"authenticationStatus":"Source label only; underlying withheld records do not publicly authenticate the reported incident description.","knowledgePermanence":"permanent"}})

claims = [
    ("claim-congress-identified-five-uap-uso-cases","Congress identified the five UAP/USO case labels in a records request","The March 31, 2026 House request included the five labels later used in Greenewald's targeted FOIA effort.","primary_document_fact"),
    ("claim-greenewald-filed-five-case-aaro-foia","Greenewald sought AARO context records for five named cases","John Greenewald Jr. reports filing a targeted FOIA request for records beyond the already public imagery associated with five named cases.","requester_reported_procedural_fact"),
    ("claim-aaro-located-responsive-records-five-cases","AARO reported locating responsive records for the five-case request","AARO's determination in FOIA case 26-F-1892 states that responsive material was located for the request covering five named UAP/USO cases.","agency_determination_fact"),
    ("claim-aaro-withheld-five-case-records-in-full","AARO withheld the responsive records in their entirety","The reported determination withholds the located responsive records in full under the classified national-security provisions of FOIA Exemption (b)(1) and Executive Order 13526.","agency_withholding_determination"),
    ("claim-responsive-records-do-not-authenticate-incidents","Responsive records do not authenticate the incident descriptions","The existence of records responsive to a search does not independently verify that the uploader-defined labels, reported motions, object shapes or air-water behavior are accurate.","evidentiary_limitation"),
    ("claim-classification-does-not-establish-record-contents","Classification does not establish what the withheld records contain","A classification-based withholding identifies an access restriction; it does not establish extraterrestrial origin, extraordinary performance, transmedium travel or any other specific content.","evidentiary_limitation")
]
for eid, name, summary, classification in claims:
    entity({"id":eid,"type":"claim","name":name,"summary":summary,"relationships":[rel("contained_in",DOC,role="claim subject")],"referenceSources":[{"label":"The Black Vault — AARO FOIA determination report","url":ARTICLE,"sourceType":"investigative_reporting_with_agency_correspondence","role":"claim_source"}],"claimMetadata":{"classification":classification,"knowledgePermanence":"permanent","evidenceBoundary":"Record existence, classification and incident authenticity are separate propositions."}})

entity({
    "id":DOC,"type":"publication","entitySubtype":"Government FOIA Determination / Classified Records Withholding","name":"AARO FOIA Determination on Five UAP/USO Case Records",
    "summary":"AARO reported locating records responsive to John Greenewald Jr.'s request concerning five congressionally identified UAP/USO incident labels, then withheld the responsive material in full under classification-related FOIA authority. The determination establishes a records-access outcome, not the authenticity or nature of the underlying incidents.",
    "title":"AARO FOIA Determination on Five UAP/USO Case Records","publicationDate":"2026-10","publicationStatus":"Government FOIA determination reported and reproduced by requester","publisher":"All-domain Anomaly Resolution Office / Department of War","authors":["All-domain Anomaly Resolution Office"],"destinationPage":True,"visibleInDirectory":True,"searchable":True,"taxonomyStatus":"canonical",
    "relationships":[rel("published_by","aaro"),rel("involved_person","john-greenewald-jr",role="FOIA requester"),rel("documented_by","the-black-vault"),rel("references_person","anna-paulina-luna",role="March 2026 congressional request context"),rel("references_organization","house-oversight-committee",role="congressional records request"),rel("references_topic","congressional-oversight"),rel("references_topic","government-transparency"),rel("references_topic","uap-disclosure"),rel("references_topic","unidentified-submerged-objects"),rel("references_organization","pursue",role="withheld contextual records versus public release pathway"),*[rel("references_case",eid) for eid,_,_ in incidents],*[rel("contains_claim",eid) for eid,*_ in claims]],
    "officialLinks":[],
    "referenceSources":[{"label":"The Black Vault — AARO says it found records and withheld them","url":ARTICLE,"sourceType":"investigative_reporting_with_agency_correspondence","role":"primary_publication_source"},{"label":"House Oversight — UAP request letter","url":HOUSE,"sourceType":"primary_government_document","role":"congressional_request_context"},{"label":"AARO UAP report-document catalog","url":AARO,"sourceType":"primary_government_catalog","role":"public_imagery_context"}],
    "foiaMetadata":{"caseNumber":"26-F-1892","requester":"John Greenewald Jr.","responsiveRecordsStatus":"Located","disposition":"Withheld in full","citedAuthority":["5 U.S.C. § 552(b)(1)","Executive Order 13526"],"segregability":"The public reporting states the responsive material was withheld in its entirety; the complete package was not independently available for a line-by-line segregability audit.","appealRights":"Use the agency determination itself for the controlling appeal instructions and deadline; no deadline is inferred by GreyAlien.","scope":"Contextual and written records associated with five named UAP/USO incident labels, beyond already released imagery."},
    "editorialNotes":{"centralBoundary":"A responsive-records determination is not authentication of the case descriptions.","classificationBoundary":"Classification does not reveal the records' contents or validate any origin hypothesis.","publicRecordBoundary":"Public PURSUE imagery and withheld contextual records are distinct objects.","lifecyclePrinciple":"News can age; knowledge does not.","sourceCaution":"The case number and cited classification authority are visible in reporting about the reproduced response; the complete request/response package should control any legal deadline or appeal."},
    "relatedNewsId":NEWS
})

write(ROOT / f"data/news/{NEWS}.json", {
    "id":NEWS,"recordType":"news_record","contentType":"government_records_foia_withholding_news","title":"AARO Says It Located Records on Five UAP/USO Cases—Then Withheld Them as Classified","source":"The Black Vault","author":"John Greenewald Jr.","publicationDate":"2026-10-05","publicationDateDisplay":"October 5, 2026","originalUrl":ARTICLE,"primarySourceUrl":ARTICLE,
    "summary":"AARO reported locating records responsive to a FOIA request covering five UAP/USO case labels identified in a March 2026 congressional request, but withheld the material in full under classification-related authority. The response documents an access barrier; it does not independently authenticate the case descriptions or reveal what the withheld records contain.","dateAdded":"2026-10-07","newsStatus":"current","knowledgePermanence":"permanent",
    "relatedEntityIds":[DOC,"john-greenewald-jr","the-black-vault","aaro","anna-paulina-luna","house-oversight-committee","pursue","congressional-oversight","government-transparency","uap-disclosure","unidentified-submerged-objects",*[eid for eid,_,_ in incidents],*[eid for eid,*_ in claims]],
    "relationships":[rel("references_publication",DOC,role="permanent FOIA determination record"),rel("documented_by","the-black-vault"),rel("involved_person","john-greenewald-jr",role="FOIA requester")],
    "visibility":{"latestGateway":True,"publicEntityDirectory":False,"landmark":False},"lifecycle":{"status":"current","archiveEligible":True,"automaticAgingEnabled":False,"landmark":False},
    "editorialNotes":{"sourceHierarchy":"The agency determination reproduced in the reporting is the government source; the House letter establishes the case-label context; The Black Vault supplies the timely account.","evidenceBoundary":"Responsive records exist and were withheld; their contents and the reported incident descriptions remain unverified by the public record.","lifecyclePrinciple":"News can age; knowledge does not."}
})

for eid, kind, role in [("aaro","produced_document","FOIA determination"),("anna-paulina-luna","references_publication","March 2026 congressional request context"),("house-oversight-committee","references_publication","five incident labels"),("pursue","references_publication","public imagery versus withheld context"),("congressional-oversight","references_publication","congressional request and later FOIA response"),("government-transparency","references_publication","classified withholding outcome"),("uap-disclosure","references_publication","records-access pathway"),("unidentified-submerged-objects","references_publication","source-attributed USO case labels")]: enrich(eid, kind, role)

for path, record, label in [(ROOT/"data/news/index.json",NEWS,"V23.6D.11 AARO classified-responsive-records ingestion"),(ROOT/"data/research-library/index.json",DOC,"V23.6D.11 permanent FOIA determination ingestion")]:
    d=json.loads(path.read_text(encoding="utf-8")); d["records"]=[record]+[x for x in d.get("records",[]) if x!=record]; d["generatedBy"]=label; write(path,d)

news=ROOT/"categories/latest-uap-news.html"; html=news.read_text(encoding="utf-8"); anchor='          <article class="news-entry" id="podesta-delonge-call-2026-10-01"'
block=f'''          <article class="news-entry" id="aaro-classified-responsive-records-2026-10-05" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{ARTICLE}" target="_blank" rel="noopener noreferrer">AARO Says It Located Records on Five UAP/USO Cases—Then Withheld Them as Classified</a></h2>
            <p class="news-meta">The Black Vault / John Greenewald Jr. · October 5, 2026 · Government Records / FOIA</p>
            <p>AARO reported locating records responsive to a targeted FOIA request concerning five incident labels previously identified in a House records request. The agency withheld the responsive material in full under classification-related authority.</p>
            <p><strong>What this establishes:</strong> a defined records search produced responsive material and a classified-withholding determination. <strong>What it does not establish:</strong> that the incident descriptions are authenticated, that the objects were anomalous, or what the withheld records contain.</p>
            <p class="news-source-link"><a href="{ARTICLE}" target="_blank" rel="noopener noreferrer">Read Original Reporting →</a></p>
            <div class="news-related" aria-label="Connected Government Record"><strong>Connected Record</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id={DOC}">Permanent FOIA Record</a><a class="topic-chip" href="../entities/entity.html?id=aaro">AARO</a><a class="topic-chip" href="../entities/entity.html?id=john-greenewald-jr">John Greenewald Jr.</a><a class="topic-chip" href="../entities/entity.html?id=claim-responsive-records-do-not-authenticate-incidents">Evidence Boundary</a></div></div>
          </article>

'''
if anchor not in html: raise SystemExit("D10 news anchor missing")
news.write_text(html.replace(anchor,block+anchor,1),encoding="utf-8")

research=ROOT/"categories/research-library.html"; html=research.read_text(encoding="utf-8"); anchor='          <article class="research-entry" id="podesta-delonge-2016-uap-call"'
block=f'''          <article class="research-entry" id="aaro-five-case-classified-records" data-knowledge-permanence="permanent">
            <p class="research-type">Government Document / FOIA Determination / Classified Withholding · Permanent</p>
            <h2><a href="../entities/entity.html?id={DOC}">AARO FOIA Determination on Five UAP/USO Case Records</a></h2>
            <p class="research-meta">AARO / Department of War · FOIA 26-F-1892 · Reported October 5, 2026</p>
            <p>AARO reported locating responsive records associated with five named UAP/USO incident labels, then withheld the material in full under FOIA Exemption (b)(1) and Executive Order 13526.</p>
            <p><strong>Evidence boundary:</strong> a responsive record can concern a named allegation without authenticating it. Classification establishes an access restriction—not extraterrestrial origin, extraordinary performance, transmedium behavior or any other unseen content.</p>
            <p><strong>Related public record:</strong> the associated imagery and congressional labels are distinct from the contextual records sought through FOIA.</p>
            <p class="research-source-link"><a href="{ARTICLE}" target="_blank" rel="noopener noreferrer">Review Reporting and Reproduced Determination →</a></p>
            <div class="research-related" aria-label="Connected Evidence"><strong>Connected Evidence</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id=claim-aaro-located-responsive-records-five-cases">Records Located</a><a class="topic-chip" href="../entities/entity.html?id=claim-aaro-withheld-five-case-records-in-full">Withheld in Full</a><a class="topic-chip" href="../entities/entity.html?id=claim-classification-does-not-establish-record-contents">Classification Boundary</a><a class="topic-chip" href="latest-uap-news.html#aaro-classified-responsive-records-2026-10-05">Related News Coverage</a></div></div>
          </article>

'''
if anchor not in html: raise SystemExit("D10 research anchor missing")
research.write_text(html.replace(anchor,block+anchor,1),encoding="utf-8")

shell=ROOT/"entities/entity.html"; shell.write_text(shell.read_text(encoding="utf-8").replace("v=23.6d10","v=23.6d11"),encoding="utf-8")
print("V23.6D.11 ingestion applied")
