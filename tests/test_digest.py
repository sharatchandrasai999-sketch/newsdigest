"""Tests for newsdigest."""

from datetime import date
from pathlib import Path

from newsdigest.cli import main
from newsdigest.digest import render_digest, summarize, topic_of
from newsdigest.feed import Item, collect, dedupe, parse_feed, sample_feed_text

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_feed.xml"


def test_sample_feed_parses_to_eight_items():
    items = parse_feed(SAMPLE.read_text())
    assert len(items) == 8
    assert all(item.title and item.link for item in items)


def test_near_duplicates_dedupe_to_fewer_items():
    items = parse_feed(sample_feed_text())
    deduped = dedupe(items)
    assert len(deduped) == 7
    titles = [item.title for item in deduped]
    assert "New open-source model cuts inference costs for small teams" in titles
    assert "New open source model cuts inference cost for small teams" not in titles


def test_summary_is_non_empty_and_from_description():
    item = parse_feed(sample_feed_text())[0]
    summary = summarize(item.description)
    assert summary
    assert item.description.startswith(summary.rstrip("…"))
    # First sentence only — the second sentence must not leak in.
    assert "Early testers" not in summary


def test_summary_without_sentence_boundary_uses_first_words():
    text = " ".join(f"word{i}" for i in range(40))
    summary = summarize(text)
    assert summary.startswith("word0")
    assert "word24" in summary
    assert "word25" not in summary


def test_markdown_contains_date_header_and_links():
    items, _ = collect([], max_items=10)
    text = render_digest(items, digest_date=date(2026, 11, 8))
    assert "# Daily News Digest — 2026-11-08" in text
    assert "https://example.com/news/open-model-costs" in text
    assert "mock backend, no LLM call" in text


def test_items_grouped_by_topic():
    items, _ = collect([], max_items=10)
    text = render_digest(items, digest_date=date(2026, 11, 8))
    assert "## AI" in text
    assert "## science" in text
    assert "## business" in text
    assert "## other" in text
    assert topic_of(Item("Chatbot safety toolkit", "", "neural network checks")) == "AI"


def test_unreachable_feed_falls_back_to_sample():
    items, used_sample = collect(["http://127.0.0.1:9/rss.xml"], max_items=10)
    assert used_sample is True
    assert len(items) == 7  # 8 sample items minus the near-duplicate
    assert items[0].title.startswith("New open-source model")


def test_max_items_is_respected():
    items, _ = collect([], max_items=3)
    assert len(items) == 3


def test_out_writes_file(tmp_path, capsys):
    out = tmp_path / "digest.md"
    assert main(["--out", str(out)]) == 0
    text = out.read_text()
    assert "# Daily News Digest — " in text
    assert "https://example.com/news/" in text
    assert "using bundled sample feed" in capsys.readouterr().err
