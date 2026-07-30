import unittest
from audit_pipeline.completion import complete_episode_media, preferred_destination_issue, select_preferred

class OfficialMediaCompletionTests(unittest.TestCase):
    def episode(self, media):
        return {'id':'episode-x','episodeTitle':'Example','date':'2017-01-01','officialMedia':media,'mediaMigration':{}}

    def test_episode_destination_recovery_promotes_direct_and_preserves_series(self):
        entity=self.episode([
            {'platform':'Apple Podcasts','url':'https://podcasts.apple.com/us/podcast/show/id1','destinationType':'series','official':True,'approved':True,'published':True,'preferredRank':6},
            {'platform':'Apple Podcasts','url':'https://podcasts.apple.com/us/podcast/example/id1?i=2','destinationType':'episode','official':True,'approved':True,'published':True,'preferredRank':3,'verified':True},
        ])
        out=complete_episode_media(entity,checked_at='2026-07-30T00:00:00+00:00')
        self.assertEqual(out['mediaMigration']['preferredCanonicalUrl'], entity['officialMedia'][1]['url'])
        self.assertEqual(len(out['officialMedia']),2)
        self.assertTrue(out['officialMedia'][0]['secondaryOnly'])

    def test_existing_direct_episode_retained(self):
        url='https://open.spotify.com/episode/abc'
        out=complete_episode_media(self.episode([{'platform':'Spotify','url':url,'destinationType':'episode','official':True,'approved':True,'published':True,'preferredRank':2,'verified':True}]),checked_at='2026-07-30T00:00:00+00:00')
        self.assertEqual(out['mediaMigration']['preferredCanonicalUrl'],url)
        self.assertEqual(out['officialMedia'][0]['url'],url)

    def test_missing_direct_requires_review_without_fabrication(self):
        url='https://open.spotify.com/show/abc'
        out=complete_episode_media(self.episode([{'platform':'Spotify','url':url,'destinationType':'series','official':True,'approved':True,'published':True,'preferredRank':2}]),checked_at='2026-07-30T00:00:00+00:00')
        self.assertIsNone(out['mediaMigration']['preferredCanonicalUrl'])
        self.assertTrue(out['mediaMigration']['manualReviewRequired'])
        self.assertEqual(out['mediaMigration']['fabricatedDestinations'],0)
        self.assertEqual(out['officialMedia'][0]['url'],url)

    def test_platform_independence(self):
        records=[
            {'platform':'Apple Podcasts','url':'https://podcasts.apple.com/us/podcast/show/id1','official':True,'approved':True,'published':True},
            {'platform':'Spotify','url':'https://open.spotify.com/episode/abc','official':True,'approved':True,'published':True,'preferredRank':2},
        ]
        self.assertEqual(select_preferred(records)['platform'],'Spotify')

    def test_show_page_cannot_be_preferred(self):
        record={'platform':'Apple Podcasts','url':'https://podcasts.apple.com/us/podcast/show/id1'}
        issue=preferred_destination_issue(record)
        self.assertEqual(issue['code'],'preferred_destination_not_episode_level')
        self.assertEqual(issue['classification'],'podcast show page')

    def test_recovery_ambiguity_requires_review(self):
        entity=self.episode([
            {'platform':'Apple Podcasts','url':'https://podcasts.apple.com/us/podcast/a/id1?i=10','official':True,'approved':True,'published':True,'preferredRank':3,'recoveryProvenance':{'confirmedEpisodeIdentity':'episode-a'}},
            {'platform':'Spotify','url':'https://open.spotify.com/episode/b','official':True,'approved':True,'published':True,'preferredRank':2,'recoveryProvenance':{'confirmedEpisodeIdentity':'episode-b'}},
        ])
        out=complete_episode_media(entity,checked_at='2026-07-30T00:00:00+00:00')
        self.assertEqual(out['mediaMigration']['crossPlatformConfirmation']['status'],'review_required')
        self.assertEqual(out['mediaMigration']['crossPlatformConfirmation']['reason'],'cross_platform_episode_disagreement')

if __name__=='__main__': unittest.main()
