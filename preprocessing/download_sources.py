#!/usr/bin/env python3
"""Stream the published Huatuo datasets from Hugging Face into raw JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCES = {
    "consultation": "FreedomIntelligence/huatuo_consultation_qa",
    "encyclopedia": "FreedomIntelligence/huatuo_encyclopedia_qa",
    "knowledge_graph": "FreedomIntelligence/huatuo_knowledge_graph_qa",
    "lite": "FreedomIntelligence/Huatuo26M-Lite",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--limit", type=int, help="Optional records per source for testing")
    parser.add_argument("--source", choices=(*SOURCES, "all"), default="all")
    args = parser.parse_args()

    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit(
            "Install the Hugging Face datasets package first: pip install datasets"
        ) from exc

    args.output_dir.mkdir(parents=True, exist_ok=True)
    selected = SOURCES if args.source == "all" else {args.source: SOURCES[args.source]}
    for source, repository in selected.items():
        output_path = args.output_dir / f"{source}.jsonl"
        count = 0
        loaded = load_dataset(repository, streaming=True)
        if hasattr(loaded, "keys"):
            split = "train" if "train" in loaded else next(iter(loaded.keys()))
            dataset = loaded[split]
        else:
            dataset = loaded
        with output_path.open("w", encoding="utf-8") as output:
            for record in dataset:
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
                if args.limit and count >= args.limit:
                    break
        print(f"{source}: wrote {count} records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
