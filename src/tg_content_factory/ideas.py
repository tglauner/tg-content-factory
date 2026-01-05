from __future__ import annotations

import random
from datetime import datetime, timezone

from tg_content_factory import db

TOPICS = [
    "Build better habits with tiny experiments",
    "Explain recursion with a real-world metaphor",
    "How to map a lecture into a 60-second script",
    "Turn a Q&A into an engaging clip",
    "Designing slide decks for quick comprehension",
]


def generate_ideas(db_path: str, count: int) -> list[int]:
    db.init_db(db_path)
    created_ids: list[int] = []
    with db.get_connection(db_path) as conn:
        for _ in range(count):
            prompt = random.choice(TOPICS)
            cursor = conn.execute(
                "INSERT INTO ideas (created_at, prompt, status) VALUES (?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), prompt, "new"),
            )
            created_ids.append(cursor.lastrowid)
    return created_ids


def list_ideas(db_path: str) -> list[dict[str, str]]:
    db.init_db(db_path)
    with db.get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, created_at, prompt, status FROM ideas ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]
