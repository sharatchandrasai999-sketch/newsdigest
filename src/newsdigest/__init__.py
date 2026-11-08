"""newsdigest — daily news digest from RSS feeds."""

__version__ = "0.1.0"

from .digest import render_digest, summarize, topic_of
from .feed import Item, collect, dedupe, parse_feed

__all__ = [
    "Item",
    "collect",
    "dedupe",
    "parse_feed",
    "render_digest",
    "summarize",
    "topic_of",
    "__version__",
]
