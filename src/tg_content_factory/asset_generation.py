"""Asset generation service for b-roll, text overlays, and stock clips."""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from .data import AssetGenerationRequest, ClipMetadata
from .metadata import MetadataStore
from .storage import ObjectStorage


class AssetGenService:
    def __init__(self, storage: ObjectStorage, metadata_store: MetadataStore) -> None:
        self.storage = storage
        self.metadata_store = metadata_store

    def generate_assets(self, request: AssetGenerationRequest) -> list[ClipMetadata]:
        clips: list[ClipMetadata] = []
        for item in request.items:
            clip_id = f"clip_{uuid.uuid4().hex}"
            payload = {
                "clip_id": clip_id,
                "asset_type": item.asset_type.value,
                "prompt": item.prompt,
                "duration_seconds": item.duration_seconds,
                "license": item.license,
                "source": item.source,
                "generated_at": datetime.utcnow().isoformat(),
            }
            blob, content_type = _render_placeholder_payload(item.asset_type.value, payload)
            key = f"assets/{request.request_id}/{clip_id}.bin"
            storage_uri = self.storage.put_object(key, blob, content_type)
            clip = ClipMetadata(
                clip_id=clip_id,
                asset_type=item.asset_type,
                duration_seconds=item.duration_seconds,
                source=item.source,
                prompt=item.prompt,
                license=item.license,
                storage_uri=storage_uri,
            )
            clips.append(clip)
        self.metadata_store.insert_clips(clips)
        return clips


def _render_placeholder_payload(asset_type: str, payload: dict) -> tuple[bytes, str]:
    if asset_type == "text_overlay":
        svg = (
            "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1280\" height=\"720\">"
            "<rect width=\"100%\" height=\"100%\" fill=\"black\"/>"
            "<text x=\"50%\" y=\"50%\" fill=\"white\" font-size=\"36\" text-anchor=\"middle\">"
            f"{payload['prompt']}"
            "</text>"
            "</svg>"
        )
        return svg.encode("utf-8"), "image/svg+xml"
    payload_bytes = json.dumps(payload, indent=2).encode("utf-8")
    return payload_bytes, "application/json"
