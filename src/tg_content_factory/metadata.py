"""SQLite-backed metadata store for clips and videos."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .data import AssetType, ClipMetadata, TimelineEntry, VideoArtifact, VideoManifest


class MetadataStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS clips (
                    clip_id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    source TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    license TEXT NOT NULL,
                    storage_uri TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    storage_uri TEXT NOT NULL,
                    manifest_uri TEXT NOT NULL,
                    timeline_json TEXT NOT NULL,
                    captions_json TEXT NOT NULL,
                    call_to_action TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def insert_clips(self, clips: Iterable[ClipMetadata]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO clips (
                    clip_id,
                    asset_type,
                    duration_seconds,
                    source,
                    prompt,
                    license,
                    storage_uri
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        clip.clip_id,
                        clip.asset_type.value,
                        clip.duration_seconds,
                        clip.source,
                        clip.prompt,
                        clip.license,
                        clip.storage_uri,
                    )
                    for clip in clips
                ],
            )
            conn.commit()

    def insert_video(self, video: VideoArtifact) -> None:
        timeline_payload = json.dumps(
            [
                {
                    "clip_id": entry.clip_id,
                    "start": entry.start_time_seconds,
                    "end": entry.end_time_seconds,
                    "storage_uri": entry.storage_uri,
                }
                for entry in video.manifest.timeline
            ]
        )
        captions_payload = json.dumps(video.manifest.captions)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO videos (
                    video_id,
                    storage_uri,
                    manifest_uri,
                    timeline_json,
                    captions_json,
                    call_to_action
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    video.video_id,
                    video.storage_uri,
                    video.manifest_uri,
                    timeline_payload,
                    captions_payload,
                    video.manifest.call_to_action,
                ),
            )
            conn.commit()

    def fetch_clips(self) -> list[ClipMetadata]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT clip_id, asset_type, duration_seconds, source, prompt, license, storage_uri FROM clips"
            ).fetchall()
        return [
            ClipMetadata(
                clip_id=row[0],
                asset_type=AssetType(row[1]),
                duration_seconds=row[2],
                source=row[3],
                prompt=row[4],
                license=row[5],
                storage_uri=row[6],
            )
            for row in rows
        ]

    def fetch_videos(self) -> list[VideoArtifact]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT video_id, storage_uri, manifest_uri, timeline_json, captions_json, call_to_action
                FROM videos
                """
            ).fetchall()
        videos = []
        for row in rows:
            timeline_entries = [
                TimelineEntry(
                    clip_id=entry["clip_id"],
                    start_time_seconds=entry["start"],
                    end_time_seconds=entry["end"],
                    storage_uri=entry["storage_uri"],
                )
                for entry in json.loads(row[3])
            ]
            manifest = VideoManifest(
                timeline=timeline_entries,
                captions=json.loads(row[4]),
                call_to_action=row[5],
            )
            videos.append(
                VideoArtifact(
                    video_id=row[0],
                    storage_uri=row[1],
                    manifest_uri=row[2],
                    manifest=manifest,
                )
            )
        return videos
