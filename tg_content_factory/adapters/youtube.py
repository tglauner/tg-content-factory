"""YouTube venue adapter."""

from __future__ import annotations

from typing import Any, Dict

from tg_content_factory.adapters.base import ApiClient, AuthConfig, VenueAdapter
from tg_content_factory.models import PostPayload


class YouTubeAdapter(VenueAdapter):
    venue_name = "youtube"

    def __init__(self, api_key: str) -> None:
        client = ApiClient("https://api.youtube.local", AuthConfig(token=api_key))
        super().__init__(client)

    def format_payload(self, payload: PostPayload) -> Dict[str, Any]:
        return {
            "title": payload.title,
            "description": payload.description,
            "tags": payload.tags,
            "category": "Education",
            "video_url": payload.video_url,
        }
