#!/usr/bin/env python3
"""Create deterministic 25/50/75/100 percent benchmark JSONL inputs."""

from __future__ import annotations

import argparse
import json
from contextlib import ExitStack
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    percentages = (25, 50, 75, 100)
    counts = {percentage: 0 for percentage in percentages}
    with ExitStack() as stack:
        outputs = {
            percentage: stack.enter_context(
                (args.output_dir / f"huatuo_{percentage}.jsonl").open(
                    "w", encoding="utf-8"
                )
            )
            for percentage in percentages
        }
        with args.input.open(encoding="utf-8") as source:
            for line in source:
                if not line.strip():
                    continue
                record = json.loads(line)
                bucket = int(record["question_hash"][:8], 16) % 100
                for percentage, output in outputs.items():
                    if bucket < percentage:
                        output.write(line)
                        counts[percentage] += 1
    print(json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
