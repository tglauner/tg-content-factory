from __future__ import annotations

from tg_content_factory import content_db as db


def set_review_status(db_path: str, draft_id: int, status: str) -> bool:
    db.init_db(db_path)
    with db.get_connection(db_path) as conn:
        cursor = conn.execute(
            "UPDATE drafts SET status = ? WHERE id = ?",
            (status, draft_id),
        )
        return cursor.rowcount > 0


def list_pending_reviews(db_path: str) -> list[dict[str, str]]:
    return _list_by_status(db_path, "pending_review")


def _list_by_status(db_path: str, status: str) -> list[dict[str, str]]:
    db.init_db(db_path)
    with db.get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, idea_id, template_name, status, created_at FROM drafts WHERE status = ?",
            (status,),
        ).fetchall()
    return [dict(row) for row in rows]
