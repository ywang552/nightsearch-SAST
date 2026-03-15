# AGENTS.md

## Mission
`nightsearch-SAST` is a Python-first research codebase for spatial transcriptomics spot annotation/deconvolution. Agent work should improve model quality, reproducibility, and research clarity while preserving existing runnable paths (`synthetic` and `real_npz`) and keeping PR review human-controlled.

## Coding standards
- Prefer small, reviewable diffs that extend existing modules instead of adding parallel systems.
- Keep source under `src/nightsearch_sast/`; keep runnable helpers under `scripts/`.
- Follow existing style: type hints where practical, descriptive function names, and concise docstrings for scripts.
- Avoid introducing heavy dependencies unless justified in the PR notes.
- Never commit generated large artifacts (especially PDFs or bulky binary outputs).

## Testing expectations
- For Python changes, run at least:
  - `PYTHONPATH=src pytest -q -m "not slow"`
- When touching training/data pipelines or scripts, also run relevant entrypoint checks, e.g.:
  - `PYTHONPATH=src python -m nightsearch_sast.main --config configs/smoke.yaml`
  - `PYTHONPATH=src python scripts/run_synthetic_baseline.py --config configs/default.yaml --output <tmpfile>`
- Keep tests cheap by default; mark longer cases with `@pytest.mark.slow`.

## CI expectations
- `validate.yml` is the fast PR gate (required-file checks, smoke run, fast tests, shell syntax).
- `validate-full.yml` is broader validation for `main` and manual execution.
- New automation should be lightweight, understandable, and GitHub-native.

## Branching and PR rules
- One scoped task per PR where possible.
- Do not mix unrelated refactors with feature changes.
- Summarize what changed, why, and how it was validated.
- Human approval is required before merge; agents must not assume auto-merge.

## Docs and report policy
- Keep reports and research notes in Markdown under `reports/`.
- Use GitHub-compatible math formatting (`$$...$$` / `$...$`).
- Archive historical notes in `reports/archive/`.
- Do not commit generated PDFs or notebook outputs unless explicitly requested.

## Autonomous change safety limits
Agents may autonomously:
- Add/modify scripts, tests, docs, and CI for clear low-risk improvements.
- Refactor small internal code paths when behavior is preserved and validated.

Agents must avoid without explicit human direction:
- Large architecture rewrites.
- Dependency overhauls.
- Broad data-format migrations.
- Destructive cleanup of research history.

## When to stop and defer to a human
Stop and defer when:
- Multiple plausible research directions exist and choice materially affects outcomes.
- A change would alter benchmark interpretation or reported conclusions.
- Required data/license context is unavailable.
- A requested cleanup appears high-risk or potentially lossy.

## Preferred task size and scope
- Target tasks that can be reviewed in ~50-300 LOC net change.
- If a task is larger, split into planner-defined sub-tasks with explicit success criteria.
- Keep each task independently testable and reversible.
