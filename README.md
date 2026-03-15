# nightsearch-SAST

`nightsearch-SAST` is a Python research repository for future work on spatial transcriptomics spot annotation. The repository is intentionally minimal today: it provides a clean project layout, a small runnable placeholder, and a Codex-friendly cloud scaffold so later sessions can install dependencies, understand the structure, and start adding research code without repo cleanup first.

The actual spot annotation method is not implemented yet. This baseline is only for environment setup, project organization, and future cloud execution.

## Repository Overview

The repository is organized to support research code, configs, notebooks, and tests without committing to a specific modeling pipeline yet.

- `src/nightsearch_sast/`: Python package for future research modules
- `configs/`: experiment and runtime configuration files
- `scripts/`: helper scripts, including the Codex cloud entrypoint
- `notebooks/`: exploratory notebooks
- `tests/`: smoke tests and future unit tests
- `data/`: local-only data placement guidance

## Environment Setup

The intended baseline for new environments is Python 3.11.

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Getting Started

Run the placeholder entrypoint from the repository root:

```bash
python -m nightsearch_sast.main --config configs/default.yaml
```

Run the smoke tests:

```bash
pytest -q
```

Future Codex cloud sessions should start with:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m nightsearch_sast.main --config configs/default.yaml
```

## Codex Cloud Usage

The repository keeps a minimal Docker plus GitHub Actions scaffold so Codex can be run against this repo from the cloud later.

- `Dockerfile` builds a Python-capable Codex runtime image.
- `scripts/run-codex.sh` validates runtime inputs and launches the Codex CLI from the repository root.
- `.github/workflows/validate.yml` checks the Python scaffold and container build path.
- `.github/workflows/codex-run.yml` provides a manual GitHub Actions entrypoint for Codex tasks.

For local dry-run testing of the container entrypoint:

```bash
docker build -t codex-cloud-repo .
docker run --rm \
  -e CODEX_DRY_RUN=1 \
  -e CODEX_TASK="Inspect the repository and summarize the Python research scaffold." \
  -v "$PWD:/workspace" \
  codex-cloud-repo
```

For a real cloud or local container run, set `OPENAI_API_KEY` and provide a task string.

## Planned Work

This repository will later be used for:

- spatial transcriptomics spot annotation
- cross attention based modeling
- dictionary guided prediction
- research experiments

## Notes For Future Coding Sessions

- Use `src/nightsearch_sast/` for importable Python modules.
- Prefer configs under `configs/` instead of hardcoded parameters.
- Keep exploratory work in `notebooks/`, but move reusable logic into `src/`.
- Treat `data/` contents as local outputs unless explicitly documented otherwise.
