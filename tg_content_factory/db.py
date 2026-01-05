"""SQLite-backed storage for posts and submission attempts."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from typing import Iterable, Optional

from tg_content_factory.models import PostPayload, normalize_post_payload


class Database:
    """Simple SQLite database wrapper."""

    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                venue TEXT NOT NULL,
                status TEXT NOT NULL,
                attempt INTEGER NOT NULL,
                scheduled_at TEXT NOT NULL,
                last_error TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(post_id) REFERENCES posts(id)
            );
            """
        )
        self._conn.commit()

    def create_post(self, payload: PostPayload) -> int:
        normalized = normalize_post_payload(payload)
        payload_json = json.dumps(asdict(normalized))
        created_at = datetime.utcnow().isoformat()
        cursor = self._conn.execute(
            "INSERT INTO posts (payload_json, created_at) VALUES (?, ?)",
            (payload_json, created_at),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def get_post_payload(self, post_id: int) -> PostPayload:
        row = self._conn.execute(
            "SELECT payload_json FROM posts WHERE id = ?", (post_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown post id {post_id}")
        data = json.loads(row["payload_json"])
        return PostPayload(**data)

    def create_submission(
        self, post_id: int, venue: str, status: str, attempt: int, scheduled_at: datetime
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO submissions (
                post_id, venue, status, attempt, scheduled_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                venue,
                status,
                attempt,
                scheduled_at.isoformat(),
                datetime.utcnow().isoformat(),
            ),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def update_submission(
        self, submission_id: int, status: str, last_error: Optional[str] = None
    ) -> None:
        self._conn.execute(
            """
            UPDATE submissions
            SET status = ?, last_error = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, last_error, datetime.utcnow().isoformat(), submission_id),
        )
        self._conn.commit()

    def list_pending_submissions(self, now: datetime) -> Iterable[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT * FROM submissions
            WHERE status IN ('scheduled', 'retry_scheduled')
            AND scheduled_at <= ?
            ORDER BY scheduled_at ASC
            """,
            (now.isoformat(),),
        ).fetchall()

    def get_submission(self, submission_id: int) -> sqlite3.Row:
        row = self._conn.execute(
            "SELECT * FROM submissions WHERE id = ?", (submission_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown submission id {submission_id}")
        return row
