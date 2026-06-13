#!/usr/bin/env bash
set -euo pipefail

framework_filter="${1:-all}"
case_filter="${2:-1,2,3,4}"
timestamp="$(date +%Y%m%d-%H%M%S)"

usage() {
  cat >&2 <<'EOF'
Usage:
  bash scripts/run_full_case_benchmark.sh [all|hadoop|spark] [case_numbers_csv]

Examples:
  bash scripts/run_full_case_benchmark.sh
  bash scripts/run_full_case_benchmark.sh hadoop
  bash scripts/run_full_case_benchmark.sh spark
  bash scripts/run_full_case_benchmark.sh hadoop 3,4
EOF
}

if [[ "$framework_filter" != "all" && "$framework_filter" != "hadoop" && "$framework_filter" != "spark" ]]; then
  usage
  exit 2
fi

export BENCHMARK_INPUT="${BENCHMARK_INPUT:-/healthcare/full/input/huatuo_unified.jsonl}"
export BENCHMARK_HADOOP_OUTPUT_PREFIX="${BENCHMARK_HADOOP_OUTPUT_PREFIX:-/healthcare/full/output/hadoop-cs}"
export BENCHMARK_SPARK_OUTPUT_PREFIX="${BENCHMARK_SPARK_OUTPUT_PREFIX:-/healthcare/full/output/spark-cs}"
export BENCHMARK_TIMINGS_FILE="${BENCHMARK_TIMINGS_FILE:-results/case-benchmark/timings-full-cluster-${timestamp}.csv}"
export BENCHMARK_LOCAL_OUTPUTS_DIR="${BENCHMARK_LOCAL_OUTPUTS_DIR:-results/full-benchmark/outputs}"

has_jps_process() {
  local process_name="$1"
  jps 2>/dev/null | awk '{print $2}' | grep -qx "$process_name"
}

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
}

cleanup_stale_pid_file() {
  local pid_file="$1"
  local label="$2"
  local command_pattern="$3"

  if [[ ! -f "$pid_file" ]]; then
    return 0
  fi

  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && ps -p "$pid" -o command= 2>/dev/null | grep -q "$command_pattern"; then
    echo "$label appears to be running as PID $pid."
    return 0
  fi

  echo "Removing stale $label PID file: $pid_file"
  rm -f "$pid_file"
}

cleanup_stale_hadoop_pid_files() {
  local hadoop_user="${HADOOP_IDENT_STRING:-${USER:-$(id -un)}}"
  local tmp_dir="${HADOOP_PID_DIR:-/tmp}"

  cleanup_stale_pid_file "$tmp_dir/hadoop-${hadoop_user}-namenode.pid" "NameNode" "NameNode"
  cleanup_stale_pid_file "$tmp_dir/hadoop-${hadoop_user}-datanode.pid" "DataNode" "DataNode"
  cleanup_stale_pid_file "$tmp_dir/hadoop-${hadoop_user}-secondarynamenode.pid" "SecondaryNameNode" "SecondaryNameNode"
  cleanup_stale_pid_file "$tmp_dir/yarn-${hadoop_user}-resourcemanager.pid" "ResourceManager" "ResourceManager"
  cleanup_stale_pid_file "$tmp_dir/yarn-${hadoop_user}-nodemanager.pid" "NodeManager" "NodeManager"
}

command_succeeds_with_timeout() {
  local timeout_seconds="$1"
  shift
  python3 - "$timeout_seconds" "$@" <<'PY'
import subprocess
import sys

timeout = float(sys.argv[1])
command = sys.argv[2:]
try:
    completed = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
except subprocess.TimeoutExpired:
    raise SystemExit(124)
raise SystemExit(completed.returncode)
PY
}

hdfs_ready() {
  command_succeeds_with_timeout 15 hdfs dfs -test -d /
}

yarn_ready() {
  command_succeeds_with_timeout 15 yarn node -list
}

wait_for_service() {
  local service_name="$1"
  local check_command="$2"
  local attempts="${3:-20}"
  local sleep_seconds="${4:-2}"

  for _ in $(seq 1 "$attempts"); do
    if "$check_command"; then
      return 0
    fi
    sleep "$sleep_seconds"
  done

  echo "Timed out waiting for $service_name to become reachable." >&2
  echo "Current Java processes:" >&2
  jps >&2 || true
  exit 1
}

ensure_hdfs_yarn() {
  require_command jps
  require_command hdfs
  require_command yarn
  require_command start-dfs.sh
  require_command start-yarn.sh

  cleanup_stale_hadoop_pid_files

  echo "Checking HDFS reachability..."
  if ! hdfs_ready; then
    echo "Starting HDFS daemons..."
    start-dfs.sh
    wait_for_service HDFS hdfs_ready
  else
    echo "HDFS is already reachable."
  fi

  echo "Checking YARN reachability..."
  if ! yarn_ready; then
    echo "Starting YARN daemons..."
    start-yarn.sh
    wait_for_service YARN yarn_ready
  else
    echo "YARN is already reachable."
  fi

  echo "Active Hadoop/YARN Java processes:"
  jps | grep -E 'NameNode|DataNode|SecondaryNameNode|ResourceManager|NodeManager' || true
  echo
}

echo "Full dataset benchmark input: $BENCHMARK_INPUT"
echo "Framework filter: $framework_filter"
echo "Case studies: $case_filter"
echo "Timing file: $BENCHMARK_TIMINGS_FILE"
echo

ensure_hdfs_yarn

hdfs dfs -test -f "$BENCHMARK_INPUT"
hdfs dfs -mkdir -p /healthcare/full/output

bash scripts/run_case_benchmark.sh cluster "$framework_filter" "$case_filter"
