# Analytics Requirements

## KPIs & Definitions
- **Daily posts count**: Number of posts published per venue per day.
- **Impressions**: Total times posts were shown within a reporting window.
- **CTR (Click-through rate)**: Clicks / impressions, reported as a percentage.
- **Conversions**: Total completed conversion events (configurable per venue; e.g., ticket purchase, signup).
- **Top performers**:
  - **Top posts** by impressions, CTR, and conversions.
  - **Top venues** by total impressions, CTR, and conversions.

## Dimensions & Filters
- **Date range** (day/week/month granularity).
- **Venue** (single/multi-select).
- **Content type** (e.g., image, video, text).
- **Campaign/tag** (optional metadata provided by venue APIs).

## Data Freshness & Latency
- Target **daily rollups** with hourly incremental updates.
- Late-arriving data can backfill up to **7 days**.

## Permissions & Overrides
- Admins can approve or override computed metrics.
- Overrides must be **audited** with user, timestamp, and reason.

## Alerts & Monitoring
- Flag **anomalies** when CTR or conversions deviate ±50% from 7-day average.
- Alert on **API failures** or missing data for a venue.

## Reporting Outputs
- **Dashboards** with trend charts, tables, and top-performer views.
- **CSV export** for filtered table views.

## Non-Functional Requirements
- API rate limits must be respected (configurable per venue).
- Idempotent ingestion with deduplication on (venue, post_id, metric_date).
- Data retention: **2 years** raw metrics, **5 years** daily rollups.
