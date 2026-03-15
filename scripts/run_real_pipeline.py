"""Run a real-data path experiment with cross-attention and NNLS baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


from nightsearch_sast.baselines.nnls import run_nnls_baseline
from nightsearch_sast.config import load_config
from nightsearch_sast.data.real_data import load_real_experiment_data
from nightsearch_sast.evaluation.metrics import evaluate_predictions
from nightsearch_sast.training.train import train_cross_attention_from_tensors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run real data pipeline (cross-attention + NNLS).")
    parser.add_argument("--config", default="configs/real_example.yaml")
    parser.add_argument("--output", default="artifacts/real_pipeline_metrics.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config(args.config)

    if cfg.data.dataset_name != "real_npz":
        raise ValueError("Real pipeline requires data.dataset_name=real_npz")

    loaded = load_real_experiment_data(cfg.data.real)
    spot_matrix = loaded.spot_matrix
    reference_dictionary = loaded.reference_dictionary

    if loaded.target_composition is None:
        nnls_targets = run_nnls_baseline(spot_matrix, reference_dictionary)
        target_composition = nnls_targets
        target_source = "nnls_pseudo_labels"
    else:
        target_composition = loaded.target_composition
        target_source = "provided_ground_truth"

    cross_pred, train_metrics = train_cross_attention_from_tensors(
        cfg,
        spot_matrix=spot_matrix,
        reference_dictionary=reference_dictionary,
        target_composition=target_composition,
    )
    nnls_pred = run_nnls_baseline(spot_matrix, reference_dictionary)

    cross_metrics = evaluate_predictions(
        predicted_composition=cross_pred,
        reference_dictionary=reference_dictionary,
        spot_matrix=spot_matrix,
        target_composition=loaded.target_composition,
    )
    nnls_metrics = evaluate_predictions(
        predicted_composition=nnls_pred,
        reference_dictionary=reference_dictionary,
        spot_matrix=spot_matrix,
        target_composition=loaded.target_composition,
    )

    payload = {
        "project": cfg.project_name,
        "dataset": cfg.data.dataset_name,
        "target_source": target_source,
        "shared_genes": len(loaded.shared_genes),
        "num_cell_types": len(loaded.cell_type_names),
        "cross_attention": {**train_metrics, **cross_metrics},
        "nnls": nnls_metrics,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Real data pipeline complete")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
