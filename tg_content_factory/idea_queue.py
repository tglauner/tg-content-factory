from __future__ import annotations

from .idea_db import IdeaRepository
from .idea_models import Idea


class AssetGenQueue:
    def __init__(self, repository: IdeaRepository) -> None:
        self._repository = repository

    def enqueue(self, idea: Idea) -> None:
        self._repository.enqueue_asset_generation(idea)
