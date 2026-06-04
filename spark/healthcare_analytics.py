#!/usr/bin/env python3
"""Equivalent PySpark implementations for all four healthcare case studies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyspark.sql import SparkSession, functions as F, types as T


def load_rules(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def resolve_input(path: str) -> str:
    candidate = Path(path)
    if "://" not in path and candidate.exists():
        return "file://" + candidate.resolve().as_posix()
    return path


def resolve_output(path: str) -> str:
    if "://" not in path and not path.startswith("/"):
        return "file://" + Path(path).resolve().as_posix()
    return path


def case_study_1(df, rules):
    diseases = rules.get("diseases", [])
    disease_departments = rules.get("disease_departments", {})

    def infer_departments(question):
        folded = (question or "").casefold()
        return sorted(
            {
                disease_departments[disease]
                for disease in diseases
                if disease.casefold() in folded and disease in disease_departments
            }
        )

    infer_udf = F.udf(infer_departments, T.ArrayType(T.StringType()))
    observed = (
        df.where(F.coalesce("department", "inferred_department").isNotNull())
        .select(
            F.coalesce("department", "inferred_department").alias("department"),
            F.when(F.col("department").isNotNull(), "observed")
            .otherwise("inferred")
            .alias("origin"),
        )
    )
    inferred = (
        df.where(F.coalesce("department", "inferred_department").isNull())
        .withColumn("departments", infer_udf("question"))
        .select(F.explode("departments").alias("department"))
        .withColumn("origin", F.lit("inferred"))
    )
    return (
        observed.unionByName(inferred)
        .groupBy("department", "origin")
        .count()
        .orderBy(F.desc("count"), "department")
    )


def case_study_2(df, rules):
    symptom_udf = F.udf(
        lambda q, a, t: [
            term
            for term in rules.get("symptoms", [])
            if term.casefold() in f"{q or ''} {a if t == 'text' else ''}".casefold()
        ],
        T.ArrayType(T.StringType()),
    )
    disease_udf = F.udf(
        lambda q, a, t, observed: sorted(
            {
                *(
                    [observed]
                    if observed
                    else []
                ),
                *[
                    disease
                    for disease in rules.get("diseases", [])
                    if disease.casefold()
                    in f"{q or ''} {a if t == 'text' else ''}".casefold()
                ],
            }
        ),
        T.ArrayType(T.StringType()),
    )
    diseases = (
        df.withColumn(
            "matched_diseases",
            disease_udf(
                "question",
                "answer",
                "answer_type",
                F.coalesce("related_disease", "inferred_disease"),
            ),
        )
        .select(F.explode("matched_diseases").alias("term"))
        .withColumn("term_type", F.lit("disease"))
    )
    symptoms = (
        df.withColumn(
            "matched", symptom_udf("question", "answer", "answer_type")
        )
        .select(F.explode("matched").alias("term"))
        .withColumn("term_type", F.lit("symptom"))
    )
    return (
        diseases.unionByName(symptoms)
        .groupBy("term_type", "term")
        .count()
        .orderBy(F.desc("count"), "term")
    )


def case_study_3(df):
    score = F.col("quality_score")
    return (
        df.groupBy("source")
        .agg(
            F.count("*").alias("records"),
            F.sum(F.col("question").isNull().cast("int")).alias("empty_questions"),
            F.sum((F.col("answer_type") == "empty").cast("int")).alias("empty_answers"),
            F.sum((F.col("answer_type") == "url").cast("int")).alias("url_answers"),
            F.sum(F.col("duplicate_flag").cast("int")).alias("duplicates"),
            F.avg("question_length").alias("average_question_length"),
            F.avg("answer_length").alias("average_answer_length"),
            F.avg(score).alias("score_average"),
            F.min(score).alias("score_min"),
            F.max(score).alias("score_max"),
        )
        .withColumn("duplicate_percentage", 100 * F.col("duplicates") / F.col("records"))
        .withColumn("url_answer_percentage", 100 * F.col("url_answers") / F.col("records"))
        .orderBy("source")
    )


def case_study_4(df, rules):
    patterns = rules.get("question_types", {})

    def classify(question):
        folded = (question or "").casefold()
        for category in sorted(patterns):
            if any(term.casefold() in folded for term in patterns[category]):
                return category
        return "other"

    classify_udf = F.udf(classify, T.StringType())
    return (
        df.withColumn("question_type", classify_udf("question"))
        .groupBy("question_type")
        .count()
        .orderBy(F.desc("count"), "question_type")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-study", choices=("1", "2", "3", "4"), required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rules", default="config/analytics_rules.json")
    parser.add_argument("--master")
    args = parser.parse_args()

    builder = SparkSession.builder.appName(f"healthcare-case-study-{args.case_study}")
    if args.master:
        builder = builder.master(args.master)
    spark = builder.getOrCreate()
    rules = load_rules(args.rules)
    df = spark.read.json(resolve_input(args.input))
    jobs = {
        "1": lambda: case_study_1(df, rules),
        "2": lambda: case_study_2(df, rules),
        "3": lambda: case_study_3(df),
        "4": lambda: case_study_4(df, rules),
    }
    result = jobs[args.case_study]()
    result.write.mode("overwrite").json(resolve_output(args.output))
    spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
