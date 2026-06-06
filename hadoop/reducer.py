#!/usr/bin/env python3
"""Hadoop Streaming reducer for the four healthcare case studies."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Iterator


def grouped_input() -> Iterator[tuple[str, list[Any]]]:
    current_key = None
    values: list[Any] = []
    for line in sys.stdin:
        if not line.strip():
            continue
        key, raw_value = line.rstrip("\n").split("\t", 1)
        if current_key is not None and key != current_key:
            yield current_key, values
            values = []
        current_key = key
        values.append(json.loads(raw_value))
    if current_key is not None:
        yield current_key, values


def reduce_quality(values: list[dict[str, Any]]) -> dict[str, Any]:
    summed = {
        name: sum(value[name] for value in values)
        for name in (
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
    }
    score_mins = [value["score_min"] for value in values if value["score_min"] is not None]
    score_maxs = [value["score_max"] for value in values if value["score_max"] is not None]
    records = summed["records"]
    score_count = summed["score_count"]
    return {
        **summed,
        "average_question_length": summed["question_length_sum"] / records,
        "average_answer_length": summed["answer_length_sum"] / records,
        "duplicate_percentage": 100 * summed["duplicates"] / records,
        "url_answer_percentage": 100 * summed["url_answers"] / records,
        "score_average": summed["score_sum"] / score_count if score_count else None,
        "score_min": min(score_mins) if score_mins else None,
        "score_max": max(score_maxs) if score_maxs else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case-study",
        choices=("1", "2", "3", "4", "all"),
        required=True,
        help="Run one case study or all case studies in a single reducer pass.",
    )
    args = parser.parse_args()

    for raw_key, values in grouped_input():
        key = json.loads(raw_key)
        result = (
            reduce_quality(values)
            if args.case_study == "3"
            or (args.case_study == "all" and key[0] == "source_quality")
            else {"count": sum(values)}
        )
        print(
            json.dumps(
                {"key": key, "metrics": result},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
