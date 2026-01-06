# Deployment (DigitalOcean Droplet)

This repo is deployed manually to a DigitalOcean droplet (no git-driven deploys).
The droplet runs the CLI and scripts directly from a checked-out working copy.

## One-time setup
1. Copy the repo to the droplet (SCP/rsync).
2. Create the required virtual environment in-place:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Configure environment variables (the CLI reads `.env` automatically from the repo root):
   ```bash
   cp .env.example .env
   source .env
   ```
4. Install any system dependencies needed for video rendering (e.g., `ffmpeg`).

## Running the CLI pipeline
From the repo root:
```bash
source .venv/bin/activate
python -m tg_content_factory.cli init-db
python -m tg_content_factory.cli generate-ideas --count 3
python -m tg_content_factory.cli create-drafts 1 --templates "Lightning Lecture"
python -m tg_content_factory.cli list-pending
```

## Nightly idea job (optional)
The nightly ideas job uses the deterministic idea pipeline and `data/course_data.json`:
```bash
source .venv/bin/activate
python scripts/nightly_idea_job.py
```

If you want this on a schedule, use `cron` or systemd timers on the droplet,
pointing at the repo root and the `.venv/` Python interpreter.
