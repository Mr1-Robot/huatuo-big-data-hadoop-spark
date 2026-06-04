# Huatuo-26M Healthcare Big Data Processing

This project standardizes heterogeneous Huatuo medical QA datasets and runs four
equivalent analytics jobs with Hadoop Streaming and PySpark.

## Environment

Required commands: Python 3, Java 17, Hadoop, and Spark. The optional full-dataset
downloader additionally requires the Hugging Face `datasets` package.

```bash
bash scripts/check_environment.sh
```

On this machine Hadoop is configured with `hdfs://localhost:9000`, but HDFS jobs
require the NameNode and DataNode daemons to be running first.

## Case Studies

1. Medical department demand using observed and inferred department labels.
2. Disease and symptom trend mining.
3. Medical QA quality and completeness analysis.
4. Medical question-type distribution and Hadoop-versus-Spark performance.

## Canonical Data Pipeline

The source datasets are standardized and unioned, not joined. The canonical JSONL
schema preserves observed metadata, marks inferred metadata, derives text lengths
and hashes, and identifies duplicate questions. Global duplicate detection uses a
disk-backed SQLite index so preprocessing does not retain millions of hashes in RAM.

Run the included sample:

```bash
bash scripts/prepare_data.sh data/samples data/standardized
python3 tests/run_tests.py
```

Download full sources after installing `datasets`:

```bash
python3 preprocessing/download_sources.py --output-dir data/raw
bash scripts/prepare_data.sh data/raw data/standardized
```

Use `--limit 10000` with the downloader for a larger trial run before downloading
all sources.

## Hadoop

Local mapper/reducer verification:

```bash
bash scripts/run_hadoop_local.sh 1 data/standardized/huatuo_unified.jsonl results/cs1.jsonl
```

Real Hadoop Streaming verification in Hadoop local-framework mode:

```bash
bash scripts/run_hadoop_framework_local.sh 1 data/standardized/huatuo_unified.jsonl cs1-output
```

Upload and run on HDFS:

```bash
bash scripts/upload_to_hdfs.sh
bash scripts/run_hadoop_streaming.sh 1 /healthcare/input/huatuo_unified.jsonl /healthcare/output/cs1
```

## Spark

```bash
bash scripts/run_spark.sh 1 data/standardized/huatuo_unified.jsonl results/spark-cs1
```

Relative existing inputs and relative outputs are treated as local files. Use an
explicit HDFS URI such as `hdfs://localhost:9000/healthcare/input/huatuo_unified.jsonl`
when running Spark against HDFS.

Use identical input and rules for Hadoop and Spark. Record preprocessing time
separately from analytics execution time.

Run the full 25/50/75/100 percent benchmark matrix after uploading the generated
benchmark partitions:

```bash
bash scripts/run_benchmarks.sh /healthcare/input/benchmarks
```
