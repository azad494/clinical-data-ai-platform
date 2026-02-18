# Clinical Data AI Platform

Production-style clinical data engineering project built with synthetic data, Python ETL, SQL modeling, and a local DuckDB warehouse.

## Current Status (Implemented)

- Daily synthetic generation is implemented for:
  - `patients.csv`
  - `encounters.csv`
- Generator supports two output modes:
  - `raw` -> `data/raw/YYYY-MM-DD/`
  - `sample` -> `data/sample/YYYY-MM-DD/`
- Batch ETL is implemented (`extract -> transform -> load`) with one entrypoint:
  - `etl_warehouse/etl/run_etl.py`
- Warehouse is implemented in DuckDB:
  - DB file: `data/processed/clinical_warehouse.duckdb`
  - Schemas: `raw`, `curated`, `gold`
  - Gold view: `gold.daily_encounter_summary`
- Data quality checks are implemented during load:
  - `curated.dim_patients` row count must match distinct `raw.patients.patient_id`
  - `curated.fact_encounters` row count must match `raw.encounters`

## Repo Areas

- `data_generator/` - synthetic data generation (Phase 1 complete)
- `etl_warehouse/` - ETL pipeline and SQL warehouse objects
- `data/raw/` - local immutable daily raw snapshots
- `data/sample/` - git-friendly demo snapshot(s)
- `data/processed/` - DuckDB warehouse and exported curated CSVs
- `dashboards/` - analytics/dashboard work area
- `docs/` - architecture and project documentation

## Quickstart

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate one day of sample data:

```bash
python data_generator/generate_daily_batch.py --date 2026-02-08 --mode sample
```

Generate one day of raw data:

```bash
python data_generator/generate_daily_batch.py --date 2026-02-09 --mode raw
```

Run ETL for a day:

```bash
python etl_warehouse/etl/run_etl.py --date 2026-02-08 --source sample
```

## Current Warehouse Model

- `raw.patients`
- `raw.encounters`
- `curated.dim_patients`
- `curated.fact_encounters`
- `gold.daily_encounter_summary`

## Next Planned Work

- Add `vitals.csv`, `labs.csv`, and `notes.jsonl` generation
- Extend ETL to ingest those datasets
- Add warehouse indexes/performance tuning
- Add BI/dashboard and AI assistant layers

## Author

Md Azad Hossain Raju  
Tucson, AZ  
LinkedIn: https://www.linkedin.com/in/azad-raju/

