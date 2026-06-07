#!/usr/bin/env python3
"""Generate a Hadoop/Spark benchmark comparison chart."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


CASE_LABELS = {
    "1": "Department\ndemand",
    "2": "Disease and\nsymptom trends",
    "3": "QA quality and\ncompleteness",
    "4": "Question-type\ndistribution",
}

FRAMEWORK_LABELS = {
    "hadoop_streaming_yarn": "Hadoop Streaming",
    "spark_submit_yarn": "Spark",
}

FRAMEWORK_COLORS = {
    "hadoop_streaming_yarn": "#2f6f9f",
    "spark_submit_yarn": "#d97706",
}


def read_timings(path: Path) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            rows.setdefault(row["case_study"], {})[row["framework"]] = float(
                row["elapsed_seconds"]
            )
    return rows


def generate_chart(input_path: Path, output_path: Path) -> None:
    timings = read_timings(input_path)
    case_ids = ["1", "2", "3", "4"]
    frameworks = ["hadoop_streaming_yarn", "spark_submit_yarn"]
    x_positions = list(range(len(case_ids)))
    bar_width = 0.36

    fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=160)

    for index, framework in enumerate(frameworks):
        offset = (index - 0.5) * bar_width
        values = [timings[case_id][framework] for case_id in case_ids]
        bars = ax.bar(
            [x + offset for x in x_positions],
            values,
            width=bar_width,
            label=FRAMEWORK_LABELS[framework],
            color=FRAMEWORK_COLORS[framework],
        )
        ax.bar_label(bars, labels=[f"{value:.1f}s" for value in values], padding=3)

    ax.set_title("Full Huatuo Dataset Benchmark on HDFS/YARN")
    ax.set_ylabel("Elapsed time (seconds)")
    ax.set_xticks(x_positions, [CASE_LABELS[case_id] for case_id in case_ids])
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="upper left")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/case-benchmark/timings-full-cluster-20260607-171724.csv",
        type=Path,
        help="Benchmark timing CSV.",
    )
    parser.add_argument(
        "--output",
        default="reports/full_benchmark_chart.png",
        type=Path,
        help="Output PNG chart path.",
    )
    args = parser.parse_args()
    generate_chart(args.input, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
