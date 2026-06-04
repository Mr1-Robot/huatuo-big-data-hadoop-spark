#!/usr/bin/env python3
"""Create a compact presentation-ready summary of the processed pilot."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/processed-pilot/huatuo_unified.jsonl"))
    parser.add_argument("--timings", type=Path, default=Path("results/pilot/timings.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/pilot_summary.json"))
    args = parser.parse_args()

    sources: Counter[str] = Counter()
    splits: Counter[str] = Counter()
    answer_types: Counter[str] = Counter()
    origins: Counter[str] = Counter()
    duplicates = records = 0
    with args.input.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            records += 1
            sources[record["source"]] += 1
            splits[f'{record["source"]}:{record["source_split"]}'] += 1
            answer_types[record["answer_type"]] += 1
            origins[record["metadata_origin"]] += 1
            duplicates += int(record["duplicate_flag"])

    timings = list(csv.DictReader(args.timings.open(encoding="utf-8")))
    summary = {
        "records": records,
        "duplicates": duplicates,
        "duplicate_percentage": round(100 * duplicates / records, 4),
        "sources": dict(sorted(sources.items())),
        "source_splits": dict(sorted(splits.items())),
        "answer_types": dict(sorted(answer_types.items())),
        "metadata_origins": dict(sorted(origins.items())),
        "timings": timings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

