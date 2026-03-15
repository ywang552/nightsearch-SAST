# Research Plan: Cross-Attention Spot Annotation for Spatial Transcriptomics

## 1) Problem formulation

Given a spatial transcriptomics dataset with spot-level observed expression vectors and a reference dictionary derived from annotated single-cell data, predict a **cell-type composition distribution** for each spot.

- Let \(x_s \in \mathbb{R}^G\) be observed spot expression for spot \(s\).
- Let dictionary entries \(r_c \in \mathbb{R}^{G_r}\) represent cell type \(c\) from reference data.
- Goal: predict \(\hat{y}_s \in \Delta^{C-1}\), where \(C\) is number of cell types.

This framing follows Zhang's problem context (spot annotation/deconvolution) and extends it with a transformer-inspired cross-attention architecture motivated by Youchuan Wang's forward direction.

## 2) Proposed model architecture

A modular model with four blocks:
1. **Spot encoder**: MLP/transformer-style encoder turning spot features into query embedding(s).
2. **Reference dictionary encoder**: projection/encoder for cell-type prototypes.
3. **Cross-attention block**: query attends over reference key-value pairs.
4. **Output head**: predicts per-spot composition distribution.

## 3) Query, Key, Value mapping

- **Query (Q):** encoded spot representation \(q_s\).
- **Key (K):** encoded reference prototypes \(k_c\).
- **Value (V):** encoded reference prototypes \(v_c\) (same or separate projection from keys).

Attention weights provide interpretable affinity between each spot and reference cell types.

## 4) Reference dictionary representation

Candidate choices:
1. Mean expression per cell type from scRNA-seq reference.
2. Multiple prototypes per cell type (substate-aware dictionary).
3. Pretrained embedding dictionary (e.g., from scGPT/Geneformer features).
4. Optional ontology-aware embeddings (Cell Ontology graph regularization).

## 5) Output definition

Primary output:
- \(\hat{y}_s\): compositional distribution over cell types for each spot.

Optional secondary outputs:
- Uncertainty estimates (Dirichlet concentration / variance head).
- Spot-level latent state embedding.

## 6) Training objectives

Primary candidates:
1. **KL divergence** between predicted and target compositions.
2. **Cross-entropy** when pseudo-label is a dominant cell type.
3. **MSE/MAE** for abundance regression when continuous proportions are available.

Regularization:
- Entropy control or sparsity on attention weights.
- Non-negativity and simplex constraints on compositions.
- Domain adaptation penalties across batches/platforms.

## 7) Supervision options

1. **Supervised:** use semi-synthetic spots with known mixtures.
2. **Weakly supervised:** pseudo-labels from established methods (cell2location/SPOTlight) plus consistency losses.
3. **Self-supervised pretraining:** pretrain encoders via masking/contrastive tasks, then fine-tune with limited labels.

## 8) Candidate datasets

Potential starting datasets (subject to licensing and preprocessing effort):
- 10x Visium public datasets (brain, cancer tissues).
- Slide-seq / Slide-seqV2 datasets with paired references.
- Benchmark datasets used in Tangram, cell2location, DestVI studies.
- Simulated mixtures derived from high-quality scRNA-seq atlases.

## 9) Baselines

1. SPOTlight-like NMF/NNLS baseline.
2. Stereoscope-like probabilistic baseline.
3. cell2location baseline.
4. DestVI baseline.
5. Ablated deep model without cross-attention (concatenation MLP).

## 10) Evaluation metrics

Primary:
- Jensen-Shannon divergence / KL divergence against ground-truth compositions.
- Pearson/Spearman correlation of predicted vs. true cell-type abundance.
- RMSE/MAE per cell type and per spot.

Secondary:
- Calibration / uncertainty quality (if uncertainty head is used).
- Biological plausibility (spatial smoothness, marker consistency).

## 11) Ablation studies

1. Remove cross-attention (replace with concatenation MLP).
2. Single prototype vs. multi-prototype dictionary.
3. Frozen vs. trainable reference encoder.
4. Pretrained encoder initialization vs. random init.
5. With/without attention sparsity regularizer.
6. Different output heads (softmax vs. Dirichlet parameterization).

## 12) Expected risks and bottlenecks

1. Domain shift between reference scRNA-seq and spatial platform.
2. Limited reliable ground-truth composition labels.
3. Overfitting with high-dimensional sparse features.
4. Sensitivity to dictionary quality and cell-type granularity.
5. Compute cost for large references or multi-resolution models.

## 13) Open research questions

1. Can cross-attention improve deconvolution robustness under severe domain shift?
2. How should dictionary entries be structured: single centroid, mixtures, or ontology-aware sets?
3. Does transformer pretraining materially help compared to strong probabilistic baselines?
4. Can attention weights provide faithful biological interpretability?

## 14) Phased implementation roadmap

### Phase 0 (done in this repo scaffold)
- Modular code skeleton (dataset/model/training/config/report).
- Minimal runnable placeholder with synthetic data.

### Phase 1 (2-4 weeks)
- Integrate one real dataset loader and one reference construction pipeline.
- Implement baseline NNLS/NMF comparator.
- Validate end-to-end metrics pipeline.

### Phase 2 (4-8 weeks)
- Run first comparative study: baseline vs cross-attention on one benchmark dataset.
- Conduct key ablations (attention on/off, dictionary variants).

### Phase 3 (8-12 weeks)
- Extend to multi-dataset evaluation and domain-shift tests.
- Add uncertainty modeling and interpretability analysis.

### Phase 4 (paper-prep)
- Consolidate best model, reproducible configs, and figure-generation scripts.
- Prepare manuscript-level benchmarking and error analysis.
