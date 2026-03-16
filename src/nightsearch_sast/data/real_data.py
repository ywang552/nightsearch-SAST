"""Real data bundle loading and gene-matching utilities for Visium-style experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from nightsearch_sast.config import RealDataConfig


@dataclass
class RealDataBundle:
    """Normalized on-disk real data bundle.

    The bundle is method-agnostic and is the shared contract for NNLS and cross-attention.
    """

    spot_matrix: torch.Tensor
    gene_names: list[str]
    spot_ids: list[str]
    sample_ids: list[str] | None
    region_labels: list[str] | None
    reference_matrix: torch.Tensor
    reference_gene_names: list[str]
    reference_cell_types: list[str]
    target_composition: torch.Tensor | None
    target_cell_type_names: list[str] | None


@dataclass
class AlignedReferenceData:
    aligned_spot_matrix: torch.Tensor
    reference_dictionary: torch.Tensor
    cell_type_names: list[str]
    matched_gene_names: list[str]
    matched_gene_count: int


def _load_npz(path: str) -> dict[str, np.ndarray]:
    npz_path = Path(path)
    if not npz_path.exists():
        raise FileNotFoundError(f"Expected NPZ file at: {npz_path}")
    with np.load(npz_path, allow_pickle=True) as data:
        return {k: data[k] for k in data.files}


def _as_string_list(values: np.ndarray) -> list[str]:
    return [str(v) for v in values]


def _normalize_rows(x: torch.Tensor) -> torch.Tensor:
    return x / x.sum(dim=1, keepdim=True).clamp_min(1e-8)


def _get_optional_strings(payload: dict[str, np.ndarray], key: str) -> list[str] | None:
    if key not in payload:
        return None
    return _as_string_list(np.asarray(payload[key]))


def build_reference_dictionary(
    reference_expression: np.ndarray,
    cell_types: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    """Build a cell-type dictionary by averaging expression per cell type label."""
    labels = [str(x) for x in cell_types]
    unique = sorted(set(labels))
    means: list[np.ndarray] = []
    for cell_type in unique:
        idx = [i for i, label in enumerate(labels) if label == cell_type]
        means.append(reference_expression[idx].mean(axis=0))
    return np.stack(means, axis=0), unique


def load_real_data_bundle(cfg: RealDataConfig) -> RealDataBundle:
    """Load normalized real-data bundle from split NPZs or a unified bundle NPZ."""
    if cfg.bundle_npz_path:
        payload = _load_npz(cfg.bundle_npz_path)
        spot_matrix = torch.tensor(np.asarray(payload["spot_matrix"], dtype=np.float32))
        reference_matrix = torch.tensor(np.asarray(payload["reference_matrix"], dtype=np.float32))
        target_composition = None
        if "target_composition" in payload:
            target_composition = _normalize_rows(
                torch.tensor(np.asarray(payload["target_composition"], dtype=np.float32))
            )
        target_cell_type_names = _get_optional_strings(payload, "target_cell_type_names")

        return RealDataBundle(
            spot_matrix=spot_matrix,
            gene_names=_as_string_list(np.asarray(payload["gene_names"])),
            spot_ids=_as_string_list(np.asarray(payload["spot_ids"])),
            sample_ids=_get_optional_strings(payload, "sample_ids"),
            region_labels=_get_optional_strings(payload, "region_labels"),
            reference_matrix=reference_matrix,
            reference_gene_names=_as_string_list(np.asarray(payload["reference_gene_names"])),
            reference_cell_types=_as_string_list(np.asarray(payload["reference_cell_types"])),
            target_composition=target_composition,
            target_cell_type_names=target_cell_type_names,
        )

    spot_payload = _load_npz(cfg.spots_npz_path)
    ref_payload = _load_npz(cfg.reference_npz_path)

    spot_expr = np.asarray(spot_payload["X"], dtype=np.float32)
    spot_genes = _as_string_list(np.asarray(spot_payload["gene_names"]))
    if "spot_ids" in spot_payload:
        spot_ids = _as_string_list(np.asarray(spot_payload["spot_ids"]))
    else:
        spot_ids = [f"spot_{idx:05d}" for idx in range(spot_expr.shape[0])]

    reference_expr = np.asarray(ref_payload["X"], dtype=np.float32)
    reference_genes = _as_string_list(np.asarray(ref_payload["gene_names"]))
    reference_cell_types = _as_string_list(np.asarray(ref_payload["cell_types"]))

    target_composition: torch.Tensor | None = None
    target_cell_type_names: list[str] | None = None
    if cfg.target_composition_npz_path:
        target_payload = _load_npz(cfg.target_composition_npz_path)
        target = torch.tensor(np.asarray(target_payload["Y"], dtype=np.float32))
        target_composition = _normalize_rows(target)
        target_cell_type_names = _get_optional_strings(target_payload, "cell_type_names")

    return RealDataBundle(
        spot_matrix=torch.tensor(spot_expr, dtype=torch.float32),
        gene_names=spot_genes,
        spot_ids=spot_ids,
        sample_ids=_get_optional_strings(spot_payload, "sample_ids"),
        region_labels=_get_optional_strings(spot_payload, "region_labels"),
        reference_matrix=torch.tensor(reference_expr, dtype=torch.float32),
        reference_gene_names=reference_genes,
        reference_cell_types=reference_cell_types,
        target_composition=target_composition,
        target_cell_type_names=target_cell_type_names,
    )


def match_reference_to_spots(bundle: RealDataBundle, min_shared_genes: int) -> AlignedReferenceData:
    """Match genes and build aligned spot matrix + cell type dictionary over shared genes."""
    shared = sorted(set(bundle.gene_names).intersection(bundle.reference_gene_names))
    if len(shared) < min_shared_genes:
        raise ValueError(
            f"Insufficient shared genes between spot and reference matrices: {len(shared)} < {min_shared_genes}"
        )

    spot_index = {g: i for i, g in enumerate(bundle.gene_names)}
    ref_index = {g: i for i, g in enumerate(bundle.reference_gene_names)}
    spot_cols = [spot_index[g] for g in shared]
    ref_cols = [ref_index[g] for g in shared]

    spot_aligned = bundle.spot_matrix[:, spot_cols].cpu().numpy()
    ref_aligned = bundle.reference_matrix[:, ref_cols].cpu().numpy()

    reference_dictionary, cell_type_names = build_reference_dictionary(
        reference_expression=ref_aligned,
        cell_types=np.asarray(bundle.reference_cell_types, dtype=object),
    )

    return AlignedReferenceData(
        aligned_spot_matrix=torch.tensor(spot_aligned, dtype=torch.float32),
        reference_dictionary=torch.tensor(reference_dictionary, dtype=torch.float32),
        cell_type_names=cell_type_names,
        matched_gene_names=shared,
        matched_gene_count=len(shared),
    )


def load_real_experiment_data(cfg: RealDataConfig) -> tuple[RealDataBundle, AlignedReferenceData]:
    """Convenience loader that returns both normalized and aligned real-data structures."""
    bundle = load_real_data_bundle(cfg)
    aligned = match_reference_to_spots(bundle, min_shared_genes=cfg.min_shared_genes)
    return bundle, aligned
