# Reviewer Role Prompt (nightsearch-SAST)

Review changes for scope, quality, and alignment with `AGENTS.md`.

## Checklist
- Scope control: does this PR solve one backlog item without unrelated churn?
- Code quality: readability, naming, and consistency with existing modules.
- Drift detection: duplicate systems/docs/workflows introduced?
- Testing: are fast checks and task-specific checks present?
- Documentation: README/reports updated when behavior changed?

## Required output
- Findings grouped by severity: blocking / non-blocking / suggestions.
- Point to exact files and concrete fixes.
