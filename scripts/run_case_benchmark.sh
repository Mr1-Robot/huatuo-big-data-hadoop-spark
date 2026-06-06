#!/usr/bin/env bash
set -euo pipefail

mode="${1:-cluster}"
framework_filter="${2:-all}"
timestamp="$(date +%Y%m%d-%H%M%S)"
results_dir="results/case-benchmark"
timings_file="${BENCHMARK_TIMINGS_FILE:-$results_dir/timings-${mode}-${timestamp}.csv}"

mkdir -p "$results_dir"
if [[ ! -f "$timings_file" ]]; then
  printf 'framework,mode,case_study,elapsed_seconds,output_records,input,output\n' > "$timings_file"
fi

elapsed_seconds() {
  python3 - "$1" "$2" <<'PY'
import sys

start = float(sys.argv[1])
end = float(sys.argv[2])
print(round(end - start, 3))
PY
}

hdfs_count() {
  hdfs dfs -cat "$1" | wc -l | tr -d ' '
}

run_cluster() {
  local input="${BENCHMARK_INPUT:-/healthcare/pilot/input/huatuo_unified.jsonl}"

  if [[ "$framework_filter" == "all" || "$framework_filter" == "hadoop" ]]; then
    for case_study in 1 2 3 4; do
      local hadoop_output="${BENCHMARK_HADOOP_OUTPUT_PREFIX:-/healthcare/pilot/output/hadoop-cs}${case_study}-${timestamp}"
      echo "Running Hadoop Streaming YARN case study ${case_study}..."
      local start
      start="$(python3 -c 'import time; print(time.time())')"
      bash scripts/run_hadoop_streaming.sh "$case_study" "$input" "$hadoop_output"
      local end
      end="$(python3 -c 'import time; print(time.time())')"
      local elapsed
      elapsed="$(elapsed_seconds "$start" "$end")"
      local records
      records="$(hdfs_count "${hadoop_output}/part-*")"
      echo "hadoop_streaming_yarn,$mode,$case_study,$elapsed,$records,$input,$hadoop_output" >> "$timings_file"
    done
  fi

  if [[ "$framework_filter" == "all" || "$framework_filter" == "spark" ]]; then
    for case_study in 1 2 3 4; do
      local spark_output="${BENCHMARK_SPARK_OUTPUT_PREFIX:-/healthcare/pilot/output/spark-cs}${case_study}-${timestamp}"
      echo "Running Spark YARN case study ${case_study}..."
      hdfs dfs -rm -r -f "$spark_output" >/dev/null 2>&1 || true
      local start
      start="$(python3 -c 'import time; print(time.time())')"
      SPARK_MASTER="${SPARK_MASTER:-yarn}" bash scripts/run_spark.sh "$case_study" "$input" "$spark_output"
      local end
      end="$(python3 -c 'import time; print(time.time())')"
      local elapsed
      elapsed="$(elapsed_seconds "$start" "$end")"
      local records
      records="$(hdfs_count "${spark_output}/part-*.json")"
      echo "spark_submit_yarn,$mode,$case_study,$elapsed,$records,$input,$spark_output" >> "$timings_file"
    done
  fi
}

case "$mode" in
  cluster)
    run_cluster
    ;;
  *)
    echo "Usage: $0 cluster [all|hadoop|spark]" >&2
    exit 2
    ;;
esac

echo "Benchmark timings written to $timings_file"
cat "$timings_file"
