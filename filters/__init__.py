"""Filtering pipeline: rule-based cleaning + optional LLM judge."""

from filters.rules import clean_text, score_text
from filters.llm_judge import judge


def apply_filters(
    texts: list[str],
    min_len: int,
    max_len: int,
    rule_threshold: int,
    judge_cfg: dict | None = None,
    range_start: int = 0,
    range_end: int | None = None,
) -> list[str]:
    """Apply rule-based and optional LLM-based filtering.

    Args:
        texts: List of raw user texts.
        min_len: Minimum text length.
        max_len: Maximum text length.
        rule_threshold: Minimum rule score to pass.
        judge_cfg: If not None, dict with keys: url, keep_score, max_results.
        range_start: Start index (0-based) for slicing valid texts.
        range_end: End index (exclusive). None = no limit.

    Returns:
        List of filtered, validated texts.
    """
    # Phase 1: Rule-based cleaning
    valid = []
    skipped_empty = 0
    skipped_clean = 0
    skipped_score = 0

    for text in texts:
        if not text:
            skipped_empty += 1
            continue

        cleaned = clean_text(text, min_len, max_len)
        if not cleaned:
            skipped_clean += 1
            continue

        score = score_text(cleaned)
        if score < rule_threshold:
            skipped_score += 1
            continue

        valid.append(cleaned)

    print(f"[FILTER] Total: {len(texts)}")
    print(f"[FILTER] Skipped empty: {skipped_empty}")
    print(f"[FILTER] Skipped by clean/len: {skipped_clean}")
    print(f"[FILTER] Skipped by score: {skipped_score}")
    print(f"[FILTER] Valid after rules: {len(valid)}")

    # Phase 2: Range slicing
    start = range_start
    end = range_end if range_end is not None else len(valid)
    valid = valid[start:end]
    print(f"[FILTER] After range [{start}:{end}]: {len(valid)}")

    # Phase 3: Optional LLM judge
    if judge_cfg:
        from tqdm import tqdm
        url = judge_cfg["url"]
        keep_score = judge_cfg.get("keep_score", 5)
        max_results = judge_cfg.get("max_results", 1000)

        final = []
        print(f"[JUDGE] Enabled (url={url}, keep_score={keep_score}, max={max_results})")

        for i, text in enumerate(tqdm(valid, desc="LLM Judge")):
            res = judge(text, url, keep_score)
            if res.get("keep", False):
                final.append(text)
            if len(final) >= max_results:
                break

        print(f"[JUDGE] Kept: {len(final)}")
        return final

    return valid


__all__ = ["clean_text", "score_text", "judge", "apply_filters"]