from __future__ import annotations

from typing import Dict
import pandas as pd


def load_day(staged_data: Dict[str, pd.DataFrame]) -> None:
    patients = staged_data["patients"]
    encounters = staged_data["encounters"]

    print("load_day: staged shapes ->", patients.shape, encounters.shape)