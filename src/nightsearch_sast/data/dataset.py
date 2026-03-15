"""Dataset interfaces for spatial transcriptomics spot annotation experiments."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch.utils.data import Dataset


@dataclass
class SpotBatch:
    spot_features: torch.Tensor
    reference_embeddings: torch.Tensor
    target_composition: torch.Tensor


class SpotAnnotationDataset(Dataset[SpotBatch]):
    """Placeholder dataset for spot annotation.

    Expected per-item tensors:
    - spot_features: [num_genes]
    - reference_embeddings: [num_cell_types, ref_dim]
    - target_composition: [num_cell_types]

    TODO: replace random fallback with loaders for Visium / Slide-seq / MERFISH derivatives.
    TODO: support sparse count matrices and optional spatial neighborhood features.
    """

    def __init__(
        self,
        num_samples: int,
        num_genes: int,
        num_cell_types: int,
        ref_dim: int,
    ) -> None:
        self.num_samples = num_samples
        self.num_genes = num_genes
        self.num_cell_types = num_cell_types
        self.ref_dim = ref_dim

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, index: int) -> SpotBatch:
        if index < 0 or index >= self.num_samples:
            raise IndexError(index)

        spot = torch.rand(self.num_genes)
        reference = torch.rand(self.num_cell_types, self.ref_dim)
        target = torch.softmax(torch.rand(self.num_cell_types), dim=0)
        return SpotBatch(
            spot_features=spot,
            reference_embeddings=reference,
            target_composition=target,
        )


def collate_spot_batches(batch: list[SpotBatch]) -> SpotBatch:
    return SpotBatch(
        spot_features=torch.stack([x.spot_features for x in batch], dim=0),
        reference_embeddings=torch.stack([x.reference_embeddings for x in batch], dim=0),
        target_composition=torch.stack([x.target_composition for x in batch], dim=0),
    )
