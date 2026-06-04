#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 CASE_STUDY INPUT_JSONL OUTPUT_DIR" >&2
  exit 2
fi

case_study="$1"
input="$2"
output="$3"
project_root="$(cd "$(dirname "$0")/.." && pwd)"
input_abs="$(cd "$(dirname "$input")" && pwd)/$(basename "$input")"
stage_dir="${TMPDIR:-/tmp}/healthcare-hadoop-framework-local"
streaming_jar="${HADOOP_STREAMING_JAR:-$(find "${HADOOP_HOME:-/usr/local/opt/hadoop}/share/hadoop/tools/lib" -name 'hadoop-streaming-*.jar' | head -1)}"
output_name="${output// /_}-$(date +%s)"

mkdir -p "$stage_dir"
cp "$project_root/hadoop/mapper.py" "$stage_dir/mapper.py"
cp "$project_root/hadoop/reducer.py" "$stage_dir/reducer.py"
cp "$project_root/preprocessing/common.py" "$stage_dir/common.py"
cp "$project_root/config/analytics_rules.json" "$stage_dir/analytics_rules.json"
cp "$input_abs" "$stage_dir/input.jsonl"
cd "$stage_dir"

hadoop jar "$streaming_jar" \
  -D mapreduce.framework.name=local \
  -D fs.defaultFS=file:/// \
  -D mapreduce.job.name="healthcare-case-study-${case_study}-local" \
  -files mapper.py,reducer.py,common.py,analytics_rules.json \
  -mapper "python3 mapper.py --case-study ${case_study} --rules analytics_rules.json" \
  -reducer "python3 reducer.py --case-study ${case_study}" \
  -input "file://$stage_dir/input.jsonl" \
  -output "file://$stage_dir/$output_name"

echo "$stage_dir/$output_name"
