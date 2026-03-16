# nightsearch-SAST

Research codebase for **spatial transcriptomics spot annotation** with a **cross-attention, reference-dictionary-guided** model and a simple **NNLS baseline**.

## What now works

This repo supports two runnable experiment paths:

1. **Synthetic path** (original scaffold kept working).
2. **Real NPZ path** with both:
   - cross-attention training/evaluation
   - NNLS baseline evaluation

The real path expects NPZ files with aligned gene names and includes a tiny generator script (`scripts/create_real_example_data.py`) so you can produce local first-run data under `data/processed/real/`.

## Repository structure

- `src/nightsearch_sast/config.py`: typed config loader (synthetic + real modes)
- `src/nightsearch_sast/data/dataset.py`: synthetic dataset
- `src/nightsearch_sast/data/real_data.py`: real loader + reference dictionary builder
- `src/nightsearch_sast/models/cross_attention.py`: cross-attention model
- `src/nightsearch_sast/baselines/nnls.py`: NNLS baseline (projected gradient)
- `src/nightsearch_sast/evaluation/metrics.py`: unified evaluation metrics
- `src/nightsearch_sast/training/train.py`: synthetic training + tensor-based training path
- `reports/`: canonical location for experiment write-ups and archived research notes
- `reports/backlog.md`: lightweight planning board for agent-driven task selection
- `.github/agent-prompts/`: repo-specific prompts for planner/builder/reviewer/verifier/hygiene/research roles
- `scripts/run_synthetic_baseline.py`: synthetic runner
- `scripts/run_real_pipeline.py`: real runner writing metrics artifact
- `configs/default.yaml`: synthetic default config
- `configs/real_example.yaml`: real mode config

## Real NPZ format assumptions

`spots.npz`
- `X`: spot expression matrix `[n_spots, n_genes]`
- `gene_names`: gene ids `[n_genes]`

`reference_cells.npz`
- `X`: single-cell expression `[n_cells, n_genes]`
- `gene_names`: gene ids `[n_genes]`
- `cell_types`: cell-type label for each cell `[n_cells]`

Optional `spot_composition.npz`
- `Y`: ground-truth composition `[n_spots, n_cell_types]`

When `Y` is absent, the pipeline trains cross-attention on NNLS pseudo-labels and still reports reconstruction metrics honestly.

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m nightsearch_sast.main --config configs/default.yaml
```

## Multi-agent operating layer

This repository uses a lightweight, GitHub-native role flow designed for small, auditable changes.

1. **Planner**
   - Uses `reports/backlog.md` and repository summaries to pick the next ready task.
   - Skips stale `todo` backlog items when success criteria are already satisfied by obvious repo evidence (e.g., required script already referenced in a workflow, or README troubleshooting section already present).
   - Helper commands:
     - `python scripts/summarize_repo_state.py`
     - `python scripts/choose_next_task.py --backlog reports/backlog.md`
2. **Builder**
   - Implements one scoped task and runs fast checks.
3. **Reviewer**
   - Verifies scope control, code quality, and AGENTS policy alignment.
4. **Verifier**
   - Runs fast checks by default; runs broad checks when model/data paths changed.
5. **Hygiene**
   - Runs low-risk consistency checks for backlog and report policies.
6. **Research**
   - Maintains Markdown experiment notes, assumptions, and measured metrics.

### Human-controlled gates

- Pull requests remain human-reviewed and human-approved before merge.
- Automation provides recommendations and validation signals, not autonomous merge decisions.

### CI/workflow map

- `validate.yml`: **fast PR checks** (smoke run, fast pytest, backlog/report hygiene checks).
- `validate-full.yml`: **broader checks** on `main` pushes/manual dispatch.
- `planner.yml`: manual planning helper that validates backlog and uploads summary/task recommendation artifacts.
- `hygiene.yml`: manual/weekly low-cost repository hygiene checks.
- `codex-run.yml`: manual Codex execution workflow for operator-provided tasks.

### Triggering workflows

- Fast PR checks: open/update a PR.
- Planner assist: run **Planner Assist (Manual)** from GitHub Actions.
- Hygiene checks: run **Hygiene Check** manually or let weekly schedule run.
- Broad CI: push to `main` or run **Validate Full** manually.

## Current implemented scope

- Cross-attention scaffold with spot and reference encoders.
- Synthetic dictionary data generation with configurable projection behavior.
- KL-based training/evaluation pipeline.
- NNLS comparator metric (`nnls_val_loss_mean`) for synthetic experiments (`train()` contract).
- Research planning docs for real-data integration and benchmark phases.

## Still missing

- Native adapters for named public real-data sources (e.g., direct Visium/Slide-seq/MERFISH ingestion beyond NPZ bundles).
- Reproduced external baselines (Tangram/cell2location/DestVI/SPOTlight).
- Experiment tracking, deterministic dataset splits, and plotting pipeline.

## Reporting docs note

`reports/` is the canonical location for experiment output and research notes. Historical planning documents are kept under `reports/archive/`.
