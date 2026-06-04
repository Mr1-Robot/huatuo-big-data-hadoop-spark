#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 CASE_STUDY INPUT_JSONL OUTPUT_PATH" >&2
  exit 2
fi

spark-submit spark/healthcare_analytics.py \
  --master "${SPARK_MASTER:-local[*]}" \
  --case-study "$1" \
  --input "$2" \
  --output "$3" \
  --rules "${ANALYTICS_RULES:-config/analytics_rules.json}"
