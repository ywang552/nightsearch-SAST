# Final Report: Cross-Attention Direction for Spatial Transcriptomics Spot Annotation

## 1) Literature reviewed

Completed a focused, recent literature review centered on:
- Spot annotation/deconvolution in spatial transcriptomics (Tangram, cell2location, DestVI, SPOTlight, Stereoscope).
- Transformer/LLM-style models in transcriptomics (scBERT, Geneformer, scGPT, xTrimoGene).
- Reference-guided and dictionary-guided prediction ideas relevant to cross-attention.

The review distinguishes:
- **Verified literature findings** from published papers/preprints.
- **Speculative but plausible research hypotheses** for our proposed architecture.

See `report/literature_review.md` for paper-by-paper details.

## 2) Research plan produced

Prepared a practical research plan in `report/research_plan.md` including:
- Formal problem setup.
- Proposed architecture and explicit Query/Key/Value assignments.
- Dictionary representation strategies.
- Output, losses, and supervision modes.
- Dataset candidates, baseline methods, metrics.
- Ablation plan, risks, open questions, and phased roadmap.

## 3) Code files created/modified

### Core scaffold added
- `src/nightsearch_sast/config.py`
- `src/nightsearch_sast/data/dataset.py`
- `src/nightsearch_sast/models/cross_attention.py`
- `src/nightsearch_sast/training/train.py`
- package `__init__` files under `data/`, `models/`, `training/`, `utils/`

### Existing files updated
- `src/nightsearch_sast/main.py` (now runs scaffold training)
- `configs/default.yaml` (experiment structure)
- `tests/test_smoke.py` (entrypoint + model shape tests)
- `requirements.txt` (torch/transformers dependencies)
- `README.md` (project/research usage documentation)

### Report deliverables
- `report/literature_review.md`
- `report/research_plan.md`
- `report/final_report.md`
- PDF counterparts in `report/` (generated from markdown source)

## 4) Assumptions made

1. Zhang's paper provides baseline framing for spot annotation/deconvolution.
2. Youchuan Wang's statement motivates transformer/LLM-style exploration.
3. Current code is intentionally a research scaffold with synthetic placeholder data.
4. Real-data loaders and benchmark pipelines require dataset-specific integration work.
5. Some cited methods are provided as conceptual baselines rather than fully reimplemented in this commit.

## 5) What remains incomplete

1. No real spatial transcriptomics dataset ingestion yet.
2. No full reproduction pipelines for Tangram/cell2location/DestVI baselines.
3. No hyperparameter search, experiment tracking, or figure-generation scripts.
4. No biological validation (marker-level interpretation, histology-aligned analyses).
5. No manuscript-quality benchmarking yet.

## 6) Recommended next steps

1. Implement one production data loader (e.g., Visium + paired reference).
2. Add at least one simple non-deep baseline (NNLS/NMF).
3. Add experiment tracking (e.g., wandb or MLflow) and deterministic splits.
4. Run initial ablations: no-attention vs cross-attention; single vs multi-prototype dictionary.
5. Evaluate domain-shift robustness and uncertainty calibration.
6. Iterate architecture toward richer reference representations and ontology constraints.

## PDF rendering note

In this environment, PDFs were generated programmatically from the markdown text to satisfy deliverable requirements. If richer formatting is needed, render the markdown with Pandoc in a local environment.
