# DLPFC real-data pipeline (v1)

## Chosen dataset target

First real-data integration targets **human DLPFC Visium** via spatialLIBD/ExperimentHub.

## Scope of v1

- one normalized NPZ bundle contract
- one deterministic split utility
- one shared metrics interface for cross-attention and NNLS
- one end-to-end runner writing a comparable JSON artifact

## Runtime boundary

R is used only upstream for data export/conversion.
Python training and evaluation remains R-free at runtime.

## Current assumptions

- reference dictionary is built by cell-type mean over matched genes
- gene matching is strict intersection of gene names
- composition labels may be missing; metrics degrade gracefully to reconstruction-only

## Output artifact

`artifacts/real_pipeline_metrics.json` includes:
- split metadata
- matched-gene count
- method-specific metrics using one schema

## Limitations

- no direct `.rds`/`SingleCellExperiment` reader in Python
- converter expects CSV exports from spatialLIBD workflow

## Usability note

Default example config resolves to `data/processed/real/dlpfc_151673_bundle.npz`.
If your generated bundle lives elsewhere (for example `/tmp/real_demo`), run with:
`--bundle-npz-path /tmp/real_demo/dlpfc_151673_bundle.npz`.

