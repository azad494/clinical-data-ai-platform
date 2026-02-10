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

## Daily Generation Order (Frozen)

For a given date `YYYY-MM-DD`, generation happens in this strict order:

1) Update persistent patient registry (local only)
   - File: `data_generator/state/patients_master.csv`
   - Add `new_patients_per_day` new patients (until `max_total`)

2) Generate encounters for the day (anchor table)
   - Output: `data/{raw|sample}/YYYY-MM-DD/encounters.csv`
   - Each encounter references `patient_id` and defines:
     - `encounter_id`, `admit_time`, `discharge_time`, `scenario`, `acuity`

3) Export daily ACTIVE patients snapshot
   - Output: `data/{raw|sample}/YYYY-MM-DD/patients.csv`
   - Contains only patients referenced in that day's `encounters.csv`

4) Generate vitals within encounter windows
   - Output: `data/{raw|sample}/YYYY-MM-DD/vitals.csv`
   - Each row must include `encounter_id`, `patient_id`, `event_time`

5) Generate labs triggered by scenario/vitals
   - Output: `data/{raw|sample}/YYYY-MM-DD/labs.csv`

6) Generate notes driven by scenario + events (vitals/labs)
   - Output: `data/{raw|sample}/YYYY-MM-DD/notes.jsonl`
   - Each note includes `encounter_id`, `patient_id`, `note_time`, `note_type`, `text`
## Output Mode Contract

The generator supports exactly two output modes:

- `raw`:
  - Output: `data/raw/YYYY-MM-DD/`
  - Used for local daily runs (ignored by git)

- `sample`:
  - Output: `data/sample/YYYY-MM-DD/`
  - Used for a single GitHub demo day (committed)

`generate_daily_batch.py` must accept an output mode parameter and write all 5 files into the selected date folder.
## Intended CLI (Design)

- Generate local daily raw data:
  - `python data_generator/generate_daily_batch.py --date YYYY-MM-DD --mode raw`

- Generate GitHub sample snapshot:
  - `python data_generator/generate_daily_batch.py --date YYYY-MM-DD --mode sample`
