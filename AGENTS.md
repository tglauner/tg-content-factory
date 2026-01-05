# Refactor Protocol (Codex)
Goal: remove Cursor-era/legacy leftovers, align architecture + docs, minimal behavior change.

Rules:
- Start by producing an INVENTORY + FINDINGS report before changing code.
- Prefer deletion over “keep but unused”. No legacy code should linger.
- Any deletion must be justified with (a) grep/ripgrep references, (b) import graph / usage check, (c) build/test run.
- Refactors must be minimal: no feature changes, no redesign, no new frameworks unless required.
- After changes: update docs so they match reality (DEPLOY.md, README, comments, env examples).
- Keep deploy behavior compatible with DigitalOcean droplet workflow (non-git-driven production).
- Every commit must be small and titled: "audit:", "delete:", "refactor:", "docs:", "chore:".
- Provide a final checklist of what was removed/changed and why.

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

