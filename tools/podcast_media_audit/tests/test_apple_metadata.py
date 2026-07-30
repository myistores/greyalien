import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from audit_pipeline.apple import extract_apple_metadata,classify_apple_destination,extract_apple_ids,normalize_apple_url
FIX=Path(__file__).parent/'fixtures'/'apple'
class AppleMetadataTests(unittest.TestCase):
 def test_direct_episode(self):
  soup=BeautifulSoup((FIX/'direct_episode.html').read_text(),'html.parser');url='https://podcasts.apple.com/us/podcast/somewhere/id1227858637?i=1000390000015'
  m=extract_apple_metadata(soup,url,url,soup.link['href'])
  self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertEqual(m['episodeTitle'],'David Jenkins: People of Earth');self.assertEqual(m['showId'],'1227858637');self.assertEqual(m['episodeId'],'1000390000015');self.assertEqual(classify_apple_destination(url,url,m['canonicalUrl'],m),'direct episode');self.assertEqual(m['metadataSources']['showTitle']['source'],'embedded_json')
 def test_show_page(self):
  soup=BeautifulSoup((FIX/'show_page.html').read_text(),'html.parser');url='https://podcasts.apple.com/us/podcast/somewhere/id1227858637';m=extract_apple_metadata(soup,url,url,url)
  self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertIsNone(m.get('episodeId'));self.assertEqual(classify_apple_destination(url,url,url,m),'podcast series or show')
 def test_ids_and_normalization(self):
  u='https://podcasts.apple.com/us/podcast/x/id123?utm_source=x&i=100456';self.assertEqual(extract_apple_ids(u),{'showId':'123','episodeId':'100456'});self.assertEqual(normalize_apple_url(u),'https://podcasts.apple.com/us/podcast/x/id123?i=100456')
if __name__=='__main__':unittest.main()
