from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .extract import extract_day
    from .transform import transform_day
    from .load import load_day
except ImportError:
    from extract import extract_day
    from transform import transform_day
    from load import load_day


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run batch ETL for one day.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--source", required=True, choices=["sample", "raw"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_dir = Path("data") / args.source / args.date
    db_path = Path("data") / "processed" / "clinical_warehouse.duckdb"
    schema_path = Path("etl_warehouse") / "sql" / "schema.sql"

    print("=== ETL START ===")
    print(f"date: {args.date}")
    print(f"source: {args.source}")
    print(f"input_dir: {input_dir}")
    print(f"db_path: {db_path}")
    print(f"schema_path: {schema_path}")

    raw_data = extract_day(input_dir)
    staged_data = transform_day(raw_data)
    load_day(staged_data, db_path=db_path, schema_path=schema_path)

    print("=== ETL COMPLETE ===")


if __name__ == "__main__":
    main()
