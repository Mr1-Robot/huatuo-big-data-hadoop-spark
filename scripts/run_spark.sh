#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "Usage: $0 CASE_STUDY|all INPUT_JSONL OUTPUT_PATH [--cache-input]" >&2
  exit 2
fi

spark_home="${SPARK_HOME:-/opt/homebrew/opt/apache-spark/libexec}"
spark_python_path="$spark_home/python/lib/pyspark.zip:$spark_home/python/lib/py4j-0.10.9.9-src.zip"
export PYTHONPATH="$spark_python_path${PYTHONPATH:+:$PYTHONPATH}"
export PYSPARK_PYTHON="${PYSPARK_PYTHON:-python3}"
export PYSPARK_DRIVER_PYTHON="${PYSPARK_DRIVER_PYTHON:-python3}"

spark-submit \
  --master "${SPARK_MASTER:-local[*]}" \
  --conf "spark.executorEnv.PYTHONPATH=$spark_python_path" \
  --conf "spark.yarn.appMasterEnv.PYTHONPATH=$spark_python_path" \
  --conf "spark.executorEnv.PYSPARK_PYTHON=$PYSPARK_PYTHON" \
  --conf "spark.yarn.appMasterEnv.PYSPARK_PYTHON=$PYSPARK_PYTHON" \
  spark/healthcare_analytics.py \
  --case-study "$1" \
  --input "$2" \
  --output "$3" \
  --rules "${ANALYTICS_RULES:-config/analytics_rules.json}" \
  ${4:-}
