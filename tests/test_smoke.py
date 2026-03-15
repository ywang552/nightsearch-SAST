import os
from pathlib import Path
import subprocess
import sys

import torch

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
