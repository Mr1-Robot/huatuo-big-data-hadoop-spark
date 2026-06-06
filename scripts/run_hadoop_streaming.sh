#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 CASE_STUDY|all HDFS_INPUT HDFS_OUTPUT" >&2
  exit 2
fi

case_study="$1"
input="$2"
output="$3"
rules="${ANALYTICS_RULES:-config/analytics_rules.json}"
streaming_jar="${HADOOP_STREAMING_JAR:-$(find "${HADOOP_HOME:-/usr/local/opt/hadoop}/share/hadoop/tools/lib" -name 'hadoop-streaming-*.jar' | head -1)}"
project_root="$(cd "$(dirname "$0")/.." && pwd)"
stage_dir="${TMPDIR:-/tmp}/healthcare-hadoop-streaming"

if [[ -z "$streaming_jar" ]]; then
  echo "Set HADOOP_STREAMING_JAR to the Hadoop Streaming JAR path." >&2
  exit 1
fi

mkdir -p "$stage_dir"
cp "$project_root/hadoop/mapper.py" "$stage_dir/mapper.py"
cp "$project_root/hadoop/reducer.py" "$stage_dir/reducer.py"
cp "$project_root/preprocessing/common.py" "$stage_dir/common.py"
cp "$project_root/$rules" "$stage_dir/analytics_rules.json"
cd "$stage_dir"

hdfs dfs -rm -r -f "$output" >/dev/null 2>&1 || true
hadoop jar "$streaming_jar" \
  -D mapreduce.job.name="healthcare-case-study-${case_study}" \
  -files mapper.py,reducer.py,common.py,analytics_rules.json \
  -mapper "python3 mapper.py --case-study ${case_study} --rules analytics_rules.json" \
  -reducer "python3 reducer.py --case-study ${case_study}" \
  -input "$input" \
  -output "$output"
