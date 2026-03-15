# Backlog

Lightweight planning board for agent-assisted work. Keep items small and dependency-aware.

## Status legend
- `todo`: not started
- `in_progress`: actively being implemented
- `blocked`: waiting on dependency or decision
- `done`: completed

## Items

| Title | Description | Priority | Status | Dependencies | Owner Role | Success Criteria |
|---|---|---|---|---|---|---|
| Add report hygiene checker to CI | Ensure Markdown report policies are validated in automation with low runtime cost. | P1 | todo | none | hygiene | Workflow runs `scripts/check_report_hygiene.py` and fails on policy violations. |
| Expand real NPZ docs with troubleshooting | Document common `real_npz` input issues and fixes. | P2 | todo | none | research | README includes a short troubleshooting subsection for NPZ schema and gene alignment. |
| Add one additional fast unit test for metrics edge-case | Improve confidence in `evaluate_predictions` for missing targets and reconstruction-only path. | P2 | todo | none | builder | New test passes in `pytest -q -m "not slow"` and verifies expected metric keys. |
