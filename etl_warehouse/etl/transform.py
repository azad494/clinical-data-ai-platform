from __future__ import annotations

from typing import Dict
import pandas as pd


def transform_day(raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    patients = raw_data["patients"].copy()
    encounters = raw_data["encounters"].copy()
    vitals = raw_data["vitals"].copy()

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

    # Vitals typing/parsing for warehouse readiness
    vitals["patient_id"] = pd.to_numeric(vitals["patient_id"], errors="coerce").astype("Int64")
    vitals["encounter_id"] = pd.to_numeric(vitals["encounter_id"], errors="coerce").astype("Int64")
    vitals["value"] = pd.to_numeric(vitals["value"], errors="coerce")
    vitals["vital_type"] = vitals["vital_type"].astype("string")
    vitals["unit"] = vitals["unit"].astype("string")
    vitals["event_time"] = pd.to_datetime(vitals["event_time"], errors="coerce")

    # Required field validation (fail ETL if any required value is null)
    required_vitals_cols = ["patient_id", "encounter_id", "event_time", "vital_type", "value"]
    null_counts = vitals[required_vitals_cols].isna().sum()
    violated = null_counts[null_counts > 0]
    if not violated.empty:
        details = ", ".join(f"{col}={int(count)}" for col, count in violated.items())
        raise ValueError(f"Vitals required-field validation failed: {details}")

    # Referential integrity: vitals must map to a real encounter and matching patient.
    encounter_lookup = encounters[["encounter_id", "patient_id", "admit_time", "discharge_time"]].copy()
    encounter_lookup = encounter_lookup.rename(columns={"patient_id": "encounter_patient_id"})
    vitals_joined = vitals.merge(encounter_lookup, on="encounter_id", how="left")

    missing_encounter_count = int(vitals_joined["encounter_patient_id"].isna().sum())
    if missing_encounter_count > 0:
        raise ValueError(
            "Vitals referential integrity failed: "
            f"{missing_encounter_count} rows have encounter_id not present in encounters"
        )

    patient_mismatch_count = int((vitals_joined["patient_id"] != vitals_joined["encounter_patient_id"]).sum())
    if patient_mismatch_count > 0:
        raise ValueError(
            "Vitals referential integrity failed: "
            f"{patient_mismatch_count} rows have patient_id that does not match the encounter patient_id"
        )

    # Core clinical time-window validation: event must occur during encounter.
    outside_window = (
        (vitals_joined["event_time"] < vitals_joined["admit_time"])
        | (vitals_joined["event_time"] > vitals_joined["discharge_time"])
    )
    outside_window_count = int(outside_window.sum())
    if outside_window_count > 0:
        raise ValueError(
            "Vitals time-window validation failed: "
            f"{outside_window_count} rows have event_time outside admit_time..discharge_time"
        )

    return {
        "patients": patients,
        "encounters": encounters,
        "vitals": vitals,
    }
