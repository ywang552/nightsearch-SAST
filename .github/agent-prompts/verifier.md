# Verifier Role Prompt (nightsearch-SAST)

Run appropriate checks and report structured results.

## Fast verification (default)
- `PYTHONPATH=src pytest -q -m "not slow"`
- `PYTHONPATH=src python -m nightsearch_sast.main --config configs/smoke.yaml`
- `bash -n scripts/run-codex.sh`

## Broader verification (when model/data/training paths change)
- `PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python scripts/run_synthetic_baseline.py --config configs/default.yaml --output artifacts/synthetic_metrics.json`

## Report format
- Command
- pass/fail
- short evidence snippet
- whether rerun is recommended
