#!/usr/bin/env python3
"""Extract canonical-schema samples from the full unified JSONL file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CANONICAL_FIELDS = (
    "record_id",
    "source",
    "source_split",
    "question",
    "answer",
    "answer_type",
    "department",
    "related_disease",
    "quality_score",
    "metadata_origin",
    "question_length",
    "answer_length",
    "question_hash",
    "duplicate_flag",
)


def canonical_record(record: dict[str, Any]) -> dict[str, Any]:
    return {field: record.get(field) for field in CANONICAL_FIELDS}


def extract_first_records(input_path: Path, limit: int) -> list[dict[str, Any]]:
    records = []
    with input_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            records.append(canonical_record(json.loads(line)))
            if len(records) >= limit:
                break
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/standardized-full/huatuo_unified.jsonl"),
        help="Full 19GB canonical unified JSONL file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/full_unified_samples.jsonl"),
        help="Canonical sample JSONL output path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of records to extract from the unified JSONL file.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Unified JSONL file not found: {args.input}")

    records = extract_first_records(args.input, args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
