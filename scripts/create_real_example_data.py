"""Create a tiny NPZ bundle mimicking one real spatial transcriptomics experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create tiny real-mode NPZ assets.")
    parser.add_argument("--output-dir", default="data/processed/real")
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    num_genes = 40
    genes = np.array([f"G{i:03d}" for i in range(num_genes)], dtype=object)
    cell_types = np.array(["astro", "neuron", "oligo", "micro"], dtype=object)

    cells_per_type = 8
    base = rng.uniform(0.5, 2.0, size=(len(cell_types), num_genes))
    ref_cells: list[np.ndarray] = []
    ref_labels: list[str] = []
    for i, cell_type in enumerate(cell_types):
        for _ in range(cells_per_type):
            expr = np.clip(base[i] + rng.normal(0, 0.15, size=num_genes), 0, None)
            ref_cells.append(expr)
            ref_labels.append(cell_type)

    reference_cells = np.asarray(ref_cells, dtype=np.float32)
    reference_labels = np.asarray(ref_labels, dtype=object)

    composition = rng.dirichlet(np.array([0.8, 1.2, 1.0, 0.7]), size=24).astype(np.float32)
    reference_dictionary = np.stack(
        [reference_cells[reference_labels == ct].mean(axis=0) for ct in cell_types],
        axis=0,
    )
    spot_matrix = (
        composition @ reference_dictionary + rng.normal(0, 0.03, size=(24, num_genes))
    ).clip(min=0).astype(np.float32)

    np.savez(output_dir / "spots.npz", X=spot_matrix, gene_names=genes)
    np.savez(
        output_dir / "reference_cells.npz",
        X=reference_cells,
        gene_names=genes,
        cell_types=reference_labels,
    )
    np.savez(output_dir / "spot_composition.npz", Y=composition, cell_type_names=cell_types)

    print(f"Wrote demo real-mode data to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
