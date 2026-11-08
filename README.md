# newsdigest

A daily news digest from RSS feeds. Fetches one or more feeds, drops
near-duplicate stories, writes a short extractive summary for each item,
and groups everything by topic into a markdown digest.

## How it works

- **Fetch**: `requests` with a 10-second timeout. If a feed cannot be
  fetched, or no `--feed` is given, the bundled sample feed
  (`data/sample_feed.xml`, 8 generic tech/AI headlines) is used instead,
  so the tool works fully offline.
- **Parse**: `xml.etree.ElementTree` from the standard library.
- **Dedupe**: titles with a `difflib.SequenceMatcher` similarity of 0.85
  or more collapse to one item — the sample feed includes two
  near-duplicate headlines to show this.
- **Summaries**: the "summariser" is a mock backend — the first sentence
  of each description, or its first 25 words when there is no sentence
  boundary. **No LLM is called anywhere in this project**, and the output
  says so.
- **Topics**: simple keyword rules on title + description — AI, science,
  business, other.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
newsdigest
newsdigest --feed https://example.com/feed.xml --feed https://example.com/other.xml
newsdigest --feed https://example.com/feed.xml --max-items 5 --out digest.md
```

Default output goes to stdout; `--out` writes a markdown file instead.
A note on stderr says when the sample feed was used.

## Example output

```markdown
# Daily News Digest — 2026-11-08

Summaries are extractive (first sentence of each description) — mock backend, no LLM call.

## AI

- [New open-source model cuts inference costs for small teams](https://example.com/news/open-model-costs) — A community-released model runs on a single GPU and uses less memory than earlier small models.
- [Researchers release a toolkit for testing chatbot safety](https://example.com/news/chatbot-safety-toolkit) — The toolkit checks chatbots for rude replies, leaked instructions, and hallucinated facts.

## science

- [Astronomers spot a bright comet in the early morning sky](https://example.com/news/morning-comet) — The comet should stay visible to the naked eye for another week before it fades.

## business

- [Venture funding for AI tools stays strong this quarter](https://example.com/news/ai-funding-quarter) — Investors continue to back small firms building tools on top of large language models.
```

## Tests

```bash
python -m pytest
```
