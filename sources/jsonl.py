import json
from typing import List, Dict, Any, Optional

from sources.base import BaseSource


class JsonlSource(BaseSource):
    """Parses JSONL files or plain JSON arrays.

    Expected format (one JSON object per line):
    {"user": "hello world"}
    {"text": "another message"}
    """

    def __init__(self, field: str = "user"):
        self.field = field

    def load(self, path: str) -> List[Dict[str, Any]]:
        data = []
        with open(path, "r", encoding="utf-8") as f:
            first = f.read(1)
            f.seek(0)

            if first == "[":
                # Regular JSON array
                data = json.load(f)
            else:
                # JSONL
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        return data if isinstance(data, list) else []

    def extract_user_text(self, item: Dict[str, Any]) -> Optional[str]:
        if not isinstance(item, dict):
            return None

        if self.field in item:
            text = item[self.field]
            if isinstance(text, str):
                return text

        # Fallback: try common field names
        for field in ("user", "text", "message", "content", "input"):
            if field in item and isinstance(item[field], str):
                return item[field]

        return None