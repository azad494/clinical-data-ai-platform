from __future__ import annotations

from pathlib import Path
from typing import Dict
import duckdb
import pandas as pd


def load_day(staged_data: Dict[str, pd.DataFrame], db_path: Path, schema_path: Path) -> None:
    patients = staged_data["patients"]
    encounters = staged_data["encounters"]

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(db_path)) as conn:
        if schema_path.exists():
            schema_sql = schema_path.read_text(encoding="utf-8").strip()
            if schema_sql:
                conn.execute(schema_sql)

        conn.register("patients_df", patients)
        conn.register("encounters_df", encounters)

        conn.execute(
            """
            CREATE SCHEMA IF NOT EXISTS raw
            """
        )
        conn.execute(
            """
            CREATE SCHEMA IF NOT EXISTS curated
            """
        )
        conn.execute(
            """
            CREATE OR REPLACE TABLE raw.patients AS
            SELECT * FROM patients_df
            """
        )
        conn.execute(
            """
            CREATE OR REPLACE TABLE raw.encounters AS
            SELECT * FROM encounters_df
            """
        )
        conn.execute(
            """
            CREATE OR REPLACE TABLE curated.dim_patients AS
            SELECT
                patient_id,
                age,
                sex
            FROM raw.patients
            """
        )
        conn.execute(
            """
            CREATE OR REPLACE TABLE curated.fact_encounters AS
            SELECT
                encounter_id,
                patient_id,
                admit_time,
                discharge_time,
                scenario,
                acuity,
                los_hours
            FROM raw.encounters
            """
        )

        gold_views_path = schema_path.with_name("gold_views.sql")
        if gold_views_path.exists():
            gold_views_sql = gold_views_path.read_text(encoding="utf-8").strip()
            if gold_views_sql:
                conn.execute(gold_views_sql)

        patients_row = conn.execute("SELECT COUNT(*) FROM curated.dim_patients").fetchone()
        encounters_row = conn.execute("SELECT COUNT(*) FROM curated.fact_encounters").fetchone()
        unique_patients_row = conn.execute("SELECT COUNT(DISTINCT patient_id) FROM raw.patients").fetchone()
        raw_encounters_row = conn.execute("SELECT COUNT(*) FROM raw.encounters").fetchone()

        if (
            patients_row is None
            or encounters_row is None
            or unique_patients_row is None
            or raw_encounters_row is None
        ):
            raise RuntimeError("Failed to fetch row counts from DuckDB.")
        patients_count = int(patients_row[0])
        encounters_count = int(encounters_row[0])
        unique_patients_count = int(unique_patients_row[0])
        raw_encounters_count = int(raw_encounters_row[0])

        if patients_count != unique_patients_count:
            raise ValueError(
                "Validation failed: curated.dim_patients count does not match unique raw patient_id count."
            )
        if encounters_count != raw_encounters_count:
            raise ValueError(
                "Validation failed: curated.fact_encounters count does not match raw.encounters row count."
            )

    print(f"load_day: wrote DuckDB file -> {db_path}")
    print(
        f"load_day: curated.dim_patients rows={patients_count}, "
        f"curated.fact_encounters rows={encounters_count}"
    )
    print(
        f"load_day: validation passed "
        f"(dim_patients={patients_count} == unique_raw_patients={unique_patients_count}, "
        f"fact_encounters={encounters_count} == raw_encounters={raw_encounters_count})"
    )
