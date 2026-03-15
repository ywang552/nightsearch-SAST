"""Select the next backlog task by priority/dependency readiness."""

from __future__ import annotations

import argparse
from pathlib import Path

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
READY_STATUSES = {"todo"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Choose next backlog task.")
    parser.add_argument("--backlog", default="reports/backlog.md")
    return parser.parse_args()


def parse_table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip().startswith("| Title |")), None)
    if start is None:
        raise ValueError("Could not find backlog table header")

    rows = []
    for line in lines[start + 2 :]:
        if not line.strip().startswith("|"):
            break
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 7:
            continue
        rows.append(
            {
                "title": cols[0],
                "description": cols[1],
                "priority": cols[2],
                "status": cols[3],
                "dependencies": cols[4],
                "owner_role": cols[5],
                "success_criteria": cols[6],
            }
        )
    return rows


def is_ready(dependencies: str) -> bool:
    dep = dependencies.strip().lower()
    return dep in {"none", "", "n/a"}


def main() -> int:
    args = parse_args()
    path = Path(args.backlog)
    items = parse_table(path)
    candidates = [i for i in items if i["status"] in READY_STATUSES and is_ready(i["dependencies"])]
    if not candidates:
        print("No ready tasks found.")
        return 1

    candidates.sort(key=lambda i: (PRIORITY_ORDER.get(i["priority"], 999), i["title"].lower()))
    choice = candidates[0]
    print("Next task recommendation")
    print(f"- Title: {choice['title']}")
    print(f"- Owner Role: {choice['owner_role']}")
    print(f"- Priority: {choice['priority']}")
    print(f"- Success Criteria: {choice['success_criteria']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
