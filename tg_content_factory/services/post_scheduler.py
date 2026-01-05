"""Scheduler for posting windows and retries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from tg_content_factory.adapters.base import VenueAdapter
from tg_content_factory.db import Database
from tg_content_factory.models import PostPayload


@dataclass(frozen=True)
class PostingWindow:
    start_hour: int
    end_hour: int

    def next_available(self, requested: Optional[datetime] = None) -> datetime:
        current = requested or datetime.utcnow()
        window_start = current.replace(hour=self.start_hour, minute=0, second=0, microsecond=0)
        window_end = current.replace(hour=self.end_hour, minute=0, second=0, microsecond=0)
        if self.start_hour <= current.hour < self.end_hour:
            return current
        if current < window_start:
            return window_start
        return window_start + timedelta(days=1)


class PostScheduler:
    """Coordinates scheduled posts and retry attempts."""

    def __init__(
        self,
        db: Database,
        adapters: Dict[str, VenueAdapter],
        window: PostingWindow,
        max_retries: int = 3,
        retry_backoff: timedelta = timedelta(minutes=15),
    ) -> None:
        self.db = db
        self.adapters = adapters
        self.window = window
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

    def schedule_post(
        self, payload: PostPayload, venue: str, requested: Optional[datetime] = None
    ) -> int:
        if venue not in self.adapters:
            raise KeyError(f"Unknown venue {venue}")
        post_id = self.db.create_post(payload)
        scheduled_at = self.window.next_available(requested)
        self.db.create_submission(post_id, venue, "scheduled", 0, scheduled_at)
        return post_id

    def process_due_submissions(self, now: Optional[datetime] = None) -> None:
        current = now or datetime.utcnow()
        for submission in self.db.list_pending_submissions(current):
            self._attempt_submission(submission)

    def _attempt_submission(self, submission: dict) -> None:
        submission_id = submission["id"]
        post_id = submission["post_id"]
        venue = submission["venue"]
        attempt = submission["attempt"]
        payload = self.db.get_post_payload(post_id)
        adapter = self.adapters[venue]
        try:
            adapter.submit(payload)
            self.db.update_submission(submission_id, "submitted")
        except Exception as exc:  # pragma: no cover - placeholder for integration errors
            if attempt + 1 > self.max_retries:
                self.db.update_submission(submission_id, "failed", str(exc))
                return
            next_time = self.window.next_available(datetime.utcnow() + self.retry_backoff)
            self.db.update_submission(submission_id, "retry_scheduled", str(exc))
            self.db.create_submission(post_id, venue, "retry_scheduled", attempt + 1, next_time)
