#!/usr/bin/env python3
"""Compare Hadoop and Spark result keys/counts for one case study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_lines(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        rows.extend(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return rows


def hadoop_counts(case_study: str, rows: list[dict]) -> dict[tuple, int]:
    if case_study == "3":
        return {tuple(row["key"]): row["metrics"]["records"] for row in rows}
    return {tuple(row["key"]): row["metrics"]["count"] for row in rows}


def spark_counts(case_study: str, rows: list[dict]) -> dict[tuple, int]:
    key_fields = {
        "1": ("department", "origin"),
        "2": ("term_type", "term"),
        "3": ("source",),
        "4": ("question_type",),
    }[case_study]
    prefix = {
        "1": ("department",),
        "2": ("term",),
        "3": ("source_quality",),
        "4": ("question_type",),
    }[case_study]
    metric = "records" if case_study == "3" else "count"
    return {
        prefix + tuple(row[field] for field in key_fields): row[metric] for row in rows
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-study", choices=("1", "2", "3", "4"), required=True)
    parser.add_argument("--hadoop", required=True, type=Path)
    parser.add_argument("--spark-dir", required=True, type=Path)
    args = parser.parse_args()

    hadoop = hadoop_counts(args.case_study, read_lines([args.hadoop]))
    spark = spark_counts(
        args.case_study, read_lines(sorted(args.spark_dir.glob("part-*.json")))
    )
    if hadoop != spark:
        print(json.dumps({"hadoop": list(hadoop.items()), "spark": list(spark.items())}, indent=2))
        return 1
    print(f"Case study {args.case_study}: Hadoop and Spark aggregate outputs match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
