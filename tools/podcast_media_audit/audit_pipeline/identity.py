from __future__ import annotations
from .common import tokens,extract_episode_number,norm_text

def _similarity(a,b):
 at,bt=tokens(a),tokens(b)
 return len(at&bt)/max(1,len(at))
def compare_identity(job,evidence):
 expected_title=job.get('episodeTitle') or ''; actual_title=evidence.get('episodeTitle') or evidence.get('ogTitle') or evidence.get('pageTitle') or ''
 expected_num=job.get('episodeNumber'); actual_num=evidence.get('episodeNumber') or extract_episode_number(actual_title)
 title_similarity=_similarity(expected_title,actual_title)
 series_expected=norm_text(job.get('expectedPodcast') or job.get('podcastSeries'))
 series_actual=norm_text(evidence.get('showTitle') or evidence.get('podcastName') or evidence.get('publisherName'))
 series_similarity=_similarity(series_expected,series_actual) if series_expected and series_actual else 0
 series_match=None if not series_expected or not series_actual else (series_expected==series_actual or series_similarity>=.75)
 number_match=None if expected_num in (None,'') or actual_num in (None,'') else int(expected_num)==int(actual_num)
 expected_date=str(job.get('publicationDate') or '')[:10]; actual_date=str(evidence.get('publicationDate') or '')[:10]
 date_match=None if not expected_date or not actual_date else expected_date==actual_date
 warnings=[]; score=0
 if evidence.get('episodeId'):score+=10
 if series_match is True:score+=20
 elif series_match is False:score-=50; warnings.append('series_conflict')
 if title_similarity>=.9:score+=30
 elif title_similarity>=.72:score+=24
 elif actual_title:score-=40; warnings.append('episode_title_conflict')
 if number_match is True:score+=20
 elif number_match is False:score-=45; warnings.append('episode_number_conflict')
 if date_match is True:score+=10
 elif date_match is False:score-=15; warnings.append('publication_date_conflict')
 score=max(0,min(100,score))
 if number_match is False or series_match is False or (actual_title and title_similarity<.42):status='mismatch'
 elif score>=60 and title_similarity>=.72 and series_match is not False:status='confirmed'
 elif title_similarity>=.42 or number_match is True:status='probable_match'
 else:status='insufficient_evidence'
 return {'status':status,'identityScore':score,'titleSimilarity':round(title_similarity,3),'seriesSimilarity':round(series_similarity,3),'seriesMatch':series_match,'episodeTitleMatch':None if not actual_title else title_similarity>=.72,'episodeNumberMatch':number_match,'publicationDateMatch':date_match,'guestMatch':None,'warnings':warnings,'expected':{'series':job.get('podcastSeries'),'title':expected_title,'episodeNumber':expected_num,'publicationDate':job.get('publicationDate'),'guests':job.get('expectedGuests',[]),'platform':job.get('platform')},'captured':{'series':evidence.get('showTitle') or evidence.get('podcastName'),'title':actual_title,'episodeNumber':actual_num,'publicationDate':evidence.get('publicationDate'),'publisher':evidence.get('publisherName'),'platform':evidence.get('platform'),'mediaIdentifier':evidence.get('episodeId') or evidence.get('mediaIdentifier'),'showId':evidence.get('showId'),'episodeId':evidence.get('episodeId')}}
