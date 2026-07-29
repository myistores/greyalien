from __future__ import annotations
import re
from urllib.parse import parse_qs,urlsplit
from .common import host

def detect_platform(url, content_type=''):
 h=host(url)
 if h in {'youtube.com','www.youtube.com','youtu.be','m.youtube.com','music.youtube.com'}: return 'YouTube'
 if h.endswith('podcasts.apple.com'): return 'Apple Podcasts'
 if h.endswith('spotify.com') or h.endswith('spotify.link'): return 'Spotify'
 if h=='link.chtbl.com': return 'tracking or redirect wrapper'
 if 'rss' in h or any(x in content_type.lower() for x in ('rss','atom','xml')): return 'RSS'
 return 'official hosted podcast page' if h else 'unknown destination'

def media_identifier(url,platform):
 s=urlsplit(url or ''); q=parse_qs(s.query)
 if platform=='YouTube':
  if host(url)=='youtu.be': return s.path.strip('/').split('/')[0] or None
  return (q.get('v') or [None])[0]
 if platform=='Apple Podcasts':
  m=re.search(r'(?:\?|&)i=(\d+)',url or ''); return m.group(1) if m else None
 if platform=='Spotify':
  m=re.search(r'/(episode|show)/([A-Za-z0-9]+)',s.path); return m.group(2) if m else None
 return None

def detect_destination_type(url,platform,metadata=None):
 metadata=metadata or {}; s=urlsplit(url or ''); p=s.path.lower(); q=parse_qs(s.query)
 if platform=='tracking or redirect wrapper': return 'tracking wrapper'
 if platform=='YouTube':
  if '/watch' in p and q.get('v'): return 'direct episode'
  if '/playlist' in p or q.get('list'): return 'playlist'
  if any(x in p for x in ('/@','/channel/','/c/','/user/')): return 'channel'
 if platform=='Apple Podcasts': return 'direct episode' if ('i' in q or metadata.get('episodeNumber')) else 'podcast series or show'
 if platform=='Spotify':
  if '/episode/' in p: return 'direct episode'
  if '/show/' in p: return 'podcast series or show'
 if platform=='RSS': return 'RSS feed'
 if metadata.get('soft404'): return 'unavailable media'
 title=(metadata.get('pageTitle') or '').lower()
 if any(x in title for x in ('page not found','404','not found')): return 'unavailable media'
 if any(x in p for x in ('/episode/','/episodes/','/podcast/')): return 'hosted episode page'
 if p in ('','/'): return 'generic homepage'
 if any(x in p for x in ('archive','episodes','podcast')): return 'series archive'
 return 'hosted episode page'
