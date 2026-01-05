from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoRenderer:
    output_dir: Path
    font_path: Path

    @classmethod
    def default(cls) -> "VideoRenderer":
        output_dir = Path(os.getenv("TG_VIDEO_OUTPUT", "data/renders"))
        if os.getenv("TG_VIDEO_RENDER_MODE") == "mock":
            return MockVideoRenderer(output_dir=output_dir)
        font_path = Path(
            os.getenv(
                "TG_VIDEO_FONT",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
            )
        )
        return cls(output_dir=output_dir, font_path=font_path)

    def render_video(self, script: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        escaped_script = script.replace(":", "\\:").replace("'", "\\'")
        command = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=1080x1920:d=12",
            "-vf",
            (
                "drawtext="
                f"fontfile={self.font_path}:"
                "fontsize=42:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:"
                f"text='{escaped_script}'"
            ),
            "-r",
            "30",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
        subprocess.run(command, check=True)

    def render_preview(self, video_path: Path, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-ss",
            "00:00:01.000",
            "-vframes",
            "1",
            str(output_path),
        ]
        subprocess.run(command, check=True)


@dataclass(frozen=True)
class MockVideoRenderer(VideoRenderer):
    font_path: Path = Path("")

    def render_video(self, script: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(script)

    def render_preview(self, video_path: Path, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"preview for {video_path.name}")
