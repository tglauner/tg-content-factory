# tg-content-factory

Content generation for lectures and automated postings.

## Overview
This repository includes the early-stage services and models for:
- Idea generation and scoring
- Queueing assets for generation
- Normalized post payloads and scheduling logic

## Install on a Mac mini (first-time setup)

### 1) Prerequisites
- macOS with Command Line Tools installed: `xcode-select --install`
- Python 3.10+ (recommended: 3.11 or newer)
- ffmpeg for video rendering: `brew install ffmpeg`

### 2) Clone the repo
```bash
git clone <YOUR_REPO_URL>
cd tg-content-factory
```

All commands below assume you're running from the repo root so the local
`tg_content_factory` package is on the Python import path.

### 3) Create the required virtual environment
> **Important:** The project expects the virtual environment folder to be `.venv/`.
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4) Configure OpenAI access
Create a local `.env` file (ignored by git) from the example and load it into your shell:
```bash
cp .env.example .env
source .env
```

Set your OpenAI API key (GPT-5.2 is the default model):
```bash
export OPENAI_API_KEY="your-key-here"
export OPENAI_MODEL="gpt-5.2"
```

Optional video output settings:
```bash
export TG_VIDEO_OUTPUT="data/renders"
export TG_VIDEO_FONT="/System/Library/Fonts/Supplemental/Arial.ttf"
```

## Generate ideas, scripts, and videos (local flow)
```bash
python -m tg_content_factory.cli init-db
python -m tg_content_factory.cli generate-ideas --count 2
python -m tg_content_factory.cli list-ideas
python -m tg_content_factory.cli create-drafts 1 --templates "Lightning Lecture"
python -m tg_content_factory.cli list-drafts
```

Drafts include `video_path` and `preview_path` for review. Open the preview image
or play the MP4 before approving.

```bash
python -m tg_content_factory.cli list-pending
python -m tg_content_factory.cli review 1 --approve
python -m tg_content_factory.cli post-approved
```

## Run the test suite (initial + regression testing)

All tests are designed to run locally with the standard library (no extra deps).

```bash
python -m unittest discover -s tests -p "test_*.py"
```

To run tests without hitting the OpenAI API or ffmpeg, use the mock toggles:
```bash
export TG_OPENAI_MOCK=1
export TG_VIDEO_RENDER_MODE=mock
python -m unittest discover -s tests -p "test_*.py"
```

## Quick sanity check (optional)
You can run a quick idea-generation run from the Python REPL:

```bash
python
```

```python
from tg_content_factory.idea_db import IdeaRepository
from tg_content_factory.idea_queue import AssetGenQueue
from tg_content_factory.idea_service import IdeaService

repo = IdeaRepository("data/ideas.db")
service = IdeaService(repo, AssetGenQueue(repo))
ideas = service.generate_and_enqueue(
    themes=["Course Marketing"],
    recent_keywords=["CTA", "Funnels"],
    trend_signals=["AI", "Shorts"],
    recent_topics=["course", "marketing"],
)
print(ideas[0].title)
```

## Test coverage (what is included)
- **Scoring logic** (deterministic scoring outputs)
- **Idea service** (persistence + enqueue behavior)
- **OpenAI idea generation** (stores model metadata)
- **Post payload normalization** (tags/hashtags cleanup)
- **Post scheduler** (submission lifecycle + venue validation)
- **Draft video generation** (video + preview assets stored per draft)

## Notes
- SQLite is used locally for lightweight storage.
- The `tests/` folder is intended to grow as regression coverage expands.
- Deployment notes live in [`DEPLOY.md`](DEPLOY.md).
