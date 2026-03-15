"""Simple non-negative least squares baseline solved with projected gradient descent."""

from __future__ import annotations

import torch


def run_nnls_baseline(
    spot_matrix: torch.Tensor,
    reference_dictionary: torch.Tensor,
    steps: int = 300,
    lr: float = 0.05,
) -> torch.Tensor:
    """Estimate spot compositions with non-negativity + simplex normalization."""
    n_spots = spot_matrix.shape[0]
    n_cell_types = reference_dictionary.shape[0]

    weights = torch.full((n_spots, n_cell_types), fill_value=1.0 / n_cell_types)
    ref_t = reference_dictionary.T

    for _ in range(steps):
        recon = weights @ reference_dictionary
        grad = (recon - spot_matrix) @ ref_t
        weights = (weights - lr * grad).clamp_min(0.0)
        weights = weights / weights.sum(dim=1, keepdim=True).clamp_min(1e-8)

    return weights
