#!/usr/bin/env python3
"""Validate canonical Huatuo JSONL and print a quality summary."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

REQUIRED = {
    "record_id",
    "source",
    "source_split",
    "question",
    "answer",
    "answer_type",
    "department",
    "related_disease",
    "quality_score",
    "inferred_department",
    "inferred_disease",
    "metadata_origin",
    "question_length",
    "answer_length",
    "question_hash",
    "duplicate_flag",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    sources: Counter[str] = Counter()
    answer_types: Counter[str] = Counter()
    origins: Counter[str] = Counter()
    duplicates = total = 0

    with args.input.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            total += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue
            missing = REQUIRED - record.keys()
            if missing:
                errors.append(f"line {line_number}: missing {sorted(missing)}")
            if not record.get("record_id"):
                errors.append(f"line {line_number}: empty record_id")
            if not record.get("question"):
                errors.append(f"line {line_number}: empty question")
            sources[record.get("source", "")] += 1
            answer_types[record.get("answer_type", "")] += 1
            origins[record.get("metadata_origin", "")] += 1
            duplicates += int(bool(record.get("duplicate_flag")))

    summary = {
        "valid": not errors,
        "records": total,
        "duplicates": duplicates,
        "sources": dict(sources),
        "answer_types": dict(answer_types),
        "metadata_origins": dict(origins),
        "errors": errors[:20],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
