#!/usr/bin/env python3
"""Verify that Hadoop and Spark pilot outputs have identical primary aggregates."""

from __future__ import annotations

import glob
import json
from pathlib import Path


def read_jsonl(paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def maps(case_study: str, hadoop: list[dict], spark: list[dict]) -> tuple[dict, dict]:
    if case_study == "1":
        return (
            {(r["key"][1], r["key"][2]): r["metrics"]["count"] for r in hadoop},
            {(r["department"], r["origin"]): r["count"] for r in spark},
        )
    if case_study == "2":
        return (
            {(r["key"][1], r["key"][2]): r["metrics"]["count"] for r in hadoop},
            {(r["term_type"], r["term"]): r["count"] for r in spark},
        )
    if case_study == "3":
        return (
            {r["key"][1]: r["metrics"]["records"] for r in hadoop},
            {r["source"]: r["records"] for r in spark},
        )
    return (
        {r["key"][1]: r["metrics"]["count"] for r in hadoop},
        {r["question_type"]: r["count"] for r in spark},
    )


def main() -> int:
    results = {}
    valid = True
    for case_study in ("1", "2", "3", "4"):
        hadoop = read_jsonl([f"results/pilot/hadoop/cs{case_study}.jsonl"])
        spark = read_jsonl(glob.glob(f"results/pilot/spark-cs{case_study}/part-*.json"))
        hadoop_map, spark_map = maps(case_study, hadoop, spark)
        matches = hadoop_map == spark_map
        valid = valid and matches
        results[case_study] = {
            "matches": matches,
            "hadoop_output_groups": len(hadoop_map),
            "spark_output_groups": len(spark_map),
        }
    report = {"valid": valid, "case_studies": results}
    Path("reports").mkdir(exist_ok=True)
    Path("reports/framework_equivalence.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())

