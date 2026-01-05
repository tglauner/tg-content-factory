from __future__ import annotations

import argparse
from pathlib import Path

from tg_content_factory import analytics, db, drafts, ideas, review, templates, venues

DEFAULT_DB = str(Path("data") / "tg_content_factory.db")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="tg-content-factory CLI")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to sqlite DB file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Initialize the database")

    generate_parser = subparsers.add_parser("generate-ideas", help="Generate ideas")
    generate_parser.add_argument("--count", type=int, default=3)

    subparsers.add_parser("list-ideas", help="List ideas")

    draft_parser = subparsers.add_parser("create-drafts", help="Create drafts")
    draft_parser.add_argument("idea_ids", nargs="+", type=int)
    draft_parser.add_argument(
        "--templates",
        nargs="+",
        default=[template.name for template in templates.TEMPLATES],
    )

    list_drafts_parser = subparsers.add_parser("list-drafts", help="List drafts")
    list_drafts_parser.add_argument("--status", default=None)

    review_parser = subparsers.add_parser("review", help="Approve or reject drafts")
    review_parser.add_argument("draft_id", type=int)
    review_parser.add_argument("--approve", action="store_true")
    review_parser.add_argument("--reject", action="store_true")

    subparsers.add_parser("list-pending", help="List drafts pending review")

    post_parser = subparsers.add_parser("post-approved", help="Post approved drafts")
    post_parser.add_argument(
        "--venues",
        nargs="+",
        default=venues.DEFAULT_VENUES,
        help="Venues to post to",
    )

    subparsers.add_parser("list-posts", help="List posted items")

    analytics_parser = subparsers.add_parser("record-analytics", help="Record metrics")
    analytics_parser.add_argument("post_id", type=int)
    analytics_parser.add_argument("views", type=int)
    analytics_parser.add_argument("clicks", type=int)

    subparsers.add_parser("list-analytics", help="List analytics")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        db.init_db(args.db)
        print(f"Initialized database at {args.db}")
        return

    if args.command == "generate-ideas":
        idea_ids = ideas.generate_ideas(args.db, args.count)
        print(f"Generated ideas: {idea_ids}")
        return

    if args.command == "list-ideas":
        for idea in ideas.list_ideas(args.db):
            print(idea)
        return

    if args.command == "create-drafts":
        draft_ids = drafts.create_drafts(args.db, args.idea_ids, args.templates)
        print(f"Created drafts: {draft_ids}")
        return

    if args.command == "list-drafts":
        for draft in drafts.list_drafts(args.db, args.status):
            print(draft)
        return

    if args.command == "review":
        status = None
        if args.approve:
            status = "approved"
        if args.reject:
            status = "rejected"
        if not status:
            parser.error("review requires --approve or --reject")
        updated = review.set_review_status(args.db, args.draft_id, status)
        if updated:
            print(f"Updated draft {args.draft_id} to {status}")
        else:
            print(f"Draft {args.draft_id} not found")
        return

    if args.command == "list-pending":
        for draft in review.list_pending_reviews(args.db):
            print(draft)
        return

    if args.command == "post-approved":
        post_ids = venues.post_approved(args.db, args.venues)
        print(f"Posted drafts: {post_ids}")
        return

    if args.command == "list-posts":
        for post in venues.list_posts(args.db):
            print(post)
        return

    if args.command == "record-analytics":
        metric_id = analytics.record_metrics(args.db, args.post_id, args.views, args.clicks)
        print(f"Recorded analytics: {metric_id}")
        return

    if args.command == "list-analytics":
        for metric in analytics.list_metrics(args.db):
            print(metric)
        return


if __name__ == "__main__":
    main()
