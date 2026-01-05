import sqlite3
import tempfile
import unittest

from src.db import IdeaRepository
from src.idea_service import IdeaService
from src.queue import AssetGenQueue


class IdeaServiceTests(unittest.TestCase):
    def test_generate_and_enqueue_persists_idea_and_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/ideas.db"
            repository = IdeaRepository(db_path)
            queue = AssetGenQueue(repository)
            service = IdeaService(repository, queue)

            ideas = service.generate_and_enqueue(
                themes=["Automation"],
                recent_keywords=["Workflow", "Pipeline"],
                trend_signals=["AI"],
                recent_topics=["automation", "marketing"],
            )

            self.assertEqual(len(ideas), 1)

            with sqlite3.connect(db_path) as conn:
                idea_row = conn.execute("SELECT title, theme FROM ideas").fetchone()
                queue_row = conn.execute("SELECT idea_title FROM asset_gen_queue").fetchone()

            self.assertIsNotNone(idea_row)
            self.assertEqual(idea_row[1], "Automation")
            self.assertIsNotNone(queue_row)
            self.assertEqual(queue_row[0], ideas[0].title)


if __name__ == "__main__":
    unittest.main()
