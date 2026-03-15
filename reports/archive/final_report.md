# Final Report: Current State of Cross-Attention Spot Annotation Scaffold

## 1) Scope completed in code

Implemented and runnable today:

1. **Cross-attention scaffold model** for spot composition prediction.
2. **Synthetic dictionary dataset** with Dirichlet-composition sampling.
3. **Config-driven training loop** with compositional KL loss.
4. **NNLS baseline comparator** using projected-gradient simplex-constrained fitting.
5. **Smoke tests** covering entrypoint, model shape, synthetic data validity, and NNLS output constraints.

## 2) What changed in this iteration

- Added `src/nightsearch_sast/baselines/nnls.py` and package export.
- Updated training to report both model validation loss and NNLS validation loss.
- Tightened synthetic data behavior so dimension mismatch requires explicit random projection.
- Aligned default config dimensions (`spot_feature_dim == ref_hidden_dim`) for a coherent synthetic setting.
- Updated tests and README to match actual code behavior.

## 3) Why this is the right next step

Before integrating real datasets, the project needed a meaningful comparator and a coherent synthetic setup. This iteration provides:

- A **non-deep baseline** to prevent evaluating cross-attention in isolation.
- A **clearer synthetic identifiability assumption** (or explicit projection opt-in).
- Better **signal for progress** through additional metrics and tests.

## 4) Current limitations

Still missing for full research execution:

1. Real spatial transcriptomics data loaders and preprocessing.
2. Reference dictionary construction from real annotated single-cell data.
3. Baseline reproductions beyond NNLS (SPOTlight/cell2location/DestVI/Tangram).
4. Experiment tracking + visualization + reproducible study scripts.

## 5) Recommended immediate next task

Implement a first real-data pipeline (e.g., one public Visium dataset) that outputs:

- spot expression matrix,
- matched reference dictionary,
- train/validation split,
- shared metric interface reused by cross-attention and NNLS.
