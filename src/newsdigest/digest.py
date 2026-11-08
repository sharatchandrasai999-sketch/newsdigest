"""Topic classification, extractive summaries and markdown rendering.

The "summariser" is a mock backend: it returns the first sentence of an
item's description (or its first 25 words). No LLM is called, and the
output says so.
"""

from __future__ import annotations

import re
from datetime import date

from .feed import Item

SUMMARY_WORDS = 25

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "AI": [
        "artificial intelligence",
        "machine learning",
        "large language model",
        "llm",
        "neural",
        "chatbot",
        "generative ai",
        "inference",
        "gpu",
    ],
    "science": [
        "research",
        "study",
        "scientist",
        "astronom",
        "space",
        "climate",
        "discovery",
        "sleep",
    ],
    "business": [
        "market",
        "startup",
        "funding",
        "venture",
        "company",
        "stock",
        "economy",
        "demand",
    ],
}
TOPIC_ORDER = ["AI", "science", "business", "other"]

_WORD_BOUNDARY = re.compile(r"\b({})\b")


def topic_of(item: Item) -> str:
    """Classify an item by simple keyword rules on title + description."""
    text = f"{item.title} {item.description}".lower()
    for topic in TOPIC_ORDER[:-1]:
        for keyword in TOPIC_KEYWORDS[topic]:
            pattern = (
                _WORD_BOUNDARY.pattern.format(re.escape(keyword))
                if " " not in keyword and len(keyword) <= 4
                else re.escape(keyword)
            )
            if re.search(pattern, text):
                return topic
    return "other"


def summarize(description: str) -> str:
    """Extractive mock summary: first sentence, else first 25 words."""
    text = " ".join(description.split())
    if not text:
        return "(no description)"
    match = re.search(r"[.!?](\s|$)", text)
    if match:
        return text[: match.start() + 1]
    words = text.split()
    if len(words) > SUMMARY_WORDS:
        return " ".join(words[:SUMMARY_WORDS]) + " …"
    return text


def render_digest(items: list[Item], digest_date: date | None = None) -> str:
    """Render the digest as markdown, grouped by topic."""
    day = digest_date or date.today()
    out = [f"# Daily News Digest — {day.isoformat()}", ""]
    out.append(
        "Summaries are extractive (first sentence of each description) — "
        "mock backend, no LLM call."
    )
    out.append("")
    grouped: dict[str, list[Item]] = {topic: [] for topic in TOPIC_ORDER}
    for item in items:
        grouped[topic_of(item)].append(item)
    for topic in TOPIC_ORDER:
        if not grouped[topic]:
            continue
        out.append(f"## {topic}")
        out.append("")
        for item in grouped[topic]:
            summary = summarize(item.description)
            if item.link:
                out.append(f"- [{item.title}]({item.link}) — {summary}")
            else:
                out.append(f"- {item.title} — {summary}")
        out.append("")
    if not items:
        out.append("No items today.")
        out.append("")
    return "\n".join(out)
