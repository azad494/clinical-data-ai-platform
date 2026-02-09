# Data Generator (Project 0)

This module generates **meaningful synthetic clinical data** for the platform.

## Output Structure

For a given date `YYYY-MM-DD`, the generator writes:

- Local daily raw data (ignored by git):
  - `data/raw/YYYY-MM-DD/`
- One-day GitHub demo snapshot (committed):
  - `data/sample/YYYY-MM-DD/`

Files generated per day:
- `patients.csv`
- `encounters.csv` (ANCHOR)
- `vitals.csv`
- `labs.csv`
- `notes.jsonl`

## Meaningful Connections (Join Strategy)

The dataset is designed around **encounters**.

- `patients.csv` is joined using `patient_id`
- `encounters.csv` contains `encounter_id` + `patient_id`
- `vitals.csv`, `labs.csv`, and `notes.jsonl` must include:
  - `encounter_id` (required)
  - `patient_id` (required for convenience)
- All event timestamps (`event_time`, `note_time`) must fall within:
  - `admit_time <= time <= discharge_time`

This ensures consistent, realistic relationships across tables.

## Schemas (Contracts)

Raw contracts live in `data_generator/schemas/` and define:
- required fields
- types and ranges
- foreign keys
- time-window constraints

Generator logic must follow these schemas.

## Modules

- `generate_daily_batch.py` = orchestrator (single entrypoint)
- `generators/` = dataset generators:
  - patients → encounters → vitals/labs/notes (in this order)

## Run Contract (to be implemented)

Examples of intended usage:

Generate GitHub demo snapshot:
- Output: `data/sample/YYYY-MM-DD/`

Generate local daily raw:
- Output: `data/raw/YYYY-MM-DD/`
