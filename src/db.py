from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .models import Idea


class IdeaRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    trends TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    engagement REAL NOT NULL,
                    novelty REAL NOT NULL,
                    venue_fit REAL NOT NULL,
                    total_score REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS asset_gen_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idea_title TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save_idea(self, idea: Idea) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO ideas (
                    title,
                    description,
                    theme,
                    keywords,
                    trends,
                    created_at,
                    engagement,
                    novelty,
                    venue_fit,
                    total_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    idea.title,
                    idea.description,
                    idea.theme,
                    json.dumps(idea.keywords),
                    json.dumps(idea.trends),
                    idea.created_at.isoformat(),
                    idea.score.engagement,
                    idea.score.novelty,
                    idea.score.venue_fit,
                    idea.score.total,
                ),
            )
            return int(cursor.lastrowid)

    def enqueue_asset_generation(self, idea: Idea) -> None:
        payload = json.dumps(asdict(idea), default=_json_serializer)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO asset_gen_queue (idea_title, payload, created_at)
                VALUES (?, ?, ?)
                """,
                (idea.title, payload, datetime.utcnow().isoformat()),
            )


def _json_serializer(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unsupported type: {type(value)!r}")
