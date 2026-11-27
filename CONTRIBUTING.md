# Contributing

Thanks for helping. Daily markdown news digest from RSS feeds, with dedupe and extractive mock summaries. This is a small, personal project, so keep changes small and easy to review.

## Before you send a change

- Run the tests from any folder: `pytest -q` (tests must not depend on the current working directory)
- Keep the offline path working: the bundled sample feeds must build a digest with no network and no API key.
- If you add a feed source, ship a small sample feed file with it.

## Reporting a problem

Open an issue and include:

- The exact command you ran
- The input file, if it is about one
- What happened, and what you expected instead

Do not include API keys, private documents, or personal details.
