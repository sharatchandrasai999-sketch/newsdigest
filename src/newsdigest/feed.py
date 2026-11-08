"""Fetch, parse and dedupe RSS feeds.

Network use is limited to plain GET requests with a short timeout.
Any failure falls back to the bundled sample feed, so the tool works
fully offline.
"""

from __future__ import annotations

import difflib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import requests

FETCH_TIMEOUT = 10
DEDUPE_THRESHOLD = 0.85

# Project-root data/sample_feed.xml (source layout: src/newsdigest/feed.py).
SAMPLE_FEED_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_feed.xml"


@dataclass
class Item:
    title: str
    link: str
    description: str
    pub_date: str = ""


def sample_feed_text() -> str:
    """Return the bundled sample feed, from the project tree or package data."""
    if SAMPLE_FEED_PATH.is_file():
        return SAMPLE_FEED_PATH.read_text(encoding="utf-8")
    # Fallback for an installed (non-editable) copy of the package.
    from importlib.resources import files

    return (files("newsdigest") / "data" / "sample_feed.xml").read_text(
        encoding="utf-8"
    )


def fetch_feed(url: str) -> str | None:
    """GET an RSS feed; return its text, or None on any failure."""
    try:
        response = requests.get(url, timeout=FETCH_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def parse_feed(xml_text: str) -> list[Item]:
    """Parse RSS 2.0 XML with the stdlib only. Missing fields become ''."""
    root = ET.fromstring(xml_text)
    items: list[Item] = []
    for element in root.iter("item"):
        def text(tag: str) -> str:
            node = element.find(tag)
            return (node.text or "").strip() if node is not None else ""

        items.append(
            Item(
                title=text("title"),
                link=text("link"),
                description=text("description"),
                pub_date=text("pubDate"),
            )
        )
    return items


def dedupe(items: list[Item], threshold: float = DEDUPE_THRESHOLD) -> list[Item]:
    """Drop near-duplicate titles, keeping the first occurrence.

    Two titles count as duplicates when difflib.SequenceMatcher gives a
    similarity ratio of 0.85 or more.
    """
    kept: list[Item] = []
    for item in items:
        title = item.title.strip().lower()
        if not title:
            continue
        duplicate = any(
            difflib.SequenceMatcher(None, title, other.title.strip().lower()).ratio()
            >= threshold
            for other in kept
        )
        if not duplicate:
            kept.append(item)
    return kept


def collect(feed_urls: list[str], max_items: int = 10) -> tuple[list[Item], bool]:
    """Gather items from the given feeds (or the sample feed).

    Returns (items, used_sample): used_sample is True when the sample feed
    was used — either because no --feed was given or because every fetch
    failed. A failed feed is replaced by the sample feed, not by an error.
    """
    items: list[Item] = []
    used_sample = False
    if not feed_urls:
        items.extend(parse_feed(sample_feed_text()))
        used_sample = True
    else:
        for url in feed_urls:
            text = fetch_feed(url)
            if text is None:
                items.extend(parse_feed(sample_feed_text()))
                used_sample = True
            else:
                items.extend(parse_feed(text))
    return dedupe(items)[:max_items], used_sample
