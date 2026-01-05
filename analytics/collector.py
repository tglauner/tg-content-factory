from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol

from .storage import PerformanceMetric, TimeSeriesStore


@dataclass(frozen=True)
class VenueMetricRow:
    post_id: str
    impressions: int
    clicks: int
    conversions: int
    content_type: str | None = None
    campaign: str | None = None


class VenueAnalyticsClient(Protocol):
    name: str

    def get_metrics(self, metric_date: date) -> Iterable[VenueMetricRow]:
        """Fetch metrics for a specific venue and date."""


class AnalyticsCollector:
    def __init__(self, store: TimeSeriesStore) -> None:
        self.store = store

    def collect_for_date(
        self,
        metric_date: date,
        clients: Iterable[VenueAnalyticsClient],
    ) -> None:
        metrics: list[PerformanceMetric] = []
        for client in clients:
            metrics.extend(self._collect_for_client(client, metric_date))
        self.store.upsert_metrics(metrics)
        for client in clients:
            self.store.upsert_daily_rollup(client.name, metric_date)

    def _collect_for_client(
        self,
        client: VenueAnalyticsClient,
        metric_date: date,
    ) -> Iterable[PerformanceMetric]:
        rows = client.get_metrics(metric_date)
        for row in rows:
            yield PerformanceMetric(
                venue=client.name,
                post_id=row.post_id,
                metric_date=metric_date,
                impressions=row.impressions,
                clicks=row.clicks,
                conversions=row.conversions,
                content_type=row.content_type,
                campaign=row.campaign,
            )
