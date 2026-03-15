"""Validate reports/backlog.md table structure and required fields."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_COLUMNS = [
    "Title",
    "Description",
    "Priority",
    "Status",
    "Dependencies",
    "Owner Role",
    "Success Criteria",
]
ALLOWED_STATUS = {"todo", "in_progress", "blocked", "done"}
ALLOWED_PRIORITY = {"P0", "P1", "P2", "P3"}
ALLOWED_OWNER_ROLES = {"planner", "builder", "reviewer", "verifier", "hygiene", "research"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate backlog markdown table.")
    parser.add_argument("--path", default="reports/backlog.md")
    return parser.parse_args()


def extract_table_lines(text: str) -> list[str]:
    lines = [line.rstrip("\n") for line in text.splitlines()]
    start = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("| Title |"):
            start = idx
            break
    if start is None:
        raise ValueError("Backlog table header not found.")

    table_lines: list[str] = []
    for line in lines[start:]:
        if not line.strip().startswith("|"):
            break
        table_lines.append(line)
    return table_lines


def split_row(row: str) -> list[str]:
    return [part.strip() for part in row.strip().strip("|").split("|")]


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    if not path.exists():
        raise SystemExit(f"Missing backlog file: {path}")

    table_lines = extract_table_lines(path.read_text(encoding="utf-8"))
    if len(table_lines) < 3:
        raise SystemExit("Backlog table must include header, separator, and at least one data row.")

    header = split_row(table_lines[0])
    if header != REQUIRED_COLUMNS:
        raise SystemExit(f"Backlog columns mismatch. Found: {header}; expected: {REQUIRED_COLUMNS}")

    errors: list[str] = []
    for idx, row in enumerate(table_lines[2:], start=1):
        cols = split_row(row)
        if len(cols) != len(REQUIRED_COLUMNS):
            errors.append(f"Row {idx}: expected {len(REQUIRED_COLUMNS)} columns, found {len(cols)}")
            continue

        title, desc, priority, status, deps, owner_role, criteria = cols
        if not title:
            errors.append(f"Row {idx}: Title is empty")
        if not desc:
            errors.append(f"Row {idx}: Description is empty")
        if priority not in ALLOWED_PRIORITY:
            errors.append(f"Row {idx}: Priority must be one of {sorted(ALLOWED_PRIORITY)}")
        if status not in ALLOWED_STATUS:
            errors.append(f"Row {idx}: Status must be one of {sorted(ALLOWED_STATUS)}")
        if not deps:
            errors.append(f"Row {idx}: Dependencies must be 'none' or a comma-separated list")
        if owner_role not in ALLOWED_OWNER_ROLES:
            errors.append(f"Row {idx}: Owner Role must be one of {sorted(ALLOWED_OWNER_ROLES)}")
        if not criteria:
            errors.append(f"Row {idx}: Success Criteria is empty")

    if errors:
        raise SystemExit("Backlog validation failed:\n- " + "\n- ".join(errors))

    print(f"Backlog valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
