#!/usr/bin/env bash
set -euo pipefail

python3 preprocessing/create_pilot.py \
  --source-dir "${1:-data/source}" \
  --output-dir "${2:-data/pilot}" \
  --records-per-source "${PILOT_RECORDS_PER_SOURCE:-100000}"

echo
du -sh "${2:-data/pilot}"
wc -l "${2:-data/pilot}"/*.jsonl

