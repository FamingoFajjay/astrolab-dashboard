import numpy as np
import pandas as pd
import pytest

from data_utils import (
    clean_numeric_data,
    get_lightcurve_stats,
    get_summary_values,
    load_csv,
)

def test_clean_numeric_data():
    df = pd.DataFrame({
        "time_btjd": [1, 2, 3, 4],
        "normalized_flux": [1.0, "bad", np.nan, 0.99],
    })

    cleaned = clean_numeric_data(
        df,
        ["time_btjd", "normalized_flux"]
    )

    assert len(cleaned) == 2
    assert cleaned["normalized_flux"].notna().all()

def test_lightcurve_stats():
    df = pd.DataFrame({
        "time_btjd": [10, 11, 12],
        "normalized_flux": [1.0, 0.98, 1.02],
    })

    stats = get_lightcurve_stats(df)

    assert stats["count"] == 3
    assert np.isclose(stats["median_flux"], 1.0)
    assert np.isclose(stats["time_span_days"], 2.0)

def test_summary_value():
    df = pd.DataFrame([{
        "best_period_days": 6.2,
        "best_duration_days": 0.12,
        "best_transit_time_btjd": 1350.0,
        "best_depth": 0.001,
    }])

    values = get_summary_values(df)

    assert np.isclose(values["best_period_days"], 6.2)
    assert values["best_depth"] > 0

def test_missing_columns(tmp_path):
    bad_df = pd.DataFrame({
        "wrong_column": [1, 2, 3]
    })

    path = tmp_path / "day03_tess_cleaned.csv"
    bad_df.to_csv(path, index=False)

    with pytest.raises(ValueError):
        load_csv("lightcurve", data_dir=tmp_path)

def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv("lightcurve", data_dir=tmp_path)

def test_real_lightcurve_csv():
    df = load_csv("lightcurve")
    cleaned = clean_numeric_data(
        df,
        ["time_btjd", "normalized_flux"]
    )

    assert len(cleaned) > 100
    assert np.isfinite(cleaned["normalized_flux"]).all()

def test_real_bls_csv():
    df = load_csv("periodogram")

    assert len(df) > 0
    assert "bls_power" in df.columns

def test_real_summary_csv():
    df = load_csv("summary")
    values = get_summary_values(df)

    assert values["best_period_days"] > 0
    assert values["best_depth"] > 0

def test_phase_data_matches_lightcurve():
    lc = load_csv("lightcurve")
    phase = load_csv("phase")

    assert len(lc) == len(phase)

    assert np.allclose(
        lc["normalized_flux"].to_numpy(),
        phase["normalized_flux"].to_numpy(),
        rtol=1e-8,
        atol=1e-10
    )

def test_best_period_exists_in_periodogram():
    periodogram = load_csv("periodogram")
    summary = load_csv("summary")

    best_period = float(summary.iloc[0]["best_period_days"])

    periods = periodogram["period_days"].to_numpy()

    assert np.isclose(
        periods,
        best_period,
        atol=1e-8
    ).any()