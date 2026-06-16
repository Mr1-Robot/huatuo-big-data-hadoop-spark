#!/usr/bin/env python3
"""Hadoop Streaming mapper for the four healthcare case studies."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.getcwd())
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "preprocessing"))
# pyrefly: ignore [missing-import]
from common import load_json, match_terms  # noqa: E402


def emit(key: object, value: object) -> None:
    print(
        json.dumps(key, ensure_ascii=False, sort_keys=True)
        + "\t"
        + json.dumps(value, ensure_ascii=False, sort_keys=True)
    )


def case_study_1(record: dict) -> None:
    department = record.get("department") or record.get("inferred_department")
    if department:
        origin = "observed" if record.get("department") else "inferred"
        emit(["department", department, origin], 1)


def case_study_1_with_rules(record: dict, rules: dict) -> None:
    if record.get("department") or record.get("inferred_department"):
        case_study_1(record)
        return
    text = record.get("question", "")
    matched_diseases = match_terms(text, rules.get("diseases", []))
    departments = {
        rules.get("disease_departments", {}).get(disease)
        for disease in matched_diseases
    }
    for department in sorted(value for value in departments if value):
        emit(["department", department, "inferred"], 1)


def case_study_2(record: dict, rules: dict) -> None:
    text = record.get("question", "")
    if record.get("answer_type") == "text":
        text += " " + record.get("answer", "")
    observed_disease = record.get("related_disease") or record.get("inferred_disease")
    diseases = set(match_terms(text, rules.get("diseases", [])))
    if observed_disease:
        diseases.add(observed_disease)
    for disease in sorted(diseases):
        emit(["term", "disease", disease], 1)
    for symptom in match_terms(text, rules.get("symptoms", [])):
        emit(["term", "symptom", symptom], 1)


def case_study_3(record: dict) -> None:
    score = record.get("quality_score")
    emit(
        ["source_quality", record.get("source", "unknown")],
        {
            "records": 1,
            "empty_questions": int(not record.get("question")),
            "empty_answers": int(record.get("answer_type") == "empty"),
            "url_answers": int(record.get("answer_type") == "url"),
            "duplicates": int(bool(record.get("duplicate_flag"))),
            "question_length_sum": int(record.get("question_length") or 0),
            "answer_length_sum": int(record.get("answer_length") or 0),
            "score_count": int(score is not None),
            "score_sum": float(score or 0),
            "score_min": score,
            "score_max": score,
        },
    )


def classify_question(question: str, patterns: dict[str, list[str]]) -> str:
    matches = [
        category
        for category, terms in sorted(patterns.items())
        if match_terms(question, terms)
    ]
    return matches[0] if matches else "other"


def case_study_4(record: dict, rules: dict) -> None:
    question_type = classify_question(
        record.get("question", ""), rules.get("question_types", {})
    )
    emit(["question_type", question_type], 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case-study",
        choices=("1", "2", "3", "4", "all"),
        required=True,
        help="Run one case study or all case studies in a single mapper pass.",
    )
    parser.add_argument("--rules", default=str(ROOT / "config" / "analytics_rules.json"))
    args = parser.parse_args()
    rules = load_json(args.rules)

    functions = {
        "1": lambda record: case_study_1_with_rules(record, rules),
        "2": lambda record: case_study_2(record, rules),
        "3": lambda record: case_study_3(record),
        "4": lambda record: case_study_4(record, rules),
    }
    selected_functions = (
        list(functions.values())
        if args.case_study == "all"
        else [functions[args.case_study]]
    )
    for line_number, line in enumerate(sys.stdin, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            for function in selected_functions:
                function(record)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"mapper skipped line {line_number}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
