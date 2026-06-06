#!/usr/bin/env python3
"""Summarize a canonical Huatuo JSONL file and write representative samples."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def update_numeric_stats(stats: dict[str, Any], value: float | int | None) -> None:
    if value is None:
        return
    stats["count"] += 1
    stats["sum"] += value
    stats["min"] = value if stats["min"] is None else min(stats["min"], value)
    stats["max"] = value if stats["max"] is None else max(stats["max"], value)


def finish_numeric_stats(stats: dict[str, Any]) -> dict[str, Any]:
    count = stats["count"]
    return {
        "count": count,
        "min": stats["min"],
        "max": stats["max"],
        "average": round(stats["sum"] / count, 4) if count else None,
    }


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record.get("record_id"),
        "source": record.get("source"),
        "source_split": record.get("source_split"),
        "question": record.get("question"),
        "answer": record.get("answer"),
        "answer_type": record.get("answer_type"),
        "department": record.get("department"),
        "related_disease": record.get("related_disease"),
        "quality_score": record.get("quality_score"),
        "metadata_origin": record.get("metadata_origin"),
        "duplicate_flag": record.get("duplicate_flag"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--summary-output", type=Path, default=Path("reports/full_summary.json"))
    parser.add_argument("--samples-dir", type=Path, default=Path("data/samples/full-canonical"))
    parser.add_argument("--samples-per-source", type=int, default=5)
    args = parser.parse_args()

    source_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    answer_types: Counter[str] = Counter()
    metadata_origins: Counter[str] = Counter()
    departments: Counter[str] = Counter()
    diseases: Counter[str] = Counter()
    missing_questions = 0
    missing_answers = 0
    duplicates = 0
    total = 0
    invalid_json = 0

    question_lengths: dict[str, Any] = {"count": 0, "sum": 0, "min": None, "max": None}
    answer_lengths: dict[str, Any] = {"count": 0, "sum": 0, "min": None, "max": None}
    quality_scores: dict[str, Any] = {"count": 0, "sum": 0, "min": None, "max": None}
    source_samples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    with args.input.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                invalid_json += 1
                continue

            total += 1
            source = str(record.get("source") or "unknown")
            split = str(record.get("source_split") or "unknown")
            answer_type = str(record.get("answer_type") or "unknown")
            origin = str(record.get("metadata_origin") or "unknown")
            question = str(record.get("question") or "")
            answer = str(record.get("answer") or "")
            department = record.get("department")
            disease = record.get("related_disease")

            source_counts[source] += 1
            split_counts[f"{source}:{split}"] += 1
            answer_types[answer_type] += 1
            metadata_origins[origin] += 1
            missing_questions += int(not question)
            missing_answers += int(not answer)
            duplicates += int(bool(record.get("duplicate_flag")))
            if department:
                departments[str(department)] += 1
            if disease:
                diseases[str(disease)] += 1

            update_numeric_stats(question_lengths, record.get("question_length"))
            update_numeric_stats(answer_lengths, record.get("answer_length"))
            update_numeric_stats(quality_scores, record.get("quality_score"))

            if len(source_samples[source]) < args.samples_per_source:
                source_samples[source].append(compact_record(record))

            if total % 1_000_000 == 0:
                print(f"Summarized {total:,} records...")

    summary = {
        "input": str(args.input),
        "file_size_bytes": args.input.stat().st_size,
        "records": total,
        "invalid_json_lines": invalid_json,
        "duplicates": duplicates,
        "duplicate_percentage": round((duplicates / total) * 100, 4) if total else 0,
        "missing_questions": missing_questions,
        "missing_answers": missing_answers,
        "sources": dict(source_counts),
        "source_splits": dict(split_counts),
        "answer_types": dict(answer_types),
        "metadata_origins": dict(metadata_origins),
        "question_lengths": finish_numeric_stats(question_lengths),
        "answer_lengths": finish_numeric_stats(answer_lengths),
        "quality_scores": finish_numeric_stats(quality_scores),
        "top_departments": dict(departments.most_common(20)),
        "top_related_diseases": dict(diseases.most_common(20)),
    }

    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    args.samples_dir.mkdir(parents=True, exist_ok=True)
    for source, records in sorted(source_samples.items()):
        output = args.samples_dir / f"{source}.jsonl"
        with output.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"Wrote summary: {args.summary_output}")
    print(f"Wrote samples: {args.samples_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
