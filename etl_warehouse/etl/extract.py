from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


def extract_day(input_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Read the daily input folder and return raw DataFrames.

    Expected files (Phase 2):
      - patients.csv
      - encounters.csv
      - vitals.csv
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {input_dir}")

    patients_path = input_dir / "patients.csv"
    encounters_path = input_dir / "encounters.csv"
    vitals_path = input_dir / "vitals.csv"

    missing = [str(p.name) for p in [patients_path, encounters_path, vitals_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required files in {input_dir}: {', '.join(missing)}")

    patients = pd.read_csv(patients_path)
    encounters = pd.read_csv(encounters_path)
    vitals = pd.read_csv(vitals_path)

    return {
        "patients": patients,
        "encounters": encounters,
        "vitals": vitals,
    }
