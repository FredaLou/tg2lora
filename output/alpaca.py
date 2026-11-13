"""Convert dataset to Alpaca format.

Format:
[
    {"prompt": "user text", "completion": "assistant reply"},
    ...
]
"""

from typing import List, Dict, Any


def to_alpaca(dataset: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert conversations dataset to Alpaca format."""
    result = []
    for item in dataset:
        convs = item.get("conversations", [])
        if not convs:
            continue

        prompt = ""
        completion = ""

        for turn in convs:
            role = turn.get("from", "")
            value = turn.get("value", "").strip()
            if role == "human" and not prompt:
                prompt = value
            elif role == "gpt" and not completion:
                completion = value

        if prompt and completion:
            result.append({"prompt": prompt, "completion": completion})

    return result