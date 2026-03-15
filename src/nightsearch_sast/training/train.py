"""Training scaffold for cross-attention spot annotation model."""

from __future__ import annotations

import random

import numpy as np
import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader

from nightsearch_sast.baselines.nnls import nnls_predict_composition
from nightsearch_sast.config import ExperimentConfig
from nightsearch_sast.data.dataset import (
    SpotBatch,
    SyntheticDictionarySpotDataset,
    collate_spot_batches,
)
from nightsearch_sast.models.cross_attention import CrossAttentionSpotAnnotator


class TensorSpotDataset(torch.utils.data.Dataset):
    """Dataset wrapping in-memory tensors for real or synthetic experiments."""

    def __init__(
        self,
        spot_matrix: torch.Tensor,
        reference_dictionary: torch.Tensor,
        target_composition: torch.Tensor,
    ) -> None:
        self.spot_matrix = spot_matrix
        self.reference_dictionary = reference_dictionary
        self.target_composition = target_composition

    def __len__(self) -> int:
        return self.spot_matrix.shape[0]

    def __getitem__(self, index: int) -> SpotBatch:
        return SpotBatch(
            spot_features=self.spot_matrix[index],
            reference_embeddings=self.reference_dictionary,
            target_composition=self.target_composition[index],
        )


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


class CompositionKLLoss(nn.Module):
    """KL divergence loss over composition distributions."""

    def __init__(self) -> None:
        super().__init__()
        self.kl = nn.KLDivLoss(reduction="batchmean")

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return self.kl(torch.log(pred.clamp_min(1e-8)), target)


def build_model(config: ExperimentConfig) -> CrossAttentionSpotAnnotator:
    return CrossAttentionSpotAnnotator(
        spot_dim=config.data.spot_feature_dim,
        ref_dim=config.model.ref_hidden_dim,
        d_model=config.model.d_model,
        num_heads=config.model.num_heads,
        dropout=config.model.dropout,
        num_cell_types=config.data.num_cell_types,
    )


def make_dataloaders(config: ExperimentConfig) -> tuple[DataLoader, DataLoader]:
    synth = config.data.synthetic
    train_ds = SyntheticDictionarySpotDataset(
        num_samples=synth.train_samples,
        num_genes=config.data.spot_feature_dim,
        num_cell_types=config.data.num_cell_types,
        ref_dim=config.model.ref_hidden_dim,
        dirichlet_alpha=synth.dirichlet_alpha,
        noise_std=synth.noise_std,
        reference_scale=synth.reference_scale,
        use_random_projection=synth.use_random_projection,
        seed=config.seed,
    )
    val_ds = SyntheticDictionarySpotDataset(
        num_samples=synth.val_samples,
        num_genes=config.data.spot_feature_dim,
        num_cell_types=config.data.num_cell_types,
        ref_dim=config.model.ref_hidden_dim,
        dirichlet_alpha=synth.dirichlet_alpha,
        noise_std=synth.noise_std,
        reference_scale=synth.reference_scale,
        use_random_projection=synth.use_random_projection,
        seed=config.seed + 1,
    )

    train_loader = DataLoader(train_ds, batch_size=config.train.batch_size, shuffle=True, collate_fn=collate_spot_batches)
    val_loader = DataLoader(val_ds, batch_size=config.train.batch_size, shuffle=False, collate_fn=collate_spot_batches)
    return train_loader, val_loader


def evaluate(model: nn.Module, loader: DataLoader, criterion: nn.Module, device: torch.device) -> float:
    model.eval()
    total = 0.0
    with torch.no_grad():
        for batch in loader:
            spot = batch.spot_features.to(device)
            ref = batch.reference_embeddings.to(device)
            target = batch.target_composition.to(device)
            pred, _attn = model(spot, ref)
            total += float(criterion(pred, target).item())
    return total / max(len(loader), 1)


def evaluate_nnls_baseline(loader: DataLoader, criterion: nn.Module, device: torch.device) -> float:
    total = 0.0
    for batch in loader:
        spot = batch.spot_features.to(device)
        ref = batch.reference_embeddings.to(device)
        target = batch.target_composition.to(device)
        pred = nnls_predict_composition(spot, ref)
        total += float(criterion(pred, target).item())
    return total / max(len(loader), 1)


def train(config: ExperimentConfig) -> dict[str, float]:
    set_seed(config.seed)
    device = torch.device(config.train.device)

    model = build_model(config).to(device)
    train_loader, val_loader = make_dataloaders(config)
    criterion = CompositionKLLoss()
    optimizer = AdamW(model.parameters(), lr=config.train.lr, weight_decay=config.train.weight_decay)

    train_loss = 0.0
    for _epoch in range(config.train.epochs):
        model.train()
        for batch in train_loader:
            spot = batch.spot_features.to(device)
            ref = batch.reference_embeddings.to(device)
            target = batch.target_composition.to(device)

            pred, _attn = model(spot, ref)
            loss = criterion(pred, target)

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            train_loss = float(loss.item())

    val_loss = evaluate(model, val_loader, criterion, device)
    nnls_val_loss = evaluate_nnls_baseline(val_loader, criterion, device)
    return {
        "train_loss_last": train_loss,
        "val_loss_mean": val_loss,
        "nnls_val_loss_mean": nnls_val_loss,
    }


def train_cross_attention_from_tensors(
    config: ExperimentConfig,
    spot_matrix: torch.Tensor,
    reference_dictionary: torch.Tensor,
    target_composition: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Train cross-attention model from in-memory tensors and return predictions."""
    set_seed(config.seed)
    device = torch.device(config.train.device)

    n_spots = spot_matrix.shape[0]
    n_train = max(1, int(n_spots * config.data.real.train_fraction))
    indices = torch.randperm(n_spots)
    train_idx, val_idx = indices[:n_train], indices[n_train:]
    if val_idx.numel() == 0:
        val_idx = train_idx

    model = CrossAttentionSpotAnnotator(
        spot_dim=spot_matrix.shape[1],
        ref_dim=reference_dictionary.shape[1],
        d_model=config.model.d_model,
        num_heads=config.model.num_heads,
        dropout=config.model.dropout,
        num_cell_types=reference_dictionary.shape[0],
    ).to(device)

    criterion = CompositionKLLoss()
    optimizer = AdamW(model.parameters(), lr=config.train.lr, weight_decay=config.train.weight_decay)

    train_ds = TensorSpotDataset(spot_matrix[train_idx], reference_dictionary, target_composition[train_idx])
    val_ds = TensorSpotDataset(spot_matrix[val_idx], reference_dictionary, target_composition[val_idx])
    train_loader = DataLoader(train_ds, batch_size=config.train.batch_size, shuffle=True, collate_fn=collate_spot_batches)
    val_loader = DataLoader(val_ds, batch_size=config.train.batch_size, shuffle=False, collate_fn=collate_spot_batches)

    train_loss = 0.0
    for _ in range(config.train.epochs):
        model.train()
        for batch in train_loader:
            spot = batch.spot_features.to(device)
            ref = batch.reference_embeddings.to(device)
            target = batch.target_composition.to(device)
            pred, _ = model(spot, ref)
            loss = criterion(pred, target)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            train_loss = float(loss.item())

    val_loss = evaluate(model, val_loader, criterion, device)
    model.eval()
    with torch.no_grad():
        ref = reference_dictionary.unsqueeze(0).expand(n_spots, -1, -1).to(device)
        pred, _ = model(spot_matrix.to(device), ref)

    return pred.cpu(), {"train_loss_last": train_loss, "val_loss_mean": val_loss}
