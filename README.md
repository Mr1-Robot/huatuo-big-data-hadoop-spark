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
config/          Shared analytics and preprocessing rules
data/samples/    Four tiny example source datasets
docs/            Assessment requirements, proposal, and selected case studies
hadoop/          Python Hadoop Streaming mapper and reducer
preprocessing/   Download, standardize, union, and validate data
scripts/         Commands for preparing and running the project
spark/           Equivalent PySpark analytics application
```

## Understand the Pipeline Using Samples

Prepare one unified sample dataset:

```bash
bash scripts/prepare_data.sh data/samples data/standardized
```

View it:

```bash
head -n 3 data/standardized/huatuo_unified.jsonl | python3 -m json.tool --json-lines
```

## Run the Real-Data Pilot

Create source-integrity evidence and run the 400,000-record pilot:

```bash
bash scripts/create_source_manifest.sh
bash scripts/run_pilot.sh
```

Pilot evidence is written to `reports/` and `results/pilot/`.

After pilot validation, prepare the complete source dataset with:

```bash
bash scripts/prepare_full_data.sh
```

## Run One Case Study

Hadoop mapper/reducer locally:

```bash
bash scripts/run_hadoop_local.sh \
  1 data/standardized/huatuo_unified.jsonl results/hadoop-cs1.jsonl

cat results/hadoop-cs1.jsonl
```

Spark locally:

```bash
bash scripts/run_spark.sh \
  1 data/standardized/huatuo_unified.jsonl results/spark-cs1

cat results/spark-cs1/part-*.json
```

Replace `1` with `2`, `3`, or `4` to run another case study.

## Real Data

Create an isolated downloader environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install datasets
```

Download the original published Hugging Face repository files:

```bash
.venv/bin/python preprocessing/download_source_snapshots.py \
  --output-dir data/source
```

These are the original source files, normally Parquet. Inspect them before
transformation:

```bash
bash scripts/inspect_source_data.sh summary
bash scripts/inspect_source_data.sh samples
```

The current standardization pipeline expects JSONL. Source Parquet conversion will
be added after the original files and schemas have been inspected.

For a small streaming JSONL trial instead:

```bash
.venv/bin/python preprocessing/download_sources.py \
  --output-dir data/raw-trial --limit 10000
```

Then standardize the trial:

```bash
bash scripts/prepare_data.sh data/raw-trial data/standardized
```

## HDFS

After starting HDFS:

```bash
bash scripts/upload_to_hdfs.sh
bash scripts/run_hadoop_streaming.sh \
  1 /healthcare/input/huatuo_unified.jsonl /healthcare/output/cs1
hdfs dfs -cat /healthcare/output/cs1/part-*
```

Check installed tools and HDFS status:

```bash
bash scripts/check_environment.sh
```
