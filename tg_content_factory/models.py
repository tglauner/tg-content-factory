"""Domain models for content payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class PostPayload:
    """Normalized payload for posting to venues."""

    title: str
    description: str
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    video_url: Optional[str] = None


def _normalize_list(values: Iterable[str]) -> List[str]:
    normalized = []
    for value in values:
        cleaned = value.strip()
        if not cleaned:
            continue
        normalized.append(cleaned)
    return normalized


def normalize_post_payload(payload: PostPayload) -> PostPayload:
    """Normalize payload fields for consistent storage and delivery."""

    tags = _normalize_list(payload.tags)
    hashtags = _normalize_list(payload.hashtags)
    return PostPayload(
        title=payload.title.strip(),
        description=payload.description.strip(),
        tags=tags,
        hashtags=hashtags,
        video_url=payload.video_url.strip() if payload.video_url else None,
    )
