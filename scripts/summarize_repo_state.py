"""Emit a compact Markdown summary of repo state for planning workflows."""

from __future__ import annotations

from pathlib import Path


WORKFLOWS_DIR = Path(".github/workflows")
REPORTS_DIR = Path("reports")
SCRIPTS_DIR = Path("scripts")


def list_files(path: Path, pattern: str) -> list[str]:
    if not path.exists():
        return []
    return sorted(str(p).replace('\\', '/') for p in path.glob(pattern))


def main() -> int:
    workflows = list_files(WORKFLOWS_DIR, "*.yml")
    reports = list_files(REPORTS_DIR, "*.md")
    scripts = list_files(SCRIPTS_DIR, "*.py")

    print("# Repo State Summary")
    print()
    print("## Workflows")
    for wf in workflows:
        print(f"- {wf}")
    print()
    print("## Top-level reports")
    for report in reports:
        print(f"- {report}")
    print()
    print("## Python helper scripts")
    for script in scripts:
        print(f"- {script}")

    backlog = Path("reports/backlog.md")
    print()
    print("## Backlog")
    print(f"- {'present' if backlog.exists() else 'missing'}: {backlog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
