#!/usr/bin/env bash
set -euo pipefail

echo "Hashing and counting original source files. This scans all 5+ GB..."
python3 preprocessing/create_source_manifest.py \
  --source-dir "${1:-data/source}" \
  --output-prefix "${2:-reports/source_manifest}"

echo "Manifest written to reports/source_manifest.csv and reports/source_manifest.json"

