"""Select the next backlog task by priority/readiness and skip stale items."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
READY_STATUSES = {"todo"}
WORKFLOWS_DIR = Path(".github/workflows")
README_PATH = Path("README.md")
REPO_SUMMARY_ARTIFACT = Path("planner-repo-summary.md")


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


def collect_repo_state() -> tuple[list[tuple[str, str]], str, str]:
    workflows: list[tuple[str, str]] = []
    for workflow in sorted(WORKFLOWS_DIR.glob("*.yml")):
        workflows.append((workflow.as_posix(), workflow.read_text(encoding="utf-8")))

    readme_text = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    summary_text = (
        REPO_SUMMARY_ARTIFACT.read_text(encoding="utf-8")
        if REPO_SUMMARY_ARTIFACT.exists()
        else ""
    )
    return workflows, readme_text, summary_text


def criterion_satisfied(item: dict[str, str], workflows: list[tuple[str, str]], readme_text: str, summary_text: str) -> str | None:
    """Return evidence when a backlog item appears to be already done."""
    criteria = item["success_criteria"]
    criteria_lower = criteria.lower()

    workflow_script_match = re.search(r"workflow runs\s+`([^`]+)`", criteria, flags=re.IGNORECASE)
    if workflow_script_match:
        script_ref = workflow_script_match.group(1)
        for workflow_name, workflow_content in workflows:
            if script_ref in workflow_content:
                return f"'{script_ref}' referenced by {workflow_name}"

    if "readme includes" in criteria_lower:
        if "real_npz" in readme_text and "troubleshooting" in readme_text.lower():
            return "README already contains real_npz troubleshooting guidance"

    if summary_text and "workflow runs" in criteria_lower:
        script_refs = re.findall(r"`([^`]+\.py)`", criteria)
        for script_ref in script_refs:
            if script_ref in summary_text:
                return f"'{script_ref}' listed in planner summary artifact"

    return None


def is_ready(dependencies: str) -> bool:
    dep = dependencies.strip().lower()
    return dep in {"none", "", "n/a"}


def main() -> int:
    args = parse_args()
    path = Path(args.backlog)
    items = parse_table(path)
    workflows, readme_text, summary_text = collect_repo_state()
    ready_items = [i for i in items if i["status"] in READY_STATUSES and is_ready(i["dependencies"])]

    skipped_stale: list[tuple[str, str]] = []
    candidates = []
    for item in ready_items:
        evidence = criterion_satisfied(item, workflows, readme_text, summary_text)
        if evidence:
            skipped_stale.append((item["title"], evidence))
            continue
        candidates.append(item)

    if skipped_stale:
        print("Skipped stale todo items")
        for title, evidence in skipped_stale:
            print(f"- {title} ({evidence})")
        print()

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
