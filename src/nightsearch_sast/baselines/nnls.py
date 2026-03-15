"""Simple non-negative least squares baseline solved with projected gradient descent."""

from __future__ import annotations

import torch


def _project_to_simplex(v: torch.Tensor) -> torch.Tensor:
    """Project vectors onto the probability simplex along the last dimension."""
    sorted_v, _ = torch.sort(v, descending=True, dim=-1)
    cssv = torch.cumsum(sorted_v, dim=-1) - 1
    rho = torch.arange(1, v.shape[-1] + 1, device=v.device, dtype=v.dtype)
    cond = sorted_v - (cssv / rho) > 0
    rho_idx = cond.sum(dim=-1, keepdim=True).clamp_min(1)
    theta = cssv.gather(-1, rho_idx - 1) / rho_idx
    return torch.clamp(v - theta, min=0.0)


def nnls_predict_composition(
    spot_features: torch.Tensor,
    reference_embeddings: torch.Tensor,
    num_steps: int = 150,
    lr: float = 5e-2,
) -> torch.Tensor:
    """Estimate per-spot composition by projected gradient descent.

    Args:
        spot_features: [batch, genes]
        reference_embeddings: [batch, cell_types, genes]
        num_steps: optimization steps for each batch element.
        lr: gradient step size.

    Returns:
        Tensor of shape [batch, cell_types] constrained to simplex.
    """
    if spot_features.dim() != 2 or reference_embeddings.dim() != 3:
        raise ValueError("Expected spot_features [B,G] and reference_embeddings [B,C,G].")

    batch_size, num_cell_types, genes = reference_embeddings.shape
    if spot_features.shape[0] != batch_size or spot_features.shape[1] != genes:
        raise ValueError("Reference and spot dimensions must match.")

    comp = torch.full(
        (batch_size, num_cell_types),
        fill_value=1.0 / num_cell_types,
        dtype=spot_features.dtype,
        device=spot_features.device,
        requires_grad=True,
    )

    for _ in range(num_steps):
        recon = torch.einsum("bc,bcg->bg", comp, reference_embeddings)
        loss = ((recon - spot_features) ** 2).mean()
        (grad,) = torch.autograd.grad(loss, comp, create_graph=False)
        with torch.no_grad():
            comp -= lr * grad
            comp.copy_(_project_to_simplex(comp))

    return comp.detach()
