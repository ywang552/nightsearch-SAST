from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "choose_next_task.py"
SPEC = importlib.util.spec_from_file_location("choose_next_task", MODULE_PATH)
assert SPEC and SPEC.loader
choose_next_task = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(choose_next_task)


def test_choose_next_task_skips_stale_workflow_item(tmp_path: Path) -> None:
    backlog = tmp_path / "backlog.md"
    backlog.write_text(
        "# Backlog\n\n"
        "| Title | Description | Priority | Status | Dependencies | Owner Role | Success Criteria |\n"
        "|---|---|---|---|---|---|---|\n"
        "| Add report hygiene checker to CI | Ensure policy checks run. | P1 | todo | none | hygiene | Workflow runs `scripts/check_report_hygiene.py` and fails on policy violations. |\n"
        "| Expand docs | Add notes. | P2 | todo | none | research | README includes a short troubleshooting subsection for NPZ schema and gene alignment. |\n",
        encoding="utf-8",
    )

    items = choose_next_task.parse_table(backlog)
    workflows = [(".github/workflows/validate.yml", "python scripts/check_report_hygiene.py")]
    readme = "No troubleshooting section"

    stale = choose_next_task.criterion_satisfied(items[0], workflows, readme, "")
    ready = choose_next_task.criterion_satisfied(items[1], workflows, readme, "")

    assert stale is not None
    assert ready is None


def test_choose_next_task_detects_readme_criteria() -> None:
    item = {
        "title": "Expand real NPZ docs with troubleshooting",
        "description": "",
        "priority": "P2",
        "status": "todo",
        "dependencies": "none",
        "owner_role": "research",
        "success_criteria": "README includes a short troubleshooting subsection for NPZ schema and gene alignment.",
    }

    evidence = choose_next_task.criterion_satisfied(
        item,
        workflows=[],
        readme_text="## real_npz troubleshooting\n- check schema and gene alignment",
        summary_text="",
    )

    assert evidence is not None
