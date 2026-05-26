"""
Shared fixtures for the spillover test suite.
All fixtures use synthetic data — no real DTA files required.
"""
import numpy as np
import pandas as pd
import pytest


def _make_wave(period: str, geo_type: str, n_areas: int, n_per_area: int,
               remit_shares: list[float], spillover_strength: float,
               seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic BID-like DataFrame for one wave.

    remit_shares: list of length n_areas — fraction of HHs receiving remittances
    spillover_strength: if > 0, non-receiver income scales with remit_share (ground truth)
    """
    rng = np.random.default_rng(seed)
    rows = []
    hh_id = 0
    for area_idx, share in enumerate(remit_shares):
        area_val = area_idx + 1
        base_income = 5000 + area_idx * 200 + spillover_strength * share * 10000
        for i in range(n_per_area):
            hh_id += 1
            is_receiver = rng.random() < share
            remesas_ch = float(rng.integers(500, 5000)) if is_receiver else 0.0
            ylm_ci = float(rng.normal(base_income, 500)) if not is_receiver else float(rng.normal(4000, 300))
            rows.append({
                "idh_ch": hh_id,
                "idp_ci": hh_id,
                "factor_ch": 1.0,
                "factor_ci": 1.0,
                "region_c" if geo_type == "dept" else "dominio": float(area_val),
                "remesas_ch": remesas_ch,
                "remesas_ci": remesas_ch,
                "ylm_ci": max(ylm_ci, 0),
                "relacion_ci": 1,  # all are heads for simplicity
                "_wave": period,
                "pais_c": 340,
            })
    return pd.DataFrame(rows)


@pytest.fixture
def synthetic_waves():
    """
    Three departments × two waves. Wave t1→t2 has built-in positive spillover.
    Dept 1: 60% remit, Dept 2: 30% remit, Dept 3: 5% remit.
    """
    shares = [0.60, 0.30, 0.05]
    w1 = _make_wave("2018m6", "dept", n_areas=3, n_per_area=50,
                    remit_shares=shares, spillover_strength=1.0, seed=1)
    # Increase shares slightly in wave 2 to ensure Δpct_remit > 0 for all areas
    shares2 = [s + 0.05 for s in shares]
    w2 = _make_wave("2019m6", "dept", n_areas=3, n_per_area=50,
                    remit_shares=shares2, spillover_strength=1.0, seed=2)
    return {"2018m6": w1, "2019m6": w2}


@pytest.fixture
def synthetic_waves_no_spillover():
    """Same structure but spillover_strength=0 — β should be near zero."""
    shares = [0.60, 0.30, 0.05]
    w1 = _make_wave("2018m6", "dept", n_areas=3, n_per_area=50,
                    remit_shares=shares, spillover_strength=0.0, seed=10)
    shares2 = [s + 0.05 for s in shares]
    w2 = _make_wave("2019m6", "dept", n_areas=3, n_per_area=50,
                    remit_shares=shares2, spillover_strength=0.0, seed=11)
    return {"2018m6": w1, "2019m6": w2}


@pytest.fixture
def single_wave(synthetic_waves):
    return {"2018m6": synthetic_waves["2018m6"]}


@pytest.fixture
def wave_with_missing_remit(synthetic_waves):
    """Copy of 2018m6 with remesas_ch set to NaN for ~20% of HHs."""
    df = synthetic_waves["2018m6"].copy()
    rng = np.random.default_rng(99)
    mask = rng.random(len(df)) < 0.2
    df.loc[mask, "remesas_ch"] = np.nan
    return {"2018m6": df}


@pytest.fixture
def wave_missing_ynlm(synthetic_waves):
    """Simulates 2022 situation: no remesas_ch column at all."""
    df = synthetic_waves["2018m6"].drop(columns=["remesas_ch", "remesas_ci"])
    df["_wave"] = "2022m6"
    return {"2022m6": df}
