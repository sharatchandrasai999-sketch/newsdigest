"""Command-line interface for newsdigest."""

from __future__ import annotations

import argparse
import sys

from .digest import render_digest
from .feed import collect


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="newsdigest",
        description="Build a daily markdown news digest from RSS feeds. "
        "Falls back to a bundled sample feed when offline or when no "
        "--feed is given.",
    )
    parser.add_argument(
        "--feed",
        action="append",
        default=[],
        metavar="RSS-URL",
        help="RSS feed URL to include (repeatable)",
    )
    parser.add_argument("--out", help="write the markdown digest to this file")
    parser.add_argument(
        "--max-items",
        type=int,
        default=10,
        help="maximum items in the digest (default: 10)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    items, used_sample = collect(args.feed, max_items=args.max_items)
    if used_sample:
        print(
            "newsdigest: using bundled sample feed "
            "(no feed given, or the feed could not be fetched)",
            file=sys.stderr,
        )
    digest = render_digest(items)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(digest)
        print(f"Digest written to {args.out}")
    else:
        print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
