from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from tg_content_factory import db

DEFAULT_VENUES = ["youtube", "tiktok"]


def post_approved(db_path: str, venues: list[str]) -> list[int]:
    db.init_db(db_path)
    post_ids: list[int] = []
    with db.get_connection(db_path) as conn:
        drafts = conn.execute(
            "SELECT id FROM drafts WHERE status = ?",
            ("approved",),
        ).fetchall()
        for draft in drafts:
            for venue in venues:
                existing = conn.execute(
                    "SELECT id FROM posts WHERE draft_id = ? AND venue = ?",
                    (draft["id"], venue),
                ).fetchone()
                if existing:
                    continue
                cursor = conn.execute(
                    """
                    INSERT INTO posts (draft_id, venue, status, external_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        draft["id"],
                        venue,
                        "posted",
                        f"mock-{uuid4().hex}",
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                post_ids.append(cursor.lastrowid)
    return post_ids


def list_posts(db_path: str) -> list[dict[str, str]]:
    db.init_db(db_path)
    with db.get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, draft_id, venue, status, external_id, created_at FROM posts ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]
