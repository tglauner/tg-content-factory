import unittest

from tg_content_factory.models import PostPayload, normalize_post_payload


class PostPayloadTests(unittest.TestCase):
    def test_normalize_post_payload_strips_and_filters(self) -> None:
        payload = PostPayload(
            title="  Daily Lesson ",
            description="  Learn fast  ",
            tags=["  video ", "", "marketing"],
            hashtags=["  #ai", "   ", "#course"],
            video_url="  https://example.com/video.mp4 ",
        )

        normalized = normalize_post_payload(payload)

        self.assertEqual(normalized.title, "Daily Lesson")
        self.assertEqual(normalized.description, "Learn fast")
        self.assertEqual(normalized.tags, ["video", "marketing"])
        self.assertEqual(normalized.hashtags, ["#ai", "#course"])
        self.assertEqual(normalized.video_url, "https://example.com/video.mp4")


if __name__ == "__main__":
    unittest.main()
