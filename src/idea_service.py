from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .db import IdeaRepository
from .models import Idea, IdeaScore
from .queue import AssetGenQueue
from .scoring import score_idea


class IdeaService:
    def __init__(self, repository: IdeaRepository, queue: AssetGenQueue) -> None:
        self._repository = repository
        self._queue = queue

    def generate_and_enqueue(
        self,
        *,
        themes: Iterable[str],
        recent_keywords: Iterable[str],
        trend_signals: Iterable[str],
        recent_topics: Iterable[str],
    ) -> list[Idea]:
        ideas: list[Idea] = []
        for theme in themes:
            idea = self._build_idea(
                theme=theme,
                recent_keywords=recent_keywords,
                trend_signals=trend_signals,
                recent_topics=recent_topics,
            )
            self._repository.save_idea(idea)
            self._queue.enqueue(idea)
            ideas.append(idea)
        return ideas

    def _build_idea(
        self,
        *,
        theme: str,
        recent_keywords: Iterable[str],
        trend_signals: Iterable[str],
        recent_topics: Iterable[str],
    ) -> Idea:
        keywords = tuple(recent_keywords)
        trends = tuple(trend_signals)
        score_breakdown = score_idea(
            theme=theme,
            keywords=keywords,
            trends=trends,
            recent_topics=recent_topics,
        )
        score = IdeaScore(
            engagement=score_breakdown.engagement,
            novelty=score_breakdown.novelty,
            venue_fit=score_breakdown.venue_fit,
        )
        created_at = datetime.utcnow()
        title = f"{theme}: {keywords[0] if keywords else 'Fresh Topic'}"
        description = (
            f"Explore {theme} with focus on {', '.join(keywords[:3]) or 'emerging themes'} "
            f"and trending signals like {', '.join(trends[:2]) or 'industry shifts'}."
        )
        return Idea.from_inputs(
            title=title,
            description=description,
            theme=theme,
            keywords=keywords,
            trends=trends,
            created_at=created_at,
            score=score,
        )
