#!/usr/bin/env python3
"""Union canonical JSONL sources and mark duplicates across all sources."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--drop-duplicates", action="store_true")
    parser.add_argument("--dedupe-db", type=Path)
    args = parser.parse_args()

    database_path = args.dedupe_db or args.output.with_suffix(".dedupe.sqlite3")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute("CREATE TABLE seen (question_hash TEXT PRIMARY KEY)")
    written = duplicates = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as output:
        for input_path in args.inputs:
            with input_path.open(encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    question_hash = record["question_hash"]
                    cursor = connection.execute(
                        "INSERT OR IGNORE INTO seen(question_hash) VALUES (?)",
                        (question_hash,),
                    )
                    duplicate = cursor.rowcount == 0
                    record["duplicate_flag"] = duplicate
                    duplicates += int(duplicate)
                    if duplicate and args.drop_duplicates:
                        continue
                    output.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                    written += 1
                    if written % 100000 == 0:
                        connection.commit()
    connection.commit()
    connection.close()
    print(f"wrote={written} duplicates={duplicates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
