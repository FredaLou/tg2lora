"""Convert dataset to ChatML format.

Each entry becomes a single string:
<|user|>user message<|assistant|>assistant reply<|end|>
"""

from typing import List, Dict, Any


def to_chatml(dataset: List[Dict[str, Any]]) -> List[str]:
    """Convert conversations dataset to list of ChatML strings."""
    result = []
    for item in dataset:
        convs = item.get("conversations", [])
        if not convs:
            continue

        parts = []
        for turn in convs:
            role = turn.get("from", "")
            value = turn.get("value", "").strip()
            if not value:
                continue

            if role == "human":
                parts.append(f"<|user|>{value}")
            elif role == "gpt":
                parts.append(f"<|assistant|>{value}<|end|>")

        if parts:
            result.append("\n".join(parts))

    return result