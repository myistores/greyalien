from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from .detection import detect_destination_type, detect_platform

NON_EPISODE_TYPES = {
    'podcast series or show', 'playlist', 'channel', 'series archive',
    'RSS feed', 'generic homepage', 'publisher landing page', 'series',
    'archive', 'show', 'podcast show page'
}
EPISODE_TYPES = {'direct episode', 'hosted episode page', 'episode'}


def classify_media_record(record: dict[str, Any]) -> str:
    platform = record.get('platform') or detect_platform(record.get('url', ''))
    detected = detect_destination_type(record.get('url', ''), platform, record.get('validationMetadata') or {})
    aliases = {
        'direct episode': 'direct episode', 'hosted episode page': 'direct episode',
        'podcast series or show': 'podcast show page', 'series archive': 'archive',
        'generic homepage': 'publisher landing page', 'unavailable media': 'unavailable',
        'tracking wrapper': 'retired',
    }
    return aliases.get(detected, detected)


def preferred_destination_issue(record: dict[str, Any] | None) -> dict[str, Any] | None:
    if not record:
        return {'code': 'preferred_destination_missing', 'classification': 'unavailable'}
    classification = record.get('validationClassification') or classify_media_record(record)
    if classification != 'direct episode':
        return {
            'code': 'preferred_destination_not_episode_level',
            'classification': classification,
            'platform': record.get('platform'),
            'url': record.get('url'),
        }
    return None


def select_preferred(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [r for r in records if r.get('official') is True and r.get('approved', True) and r.get('published', True)]
    direct = [r for r in eligible if (r.get('validationClassification') or classify_media_record(r)) == 'direct episode']
    if not direct:
        return None
    return min(direct, key=lambda r: (r.get('preferredRank', 999), r.get('platform', ''), r.get('url', '')))


def cross_platform_consistency(records: list[dict[str, Any]]) -> dict[str, Any]:
    direct = [r for r in records if (r.get('validationClassification') or classify_media_record(r)) == 'direct episode']
    identities = {str((r.get('recoveryProvenance') or {}).get('confirmedEpisodeIdentity')) for r in direct if (r.get('recoveryProvenance') or {}).get('confirmedEpisodeIdentity')}
    if len(identities) > 1:
        return {'status': 'review_required', 'reason': 'cross_platform_episode_disagreement', 'identities': sorted(identities)}
    return {'status': 'consistent' if direct else 'not_applicable', 'confirmedIdentity': next(iter(identities), None)}


def complete_episode_media(entity: dict[str, Any], release: str = 'V23.5C.3', checked_at: str | None = None) -> dict[str, Any]:
    checked_at = checked_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    out = deepcopy(entity)
    records = out.setdefault('officialMedia', [])
    for record in records:
        classification = classify_media_record(record)
        record['validationClassification'] = classification
        if classification != 'direct episode':
            record['preferredRank'] = max(int(record.get('preferredRank', 90)), 90)
            record['secondaryOnly'] = True
        provenance = record.setdefault('validationProvenance', {})
        provenance.update({
            'release': release,
            'validatedAt': checked_at,
            'recoverySource': provenance.get('recoverySource') or 'retained_repository_record',
            'confidence': provenance.get('confidence') or ('high' if classification == 'direct episode' and record.get('verified') else 'medium'),
            'identitySignals': provenance.get('identitySignals') or (['platform_episode_identifier', 'repository_title', 'publication_date'] if classification == 'direct episode' else ['repository_url_classification']),
        })

    preferred = select_preferred(records)
    migration = out.setdefault('mediaMigration', {})
    migration['completionRelease'] = release
    migration['completionCheckedAt'] = checked_at
    migration['preferredCanonicalUrl'] = preferred.get('url') if preferred else None
    migration['preferredLabel'] = preferred.get('label') if preferred else None
    migration['preferredDestinationClassification'] = 'direct episode' if preferred else None
    migration['completionStatus'] = 'complete' if preferred else 'human_review_required'
    migration['manualReviewRequired'] = not bool(preferred)
    migration['crossPlatformConfirmation'] = cross_platform_consistency(records)
    migration['validationIssue'] = preferred_destination_issue(preferred)
    migration['existingDestinationsPreserved'] = True
    migration['fabricatedDestinations'] = 0
    return out
