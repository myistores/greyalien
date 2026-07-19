#!/usr/bin/env python3
"""GreyAlien Research Accelerator.

Creates reviewable podcast-ingestion drafts from official episode URLs, saved HTML,
or supplied text/transcripts. It never writes to data/entities and never publishes.
Standard-library only so it can run on a normal local Python installation.
"""
from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from html.parser import HTMLParser
from datetime import datetime, timezone
import argparse, html, json, re, shutil, sys

ROOT = Path(__file__).resolve().parents[1]
ENTITIES = ROOT / 'data/entities'
DEFAULT_OUT = ROOT / 'data/research-accelerator/runs'
UA = 'Mozilla/5.0 (compatible; GreyAlienResearchAccelerator/1.0; +https://greyalien.com/)'

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.meta={}; self.title=''; self._in_title=False; self.text=[]; self.jsonld=[]; self._json=False; self._jsonbuf=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='title': self._in_title=True
        if tag=='meta':
            key=a.get('property') or a.get('name')
            if key and a.get('content'): self.meta[key.lower()]=a['content'].strip()
        if tag=='script' and a.get('type','').lower()=='application/ld+json': self._json=True; self._jsonbuf=[]
    def handle_endtag(self, tag):
        if tag=='title': self._in_title=False
        if tag=='script' and self._json:
            self._json=False
            raw=''.join(self._jsonbuf).strip()
            if raw:
                try: self.jsonld.append(json.loads(raw))
                except Exception: pass
    def handle_data(self, data):
        if self._in_title: self.title += data
        if self._json: self._jsonbuf.append(data)
        if data.strip(): self.text.append(data.strip())

def slugify(s):
    s=html.unescape(s).lower().replace('&',' and ')
    s=re.sub(r"[^a-z0-9]+",'-',s).strip('-')
    return s or 'untitled'

def clean(s): return re.sub(r'\s+',' ',html.unescape(s or '')).strip()

def load_entities():
    entities={}
    for p in ENTITIES.glob('*.json'):
        try:
            e=json.loads(p.read_text(encoding='utf-8')); entities[e['id']]=e
        except Exception: continue
    return entities

def aliases(e):
    vals={e.get('name',''), e.get('episodeTitle','')}
    vals.update(e.get('aliases',[]) if isinstance(e.get('aliases'),list) else [])
    # Conservative short-name aliases for person names and organizations.
    name=e.get('name','')
    if e.get('type')=='person' and len(name.split())>=2: vals.add(name)
    return sorted({clean(v) for v in vals if clean(v)}, key=len, reverse=True)

def extract_page(raw_html, url):
    p=PageParser(); p.feed(raw_html)
    title=clean(p.meta.get('og:title') or p.meta.get('twitter:title') or p.title)
    desc=clean(p.meta.get('og:description') or p.meta.get('description') or p.meta.get('twitter:description'))
    image=clean(p.meta.get('og:image') or p.meta.get('twitter:image'))
    published=clean(p.meta.get('article:published_time') or p.meta.get('date'))
    for block in p.jsonld:
        blocks=block if isinstance(block,list) else [block]
        for b in blocks:
            if not isinstance(b,dict): continue
            title=title or clean(b.get('headline') or b.get('name'))
            desc=desc or clean(b.get('description'))
            published=published or clean(b.get('datePublished'))
            if not image:
                im=b.get('image')
                image=clean(im[0] if isinstance(im,list) and im else im if isinstance(im,str) else '')
    body=clean(' '.join(p.text))
    return {'url':url,'title':title,'description':desc,'published':published,'image':image,'bodyText':body}

def fetch(url, timeout=25):
    req=Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/xhtml+xml'})
    with urlopen(req,timeout=timeout) as r:
        charset=r.headers.get_content_charset() or 'utf-8'
        return r.read().decode(charset,errors='replace')

def parse_episode_number(text, url):
    patterns=[r'episode\s*#?\s*(\d+)',r'/episode-(\d+)(?:\D|$)']
    for s in (text,url):
        for pat in patterns:
            m=re.search(pat,s or '',re.I)
            if m: return int(m.group(1))
    return None

def iso_date(value):
    if not value: return ''
    m=re.match(r'(\d{4}-\d{2}-\d{2})',value)
    if m: return m.group(1)
    for fmt in ('%B %d, %Y','%b %d, %Y','%m/%d/%Y'):
        try: return datetime.strptime(value,fmt).strftime('%Y-%m-%d')
        except Exception: pass
    return ''

def date_display(date):
    try: return datetime.strptime(date,'%Y-%m-%d').strftime('%B %-d, %Y')
    except Exception:
        try: return datetime.strptime(date,'%Y-%m-%d').strftime('%B %#d, %Y')
        except Exception: return date

