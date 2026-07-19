# Podcast ingestion package

1. Copy this folder and complete `episode.json`.
2. Add an optional transcript or private research notes outside the deployable website when rights are uncertain.
3. Run `python tools/ingest_podcast_episode.py path/to/episode.json`.
4. The command validates the episode, copies it to `data/entities/`, rebuilds the entity graph, podcast indexes, sitemap, and release summary, then runs quality checks.

The `relationships` array is the source of truth for graph connections. Display-only lists such as `mediaGuests` and `mediaSubjects` should match the relationship roles.
