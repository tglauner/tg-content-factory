# AGENTS.md — tg-content-factory (Project)

## Non-negotiables
- Single host: use the existing DO droplet that serves tglauner.com.
- DB: PostgreSQL runs locally on that droplet (no Neon/managed DB).
- No extra worker droplet.
- Tim does not hand-write code. Only allowed manual actions:
  1) drop lecture files into content/lectures/
  2) run provided make commands
  3) approve edits in the editor
- Python venv MUST be .venv/ (always).
- content/lectures is READ-ONLY (never modify/rename user files).

## Directories
- Input: content/lectures/
- Extracted: content/extracted/
- Manifests: content/manifests/
- Droplet storage (MVP):
  - /var/www/html/studio_storage/assets/
  - /var/www/html/studio_storage/renders/
  - /var/www/html/studio_storage/logs/
- Retention (default): keep renders 30 days; keep metadata indefinitely.

## MVP nightly pipeline
1) ingest: hash/index content/lectures → DB + manifest
2) extract: normalize text → content/extracted + DB
3) plan: pick 1–3 angles from extracted content
4) write: script + 2–3 hooks + captions + CTA + UTM link
5) render: ffmpeg template → MP4 + SRT + PNG thumbnail
6) publish: either export-ready bundle OR post to 1 venue (config-driven)
7) measure: store UTM + import basic metrics when available

## Output formats (defaults)
- Video: MP4 (H.264 + AAC), primary 9:16 (1080×1920)
- Captions: SRT (optional VTT)
- Thumbnail: PNG
- Post bundle: JSON (title/caption/hashtags/CTA/UTM/venue targets)

## Reliability + dashboard
- Every step writes job status + log path to DB (idempotent, retry-safe).
- Failures must be visible in a protected dashboard on tglauner.com at /studio
  showing jobs, generated videos, publish status, and last-7-days performance.

## Required Make targets
setup, dev, test, lint, ingest_now, render_sample, run_nightly
(plus DEPLOY.md with copy/paste droplet deploy steps)

