# Report Tables

These tables are generated from frozen project evidence files.

## Dataset Sources

| Source | Records | Size | Main fields |
| ------ | ------: | ---: | ----------- |
| Consultation QA | 32,708,346 | 4.537 GB | `questions`, `answers` |
| Encyclopedia QA | 364,420 | 0.608 GB | `questions`, `answers` |
| Knowledge Graph QA | 798,444 | 0.149 GB | `questions`, `answers` |
| Huatuo26M-Lite | 177,703 | 0.138 GB | `id`, `question`, `answer`, `score`, `label`, `related_diseases` |
| **Combined** | **34,048,913** | **5.432 GB** | Heterogeneous medical QA records |

## Full Canonical Dataset Summary

| Metric | Value |
| ------ | ----: |
| Records | 34,048,898 |
| File size | 20,168,846,076 bytes, about 19 GB |
| Invalid JSON lines | 0 |
| Duplicate-flagged records | 10,162,575 |
| Duplicate percentage | 29.847% |
| URL answers | 32,708,326 |
| Text answers | 1,340,572 |
| Missing questions | 0 |
| Missing answers | 0 |

## Aggregation Techniques by Case Study

| Case study | Grouping key | Main techniques | Aggregation output |
| ---------- | ------------ | --------------- | ------------------ |
| Department demand | `department`, `metadata_origin` | filtering, projection, key-value mapping, grouping, count aggregation, ranking | department demand counts |
| Disease and symptom trends | `term_type`, `matched_term` | text scanning, pattern matching, term extraction, grouping, count aggregation, frequency ranking | disease/symptom frequency counts |
| QA quality and completeness | `source` | source partitioning, URL/text classification, missing-value detection, duplicate aggregation, length aggregation, min/max/average, percentages | source-level quality summary |
| Question-type distribution | `question_type` | rule-based classification, keyword matching, grouping, count aggregation | question category distribution |

## Big Data Analytics Lifecycle Mapping

| Lifecycle stage | Project implementation |
| --------------- | ---------------------- |
| Data generation | Huatuo medical QA source repositories |
| Data aggregation | Downloaded four source snapshots into `data/source/` |
| Data preprocessing | JSONL parsing, field extraction, text formatting cleanup |
| Data integration | Canonical schema normalization and union, not join |
| Data cleaning | Missing-value handling, invalid JSON validation, URL/text answer typing |
| Data reduction | Deterministic 400,000-record pilot for validation |
| Data transformation | Canonical JSONL with derived lengths, hashes, duplicate flags, and metadata fields |
| Data analytics | Four Hadoop Streaming and Spark case studies on HDFS/YARN |

### Pilot HDFS/YARN Benchmark

| Case study | Output groups | Hadoop Streaming on YARN | Spark on YARN | Faster |
| ---------- | ------------: | -----------------------: | ------------: | ------ |
| Department demand | 16 | 18.763 s | 29.630 s | Hadoop |
| Disease and symptom trends | 2,301 | 18.558 s | 31.256 s | Hadoop |
| QA quality and completeness | 4 | 19.602 s | 25.309 s | Hadoop |
| Question-type distribution | 7 | 18.560 s | 23.310 s | Hadoop |

### Full HDFS/YARN Benchmark

| Case study | Output groups | Hadoop Streaming on YARN | Spark on YARN | Faster |
| ---------- | ------------: | -----------------------: | ------------: | ------ |
| Department demand | 16 | 128.071 s | 117.327 s | Spark |
| Disease and symptom trends | 2,711 | 139.457 s | 149.503 s | Hadoop |
| QA quality and completeness | 4 | 273.549 s | 82.296 s | Spark |
| Question-type distribution | 7 | 204.027 s | 113.497 s | Spark |
