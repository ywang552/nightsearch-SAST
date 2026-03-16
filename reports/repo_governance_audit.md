# Repository Governance and Consistency Audit

Date: 2026-03-16

## Scope and concurrency safety

- This audit was performed on branch `codex/repo-governance-audit` to avoid interference with other active work.
- No files under `notebooks/` were modified.
- Potential overlap area detected: `notebooks/` (active notebook-generation task likely writing there). Those files were inspected only at high level and intentionally not edited.

## Classification summary

- **Source code**: `src/nightsearch_sast/**`
- **Configs**: `configs/*.yaml`, `pytest.ini`
- **Tests**: `tests/*.py`
- **Scripts**: `scripts/*.py`, `scripts/run-codex.sh`
- **Reports/docs**: `README.md`, `reports/**/*.md`, `data/README.md`, `notebooks/README.md`, `docs/*.md`
- **CI/workflows**: `.github/workflows/*.yml`
- **Generated/derived artifacts currently tracked**: root-level PDFs (`13059_2025_3608_MOESM1_ESM.pdf`, `research_statement_template.pdf`)
- **Archive/legacy**: `reports/archive/*.md`

## Governance table

| Path | Category | Purpose | Canonical (Y/N) | Owner area | Status | Recommended action |
|---|---|---|---|---|---|---|
| `src/nightsearch_sast/` | source code | Core model/data/training/evaluation implementation | Y | training + data pipeline | current | Keep as single source of runtime truth. |
| `src/nightsearch_sast/main.py` | source code | CLI entrypoint for scaffold training | Y | training | current | Keep consistent with smoke config and README quickstart. |
| `src/nightsearch_sast/config.py` | source code/config schema | Typed config schema and YAML loader | Y | training + configs | current | Treat as canonical schema; update docs/tests/workflows when fields change. |
| `src/nightsearch_sast/data/real_data.py` | source code | Real NPZ bundle loader and gene matching | Y | data pipeline | current | Keep synchronized with `README.md` normalized bundle contract and converter script. |
| `scripts/run_real_pipeline.py` | script | Real-data end-to-end runner and metrics JSON writer | Y | scripts + data pipeline | current | Keep consistent with `configs/real_example.yaml` and test coverage in `tests/test_smoke.py`. |
| `scripts/run_synthetic_baseline.py` | script | Synthetic baseline runner producing JSON metrics | Y | scripts + training | current | Keep aligned with synthetic config defaults and README pathways. |
| `scripts/convert_dlpfc_spatiallibd_bundle.py` | script | Converts CSV exports to normalized NPZ bundle | Y | data pipeline | current | Keep keys/semantics aligned with loader and README contract. |
| `scripts/create_real_example_data.py` | script | Generates tiny reproducible real-style example data | Y | data pipeline | current | Keep as canonical local demo-data generation path. |
| `configs/default.yaml` | config | Default synthetic training configuration | Y | configs + training | current | Keep aligned with `main.py` default and synthetic smoke behavior. |
| `configs/smoke.yaml` | config | Fast CI-friendly smoke configuration | Y | configs + CI | current | Keep small and deterministic; required by `validate.yml`. |
| `configs/real_example.yaml` | config | Default real NPZ example configuration | Y | configs + data pipeline | current | Keep bundle path and supported keys aligned with loader script behavior. |
| `tests/test_smoke.py` | tests | Fast and integration-ish checks for runtime paths | Y | tests | current | Continue covering both synthetic and real entrypoints; keep `slow` marks accurate. |
| `tests/test_choose_next_task.py` | tests | Unit tests for planner helper logic | Y | scripts + tests | current | Keep in sync with backlog-table schema and selection heuristics. |
| `.github/workflows/validate.yml` | CI/workflow | Fast PR gate checks | Y | CI | current | Remains canonical required gate; keep commands in sync with README and scripts. |
| `.github/workflows/validate-full.yml` | CI/workflow | Expanded checks on `main` and manual runs | Y | CI | current | Keep broader checks stable; avoid drift from runtime entrypoint behavior. |
| `README.md` | documentation | Canonical user-facing usage and architecture doc | Y | docs + training/data pipeline | current | Keep as canonical top-level doc; update whenever CLI/config/NPZ contract changes. |
| `data/README.md` | documentation | Data directory conventions and NPZ notes | Y | data pipeline + docs | current | Keep consistent with real bundle contract and script outputs. |
| `notebooks/README.md` | documentation | Notebook placement guidance | Y | docs + notebooks | current | Do not mix reusable logic into notebooks; no governance changes needed here. |
| `reports/backlog.md` | reports | Agent task board and planning metadata | Y (for planning) | reports + scripts | current | Keep table schema stable because scripts parse it directly. |
| `reports/dlpfc_real_pipeline.md` | reports | Snapshot narrative for real-data v1 assumptions | N (snapshot) | reports | current | Keep as milestone note; cross-link from future live docs if still relevant. |
| `reports/synthetic_dictionary_baseline.md` | reports | Snapshot of synthetic baseline rationale | N (snapshot) | reports | current | Keep as milestone report; do not treat as API/spec source. |
| `reports/archive/` | archive | Historical notes and legacy reports | N (archive) | reports | archive | Keep archive-only; avoid editing except to move superseded notes in. |
| `scripts/summarize_repo_state.py` | script | Emits planner-oriented summary artifact | N (derived helper) | scripts + planning | current | Document output as derived and non-canonical in governance rules. |
| `planner-repo-summary.md` (if generated) | derived artifact | Generated planning snapshot | N | reports/planning | derived | Do not commit by default; regenerate as needed. |
| `scripts/check_report_hygiene.py` | script | Enforces report hygiene policy | Y | CI + reports | current | Extend only with low-cost checks; keep policy in sync with governance doc. |
| `13059_2025_3608_MOESM1_ESM.pdf` | generated/derived artifact | External/supporting PDF in repo root | N | docs/reports hygiene | stale/unclear | Move to dedicated `docs/external/` (if intentionally tracked) or remove from git and reference by URL. |
| `research_statement_template.pdf` | generated/derived artifact | Template PDF in repo root | N | docs/reports hygiene | stale/unclear | Same as above; avoid root-level binary clutter. |
| `.env.example` | config/environment | Environment template for local tooling | Y | scripts/infra | current | Keep minimal and synchronized with `scripts/run-codex.sh` expectations. |
| `Dockerfile` | infra | Codex runtime image build target used by CI | Y | CI + infra | current | Keep aligned with `validate-full.yml` docker checks and entrypoint assumptions. |

