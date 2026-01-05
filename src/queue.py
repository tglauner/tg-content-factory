from __future__ import annotations

from .db import IdeaRepository
from .models import Idea


class AssetGenQueue:
    def __init__(self, repository: IdeaRepository) -> None:
        self._repository = repository

    def enqueue(self, idea: Idea) -> None:
        self._repository.enqueue_asset_generation(idea)
