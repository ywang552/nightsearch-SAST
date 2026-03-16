"""Run real data pipeline (cross-attention + NNLS) on a normalized bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nightsearch_sast.baselines.nnls import run_nnls_with_metrics
from nightsearch_sast.config import load_config
from nightsearch_sast.data.real_data import load_real_experiment_data
from nightsearch_sast.data.split import make_spot_split
from nightsearch_sast.training.train import run_cross_attention_with_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run real data pipeline (cross-attention + NNLS).")
    parser.add_argument("--config", default="configs/real_example.yaml")
    parser.add_argument("--output", default="artifacts/real_pipeline_metrics.json")
    parser.add_argument(
        "--bundle-npz-path",
        default="",
        help="Optional override for data.real.bundle_npz_path without editing config",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config(args.config)

    if cfg.data.dataset_name != "real_npz":
        raise ValueError("Real pipeline requires data.dataset_name=real_npz")

    if args.bundle_npz_path:
        cfg.data.real.bundle_npz_path = args.bundle_npz_path

    bundle_path = cfg.data.real.bundle_npz_path
    if bundle_path and not Path(bundle_path).exists():
        raise FileNotFoundError(
            "Configured real bundle path was not found: "
            f"{bundle_path}. Either generate demo data at data/processed/real "
            "(PYTHONPATH=src python scripts/create_real_example_data.py --output-dir data/processed/real) "
            "or pass --bundle-npz-path <path-to-bundle.npz>."
        )

    bundle, aligned = load_real_experiment_data(cfg.data.real)
    split = make_spot_split(
        num_spots=aligned.aligned_spot_matrix.shape[0],
        validation_fraction=cfg.data.real.validation_fraction,
        seed=cfg.seed,
    )

    nnls_all_pred, _ = run_nnls_with_metrics(
        spot_matrix=aligned.aligned_spot_matrix,
        reference_dictionary=aligned.reference_dictionary,
        split_name="all",
        target_composition=None,
    )
    train_target = bundle.target_composition if bundle.target_composition is not None else nnls_all_pred
    target_source = "provided_ground_truth" if bundle.target_composition is not None else "nnls_pseudo_labels"

    cross_pred, cross_metrics = run_cross_attention_with_metrics(
        config=cfg,
        spot_matrix=aligned.aligned_spot_matrix,
        reference_dictionary=aligned.reference_dictionary,
        target_composition=train_target,
        split=split,
        supervised_target=bundle.target_composition,
    )

    val_idx = split.validation_indices
    nnls_pred, nnls_metrics = run_nnls_with_metrics(
        spot_matrix=aligned.aligned_spot_matrix[val_idx],
        reference_dictionary=aligned.reference_dictionary,
        split_name="validation",
        target_composition=bundle.target_composition[val_idx] if bundle.target_composition is not None else None,
    )

    payload = {
        "project": cfg.project_name,
        "dataset": cfg.data.dataset_name,
        "dataset_family": cfg.data.real.dataset_family,
        "target_source": target_source,
        "num_spots": len(bundle.spot_ids),
        "matched_genes": aligned.matched_gene_count,
        "num_cell_types": len(aligned.cell_type_names),
        "split": {
            "seed": split.seed,
            "validation_fraction": split.validation_fraction,
            "train_size": int(split.train_indices.numel()),
            "validation_size": int(split.validation_indices.numel()),
        },
        "cross_attention": cross_metrics,
        "nnls": nnls_metrics,
        "metadata": {
            "sample_ids_available": bundle.sample_ids is not None,
            "region_labels_available": bundle.region_labels is not None,
            "spot_ids_preview": bundle.spot_ids[:5],
            "cell_type_names": aligned.cell_type_names,
            "matched_gene_names_preview": aligned.matched_gene_names[:10],
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    _ = cross_pred, nnls_pred
    print("Real data pipeline complete")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
