"""LLM response generator using a local llama.cpp / OpenAI-compatible server.

Sends user text with a system prompt to the server and collects the reply.
"""

import re
import requests
from typing import Optional

# Qwen3 thinking tags (assembled to avoid tool interpolation)
_THINK_START = "<" + "think" + ">"
_THINK_END = "<" + "/" + "think" + ">"


def _strip_thinking(text: str) -> str:
    """Remove ALL Qwen3 thinking blocks. Returns empty string if no real answer."""
    if _THINK_START not in text:
        return text
    # Repeatedly strip the first thinking block until none remain
    while _THINK_START in text:
        end = text.find(_THINK_END)
        if end == -1:
            return ""
        text = text[end + len(_THINK_END):].strip()
    return text


def generate(
    user_text: str,
    url: str,
    system_prompt: str,
    temperature: float = 0.85,
    max_tokens: int = 150,
    top_p: float = 0.9,
    min_p: float = 0.05,
    repeat_penalty: float = 1.1,
    stop: Optional[list] = None,
) -> Optional[str]:
    """Generate a single assistant reply."""
    prompt = f"""{system_prompt}

This is a continuation of a conversation.
Respond naturally and concisely.

User: {user_text}
Assistant:"""

    payload = {
        "prompt": prompt,
        "temperature": temperature,
        "top_p": top_p,
        "min_p": min_p,
        "repeat_penalty": repeat_penalty,
        "n_predict": max_tokens,
        "stop": stop or ["</s>", "User:"],
    }

    try:
        r = requests.post(url, json=payload, timeout=180)
        data = r.json()

        if "content" in data:
            text = data["content"]
        elif "choices" in data:
            text = data["choices"][0].get("text", "")
        else:
            return None

        if not text:
            return None

        text = text.strip()
        text = _strip_thinking(text)

        if not text:
            return None

        return text

    except requests.exceptions.ConnectionError:
        print(f"[GEN] Connection error: {url}")
        return None
    except Exception as e:
        print(f"[GEN] Error: {e}")
        return None

__all__ = ["generate", "_strip_thinking"]

