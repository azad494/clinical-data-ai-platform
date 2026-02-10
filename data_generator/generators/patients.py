from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Dict, TypedDict, List, Set, Tuple


class PatientRow(TypedDict):
    patient_id: int
    age: int
    sex: str


def _random_sex(rng: random.Random) -> str:
    return rng.choice(["M", "F", "U"])


def _random_age(rng: random.Random) -> int:
    # Simple but valid per schema (0..120)
    return rng.randint(0, 120)


def ensure_patients_master(master_path: Path, initial_count: int, seed: int) -> List[PatientRow]:
    """
    Ensure patients_master.csv exists. If not, create with initial_count patients.
    Returns the full master list (in memory) as dict rows with keys: patient_id, age, sex.
    """
    rng = random.Random(seed + 1001)

    if master_path.exists() and master_path.stat().st_size > 0:
        return load_patients_master(master_path)

    # Initialize fresh master
    rows: List[PatientRow] = []
    for pid in range(1, initial_count + 1):
        rows.append(
            {"patient_id": pid, "age": _random_age(rng), "sex": _random_sex(rng)}
        )

    write_patients_csv(master_path, rows)
    return rows


def load_patients_master(master_path: Path) -> List[PatientRow]:
    rows: List[PatientRow] = []
    with master_path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(
                {
                    "patient_id": int(row["patient_id"]),
                    "age": int(row["age"]),
                    "sex": row["sex"],
                }
            )
    return rows


def write_patients_csv(path: Path, rows: List[PatientRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["patient_id", "age", "sex"])
        w.writeheader()
        for row in rows:
            w.writerow(row)


def add_new_patients(
    master_path: Path,
    master_rows: List[PatientRow],
    new_patients_per_day: int,
    max_total: int,
    seed: int,
) -> Tuple[List[PatientRow], int]:
    """
    Append new patients to the master list up to max_total.
    Returns (updated_master_rows, added_count).
    """
    if new_patients_per_day <= 0:
        return master_rows, 0

    rng = random.Random(seed + 2002)

    current_total = len(master_rows)
    if current_total >= max_total:
        return master_rows, 0

    can_add = min(new_patients_per_day, max_total - current_total)
    next_id = max(int(r["patient_id"]) for r in master_rows) + 1 if master_rows else 1

    for i in range(can_add):
        pid = next_id + i
        master_rows.append(
            {"patient_id": pid, "age": _random_age(rng), "sex": _random_sex(rng)}
        )

    write_patients_csv(master_path, master_rows)
    return master_rows, can_add


def export_active_patients_snapshot(
    master_rows: List[PatientRow],
    active_patient_ids: Set[int],
    out_dir: Path,
) -> int:
    """
    Write daily patients.csv containing only active patients for that day.
    Output: out_dir/patients.csv
    Returns number of rows written.
    """
    active_rows = [r for r in master_rows if int(r["patient_id"]) in active_patient_ids]
    out_path = out_dir / "patients.csv"
    write_patients_csv(out_path, active_rows)
    return len(active_rows)
