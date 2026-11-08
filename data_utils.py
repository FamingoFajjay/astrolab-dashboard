
from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data"

FILES = {
    "lightcurve": "day03_tess_cleaned.csv",
    "periodogram": "day04_bls_periodogram.csv",
    "phase": "day04_phase_folded.csv",
    "summary": "day04_detection_summary.csv",
}

REQUIRED_COLUMNS = {
    "lightcurve": ["time_btjd", "normalized_flux"],
    "periodogram": ["period_days", "bls_power"],
    "phase": ["phase", "normalized_flux"],
    "summary": [
        "best_period_days",
        "best_duration_days",
        "best_transit_time_btjd",
        "best_depth",
    ],
}


def load_csv(kind, data_dir=DATA_DIR):
    """Read and validate one AstroLab CSV file."""

    if kind not in FILES:
        raise ValueError(f"Unknown dataset type: {kind}")

    path = Path(data_dir) / FILES[kind]

    if not path.is_file():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(f"CSV is empty: {path.name}")

    missing = [
        column
        for column in REQUIRED_COLUMNS[kind]
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{path.name} is missing columns: {missing}"
        )

    return df


def clean_numeric_data(df, columns):
    """Convert selected columns to numbers and remove invalid rows."""

    cleaned = df.copy()

    for column in columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce"
        )

    cleaned = cleaned.replace(
        [np.inf, -np.inf],
        np.nan
    )

    cleaned = cleaned.dropna(subset=columns)

    return cleaned


def get_lightcurve_stats(df):
    """Calculate descriptive statistics for a light curve."""

    cleaned = clean_numeric_data(
        df,
        ["time_btjd", "normalized_flux"]
    )

    if cleaned.empty:
        raise ValueError("No valid light curve observations.")

    time = cleaned["time_btjd"]
    flux = cleaned["normalized_flux"]

    return {
        "count": len(cleaned),
        "median_flux": float(flux.median()),
        "min_flux": float(flux.min()),
        "max_flux": float(flux.max()),
        "time_span_days": float(time.max() - time.min()),
    }


def get_summary_values(df):
    """Extract numeric results from the Day 4 summary."""

    row = df.iloc[0]

    keys = [
        "best_period_days",
        "best_duration_days",
        "best_transit_time_btjd",
        "best_depth",
    ]

    values = {}

    for key in keys:
        values[key] = float(row[key])

        if not np.isfinite(values[key]):
            raise ValueError(f"Invalid summary value: {key}")

    if values["best_period_days"] <= 0:
        raise ValueError("Period must be positive.")

    if not (
        0 < values["best_duration_days"]
        < values["best_period_days"]
    ):
        raise ValueError("Invalid transit duration.")

    return values
