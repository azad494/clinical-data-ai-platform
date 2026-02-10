from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict, List, Tuple, Dict


class EncounterRow(TypedDict):
    encounter_id: int
    patient_id: int
    admit_time: str  # ISO format
    discharge_time: str  # ISO format
    scenario: str
    acuity: str


SCENARIO_DEFAULTS = {
    "routine": {"acuity_choices": ["low", "medium"], "los_hours": (6, 36)},
    "chest_pain": {"acuity_choices": ["medium", "high"], "los_hours": (12, 72)},
    "sepsis": {"acuity_choices": ["high"], "los_hours": (24, 120)},
    "copd_hypoxia": {"acuity_choices": ["medium", "high"], "los_hours": (24, 96)},
}


def ensure_encounter_counter(counter_path: Path) -> int:
    """
    Ensure encounter_id_counter.txt exists. If missing, create with '0'.
    Returns the last-used encounter_id (int).
    """
    counter_path.parent.mkdir(parents=True, exist_ok=True)

    if not counter_path.exists() or counter_path.stat().st_size == 0:
        counter_path.write_text("0", encoding="utf-8")
        return 0

    raw = counter_path.read_text(encoding="utf-8").strip()
    try:
        return int(raw)
    except ValueError:
        # If corrupted, reset to 0 (safe fallback for local dev)
        counter_path.write_text("0", encoding="utf-8")
        return 0


def _choose_scenario(rng: random.Random, scenario_weights: Dict[str, float]) -> str:
    scenarios = list(scenario_weights.keys())
    weights = [float(scenario_weights[s]) for s in scenarios]
    # Normalize just in case
    total = sum(weights) if sum(weights) > 0 else 1.0
    weights = [w / total for w in weights]
    return rng.choices(scenarios, weights=weights, k=1)[0]


def generate_encounters_for_day(
    day: str,
    encounters_per_day: int,
    patient_ids: List[int],
    start_encounter_id: int,
    scenario_weights: Dict[str, float],
    out_dir: Path,
    counter_path: Path,
    seed: int,
) -> Tuple[List[EncounterRow], int]:
    """
    Generate encounters for a given day and write encounters.csv into out_dir.
    Encounter IDs are globally unique using start_encounter_id as last-used.
    Updates counter_path to the new last-used ID.
    Returns (encounters_rows, new_last_encounter_id).
    """
    rng = random.Random(seed + 3003)

    day_start = datetime.fromisoformat(f"{day}T00:00:00")
    rows: List[EncounterRow] = []

    last_id = start_encounter_id

    for _ in range(encounters_per_day):
        last_id += 1
        encounter_id = last_id

        patient_id = int(rng.choice(patient_ids))
        scenario = _choose_scenario(rng, scenario_weights)

        scenario_cfg = SCENARIO_DEFAULTS.get(scenario, SCENARIO_DEFAULTS["routine"])
        acuity = rng.choice(scenario_cfg["acuity_choices"])
        los_min, los_max = scenario_cfg["los_hours"]
        los_hours = int(rng.randint(los_min, los_max))

        admit_offset_minutes = int(rng.randint(0, 23 * 60 + 59))
        admit = day_start + timedelta(minutes=admit_offset_minutes)
        discharge = admit + timedelta(hours=los_hours)

        rows.append(
            {
                "encounter_id": encounter_id,
                "patient_id": patient_id,
                "admit_time": admit.isoformat(timespec="seconds"),
                "discharge_time": discharge.isoformat(timespec="seconds"),
                "scenario": scenario,
                "acuity": acuity,
            }
        )

    # Write encounters.csv
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "encounters.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["encounter_id", "patient_id", "admit_time", "discharge_time", "scenario", "acuity"],
        )
        w.writeheader()
        for row in rows:
            w.writerow(row)

    # Update counter
    counter_path.write_text(str(last_id), encoding="utf-8")
    return rows, last_id
