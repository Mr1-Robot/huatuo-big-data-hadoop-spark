#!/usr/bin/env python3
"""Create a reproducible integrity manifest for original Huatuo JSONL files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def inspect(path: Path) -> dict:
    digest = hashlib.sha256()
    records = 0
    with path.open("rb") as handle:
        for line in handle:
            digest.update(line)
            if line.strip():
                records += 1
    return {
        "path": path.as_posix(),
        "bytes": path.stat().st_size,
        "records": records,
        "sha256": digest.hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("data/source"))
    parser.add_argument("--output-prefix", type=Path, default=Path("reports/source_manifest"))
    args = parser.parse_args()

    rows = [inspect(path) for path in sorted(args.source_dir.rglob("*.jsonl"))]
    totals = {
        "files": len(rows),
        "bytes": sum(row["bytes"] for row in rows),
        "records": sum(row["records"] for row in rows),
    }
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    with args.output_prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=("path", "bytes", "records", "sha256"))
        writer.writeheader()
        writer.writerows(rows)
    args.output_prefix.with_suffix(".json").write_text(
        json.dumps({"files": rows, "totals": totals}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(totals, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
