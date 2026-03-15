# Literature Review: Spatial Transcriptomics Spot Annotation with Cross-Attention Direction

## Scope and framing

## Required grounding note

Per project requirements, this review should be grounded by two repository PDFs (`13059_2025_3608_MOESM1_ESM.pdf` and `research_statement_template.pdf`) before synthesis. In this runtime those files were not present, so this review is marked provisional and should be updated immediately once those files are available.

---

This review focuses on work from roughly 2021-2025, with emphasis on: (1) spot-level annotation/deconvolution for spatial transcriptomics, (2) transformer/LLM-style methods in transcriptomics and omics, and (3) reference-guided or dictionary-guided prediction paradigms relevant to a query-key-value formulation.

**Context framing used in this project**
- Baseline problem framing follows Zhang et al. (spot annotation/deconvolution as a core spatial transcriptomics challenge).
- Forward direction follows Youchuan Wang's research statement: investigate transformer/LLM-style architectures, especially cross-attention, for spot annotation.

---

## Verified literature summaries

### 1) Li et al., Tangram (Nature Methods, 2021)
- **Problem setting:** Map single-cell references onto spatial transcriptomics positions.
- **Input/Output:** Input is scRNA-seq reference + spatial expression matrix; output is mapping probabilities from cells/cell types to locations.
- **Model idea:** Optimization-based alignment preserving gene-expression concordance across modalities.
- **Supervision:** Weakly supervised/self-consistent alignment, no direct cell-level ground truth required.
- **Strengths:** Flexible integration between single-cell and spatial datasets; broad adoption.
- **Weaknesses:** Depends strongly on reference quality and shared gene signal.
- **Relevance:** Conceptually close to dictionary-guided annotation where reference priors drive spot interpretation.

### 2) Kleshchevnikov et al., cell2location (Nature Biotechnology, 2022)
- **Problem setting:** Estimate cell-type abundance in each spatial spot using single-cell references.
- **Input/Output:** Input is spatial counts + reference signatures; output is spot-wise cell-type abundance estimates.
- **Model idea:** Hierarchical Bayesian model accounting for technical effects and overdispersion.
- **Supervision:** Reference-guided probabilistic inference.
- **Strengths:** Strong uncertainty-aware framework; robust in noisy data.
- **Weaknesses:** Inference can be computationally intensive; model assumptions may be restrictive in some tissues.
- **Relevance:** A high-quality baseline for our proposal's output target (cell-type composition per spot).

### 3) Lopez et al., DestVI (Nature Biotechnology, 2022)
- **Problem setting:** Multi-resolution deconvolution and cell-state variation in spatial spots.
- **Input/Output:** Input is scRNA-seq + spatial counts; output includes cell-type proportions and latent state information.
- **Model idea:** Variational inference framework extending deep generative modeling for spatial mapping.
- **Supervision:** Reference-informed latent variable modeling.
- **Strengths:** Captures within-cell-type variation beyond coarse proportions.
- **Weaknesses:** Increased model complexity and tuning overhead.
- **Relevance:** Suggests that composition-only outputs can be extended with richer state-aware heads in future cross-attention variants.

### 4) Andersson et al., Stereoscope (Nature Methods, 2020; included as classic baseline)
- **Problem setting:** Deconvolve spatial spots using scRNA-seq references.
- **Input/Output:** Spot counts + reference scRNA-seq; output spot-level cell-type proportions.
- **Model idea:** Probabilistic count-based modeling.
- **Supervision:** Reference-based statistical inference.
- **Strengths:** Influential and interpretable baseline.
- **Weaknesses:** Earlier generation method; may underperform newer flexible models.
- **Relevance:** Important baseline comparator despite being slightly older than the 4-year emphasis.

### 5) Elosua-Bayes et al., SPOTlight (NAR, 2021)
- **Problem setting:** Reference-based deconvolution for spatial transcriptomics spots.
- **Input/Output:** Spatial expression and scRNA-seq-derived signatures; output mixture proportions.
- **Model idea:** Seeded non-negative matrix factorization + non-negative least squares.
- **Supervision:** Reference-guided matrix decomposition.
- **Strengths:** Practical and interpretable; relatively easy to deploy.
- **Weaknesses:** Linear assumptions can limit expressivity.
- **Relevance:** A direct dictionary-style baseline to benchmark against cross-attention.

### 6) He et al., scBERT (Briefings in Bioinformatics, 2022)
- **Problem setting:** Foundation-style modeling for single-cell transcriptomes.
- **Input/Output:** Gene-expression tokens/features as input; outputs for downstream classification/annotation tasks.
- **Model idea:** BERT-like transformer pretraining adapted for scRNA-seq.
- **Supervision:** Self-supervised pretraining + fine-tuning.
- **Strengths:** Demonstrates transformer feasibility for cellular expression data.
- **Weaknesses:** Primarily single-cell; not spatially explicit.
- **Relevance:** Supports using transformer encoders for spot/query representations.

