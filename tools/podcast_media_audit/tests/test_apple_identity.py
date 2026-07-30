import unittest
from audit_pipeline.identity import compare_identity
class AppleIdentityTests(unittest.TestCase):
 def test_match(self):
  r=compare_identity({'episodeTitle':'David Jenkins: People of Earth','podcastSeries':'Somewhere in the Skies'},{'episodeTitle':'David Jenkins — People of Earth','showTitle':'Somewhere in the Skies','episodeId':'1001'})
  self.assertEqual(r['status'],'confirmed');self.assertTrue(r['seriesMatch'])
 def test_wrong_series(self):
  r=compare_identity({'episodeTitle':'David Jenkins: People of Earth','podcastSeries':'Somewhere in the Skies'},{'episodeTitle':'David Jenkins: People of Earth','showTitle':'Another Show','episodeId':'1001'})
  self.assertEqual(r['status'],'mismatch')
 def test_off_by_one(self):
  r=compare_identity({'episodeTitle':'Episode 15 David Jenkins','episodeNumber':15,'podcastSeries':'Somewhere in the Skies'},{'episodeTitle':'Episode 14 David Jenkins','episodeNumber':14,'showTitle':'Somewhere in the Skies','episodeId':'1001'})
  self.assertEqual(r['status'],'mismatch')
if __name__=='__main__':unittest.main()
