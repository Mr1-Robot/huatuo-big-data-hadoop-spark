#!/usr/bin/env python3
"""Shared helpers for Huatuo preprocessing and analytics."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

URL_RE = re.compile(r"^https?://", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")


def load_json(path: str | Path) -> Any:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = " ".join(normalize_text(item) for item in value)
    elif isinstance(value, dict):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return WHITESPACE_RE.sub(" ", str(value)).strip()


def first_present(record: dict[str, Any], aliases: Iterable[str]) -> Any:
    for alias in aliases:
        if alias in record and record[alias] is not None:
            return record[alias]
    return None


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_answer(answer: str) -> str:
    if not answer:
        return "empty"
    if URL_RE.match(answer):
        return "url"
    return "text"


def match_terms(text: str, terms: Iterable[str]) -> list[str]:
    folded = text.casefold()
    return sorted({term for term in terms if term and term.casefold() in folded})


def write_jsonl(records: Iterable[dict[str, Any]], path: str | Path) -> int:
    count = 0
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count