def title_from_page(title, episode_number):
    t=re.sub(r'\s*[|–—-]\s*WEAPONIZED.*$','',title,flags=re.I)
    t=re.sub(r'^WEAPONIZED\s*(?:Episode)?\s*#?\s*\d+\s*[|:–—-]*\s*','',t,flags=re.I)
    t=clean(t)
    return t or (f'Episode {episode_number}' if episode_number else 'Episode title requires review')

def detect_mentions(text, entities, excluded):
    hay=' '+clean(text).lower()+' '
    found=[]
    for eid,e in entities.items():
        if eid in excluded or e.get('type') in ('podcast_episode','timeline_event','podcast_series'): continue
        best=''
        for a in aliases(e):
            al=a.lower()
            if len(al)<5: continue
            if re.search(r'(?<![a-z0-9])'+re.escape(al)+r'(?![a-z0-9])',hay): best=a; break
        if best: found.append({'id':eid,'name':e.get('name',eid),'type':e.get('type'),'matchedText':best})
    return sorted(found,key=lambda x:(x['type'],x['name']))

def relationship_for(entity):
    typ=entity['type']
    return {'person':'features_person','organization':'references_organization','topic':'discussed_topic','case':'references_case','document':'references_document','publication':'references_publication','hearing':'references_hearing','legislation':'references_legislation','claim':'presented_claim'}.get(typ,'references_entity')

def confidence(page, date, epno, mentions, transcript):
    score=0; reasons=[]
    if page.get('title'): score+=20
    else: reasons.append('Missing page title')
    if page.get('description'): score+=20
    else: reasons.append('Missing official description')
    if date: score+=15
    else: reasons.append('Publication date requires review')
    if epno is not None: score+=15
    else: reasons.append('Episode number requires review')
    if mentions: score+=15
    else: reasons.append('No existing knowledge-graph entities matched')
    if transcript: score+=15
    else: reasons.append('No transcript supplied; relationships derive from page metadata/text only')
    return score,reasons

def make_draft(item, page, entities, cfg, transcript=''):
    series_id=item.get('seriesId') or cfg['seriesId']; series=entities.get(series_id,{})
    epno=item.get('episodeNumber') or parse_episode_number(page.get('title',''),page.get('url',''))
    date=item.get('date') or iso_date(page.get('published',''))
    ep_title=item.get('episodeTitle') or title_from_page(page.get('title',''),epno)
    year=date[:4] if date else 'undated'
    eid=item.get('id') or f'{year}-{slugify(series.get("name",series_id))}-episode-{epno if epno is not None else slugify(ep_title)[:28]}'
    research_text=' '.join([page.get('title',''),page.get('description',''),page.get('bodyText','')[:50000],transcript[:150000]])
    host_ids=cfg.get('hostIds',[])
    mentions=detect_mentions(research_text,entities,set(host_ids+[series_id,eid]))
    rel=[{'type':'episode_of','target':series_id}]
    for hid in host_ids:
        rel.append({'type':'features_person','target':hid,'role':'host','context':f'{series.get("name",series_id)} host'})
    for m in mentions:
        r={'type':relationship_for(m),'target':m['id']}
        if m['type']=='person': r.update({'role':'referenced_subject','context':f'Automatically matched from {m["matchedText"]}; verify guest/subject role'})
        rel.append(r)
    score,reasons=confidence(page,date,epno,mentions,bool(transcript.strip()))
    url=page.get('url','')
    summary=page.get('description') or 'Summary requires human review from the official episode page or transcript.'
    draft={
      'id':eid,'type':'podcast_episode','name':f'{series.get("name",series_id)} Episode #{epno} — {ep_title}' if epno is not None else f'{series.get("name",series_id)} — {ep_title}',
      'summary':summary,'date':date,'dateDisplay':date_display(date),'seriesId':series_id,'episodeNumber':epno,
      'episodeTitle':ep_title,'status':item.get('status','Draft — human review required'),'mediaType':'Podcast episode',
      'mediaPlatform':series.get('name',series_id),'mediaHost':', '.join(entities.get(x,{}).get('name',x) for x in host_ids),
      'mediaGuests':[],'mediaSubjects':[m['name'] for m in mentions],'principalClaims':[],
      'researchNotes':['Generated by GreyAlien Research Accelerator; every relationship and role requires human review.'],
      'relationships':rel,'mediaLinks':[{'label':'Open official episode page','url':url,'platform':series.get('name',series_id)}] if url else [],
      'officialLinks':[], 'referenceSources':[{'label':'Official episode page','url':url,'sourceType':'official_episode_page','role':'primary_reference'}] if url else []
    }
    review={'id':eid,'sourceUrl':url,'confidenceScore':score,'confidenceBand':'high' if score>=80 else 'medium' if score>=55 else 'low',
            'matchedExistingEntities':mentions,'unresolvedCandidatePhrases':[], 'warnings':reasons,
            'requiredReview':['Verify title and publication date','Classify each matched person as guest, host, or discussed subject','Remove false-positive entity matches','Add important new people/organizations/cases not already in the graph','Draft 3–7 principal claims only when the episode materially advances claims','Confirm Official Links remain entity-owned and episode URLs stay in Reference Sources']}
    return draft,review

