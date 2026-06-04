#!/usr/bin/env bash
set -euo pipefail

source_dir="${1:-data/source}"
output_dir="${2:-data/standardized-full}"
rules="${ENRICHMENT_RULES:-config/no_enrichment_rules.json}"
mkdir -p "$output_dir/sources"

inputs=()
for source in consultation encyclopedia knowledge_graph; do
  for split in train validation test; do
    input="$source_dir/$source/${split}_datasets.jsonl"
    output="$output_dir/sources/${source}_${split}.jsonl"
    echo "Standardizing $source/$split..."
    python3 preprocessing/standardize_records.py \
      --source "$source" \
      --source-split "$split" \
      --input "$input" \
      --output "$output" \
      --rules "$rules" \
      --skip-duplicate-detection
    inputs+=("$output")
  done
done

echo "Standardizing lite/full..."
python3 preprocessing/standardize_records.py \
  --source lite \
  --source-split full \
  --input "$source_dir/lite/format_data.jsonl" \
  --output "$output_dir/sources/lite_full.jsonl" \
  --rules "$rules" \
  --skip-duplicate-detection
inputs+=("$output_dir/sources/lite_full.jsonl")

echo "Unioning standardized sources and detecting cross-source duplicates..."
python3 preprocessing/union_datasets.py \
  --inputs "${inputs[@]}" \
  --output "$output_dir/huatuo_unified.jsonl"

python3 preprocessing/validate_dataset.py "$output_dir/huatuo_unified.jsonl"

