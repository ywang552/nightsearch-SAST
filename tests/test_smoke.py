import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import torch

from nightsearch_sast.baselines.nnls import nnls_predict_composition, run_nnls_with_metrics
from nightsearch_sast.config import load_config
from nightsearch_sast.data.dataset import SyntheticDictionarySpotDataset
from nightsearch_sast.data.real_data import (
    build_reference_dictionary,
    load_real_data_bundle,
    load_real_experiment_data,
    match_reference_to_spots,
)
from nightsearch_sast.data.split import make_spot_split
from nightsearch_sast.evaluation.metrics import evaluate_predictions
from nightsearch_sast.models.cross_attention import CrossAttentionSpotAnnotator
from nightsearch_sast.training.train import run_cross_attention_with_metrics


def _write_real_npz_bundle(base_dir: Path) -> tuple[Path, Path, Path, Path]:
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

    spot_ids = np.array(["s0", "s1", "s2"], dtype=object)
    sample_ids = np.array(["151673", "151673", "151673"], dtype=object)
    regions = np.array(["L2", "L3", "WM"], dtype=object)

    spots_path = base_dir / "spots.npz"
    ref_path = base_dir / "reference_cells.npz"
    target_path = base_dir / "spot_composition.npz"
    bundle_path = base_dir / "bundle.npz"

    np.savez(spots_path, X=spots.astype(np.float32), gene_names=genes, spot_ids=spot_ids, sample_ids=sample_ids, region_labels=regions)
    np.savez(ref_path, X=reference, gene_names=genes, cell_types=labels)
    np.savez(target_path, Y=composition, cell_type_names=np.array(["A", "B"], dtype=object))
    np.savez(
        bundle_path,
        spot_matrix=spots.astype(np.float32),
        gene_names=genes,
        spot_ids=spot_ids,
        sample_ids=sample_ids,
        region_labels=regions,
        reference_matrix=reference,
        reference_gene_names=genes,
        reference_cell_types=labels,
        target_composition=composition,
        target_cell_type_names=np.array(["A", "B"], dtype=object),
    )
    return spots_path, ref_path, target_path, bundle_path


