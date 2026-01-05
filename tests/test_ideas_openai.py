import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


class OpenAIIdeaTests(unittest.TestCase):
    def test_generate_ideas_persists_openai_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/tg.db"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path.cwd())
            env["OPENAI_API_KEY"] = "test-key"
            env["TG_OPENAI_MOCK"] = "1"

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
                    "2",
                ],
                check=True,
                env=env,
                cwd=tmpdir,
            )

            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT prompt, generated_by, model FROM ideas ORDER BY id ASC LIMIT 1"
                ).fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row["generated_by"], "openai")
            self.assertEqual(row["model"], "gpt-5.2")


if __name__ == "__main__":
    unittest.main()
