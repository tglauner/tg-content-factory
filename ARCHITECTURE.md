# TG Content Factory Architecture

## Overview
This document defines the core modules/services and how they coordinate to generate, assemble, and schedule content for tglauner.com.

## Modules / Services

### IdeaService
**Purpose:** Generate and curate content ideas per channel or campaign.
**Inputs:** Topic seeds, trend signals, audience metadata.
**Outputs:** Idea records with score, tags, and target format.

### ScriptService
**Purpose:** Convert approved ideas into scripts/shot lists.
**Inputs:** Idea payloads, brand style guide, tone, length constraints.
**Outputs:** Script document + structured scene/beat list.

### AssetGenService
**Purpose:** Produce media assets (images, voiceovers, b-roll prompts).
**Inputs:** Script scenes/asset requests, style presets.
**Outputs:** Asset manifests with storage URLs and metadata.

### VideoAssembler
**Purpose:** Assemble assets into final videos.
**Inputs:** Asset manifest, script timing, templates.
**Outputs:** Rendered video + thumbnail + metadata.

### PostScheduler
**Purpose:** Publish content to distribution channels.
**Inputs:** Final asset + platform schedule rules.
**Outputs:** Published post IDs, status updates.

### AnalyticsCollector
**Purpose:** Pull performance metrics and feedback signals.
**Inputs:** Published post IDs, platform APIs.
**Outputs:** Engagement metrics, retention, and audience signals.

### UserPortal (tglauner.com)
**Purpose:** Operator UI for review, approval, and monitoring.
**Inputs:** All service statuses and artifacts.
**Outputs:** Approvals, overrides, manual edits, and configuration.

## Workflow Orchestrator
**Choice:** Temporal.

**Rationale:**
- Deterministic workflows with retries and state tracking.
- Built-in scheduling for daily runs.
- Easy fan-out/fan-in for asset generation and rendering.
- Strong observability and audit trails for approvals.

**Daily Run Workflow (high level):**
1. Trigger `DailyContentWorkflow`.
2. Generate ideas and score.
3. Run optional manual review.
4. Generate scripts.
5. Generate assets.
6. Assemble video(s).
7. Schedule posts.
8. Collect analytics on a rolling basis.

## Data Flow and Messaging

### Topics / Queues
- `ideas.generated`
- `ideas.approved`
- `scripts.generated`
- `assets.requested`
- `assets.generated`
- `videos.rendered`
- `posts.scheduled`
- `analytics.collected`

### Payload Schemas (canonical fields)

**IdeaPayload**
```json
{
  "idea_id": "uuid",
  "title": "string",
  "description": "string",
  "tags": ["string"],
  "score": 0.0,
  "target_format": "short|long|carousel",
  "created_at": "iso8601"
}
```

**ScriptPayload**
```json
{
  "script_id": "uuid",
  "idea_id": "uuid",
  "scenes": [
    {
      "scene_id": "uuid",
      "beat": "string",
      "duration_sec": 0,
      "asset_needs": ["string"]
    }
  ],
  "version": 1,
  "created_at": "iso8601"
}
```

**AssetManifestPayload**
```json
{
  "manifest_id": "uuid",
  "script_id": "uuid",
  "assets": [
    {
      "asset_id": "uuid",
      "type": "image|audio|video",
      "source": "string",
      "url": "string",
      "metadata": {}
    }
  ],
  "created_at": "iso8601"
}
```

**VideoPayload**
```json
{
  "video_id": "uuid",
  "manifest_id": "uuid",
  "render_url": "string",
  "thumbnail_url": "string",
  "duration_sec": 0,
  "created_at": "iso8601"
}
```

**PostPayload**
```json
{
  "post_id": "uuid",
  "video_id": "uuid",
  "platform": "string",
  "scheduled_at": "iso8601",
  "status": "scheduled|published|failed",
  "created_at": "iso8601"
}
```

**AnalyticsPayload**
```json
{
  "post_id": "uuid",
  "platform": "string",
  "metrics": {
    "views": 0,
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "watch_time_sec": 0
  },
  "collected_at": "iso8601"
}
```

### Status Tracking
Each entity tracks a `status` field and `updated_at` timestamp. Suggested states:
- Idea: `new` → `approved` → `rejected`
- Script: `draft` → `approved`
- Asset: `requested` → `generated` → `failed`
- Video: `rendering` → `ready` → `failed`
- Post: `scheduled` → `published` → `failed`

Temporal workflow state is the source of truth, with event sourcing mirrored in a database for the UI.

## MVP vs Scale Responsibilities

### MVP (Single Tenant, Manual Review)
- **IdeaService:** Single tenant; manual approval gate in UserPortal.
- **ScriptService:** Human-in-the-loop edits allowed before asset gen.
- **AssetGenService:** Limited templates, slower batch rendering.
- **VideoAssembler:** Single render queue, basic templates.
- **PostScheduler:** Manual schedule confirmation.
- **AnalyticsCollector:** Daily pull for a small number of posts.
- **UserPortal:** Admin-only UI for approvals and overrides.

### Scale Phase (Multi-Tenant, Automated)
- **IdeaService:** Multi-tenant, automated scoring and routing.
- **ScriptService:** Automated script generation with QA checks.
- **AssetGenService:** Parallelized asset generation per tenant.
- **VideoAssembler:** Auto-scaling render workers with priority queues.
- **PostScheduler:** Automated scheduling with platform-specific rules.
- **AnalyticsCollector:** Near-real-time ingestion + anomaly detection.
- **UserPortal:** Role-based access, per-tenant dashboards.

