#!/usr/bin/env python3
"""Generate report figures and data-flow diagrams from frozen project evidence."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", ".matplotlib-cache")
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
FIGURES = ROOT / "figures"

PILOT_TIMINGS = PROJECT / "results/case-benchmark/timings-cluster-20260606-153149.csv"
FULL_TIMINGS = PROJECT / "results/case-benchmark/timings-full-cluster-20260607-171724.csv"
FULL_SUMMARY = PROJECT / "reports/full_summary.json"

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
    "blue": "#2f6f9f",
    "orange": "#d97706",
    "green": "#267e65",
    "purple": "#7c3aed",
    "light": "#edf4f8",
    "ink": "#18232d",
}

DEPARTMENT_LABELS = {
    "内科": "Internal Medicine",
    "妇产科": "Obstetrics & Gynecology",
    "皮肤性病科": "Dermatology & Venereology",
    "儿科": "Pediatrics",
    "眼耳鼻喉科": "ENT & Ophthalmology",
    "肿瘤科": "Oncology",
    "神经科学": "Neurology",
    "外科": "Surgery",
    "男性健康科": "Men's Health",
    "感染与免疫科": "Infectious & Immunology",
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

    fig, ax = plt.subplots(figsize=(10.8, 5.8), dpi=170)
    for index, framework in enumerate(frameworks):
        offset = (index - 0.5) * bar_width
        values = [float(timings[case_id][framework]["elapsed_seconds"]) for case_id in case_ids]
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

    fig, ax = plt.subplots(figsize=(10.2, 5.4), dpi=170)
    bars = ax.barh(labels, values, color=[COLORS["blue"], COLORS["green"], COLORS["orange"], COLORS["purple"]])
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
    values = [summary["answer_types"]["url"], summary["answer_types"]["text"]]
    labels = ["URL answers", "Text answers"]

    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=170)
    _, _, autotexts = ax.pie(
        values,
        labels=labels,
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=110,
        colors=[COLORS["blue"], COLORS["orange"]],
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
    values = [unique, duplicates]
    labels = ["Unique / first occurrence", "Duplicate-flagged"]

    fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=170)
    bars = ax.bar(labels, values, color=[COLORS["green"], COLORS["orange"]])
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
    labels = [DEPARTMENT_LABELS.get(key, key) for key, _ in top]
    values = [value for _, value in top]

    fig, ax = plt.subplots(figsize=(9.4, 5.9), dpi=170)
    bars = ax.barh(labels, values, color=COLORS["blue"])
    ax.set_title("Top Observed Departments in Huatuo26M-Lite")
    ax.set_xlabel("Records")
    ax.bar_label(bars, labels=[f"{value:,}" for value in values], padding=4)
    ax.grid(axis="x", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_total_time_pie(path: Path, title: str, output: Path) -> None:
    timings = read_timings(path)
    totals = {
        framework: sum(float(timings[case_id][framework]["elapsed_seconds"]) for case_id in ["1", "2", "3", "4"])
        for framework in ["hadoop_streaming_yarn", "spark_submit_yarn"]
    }
    labels = [f"Hadoop Streaming\n{totals['hadoop_streaming_yarn']:.1f}s", f"Spark\n{totals['spark_submit_yarn']:.1f}s"]
    values = [totals["hadoop_streaming_yarn"], totals["spark_submit_yarn"]]

    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=170)
    wedges, _, autotexts = ax.pie(
        values,
        labels=labels,
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=105,
        colors=[COLORS["blue"], COLORS["orange"]],
        wedgeprops={"linewidth": 1.2, "edgecolor": "white"},
        textprops={"fontsize": 10},
    )
    for text in autotexts:
        text.set_color("white")
        text.set_fontweight("bold")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_speedup_chart(path: Path, output: Path) -> None:
    timings = read_timings(path)
    case_ids = ["1", "2", "3", "4"]
    labels = [CASE_NAMES[case_id] for case_id in case_ids]
    values = []
    colors = []
    for case_id in case_ids:
        hadoop = float(timings[case_id]["hadoop_streaming_yarn"]["elapsed_seconds"])
        spark = float(timings[case_id]["spark_submit_yarn"]["elapsed_seconds"])
        percent = (hadoop - spark) / hadoop * 100
        values.append(percent)
        colors.append(COLORS["green"] if percent >= 0 else COLORS["orange"])

    fig, ax = plt.subplots(figsize=(10.8, 5.8), dpi=170)
    bars = ax.barh(labels, values, color=colors, edgecolor=COLORS["ink"], linewidth=1.0)
    ax.axvline(0, color=COLORS["ink"], linewidth=1)
    ax.set_title("Spark Relative Time Improvement on Full Dataset")
    ax.set_xlabel("Improvement versus Hadoop Streaming (%)")
    ax.bar_label(bars, labels=[f"{value:+.1f}%" for value in values], padding=4)
    ax.grid(axis="x", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_output_groups_chart(path: Path, output: Path) -> None:
    timings = read_timings(path)
    case_ids = ["1", "2", "3", "4"]
    labels = [CASE_LABELS[case_id] for case_id in case_ids]
    values = [int(timings[case_id]["hadoop_streaming_yarn"]["output_records"]) for case_id in case_ids]

    fig, ax = plt.subplots(figsize=(9.8, 5.4), dpi=170)
    bars = ax.bar(labels, values, color=COLORS["blue"], edgecolor=COLORS["ink"], linewidth=1.0)
    ax.set_yscale("log")
    ax.set_title("Output Group Counts by Case Study")
    ax.set_ylabel("Output groups, log scale")
    ax.bar_label(bars, labels=[f"{value:,}" for value in values], padding=3)
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def box(ax, xy: tuple[float, float], text: str, width: float = 2.5, height: float = 0.72, color: str = "#edf4f8") -> None:
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=1.1,
        edgecolor="#9fb4c3",
        facecolor=color,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=9, color=COLORS["ink"])


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.2,
            color="#617685",
        )
    )


def custom_box(ax, node: dict) -> None:
    box(
        ax,
        (node["x"], node["y"]),
        node["text"],
        width=node.get("w", 2.2),
        height=node.get("h", 0.68),
        color=node.get("color", "#edf4f8"),
    )


def node_anchor(node: dict, side: str) -> tuple[float, float]:
    x, y = node["x"], node["y"]
    w, h = node.get("w", 2.2), node.get("h", 0.68)
    if side == "left":
        return (x, y + h / 2)
    if side == "right":
        return (x + w, y + h / 2)
    if side == "top":
        return (x + w / 2, y + h)
    if side == "bottom":
        return (x + w / 2, y)
    return (x + w / 2, y + h / 2)


def save_custom_dfd(title: str, nodes: list[dict], edges: list[tuple[str, str, str, str]], output: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.2, 5.8), dpi=170)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.8)
    ax.axis("off")
    ax.text(0.2, 5.35, title, fontsize=15, fontweight="bold", color=COLORS["ink"])
    lookup = {node["id"]: node for node in nodes}
    for node in nodes:
        custom_box(ax, node)
    for source, target, source_side, target_side in edges:
        arrow(ax, node_anchor(lookup[source], source_side), node_anchor(lookup[target], target_side))
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_dfd(title: str, steps: list[str], output: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.8), dpi=170)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.8)
    ax.axis("off")
    ax.text(0.2, 4.45, title, fontsize=15, fontweight="bold", color=COLORS["ink"])

    positions = [(0.35, 2.7), (3.0, 2.7), (5.65, 2.7), (8.3, 2.7), (8.3, 1.15)]
    colors = ["#edf4f8", "#fff3e3", "#edf4f8", "#ecf7f2", "#f5f1ff"]
    for pos, step, color in zip(positions, steps, colors):
        box(ax, pos, step, color=color)

    arrow(ax, (2.85, 3.06), (3.0, 3.06))
    arrow(ax, (5.5, 3.06), (5.65, 3.06))
    arrow(ax, (8.15, 3.06), (8.3, 3.06))
    arrow(ax, (9.55, 2.7), (9.55, 1.9))

    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_spark_dfd(title: str, steps: list[str], output: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=170)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    ax.text(0.2, 4.82, title, fontsize=15, fontweight="bold", color=COLORS["ink"])

    positions = [(0.45, 3.35), (3.15, 3.35), (5.85, 3.35), (5.85, 1.72), (8.45, 1.72)]
    colors = ["#edf4f8", "#fff3e3", "#ecf7f2", "#f5f1ff", "#edf4f8"]
    for pos, step, color in zip(positions, steps, colors):
        box(ax, pos, step, color=color)

    arrow(ax, (2.95, 3.72), (3.15, 3.72))
    arrow(ax, (5.65, 3.72), (5.85, 3.72))
    arrow(ax, (7.1, 3.35), (7.1, 2.47))
    arrow(ax, (8.35, 2.08), (8.45, 2.08))

    ax.text(
        6.95,
        2.72,
        "Spark execution plan",
        ha="center",
        va="center",
        fontsize=8,
        color="#617685",
    )

    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def save_data_flow_diagrams() -> None:
    blue = "#edf4f8"
    orange = "#fff3e3"
    green = "#ecf7f2"
    purple = "#f5f1ff"
    red = "#fff0f0"

    save_custom_dfd(
        "Hadoop DFD: Case Study 1 Department Demand",
        [
            {"id": "input", "x": 0.3, "y": 2.45, "text": "Canonical JSONL\nrecords", "color": blue},
            {"id": "map", "x": 2.7, "y": 2.45, "text": "Mapper\nread record", "color": orange},
            {"id": "observed", "x": 5.1, "y": 3.35, "text": "Observed department\nfrom metadata", "color": green},
            {"id": "infer", "x": 5.1, "y": 1.55, "text": "No metadata:\ninfer from disease rules", "color": purple},
            {"id": "emit", "x": 7.65, "y": 2.45, "text": "Emit\n(department, origin) -> 1", "w": 2.45, "color": blue},
            {"id": "reduce", "x": 10.2, "y": 2.45, "text": "Reducer\nsum and rank", "w": 1.7, "color": green},
        ],
        [("input", "map", "right", "left"), ("map", "observed", "right", "left"), ("map", "infer", "right", "left"), ("observed", "emit", "right", "left"), ("infer", "emit", "right", "left"), ("emit", "reduce", "right", "left")],
        FIGURES / "dfd_case_study_1_department_demand.png",
    )

    save_custom_dfd(
        "Hadoop DFD: Case Study 2 Disease and Symptom Trends",
        [
            {"id": "input", "x": 0.3, "y": 2.45, "text": "Canonical JSONL\nquestion + text answer", "w": 2.35, "color": blue},
            {"id": "map", "x": 2.95, "y": 2.45, "text": "Mapper\nbuild searchable text", "w": 2.25, "color": orange},
            {"id": "disease", "x": 5.55, "y": 3.45, "text": "Disease matcher\n+ observed disease", "color": green},
            {"id": "symptom", "x": 5.55, "y": 1.45, "text": "Symptom matcher\nfrom rules", "color": purple},
            {"id": "emitd", "x": 8.0, "y": 3.45, "text": "Emit disease\n(term, disease)", "color": blue},
            {"id": "emits", "x": 8.0, "y": 1.45, "text": "Emit symptom\n(term, symptom)", "color": blue},
            {"id": "reduce", "x": 10.25, "y": 2.45, "text": "Reducer\nfrequency counts", "w": 1.75, "color": green},
        ],
        [("input", "map", "right", "left"), ("map", "disease", "right", "left"), ("map", "symptom", "right", "left"), ("disease", "emitd", "right", "left"), ("symptom", "emits", "right", "left"), ("emitd", "reduce", "right", "left"), ("emits", "reduce", "right", "left")],
        FIGURES / "dfd_case_study_2_disease_symptom_trends.png",
    )

    save_custom_dfd(
        "Hadoop DFD: Case Study 3 QA Quality and Completeness",
        [
            {"id": "input", "x": 0.25, "y": 2.35, "text": "Canonical JSONL\nall sources", "color": blue},
            {"id": "map", "x": 2.65, "y": 2.35, "text": "Mapper\ncreate metrics object", "w": 2.35, "color": orange},
            {"id": "flags", "x": 5.35, "y": 3.55, "text": "Flags\nmissing, URL, duplicate", "w": 2.25, "color": red},
            {"id": "sums", "x": 5.35, "y": 2.35, "text": "Sums\nlengths and scores", "w": 2.25, "color": green},
            {"id": "minmax", "x": 5.35, "y": 1.15, "text": "Min/Max\nquality scores", "w": 2.25, "color": purple},
            {"id": "reduce", "x": 8.15, "y": 2.35, "text": "Reducer by source\ncombine metric objects", "w": 2.25, "color": blue},
            {"id": "output", "x": 10.65, "y": 2.35, "text": "Output\nrates, avg, min/max", "w": 1.35, "color": green},
        ],
        [("input", "map", "right", "left"), ("map", "flags", "right", "left"), ("map", "sums", "right", "left"), ("map", "minmax", "right", "left"), ("flags", "reduce", "right", "left"), ("sums", "reduce", "right", "left"), ("minmax", "reduce", "right", "left"), ("reduce", "output", "right", "left")],
        FIGURES / "dfd_case_study_3_qa_quality.png",
    )

    save_custom_dfd(
        "Hadoop DFD: Case Study 4 Question-Type Distribution",
        [
            {"id": "input", "x": 0.3, "y": 2.4, "text": "Canonical JSONL\nquestion field", "color": blue},
            {"id": "map", "x": 2.65, "y": 2.4, "text": "Mapper\nrule-based classifier", "w": 2.3, "color": orange},
            {"id": "known", "x": 5.25, "y": 3.35, "text": "Matched intent\ntreatment/diagnosis/...", "w": 2.45, "color": green},
            {"id": "other", "x": 5.25, "y": 1.45, "text": "No matched rule\ncategory = other", "w": 2.45, "color": purple},
            {"id": "shuffle", "x": 8.05, "y": 2.4, "text": "Shuffle/group\nby question_type", "w": 2.05, "color": blue},
            {"id": "reduce", "x": 10.45, "y": 2.4, "text": "Reducer\nsum category counts", "w": 1.45, "color": green},
        ],
        [("input", "map", "right", "left"), ("map", "known", "right", "left"), ("map", "other", "right", "left"), ("known", "shuffle", "right", "left"), ("other", "shuffle", "right", "left"), ("shuffle", "reduce", "right", "left")],
        FIGURES / "dfd_case_study_4_question_type.png",
    )

    save_custom_dfd(
        "Spark DFD: Case Study 1 Department Demand",
        [
            {"id": "driver", "x": 0.3, "y": 4.25, "text": "Driver\nbuild Spark plan", "w": 2.0, "color": purple},
            {"id": "read", "x": 0.3, "y": 2.2, "text": "read.json\nHDFS input", "w": 1.9, "color": blue},
            {"id": "obs", "x": 2.75, "y": 3.25, "text": "DataFrame A\nobserved departments", "w": 2.25, "color": green},
            {"id": "inf", "x": 2.75, "y": 1.25, "text": "DataFrame B\nUDF inferred departments", "w": 2.25, "color": orange},
            {"id": "union", "x": 5.5, "y": 2.2, "text": "unionByName\nobserved + inferred", "w": 2.25, "color": blue},
            {"id": "group", "x": 8.0, "y": 2.2, "text": "groupBy\n.department, origin", "w": 2.0, "color": green},
            {"id": "write", "x": 10.45, "y": 2.2, "text": "write JSON\ncount output", "w": 1.45, "color": purple},
        ],
        [("driver", "read", "bottom", "top"), ("read", "obs", "right", "left"), ("read", "inf", "right", "left"), ("obs", "union", "right", "left"), ("inf", "union", "right", "left"), ("union", "group", "right", "left"), ("group", "write", "right", "left")],
        FIGURES / "dfd_spark_case_study_1_department_demand.png",
    )

    save_custom_dfd(
        "Spark DFD: Case Study 2 Disease and Symptom Trends",
        [
            {"id": "read", "x": 0.3, "y": 2.35, "text": "read.json\nquestion + answer", "color": blue},
            {"id": "udf", "x": 2.75, "y": 2.35, "text": "UDFs\nreturn arrays of terms", "w": 2.2, "color": orange},
            {"id": "darr", "x": 5.35, "y": 3.4, "text": "matched_diseases\narray", "w": 2.1, "color": green},
            {"id": "sarr", "x": 5.35, "y": 1.3, "text": "matched_symptoms\narray", "w": 2.1, "color": purple},
            {"id": "explode", "x": 7.9, "y": 2.35, "text": "explode arrays\none row per term", "w": 2.05, "color": blue},
            {"id": "group", "x": 10.15, "y": 2.35, "text": "groupBy term\ncount", "w": 1.6, "color": green},
        ],
        [("read", "udf", "right", "left"), ("udf", "darr", "right", "left"), ("udf", "sarr", "right", "left"), ("darr", "explode", "right", "left"), ("sarr", "explode", "right", "left"), ("explode", "group", "right", "left")],
        FIGURES / "dfd_spark_case_study_2_disease_symptom_trends.png",
    )

    save_custom_dfd(
        "Spark DFD: Case Study 3 QA Quality and Completeness",
        [
            {"id": "read", "x": 0.25, "y": 2.4, "text": "read.json\nall records", "color": blue},
            {"id": "expr", "x": 2.7, "y": 3.3, "text": "Column expressions\nflags and lengths", "w": 2.25, "color": orange},
            {"id": "score", "x": 2.7, "y": 1.45, "text": "Quality score\nnumeric columns", "w": 2.25, "color": purple},
            {"id": "agg", "x": 5.55, "y": 2.4, "text": "groupBy source\nagg count/sum/avg/min/max", "w": 2.55, "color": green},
            {"id": "derive", "x": 8.45, "y": 2.4, "text": "withColumn\nderive percentages", "w": 2.0, "color": blue},
            {"id": "write", "x": 10.75, "y": 2.4, "text": "write JSON\nsource metrics", "w": 1.25, "color": purple},
        ],
        [("read", "expr", "right", "left"), ("read", "score", "right", "left"), ("expr", "agg", "right", "left"), ("score", "agg", "right", "left"), ("agg", "derive", "right", "left"), ("derive", "write", "right", "left")],
        FIGURES / "dfd_spark_case_study_3_qa_quality.png",
    )

    save_custom_dfd(
        "Spark DFD: Case Study 4 Question-Type Distribution",
        [
            {"id": "read", "x": 0.3, "y": 2.4, "text": "read.json\nquestions", "color": blue},
            {"id": "udf", "x": 2.65, "y": 2.4, "text": "classify UDF\nscan intent rules", "w": 2.1, "color": orange},
            {"id": "col", "x": 5.1, "y": 2.4, "text": "withColumn\nquestion_type", "w": 2.0, "color": purple},
            {"id": "cats", "x": 7.35, "y": 3.45, "text": "Named categories\ntreatment, diagnosis...", "w": 2.2, "color": green},
            {"id": "other", "x": 7.35, "y": 1.35, "text": "Fallback category\nother", "w": 2.2, "color": red},
            {"id": "group", "x": 10.0, "y": 2.4, "text": "groupBy type\ncount + write", "w": 1.75, "color": blue},
        ],
        [("read", "udf", "right", "left"), ("udf", "col", "right", "left"), ("col", "cats", "right", "left"), ("col", "other", "right", "left"), ("cats", "group", "right", "left"), ("other", "group", "right", "left")],
        FIGURES / "dfd_spark_case_study_4_question_type.png",
    )


def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    summary = load_summary()
    save_grouped_timing_chart(PILOT_TIMINGS, "Pilot Benchmark on HDFS/YARN (400,000 Records)", FIGURES / "pilot_execution_time.png")
    save_grouped_timing_chart(FULL_TIMINGS, "Full Benchmark on HDFS/YARN (34,048,898 Records)", FIGURES / "full_execution_time.png")
    save_source_distribution(summary, FIGURES / "source_distribution.png")
    save_answer_type_chart(summary, FIGURES / "answer_type_distribution.png")
    save_duplicate_chart(summary, FIGURES / "duplicate_records.png")
    save_top_departments(summary, FIGURES / "top_departments.png")
    save_total_time_pie(FULL_TIMINGS, "Total Full Benchmark Time Share", FIGURES / "full_total_time_share.png")
    save_speedup_chart(FULL_TIMINGS, FIGURES / "full_spark_speedup.png")
    save_output_groups_chart(FULL_TIMINGS, FIGURES / "full_output_groups.png")
    save_data_flow_diagrams()
    print(f"Wrote report figures to {FIGURES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
