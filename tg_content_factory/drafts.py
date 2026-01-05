from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from tg_content_factory import content_db as db, templates
from tg_content_factory.openai_client import OpenAIClient
from tg_content_factory.video_renderer import VideoRenderer


def create_drafts(
    db_path: str,
    idea_ids: list[int],
    template_names: list[str],
    client: Optional[OpenAIClient] = None,
    renderer: Optional[VideoRenderer] = None,
) -> list[int]:
    db.init_db(db_path)
    draft_ids: list[int] = []
    openai_client = client or OpenAIClient.from_env()
    video_renderer = renderer or VideoRenderer.default()
    with db.get_connection(db_path) as conn:
        for idea_id in idea_ids:
            idea = conn.execute(
                "SELECT id, prompt FROM ideas WHERE id = ?", (idea_id,)
            ).fetchone()
            if not idea:
                continue
            for template_name in template_names:
                template = templates.get_template(template_name)
                content = openai_client.generate_script(idea["prompt"], template.description)
                video_path, preview_path = _render_video_assets(
                    video_renderer,
                    idea["id"],
                    template.name,
                    content,
                )
                cursor = conn.execute(
                    """
                    INSERT INTO drafts (
                        idea_id,
                        template_name,
                        content,
                        video_path,
                        preview_path,
                        status,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        idea["id"],
                        template.name,
                        content,
                        str(video_path),
                        str(preview_path),
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


def _render_video_assets(
    renderer: VideoRenderer,
    idea_id: int,
    template_name: str,
    content: str,
) -> tuple[Path, Path]:
    slug = template_name.lower().replace(" ", "-")
    output_dir = renderer.output_dir / f"idea_{idea_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / f"{slug}.mp4"
    preview_path = output_dir / f"{slug}.png"
    renderer.render_video(content, video_path)
    renderer.render_preview(video_path, preview_path)
    return video_path, preview_path


def list_drafts(db_path: str, status: str | None = None) -> list[dict[str, str]]:
    db.init_db(db_path)
    query = (
        "SELECT id, idea_id, template_name, status, created_at, video_path, preview_path "
        "FROM drafts"
    )
    params: list[str] = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY id DESC"
    with db.get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]
