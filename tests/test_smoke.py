import os
from pathlib import Path
import subprocess
import sys


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
    assert "scaffold ready for future research code" in result.stdout
