from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ScoreBreakdown:
    engagement: float
    novelty: float
    venue_fit: float


def score_idea(
    *,
    theme: str,
    keywords: Iterable[str],
    trends: Iterable[str],
    recent_topics: Iterable[str],
) -> ScoreBreakdown:
    keyword_list = [word.lower() for word in keywords]
    trend_list = [trend.lower() for trend in trends]
    recent_list = [topic.lower() for topic in recent_topics]

    overlap = set(keyword_list) & set(trend_list)
    engagement = min(5.0, 1.0 + len(overlap) * 1.2 + len(trend_list) * 0.3)

    recency_counts = Counter(recent_list)
    novelty_penalty = sum(recency_counts[word] for word in keyword_list if word in recency_counts)
    novelty = max(0.5, 5.0 - novelty_penalty * 0.8)

    venue_fit = 2.5 + (0.2 if theme.lower() in recent_list else 0.0) + min(2.5, len(keyword_list) * 0.3)

    return ScoreBreakdown(
        engagement=round(engagement, 3),
        novelty=round(novelty, 3),
        venue_fit=round(venue_fit, 3),
    )
