# TG Content Factory Architecture

## Overview
This repository contains two small pipelines plus supporting utilities:
- **CLI content pipeline** for OpenAI idea generation, drafts, review, posting, and analytics.
- **Idea scoring pipeline** for deterministic idea generation + enqueueing.
- **Posting scheduler** for venue submissions (used by tests and adapters).

## Modules / Services
### CLI content pipeline
- `tg_content_factory/cli.py` (entrypoint via `python -m tg_content_factory.cli`)
- `tg_content_factory/content_db.py` (SQLite schema for ideas/drafts/posts/analytics)
- `tg_content_factory/ideas.py`, `drafts.py`, `review.py`, `venues.py`, `analytics.py`
- `tg_content_factory/openai_client.py`, `templates.py`, `video_renderer.py`

### Idea scoring pipeline
- `tg_content_factory/idea_service.py` (build + enqueue ideas)
- `tg_content_factory/idea_db.py`, `idea_models.py`, `idea_queue.py`, `idea_scoring.py`
- Script entrypoint: `scripts/nightly_idea_job.py`

### Posting scheduler + adapters
- `tg_content_factory/db.py`, `models.py`
- `tg_content_factory/services/post_scheduler.py`
- `tg_content_factory/adapters/` (Twitter/X, YouTube mock adapters)

### Frontend (static)
- `frontend/dashboard.html` (static mockup; no server wiring)
