# Data Directory

Use this directory for local research data only.

- `data/raw/`: source data copied or downloaded locally
- `data/interim/`: temporary intermediate files
- `data/processed/`: derived datasets and features
- `data/processed/real/`: location for generated tiny NPZ example files (`scripts/create_real_example_data.py`)

Large datasets and generated outputs should stay out of git unless a workflow explicitly requires tracked sample data.
