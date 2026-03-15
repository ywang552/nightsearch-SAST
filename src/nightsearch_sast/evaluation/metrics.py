"""Unified metrics for composition and reconstruction quality."""

from __future__ import annotations

import torch


def evaluate_predictions(
    predicted_composition: torch.Tensor,
    reference_dictionary: torch.Tensor,
    spot_matrix: torch.Tensor,
    target_composition: torch.Tensor | None = None,
) -> dict[str, float]:
    recon = predicted_composition @ reference_dictionary
    mse = torch.mean((recon - spot_matrix) ** 2).item()

    metrics: dict[str, float] = {
        "reconstruction_mse": float(mse),
    }

    if target_composition is not None:
        target = target_composition
        mae = torch.mean(torch.abs(predicted_composition - target)).item()
        kl = torch.sum(
            target * (torch.log(target.clamp_min(1e-8)) - torch.log(predicted_composition.clamp_min(1e-8))),
            dim=1,
        ).mean().item()
        metrics["composition_mae"] = float(mae)
        metrics["composition_kl"] = float(kl)

    return metrics
