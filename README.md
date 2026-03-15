# nightsearch-SAST

Research codebase for **spatial transcriptomics spot annotation** with a **cross-attention, reference-dictionary-guided** model and a simple **NNLS baseline**.

## Project goal

This repository targets spot-level cell type composition estimation where:
- **Query** comes from observed spot expression.
- **Key/Value** come from a reference cell type dictionary.
- Output is a **cell-type composition distribution per spot**.

## Repository structure

- `src/nightsearch_sast/`
  - `config.py`: typed config loader.
  - `data/dataset.py`: synthetic dictionary dataset + collate.
  - `models/cross_attention.py`: cross-attention model scaffold.
  - `baselines/nnls.py`: projected-gradient NNLS baseline.
  - `training/train.py`: training loop and validation metrics.
  - `main.py`: CLI entrypoint.
- `scripts/run_synthetic_baseline.py`: run experiment and write JSON metrics.
- `configs/default.yaml`: default experiment settings.
- `report/`: literature review, research plan, and current status report.
- `tests/test_smoke.py`: smoke tests for package and baseline.

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m nightsearch_sast.main --config configs/default.yaml
```

## Current implemented scope

- Cross-attention scaffold with spot and reference encoders.
- Synthetic dictionary data generation with configurable projection behavior.
- KL-based training/evaluation pipeline.
- NNLS comparator metric (`nnls_val_loss_mean`) for synthetic experiments.
- Research planning docs for real-data integration and benchmark phases.

## Still missing

- Real data loaders (Visium/Slide-seq/MERFISH).
- Reproduced external baselines (Tangram/cell2location/DestVI/SPOTlight).
- Experiment tracking, deterministic dataset splits, and plotting pipeline.
