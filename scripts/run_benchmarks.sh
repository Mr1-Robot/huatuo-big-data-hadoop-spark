#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 HDFS_BENCHMARK_DIR [RESULTS_CSV]" >&2
  exit 2
fi

hdfs_dir="${1%/}"
results="${2:-results/benchmark_times.csv}"
mkdir -p "$(dirname "$results")"
echo "framework,case_study,input_percentage,run,elapsed_seconds" > "$results"

for case_study in 1 2 3 4; do
  for percentage in 25 50 75 100; do
    input="$hdfs_dir/huatuo_${percentage}.jsonl"
    for run in 1 2 3; do
      start="$(date +%s)"
      scripts/run_hadoop_streaming.sh "$case_study" "$input" "/healthcare/output/cs${case_study}-${percentage}-run${run}"
      end="$(date +%s)"
      echo "hadoop,$case_study,$percentage,$run,$((end-start))" >> "$results"

      start="$(date +%s)"
      scripts/run_spark.sh "$case_study" "$input" "/healthcare/spark-output/cs${case_study}-${percentage}-run${run}"
      end="$(date +%s)"
      echo "spark,$case_study,$percentage,$run,$((end-start))" >> "$results"
    done
  done
done

echo "Wrote benchmark results to $results"
