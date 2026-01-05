"""Video assembly service for composing clips."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Iterable

from .data import AssemblyRequest, ClipMetadata, TimelineEntry, VideoArtifact, VideoManifest
from .metadata import MetadataStore
from .storage import ObjectStorage


class VideoAssembler:
    def __init__(self, storage: ObjectStorage, metadata_store: MetadataStore) -> None:
        self.storage = storage
        self.metadata_store = metadata_store

    def assemble(self, request: AssemblyRequest) -> VideoArtifact:
        timeline = self._build_timeline(request.clips)
        manifest = VideoManifest(
            timeline=timeline,
            captions=request.captions,
            call_to_action=request.call_to_action,
        )
        video_id = f"video_{uuid.uuid4().hex}"
        video_key = f"videos/{request.request_id}/{video_id}.mp4"
        video_payload = self._render_placeholder_video(manifest)
        storage_uri = self.storage.put_object(video_key, video_payload, "video/mp4")
        manifest_key = f"videos/{request.request_id}/{video_id}_manifest.json"
        manifest_uri = self.storage.put_json(manifest_key, _serialize_manifest(manifest))
        video = VideoArtifact(
            video_id=video_id,
            storage_uri=storage_uri,
            manifest_uri=manifest_uri,
            manifest=manifest,
        )
        self.metadata_store.insert_video(video)
        return video

    def _build_timeline(self, clips: Iterable[ClipMetadata]) -> list[TimelineEntry]:
        entries: list[TimelineEntry] = []
        cursor = 0.0
        for clip in clips:
            end_time = cursor + clip.duration_seconds
            entries.append(
                TimelineEntry(
                    clip_id=clip.clip_id,
                    start_time_seconds=cursor,
                    end_time_seconds=end_time,
                    storage_uri=clip.storage_uri,
                )
            )
            cursor = end_time
        return entries

    def _render_placeholder_video(self, manifest: VideoManifest) -> bytes:
        payload = {
            "generated_at": datetime.utcnow().isoformat(),
            "timeline": [asdict(entry) for entry in manifest.timeline],
            "captions": manifest.captions,
            "call_to_action": manifest.call_to_action,
        }
        return json.dumps(payload, indent=2).encode("utf-8")


def _serialize_manifest(manifest: VideoManifest) -> dict:
    return {
        "timeline": [asdict(entry) for entry in manifest.timeline],
        "captions": list(manifest.captions),
        "call_to_action": manifest.call_to_action,
    }
