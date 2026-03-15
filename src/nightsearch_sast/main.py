"""CLI entrypoint for running scaffold experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

from nightsearch_sast.config import load_config
from nightsearch_sast.training.train import train


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run cross-attention scaffold training for spot annotation.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to a YAML config file.")
    return parser.parse_args()


def _print_metric(label: str, metrics: dict[str, float], key: str) -> None:
    value = metrics.get(key)
    if value is None:
        print(f"{label}: not available for this run")
        return
    print(f"{label}: {value:.6f}")


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    cfg = load_config(config_path)
    metrics = train(cfg)

    print("nightsearch-SAST cross-attention scaffold")
    print("Config:", config_path)
    print("Project:", cfg.project_name)
    _print_metric("Train loss (last)", metrics, "train_loss_last")
    _print_metric("Validation loss (mean)", metrics, "val_loss_mean")
    _print_metric("NNLS baseline validation loss (mean)", metrics, "nnls_val_loss_mean")
    print("Status: scaffold run complete (synthetic dictionary baseline)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
