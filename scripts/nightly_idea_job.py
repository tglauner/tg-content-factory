from __future__ import annotations

import json
from pathlib import Path

from src.db import IdeaRepository
from src.idea_service import IdeaService
from src.queue import AssetGenQueue


def load_config(config_path: Path) -> dict[str, list[str]]:
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    config_path = Path(__file__).resolve().parent.parent / "data" / "course_data.json"
    config = load_config(config_path)
    repository = IdeaRepository(db_path=str(Path("data") / "ideas.db"))
    queue = AssetGenQueue(repository)
    service = IdeaService(repository, queue)
    service.generate_and_enqueue(
        themes=config["themes"],
        recent_keywords=config["recent_keywords"],
        trend_signals=config["trend_signals"],
        recent_topics=config["recent_topics"],
    )


if __name__ == "__main__":
    main()
