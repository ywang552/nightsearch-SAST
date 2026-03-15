"""Real data loading and reference dictionary construction utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from nightsearch_sast.config import RealDataConfig


@dataclass
class RealExperimentData:
    spot_matrix: torch.Tensor
    reference_dictionary: torch.Tensor
    cell_type_names: list[str]
    shared_genes: list[str]
    target_composition: torch.Tensor | None


def _load_npz(path: str) -> dict[str, np.ndarray]:
    npz_path = Path(path)
    if not npz_path.exists():
        raise FileNotFoundError(f"Expected NPZ file at: {npz_path}")
    with np.load(npz_path, allow_pickle=True) as data:
        return {k: data[k] for k in data.files}


def _normalize_rows(x: torch.Tensor) -> torch.Tensor:
    return x / x.sum(dim=1, keepdim=True).clamp_min(1e-8)


def build_reference_dictionary(
    reference_expression: np.ndarray,
    cell_types: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    """Build cell-type dictionary by averaging single-cell expression per label."""
    labels = [str(x) for x in cell_types]
    unique = sorted(set(labels))
    means: list[np.ndarray] = []
    for cell_type in unique:
        idx = [i for i, label in enumerate(labels) if label == cell_type]
        means.append(reference_expression[idx].mean(axis=0))
    return np.stack(means, axis=0), unique


def load_real_experiment_data(cfg: RealDataConfig) -> RealExperimentData:
    spot_payload = _load_npz(cfg.spots_npz_path)
    ref_payload = _load_npz(cfg.reference_npz_path)

    spot_expr = np.asarray(spot_payload["X"], dtype=np.float32)
    spot_genes = [str(g) for g in spot_payload["gene_names"]]

    reference_expr = np.asarray(ref_payload["X"], dtype=np.float32)
    reference_genes = [str(g) for g in ref_payload["gene_names"]]
    reference_cell_types = np.asarray(ref_payload["cell_types"])

    shared = sorted(set(spot_genes).intersection(reference_genes))
    if len(shared) < cfg.min_shared_genes:
        raise ValueError(
            f"Insufficient shared genes between spot and reference matrices: {len(shared)} < {cfg.min_shared_genes}"
        )

    spot_index = {g: i for i, g in enumerate(spot_genes)}
    ref_index = {g: i for i, g in enumerate(reference_genes)}
    spot_cols = [spot_index[g] for g in shared]
    ref_cols = [ref_index[g] for g in shared]

    spot_aligned = spot_expr[:, spot_cols]
    ref_aligned = reference_expr[:, ref_cols]

    reference_dictionary, cell_type_names = build_reference_dictionary(
        reference_expression=ref_aligned,
        cell_types=reference_cell_types,
    )

    target_composition: torch.Tensor | None = None
    if cfg.target_composition_npz_path:
        target_payload = _load_npz(cfg.target_composition_npz_path)
        target = torch.tensor(np.asarray(target_payload["Y"], dtype=np.float32))
        target_composition = _normalize_rows(target)

    return RealExperimentData(
        spot_matrix=torch.tensor(spot_aligned, dtype=torch.float32),
        reference_dictionary=torch.tensor(reference_dictionary, dtype=torch.float32),
        cell_type_names=cell_type_names,
        shared_genes=shared,
        target_composition=target_composition,
    )
