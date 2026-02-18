# Staged Data Zone

Reserved for intermediate/staging outputs between raw ingestion and warehouse load.

## Current State

- Not actively populated by the current ETL flow.
- Current ETL loads directly into DuckDB schemas (`raw`, `curated`, `gold`) under `data/processed/clinical_warehouse.duckdb`.

## Intended Use

- Temporary files for future multi-step transforms
- Validation snapshots before final warehouse load
