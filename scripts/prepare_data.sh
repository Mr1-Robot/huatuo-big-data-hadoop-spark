#!/usr/bin/env bash
set -euo pipefail

raw_dir="${1:-data/raw}"
output_dir="${2:-data/standardized}"
enrichment_rules="${ENRICHMENT_RULES:-config/no_enrichment_rules.json}"
mkdir -p "$output_dir"

for source in consultation encyclopedia knowledge_graph lite; do
  python3 preprocessing/standardize_records.py \
    --source "$source" \
    --input "$raw_dir/${source}.jsonl" \
    --output "$output_dir/${source}.jsonl" \
    --rules "$enrichment_rules" \
    --skip-duplicate-detection
done

python3 preprocessing/union_datasets.py \
  --inputs \
    "$output_dir/consultation.jsonl" \
    "$output_dir/encyclopedia.jsonl" \
    "$output_dir/knowledge_graph.jsonl" \
    "$output_dir/lite.jsonl" \
  --output "$output_dir/huatuo_unified.jsonl"

python3 preprocessing/validate_dataset.py "$output_dir/huatuo_unified.jsonl"
