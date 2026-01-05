import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


class DraftVideoTests(unittest.TestCase):
    def test_create_drafts_writes_video_and_preview_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/tg.db"
            output_dir = f"{tmpdir}/renders"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path.cwd())
            env["OPENAI_API_KEY"] = "test-key"
            env["TG_OPENAI_MOCK"] = "1"
            env["TG_VIDEO_RENDER_MODE"] = "mock"
            env["TG_VIDEO_OUTPUT"] = output_dir

            subprocess.run(
                [
                    "python",
                    "-m",
                    "tg_content_factory.cli",
                    "--db",
                    db_path,
                    "init-db",
                ],
                check=True,
                env=env,
                cwd=tmpdir,
            )
            subprocess.run(
                [
                    "python",
                    "-m",
                    "tg_content_factory.cli",
                    "--db",
                    db_path,
                    "generate-ideas",
                    "--count",
                    "1",
                ],
                check=True,
                env=env,
                cwd=tmpdir,
            )
            subprocess.run(
                [
                    "python",
                    "-m",
                    "tg_content_factory.cli",
                    "--db",
                    db_path,
                    "create-drafts",
                    "1",
                    "--templates",
                    "Lightning Lecture",
                ],
                check=True,
                env=env,
                cwd=tmpdir,
            )

            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT video_path, preview_path FROM drafts ORDER BY id ASC LIMIT 1"
                ).fetchone()

            self.assertIsNotNone(row)
            self.assertTrue(Path(row["video_path"]).exists())
            self.assertTrue(Path(row["preview_path"]).exists())


if __name__ == "__main__":
    unittest.main()
