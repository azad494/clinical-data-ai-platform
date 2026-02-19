from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, TypedDict


class VitalRow(TypedDict):
    encounter_id: int
    patient_id: int
    event_time: str
    vital_type: str
    value: float
    unit: str
    source: str


DEFAULT_ENABLED_VITAL_TYPES = [
    "heart_rate",
    "resp_rate",
    "temperature_c",
    "spo2",
    "systolic_bp",
    "diastolic_bp",
]

DEFAULT_SCENARIO_RANGES: Dict[str, Dict[str, Dict[str, float]]] = {
    "routine": {
        "heart_rate": {"min": 60, "max": 100},
        "resp_rate": {"min": 12, "max": 20},
        "temperature_c": {"min": 36.3, "max": 37.5},
        "spo2": {"min": 95, "max": 100},
        "systolic_bp": {"min": 105, "max": 130},
        "diastolic_bp": {"min": 65, "max": 85},
    },
    "chest_pain": {
        "heart_rate": {"min": 75, "max": 115},
        "resp_rate": {"min": 14, "max": 24},
        "temperature_c": {"min": 36.0, "max": 37.8},
        "spo2": {"min": 92, "max": 98},
        "systolic_bp": {"min": 130, "max": 170},
        "diastolic_bp": {"min": 80, "max": 100},
    },
    "sepsis": {
        "heart_rate": {"min": 95, "max": 140},
        "resp_rate": {"min": 18, "max": 34},
        "temperature_c": {"min": 38.0, "max": 40.2},
        "spo2": {"min": 88, "max": 95},
        "systolic_bp": {"min": 80, "max": 105},
        "diastolic_bp": {"min": 45, "max": 70},
    },
    "copd_hypoxia": {
        "heart_rate": {"min": 80, "max": 120},
        "resp_rate": {"min": 16, "max": 30},
        "temperature_c": {"min": 36.4, "max": 38.0},
        "spo2": {"min": 82, "max": 92},
        "systolic_bp": {"min": 110, "max": 150},
        "diastolic_bp": {"min": 65, "max": 95},
    },
}

UNIT_BY_VITAL_TYPE = {
    "heart_rate": "bpm",
    "resp_rate": "breaths/min",
    "temperature_c": "C",
    "spo2": "%",
    "systolic_bp": "mmHg",
    "diastolic_bp": "mmHg",
}


def _pick_source(rng: random.Random, source_weights: Dict[str, float]) -> str:
    monitor_weight = float(source_weights.get("monitor", 0.85))
    manual_weight = float(source_weights.get("manual", 0.15))
    total = monitor_weight + manual_weight
    if total <= 0:
        return "monitor"
    r = rng.random() * total
    return "monitor" if r <= monitor_weight else "manual"


def _sample_value(
    rng: random.Random,
    vital_type: str,
    scenario: str,
    scenario_ranges: Dict[str, Dict[str, Dict[str, float]]],
) -> float:
    scenario_map = scenario_ranges.get(scenario, scenario_ranges.get("routine", {}))
    vital_range = scenario_map.get(vital_type)

    if vital_range is None:
        fallback = DEFAULT_SCENARIO_RANGES["routine"][vital_type]
        min_v = float(fallback["min"])
        max_v = float(fallback["max"])
    else:
        min_v = float(vital_range["min"])
        max_v = float(vital_range["max"])

    sampled = rng.uniform(min_v, max_v)
    if vital_type == "temperature_c":
        return round(sampled, 1)
    return round(sampled, 0)


def generate_vitals_for_day(
    day: str,
    encounters_rows: List[Dict[str, Any]],
    vitals_cfg: Dict[str, Any],
    seed: int,
) -> List[VitalRow]:
    """
    Build encounter-linked vitals rows for one day.
    Output row schema matches vitals.schema.json event model.
    """
    _ = day  # reserved for future date-specific behaviors

    rng = random.Random(seed + 4004)
    frequency_minutes = int(vitals_cfg.get("frequency_minutes", 60))
    if frequency_minutes <= 0:
        frequency_minutes = 60

    enabled_vital_types = vitals_cfg.get("enabled_vital_types", DEFAULT_ENABLED_VITAL_TYPES)
    if not enabled_vital_types:
        enabled_vital_types = DEFAULT_ENABLED_VITAL_TYPES

    scenario_ranges = vitals_cfg.get("scenario_ranges", DEFAULT_SCENARIO_RANGES)
    source_weights = vitals_cfg.get("source_weights", {"monitor": 0.85, "manual": 0.15})

    rows: List[VitalRow] = []
    step = timedelta(minutes=frequency_minutes)

    for encounter in encounters_rows:
        encounter_id = int(encounter["encounter_id"])
        patient_id = int(encounter["patient_id"])
        scenario = str(encounter.get("scenario", "routine"))

        admit = datetime.fromisoformat(str(encounter["admit_time"]))
        discharge = datetime.fromisoformat(str(encounter["discharge_time"]))
        if discharge < admit:
            continue

        event_time = admit
        while event_time <= discharge:
            source = _pick_source(rng, source_weights)
            for vital_type in enabled_vital_types:
                value = _sample_value(rng, str(vital_type), scenario, scenario_ranges)
                rows.append(
                    {
                        "encounter_id": encounter_id,
                        "patient_id": patient_id,
                        "event_time": event_time.isoformat(timespec="seconds"),
                        "vital_type": str(vital_type),
                        "value": float(value),
                        "unit": UNIT_BY_VITAL_TYPE[str(vital_type)],
                        "source": source,
                    }
                )
            event_time = event_time + step

    return rows


def write_vitals_csv(rows: List[VitalRow], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "vitals.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["encounter_id", "patient_id", "event_time", "vital_type", "value", "unit", "source"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return out_path
