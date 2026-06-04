#!/usr/bin/env python3
"""Download the original published files from each Huatuo Hugging Face repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

SOURCES = {
    "consultation": "FreedomIntelligence/huatuo_consultation_qa",
    "encyclopedia": "FreedomIntelligence/huatuo_encyclopedia_qa",
    "knowledge_graph": "FreedomIntelligence/huatuo_knowledge_graph_qa",
    "lite": "FreedomIntelligence/Huatuo26M-Lite",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/source"))
    parser.add_argument("--source", choices=(*SOURCES, "all"), default="all")
    args = parser.parse_args()

    selected = SOURCES if args.source == "all" else {args.source: SOURCES[args.source]}
    for name, repository in selected.items():
        destination = args.output_dir / name
        destination.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {repository} -> {destination}", flush=True)
        snapshot_download(
            repo_id=repository,
            repo_type="dataset",
            local_dir=destination,
        )
        print(f"Completed {name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
