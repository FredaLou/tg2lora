"""Dataset filter & generator CLI.

Usage:
    python main.py filter --input data/chat.json --output data/filtered.json
    python main.py generate --input data/filtered.json --output data/train.json
    python main.py full --input data/chat.json --output data/train.json
    python main.py full --input data/chat.json --output data/train.json --format chatml
"""

import argparse
import json
import sys
from pathlib import Path

from config.loader import load_config
from sources import create_source
from filters import apply_filters
from generators import run_generation
from output import save_dataset


def cmd_filter(args):
    """Filter input file and save cleaned texts as JSON."""
    cfg = load_config(args.config)
    src_cfg = cfg["source"]
    flt_cfg = cfg["filters"]

    source = create_source(
        format=src_cfg["format"],
        field=src_cfg.get("field", "user"),
        sender=src_cfg.get("sender"),
    )

    print(f"[FILTER] Loading source: {args.input}")
    texts = source.process(args.input)
    print(f"[FILTER] Extracted {len(texts)} raw texts")

    judge_cfg = None
    if flt_cfg.get("llm_judge", {}).get("enabled", False):
        judge_cfg = {
            "url": flt_cfg["llm_judge"]["url"],
            "keep_score": flt_cfg["llm_judge"].get("keep_score", 5),
            "max_results": flt_cfg["llm_judge"].get("max_results", 1000),
        }

    rng = flt_cfg.get("range", {})
    filtered = apply_filters(
        texts=texts,
        min_len=flt_cfg.get("min_len", 30),
        max_len=flt_cfg.get("max_len", 300),
        rule_threshold=flt_cfg.get("rule_threshold", 0),
        judge_cfg=judge_cfg,
        range_start=rng.get("start", 0),
        range_end=rng.get("end"),
    )

    print(f"[FILTER] Final count: {len(filtered)}")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"[FILTER] Saved to {out_path}")


def cmd_generate(args):
    """Generate LoRA training data from filtered texts."""
    cfg = load_config(args.config)
    gen_cfg = cfg["generation"]

    print(f"[GEN] Loading filtered texts: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        texts = json.load(f)
    print(f"[GEN] {len(texts)} texts to process")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results = run_generation(texts, str(out_path), gen_cfg)

    # Final cleanup: remove empty/duplicate pairs
    before = len(results)
    seen = set()
    clean = []
    for item in results:
        try:
            human = item["conversations"][0]["value"].strip()
            gpt = item["conversations"][1]["value"].strip()
        except (KeyError, IndexError):
            continue
        if not human or not gpt:
            continue
        if human in seen:
            continue
        seen.add(human)
        clean.append(item)
    removed = before - len(clean)
    if removed:
        print(f"[GEN] Cleanup: removed {removed} empty/duplicate pairs")

    results = clean
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    out_fmt = args.format or cfg.get("output", {}).get("format", "conversations")
    if out_fmt != "conversations":
        save_dataset(results, out_path, out_fmt)
        print(f"[GEN] Converted to {out_fmt}: {len(results)} samples -> {out_path}")
    else:
        print(f"[GEN] Saved {len(results)} samples to {out_path}")


def cmd_full(args):
    """Full pipeline: filter then generate in one shot."""
    filter_output = args.filtered_output or str(Path("data") / "_tmp_filtered.json")

    # Phase 1: Filter
    filter_args = argparse.Namespace(
        config=args.config,
        input=args.input,
        output=filter_output,
    )
    cmd_filter(filter_args)

    # Phase 2: Generate
    gen_args = argparse.Namespace(
        config=args.config,
        input=filter_output,
        output=args.output,
        format=args.format,
    )
    cmd_generate(gen_args)

    # Cleanup temp file if auto-created
    if args.filtered_output is None and Path(filter_output).exists():
        Path(filter_output).unlink()


def main():
    parser = argparse.ArgumentParser(description="Dataset filter & generator for LoRA fine-tuning")
    sub = parser.add_subparsers(dest="command")

    # filter
    p_filter = sub.add_parser("filter", help="Filter input data")
    p_filter.add_argument("--input", required=True)
    p_filter.add_argument("--output", required=True)
    p_filter.add_argument("--config", default="dataset_config.yaml")

    # generate
    p_gen = sub.add_parser("generate", help="Generate training data")
    p_gen.add_argument("--input", required=True)
    p_gen.add_argument("--output", required=True)
    p_gen.add_argument("--config", default="dataset_config.yaml")
    p_gen.add_argument("--format", default=None)

    # full
    p_full = sub.add_parser("full", help="Filter + generate")
    p_full.add_argument("--input", required=True)
    p_full.add_argument("--output", required=True)
    p_full.add_argument("--filtered-output", default=None)
    p_full.add_argument("--config", default="dataset_config.yaml")
    p_full.add_argument("--format", default=None)

    args = parser.parse_args()

    if args.command == "filter":
        cmd_filter(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "full":
        cmd_full(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()