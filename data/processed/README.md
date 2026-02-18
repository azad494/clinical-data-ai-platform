# Processed Data Zone

This folder contains warehouse outputs and analytics-ready artifacts.

## Current Contents

- `clinical_warehouse.duckdb`
  - Local DuckDB warehouse created by ETL
  - Includes schemas: `raw`, `curated`, `gold`
- `curated_dim_patients.csv`
  - Export of curated patient dimension
- `curated_fact_encounters.csv`
  - Export of curated encounter fact table

## How Data Gets Here

Run ETL:

```bash
python etl_warehouse/etl/run_etl.py --date YYYY-MM-DD --source sample
```

or

```bash
python etl_warehouse/etl/run_etl.py --date YYYY-MM-DD --source raw
```
