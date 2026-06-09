# Huatuo Big Data Processing Project

This repository implements a large-scale healthcare analytics pipeline for the
Huatuo medical QA datasets. It standardizes four heterogeneous Huatuo sources
into one canonical JSONL dataset, then runs equivalent analytical workloads with
Hadoop Streaming and Apache Spark on HDFS/YARN.

The project was built for WOC7017 Big Data Processing and is designed to show:

- Big-data preprocessing on a dataset larger than 2 GB.
- Schema normalization and union of heterogeneous medical QA sources.
- Four MapReduce-style healthcare analytics case studies.
- Equivalent Hadoop Streaming and PySpark implementations.
- HDFS/YARN benchmark results comparing Hadoop and Spark.

## Dataset

The project uses four Huatuo source repositories:

| Source             | Main fields                                                      |        Records |         Size |
| ------------------ | ---------------------------------------------------------------- | -------------: | -----------: |
| Consultation QA    | `questions`, `answers`                                           |     32,708,346 |     4.537 GB |
| Encyclopedia QA    | `questions`, `answers`                                           |        364,420 |     0.608 GB |
| Knowledge Graph QA | `questions`, `answers`                                           |        798,444 |     0.149 GB |
| Huatuo26M-Lite     | `id`, `question`, `answer`, `score`, `label`, `related_diseases` |        177,703 |     0.138 GB |
| **Combined**       | Heterogeneous medical QA records                                 | **34,048,913** | **5.432 GB** |

The combined original source snapshot is:

```text
5,431,518,498 bytes
5.432 decimal GB
5.058 GiB
```

The source files are JSONL. No Pandas conversion is required for the production
pipeline because Python, Hadoop Streaming, and Spark can read JSONL directly.

## Data Integration Method

The Huatuo sources are integrated by **schema normalization and union**, not by
joining records.

A join would imply that records from different sources describe the same
patient, consultation, or medical event. The datasets do not provide a reliable
shared patient ID, consultation ID, or universal question ID. To avoid creating
false relationships, each record is preserved as a separate medical QA
observation.

The integration logic is:

```text
Original Huatuo source JSONL files
                |
                v
Normalize different source schemas
                |
                v
Create one canonical JSONL schema
                |
                v
Union all standardized records
                |
                v
Upload standardized data to HDFS
                |
                v
Run equivalent Hadoop and Spark analytics
```

Source provenance is retained in `source` and `source_split`. Missing metadata
is represented as `null`, and duplicate questions are flagged using a normalized
question hash.

## Canonical Schema

Every source record is mapped into this common structure:

```json
{
  "record_id": "source-specific-id",
  "source": "consultation",
  "source_split": "train",
  "question": "Normalized question text",
  "answer": "Normalized answer text or URL",
  "answer_type": "text",
  "department": null,
  "related_disease": null,
  "quality_score": null,
  "metadata_origin": "unavailable",
  "question_length": 25,
  "answer_length": 100,
  "question_hash": "sha256-value",
  "duplicate_flag": false
}
```

Question normalization is formatting cleanup only. It does not translate,
rewrite, medically correct, or change question meaning.

The normalization step:

- Converts missing values to an empty string.
- Joins list-valued questions into one string.
- Converts dictionary-valued questions into JSON text.
- Replaces repeated whitespace with one space.
- Removes leading and trailing spaces.

For duplicate detection, the normalized question is casefolded and hashed with
SHA-256. This flags questions that differ only by spacing or capitalization.

## Project Structure

```text
config/          Shared case-study rules used by Hadoop and Spark
data/samples/    Small sample records for inspection
hadoop/          Hadoop Streaming mapper and reducer
preprocessing/   Download, standardize, union, and validation code
reports/         Source integrity and analytics summary evidence
scripts/         Reproducible terminal commands
spark/           Equivalent PySpark analytics implementation
README.md        Short operational entry point
journey.md       Detailed project guide
```

The following directories are intentionally ignored by Git because they contain
large local data, private reference documents, or generated outputs:

```text
.venv/
data/source/
data/pilot/
data/processed-pilot/
data/standardized-full/
docs/
results/
```

## Case Studies

### 1. Medical Department Demand

Counts observed department labels from Huatuo26M-Lite.

MapReduce behavior:

- Map: emit department keys with value `1`.
- Reduce: sum counts for each department.
- Output: department demand distribution.

### 2. Disease and Symptom Trend Mining

Counts disease and symptom mentions in medical questions and textual answers.

MapReduce behavior:

- Map: search text for configured disease and symptom terms, then emit term keys.
- Reduce: sum counts for each disease or symptom term.
- Output: disease and symptom frequency table.

### 3. Medical QA Quality and Completeness

Compares source-level completeness and quality characteristics.

Metrics include:

- Empty questions.
- Empty answers.
- URL-only answers.
- Duplicate questions.
- Average question and answer lengths.
- Huatuo26M-Lite score statistics.

MapReduce behavior:

- Map: emit one source-level quality record per input row.
- Reduce: aggregate counts, averages, percentages, min score, and max score.
- Output: one quality summary per source.

