"""Configuration dataclasses for cross-attention spot annotation experiments."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SyntheticDataConfig:
    """Parameters for synthetic dictionary-driven baseline data generation."""

    train_samples: int = 256
    val_samples: int = 64
    dirichlet_alpha: float = 0.5
    noise_std: float = 0.05
    reference_scale: float = 1.0
    use_random_projection: bool = False


@dataclass
class RealDataConfig:
    """Parameters and file paths for real spatial transcriptomics experiments."""

    dataset_family: str = "dlpfc_visium"
    bundle_npz_path: str = ""
    spots_npz_path: str = "data/processed/real/spots.npz"
    reference_npz_path: str = "data/processed/real/reference_cells.npz"
    target_composition_npz_path: str = ""
    train_fraction: float = 0.8
    validation_fraction: float = 0.2
    min_shared_genes: int = 25


@dataclass
class DataConfig:
    dataset_name: str = "synthetic_dictionary"
    train_path: str = "data/train_placeholder.npz"
    val_path: str = "data/val_placeholder.npz"
    num_genes: int = 256
    num_cell_types: int = 20
    spot_feature_dim: int = 256
    synthetic: SyntheticDataConfig = field(default_factory=SyntheticDataConfig)
    real: RealDataConfig = field(default_factory=RealDataConfig)


@dataclass
class ModelConfig:
    d_model: int = 128
    num_heads: int = 4
    num_layers: int = 1
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
    """Load YAML into typed experiment config."""
    with Path(path).open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    raw_data = dict(raw.get("data", {}))
    synthetic = SyntheticDataConfig(**raw_data.pop("synthetic", {}))
    real = RealDataConfig(**raw_data.pop("real", {}))
    data = DataConfig(**raw_data, synthetic=synthetic, real=real)
    model = ModelConfig(**raw.get("model", {}))
    train = TrainConfig(**raw.get("train", {}))

    return ExperimentConfig(
        project_name=raw.get("project_name", "nightsearch-sast"),
        seed=raw.get("seed", 42),
        data=data,
        model=model,
        train=train,
    )
