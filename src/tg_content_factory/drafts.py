from __future__ import annotations

from datetime import datetime, timezone

from tg_content_factory import db, templates


def create_drafts(db_path: str, idea_ids: list[int], template_names: list[str]) -> list[int]:
    db.init_db(db_path)
    draft_ids: list[int] = []
    with db.get_connection(db_path) as conn:
        for idea_id in idea_ids:
            idea = conn.execute(
                "SELECT id, prompt FROM ideas WHERE id = ?", (idea_id,)
            ).fetchone()
            if not idea:
                continue
            for template_name in template_names:
                template = templates.get_template(template_name)
                content = template.render(idea["prompt"])
                cursor = conn.execute(
                    """
                    INSERT INTO drafts (idea_id, template_name, content, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        idea["id"],
                        template.name,
                        content,
                        "pending_review",
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                draft_ids.append(cursor.lastrowid)
            conn.execute(
                "UPDATE ideas SET status = ? WHERE id = ?",
                ("drafted", idea["id"]),
            )
    return draft_ids


def list_drafts(db_path: str, status: str | None = None) -> list[dict[str, str]]:
    db.init_db(db_path)
    query = "SELECT id, idea_id, template_name, status, created_at FROM drafts"
    params: list[str] = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY id DESC"
    with db.get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]
