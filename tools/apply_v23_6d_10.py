#!/usr/bin/env python3
"""Apply V23.6D.10 Podesta/DeLonge historical-event ingestion."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENT = ROOT / "data/entities"
EVENT = "event-2016-podesta-delonge-uap-conference-call"
NEWS = "2026-10-01-paradigm-podesta-delonge-uap-call"
PARADIGM = "https://www.paradigm.news/p/exclusive-podesta-responds-to-gruschs"
GUARDIAN = "https://www.theguardian.com/music/2016/oct/11/blink-182-hillary-clintons-campaign-chief-ufos-tom-delonge-john-podesta"
ROGAN = "https://www.youtube.com/watch?v=dYPXINFcvmI"

def write(path, obj): path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
def rel(kind, target, **extra): return {"type": kind, "target": target, **extra}
def entity(obj):
    obj.setdefault("relationships", []); obj.setdefault("officialLinks", []); obj.setdefault("referenceSources", [])
    write(ENT/f"{obj['id']}.json", obj)
def enrich(eid, kind, role):
    p=ENT/f"{eid}.json"; d=json.loads(p.read_text(encoding="utf-8"))
    if not any(r.get("target")==EVENT for r in d.get("relationships", [])): d.setdefault("relationships", []).append(rel(kind, EVENT, role=role))
    if not any(s.get("url")==PARADIGM for s in d.get("referenceSources", [])): d.setdefault("referenceSources", []).append({"label":"Paradigm — Podesta response to Grusch characterization","url":PARADIGM,"sourceType":"direct_interview_reporting","role":"connected_event_source"})
    write(p,d)

people = [
    ("john-podesta","John Podesta","Former White House chief of staff and government-transparency advocate who confirmed participating in the 2016 conference call while disputing its characterization as a public-acclimatization operation.","Former White House Chief of Staff and 2016 Clinton campaign chairman"),
    ("neil-mccasland","Neil McCasland","Retired U.S. Air Force major general identified as a participant in the 2016 UAP-related conference call confirmed by John Podesta.","Retired U.S. Air Force Major General"),
    ("robert-weiss","Robert Weiss","Former Lockheed Martin executive identified as a participant in the 2016 UAP-related conference call confirmed by John Podesta.","Former Lockheed Martin executive")
]
for eid,name,summary,status in people:
    entity({"id":eid,"type":"person","name":name,"summary":summary,"profileStatus":status,"profileSummary":summary,"inclusionNote":"Included because of directly reported participation in the historically documented 2016 conference call.","destinationPage":True,"visibleInDirectory":True,"searchable":True,"taxonomyStatus":"canonical","relationships":[rel("participated_in",EVENT,role="conference-call participant")],"referenceSources":[{"label":"Paradigm — Podesta responds to Grusch","url":PARADIGM,"sourceType":"direct_interview_reporting","role":"primary_reference"}]})

entity({"id":"lockheed-martin","type":"organization","name":"Lockheed Martin","summary":"U.S. aerospace and defense company; former executive Robert Weiss was identified as a participant in the 2016 UAP-related conference call.","organizationPurpose":"Aerospace, defense and advanced-technology development.","destinationPage":True,"visibleInDirectory":True,"searchable":True,"taxonomyStatus":"canonical","relationships":[rel("affiliated_with","robert-weiss",role="former executive; relationship direction retained for repository compatibility"),rel("timeline_connection",EVENT,role="participant affiliation context")],"officialLinks":[{"label":"Official website","url":"https://www.lockheedmartin.com/","linkType":"official_website"}],"referenceSources":[{"label":"Paradigm — Podesta responds to Grusch","url":PARADIGM,"sourceType":"direct_interview_reporting","role":"event_context"}]})

claims=[
 ("claim-2016-call-occurred","Podesta confirms the 2016 UAP-related conference call occurred","John Podesta says Tom DeLonge arranged a conference call involving Podesta, DeLonge, Neil McCasland and Robert Weiss.","confirmed_participant_statement"),
 ("claim-2016-call-declassification-discussion","The call included discussion of declassifying Department of Defense files","Podesta recalls that declassifying Department of Defense files was among the subjects discussed.","confirmed_discussion_subject"),
 ("claim-2016-call-stigma-discussion","The call included discussion of reducing professional stigma around UAP","Podesta recalls discussion of reducing the stigma faced by professionals who take UAP seriously.","confirmed_discussion_subject"),
 ("claim-grusch-2016-acclimatization-interpretation","Grusch characterizes the 2016 engagement as an authorized acclimatization effort","David Grusch attributed DeLonge's access to senior advisers to top cover for an effort to prepare the public before the 2016 election.","attributed_witness_interpretation_disputed"),
 ("claim-podesta-disputes-acclimatization-interpretation","Podesta disputes Grusch's acclimatization characterization","Podesta says he would not characterize the interaction as Grusch did and states that he believed the public did not need to be acclimated.","direct_participant_response"),
 ("claim-2016-call-confirmation-not-program-proof","Confirmation of the call does not establish an official acclimatization program","The confirmed call and discussion subjects do not independently prove that the interaction formed part of a covert or authorized public-acclimatization operation.","evidentiary_limitation")
]
for eid,name,summary,classification in claims:
    sources=[{"label":"Paradigm — Podesta responds to Grusch","url":PARADIGM,"sourceType":"direct_interview_reporting","role":"claim_source"}]
    if eid=="claim-grusch-2016-acclimatization-interpretation": sources.append({"label":"Joe Rogan Experience — David Grusch interview","url":ROGAN,"sourceType":"primary_interview","role":"attributed_claim_source"})
    entity({"id":eid,"type":"claim","name":name,"summary":summary,"relationships":[rel("timeline_connection",EVENT,role="claim subject")],"referenceSources":sources,"claimMetadata":{"classification":classification,"knowledgePermanence":"permanent","evidenceBoundary":"The event, the speaker's interpretation and the participant's response are represented independently."}})

entity({
 "id":EVENT,"type":"timeline_event","entitySubtype":"Historical UAP Discussion / Private Conference Call","name":"2016 Podesta–DeLonge UAP Conference Call",
 "summary":"A 2016 conference call arranged by Tom DeLonge and involving John Podesta, Neil McCasland and Robert Weiss. Podesta confirms that declassification of Department of Defense files and reduction of professional stigma around UAP were discussed, while disputing David Grusch's later characterization of the interaction as an authorized public-acclimatization operation.",
 "date":"2016-01","dateDisplay":"January 2016 (apparent timing in contemporary correspondence; exact call date not independently established)","eventCategory":"Historical UAP discussion and competing interpretations",
 "destinationPage":True,"visibleInDirectory":True,"searchable":True,"taxonomyStatus":"canonical",
 "relationships":[rel("involved_person","tom-delonge",role="organizer and participant"),rel("involved_person","john-podesta",role="participant"),rel("involved_person","neil-mccasland",role="participant"),rel("involved_person","robert-weiss",role="participant"),rel("references_organization","department-of-defense",role="declassification discussion"),rel("references_organization","lockheed-martin",role="Weiss affiliation context"),rel("references_organization","to-the-stars-academy",role="later organizational context; the call did not itself create TTSA"),rel("references_topic","uap-disclosure"),rel("references_topic","government-transparency"),*[rel("contains_claim",eid) for eid,*_ in claims]],
 "officialLinks":[],"referenceSources":[{"label":"Paradigm — Podesta responds to Grusch's claims","url":PARADIGM,"sourceType":"direct_interview_reporting","role":"primary_2026_confirmation"},{"label":"The Guardian — 2016 DeLonge/Podesta correspondence coverage","url":GUARDIAN,"sourceType":"contemporary_secondary_reporting","role":"historical_context"},{"label":"Joe Rogan Experience — David Grusch interview","url":ROGAN,"sourceType":"primary_interview","role":"grusch_interpretation_source"}],
 "historicalEventMetadata":{"eventStatus":"Occurrence and participants confirmed by John Podesta; broader purpose disputed","organizer":"Tom DeLonge","participants":["John Podesta","Tom DeLonge","Neil McCasland","Robert Weiss"],"confirmedSubjects":["Potential declassification of Department of Defense files","Reducing professional stigma around taking UAP seriously"],"disputedInterpretation":"Government-approved public acclimatization or popularization activity","relatedNewsId":NEWS},
 "editorialNotes":{"eventMeaningSeparation":"Confirmation that the call occurred is not confirmation of Grusch's explanation for why it occurred.","emailProvenance":"Historical messages establish what their authors wrote; embedded assertions require independent support.","ttsBoundary":"The event may provide historical context for DeLonge's later organizational activity but is not represented as formally creating To The Stars Academy.","lifecyclePrinciple":"News can age; knowledge does not."}
})

write(ROOT/f"data/news/{NEWS}.json",{
 "id":NEWS,"recordType":"news_record","contentType":"historical_confirmation_competing_claims_news","title":"Podesta Confirms 2016 UAP Discussion but Disputes Grusch's ‘Acclimatization’ Interpretation","source":"Paradigm","author":"Ben Schreckinger","publicationDate":"2026-10-01","publicationDateDisplay":"October 1, 2026","originalUrl":PARADIGM,"primarySourceUrl":PARADIGM,
 "summary":"John Podesta confirmed joining a 2016 conference call arranged by Tom DeLonge with Neil McCasland and Robert Weiss to discuss subjects including Defense Department file declassification and professional stigma around UAP. Podesta disputed David Grusch's characterization of the interaction as an authorized effort to acclimatize the public.","dateAdded":"2026-10-03","newsStatus":"current","knowledgePermanence":"permanent",
 "relatedEntityIds":[EVENT,"john-podesta","tom-delonge","neil-mccasland","robert-weiss","david-grusch","to-the-stars-academy","lockheed-martin","department-of-defense","uap-disclosure","government-transparency",*[eid for eid,*_ in claims]],
 "relationships":[rel("timeline_connection",EVENT,role="permanent historical record"),rel("documented_by","john-podesta",role="direct participant confirmation reported by Paradigm"),rel("references_person","david-grusch",role="source of disputed interpretation")],
 "visibility":{"latestGateway":True,"publicEntityDirectory":False,"landmark":False},"lifecycle":{"status":"current","archiveEligible":True,"automaticAgingEnabled":False,"landmark":False},
 "editorialNotes":{"sourceHierarchy":"Podesta's on-record response is the direct participant source; Grusch's interview supplies the attributed interpretation; historical correspondence supplies context.","evidenceBoundary":"The call is confirmed while its alleged acclimatization purpose remains disputed.","lifecyclePrinciple":"News can age; knowledge does not."}
})

for eid,kind,role in [("tom-delonge","participated_in","organizer and participant"),("david-grusch","made_claim","later disputed interpretation"),("to-the-stars-academy","timeline_connection","historical precursor context only"),("department-of-defense","timeline_connection","files discussed for possible declassification"),("uap-disclosure","timeline_connection","historical disclosure discussion"),("government-transparency","timeline_connection","declassification and stigma discussion")]: enrich(eid,kind,role)

for path,record,label in [(ROOT/"data/news/index.json",NEWS,"V23.6D.10 historical confirmation and competing-claims ingestion"),(ROOT/"data/research-library/index.json",EVENT,"V23.6D.10 permanent historical-event ingestion")]:
 d=json.loads(path.read_text(encoding="utf-8")); d["records"]=[record]+[x for x in d.get("records",[]) if x!=record]; d["generatedBy"]=label; write(path,d)

news=ROOT/"categories/latest-uap-news.html"; html=news.read_text(encoding="utf-8"); anchor='          <article class="news-entry" id="pursue-release-06-2026-09-18"'
block=f'''          <article class="news-entry" id="podesta-delonge-call-2026-10-01" data-news-status="current" data-knowledge-permanence="permanent">
            <h2><a href="{PARADIGM}" target="_blank" rel="noopener noreferrer">Podesta Confirms 2016 UAP Discussion but Disputes Grusch's “Acclimatization” Interpretation</a></h2>
            <p class="news-meta">Paradigm / Ben Schreckinger · October 1, 2026 · Historical Confirmation / Competing Claims</p>
            <p>John Podesta confirmed participating in a 2016 conference call arranged by Tom DeLonge with retired Air Force Maj. Gen. Neil McCasland and former Lockheed executive Robert Weiss. Podesta recalls discussion of declassifying Defense Department files and reducing professional stigma around taking UAP seriously.</p>
            <p><strong>Disputed interpretation:</strong> David Grusch characterized the interaction as an authorized public-acclimatization effort. Podesta rejected that characterization. Confirmation of the call does not independently establish that such a government program existed.</p>
            <p class="news-source-link"><a href="{PARADIGM}" target="_blank" rel="noopener noreferrer">Read Original Reporting →</a></p>
            <div class="news-related" aria-label="Connected Historical Record"><strong>Connected Record</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id={EVENT}">Permanent Conference-Call Record</a><a class="topic-chip" href="../entities/entity.html?id=john-podesta">John Podesta</a><a class="topic-chip" href="../entities/entity.html?id=tom-delonge">Tom DeLonge</a><a class="topic-chip" href="../entities/entity.html?id=david-grusch">David Grusch</a><a class="topic-chip" href="../entities/entity.html?id=claim-2016-call-confirmation-not-program-proof">Evidence Boundary</a></div></div>
          </article>

'''
if anchor not in html: raise SystemExit("D9 news anchor missing")
news.write_text(html.replace(anchor,block+anchor,1),encoding="utf-8")

research=ROOT/"categories/research-library.html"; html=research.read_text(encoding="utf-8"); anchor='          <article class="research-entry" id="pursue-release-06"'
block=f'''          <article class="research-entry" id="podesta-delonge-2016-uap-call" data-knowledge-permanence="permanent">
            <p class="research-type">Historical Record / Confirmed Discussion / Competing Interpretations · Permanent</p>
            <h2><a href="../entities/entity.html?id={EVENT}">2016 Podesta–DeLonge UAP Conference Call</a></h2>
            <p class="research-meta">John Podesta, Tom DeLonge, Neil McCasland &amp; Robert Weiss · January 2016 context · Confirmed by Podesta October 1, 2026</p>
            <p>Podesta confirms the call and recalls discussion of Defense Department file declassification and reducing professional stigma around UAP. Historical correspondence provides additional context for DeLonge's contacts and planned discussions.</p>
            <p><strong>Competing interpretations:</strong> Grusch describes the engagement as an authorized acclimatization effort; Podesta disputes that account. GreyAlien preserves the confirmed event independently from both interpretations.</p>
            <p><strong>Evidence boundary:</strong> A historical email proves what its author wrote—not every factual assertion embedded in the message. Confirmation of the call does not establish a covert government program.</p>
            <p class="research-source-link"><a href="{PARADIGM}" target="_blank" rel="noopener noreferrer">Read Podesta's Reported Response →</a></p>
            <div class="research-related" aria-label="Connected Claims"><strong>Connected Claims</strong><div class="topic-cloud"><a class="topic-chip" href="../entities/entity.html?id=claim-2016-call-occurred">Call Confirmed</a><a class="topic-chip" href="../entities/entity.html?id=claim-grusch-2016-acclimatization-interpretation">Grusch Interpretation</a><a class="topic-chip" href="../entities/entity.html?id=claim-podesta-disputes-acclimatization-interpretation">Podesta Dispute</a><a class="topic-chip" href="latest-uap-news.html#podesta-delonge-call-2026-10-01">Related News Coverage</a></div></div>
          </article>

'''
if anchor not in html: raise SystemExit("D9 research anchor missing")
research.write_text(html.replace(anchor,block+anchor,1),encoding="utf-8")

shell=ROOT/"entities/entity.html"; shell.write_text(shell.read_text(encoding="utf-8").replace("v=23.6d9","v=23.6d10"),encoding="utf-8")
print("V23.6D.10 ingestion applied")
