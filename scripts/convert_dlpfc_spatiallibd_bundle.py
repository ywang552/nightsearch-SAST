"""Convert one spatialLIBD-exported DLPFC sample into the normalized NPZ real-data bundle.

Expected inputs are CSV files exported from R/spatialLIBD for one sample:
1) spot_expression_csv: first column = spot ID, remaining columns = genes.
2) spot_metadata_csv: must contain `spot_id`; optional `sample_id`, `region_label`.
3) reference_cells_csv: first column = reference-cell ID, remaining columns = genes.
4) reference_labels_csv: must contain `cell_type` in row order of reference cells.

This keeps runtime training/evaluation fully Python-only while supporting DLPFC Visium data.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def _read_matrix_csv(path: str) -> tuple[list[str], np.ndarray, list[str]]:
    with Path(path).open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) < 2:
            raise ValueError(f"Expected matrix CSV with id column and >=1 gene columns: {path}")
        genes = [str(x) for x in header[1:]]
        row_ids: list[str] = []
        rows: list[list[float]] = []
        for row in reader:
            row_ids.append(str(row[0]))
            rows.append([float(v) for v in row[1:]])
    return genes, np.asarray(rows, dtype=np.float32), row_ids


def _read_table_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = [{k: str(v) for k, v in row.items()} for row in reader]
    return fields, rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert spatialLIBD DLPFC exports to a normalized NPZ bundle")
    parser.add_argument("--spot-expression-csv", required=True)
    parser.add_argument("--spot-metadata-csv", required=True)
    parser.add_argument("--reference-cells-csv", required=True)
    parser.add_argument("--reference-labels-csv", required=True)
    parser.add_argument("--output-npz", required=True)
    parser.add_argument("--target-composition-csv", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    spot_genes, spot_matrix, spot_ids_from_matrix = _read_matrix_csv(args.spot_expression_csv)
    ref_genes, reference_matrix, _ = _read_matrix_csv(args.reference_cells_csv)

    spot_fields, spot_meta_rows = _read_table_csv(args.spot_metadata_csv)
    if "spot_id" not in spot_fields:
        raise ValueError("spot_metadata_csv must include a `spot_id` column")
    spot_meta_by_id = {row["spot_id"]: row for row in spot_meta_rows}

    ref_label_fields, ref_label_rows = _read_table_csv(args.reference_labels_csv)
    if "cell_type" not in ref_label_fields:
        raise ValueError("reference_labels_csv must include a `cell_type` column")
    if len(ref_label_rows) != reference_matrix.shape[0]:
        raise ValueError("reference-cells and reference-labels row counts must match")

    sample_ids: list[str] = []
    region_labels: list[str] = []
    for spot_id in spot_ids_from_matrix:
        row = spot_meta_by_id.get(spot_id, {})
        sample_ids.append(row.get("sample_id", ""))
        region_labels.append(row.get("region_label", ""))

    payload: dict[str, np.ndarray] = {
        "spot_matrix": spot_matrix,
        "gene_names": np.asarray(spot_genes, dtype=object),
        "spot_ids": np.asarray(spot_ids_from_matrix, dtype=object),
        "reference_matrix": reference_matrix,
        "reference_gene_names": np.asarray(ref_genes, dtype=object),
        "reference_cell_types": np.asarray([row["cell_type"] for row in ref_label_rows], dtype=object),
    }

    if any(sample_ids):
        payload["sample_ids"] = np.asarray(sample_ids, dtype=object)
    if any(region_labels):
        payload["region_labels"] = np.asarray(region_labels, dtype=object)

    if args.target_composition_csv:
        target_genes, target_matrix, _ = _read_matrix_csv(args.target_composition_csv)
        payload["target_composition"] = target_matrix
        payload["target_cell_type_names"] = np.asarray(target_genes, dtype=object)

    output_path = Path(args.output_npz)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_path, **payload)
    print(f"Wrote normalized DLPFC bundle: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
