#!/usr/bin/env python3
"""Validate entity-section rendering groups used by the browser renderer."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'data/schema/rendering-groups.json'
ENTITY_ENGINE=ROOT/'assets/js/entity-engine.js'

def main():
    errors=[]
    data=json.loads(CONFIG.read_text(encoding='utf-8'))
    groups=data.get('sectionGroups',[])
    keys=[]; assigned={}
    for group in groups:
        key=group.get('key'); label=group.get('label'); types=group.get('types',[])
        if not key or not label or not types:
            errors.append(f'Invalid section group: {group!r}')
            continue
        if key in keys: errors.append(f'Duplicate section key: {key}')
        keys.append(key)
        for entity_type in types:
            if entity_type in assigned:
                errors.append(f'Entity type {entity_type} appears in both {assigned[entity_type]} and {key}')
            assigned[entity_type]=key
    for required in ('interview','podcast_episode'):
        if assigned.get(required)!='media':
            errors.append(f'{required} must render in the unified media section')
    engine=ENTITY_ENGINE.read_text(encoding='utf-8')
    if 'rendering-groups.json' not in engine or 'sectionGroups=rendering.sectionGroups' not in engine:
        errors.append('Entity renderer is not using the centralized rendering-group configuration')
    if errors:
        print('Rendering rule validation: FAILED')
        for error in errors: print(f'- {error}')
        return 1
    print(f'Rendering rule validation: PASSED ({len(groups)} categories, {len(assigned)} entity types)')
    print('Unified Media category: interview + podcast_episode')
    return 0
if __name__=='__main__': raise SystemExit(main())