### 4. Question-Type Distribution

Classifies medical questions into configured categories such as treatment,
diagnosis, symptoms, medication, prevention, cause, or other.

MapReduce behavior:

- Map: classify each question and emit the category with value `1`.
- Reduce: sum counts for each question type.
- Output: question-type distribution.

## Environment

Create and activate the local Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

For an existing environment, only activate it:

```bash
source .venv/bin/activate
```

## Source Data Inspection

Inspect downloaded source sizes, record counts, and samples:

```bash
bash scripts/inspect_source_data.sh summary
bash scripts/inspect_source_data.sh samples
```

Create the source integrity manifest:

```bash
bash scripts/create_source_manifest.sh
```

Generated evidence:

```text
reports/source_manifest.csv
reports/source_manifest.json
```

The manifest records each original JSONL file path, byte size, record count, and
SHA-256 checksum.

## Pilot Pipeline

The pilot is a deterministic 400,000-record real-data subset used to validate
the pipeline before running the full dataset.

It contains 100,000 records from each source:

| Source          | Validation |      Test |   Train/Full |       Total |
| --------------- | ---------: | --------: | -----------: | ----------: |
| Consultation    |      1,000 |     1,000 | 98,000 train |     100,000 |
| Encyclopedia    |      1,000 |     1,000 | 98,000 train |     100,000 |
| Knowledge Graph |      1,000 |     1,000 | 98,000 train |     100,000 |
| Lite            |        N/A |       N/A | 100,000 full |     100,000 |
| **Combined**    |  **3,000** | **3,000** |  **394,000** | **400,000** |

Create and process the pilot:

```bash
bash scripts/create_pilot.sh
bash scripts/prepare_data.sh data/pilot data/processed-pilot
```

Pilot output:

```text
data/processed-pilot/huatuo_unified.jsonl
```

Pilot preprocessing result:

| Metric                       |  Result |
| ---------------------------- | ------: |
| Input records                | 400,000 |
| Unified output records       | 400,000 |
| Text answers                 | 300,000 |
| URL answers                  | 100,000 |
| Observed metadata records    | 100,000 |
| Metadata-unavailable records | 300,000 |
| Duplicate questions detected |     709 |
| Duplicate percentage         | 0.1772% |
| Validation status            |   Valid |

## Full Dataset Pipeline

Prepare the complete canonical dataset:

```bash
bash scripts/prepare_full_data.sh data/source data/standardized-full
```

Full canonical output:

```text
data/standardized-full/huatuo_unified.jsonl
```

The full preprocessing command performs:

- Schema normalization for every source split.
- Text normalization for question and answer fields.
- Union into one canonical JSONL file.
- Cross-source duplicate flagging using normalized `question_hash`.
- Validation of the final canonical file.

Observed preprocessing runtime:

```text
Full preprocessing runtime: approximately 2 hours 23 minutes
Measured window: 2026-06-06 16:17:30 to about 18:40 +08
Union output write phase: 2 hours 20 minutes 26 seconds
```

The runtime was measured from observed output-file timestamps and command
completion polling. For a formal rerun, wrap the command with `/usr/bin/time`.

## Full Dataset Inspection

Inspect the complete canonical dataset before submitting Hadoop or Spark jobs:

```bash
bash scripts/summarize_full_data.sh
```

This creates:

```text
reports/full_summary.json
data/samples/full-canonical/
```

Full canonical inspection result:

| Metric                    |                             Value |
| ------------------------- | --------------------------------: |
| Final canonical records   |                        34,048,898 |
| Final canonical file size | 20,168,846,076 bytes, about 19 GB |
| Invalid JSON lines        |                                 0 |
| Duplicate-flagged records |                        10,162,575 |
| Duplicate percentage      |                           29.847% |
| URL answers               |                        32,708,326 |
| Text answers              |                         1,340,572 |
| Missing questions         |                                 0 |
| Missing answers           |                                 0 |

Source distribution:

| Source             |    Records |
| ------------------ | ---------: |
| Consultation QA    | 32,708,331 |
| Encyclopedia QA    |    364,420 |
| Knowledge Graph QA |    798,444 |
| Huatuo26M-Lite     |    177,703 |

## Storage Notes

The raw source snapshot is about 5.4 GB, while the canonical dataset is about
19 GB. This is expected because the canonical JSONL adds provenance, quality,
length, hash, and duplicate metadata to every row. JSONL also repeats field
names on every record.

During preprocessing, the working directory temporarily reached about 41 GB
because it contained both intermediate standardized files and the final unified
file. After validation and HDFS upload, temporary intermediate files were
removed. The final local full-data artifact is:

```text
data/standardized-full/huatuo_unified.jsonl
```

## HDFS Staging

Start Hadoop services:

```bash
start-dfs.sh
start-yarn.sh
```

If ResourceManager is not reachable after `start-yarn.sh`, run it in a separate
terminal during benchmarking:

```bash
yarn resourcemanager
```

Upload the pilot input:

