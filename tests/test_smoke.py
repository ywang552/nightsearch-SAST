import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import torch

from nightsearch_sast.config import load_config
from nightsearch_sast.data.dataset import SyntheticDictionarySpotDataset
from nightsearch_sast.data.real_data import build_reference_dictionary, load_real_experiment_data
from nightsearch_sast.evaluation.metrics import evaluate_predictions
from nightsearch_sast.models.cross_attention import CrossAttentionSpotAnnotator


def _write_real_npz_bundle(base_dir: Path) -> tuple[Path, Path, Path]:
    genes = np.array(["G0", "G1", "G2", "G3"], dtype=object)
    reference = np.array(
        [
            [2.0, 1.0, 0.5, 0.2],
            [1.8, 1.2, 0.6, 0.1],
            [0.3, 1.9, 2.0, 1.0],
            [0.2, 2.1, 1.8, 1.2],
        ],
        dtype=np.float32,
    )
    labels = np.array(["A", "A", "B", "B"], dtype=object)
    dictionary, _ = build_reference_dictionary(reference, labels)
    composition = np.array([[0.7, 0.3], [0.2, 0.8], [0.5, 0.5]], dtype=np.float32)
    spots = composition @ dictionary

    spots_path = base_dir / "spots.npz"
    ref_path = base_dir / "reference_cells.npz"
    target_path = base_dir / "spot_composition.npz"

    np.savez(spots_path, X=spots.astype(np.float32), gene_names=genes)
    np.savez(ref_path, X=reference, gene_names=genes, cell_types=labels)
    np.savez(target_path, Y=composition)
    return spots_path, ref_path, target_path


def test_placeholder_entrypoint_runs():
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "nightsearch_sast.main",
            "--config",
            str(repo_root / "configs" / "default.yaml"),
        ],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Status: scaffold run complete" in result.stdout


def test_cross_attention_forward_shapes():
    model = CrossAttentionSpotAnnotator(
        spot_dim=32,
        ref_dim=16,
        d_model=16,
        num_heads=4,
        dropout=0.1,
        num_cell_types=5,
    )
    spot = torch.rand(2, 32)
    reference = torch.rand(2, 5, 16)

    pred, attn = model(spot, reference)

    assert pred.shape == (2, 5)
    assert attn.shape[0] == 2


def test_synthetic_dictionary_dataset_shapes_and_simplex_targets():
    ds = SyntheticDictionarySpotDataset(
        num_samples=4,
        num_genes=32,
        num_cell_types=6,
        ref_dim=16,
        dirichlet_alpha=0.5,
        noise_std=0.01,
        seed=1,
    )
    item = ds[0]

    assert item.spot_features.shape == (32,)
    assert item.reference_embeddings.shape == (6, 16)
    assert item.target_composition.shape == (6,)
    assert torch.isclose(item.target_composition.sum(), torch.tensor(1.0), atol=1e-5)


def test_minimal_experiment_script_writes_metrics(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    output_file = tmp_path / "metrics.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_synthetic_baseline.py",
            "--config",
            str(repo_root / "configs" / "default.yaml"),
            "--output",
            str(output_file),
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["dataset"] == "synthetic_dictionary"
    assert "val_loss_mean" in payload["metrics"]


def test_config_loads_synthetic_section():
    repo_root = Path(__file__).resolve().parents[1]
    cfg = load_config(repo_root / "configs" / "default.yaml")
    assert cfg.data.synthetic.train_samples > 0
    assert cfg.data.real.min_shared_genes > 0


def test_build_reference_dictionary_groups_by_cell_type():
    reference = np.array([[1.0, 2.0], [3.0, 4.0], [10.0, 11.0]], dtype=np.float32)
    labels = np.array(["A", "A", "B"], dtype=object)
    dictionary, names = build_reference_dictionary(reference, labels)
    assert names == ["A", "B"]
    assert np.allclose(dictionary[0], np.array([2.0, 3.0], dtype=np.float32))


def test_real_pipeline_script_writes_metrics(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    spots_path, ref_path, target_path = _write_real_npz_bundle(tmp_path)
    cfg_path = tmp_path / "real.yaml"
    cfg_path.write_text(
        f"""project_name: test-real
seed: 1

data:
  dataset_name: real_npz
  num_genes: 4
  num_cell_types: 2
  spot_feature_dim: 4
  real:
    spots_npz_path: {spots_path}
    reference_npz_path: {ref_path}
    target_composition_npz_path: {target_path}
    train_fraction: 0.67
    min_shared_genes: 2

model:
  d_model: 16
  num_heads: 2
  num_layers: 1
  dropout: 0.1
  ref_hidden_dim: 16

train:
  epochs: 2
  batch_size: 2
  lr: 0.001
  weight_decay: 0.0
  device: cpu
""",
        encoding="utf-8",
    )
    output_file = tmp_path / "real_metrics.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_real_pipeline.py",
            "--config",
            str(cfg_path),
            "--output",
            str(output_file),
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert "cross_attention" in payload
    assert "nnls" in payload
    assert "reconstruction_mse" in payload["cross_attention"]


def test_unified_metrics_function_includes_supervised_metrics_when_target_exists():
    pred = torch.tensor([[0.6, 0.4], [0.2, 0.8]])
    ref = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    spot = pred @ ref
    target = pred.clone()
    metrics = evaluate_predictions(pred, ref, spot, target)
    assert metrics["reconstruction_mse"] < 1e-7
    assert "composition_mae" in metrics


def test_load_real_experiment_data_reads_npz_bundle(tmp_path: Path):
    spots_path, ref_path, target_path = _write_real_npz_bundle(tmp_path)
    cfg = load_config(Path(__file__).resolve().parents[1] / "configs" / "default.yaml")
    cfg.data.real.spots_npz_path = str(spots_path)
    cfg.data.real.reference_npz_path = str(ref_path)
    cfg.data.real.target_composition_npz_path = str(target_path)
    cfg.data.real.min_shared_genes = 2
    loaded = load_real_experiment_data(cfg.data.real)
    assert loaded.spot_matrix.shape[0] == 3
    assert loaded.reference_dictionary.shape[0] == 2
    assert loaded.target_composition is not None
