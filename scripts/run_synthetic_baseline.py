"""Run a minimal synthetic dictionary baseline experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nightsearch_sast.config import load_config
from nightsearch_sast.training.train import train


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run synthetic dictionary baseline.")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--output", default="artifacts/synthetic_baseline_metrics.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config(args.config)
    metrics = train(cfg)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "project": cfg.project_name,
        "dataset": cfg.data.dataset_name,
        "metrics": metrics,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Synthetic baseline complete")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
