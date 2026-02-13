from __future__ import annotations

from typing import Dict
import pandas as pd


def transform_day(raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    patients = raw_data["patients"].copy()
    encounters = raw_data["encounters"].copy()

    # Ensure integer IDs
    patients["patient_id"] = patients["patient_id"].astype(int)
    encounters["patient_id"] = encounters["patient_id"].astype(int)
    encounters["encounter_id"] = encounters["encounter_id"].astype(int)

    # Parse timestamps
    encounters["admit_time"] = pd.to_datetime(encounters["admit_time"])
    encounters["discharge_time"] = pd.to_datetime(encounters["discharge_time"])

    # Calculate length of stay (hours)
    delta = pd.to_datetime(encounters["discharge_time"]) - pd.to_datetime(encounters["admit_time"])
    encounters["los_hours"] = delta.dt.total_seconds() / 3600.0

    return {
        "patients": patients,
        "encounters": encounters,
    }