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


class SyntheticDictionarySpotDataset(Dataset[SpotBatch]):
    """Synthetic spot dataset with a fixed cell-type reference dictionary.

    The per-spot composition is sampled from a Dirichlet distribution and mixed through
    the reference dictionary to produce spot-level expression features.

    Shapes:
    - reference_dictionary: [num_cell_types, ref_dim]
    - spot_features: [num_genes]
    - target_composition: [num_cell_types]
    """

    def __init__(
        self,
        num_samples: int,
        num_genes: int,
        num_cell_types: int,
        ref_dim: int,
        dirichlet_alpha: float,
        noise_std: float,
        reference_scale: float = 1.0,
        seed: int = 42,
    ) -> None:
        self.num_samples = num_samples
        self.num_genes = num_genes
        self.num_cell_types = num_cell_types
        self.ref_dim = ref_dim
        self.noise_std = noise_std

        generator = torch.Generator().manual_seed(seed)
        self.reference_dictionary = torch.rand(
            num_cell_types,
            ref_dim,
            generator=generator,
        ) * reference_scale

        concentration = torch.full(
            (num_cell_types,),
            fill_value=max(dirichlet_alpha, 1e-3),
        )
        dirichlet = torch.distributions.Dirichlet(concentration)

        compositions = dirichlet.sample((num_samples,))
        projected_reference = self.reference_dictionary
        if ref_dim != num_genes:
            projector = torch.rand(ref_dim, num_genes, generator=generator)
            projected_reference = projected_reference @ projector

        clean_spots = compositions @ projected_reference
        noise = torch.randn(num_samples, num_genes, generator=generator) * noise_std
        self.spot_matrix = (clean_spots + noise).clamp_min(0.0)
        self.targets = compositions

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, index: int) -> SpotBatch:
        if index < 0 or index >= self.num_samples:
            raise IndexError(index)

        return SpotBatch(
            spot_features=self.spot_matrix[index],
            reference_embeddings=self.reference_dictionary,
            target_composition=self.targets[index],
        )


def collate_spot_batches(batch: list[SpotBatch]) -> SpotBatch:
    return SpotBatch(
        spot_features=torch.stack([x.spot_features for x in batch], dim=0),
        reference_embeddings=torch.stack([x.reference_embeddings for x in batch], dim=0),
        target_composition=torch.stack([x.target_composition for x in batch], dim=0),
    )
