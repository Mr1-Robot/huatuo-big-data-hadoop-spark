#!/usr/bin/env python3
"""Hadoop Streaming reducer for the four healthcare case studies."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


QUALITY_SUM_FIELDS = (
    "records",
    "empty_questions",
    "empty_answers",
    "url_answers",
    "duplicates",
    "question_length_sum",
    "answer_length_sum",
    "score_count",
    "score_sum",
)


def is_quality_key(case_study: str, key: list[Any]) -> bool:
    return case_study == "3" or (case_study == "all" and key[0] == "source_quality")


def empty_quality_accumulator() -> dict[str, Any]:
    return {
        **{name: 0 for name in QUALITY_SUM_FIELDS},
        "score_min": None,
        "score_max": None,
    }


def add_quality(accumulator: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    for name in QUALITY_SUM_FIELDS:
        accumulator[name] += value[name]
    score_min = value["score_min"]
    score_max = value["score_max"]
    if score_min is not None:
        accumulator["score_min"] = (
            score_min
            if accumulator["score_min"] is None
            else min(accumulator["score_min"], score_min)
        )
    if score_max is not None:
        accumulator["score_max"] = (
            score_max
            if accumulator["score_max"] is None
            else max(accumulator["score_max"], score_max)
        )
    return accumulator


def reduce_quality(summed: dict[str, Any]) -> dict[str, Any]:
    records = summed["records"]
    score_count = summed["score_count"]
    return {
        **summed,
        "average_question_length": summed["question_length_sum"] / records,
        "average_answer_length": summed["answer_length_sum"] / records,
        "duplicate_percentage": 100 * summed["duplicates"] / records,
        "url_answer_percentage": 100 * summed["url_answers"] / records,
        "score_average": summed["score_sum"] / score_count if score_count else None,
        "score_min": summed["score_min"],
        "score_max": summed["score_max"],
    }


def print_result(key: list[Any], result: dict[str, Any]) -> None:
    print(
        json.dumps(
            {"key": key, "metrics": result},
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case-study",
        choices=("1", "2", "3", "4", "all"),
        required=True,
        help="Run one case study or all case studies in a single reducer pass.",
    )
    args = parser.parse_args()

    current_raw_key: str | None = None
    current_key: list[Any] | None = None
    accumulator: Any = None

    for line in sys.stdin:
        if not line.strip():
            continue
        raw_key, raw_value = line.rstrip("\n").split("\t", 1)
        if current_raw_key is not None and raw_key != current_raw_key:
            if current_key is None:
                raise ValueError("Reducer reached an empty grouped key")
            result = (
                reduce_quality(accumulator)
                if is_quality_key(args.case_study, current_key)
                else {"count": accumulator}
            )
            print_result(current_key, result)
            accumulator = None

        if raw_key != current_raw_key:
            current_raw_key = raw_key
            current_key = json.loads(raw_key)
            accumulator = (
                empty_quality_accumulator()
                if is_quality_key(args.case_study, current_key)
                else 0
            )

        value = json.loads(raw_value)
        if current_key is None:
            raise ValueError("Reducer received value without a key")
        if is_quality_key(args.case_study, current_key):
            accumulator = add_quality(accumulator, value)
        else:
            accumulator += value

    if current_key is not None:
        result = (
            reduce_quality(accumulator)
            if is_quality_key(args.case_study, current_key)
            else {"count": accumulator}
        )
        print_result(current_key, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
