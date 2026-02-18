# Data Generator

Synthetic clinical data generator for daily batch inputs.

## Implemented Scope (Phase 1)

For each run date, the generator currently creates:

- `patients.csv`
- `encounters.csv`

Output modes:

- `raw` -> `data/raw/YYYY-MM-DD/`
- `sample` -> `data/sample/YYYY-MM-DD/`

## Entry Point

- `data_generator/generate_daily_batch.py`

Run examples:

```bash
python data_generator/generate_daily_batch.py --date 2026-02-08 --mode sample
python data_generator/generate_daily_batch.py --date 2026-02-09 --mode raw
```

## Current Generation Flow

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

## Planned Next

- Add `vitals.csv`
- Add `labs.csv`
- Add `notes.jsonl`
- Enforce full schema contracts across all generated datasets
