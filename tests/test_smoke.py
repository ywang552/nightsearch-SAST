import json
import os
from pathlib import Path
import subprocess
import sys

import torch

from nightsearch_sast.baselines.nnls import nnls_predict_composition
from nightsearch_sast.config import load_config
from nightsearch_sast.data.dataset import SyntheticDictionarySpotDataset
from nightsearch_sast.models.cross_attention import CrossAttentionSpotAnnotator


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
        num_genes=16,
        num_cell_types=6,
        ref_dim=16,
        dirichlet_alpha=0.5,
        noise_std=0.01,
        seed=1,
    )
    item = ds[0]

    assert item.spot_features.shape == (16,)
    assert item.reference_embeddings.shape == (6, 16)
    assert item.target_composition.shape == (6,)
    assert torch.isclose(item.target_composition.sum(), torch.tensor(1.0), atol=1e-5)


def test_nnls_baseline_predicts_simplex_distribution():
    batch_size, cell_types, genes = 2, 4, 8
    reference = torch.rand(batch_size, cell_types, genes)
    true_mix = torch.softmax(torch.rand(batch_size, cell_types), dim=-1)
    spots = torch.einsum("bc,bcg->bg", true_mix, reference)

    pred = nnls_predict_composition(spots, reference, num_steps=80)
    assert pred.shape == (batch_size, cell_types)
    assert torch.all(pred >= 0)
    assert torch.allclose(pred.sum(dim=-1), torch.ones(batch_size), atol=1e-4)


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
    assert "nnls_val_loss_mean" in payload["metrics"]


def test_config_loads_synthetic_section():
    repo_root = Path(__file__).resolve().parents[1]
    cfg = load_config(repo_root / "configs" / "default.yaml")
    assert cfg.data.synthetic.train_samples > 0
    assert cfg.data.synthetic.use_random_projection is False
