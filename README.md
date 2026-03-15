# nightsearch-SAST

Research scaffold for **spatial transcriptomics spot annotation** with a proposed **cross-attention, reference-dictionary-guided** architecture.

## Project goal

This repository now serves as a serious starting point for a research program where:
- **Query** comes from observed spatial spot information,
- **Key/Value** come from a biological reference dictionary (e.g., cell-type signatures),
- model output is a **cell-type composition distribution per spot**.

The method is intentionally a scaffold, not a finalized algorithm.

## Repository structure

- `src/nightsearch_sast/`
  - `config.py`: typed experiment config loader
  - `data/dataset.py`: synthetic dictionary dataset + collate
  - `models/cross_attention.py`: spot encoder, reference encoder, cross-attention block, output head
  - `training/train.py`: training skeleton + loss + dataloaders
  - `main.py`: runnable experiment entrypoint
- `scripts/run_synthetic_baseline.py`: minimal experiment runner that writes JSON metrics
- `configs/default.yaml`: default experiment configuration
- `report/`
  - `literature_review.md` and `.pdf`
  - `research_plan.md` and `.pdf`
  - `final_report.md` and `.pdf`
- `tests/test_smoke.py`: smoke tests

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest -q
python -m nightsearch_sast.main --config configs/default.yaml
```

## What is implemented now

- Modular model skeleton for cross-attention spot annotation.
- Synthetic dictionary-driven dataset baseline with Dirichlet composition sampling.
- Training loop skeleton with compositional KL loss.
- Config-driven experiment entrypoint.
- Research documentation: literature review, research plan, final report.

## What is not implemented yet

- Real loaders for Visium/Slide-seq/MERFISH datasets.
- Full benchmark baselines (Tangram/cell2location/DestVI/SPOTlight reproductions).
- End-to-end experiment tracking and reproducibility scripts.

## PDF deliverables

PDF versions of literature review, research plan, and final report are included in `report/`.

If you want richer typography, regenerate with Pandoc locally:

```bash
pandoc report/literature_review.md -o report/literature_review.pdf
pandoc report/research_plan.md -o report/research_plan.pdf
pandoc report/final_report.md -o report/final_report.pdf
```

## Merge setup

Run this one-time local Git configuration so merges of generated report files keep the incoming version.

For Git Bash or macOS/Linux:

```bash
git config merge.keepIncoming.name "keep incoming version"
git config merge.keepIncoming.driver "cp %B %A"
```

For Windows PowerShell:

```powershell
git config merge.keepIncoming.name "keep incoming version"
git config merge.keepIncoming.driver "powershell -Command Copy-Item '%B' '%A' -Force"
```
