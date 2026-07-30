import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from audit_pipeline.apple import (
 extract_apple_metadata,classify_apple_destination,extract_apple_ids,
 normalize_apple_url,is_apple_branding,is_apple_platform_branding,
 is_generic_episode_ui_label
)
FIX=Path(__file__).parent/'fixtures'/'apple'
class AppleMetadataTests(unittest.TestCase):
 def parse(self,name,url,canonical=None):
  soup=BeautifulSoup((FIX/name).read_text(),'html.parser');return extract_apple_metadata(soup,url,url,canonical or url)
 def test_direct_episode(self):
  url='https://podcasts.apple.com/us/podcast/somewhere/id1227858637?i=1000390000015';m=self.parse('direct_episode.html',url)
  self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertEqual(m['episodeTitle'],'David Jenkins: People of Earth');self.assertEqual(m['showId'],'1227858637');self.assertEqual(m['episodeId'],'1000390000015');self.assertEqual(classify_apple_destination(url,url,m['canonicalUrl'],m),'direct episode');self.assertIn(m['metadataSources']['showTitle']['source'],{'json_ld','apple_structured_metadata'})
 def test_show_page(self):
  url='https://podcasts.apple.com/us/podcast/somewhere-in-the-skies/id1227858637';m=self.parse('show_page.html',url)
  self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertIsNone(m.get('episodeId'));self.assertEqual(classify_apple_destination(url,url,url,m),'podcast series or show')
 def test_branding_rejected(self):
  url='https://podcasts.apple.com/us/podcast/x/id123';m=self.parse('branding_candidate.html',url)
  self.assertNotEqual(m.get('showTitle'),'Apple Podcasts');self.assertTrue(any(c['rejectionReason']=='platform_branding' for c in m['rejectedMetadataCandidates']));self.assertTrue(is_apple_branding('Listen on Apple Podcasts'))
 def test_branding_variants(self):
  variants=['Apple Podcasts','@ApplePodcasts',' Apple   Podcasts Preview ','Listen with Apple Podcasts','Available on Apple Podcasts','Apple Podcasts – Preview','Podcasts on Apple']
  for value in variants:self.assertTrue(is_apple_platform_branding(value),value)
  self.assertFalse(is_apple_platform_branding('The Apple Orchard Mysteries'))
 def test_generic_ui_labels(self):
  for value in ['Play','Listen Now','Preview',' Share ']:self.assertTrue(is_generic_episode_ui_label(value),value)
  self.assertFalse(is_generic_episode_ui_label('Play It Again: The History of UFO Radio'))
  self.assertFalse(is_generic_episode_ui_label('Preview of Tomorrow’s Disclosure Hearing'))
 def test_twitter_branding_structured_title_wins(self):
  url='https://podcasts.apple.com/us/podcast/x/id123';m=self.parse('twitter_branding.html',url)
  self.assertEqual(m['showTitle'],'Somewhere in the Skies')
  self.assertTrue(any(c['value']=='@ApplePodcasts' and c['rejectionReason']=='platform_branding' for c in m['rejectedMetadataCandidates']))
 def test_branding_only_returns_null(self):
  url='https://podcasts.apple.com/us/podcast/id123';m=self.parse('branding_only.html',url)
  self.assertIsNone(m.get('showTitle'));self.assertIn('insufficient_metadata:showTitle',m['reviewReasons'])
 def test_generic_play_label_rejected(self):
  url='https://podcasts.apple.com/us/podcast/x/id123?i=1001';m=self.parse('generic_play.html',url)
  self.assertEqual(m['episodeTitle'],'David Jenkins: People of Earth')
  self.assertTrue(any(c['value']=='Play' and c['rejectionReason']=='generic_ui_label' for c in m['rejectedMetadataCandidates']))
 def test_embedded_metadata_outranks_og_and_dom(self):
  url='https://podcasts.apple.com/us/podcast/x/id123?i=1001';m=self.parse('structured_precedence.html',url)
  self.assertEqual(m['episodeTitle'],'David Jenkins: People of Earth');self.assertEqual(m['metadataSources']['episodeTitle']['source'],'apple_structured_metadata')
 def test_jsonld_episode_fallback(self):
  url='https://podcasts.apple.com/us/podcast/x/id123?i=1001';m=self.parse('jsonld_episode_fallback.html',url)
  self.assertEqual(m['episodeTitle'],'Micah Hanks: Toward a Better Ufology');self.assertEqual(m['metadataSources']['episodeTitle']['source'],'json_ld')
 def test_valid_titles_containing_play_and_apple(self):
  episode_url='https://podcasts.apple.com/us/podcast/x/id123?i=1001';m=self.parse('valid_play_title.html',episode_url)
  self.assertEqual(m['episodeTitle'],'Play It Again: The History of UFO Radio')
  show_url='https://podcasts.apple.com/us/podcast/x/id123';m=self.parse('valid_apple_title.html',show_url)
  self.assertEqual(m['showTitle'],'The Apple Orchard Mysteries')
 def test_twitter_branding_og_fallback(self):
  url='https://podcasts.apple.com/us/podcast/x/id123';m=self.parse('twitter_branding_og_fallback.html',url)
  self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertEqual(m['metadataSources']['showTitle']['source'],'open_graph')
 def test_play_heading_and_button_do_not_override_structured(self):
  url='https://podcasts.apple.com/us/podcast/x/id123?i=1001';m=self.parse('play_heading.html',url)
  self.assertEqual(m['episodeTitle'],'David Jenkins: People of Earth')
  self.assertTrue(any(c['source']=='dom_text' and c['value']=='Play' and c['rejected'] for c in m['metadataCandidates']))
 def test_jsonld_precedence(self):
  url='https://podcasts.apple.com/us/podcast/x/id123?i=1001';m=self.parse('jsonld_fallback.html',url);self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertEqual(m['metadataSources']['showTitle']['source'],'json_ld')
 def test_open_graph_fallback(self):
  url='https://podcasts.apple.com/us/podcast/x/id123?i=1001';m=self.parse('og_fallback.html',url);self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertEqual(m['metadataSources']['showTitle']['source'],'open_graph')
 def test_html_title_and_canonical_fallback(self):
  url='https://podcasts.apple.com/gb/podcast/somewhere-in-the-skies/id1227858637';m=self.parse('title_fallback.html',url);self.assertEqual(m['showTitle'],'Somewhere in the Skies');self.assertIn(m['metadataSources']['showTitle']['source'],{'canonical_metadata','document_title'});self.assertEqual(m['countryOrStorefront'],'gb')
 def test_ids_and_normalization(self):
  u='https://podcasts.apple.com/us/podcast/x/id123?utm_source=x&i=100456';self.assertEqual(extract_apple_ids(u),{'showId':'123','episodeId':'100456'});self.assertEqual(normalize_apple_url(u),'https://podcasts.apple.com/us/podcast/x/id123?i=100456')
if __name__=='__main__':unittest.main()
