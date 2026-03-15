# nightsearch-SAST: Minimal Synthetic Dictionary Baseline for Cross-Attention Spot Annotation

## Overview
This report documents a runnable synthetic dictionary baseline for end-to-end spot annotation experiments with a cross-attention architecture. The baseline is intended as a controlled environment for validating model wiring, tensor interfaces, and optimization behavior before introducing real spatial transcriptomics and scRNA-seq references.

## Problem Statement
We need a minimal but complete pipeline that:

1. generates synthetic spot-level mixtures from a fixed cell-type dictionary,
2. maps spots and references into a shared latent space,
3. uses cross-attention to align spot queries with dictionary entries, and
4. predicts cell-type composition vectors suitable for KL-based training.

The goal is to provide fast, reproducible experimentation with clear tensor semantics.

## Method
### Implemented components
- Typed config support for synthetic data controls.
- Synthetic dataset generation from a fixed cell-type reference dictionary.
- Spot encoder + cross-attention + output head wiring.
- Minimal training script that logs metrics to JSON.

### Mathematical role of $Q$, $K$, and $V$
For a batch of spots:
- Spot features: $X \in \mathbb{R}^{B \times G}$
- Reference dictionary (batched): $R \in \mathbb{R}^{B \times C \times D_r}$
- Model width: $d$

Encoders produce:
$$
Q = f_{\text{spot}}(X) \in \mathbb{R}^{B \times 1 \times d},
$$
$$
K = f_{\text{ref}}(R) \in \mathbb{R}^{B \times C \times d},
$$
$$
V = f_{\text{ref}}(R) \in \mathbb{R}^{B \times C \times d}.
$$

Cross-attention:
$$
\operatorname{Attn}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_h}}\right)V,
$$
with head dimension $d_h=d/H$.

The output head maps attended representation $Z \in \mathbb{R}^{B \times 1 \times d}$ to composition probabilities:
$$
\hat{y}=\operatorname{softmax}(WZ+b) \in \mathbb{R}^{B \times C}.
$$

Training minimizes KL divergence against target mixtures sampled from a Dirichlet prior.

## Experiments
### Synthetic data assumptions
- A global reference dictionary $R_0 \in \mathbb{R}^{C \times D_r}$ is sampled once per split.
- Spot compositions are sampled as $y_i \sim \operatorname{Dirichlet}(\alpha\mathbf{1})$.
- Clean spot features follow linear mixing $x_i=y_iR_0$.
- If $D_r \neq G$, a random projection aligns feature dimensions.
- Gaussian noise is added to mixed features.

### Default tensor shapes
| Tensor | Shape |
|---|---|
| `spot_features` | `[B, G]` |
| `reference_embeddings` | `[B, C, D_r]` |
| `target_composition` | `[B, C]` |
| attention weights (averaged heads) | `[B, 1, C]` |

## Results
This baseline currently provides a functional training/evaluation path and machine-readable metric output (JSON), enabling iterative model and data-pipeline verification.

## Discussion
The synthetic setup isolates architectural behavior and confirms end-to-end consistency, but it does not yet capture domain shift, biological variability, or spatial covariate structure present in real data.

## Next Steps
1. Replace synthetic dictionary generation with a real scRNA-seq cell-type reference matrix.
2. Add optional spatial neighborhood covariates to the spot encoder.
3. Add calibration and ablation metrics (e.g., JS divergence, per-cell-type AUROC when labels exist).
4. Benchmark against classical deconvolution baselines on matched datasets.

## Implementation Notes
- Migrated this report from LaTeX to GitHub Markdown for direct repository readability.
- Preserved equations using GitHub-compatible math blocks.
- Replaced LaTeX tables with Markdown tables.
