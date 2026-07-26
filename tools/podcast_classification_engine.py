#!/usr/bin/env python3
"""GreyAlien V23 Podcast Classification Engine.

Classifies podcast releases during draft creation. It never publishes records,
never creates canonical entities, and never adds unreviewed relationships.
"""
from __future__ import annotations
from pathlib import Path
import argparse, json, re

ROOT=Path(__file__).resolve().parents[1]
CONFIG_PATH=ROOT/'data/podcast-classification-config.json'
ENTITY_TYPES=('person','organization','case','document','publication','topic','hearing','legislation','claim')

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def load_config(path=CONFIG_PATH): return json.loads(Path(path).read_text(encoding='utf-8'))
def phrase_hits(text, phrases):
    t=' '+text.lower()+' '
    return [p for p in phrases if re.search(r'(?<![a-z0-9])'+re.escape(p.lower())+r'(?![a-z0-9])',t)]

def classify_release(metadata, matched_entities=None, config=None):
    cfg=config or load_config(); matched_entities=matched_entities or []
    text=' '.join(clean(metadata.get(k,'')) for k in ('title','episodeTitle','description','summary','bodyText','transcript')).lower()
    source_depth=sum(bool(clean(metadata.get(k,''))) for k in ('description','bodyText','transcript'))
    topic_scores={tid:len(phrase_hits(text,terms)) for tid,terms in cfg['topics'].items()}
    ranked=[(t,s) for t,s in sorted(topic_scores.items(),key=lambda x:(-x[1],x[0])) if s]
    primary=[t for t,_ in ranked[:3]]; secondary=[t for t,_ in ranked[3:]]
    type_scores={typ:len(phrase_hits(text,terms)) for typ,terms in cfg['typeSignals'].items()}
    episode_type=max(type_scores,key=lambda k:type_scores[k]) if any(type_scores.values()) else 'unknown'
    research_hits=phrase_hits(text,cfg['researchSignals']); catalog_hits=phrase_hits(text,cfg['catalogSignals'])
    substantive=len(clean(metadata.get('description','')))>=120 or len(clean(metadata.get('transcript','')))>=600
    score=0; reasons=[]; warnings=[]
    if substantive: score+=25; reasons.append('Substantive official description or transcript available')
    score+=min(25,len(research_hits)*5)
    if research_hits: reasons.append('Research signals: '+', '.join(research_hits[:5]))
    score+=min(20,len(matched_entities)*4)
    if matched_entities: reasons.append(f'{len(matched_entities)} existing canonical entity match(es)')
    score+=min(20,sum(topic_scores.values())*3)
    if primary: reasons.append('Canonical topic matches: '+', '.join(primary))
    if episode_type in ('case_investigation','research_analysis','witness_account','documentary'): score+=10
    if catalog_hits:
        score-=35; reasons.append('Catalog-only signals: '+', '.join(catalog_hits[:4]))
    if episode_type in ('trailer','announcement','re_release'): score=min(score,25)
    if score>=cfg['contentClasses']['research']['minimumScore']: content_class='research'
    elif score>=cfg['contentClasses']['standard']['minimumScore']: content_class='standard'
    else: content_class='catalog'
    accelerator=cfg['contentClasses'][content_class]['researchAccelerator']
    confidence=45 + min(20,source_depth*7) + min(15,sum(topic_scores.values())*3) + (10 if episode_type!='unknown' else 0) + min(10,len(matched_entities)*2)
    confidence=max(0,min(100,confidence))
    if episode_type=='unknown': warnings.append('Episode type could not be determined confidently')
    if not primary: warnings.append('No canonical topic matched; manual topic assignment required')
    if not clean(metadata.get('description','')) and not clean(metadata.get('transcript','')): warnings.append('Classification is based on title/minimal metadata only')
    review_required=confidence<85 or bool(warnings) or content_class=='research'
    existing=[m.get('id') for m in matched_entities if m.get('id')]
    candidate_names=metadata.get('candidateEntityNames',[]) if isinstance(metadata.get('candidateEntityNames',[]),list) else []
    extract_types=['person','organization','case','document','publication','topic']
    if content_class=='catalog': extract_types=['person','topic']
    return {
      'engineVersion':cfg.get('engineVersion','23.0'),'contentClass':content_class,'episodeType':episode_type,
      'primaryTopics':primary,'secondaryTopics':secondary,'researchAccelerator':accelerator,
      'entityExtraction':{'existingCanonicalIds':existing,'candidateNames':candidate_names,'extractTypes':extract_types},
      'confidence':confidence,'score':score,'reasons':reasons,'warnings':warnings,'reviewRequired':review_required
    }

def main():
    ap=argparse.ArgumentParser(description='Classify one podcast-release metadata JSON file.')
    ap.add_argument('json_file'); ap.add_argument('--output'); args=ap.parse_args()
    data=json.loads(Path(args.json_file).read_text(encoding='utf-8'))
    result=classify_release(data,data.get('matchedEntities',[]))
    out=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output: Path(args.output).write_text(out,encoding='utf-8')
    else: print(out,end='')
if __name__=='__main__': main()
