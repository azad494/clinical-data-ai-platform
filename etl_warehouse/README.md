# Project 1 - Batch ETL and Warehouse

Batch ETL module for loading daily synthetic clinical data into a local DuckDB warehouse.

## Current Implementation

ETL entrypoint:

- `etl_warehouse/etl/run_etl.py`

Flow:

- `extract.py` reads `patients.csv` and `encounters.csv` from `data/{sample|raw}/YYYY-MM-DD/`
- `transform.py` enforces IDs, parses timestamps, computes `los_hours`
- `load.py` creates/loads warehouse tables and gold view in DuckDB

Warehouse SQL:

- `etl_warehouse/sql/schema.sql`
- `etl_warehouse/sql/gold_views.sql`

## Warehouse Objects

- `raw.patients`
- `raw.encounters`
- `curated.dim_patients`
- `curated.fact_encounters`
- `gold.daily_encounter_summary`

DuckDB file path:

- `data/processed/clinical_warehouse.duckdb`

## Run

```bash
python etl_warehouse/etl/run_etl.py --date 2026-02-08 --source sample
```

or

```bash
python etl_warehouse/etl/run_etl.py --date 2026-02-09 --source raw
```

## Validation Checks in Load Step

- `COUNT(curated.dim_patients)` must equal `COUNT(DISTINCT raw.patients.patient_id)`
- `COUNT(curated.fact_encounters)` must equal `COUNT(raw.encounters)`

If either check fails, ETL raises an error.
