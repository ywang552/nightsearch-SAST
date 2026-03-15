"""Cross-attention model skeleton for spot-to-reference cell type composition prediction."""

from __future__ import annotations

import torch
from torch import nn


class SpotEncoder(nn.Module):
    """Encode observed spot features into query embeddings."""

    def __init__(self, input_dim: int, d_model: int, dropout: float) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, d_model),
        )

    def forward(self, spot_features: torch.Tensor) -> torch.Tensor:
        return self.net(spot_features)


class ReferenceEncoder(nn.Module):
    """Project reference dictionary embeddings into key/value space."""

    def __init__(self, ref_dim: int, d_model: int, dropout: float) -> None:
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(ref_dim, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, d_model),
        )

    def forward(self, reference_embeddings: torch.Tensor) -> torch.Tensor:
        return self.proj(reference_embeddings)


class SpotReferenceCrossAttention(nn.Module):
    """Cross-attention block where spot query attends to reference keys/values."""

    def __init__(self, d_model: int, num_heads: int, dropout: float) -> None:
        super().__init__()
        self.attn = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        query: torch.Tensor,
        key_value: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        attended, attn_weights = self.attn(query, key_value, key_value)
        return self.norm(query + attended), attn_weights


class CellTypeDistributionHead(nn.Module):
    """Map attended query features to cell-type logits/distribution."""

    def __init__(self, d_model: int, num_cell_types: int) -> None:
        super().__init__()
        self.out = nn.Linear(d_model, num_cell_types)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        logits = self.out(features)
        return torch.softmax(logits, dim=-1)


class CrossAttentionSpotAnnotator(nn.Module):
    """End-to-end scaffold model for spot annotation.

    Query: encoded spot features.
    Key/Value: encoded cell-type reference dictionary entries.
    Output: predicted per-spot cell type composition distribution.
    """

    def __init__(
        self,
        spot_dim: int,
        ref_dim: int,
        d_model: int,
        num_heads: int,
        dropout: float,
        num_cell_types: int,
    ) -> None:
        super().__init__()
        self.spot_encoder = SpotEncoder(spot_dim, d_model, dropout)
        self.reference_encoder = ReferenceEncoder(ref_dim, d_model, dropout)
        self.cross_attention = SpotReferenceCrossAttention(d_model, num_heads, dropout)
        self.head = CellTypeDistributionHead(d_model, num_cell_types)

    def forward(
        self,
        spot_features: torch.Tensor,
        reference_embeddings: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        spot_q = self.spot_encoder(spot_features).unsqueeze(1)
        ref_kv = self.reference_encoder(reference_embeddings)

        attended, attn_weights = self.cross_attention(spot_q, ref_kv)
        composition = self.head(attended).squeeze(1)
        return composition, attn_weights
