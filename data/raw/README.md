# Raw Data Zone

Immutable daily source snapshots generated locally.

## Layout

- `data/raw/YYYY-MM-DD/patients.csv`
- `data/raw/YYYY-MM-DD/encounters.csv`

## Notes

- Files in this zone are input to ETL (`--source raw`).
- This zone represents Bronze/raw data and should not be manually edited.