@pytest.mark.slow
def test_placeholder_entrypoint_runs():
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()

    result = subprocess.run(
        [sys.executable, "-m", "nightsearch_sast.main", "--config", str(repo_root / "configs" / "default.yaml")],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_cross_attention_forward_shapes():
    model = CrossAttentionSpotAnnotator(spot_dim=32, ref_dim=16, d_model=16, num_heads=4, dropout=0.1, num_cell_types=5)
    spot = torch.rand(2, 32)
    reference = torch.rand(2, 5, 16)
    pred, attn = model(spot, reference)
    assert pred.shape == (2, 5)
    assert attn.shape[0] == 2


def test_synthetic_dictionary_dataset_shapes_and_simplex_targets():
    ds = SyntheticDictionarySpotDataset(num_samples=4, num_genes=16, num_cell_types=6, ref_dim=16, dirichlet_alpha=0.5, noise_std=0.01, seed=1)
    item = ds[0]
    assert item.spot_features.shape == (16,)
    assert item.reference_embeddings.shape == (6, 16)
    assert torch.isclose(item.target_composition.sum(), torch.tensor(1.0), atol=1e-5)


def test_nnls_baseline_predicts_simplex_distribution():
    reference = torch.rand(2, 4, 8)
    true_mix = torch.softmax(torch.rand(2, 4), dim=-1)
    spots = torch.einsum("bc,bcg->bg", true_mix, reference)
    pred = nnls_predict_composition(spots, reference, num_steps=80)
    assert pred.shape == (2, 4)
    assert torch.allclose(pred.sum(dim=-1), torch.ones(2), atol=1e-4)


def test_split_is_deterministic():
    s1 = make_spot_split(num_spots=7, validation_fraction=0.3, seed=3)
    s2 = make_spot_split(num_spots=7, validation_fraction=0.3, seed=3)
    assert torch.equal(s1.train_indices, s2.train_indices)
    assert torch.equal(s1.validation_indices, s2.validation_indices)


def test_config_loads_synthetic_section():
    repo_root = Path(__file__).resolve().parents[1]
    cfg = load_config(repo_root / "configs" / "default.yaml")
    assert cfg.data.synthetic.train_samples > 0
    assert cfg.data.real.min_shared_genes > 0


def test_real_bundle_loader_and_matching(tmp_path: Path):
    spots_path, ref_path, target_path, bundle_path = _write_real_npz_bundle(tmp_path)
    cfg = load_config(Path(__file__).resolve().parents[1] / "configs" / "default.yaml")
    cfg.data.real.spots_npz_path = str(spots_path)
    cfg.data.real.reference_npz_path = str(ref_path)
    cfg.data.real.target_composition_npz_path = str(target_path)
    cfg.data.real.bundle_npz_path = ""
    cfg.data.real.min_shared_genes = 2
    bundle, aligned = load_real_experiment_data(cfg.data.real)
    assert bundle.sample_ids is not None
    assert aligned.reference_dictionary.shape == (2, 4)

    cfg.data.real.bundle_npz_path = str(bundle_path)
    bundle2 = load_real_data_bundle(cfg.data.real)
    aligned2 = match_reference_to_spots(bundle2, min_shared_genes=2)
    assert aligned2.matched_gene_count == 4


def test_unified_metrics_schema_handles_missing_labels():
    pred = torch.tensor([[0.6, 0.4], [0.2, 0.8]])
    ref = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    spot = pred @ ref
    metrics = evaluate_predictions("nnls", "validation", pred, ref, spot, None)
    assert metrics["composition_mae"] is None
    assert metrics["method"] == "nnls"


def test_nnls_and_cross_attention_real_style_paths(tmp_path: Path):
    spots_path, ref_path, target_path, _ = _write_real_npz_bundle(tmp_path)
    cfg = load_config(Path(__file__).resolve().parents[1] / "configs" / "default.yaml")
    cfg.data.real.spots_npz_path = str(spots_path)
    cfg.data.real.reference_npz_path = str(ref_path)
    cfg.data.real.target_composition_npz_path = str(target_path)
    cfg.data.real.min_shared_genes = 2
    cfg.train.epochs = 1
    cfg.train.batch_size = 2

    bundle, aligned = load_real_experiment_data(cfg.data.real)
    split = make_spot_split(num_spots=aligned.aligned_spot_matrix.shape[0], validation_fraction=0.34, seed=cfg.seed)

    _nnls_pred, nnls_metrics = run_nnls_with_metrics(
        spot_matrix=aligned.aligned_spot_matrix[split.validation_indices],
        reference_dictionary=aligned.reference_dictionary,
        split_name="validation",
        target_composition=bundle.target_composition[split.validation_indices],
    )
    _cross_pred, cross_metrics = run_cross_attention_with_metrics(
        config=cfg,
        spot_matrix=aligned.aligned_spot_matrix,
        reference_dictionary=aligned.reference_dictionary,
        target_composition=bundle.target_composition,
        split=split,
        supervised_target=bundle.target_composition,
    )
    assert nnls_metrics["reconstruction_mse"] >= 0
    assert cross_metrics["method"] == "cross_attention"


@pytest.mark.slow
def test_real_pipeline_script_writes_metrics(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    spots_path, ref_path, target_path, bundle_path = _write_real_npz_bundle(tmp_path)
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
    dataset_family: dlpfc_visium
    bundle_npz_path: {bundle_path}
    spots_npz_path: {spots_path}
    reference_npz_path: {ref_path}
    target_composition_npz_path: {target_path}
    validation_fraction: 0.34
    min_shared_genes: 2

model:
  d_model: 16
  num_heads: 2
  num_layers: 1
  dropout: 0.1
  ref_hidden_dim: 16

train:
  epochs: 1
  batch_size: 2
  lr: 0.001
  weight_decay: 0.0
  device: cpu
""",
        encoding="utf-8",
    )
    output_file = tmp_path / "real_metrics.json"
    result = subprocess.run(
        [sys.executable, "scripts/run_real_pipeline.py", "--config", str(cfg_path), "--output", str(output_file)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["dataset_family"] == "dlpfc_visium"
    assert payload["cross_attention"]["method"] == "cross_attention"


def test_real_pipeline_bundle_override_missing_path_has_clear_error(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    cfg_path = tmp_path / "real_missing.yaml"
    cfg_path.write_text(
        """project_name: test-real
seed: 1

data:
  dataset_name: real_npz
  num_genes: 4
  num_cell_types: 2
  spot_feature_dim: 4
  real:
    dataset_family: dlpfc_visium
    bundle_npz_path: data/processed/real/dlpfc_151673_bundle.npz
    validation_fraction: 0.2
    min_shared_genes: 2

model:
  d_model: 16
  num_heads: 2
  num_layers: 1
  dropout: 0.1
  ref_hidden_dim: 16

train:
  epochs: 1
  batch_size: 2
  lr: 0.001
  weight_decay: 0.0
  device: cpu
""",
        encoding="utf-8",
    )

    missing_bundle = tmp_path / "does_not_exist_bundle.npz"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_real_pipeline.py",
            "--config",
            str(cfg_path),
            "--bundle-npz-path",
            str(missing_bundle),
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Configured real bundle path was not found" in result.stderr
    assert "--bundle-npz-path" in result.stderr
