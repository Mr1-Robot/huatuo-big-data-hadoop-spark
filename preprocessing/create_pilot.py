#!/usr/bin/env python3
"""Create a deterministic, balanced pilot from the original Huatuo sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCES = {
    "consultation": (
        ("validation", "validation_datasets.jsonl"),
        ("test", "test_datasets.jsonl"),
        ("train", "train_datasets.jsonl"),
    ),
    "encyclopedia": (
        ("validation", "validation_datasets.jsonl"),
        ("test", "test_datasets.jsonl"),
        ("train", "train_datasets.jsonl"),
    ),
    "knowledge_graph": (
        ("validation", "validation_datasets.jsonl"),
        ("test", "test_datasets.jsonl"),
        ("train", "train_datasets.jsonl"),
    ),
    "lite": (("full", "format_data.jsonl"),),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("data/source"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/pilot"))
    parser.add_argument("--records-per-source", type=int, default=100000)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, dict[str, int]] = {}
    for source, split_files in SOURCES.items():
        written = 0
        split_counts: dict[str, int] = {}
        output_path = args.output_dir / f"{source}.jsonl"
        with output_path.open("w", encoding="utf-8") as output:
            for split, filename in split_files:
                split_count = 0
                with (args.source_dir / source / filename).open(encoding="utf-8") as handle:
                    for line in handle:
                        if written >= args.records_per_source:
                            break
                        if not line.strip():
                            continue
                        record = json.loads(line)
                        record["source_split"] = split
                        output.write(json.dumps(record, ensure_ascii=False) + "\n")
                        written += 1
                        split_count += 1
                split_counts[split] = split_count
                if written >= args.records_per_source:
                    break
        summary[source] = {"total": written, **split_counts}
    (args.output_dir / "pilot_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

