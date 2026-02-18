# Generator State

Persistent state used by `data_generator/generate_daily_batch.py`.

## Files

- `patients_master.csv`
  - Master registry of all generated patients across dates
  - Ensures patient IDs stay consistent and unique
- `encounter_id_counter.txt`
  - Last-used encounter ID
  - Ensures `encounter_id` remains globally unique across dates

## Notes

- Generator updates these files on each run.
- Daily generated outputs are written to `data/raw/YYYY-MM-DD/` or `data/sample/YYYY-MM-DD/`.
