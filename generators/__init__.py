"""Generation pipeline: sends filtered texts to LLM server and collects replies."""

import json
import random
import time
from pathlib import Path
from typing import Optional

from tqdm import tqdm
from generators.llama_server import generate


def load_existing(path: str) -> tuple[list, set]:
    """Load existing output file for resume support.

    Returns:
        (dataset, done_set) where done_set contains user texts already processed.
    """
    if not Path(path).exists():
        return [], set()

    try:
        with open(path, "r", encoding="utf-8") as f:
            dataset = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], set()

    done = set()
    for item in dataset:
        try:
            done.add(item["conversations"][0]["value"])
        except (KeyError, IndexError):
            continue

    return dataset, done


def run_generation(
    texts: list[str],
    output_path: str,
    gen_cfg: dict,
) -> list:
    """Run full generation pipeline with resume support.

    Args:
        texts: List of filtered user texts to generate replies for.
        output_path: Where to save the dataset (JSON).
        gen_cfg: Generation config dict with keys:
            url, temperature, max_tokens, top_p, min_p,
            repeat_penalty, delay, stop, system_prompt

    Returns:
        The full dataset (existing + new).
    """
    dataset, done = load_existing(output_path)

    random.shuffle(texts)

    print(f"[GEN] Total input: {len(texts)}")
    print(f"[GEN] Already done: {len(done)}")

    url = gen_cfg["url"]
    system_prompt = gen_cfg["system_prompt"]
    temperature = gen_cfg.get("temperature", 0.85)
    max_tokens = gen_cfg.get("max_tokens", 150)
    top_p = gen_cfg.get("top_p", 0.9)
    min_p = gen_cfg.get("min_p", 0.05)
    repeat_penalty = gen_cfg.get("repeat_penalty", 1.1)
    delay = gen_cfg.get("delay", 0.2)
    stop = gen_cfg.get("stop", ["</s>", "User:"])

    saved = 0

    for i, text in enumerate(tqdm(texts, desc="Generating")):
        if text in done:
            continue

        reply = generate(
            user_text=text,
            url=url,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            min_p=min_p,
            repeat_penalty=repeat_penalty,
            stop=stop,
        )

        if not reply:
            continue

        dataset.append({
            "conversations": [
                {"from": "human", "value": text},
                {"from": "gpt", "value": reply},
            ]
        })
        done.add(text)
        saved += 1

        # Save after each item (crash-safe)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        time.sleep(delay)

    print(f"[GEN] New items: {saved}")
    print(f"[GEN] Total dataset: {len(dataset)}")
    print(f"[GEN] Saved to: {output_path}")

    return dataset


__all__ = ["generate", "run_generation", "load_existing"]