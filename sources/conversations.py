import json
from typing import List, Dict, Any, Optional

from sources.base import BaseSource


class ConversationsSource(BaseSource):
    """Parses files already in conversation format.

    Expected format:
    [
        {
            "conversations": [
                {"from": "human", "value": "user text"},
                {"from": "gpt", "value": "assistant reply"}
            ]
        },
        ...
    ]

    This source extracts only the human turns for re-filtering or re-generation.
    """

    def load(self, path: str) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def extract_user_text(self, item: Dict[str, Any]) -> Optional[str]:
        if not isinstance(item, dict):
            return None

        convs = item.get("conversations")
        if not isinstance(convs, list):
            return None

        for turn in convs:
            if isinstance(turn, dict) and turn.get("from") in ("human", "user"):
                value = turn.get("value", "")
                if isinstance(value, str) and value.strip():
                    return value

        return None