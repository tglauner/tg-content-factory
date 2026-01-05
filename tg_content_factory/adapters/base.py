"""Base adapter definitions for external venues."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from tg_content_factory.models import PostPayload


@dataclass(frozen=True)
class AuthConfig:
    token: str


class ApiClient:
    """Minimal API client placeholder."""

    def __init__(self, base_url: str, auth: AuthConfig) -> None:
        self.base_url = base_url
        self.auth = auth

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate API post call."""
        return {
            "endpoint": f"{self.base_url}{path}",
            "payload": payload,
            "token": self.auth.token,
        }


class VenueAdapter:
    """Interface for venue integrations."""

    venue_name: str

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def format_payload(self, payload: PostPayload) -> Dict[str, Any]:
        raise NotImplementedError

    def submit(self, payload: PostPayload) -> Dict[str, Any]:
        formatted = self.format_payload(payload)
        return self.client.post("/posts", formatted)