```bash
bash scripts/upload_to_hdfs.sh \
  data/processed-pilot/huatuo_unified.jsonl \
  /healthcare/pilot/input
```

Upload the full input:

```bash
bash scripts/upload_to_hdfs.sh \
  data/standardized-full/huatuo_unified.jsonl \
  /healthcare/full/input
```

Verify the full HDFS input:

```bash
hdfs dfs -ls -h /healthcare/full/input/huatuo_unified.jsonl
```

Verified full HDFS input from this project run:

```text
-rw-r--r--   1 muammar.jsx supergroup  18.8 G  2026-06-06 20:54  /healthcare/full/input/huatuo_unified.jsonl
```

## Benchmark Commands

Run the pilot HDFS/YARN benchmark:

```bash
bash scripts/run_case_benchmark.sh cluster
```

Run the full HDFS/YARN benchmark:

```bash
bash scripts/run_full_case_benchmark.sh
```

We can limit it like this:

```bash
bash scripts/run_full_case_benchmark.sh hadoop
bash scripts/run_full_case_benchmark.sh spark
bash scripts/run_full_case_benchmark.sh hadoop 3,4
```

Results:

```bash
ls -lh results/full-benchmark/outputs
```

Print outputs:

```bash
head results/full-benchmark/outputs/hadoop-cs1.jsonl
head results/full-benchmark/outputs/spark-cs1.jsonl
.
.
.
```

Run only one framework:

```bash
bash scripts/run_full_case_benchmark.sh hadoop
bash scripts/run_full_case_benchmark.sh spark
```

Run selected case studies:

```bash
bash scripts/run_full_case_benchmark.sh hadoop 3,4
bash scripts/run_full_case_benchmark.sh spark 1,2,3,4
```

The benchmark output CSV format is:

```text
framework,mode,case_study,elapsed_seconds,output_records,input,output
```

Regenerate the full benchmark chart:

```bash
MPLCONFIGDIR=.matplotlib-cache \
  .venv/bin/python scripts/generate_benchmark_chart.py
```

## Benchmark Results

Full HDFS/YARN benchmark on the 34,048,898-record canonical dataset:

![Full Huatuo HDFS/YARN benchmark chart](reports/full_benchmark_chart.png)

| Case study                  | Output groups | Hadoop Streaming on YARN | Spark on YARN |
| --------------------------- | ------------: | -----------------------: | ------------: |
| Department demand           |            16 |                128.071 s |     117.327 s |
| Disease and symptom trends  |         2,711 |                139.457 s |     149.503 s |
| QA quality and completeness |             4 |                273.549 s |      82.296 s |
| Question-type distribution  |             7 |                204.027 s |     113.497 s |

Timing file:

```text
results/case-benchmark/timings-full-cluster-20260607-171724.csv
```

Local output copies:

```text
results/full-benchmark/outputs/hadoop-cs1.jsonl
results/full-benchmark/outputs/hadoop-cs2.jsonl
results/full-benchmark/outputs/hadoop-cs3.jsonl
results/full-benchmark/outputs/hadoop-cs4.jsonl
results/full-benchmark/outputs/spark-cs1.jsonl
results/full-benchmark/outputs/spark-cs2.jsonl
results/full-benchmark/outputs/spark-cs3.jsonl
results/full-benchmark/outputs/spark-cs4.jsonl
```

Output row counts match between Hadoop and Spark for every case study:

| Case study | Hadoop rows | Spark rows |
| ---------- | ----------: | ---------: |
| 1          |          16 |         16 |
| 2          |       2,711 |      2,711 |
| 3          |           4 |          4 |
| 4          |           7 |          7 |

Pilot HDFS/YARN benchmark on the 400,000-record dataset:

| Case study                  | Output groups | Hadoop Streaming on YARN | Spark on YARN |
| --------------------------- | ------------: | -----------------------: | ------------: |
| Department demand           |            16 |                 18.763 s |      29.630 s |
| Disease and symptom trends  |         2,301 |                 18.558 s |      31.256 s |
| QA quality and completeness |             4 |                 19.602 s |      25.309 s |
| Question-type distribution  |             7 |                 18.560 s |      23.310 s |

Pilot timing file:

```text
results/case-benchmark/timings-cluster-20260606-153149.csv
```

## Implementation Notes

The Hadoop reducer uses streaming aggregation. This matters for full-scale data:
case study 3 can produce millions of intermediate quality records for a single
source, so the reducer must aggregate values as they arrive instead of storing
all values in memory.

Both implementations use shared analytical rules from `config/` so that Hadoop
and Spark classify departments, disease/symptom terms, and question types
consistently.

## Evidence Files

Key reproducibility and evidence files:

```text
reports/source_manifest.csv
reports/source_manifest.json
reports/pilot_summary.json
reports/framework_equivalence.json
reports/full_summary.json
reports/full_benchmark_chart.png
results/case-benchmark/timings-cluster-20260606-153149.csv
results/case-benchmark/timings-full-cluster-20260607-171724.csv
```

Large generated datasets and benchmark outputs are ignored by Git. They can be
recreated with the scripts documented above.
