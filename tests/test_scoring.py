import unittest

from src.scoring import score_idea


class ScoreIdeaTests(unittest.TestCase):
    def test_scores_are_deterministic_and_rounded(self) -> None:
        breakdown = score_idea(
            theme="AI",
            keywords=["LLM", "Scale"],
            trends=["LLM", "Video"],
            recent_topics=["ai", "llm", "growth"],
        )

        self.assertEqual(breakdown.engagement, 2.8)
        self.assertEqual(breakdown.novelty, 4.2)
        self.assertEqual(breakdown.venue_fit, 3.3)


if __name__ == "__main__":
    unittest.main()
