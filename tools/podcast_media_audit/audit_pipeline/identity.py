from __future__ import annotations
from datetime import date
from .common import tokens,extract_episode_number,norm_text

def compare_identity(job, evidence):
 expected_title=job.get('episodeTitle') or ''; actual_title=evidence.get('episodeTitle') or evidence.get('ogTitle') or evidence.get('pageTitle') or ''
 expected_num=job.get('episodeNumber'); actual_num=evidence.get('episodeNumber') or extract_episode_number(actual_title)
 et,at=tokens(expected_title),tokens(actual_title); overlap=len(et&at)/max(1,len(et))
 series_expected=norm_text(job.get('expectedPodcast') or job.get('podcastSeries')); series_actual=norm_text(evidence.get('podcastName') or evidence.get('publisherName') or actual_title)
 series_match=bool(series_expected and (series_expected in series_actual or len(tokens(series_expected)&tokens(series_actual))>=max(1,min(2,len(tokens(series_expected))))))
 number_match=None if expected_num in (None,'') or actual_num in (None,'') else int(expected_num)==int(actual_num)
 expected_date=str(job.get('publicationDate') or '')[:10]; actual_date=str(evidence.get('publicationDate') or '')[:10]
 date_match=None if not expected_date or not actual_date else expected_date==actual_date
 if number_match is False: status='mismatch'
 elif overlap>=.72 and (series_match or not series_expected) and number_match is not False: status='confirmed'
 elif overlap>=.42 or number_match is True: status='probable_match'
 elif not actual_title: status='insufficient_evidence'
 else: status='mismatch'
 return {'status':status,'titleSimilarity':round(overlap,3),'seriesMatch':series_match,'episodeNumberMatch':number_match,'publicationDateMatch':date_match,'expected':{'series':job.get('podcastSeries'),'title':expected_title,'episodeNumber':expected_num,'publicationDate':job.get('publicationDate'),'guests':job.get('expectedGuests',[]),'platform':job.get('platform')},'captured':{'series':evidence.get('podcastName'),'title':actual_title,'episodeNumber':actual_num,'publicationDate':evidence.get('publicationDate'),'publisher':evidence.get('publisherName'),'platform':evidence.get('platform'),'mediaIdentifier':evidence.get('mediaIdentifier')}}