def read_manifest(path):
    d=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(d,list): return {'seriesId':'weaponized-podcast','hostIds':['jeremy-corbell','george-knapp'],'episodes':d}
    return d

def main():
    ap=argparse.ArgumentParser(description='Create reviewable GreyAlien podcast ingestion drafts.')
    ap.add_argument('manifest',help='JSON manifest containing seriesId, hostIds, and episodes')
    ap.add_argument('--out',default='',help='Output run directory')
    ap.add_argument('--offline-dir',default='',help='Directory containing saved HTML files named by episode number or manifest htmlFile')
    ap.add_argument('--transcript-dir',default='',help='Directory containing transcript files named episode-N.txt or manifest transcriptFile')
    ap.add_argument('--no-network',action='store_true',help='Do not fetch URLs; require saved HTML or supplied title/description')
    args=ap.parse_args()
    manifest_path=Path(args.manifest).resolve(); cfg=read_manifest(manifest_path); entities=load_entities()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); out=Path(args.out).resolve() if args.out else DEFAULT_OUT/stamp
    drafts=out/'drafts'; reviews=out/'reviews'; rawdir=out/'raw'; drafts.mkdir(parents=True,exist_ok=True); reviews.mkdir(); rawdir.mkdir()
    offline=Path(args.offline_dir).resolve() if args.offline_dir else None; tdir=Path(args.transcript_dir).resolve() if args.transcript_dir else None
    run={'schemaVersion':1,'generatedAt':datetime.now(timezone.utc).isoformat(),'manifest':str(manifest_path),'seriesId':cfg.get('seriesId'),'status':'completed','episodes':[]}
    for item in cfg.get('episodes',[]):
        epno=item.get('episodeNumber'); url=item.get('url',''); raw=''; source_mode='manifest_metadata'
        html_file=item.get('htmlFile')
        candidates=[]
        if html_file: candidates.append(Path(html_file))
        if offline and epno is not None: candidates += [offline/f'episode-{epno}.html',offline/f'{epno}.html']
        for c in candidates:
            if not c.is_absolute(): c=manifest_path.parent/c
            if c.exists(): raw=c.read_text(encoding='utf-8',errors='replace'); source_mode='saved_html'; break
        err=''
        if not raw and url and not args.no_network:
            try: raw=fetch(url); source_mode='network'; (rawdir/f'episode-{epno or "unknown"}.html').write_text(raw,encoding='utf-8')
            except Exception as ex: err=f'Fetch failed: {ex}'
        page=extract_page(raw,url) if raw else {'url':url,'title':item.get('pageTitle',''),'description':item.get('description',''),'published':item.get('date',''),'image':'','bodyText':item.get('bodyText','')}
        transcript=''; tf=item.get('transcriptFile')
        tc=[]
        if tf: tc.append(Path(tf))
        if tdir and epno is not None: tc += [tdir/f'episode-{epno}.txt',tdir/f'{epno}.txt']
        for c in tc:
            if not c.is_absolute(): c=manifest_path.parent/c
            if c.exists(): transcript=c.read_text(encoding='utf-8',errors='replace'); break
        draft,review=make_draft(item,page,entities,cfg,transcript)
        if err: review['warnings'].append(err)
        (drafts/f'{draft["id"]}.json').write_text(json.dumps(draft,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        (reviews/f'{draft["id"]}.json').write_text(json.dumps(review,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        md=[f'# Review — {draft["name"]}','',f'- Confidence: **{review["confidenceScore"]}/100 ({review["confidenceBand"]})**',f'- Source mode: `{source_mode}`',f'- Official page: {url or "Not supplied"}','','## Existing entity matches']
        md += [f'- `{m["id"]}` — {m["name"]} ({m["type"]}; matched “{m["matchedText"]}”)' for m in review['matchedExistingEntities']] or ['- None']
        md += ['','## Warnings']+[f'- {x}' for x in review['warnings']] + ['','## Required human review']+[f'- [ ] {x}' for x in review['requiredReview']]
        (reviews/f'{draft["id"]}.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
        run['episodes'].append({'id':draft['id'],'episodeNumber':draft.get('episodeNumber'),'confidenceScore':review['confidenceScore'],'sourceMode':source_mode,'warnings':review['warnings']})
    (out/'run-report.json').write_text(json.dumps(run,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'README.md').write_text('# Research Accelerator Run\n\nDrafts are not publication-ready until every review checklist is completed.\n\nAfter review, copy approved JSON records into a clean batch folder and run:\n\n```bash\npython tools/import_batch.py path/to/approved-batch --dry-run\npython tools/import_batch.py path/to/approved-batch\n```\n',encoding='utf-8')
    print(f'Research Accelerator created {len(run["episodes"])} draft(s) in {out}')
    print('No live entity records were modified.')

if __name__=='__main__': main()
