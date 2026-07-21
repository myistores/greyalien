# V20.1 — Related Podcast Series Optimization

- Suppressed each podcast episode's own parent series from the Related Podcast Series section.
- Preserved display of other podcast series when a direct cross-series relationship exists.
- Automatically suppresses the entire Related Podcast Series section when no qualifying series remains.
- Implemented generically through each episode's `seriesId`, so the same behavior applies to all current and future podcast series.
- No unrelated architecture, schema, navigation, UI, styling, routing, or content changes.
