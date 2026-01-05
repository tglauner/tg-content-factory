"""Data models for asset generation and video assembly."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Optional


class AssetType(str, Enum):
    B_ROLL = "b_roll"
    TEXT_OVERLAY = "text_overlay"
    STOCK_CLIP = "stock_clip"


@dataclass(frozen=True)
class AssetGenerationItem:
    asset_type: AssetType
    prompt: str
    duration_seconds: float
    license: str
    source: str


@dataclass(frozen=True)
class AssetGenerationRequest:
    request_id: str
    items: List[AssetGenerationItem]


@dataclass(frozen=True)
class ClipMetadata:
    clip_id: str
    asset_type: AssetType
    duration_seconds: float
    source: str
    prompt: str
    license: str
    storage_uri: str


@dataclass(frozen=True)
class TimelineEntry:
    clip_id: str
    start_time_seconds: float
    end_time_seconds: float
    storage_uri: str


@dataclass(frozen=True)
class VideoManifest:
    timeline: List[TimelineEntry]
    captions: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None


@dataclass(frozen=True)
class AssemblyRequest:
    request_id: str
    clips: Iterable[ClipMetadata]
    captions: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None


@dataclass(frozen=True)
class VideoArtifact:
    video_id: str
    storage_uri: str
    manifest_uri: str
    manifest: VideoManifest
