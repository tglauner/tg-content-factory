from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from tg_content_factory import db
from tg_content_factory.openai_client import OpenAIClient


def generate_ideas(
    db_path: str, count: int, client: Optional[OpenAIClient] = None
) -> list[int]:
    db.init_db(db_path)
    created_ids: list[int] = []
    openai_client = client or OpenAIClient.from_env()
    prompts = openai_client.generate_ideas(count)
    with db.get_connection(db_path) as conn:
        for prompt in prompts:
            cursor = conn.execute(
                """
                INSERT INTO ideas (created_at, prompt, status, generated_by, model)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    prompt,
                    "new",
                    "openai",
                    openai_client.model,
                ),
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
