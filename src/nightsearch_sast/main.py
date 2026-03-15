"""Minimal entrypoint for future research workflows."""

import argparse
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Placeholder entrypoint for nightsearch-SAST research code."
    )
    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="Path to a YAML config file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)

    if not config_path.exists():
        raise FileNotFoundError("Config file not found: {}".format(config_path))

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    print("nightsearch-SAST placeholder")
    print("Config:", config_path)
    print("Project:", config.get("project_name", "unknown"))
    print("Status: scaffold ready for future research code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
