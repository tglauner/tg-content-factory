from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class IdeaScore:
    engagement: float
    novelty: float
    venue_fit: float

    @property
    def total(self) -> float:
        return round(self.engagement + self.novelty + self.venue_fit, 4)


@dataclass(frozen=True)
class Idea:
    title: str
    description: str
    theme: str
    keywords: tuple[str, ...]
    trends: tuple[str, ...]
    created_at: datetime
    score: IdeaScore

    @classmethod
    def from_inputs(
        cls,
        *,
        title: str,
        description: str,
        theme: str,
        keywords: Iterable[str],
        trends: Iterable[str],
        created_at: datetime,
        score: IdeaScore,
    ) -> "Idea":
        return cls(
            title=title,
            description=description,
            theme=theme,
            keywords=tuple(keywords),
            trends=tuple(trends),
            created_at=created_at,
            score=score,
        )
