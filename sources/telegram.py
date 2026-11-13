import json
from typing import List, Dict, Any, Optional

from sources.base import BaseSource


class TelegramSource(BaseSource):
    """Parses Telegram chat export.

    Supports two formats:
    1. Object: {"name": ..., "messages": [...]}
    2. Flat array: [{"from": ..., "text": ...}, ...]

    Each message is expected to have:
        "from": sender name
        "text": message text (may be empty for media-only)
    """

    def __init__(self, field: str = "text", sender: Optional[str] = None):
        self.field = field
        self.sender = sender  # if set, only extract messages from this sender

    def load(self, path: str) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            # Object format: {"name": ..., "messages": [...]}
            messages = data.get("messages", [])
            return messages if isinstance(messages, list) else []
        elif isinstance(data, list):
            return data
        return []

    def extract_user_text(self, item: Dict[str, Any]) -> Optional[str]:
        if not isinstance(item, dict):
            return None

        # Filter by sender if specified
        if self.sender is not None:
            sender = item.get("from", "")
            if sender != self.sender:
                return None

        # Primary: configured field
        if self.field in item:
            text = item[self.field]
            if isinstance(text, str) and text.strip():
                return text
            return None

        # Fallback: common field names
        for fallback in ("text", "user", "message", "content"):
            if fallback in item:
                val = item[fallback]
                if isinstance(val, str) and val.strip():
                    return val
                # Telegram "text" can be a list of entity dicts
                if isinstance(val, list):
                    parts = []
                    for t in val:
                        if isinstance(t, dict):
                            parts.append(t.get("text", ""))
                        else:
                            parts.append(str(t))
                    joined = "".join(parts).strip()
                    if joined:
                        return joined

        return None