#!/usr/bin/env python3
"""Dependency-free integration tests for preprocessing and Hadoop logic."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> int:
    run("bash", "scripts/prepare_data.sh", "data/samples", "data/standardized")
    unified = jsonl(ROOT / "data/standardized/huatuo_unified.jsonl")
    assert len(unified) == 8
    assert sum(record["duplicate_flag"] for record in unified) == 1
    assert any(record["metadata_origin"] == "inferred" for record in unified)
    assert any(record["answer_type"] == "url" for record in unified)

    expected = {
        "1": lambda rows: any(row["key"][0] == "department" for row in rows),
        "2": lambda rows: any(row["key"][1] == "symptom" for row in rows),
        "3": lambda rows: all(row["key"][0] == "source_quality" for row in rows),
        "4": lambda rows: any(row["key"] == ["question_type", "diagnosis"] for row in rows),
    }
    for case_study, check in expected.items():
        output = ROOT / f"results/test-cs{case_study}.jsonl"
        run(
            "bash",
            "scripts/run_hadoop_local.sh",
            case_study,
            "data/standardized/huatuo_unified.jsonl",
            str(output.relative_to(ROOT)),
        )
        rows = jsonl(output)
        assert rows and check(rows), f"case study {case_study} output failed validation"

    print("All preprocessing and Hadoop local integration tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

