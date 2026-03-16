"""Unified metrics for composition and reconstruction quality."""

from __future__ import annotations

from typing import Any

import torch


def _none_if_nan(value: float) -> float | None:
    return None if value != value else float(value)


def evaluate_predictions(
    method: str,
    split: str,
    predicted_composition: torch.Tensor,
    reference_dictionary: torch.Tensor,
    spot_matrix: torch.Tensor,
    target_composition: torch.Tensor | None = None,
) -> dict[str, Any]:
    """Evaluate predictions under one consistent schema across methods."""
    recon = predicted_composition @ reference_dictionary
    mse = torch.mean((recon - spot_matrix) ** 2).item()

    composition_mae: float | None = None
    composition_kl: float | None = None
    if target_composition is not None:
        target = target_composition
        composition_mae = torch.mean(torch.abs(predicted_composition - target)).item()
        composition_kl = (
            torch.sum(
                target
                * (
                    torch.log(target.clamp_min(1e-8))
                    - torch.log(predicted_composition.clamp_min(1e-8))
                ),
                dim=1,
            )
            .mean()
            .item()
        )

    return {
        "method": method,
        "split": split,
        "reconstruction_mse": float(mse),
        "composition_mae": _none_if_nan(composition_mae) if composition_mae is not None else None,
        "composition_kl": _none_if_nan(composition_kl) if composition_kl is not None else None,
    }
