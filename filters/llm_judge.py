"""LLM-based text quality judge.

Sends text to a local LLM server and asks it to rate quality.
Returns a dict with "score" (0-10) and "keep" (bool).
"""

import json
import re
import requests
from typing import Optional


JUDGE_PROMPT = """You are evaluating messages for a personality dataset.

KEEP:
- natural speech
- emotions
- slang
- everyday phrases
- distinct character

DROP:
- garbage
- fragments
- meaningless text

IMPORTANT:
Reply ONLY with JSON:
{{"score": 0-10, "keep": true/false}}

Message:
{text}
"""


def safe_json_extract(text: str) -> Optional[dict]:
    """Extract first JSON object from LLM response."""
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def judge(text: str, url: str, keep_score: int = 5) -> dict:
    """Judge a single text via LLM server.

    Args:
        text: The text to evaluate.
        url: LLM server endpoint (e.g. http://127.0.0.1:8001/completion).
        keep_score: Minimum score to keep (0-10).

    Returns:
        dict with keys: score (int), keep (bool), reason (str or None)
    """
    prompt = JUDGE_PROMPT.format(text=text)

    payload = {
        "prompt": prompt,
        "n_predict": 120,
        "temperature": 0.2,
        "stop": ["</s>"],
    }

    try:
        r = requests.post(url, json=payload, timeout=120)
        data = r.json()

        if "content" in data:
            raw = data["content"]
        elif "choices" in data:
            raw = data["choices"][0].get("text", "")
        else:
            return {"score": 0, "keep": False, "reason": "bad_response_format"}

        parsed = safe_json_extract(raw)
        if parsed is None:
            return {"score": 0, "keep": False, "reason": "json_parse_fail"}

        score = int(parsed.get("score", 0))
        keep = bool(parsed.get("keep", False))

        # Enforce score threshold
        if keep and score < keep_score:
            keep = False

        return {"score": score, "keep": keep, "reason": None}

    except requests.exceptions.ConnectionError:
        return {"score": 0, "keep": False, "reason": f"connection_error: {url}"}
    except Exception as e:
        return {"score": 0, "keep": False, "reason": str(e)}