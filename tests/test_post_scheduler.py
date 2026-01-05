import unittest
from datetime import datetime, timedelta

from tg_content_factory.db import Database
from tg_content_factory.models import PostPayload
from tg_content_factory.services.post_scheduler import PostScheduler, PostingWindow


class FakeAdapter:
    def __init__(self) -> None:
        self.submissions = []

    def submit(self, payload: PostPayload) -> None:
        self.submissions.append(payload)


class PostSchedulerTests(unittest.TestCase):
    def test_schedule_post_creates_submission(self) -> None:
        db = Database()
        adapter = FakeAdapter()
        window = PostingWindow(start_hour=9, end_hour=17)
        scheduler = PostScheduler(db, {"youtube": adapter}, window)

        payload = PostPayload(title="Hello", description="World")
        requested = datetime(2024, 1, 1, 10, 0, 0)
        post_id = scheduler.schedule_post(payload, "youtube", requested=requested)

        submission = db.get_submission(1)
        self.assertEqual(submission["post_id"], post_id)
        self.assertEqual(submission["status"], "scheduled")

    def test_process_due_submissions_calls_adapter(self) -> None:
        db = Database()
        adapter = FakeAdapter()
        window = PostingWindow(start_hour=9, end_hour=17)
        scheduler = PostScheduler(db, {"youtube": adapter}, window)

        payload = PostPayload(title="Hello", description="World")
        requested = datetime(2024, 1, 1, 10, 0, 0)
        scheduler.schedule_post(payload, "youtube", requested=requested)

        scheduler.process_due_submissions(now=requested + timedelta(minutes=1))

        self.assertEqual(len(adapter.submissions), 1)
        submission = db.get_submission(1)
        self.assertEqual(submission["status"], "submitted")

    def test_schedule_post_unknown_venue_raises(self) -> None:
        db = Database()
        window = PostingWindow(start_hour=9, end_hour=17)
        scheduler = PostScheduler(db, {}, window)

        payload = PostPayload(title="Hello", description="World")
        with self.assertRaises(KeyError):
            scheduler.schedule_post(payload, "unknown")


if __name__ == "__main__":
    unittest.main()
