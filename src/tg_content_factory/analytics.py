from __future__ import annotations

from datetime import datetime, timezone

from tg_content_factory import db


def record_metrics(db_path: str, post_id: int, views: int, clicks: int) -> int:
    db.init_db(db_path)
    with db.get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO analytics (post_id, views, clicks, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (post_id, views, clicks, datetime.now(timezone.utc).isoformat()),
        )
        return cursor.lastrowid


def list_metrics(db_path: str) -> list[dict[str, str]]:
    db.init_db(db_path)
    with db.get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                analytics.id,
                analytics.post_id,
                posts.venue,
                posts.status,
                analytics.views,
                analytics.clicks,
                analytics.updated_at
            FROM analytics
            JOIN posts ON posts.id = analytics.post_id
            ORDER BY analytics.updated_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]
