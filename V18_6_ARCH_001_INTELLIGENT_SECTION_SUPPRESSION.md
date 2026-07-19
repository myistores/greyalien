# GreyAlien V18.6 — ARCH-001 Intelligent Section Suppression

## Purpose
Prevent duplicate source blocks when **Research Provenance** and **Available Media** point to the same destinations.

## Rendering rule
The entity renderer now creates a canonical URL set for `referenceSources` and `mediaLinks`.

When both non-empty sets are identical, the renderer:

- keeps **Watch or Listen / Available Media**;
- suppresses **Research Provenance / Reference Sources**.

When the sets differ, both sections remain visible so research-only sources are preserved.

## Canonical URL normalization
Before comparison, the renderer normalizes URLs by:

- removing fragments;
- normalizing host casing and default ports;
- removing common tracking parameters (`utm_*`, `fbclid`, `gclid`, `mc_cid`, `mc_eid`);
- sorting remaining query parameters;
- collapsing duplicate path slashes;
- treating trailing-slash variants as equivalent.

## Scope
Architecture/rendering change only. No entity research data, relationships, page content, or navigation were otherwise changed.
