#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/pilot/hadoop

echo "1/4 Creating deterministic pilot..."
bash scripts/create_pilot.sh

echo "2/4 Standardizing and validating pilot..."
rm -rf data/processed-pilot
bash scripts/prepare_data.sh data/pilot data/processed-pilot

echo "3/4 Running local Hadoop mapper/reducer jobs..."
printf 'framework,case_study,elapsed_seconds,output_records\n' > results/pilot/timings.csv
for case_study in 1 2 3 4; do
  start="$(python3 -c 'import time; print(time.time())')"
  bash scripts/run_hadoop_local.sh \
    "$case_study" \
    data/processed-pilot/huatuo_unified.jsonl \
    "results/pilot/hadoop/cs${case_study}.jsonl"
  end="$(python3 -c 'import time; print(time.time())')"
  elapsed="$(python3 -c "print(round($end-$start, 3))")"
  records="$(wc -l < "results/pilot/hadoop/cs${case_study}.jsonl" | tr -d ' ')"
  echo "hadoop_local,$case_study,$elapsed,$records" >> results/pilot/timings.csv
done

echo "4/4 Running local Spark jobs..."
for case_study in 1 2 3 4; do
  start="$(python3 -c 'import time; print(time.time())')"
  SPARK_MASTER="${SPARK_MASTER:-local[2]}" bash scripts/run_spark.sh \
    "$case_study" \
    data/processed-pilot/huatuo_unified.jsonl \
    "results/pilot/spark-cs${case_study}"
  end="$(python3 -c 'import time; print(time.time())')"
  elapsed="$(python3 -c "print(round($end-$start, 3))")"
  records="$(cat results/pilot/spark-cs${case_study}/part-*.json | wc -l | tr -d ' ')"
  echo "spark_local,$case_study,$elapsed,$records" >> results/pilot/timings.csv
done

python3 preprocessing/verify_pilot_outputs.py
python3 preprocessing/summarize_pilot.py
