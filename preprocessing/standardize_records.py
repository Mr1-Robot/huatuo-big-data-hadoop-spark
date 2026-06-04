#!/usr/bin/env python3
"""Convert a Huatuo source JSON/JSONL file into the canonical JSONL schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator

from common import (
    classify_answer,
    first_present,
    load_json,
    match_terms,
    normalize_text,
    stable_hash,
)

ALIASES = {
    "id": ("record_id", "id", "ID", "_id"),
    "question": ("question", "questions", "Question", "Question_Sequence"),
    "answer": ("answer", "answers", "Answer", "Answer_Sequence"),
    "quality_score": ("quality_score", "score", "Expert_Score"),
    "department": ("department", "label", "Department_Label"),
    "related_disease": (
        "related_disease",
        "related_diseases",
        "Related_Diseases",
        "disease",
    ),
}


def read_records(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        first = handle.read(1)
        handle.seek(0)
        if first == "[":
            data = json.load(handle)
            if not isinstance(data, list):
                raise ValueError("JSON input must contain a list of records")
            yield from data
            return
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Line {line_number} is not a JSON object")
            yield record


def infer_metadata(
    question: str,
    answer: str,
    rules: dict[str, dict[str, list[str]]],
) -> tuple[str | None, str | None]:
    text = f"{question} {answer}"
    departments = [
        name
        for name, terms in rules.get("departments", {}).items()
        if match_terms(text, terms)
    ]
    diseases = [
        name
        for name, terms in rules.get("diseases", {}).items()
        if match_terms(text, terms)
    ]
    return (departments[0] if departments else None, diseases[0] if diseases else None)


def canonicalize(
    raw: dict[str, Any],
    source: str,
    row_number: int,
    rules: dict[str, Any],
) -> dict[str, Any]:
    question = normalize_text(first_present(raw, ALIASES["question"]))
    answer = normalize_text(first_present(raw, ALIASES["answer"]))
    observed_department = normalize_text(first_present(raw, ALIASES["department"])) or None
    observed_disease = normalize_text(first_present(raw, ALIASES["related_disease"])) or None
    raw_id = normalize_text(first_present(raw, ALIASES["id"]))
    question_hash = stable_hash(question.casefold()) if question else ""
    inferred_department, inferred_disease = infer_metadata(question, answer, rules)

    score = first_present(raw, ALIASES["quality_score"])
    try:
        quality_score = float(score) if score not in (None, "") else None
    except (TypeError, ValueError):
        quality_score = None

    return {
        "record_id": raw_id or f"{source}-{row_number}-{question_hash[:12]}",
        "source": source,
        "question": question,
        "answer": answer,
        "answer_type": classify_answer(answer),
        "department": observed_department,
        "related_disease": observed_disease,
        "quality_score": quality_score,
        "inferred_department": inferred_department if not observed_department else None,
        "inferred_disease": inferred_disease if not observed_disease else None,
        "metadata_origin": "observed" if observed_department or observed_disease else (
            "inferred" if inferred_department or inferred_disease else "unavailable"
        ),
        "question_length": len(question),
        "answer_length": len(answer) if classify_answer(answer) == "text" else 0,
        "question_hash": question_hash,
        "duplicate_flag": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source", required=True)
    parser.add_argument("--rules", type=Path, default=Path("config/enrichment_rules.json"))
    parser.add_argument("--keep-empty-questions", action="store_true")
    parser.add_argument("--skip-duplicate-detection", action="store_true")
    args = parser.parse_args()

    rules = load_json(args.rules) if args.rules.exists() else {}
    seen_hashes: set[str] = set()
    written = skipped = duplicates = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as output:
        for row_number, raw in enumerate(read_records(args.input), 1):
            record = canonicalize(raw, args.source, row_number, rules)
            if not record["question"] and not args.keep_empty_questions:
                skipped += 1
                continue
            question_hash = record["question_hash"]
            record["duplicate_flag"] = (
                False if args.skip_duplicate_detection else question_hash in seen_hashes
            )
            duplicates += int(record["duplicate_flag"])
            if not args.skip_duplicate_detection:
                seen_hashes.add(question_hash)
            output.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            written += 1

    print(
        json.dumps(
            {"written": written, "skipped": skipped, "duplicates": duplicates},
            sort_keys=True,
        ),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