### 7) Theodoris et al., Geneformer (Nature, 2023)
- **Problem setting:** Foundation transformer model for context-aware representation learning in transcriptomes.
- **Input/Output:** Large-scale single-cell transcriptomes in tokenized/ranked gene space; outputs latent embeddings for multiple tasks.
- **Model idea:** Transformer pretraining to capture gene-gene context.
- **Supervision:** Large-scale self-supervised pretraining.
- **Strengths:** Strong transfer learning evidence in transcriptomics.
- **Weaknesses:** Limited direct spatial inductive bias.
- **Relevance:** Motivates initializing spot encoders or reference encoders with pretrained omics transformers.

### 8) Cui et al., scGPT (Nature Methods, 2024)
- **Problem setting:** Generative pretraining for single-cell biology across tasks/modalities.
- **Input/Output:** Single-cell expression as model tokens/features; outputs include embeddings and task-specific predictions.
- **Model idea:** GPT-style pretraining objective adapted to cell biology.
- **Supervision:** Primarily self-supervised pretraining with downstream adaptation.
- **Strengths:** Strong foundation-model evidence in cellular omics.
- **Weaknesses:** Spatial integration remains indirect.
- **Relevance:** Supports LLM-style research direction and potential pretraining assets for our architecture.

### 9) Lai et al., xTrimoGene (arXiv, 2023)
- **Problem setting:** Large-scale masked modeling for single-cell transcriptomics.
- **Input/Output:** Sparse gene-expression profiles; output contextual representations.
- **Model idea:** Scalable transformer for single-cell foundation modeling.
- **Supervision:** Self-supervised masked modeling.
- **Strengths:** Scalability and representation quality.
- **Weaknesses:** Preprint status and limited direct spatial benchmarks.
- **Relevance:** Candidate backbone for query or dictionary encoders.

### 10) Histology-aware deep models for spatial gene expression prediction (e.g., HisToGene, 2023)
- **Problem setting:** Predict expression or spatial patterns from histology/context.
- **Input/Output:** Histology image patches and/or spatial neighborhoods as input; predicted gene/spatial features as output.
- **Model idea:** Attention/transformer modules for long-range context.
- **Supervision:** Supervised training with aligned image-expression data.
- **Strengths:** Demonstrates attention mechanisms in spatial omics contexts.
- **Weaknesses:** Task differs from reference-based spot deconvolution.
- **Relevance:** Architectural clues for adding multi-modal keys/values (e.g., histology dictionary augmentation).

---

## Clearly marked speculative connections (not established methods)

1. **Cross-attention dictionary deconvolution** (our proposed direction): using spot embedding as query and cell-type reference prototypes as key/value to predict composition.
2. **Hybrid losses** that combine compositional KL with attention sparsity regularizers and ontology constraints.
3. **Foundation-pretrained initialization** (Geneformer/scGPT-like) for both spot and reference encoders in spatial tasks.
4. **Uncertainty-aware attention** by integrating Bayesian output heads with deterministic cross-attention backbones.

These are plausible research directions inferred from existing trends, not claims of already published solutions under the same formulation.

---

## Practical baseline set for this repository

Recommended initial baseline methods to implement/compare:
1. NNLS/NMF-style dictionary regression (SPOTlight-like baseline).
2. Probabilistic reference-guided deconvolution (cell2location-like baseline when tooling permits).
3. Deep latent deconvolution baseline (DestVI-style if available).
4. Proposed cross-attention model scaffold in this repo.

---

## References

1. Li B, et al. Tangram: alignment of spatially resolved and single-cell transcriptomes. *Nature Methods*. 2021.
2. Kleshchevnikov V, et al. Cell2location maps fine-grained cell types in spatial transcriptomics. *Nature Biotechnology*. 2022.
3. Lopez R, et al. DestVI identifies cell-type proportions and states in spatial transcriptomics. *Nature Biotechnology*. 2022.
4. Andersson A, et al. Single-cell and spatial transcriptomics enables probabilistic inference of cell type topography (Stereoscope). *Nature Methods*. 2020.
5. Elosua-Bayes M, et al. SPOTlight: seeded NMF regression for spot deconvolution. *Nucleic Acids Research*. 2021.
6. He B, et al. scBERT as a pretrained model for single-cell analysis. *Briefings in Bioinformatics*. 2022.
7. Theodoris CV, et al. Geneformer: transfer learning in single-cell transcriptomics. *Nature*. 2023.
8. Cui H, et al. scGPT: toward a foundation model for single-cell multi-omics. *Nature Methods*. 2024.
9. Lai Y, et al. xTrimoGene: large-scale foundation model for single-cell transcriptome data. *arXiv*. 2023.
10. He X, et al. HisToGene: spatial gene expression prediction from histology with attention. *arXiv*. 2023.
