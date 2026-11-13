import re
from typing import Optional


def clean_text(text: str, min_len: int = 30, max_len: int = 300) -> Optional[str]:
    """Clean and validate text. Returns None if text is invalid."""
    if not isinstance(text, str):
        return None

    if "http://" in text or "https://" in text:
        return None

    text = re.sub(r"[^\w\s\.\,\!\?\-\:\;\(\)]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) < min_len or len(text) > max_len:
        return None

    return text


def score_text(text: str) -> int:
    """Score text quality based on linguistic features.

    Higher score = more likely to be natural, expressive speech.
    """
    score = 0
    low = text.lower()

    emotional_markers = ["бля", "пиздец", "чел", "...", "??", "!!!",
                         "damn", "holy", "seriously", "ugh", "omg"]
    if any(x in low for x in emotional_markers):
        score += 2

    casual_markers = ["норм", "жесть", "тупо", "имба", "хз",
                      "lol", "idk", "nah", "yeah", "like", "kinda"]
    if any(x in low for x in casual_markers):
        score += 2

    repeat_markers = ["опять", "снова", "как всегда",
                      "again", "always", "every time"]
    if any(x in low for x in repeat_markers):
        score += 2

    if len(low.split()) < 4:
        score -= 2

    return score