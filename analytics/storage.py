from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class PerformanceMetric:
    venue: str
    post_id: str
    metric_date: date
    impressions: int
    clicks: int
    conversions: int
    content_type: str | None = None
    campaign: str | None = None


class TimeSeriesStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_schema(self, schema_path: str) -> None:
        with self._connect() as connection, open(schema_path, "r", encoding="utf-8") as handle:
            connection.executescript(handle.read())

    def upsert_metrics(self, metrics: Iterable[PerformanceMetric]) -> None:
        rows = [
            (
                metric.venue,
                metric.post_id,
                metric.metric_date.isoformat(),
                metric.impressions,
                metric.clicks,
                metric.conversions,
                metric.content_type,
                metric.campaign,
            )
            for metric in metrics
        ]
        if not rows:
            return
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO post_metrics (
                    venue,
                    post_id,
                    metric_date,
                    impressions,
                    clicks,
                    conversions,
                    content_type,
                    campaign
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(venue, post_id, metric_date)
                DO UPDATE SET
                    impressions = excluded.impressions,
                    clicks = excluded.clicks,
                    conversions = excluded.conversions,
                    content_type = excluded.content_type,
                    campaign = excluded.campaign,
                    updated_at = CURRENT_TIMESTAMP
                """,
                rows,
            )

    def upsert_daily_rollup(self, venue: str, metric_date: date) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                SELECT
                    COUNT(*) AS posts_count,
                    COALESCE(SUM(impressions), 0) AS impressions,
                    COALESCE(SUM(clicks), 0) AS clicks,
                    COALESCE(SUM(conversions), 0) AS conversions
                FROM post_metrics
                WHERE venue = ? AND metric_date = ?
                """,
                (venue, metric_date.isoformat()),
            )
            row = cursor.fetchone()
            if row is None:
                return
            impressions = int(row["impressions"])
            clicks = int(row["clicks"])
            ctr = (clicks / impressions) if impressions else 0
            connection.execute(
                """
                INSERT INTO daily_rollups (
                    venue,
                    metric_date,
                    posts_count,
                    impressions,
                    clicks,
                    conversions,
                    ctr
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(venue, metric_date)
                DO UPDATE SET
                    posts_count = excluded.posts_count,
                    impressions = excluded.impressions,
                    clicks = excluded.clicks,
                    conversions = excluded.conversions,
                    ctr = excluded.ctr,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    venue,
                    metric_date.isoformat(),
                    int(row["posts_count"]),
                    impressions,
                    clicks,
                    int(row["conversions"]),
                    ctr,
                ),
            )
