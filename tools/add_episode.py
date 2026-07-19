#!/usr/bin/env python3
"""Backward-compatible wrapper for the Phase 2 podcast ingestion command."""
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2:
    raise SystemExit('Usage: python tools/add_episode.py episode.json')
raise SystemExit(subprocess.call([sys.executable,str(ROOT/'tools/ingest_podcast_episode.py'),sys.argv[1]]))
