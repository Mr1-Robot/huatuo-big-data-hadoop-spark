#!/usr/bin/env python3
"""Generate report-only tables and figures from frozen project evidence."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", ".matplotlib-cache")

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
FIGURES_DIR = REPORT_DIR / "figures"
TABLES_DIR = REPORT_DIR / "tables"

PILOT_TIMINGS = ROOT / "results/case-benchmark/timings-cluster-20260606-153149.csv"
FULL_TIMINGS = ROOT / "results/case-benchmark/timings-full-cluster-20260607-171724.csv"
FULL_SUMMARY = ROOT / "reports/full_summary.json"

CASE_LABELS = {
    "1": "Department\ndemand",
    "2": "Disease and\nsymptom trends",
    "3": "QA quality and\ncompleteness",
    "4": "Question-type\ndistribution",
}

CASE_NAMES = {
    "1": "Department demand",
    "2": "Disease and symptom trends",
    "3": "QA quality and completeness",
    "4": "Question-type distribution",
}

FRAMEWORK_LABELS = {
    "hadoop_streaming_yarn": "Hadoop Streaming",
    "spark_submit_yarn": "Spark",
}

COLORS = {
    "hadoop_streaming_yarn": "#2f6f9f",
    "spark_submit_yarn": "#d97706",
    "consultation": "#2f6f9f",
    "encyclopedia": "#267e65",
    "knowledge_graph": "#d97706",
    "lite": "#7c3aed",
}

DEPARTMENT_LABELS = {
    "中医科": "Traditional Chinese Medicine",
    "儿科": "Pediatrics",
    "其他": "Other",
    "内科": "Internal Medicine",
    "口腔科": "Stomatology",
    "外科": "Surgery",
    "妇产科": "Obstetrics & Gynecology",
    "心理科学": "Psychology",
    "急诊科": "Emergency",
    "感染与免疫科": "Infectious & Immunology",
    "生殖健康科": "Reproductive Health",
    "男性健康科": "Men's Health",
    "皮肤性病科": "Dermatology & Venereology",
    "眼耳鼻喉科": "ENT & Ophthalmology",
    "神经科学": "Neurology",
    "肿瘤科": "Oncology",
}


def read_timings(path: Path) -> dict[str, dict[str, dict[str, str]]]:
    rows: dict[str, dict[str, dict[str, str]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.setdefault(row["case_study"], {})[row["framework"]] = row
    return rows


def load_summary() -> dict:
    return json.loads(FULL_SUMMARY.read_text(encoding="utf-8"))


def save_grouped_timing_chart(path: Path, title: str, output: Path) -> None:
    timings = read_timings(path)
    case_ids = ["1", "2", "3", "4"]
    frameworks = ["hadoop_streaming_yarn", "spark_submit_yarn"]
    x_positions = list(range(len(case_ids)))
    bar_width = 0.36

    fig, ax = plt.subplots(figsize=(10.8, 5.8), dpi=160)
    for index, framework in enumerate(frameworks):
        offset = (index - 0.5) * bar_width
        values = [
            float(timings[case_id][framework]["elapsed_seconds"])
            for case_id in case_ids
        ]
        bars = ax.bar(
            [x + offset for x in x_positions],
            values,
            width=bar_width,
            label=FRAMEWORK_LABELS[framework],
            color=COLORS[framework],
        )
        ax.bar_label(bars, labels=[f"{value:.1f}s" for value in values], padding=3)

    ax.set_title(title)
    ax.set_ylabel("Elapsed time (seconds)")
    ax.set_xticks(x_positions, [CASE_LABELS[case_id] for case_id in case_ids])
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="upper left")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_source_distribution(summary: dict, output: Path) -> None:
    sources = summary["sources"]
    labels = ["Consultation QA", "Knowledge Graph QA", "Encyclopedia QA", "Huatuo26M-Lite"]
    keys = ["consultation", "knowledge_graph", "encyclopedia", "lite"]
    values = [sources[key] for key in keys]

    fig, ax = plt.subplots(figsize=(10.2, 5.4), dpi=160)
    bars = ax.barh(labels, values, color=[COLORS[key] for key in keys])
    ax.set_title("Full Canonical Dataset Source Distribution")
    ax.set_xlabel("Records, log scale")
    ax.set_xscale("log")
    ax.bar_label(bars, labels=[f"{value:,}" for value in values], padding=4)
    ax.grid(axis="x", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_answer_type_chart(summary: dict, output: Path) -> None:
    answer_types = summary["answer_types"]
    labels = ["URL answers", "Text answers"]
    values = [answer_types["url"], answer_types["text"]]

    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=160)
    wedges, _, autotexts = ax.pie(
        values,
        labels=labels,
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=110,
        colors=["#2f6f9f", "#d97706"],
        textprops={"fontsize": 10},
    )
    for text in autotexts:
        text.set_color("white")
        text.set_fontweight("bold")
    ax.set_title("Answer Type Distribution in Full Canonical Dataset")
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_duplicate_chart(summary: dict, output: Path) -> None:
    duplicates = summary["duplicates"]
    unique = summary["records"] - duplicates
    labels = ["Unique / first occurrence", "Duplicate-flagged"]
    values = [unique, duplicates]

    fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=160)
    bars = ax.bar(labels, values, color=["#267e65", "#d97706"])
    ax.set_title("Duplicate-Flagged Records After Question Hashing")
    ax.set_ylabel("Records")
    ax.bar_label(bars, labels=[f"{value:,}" for value in values], padding=3)
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_top_departments(summary: dict, output: Path) -> None:
    top = sorted(summary["top_departments"].items(), key=lambda item: item[1])[-10:]
    labels = [DEPARTMENT_LABELS.get(item[0], item[0]) for item in top]
    values = [item[1] for item in top]

    fig, ax = plt.subplots(figsize=(8.8, 5.6), dpi=160)
    bars = ax.barh(labels, values, color="#2f6f9f")
    ax.set_title("Top Observed Departments in Huatuo26M-Lite")
    ax.set_xlabel("Records")
    ax.bar_label(bars, labels=[f"{value:,}" for value in values], padding=4)
    ax.grid(axis="x", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def timing_table(name: str, path: Path) -> str:
    timings = read_timings(path)
    lines = [
        f"### {name}",
        "",
        "| Case study | Output groups | Hadoop Streaming on YARN | Spark on YARN | Faster |",
        "| ---------- | ------------: | -----------------------: | ------------: | ------ |",
    ]
    for case_id in ["1", "2", "3", "4"]:
        hadoop = timings[case_id]["hadoop_streaming_yarn"]
        spark = timings[case_id]["spark_submit_yarn"]
        hadoop_seconds = float(hadoop["elapsed_seconds"])
        spark_seconds = float(spark["elapsed_seconds"])
        faster = "Hadoop" if hadoop_seconds < spark_seconds else "Spark"
        lines.append(
            f"| {CASE_NAMES[case_id]} | {int(hadoop['output_records']):,} | "
            f"{hadoop_seconds:.3f} s | {spark_seconds:.3f} s | {faster} |"
        )
    return "\n".join(lines)


def write_tables(summary: dict) -> None:
    lines = [
        "# Report Tables",
        "",
        "These tables are generated from frozen project evidence files.",
        "",
        "## Dataset Sources",
        "",
        "| Source | Records | Size | Main fields |",
        "| ------ | ------: | ---: | ----------- |",
        "| Consultation QA | 32,708,346 | 4.537 GB | `questions`, `answers` |",
        "| Encyclopedia QA | 364,420 | 0.608 GB | `questions`, `answers` |",
        "| Knowledge Graph QA | 798,444 | 0.149 GB | `questions`, `answers` |",
        "| Huatuo26M-Lite | 177,703 | 0.138 GB | `id`, `question`, `answer`, `score`, `label`, `related_diseases` |",
        "| **Combined** | **34,048,913** | **5.432 GB** | Heterogeneous medical QA records |",
        "",
        "## Full Canonical Dataset Summary",
        "",
        "| Metric | Value |",
        "| ------ | ----: |",
        f"| Records | {summary['records']:,} |",
        f"| File size | {summary['file_size_bytes']:,} bytes, about 19 GB |",
        f"| Invalid JSON lines | {summary['invalid_json_lines']:,} |",
        f"| Duplicate-flagged records | {summary['duplicates']:,} |",
        f"| Duplicate percentage | {summary['duplicate_percentage']:.3f}% |",
        f"| URL answers | {summary['answer_types']['url']:,} |",
        f"| Text answers | {summary['answer_types']['text']:,} |",
        f"| Missing questions | {summary['missing_questions']:,} |",
        f"| Missing answers | {summary['missing_answers']:,} |",
        "",
        "## Aggregation Techniques by Case Study",
        "",
        "| Case study | Grouping key | Main techniques | Aggregation output |",
        "| ---------- | ------------ | --------------- | ------------------ |",
        "| Department demand | `department`, `metadata_origin` | filtering, projection, key-value mapping, grouping, count aggregation, ranking | department demand counts |",
        "| Disease and symptom trends | `term_type`, `matched_term` | text scanning, pattern matching, term extraction, grouping, count aggregation, frequency ranking | disease/symptom frequency counts |",
        "| QA quality and completeness | `source` | source partitioning, URL/text classification, missing-value detection, duplicate aggregation, length aggregation, min/max/average, percentages | source-level quality summary |",
        "| Question-type distribution | `question_type` | rule-based classification, keyword matching, grouping, count aggregation | question category distribution |",
        "",
        "## Big Data Analytics Lifecycle Mapping",
        "",
        "| Lifecycle stage | Project implementation |",
        "| --------------- | ---------------------- |",
        "| Data generation | Huatuo medical QA source repositories |",
        "| Data aggregation | Downloaded four source snapshots into `data/source/` |",
        "| Data preprocessing | JSONL parsing, field extraction, text formatting cleanup |",
        "| Data integration | Canonical schema normalization and union, not join |",
        "| Data cleaning | Missing-value handling, invalid JSON validation, URL/text answer typing |",
        "| Data reduction | Deterministic 400,000-record pilot for validation |",
        "| Data transformation | Canonical JSONL with derived lengths, hashes, duplicate flags, and metadata fields |",
        "| Data analytics | Four Hadoop Streaming and Spark case studies on HDFS/YARN |",
        "",
        timing_table("Pilot HDFS/YARN Benchmark", PILOT_TIMINGS),
        "",
        timing_table("Full HDFS/YARN Benchmark", FULL_TIMINGS),
        "",
    ]
    (TABLES_DIR / "report_tables.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    summary = load_summary()

    save_grouped_timing_chart(
        PILOT_TIMINGS,
        "Pilot Benchmark on HDFS/YARN (400,000 Records)",
        FIGURES_DIR / "pilot_execution_time.png",
    )
    save_grouped_timing_chart(
        FULL_TIMINGS,
        "Full Benchmark on HDFS/YARN (34,048,898 Records)",
        FIGURES_DIR / "full_execution_time.png",
    )
    save_source_distribution(summary, FIGURES_DIR / "source_distribution.png")
    save_answer_type_chart(summary, FIGURES_DIR / "answer_type_distribution.png")
    save_duplicate_chart(summary, FIGURES_DIR / "duplicate_records.png")
    save_top_departments(summary, FIGURES_DIR / "top_departments.png")
    write_tables(summary)

    print(f"Wrote figures: {FIGURES_DIR}")
    print(f"Wrote tables: {TABLES_DIR / 'report_tables.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
