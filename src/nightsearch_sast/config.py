"""Configuration dataclasses for cross-attention spot annotation experiments."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DataConfig:
    dataset_name: str = "placeholder"
    train_path: str = "data/train_placeholder.npz"
    val_path: str = "data/val_placeholder.npz"
    num_genes: int = 2000
    num_cell_types: int = 20
    spot_feature_dim: int = 2000


@dataclass
class ModelConfig:
    d_model: int = 256
    num_heads: int = 8
    num_layers: int = 2
    dropout: float = 0.1
    ref_hidden_dim: int = 256


@dataclass
class TrainConfig:
    epochs: int = 5
    batch_size: int = 8
    lr: float = 1e-4
    weight_decay: float = 1e-4
    device: str = "cpu"


@dataclass
class ExperimentConfig:
    project_name: str = "nightsearch-sast"
    seed: int = 42
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)



def load_config(path: str | Path) -> ExperimentConfig:
    """Load YAML into typed experiment config.

    TODO: add stricter schema validation (e.g., pydantic) when configs stabilize.
    """
    with Path(path).open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    data = DataConfig(**raw.get("data", {}))
    model = ModelConfig(**raw.get("model", {}))
    train = TrainConfig(**raw.get("train", {}))

    return ExperimentConfig(
        project_name=raw.get("project_name", "nightsearch-sast"),
        seed=raw.get("seed", 42),
        data=data,
        model=model,
        train=train,
    )
