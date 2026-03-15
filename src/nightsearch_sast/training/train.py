"""Training loop skeleton for cross-attention spot annotation model."""

from __future__ import annotations

import random

import numpy as np
import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader

from nightsearch_sast.config import ExperimentConfig
from nightsearch_sast.data.dataset import SpotAnnotationDataset, collate_spot_batches
from nightsearch_sast.models.cross_attention import CrossAttentionSpotAnnotator


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
        # TODO: compare with alternatives (MSE, cross entropy on pseudo-labels, OT losses).
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
    train_ds = SpotAnnotationDataset(
        num_samples=64,
        num_genes=config.data.spot_feature_dim,
        num_cell_types=config.data.num_cell_types,
        ref_dim=config.model.ref_hidden_dim,
    )
    val_ds = SpotAnnotationDataset(
        num_samples=16,
        num_genes=config.data.spot_feature_dim,
        num_cell_types=config.data.num_cell_types,
        ref_dim=config.model.ref_hidden_dim,
    )

    train_loader = DataLoader(
        train_ds,
        batch_size=config.train.batch_size,
        shuffle=True,
        collate_fn=collate_spot_batches,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=config.train.batch_size,
        shuffle=False,
        collate_fn=collate_spot_batches,
    )
    return train_loader, val_loader


def train(config: ExperimentConfig) -> dict[str, float]:
    set_seed(config.seed)
    device = torch.device(config.train.device)

    model = build_model(config).to(device)
    train_loader, val_loader = make_dataloaders(config)
    criterion = CompositionKLLoss()
    optimizer = AdamW(
        model.parameters(),
        lr=config.train.lr,
        weight_decay=config.train.weight_decay,
    )

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

    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for batch in val_loader:
            spot = batch.spot_features.to(device)
            ref = batch.reference_embeddings.to(device)
            target = batch.target_composition.to(device)
            pred, _attn = model(spot, ref)
            val_loss += float(criterion(pred, target).item())

    val_loss /= max(len(val_loader), 1)
    return {"train_loss_last": train_loss, "val_loss_mean": val_loss}
