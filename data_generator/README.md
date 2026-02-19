# Data Generator

Synthetic clinical data generator for daily batch inputs.

## Implemented Scope (Current)

For each run date, the generator currently creates:

- `patients.csv`
- `encounters.csv`

Output modes:

- `raw` -> `data/raw/YYYY-MM-DD/`
- `sample` -> `data/sample/YYYY-MM-DD/`

## Daily Output Files (Contract)

For a given date `YYYY-MM-DD`, daily files are written as:

- Raw mode:
  - `data/raw/YYYY-MM-DD/patients.csv`
  - `data/raw/YYYY-MM-DD/encounters.csv`
  - `data/raw/YYYY-MM-DD/vitals.csv`
- Sample mode:
  - `data/sample/YYYY-MM-DD/patients.csv`
  - `data/sample/YYYY-MM-DD/encounters.csv`
  - `data/sample/YYYY-MM-DD/vitals.csv`

Vitals file contract:

- Filename and format: `vitals.csv` (CSV)
- Columns must match: `data_generator/schemas/vitals.schema.json`

## Entry Point

- `data_generator/generate_daily_batch.py`

Run examples:

```bash
python data_generator/generate_daily_batch.py --date 2026-02-08 --mode sample
python data_generator/generate_daily_batch.py --date 2026-02-09 --mode raw
```

## Generation Order (Contract)

1. Patients (master + daily snapshot)
2. Encounters
3. Vitals
4. Labs (later)
5. Notes (later)

Rationale:

- Vitals generation depends on encounter windows (`admit_time` to `discharge_time`).

## Current Generation Flow (Implemented Today)

1. Load config from `data_generator/config.yaml`
2. Initialize/read patient master state
3. Add new patients for the day
4. Ensure global encounter ID counter exists
5. Generate daily encounters with scenario-weighted logic
6. Export active-day patient snapshot

## State Management

Persistent local state is stored in `data_generator/state/`:

- `patients_master.csv`
- `encounter_id_counter.txt`

This keeps IDs stable and globally unique across dates.

Vitals state impact:

- Vitals does not change global counters such as `encounter_id_counter.txt`.
- Vitals rows are derived from existing daily encounters only.

## Planned Next

- Add `labs.csv`
- Add `notes.jsonl`
- Enforce full schema contracts across all generated datasets
