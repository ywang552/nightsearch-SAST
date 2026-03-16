# Data Directory

Use this directory for local research data only.

- `data/raw/`: source data copied or downloaded locally
- `data/interim/`: temporary intermediate files
- `data/processed/`: derived datasets and features
- `data/processed/real/`: location for generated tiny NPZ example files (`scripts/create_real_example_data.py`)

## Normalized real bundle

Preferred real-data input is one NPZ bundle (for example `data/processed/real/dlpfc_151673_bundle.npz`) containing:
- `spot_matrix`, `gene_names`, `spot_ids`
- optional `sample_ids`, `region_labels`
- `reference_matrix`, `reference_gene_names`, `reference_cell_types`
- optional `target_composition`, `target_cell_type_names`

Large datasets and generated outputs should stay out of git unless a workflow explicitly requires tracked sample data.
