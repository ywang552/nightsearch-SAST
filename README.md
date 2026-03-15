# nightsearch-SAST

Research scaffold for **spatial transcriptomics spot annotation** with a **cross-attention** model and an **NNLS** baseline.

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
pytest -q
```

Run synthetic baseline:

```bash
python scripts/run_synthetic_baseline.py --config configs/default.yaml --output artifacts/synthetic_baseline_metrics.json
```

Run real pipeline (cross-attention + NNLS):

```bash
python scripts/create_real_example_data.py --output-dir data/processed/real
python scripts/run_real_pipeline.py --config configs/real_example.yaml --output artifacts/real_pipeline_metrics.json
```
