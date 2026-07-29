import unittest
from audit_pipeline.common import normalize_url
from audit_pipeline.detection import detect_platform,detect_destination_type,media_identifier
from audit_pipeline.identity import compare_identity
from audit_pipeline.http_client import classify_transport
from requests.exceptions import ConnectTimeout,SSLError
class Tests(unittest.TestCase):
 def test_normalize(self): self.assertEqual(normalize_url('HTTP://WWW.YouTube.com/watch?v=x&utm_source=a#z'),'http://www.youtube.com/watch?v=x')
 def test_platforms(self):
  self.assertEqual(detect_platform('https://youtu.be/abc'),'YouTube'); self.assertEqual(detect_platform('https://link.chtbl.com/x'),'tracking or redirect wrapper')
 def test_youtube_type(self): self.assertEqual(detect_destination_type('https://youtube.com/watch?v=abc','YouTube'),'direct episode')
 def test_id(self): self.assertEqual(media_identifier('https://youtube.com/watch?v=abc','YouTube'),'abc')
 def test_identity_off_by_one(self):
  r=compare_identity({'episodeTitle':'Need to Know Episode 14','episodeNumber':14,'podcastSeries':'Need to Know'},{'pageTitle':'Need to Know Episode 13','episodeNumber':13,'podcastName':'Need to Know','platform':'YouTube'})
  self.assertEqual(r['status'],'mismatch')
 def test_transport(self): self.assertEqual(classify_transport(ConnectTimeout()),'connection_timeout'); self.assertEqual(classify_transport(SSLError()),'tls_negotiation_failure')
if __name__=='__main__':unittest.main()
