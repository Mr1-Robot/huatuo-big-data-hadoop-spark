#!/usr/bin/env bash
set -euo pipefail

framework_filter="${1:-all}"
case_filter="${2:-1,2,3,4}"
timestamp="$(date +%Y%m%d-%H%M%S)"

export BENCHMARK_INPUT="${BENCHMARK_INPUT:-/healthcare/full/input/huatuo_unified.jsonl}"
export BENCHMARK_HADOOP_OUTPUT_PREFIX="${BENCHMARK_HADOOP_OUTPUT_PREFIX:-/healthcare/full/output/hadoop-cs}"
export BENCHMARK_SPARK_OUTPUT_PREFIX="${BENCHMARK_SPARK_OUTPUT_PREFIX:-/healthcare/full/output/spark-cs}"
export BENCHMARK_TIMINGS_FILE="${BENCHMARK_TIMINGS_FILE:-results/case-benchmark/timings-full-cluster-${timestamp}.csv}"

echo "Full dataset benchmark input: $BENCHMARK_INPUT"
echo "Framework filter: $framework_filter"
echo "Case studies: $case_filter"
echo "Timing file: $BENCHMARK_TIMINGS_FILE"
echo

hdfs dfs -test -f "$BENCHMARK_INPUT"
hdfs dfs -mkdir -p /healthcare/full/output

bash scripts/run_case_benchmark.sh cluster "$framework_filter" "$case_filter"
