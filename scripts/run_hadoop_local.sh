#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 CASE_STUDY INPUT_JSONL OUTPUT_JSONL" >&2
  exit 2
fi

case_study="$1"
input="$2"
output="$3"
rules="${ANALYTICS_RULES:-config/analytics_rules.json}"

python3 hadoop/mapper.py --case-study "$case_study" --rules "$rules" < "$input" \
  | LC_ALL=C sort \
  | python3 hadoop/reducer.py --case-study "$case_study" > "$output"
