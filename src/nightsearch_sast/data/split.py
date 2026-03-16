"""Deterministic spot-level train/validation splitting utilities."""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class DataSplit:
    train_indices: torch.Tensor
    validation_indices: torch.Tensor
    seed: int
    validation_fraction: float


def make_spot_split(num_spots: int, validation_fraction: float, seed: int) -> DataSplit:
    """Create deterministic train/validation split indices for spot-only data."""
    if num_spots < 1:
        raise ValueError("num_spots must be positive")
    if not (0.0 <= validation_fraction < 1.0):
        raise ValueError("validation_fraction must be in [0,1)")

    generator = torch.Generator().manual_seed(seed)
    indices = torch.randperm(num_spots, generator=generator)
    n_val = int(round(num_spots * validation_fraction))
    n_val = min(max(n_val, 1), num_spots - 1) if num_spots > 1 else 0

    val_idx = indices[:n_val]
    train_idx = indices[n_val:]
    if train_idx.numel() == 0:
        train_idx = val_idx
    if val_idx.numel() == 0:
        val_idx = train_idx

    return DataSplit(
        train_indices=train_idx,
        validation_indices=val_idx,
        seed=seed,
        validation_fraction=validation_fraction,
    )
