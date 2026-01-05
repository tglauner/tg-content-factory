"""Twitter/X venue adapter."""

from __future__ import annotations

from typing import Any, Dict

from tg_content_factory.adapters.base import ApiClient, AuthConfig, VenueAdapter
from tg_content_factory.models import PostPayload


class TwitterAdapter(VenueAdapter):
    venue_name = "twitter"

    def __init__(self, bearer_token: str) -> None:
        client = ApiClient("https://api.twitter.local", AuthConfig(token=bearer_token))
        super().__init__(client)

    def format_payload(self, payload: PostPayload) -> Dict[str, Any]:
        hashtags = " ".join(f"#{tag.lstrip('#')}" for tag in payload.hashtags)
        text_parts = [payload.title, payload.description, hashtags]
        text = "\n".join(part for part in text_parts if part)
        return {
            "text": text,
            "tags": payload.tags,
            "video_url": payload.video_url,
        }
