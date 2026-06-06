#!/usr/bin/env bash
set -euo pipefail

input="${1:-data/standardized-full/huatuo_unified.jsonl}"
summary_output="${2:-reports/full_summary.json}"
samples_dir="${3:-data/samples/full-canonical}"

echo "Inspecting canonical full dataset..."
echo "Input: $input"
echo

echo "File properties:"
ls -lh "$input"
du -h "$input"
wc -l "$input"
echo

python3 preprocessing/summarize_canonical.py \
  "$input" \
  --summary-output "$summary_output" \
  --samples-dir "$samples_dir"
