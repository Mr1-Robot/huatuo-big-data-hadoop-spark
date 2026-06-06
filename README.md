# Huatuo Big Data Processing

This project processes Huatuo medical question-answer datasets with the same four
analytics case studies in Hadoop Streaming and Apache Spark.

## What We Are Doing

```text
Four different Huatuo source datasets
                |
                v
Standardize every source into one JSONL schema
                |
                v
Union the standardized records into one dataset
                |
                v
Run the same analytics with Hadoop and Spark
```

The datasets are **unioned**, not joined, because they do not share a reliable
consultation identifier.

## Project Structure

```text
config/          Analytics and preprocessing rules
data/source/     Original Huatuo source files
data/pilot/      Deterministic 400,000-record pilot
data/processed-pilot/
                 Canonical pilot JSONL used for benchmarking
docs/            Local assessment PDFs, ignored by Git
journey.md       Presentation-ready project journey
hadoop/          Hadoop Streaming mapper and reducer
preprocessing/   Manifest, pilot, standardization, union, validation
reports/         Source and pilot evidence
results/         Final benchmark timing CSV
scripts/         Reproducible terminal commands
spark/           Equivalent PySpark analytics application
```

## Current Benchmark

The benchmark used in the report is the per-case-study HDFS/YARN run:

```bash
bash scripts/run_case_benchmark.sh cluster
```

Final timing evidence:

```text
results/case-benchmark/timings-cluster-20260606-153149.csv
```

## Recreate the Pilot Input

Create the source manifest:

```bash
bash scripts/create_source_manifest.sh
```

Create and standardize the deterministic pilot:

```bash
bash scripts/create_pilot.sh
bash scripts/prepare_data.sh data/pilot data/processed-pilot
```

The benchmark input is:

```text
data/processed-pilot/huatuo_unified.jsonl
```

## Real Data

Create a temporary downloader environment only if the source files need to be
downloaded again:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install datasets
```

Download the original published Hugging Face repository files:

```bash
.venv/bin/python preprocessing/download_source_snapshots.py \
  --output-dir data/source
```

Inspect the downloaded sources:

```bash
bash scripts/inspect_source_data.sh summary
bash scripts/inspect_source_data.sh samples
```

## HDFS

Upload the processed pilot to HDFS:

```bash
bash scripts/upload_to_hdfs.sh \
  data/processed-pilot/huatuo_unified.jsonl \
  /healthcare/pilot/input
```

Run one Hadoop Streaming case manually:

```bash
bash scripts/run_hadoop_streaming.sh \
  1 \
  /healthcare/pilot/input/huatuo_unified.jsonl \
  /healthcare/pilot/output/manual-cs1
```

Check local tools and HDFS status:

```bash
bash scripts/check_environment.sh
```
