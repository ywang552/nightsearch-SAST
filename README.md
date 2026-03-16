# nightsearch-SAST

Research codebase for **spatial transcriptomics spot annotation** with a **cross-attention, reference-dictionary-guided** model and a simple **NNLS baseline**.

## Real-data v1 target: spatialLIBD DLPFC Visium

The first concrete public real-data family is **human DLPFC Visium** via **spatialLIBD / ExperimentHub**.

- spatialLIBD project: https://research.libd.org/spatialLIBD/
- DLPFC workflow: https://bioconductor.org/books/release/OSTA/pages/seq-workflow-dlpfc.html
- spatialLIBD intro (`fetch_data()`): https://research.libd.org/spatialLIBD/articles/spatialLIBD.html

Why this target for v1:
- public, documented, benchmark-style Visium dataset
- includes spot-level expression and region annotations
- stable programmatic access on the R side

## Python-first real-data architecture

Training/evaluation does **not** depend on R at runtime. Instead we use a normalized NPZ bundle contract consumed by both NNLS and cross-attention.

### Normalized bundle contract

`bundle.npz` keys:
- `spot_matrix`: `[num_spots, num_genes]`
- `gene_names`: `[num_genes]`
- `spot_ids`: `[num_spots]`
- optional `sample_ids`: `[num_spots]`
- optional `region_labels`: `[num_spots]`
- `reference_matrix`: `[num_reference_cells, num_reference_genes]`
- `reference_gene_names`: `[num_reference_genes]`
- `reference_cell_types`: `[num_reference_cells]`
- optional `target_composition`: `[num_spots, num_cell_types]`
- optional `target_cell_type_names`: `[num_cell_types]`

Split NPZ inputs (`spots.npz`, `reference_cells.npz`, optional `spot_composition.npz`) are also supported for compatibility.

## End-to-end real pipeline

`scripts/run_real_pipeline.py` performs:
1. load normalized bundle
2. gene match + aligned dictionary construction
3. deterministic train/validation split
4. cross-attention train/eval
5. NNLS eval
6. single JSON artifact with shared metric schema

Shared metric schema:
```json
{
  "method": "cross_attention|nnls",
  "split": "validation",
  "reconstruction_mse": 0.0,
  "composition_mae": 0.0,
  "composition_kl": 0.0
}
```
If supervised labels are unavailable, composition metrics are `null`.

## DLPFC conversion utility

Use `scripts/convert_dlpfc_spatiallibd_bundle.py` to convert one spatialLIBD-exported DLPFC sample into the normalized bundle.

Expected CSV inputs:
- spot expression matrix (row=spot, col=gene)
- spot metadata with `spot_id` and optional `sample_id`, `region_label`
- reference-cell expression matrix (row=cell, col=gene)
- reference labels with `cell_type`
- optional composition matrix CSV (for supervised evaluation)

Example:
```bash
PYTHONPATH=src python scripts/convert_dlpfc_spatiallibd_bundle.py \
  --spot-expression-csv data/raw/dlpfc_151673_spot_expression.csv \
  --spot-metadata-csv data/raw/dlpfc_151673_spot_metadata.csv \
  --reference-cells-csv data/raw/dlpfc_reference_cells.csv \
  --reference-labels-csv data/raw/dlpfc_reference_labels.csv \
  --output-npz data/processed/real/dlpfc_151673_bundle.npz
```

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
PYTHONPATH=src pytest -q -m "not slow"
PYTHONPATH=src python scripts/create_real_example_data.py --output-dir data/processed/real
PYTHONPATH=src python scripts/run_real_pipeline.py --config configs/real_example.yaml --output artifacts/real_pipeline_metrics.json
# Optional: override bundle path when data lives outside data/processed/real
PYTHONPATH=src python scripts/run_real_pipeline.py --config configs/real_example.yaml --bundle-npz-path /tmp/real_demo/dlpfc_151673_bundle.npz --output artifacts/real_pipeline_metrics.json
```


The default `configs/real_example.yaml` expects `data/processed/real/dlpfc_151673_bundle.npz`.
Use `--bundle-npz-path` to point to a different generated location without editing config.

## Configs

- `configs/default.yaml`: synthetic baseline path
- `configs/real_example.yaml`: DLPFC-family real path (bundle-first)

## Notes

- Synthetic path remains intact.
- v1 focuses on one cleanly-supported DLPFC sample flow, not many partially-supported formats.