## Drift and consistency findings

### README vs implementation

- README’s described real NPZ bundle contract matches loader keys in `src/nightsearch_sast/data/real_data.py` and conversion/runtime scripts.
- README quickstart commands align with existing scripts and configs.
- Minor governance gap: README does not explicitly distinguish **canonical docs** vs **snapshot reports**, which can cause maintenance drift over time.

### Reports vs implementation state

- `reports/dlpfc_real_pipeline.md` and `reports/synthetic_dictionary_baseline.md` read as milestone snapshots and are broadly consistent, but they are not versioned as explicitly “snapshot-only” by naming convention.
- `reports/archive/` exists and is being used, but top-level `reports/` currently mixes planning (`backlog.md`) and milestone notes without a clear taxonomy.

### Configs vs supported runtime paths

- Supported runtime paths are clear: synthetic via `main.py`/`run_synthetic_baseline.py`, real via `run_real_pipeline.py`.
- `configs/default.yaml` still includes split-NPZ real paths while project direction emphasizes bundle-first; this is not incorrect (compatibility mode exists), but should remain documented as secondary compatibility path.

### Tests vs claimed functionality

- Fast tests cover synthetic forward path, real bundle loading/alignment, runner behavior, and planner utility.
- Slow integration tests are appropriately marked with `@pytest.mark.slow`, matching CI split between fast and full runs.

### CI workflows vs actual commands

- `validate.yml` commands align with stated fast checks and hygiene/backlog validation scripts.
- `validate-full.yml` adds Docker checks not described in detail in README, but this is acceptable; governance should document CI file roles explicitly.

### Scripts vs entrypoints

- Script entrypoints are coherent with config defaults and test coverage.
- Planner/helper scripts rely on stable Markdown table shape in `reports/backlog.md`; this coupling should be explicitly governed.

## Top duplication and risk issues

1. **Mixed report roles** in `reports/` (planning + snapshots + historical) without strict structure labels.
2. **Root-level PDFs** introduce ambiguous ownership/state and conflict with lightweight repo hygiene goals.
3. **Potential dual-path ambiguity** in real data inputs (bundle NPZ vs split NPZ) can confuse contributors if not governed as canonical+compatibility.

## Proposed canonical structure going forward

- `README.md`: canonical user/operator guide.
- `docs/repo_governance.md`: canonical repository governance and update policy.
- `reports/backlog.md`: canonical planning board (machine-parseable table).
- `reports/milestones/*.md` (proposed future folder): dated milestone snapshots.
- `reports/archive/*.md`: immutable or near-immutable historical notes.
- `src/nightsearch_sast/config.py`: canonical config schema authority.

## Archive/delete/merge/rename recommendations

- **Archive/relocate** root PDFs into a single explicit location (`docs/external/`) if they must be tracked; otherwise remove from git.
- **Introduce `reports/milestones/`** and migrate top-level milestone notes there in a future low-risk cleanup PR.
- **Keep `reports/archive/` as archive-only**; no policy exceptions.
- **Retain split-NPZ compatibility code**, but label it compatibility mode in docs/governance.

## Skipped due to likely overlap with active notebook task

- All edits under `notebooks/` were intentionally skipped.
- Any notebook-linked narrative updates were deferred to avoid conflicting with the concurrent notebook-generation task.

## Top 10 stale or risky files/folders

1. `13059_2025_3608_MOESM1_ESM.pdf` (root-level binary; unclear governance)
2. `research_statement_template.pdf` (root-level binary; unclear governance)
3. `reports/` (mixed lifecycle roles without strong folder taxonomy)
4. `reports/dlpfc_real_pipeline.md` (snapshot naming/lifecycle ambiguity)
5. `reports/synthetic_dictionary_baseline.md` (snapshot naming/lifecycle ambiguity)
6. `configs/default.yaml` real split-path fields (canonical-vs-compatibility ambiguity)
7. `scripts/choose_next_task.py` + `reports/backlog.md` tight schema coupling risk
8. `scripts/summarize_repo_state.py` output artifact ownership unclear when generated
9. `README.md` lacks explicit canonical/derived ownership map
10. `.github/workflows/validate-full.yml` broader checks not captured in a dedicated governance doc (addressed by new governance file)
