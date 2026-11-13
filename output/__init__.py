"""Output format converters.

Converts the internal conversation dataset to various training formats:
- conversations: [{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}]
- chatml: <|user|>...<|assistant|>...
- alpaca: {"prompt": "...", "completion": "..."}
"""

import json
from pathlib import Path


from output.conversations import to_conversations
from output.chatml import to_chatml
from output.alpaca import to_alpaca


FORMATS = {
    "conversations": to_conversations,
    "chatml": to_chatml,
    "alpaca": to_alpaca,
}


def save_dataset(dataset: list, output_path: str, fmt: str = "conversations"):
    """Convert dataset to specified format and save to file.

    Args:
        dataset: List of {"conversations": [...]} items.
        output_path: Output file path.
        fmt: Target format name.
    """
    if fmt not in FORMATS:
        raise ValueError(f"Unknown output format: '{fmt}'. Available: {list(FORMATS.keys())}")

    converted = FORMATS[fmt](dataset)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if fmt in ("conversations", "alpaca"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(converted, f, ensure_ascii=False, indent=2)
    elif fmt == "chatml":
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in converted:
                f.write(entry + "\n")

    print(f"[OUTPUT] Saved {len(converted)} items to {output_path} (format={fmt})")


__all__ = ["save_dataset", "FORMATS"]