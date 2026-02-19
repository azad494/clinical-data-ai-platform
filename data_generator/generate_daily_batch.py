from __future__ import annotations

import argparse
import random
from datetime import date
from pathlib import Path

import yaml

try:
    from data_generator.generators.patients import (
        ensure_patients_master,
        add_new_patients,
        export_active_patients_snapshot,
    )
    from data_generator.generators.encounters import (
        ensure_encounter_counter,
        generate_encounters_for_day,
    )
    from data_generator.generators.vitals import (
        generate_vitals_for_day,
        write_vitals_csv,
    )
except ImportError:
    from generators.patients import (
        ensure_patients_master,
        add_new_patients,
        export_active_patients_snapshot,
    )
    from generators.encounters import (
        ensure_encounter_counter,
        generate_encounters_for_day,
    )
    from generators.vitals import (
        generate_vitals_for_day,
        write_vitals_csv,
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate one day of synthetic clinical data (Phase 1).")
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--mode", required=True, choices=["raw", "sample"], help="Output mode: raw or sample")
    return p.parse_args()


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg


def resolve_output_dir(mode: str, day: str) -> Path:
    base = Path("data") / ("raw" if mode == "raw" else "sample")
    return base / day


def main() -> None:
    args = parse_args()

    # Validate date format early
    _ = date.fromisoformat(args.date)

    config = load_config(Path("data_generator") / "config.yaml")

    # Reproducibility
    seed = int(config.get("seed", 42))
    random.seed(seed)

    # Prepare output folder
    out_dir = resolve_output_dir(args.mode, args.date)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Ensure local state folder exists
    state_dir = Path("data_generator") / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # ---- Phase 1 Pipeline ----
    # 1) Ensure patient master exists (or initialize)
    master_path = state_dir / "patients_master.csv"
    patients_cfg = config.get("patients", {})
    master_rows = ensure_patients_master(
        master_path=master_path,
        initial_count=int(patients_cfg.get("initial_count", 100)),
        seed=seed,
    )

    # 2) Add new patients for the day (growth)
    new_per_day = int(patients_cfg.get("new_patients_per_day", 0))
    max_total = int(patients_cfg.get("max_total", 5000))
    master_rows, added_count = add_new_patients(
        master_path=master_path,
        master_rows=master_rows,
        new_patients_per_day=new_per_day,
        max_total=max_total,
        seed=seed,
    )

    # 3) Ensure encounter counter exists
    counter_path = state_dir / "encounter_id_counter.txt"
    last_encounter_id = ensure_encounter_counter(counter_path)

    # 4) Generate encounters (globally unique IDs) and write encounters.csv
    encounters_cfg = config.get("encounters", {})
    encounters_per_day = int(encounters_cfg.get("count_per_day", 160))
    scenario_weights = encounters_cfg.get("scenarios", {
        "routine": 0.55,
        "chest_pain": 0.20,
        "sepsis": 0.15,
        "copd_hypoxia": 0.10
    })

    patient_ids_all = [r["patient_id"] for r in master_rows]
    encounters_rows, new_last_id = generate_encounters_for_day(
        day=args.date,
        encounters_per_day=encounters_per_day,
        patient_ids=patient_ids_all,
        start_encounter_id=last_encounter_id,
        scenario_weights=scenario_weights,
        out_dir=out_dir,
        counter_path=counter_path,
        seed=seed,
    )

    # 5) Generate encounter-linked vitals and write vitals.csv
    vitals_cfg = config.get("vitals", {})
    vitals_rows = generate_vitals_for_day(
        day=args.date,
        encounters_rows=encounters_rows,
        vitals_cfg=vitals_cfg,
        seed=seed,
    )
    vitals_path = write_vitals_csv(vitals_rows, out_dir=out_dir)

    # 6) Export ACTIVE patients snapshot for the day (patients.csv)
    active_patient_ids = sorted({row["patient_id"] for row in encounters_rows})
    active_count = export_active_patients_snapshot(
        master_rows=master_rows,
        active_patient_ids=set(active_patient_ids),
        out_dir=out_dir,
    )

    # ---- Summary ----
    print("=== Phase 1 Generation Complete ===")
    print(f"date: {args.date}")
    print(f"mode: {args.mode}")
    print(f"output_dir: {out_dir}")
    print(f"seed: {seed}")
    print(f"patients_master_path: {master_path}")
    print(f"patients_master_total: {len(master_rows)} (added today: {added_count})")
    print(f"encounters_written: {len(encounters_rows)}")
    print(f"vitals_written: {len(vitals_rows)}")
    print(f"vitals_path: {vitals_path}")
    print(f"active_patients_written: {active_count}")
    print(f"encounter_id_counter updated to: {new_last_id}")


if __name__ == "__main__":
    main()
