# AGENTS.md — tg-content-factory (Project)

## Non-negotiables
- Python venv MUST be .venv/ (always).
- content/lectures is READ-ONLY (never modify/rename user files).

## Directories

## MVP nightly pipeline

## Output formats (defaults)
- Video: MP4 (H.264 + AAC), primary 9:16 (1080×1920)
- Captions: SRT (optional VTT)
- Thumbnail: PNG

## Reliability + dashboard
- Every step writes job status + log path to DB (idempotent, retry-safe).
- Failures must be visible in a protected dashboard on tglauner.com at /studio
  showing jobs, generated videos, publish status, and last-7-days performance.

