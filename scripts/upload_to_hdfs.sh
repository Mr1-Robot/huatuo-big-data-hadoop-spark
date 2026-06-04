#!/usr/bin/env bash
set -euo pipefail

local_input="${1:-data/standardized/huatuo_unified.jsonl}"
hdfs_dir="${2:-/healthcare/input}"

hdfs dfs -mkdir -p "$hdfs_dir"
hdfs dfs -put -f "$local_input" "$hdfs_dir/"
hdfs dfs -mkdir -p "$hdfs_dir/benchmarks"
hdfs dfs -put -f "$(dirname "$local_input")"/benchmarks/*.jsonl "$hdfs_dir/benchmarks/"
hdfs dfs -ls -h "$hdfs_dir"
