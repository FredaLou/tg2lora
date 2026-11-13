"""Convert dataset to standard conversations format.

Format:
[
    {
        "conversations": [
            {"from": "human", "value": "user text"},
            {"from": "gpt", "value": "assistant reply"}
        ]
    },
    ...
]
"""

from typing import List, Dict, Any


def to_conversations(dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Pass-through: dataset is already in conversations format.

    Just validates and cleans each entry.
    """
    result = []
    for item in dataset:
        convs = item.get("conversations", [])
        if not convs:
            continue

        cleaned = []
        for turn in convs:
            if not isinstance(turn, dict):
                continue
            role = turn.get("from", "")
            value = turn.get("value", "").strip()
            if role in ("human", "gpt") and value:
                cleaned.append({"from": role, "value": value})

        if len(cleaned) >= 2:
            result.append({"conversations": cleaned})

    return result