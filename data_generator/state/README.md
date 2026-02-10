# Generator State (Local Only)

This folder stores persistent generator state required to model longitudinal data.

## Files

- `patients_master.csv`
  - Persistent master list of all synthetic patients generated so far
  - Grows over time as `new_patients_per_day` are added
  - Used so patient IDs remain unique across days

## Notes

- This folder is local-only and should be ignored by git.
- Sample data committed to GitHub lives under `data/sample/YYYY-MM-DD/`.
