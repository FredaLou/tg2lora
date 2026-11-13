from sources.base import BaseSource
from sources.telegram import TelegramSource
from sources.jsonl import JsonlSource
from sources.conversations import ConversationsSource


def create_source(format: str, **kwargs) -> BaseSource:
    """Factory: create source by format name."""
    sources = {
        "telegram": TelegramSource,
        "jsonl": JsonlSource,
        "conversations": ConversationsSource,
    }
    if format not in sources:
        raise ValueError(f"Unknown source format: '{format}'. Available: {list(sources.keys())}")
    return sources[format](**kwargs)


__all__ = ["BaseSource", "TelegramSource", "JsonlSource", "ConversationsSource", "create_source"]
