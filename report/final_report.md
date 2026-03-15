# Final Report: Cross-Attention Direction for Spatial Transcriptomics Spot Annotation

## Grounding step on required source PDFs

I attempted to read the two required PDF files before preparing the updates:

1. `13059_2025_3608_MOESM1_ESM.pdf` (Zhang context file)
2. `research_statement_template.pdf` (Youchuan Wang direction file)

However, in this runtime those files are not present in the repository or elsewhere in the container filesystem. Because of that, I could not extract their exact text directly here. This report and associated plans are therefore grounded in the stated task framing, and are explicitly marked as **provisional until those two PDFs are mounted in the repo**.

## 1) Literature reviewed

Completed a focused literature review centered on:
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
- `src/nightsearch_sast/main.py` (runs scaffold training)
- `configs/default.yaml` (experiment structure)
- `tests/test_smoke.py` (entrypoint + model shape tests)
- `requirements.txt` (torch/transformers dependencies)
- `README.md` (project/research usage documentation)

### Report deliverables   
- `report/literature_review.md`
- `report/research_plan.md`
- `report/final_report.md`
- PDF counterparts in `report/` (generated from markdown source)

## 4) How each required source file informed the work

Because the two PDFs were unavailable in this container, this section reflects the *intended mapping* and what was used from the task statement:

1. `13059_2025_3608_MOESM1_ESM.pdf` (Zhang): used as the intended anchor for the spot-annotation problem framing and baseline orientation.
2. `research_statement_template.pdf` (Youchuan Wang): used as the intended motivation for transformer/LLM-style, especially cross-attention, future direction.

Once those PDFs are present, the immediate next revision should add line-precise evidence from each file and update all report sections accordingly.

## 5) Assumptions made

1. Zhang's file is intended to frame spot annotation/deconvolution as the core problem context.
2. Youchuan Wang's statement is intended to motivate transformer/LLM-style exploration.
3. Current code is intentionally a research scaffold with synthetic placeholder data.
4. Real-data load ers and benchmark pipelines require dataset-specific integration work.
5. Some cited methods are provided as conceptual baselines rather than fully reimplemented in this commit.

## 6) What remains incomplete

1. No real spatial transcriptomics dataset ingestion yet.
2. No full reproduction pipelines for Tangram/cell2location/DestVI baselines.
3. No hyperparameter search, experiment tracking, or figure-generation scripts.
4. No biological validation (marker-level interpretation, histology-aligned analyses).
5. No manuscript-quality benchmarking yet.
6. Required source PDF extraction could not be completed in this runtime due to missing files.

## 7) Recommended next steps

1. Add the two required PDFs into repository root and rerun grounding extraction.
2. Revise literature/research/final reports with explicit quotations/structured notes from those two files.
3. Implement one production data loader (e.g., Visium + paired reference).
4. Add at least one simple non-deep baseline (NNLS/NMF).
5. Run initial ablations: no-attention vs cross-attention; single vs multi-prototype dictionary.

## PDF rendering note

In this environment, PDFs were generated programmatically from the markdown text to satisfy deliverable requirements. If richer formatting is needed, render the markdown with Pandoc in a local environment.
