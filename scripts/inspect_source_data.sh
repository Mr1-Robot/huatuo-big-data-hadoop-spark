#!/usr/bin/env bash
set -euo pipefail

source_dir="${SOURCE_DIR:-data/source}"
command="${1:-summary}"

run_with_spinner() {
  local message="$1"
  shift
  local output_file
  output_file="$(mktemp)"

  "$@" >"$output_file" &
  local command_pid=$!
  local frames='|/-\'
  local index=0

  while kill -0 "$command_pid" 2>/dev/null; do
    printf "\r%s %s" "$message" "${frames:index++%4:1}"
    sleep 0.1
  done

  wait "$command_pid"
  local status=$?
  printf "\r\033[K"
  cat "$output_file"
  rm -f "$output_file"
  return "$status"
}

case "$command" in
  summary)
    echo "Dataset sizes:"
    du -sh "$source_dir" "$source_dir"/*
    echo
    echo "Record counts:"
    run_with_spinner "Counting records..." wc -l \
      "$source_dir"/consultation/*.jsonl \
      "$source_dir"/encyclopedia/*.jsonl \
      "$source_dir"/knowledge_graph/*.jsonl \
      "$source_dir"/lite/*.jsonl
    ;;

  samples)
    for file in \
      "$source_dir/consultation/train_datasets.jsonl" \
      "$source_dir/encyclopedia/train_datasets.jsonl" \
      "$source_dir/knowledge_graph/train_datasets.jsonl" \
      "$source_dir/lite/format_data.jsonl"
    do
      echo
      echo "=== $file ==="
      head -n 1 "$file" | python3 -m json.tool
    done
    ;;

  line)
    file="${2:?Usage: $0 line FILE LINE_NUMBER}"
    line_number="${3:?Usage: $0 line FILE LINE_NUMBER}"
    sed -n "${line_number}p" "$file" | python3 -m json.tool
    ;;

  pandas)
    file="${2:-$source_dir/consultation/train_datasets.jsonl}"
    .venv/bin/python - "$file" <<'PY'
import sys
import pandas as pd

reader = pd.read_json(sys.argv[1], lines=True, chunksize=5)
print(next(reader).to_string())
PY
    ;;

  *)
    echo "Usage: $0 {summary|samples|line FILE LINE_NUMBER|pandas [FILE]}" >&2
    exit 2
    ;;
esac
