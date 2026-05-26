"""
Tests for hdmf_spillover_hnd.py

All synthetic-fixture tests run without any real DTA files.
The real-data smoke test (test_real_data_dept_count) requires HND_2023m6_BID.dta.

Run:
    pytest "bases armo/armo/tests/test_spillover_hnd.py" -v
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Add the armo directory to path so we can import the script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hdmf_spillover_hnd import (
    build_area_panel,
    run_correlations,
    run_fd_regression,
    _weighted_mean,
    _weighted_share,
    SKIP_WAVES,
    HND_DIR,
)


# ---------------------------------------------------------------------------
# Unit tests — _weighted_mean / _weighted_share helpers
# ---------------------------------------------------------------------------

def test_weighted_mean_basic():
    v = pd.Series([10.0, 20.0, 30.0])
    w = pd.Series([1.0, 2.0, 1.0])
    result = _weighted_mean(v, w)
    expected = (10 * 1 + 20 * 2 + 30 * 1) / 4
    assert abs(result - expected) < 1e-9


def test_weighted_mean_all_missing():
    v = pd.Series([np.nan, np.nan])
    w = pd.Series([1.0, 1.0])
    assert np.isnan(_weighted_mean(v, w))


def test_weighted_share_basic():
    flag = pd.Series([1.0, 0.0, 1.0, 0.0])
    w = pd.Series([1.0, 1.0, 1.0, 1.0])
    assert abs(_weighted_share(flag, w) - 0.5) < 1e-9


def test_weighted_share_with_nan():
    flag = pd.Series([1.0, np.nan, 0.0])
    w = pd.Series([1.0, 1.0, 1.0])
    # NaN row excluded → 1 out of 2 = 0.5
    assert abs(_weighted_share(flag, w) - 0.5) < 1e-9


# ---------------------------------------------------------------------------
# Remit flag logic
# ---------------------------------------------------------------------------

def test_remit_flag_positive(synthetic_waves):
    df = synthetic_waves["2018m6"].copy()
    panel = build_area_panel({"2018m6": df})
    # pct_remit must be between 0 and 1
    assert panel["pct_remit"].between(0, 1).all()


def test_remit_flag_zero_means_no_receivers(synthetic_waves):
    """Areas with 0% receivers should have pct_remit == 0."""
    df = synthetic_waves["2018m6"].copy()
    df["remesas_ch"] = 0.0   # zero out all remittances
    panel = build_area_panel({"2018m6": df})
    assert (panel["pct_remit"] == 0).all()


# ---------------------------------------------------------------------------
# build_area_panel shape and contamination
# ---------------------------------------------------------------------------

def test_area_panel_shape(synthetic_waves):
    """One row per wave × geo_unit."""
    panel = build_area_panel(synthetic_waves)
    # 2 waves × 3 depts = 6 rows
    assert len(panel) == 6
    assert set(panel["wave"].unique()) == {"2018m6", "2019m6"}
    assert panel["geo_unit"].nunique() == 3


def test_no_receiver_contamination(synthetic_waves):
    """
    Non-receiver income (mean_ylm_nr) must not include any receiving HH.
    Verify by checking that mean_ylm_nr < overall mean for areas with high share.
    """
    df = synthetic_waves["2018m6"].copy()
    # Manually set receivers to have very high income so contamination would be obvious
    df.loc[df["remesas_ch"] > 0, "ylm_ci"] = 999999.0
    panel = build_area_panel({"2018m6": df})
    # If non-receivers are correctly filtered, mean_ylm_nr should be << 999999
    assert (panel["mean_ylm_nr"] < 50000).all()


def test_missing_remesas_wave_skipped(wave_missing_ynlm):
    """Wave without remesas_ch column should produce empty panel (0 rows)."""
    panel = build_area_panel(wave_missing_ynlm)
    assert len(panel) == 0


def test_partial_nan_remesas(wave_with_missing_remit):
    """Panel still builds when some remesas_ch are NaN — no crash."""
    panel = build_area_panel(wave_with_missing_remit)
    assert len(panel) > 0
    assert panel["pct_remit"].notna().all()


# ---------------------------------------------------------------------------
# Outcome variable: ylm_ci used, not ytot_ci
# ---------------------------------------------------------------------------

def test_income_variable_no_double_count(synthetic_waves):
    """
    Ensure mean_ylm_nr is computed from ylm_ci, not ytot_ci.
    We add a ytot_ci column with values 10x larger.
    If the code mistakenly uses ytot_ci, mean_ylm_nr would be ~10x higher.
    """
    waves = {}
    for period, df in synthetic_waves.items():
        df = df.copy()
        df["ytot_ci"] = df["ylm_ci"] * 10
        waves[period] = df
    panel = build_area_panel(waves)
    # mean_ylm_nr should reflect ylm_ci range (~5000), not ytot_ci range (~50000)
    assert (panel["mean_ylm_nr"] < 15000).all(), "mean_ylm_nr appears to use ytot_ci instead of ylm_ci"


# ---------------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------------

def test_correlations_returns_dataframe(synthetic_waves):
    panel = build_area_panel(synthetic_waves)
    corr = run_correlations(panel)
    assert isinstance(corr, pd.DataFrame)
    assert "pearson_r" in corr.columns
    assert "spearman_r" in corr.columns


def test_correlations_pooled_present(synthetic_waves):
    panel = build_area_panel(synthetic_waves)
    corr = run_correlations(panel)
    assert "pooled" in corr["subset"].values


def test_correlations_positive_with_spillover(synthetic_waves):
    """With built-in positive spillover, pooled Pearson ρ should be > 0."""
    panel = build_area_panel(synthetic_waves)
    corr = run_correlations(panel)
    pooled_r = corr.loc[corr["subset"] == "pooled", "pearson_r"].iloc[0]
    assert pooled_r > 0, f"Expected positive correlation, got {pooled_r}"


# ---------------------------------------------------------------------------
# First-differences regression
# ---------------------------------------------------------------------------

def test_fd_n_obs(synthetic_waves):
    """FD regression should have exactly n_areas obs per pair."""
    panel = build_area_panel(synthetic_waves)
    fd = run_fd_regression(panel, wave_pairs=[("2018m6", "2019m6")])
    assert len(fd) == 1
    assert fd.iloc[0]["n_depts"] == 3


def test_fd_sign_positive_with_spillover(synthetic_waves):
    """β should be positive when synthetic data has spillover."""
    panel = build_area_panel(synthetic_waves)
    fd = run_fd_regression(panel, wave_pairs=[("2018m6", "2019m6")])
    assert len(fd) == 1
    assert fd.iloc[0]["sign_positive"], f"Expected β > 0, got β={fd.iloc[0]['beta']}"


def test_fd_missing_wave_skipped(synthetic_waves):
    """If one wave of a pair is missing, that pair is skipped without error."""
    panel = build_area_panel({"2018m6": synthetic_waves["2018m6"]})   # only one wave
    fd = run_fd_regression(panel, wave_pairs=[("2018m6", "2019m6")])
    assert len(fd) == 0


def test_fd_beta_columns_present(synthetic_waves):
    """Result DataFrame must have beta, se, ci_lo_boot, ci_hi_boot columns."""
    panel = build_area_panel(synthetic_waves)
    fd = run_fd_regression(panel, wave_pairs=[("2018m6", "2019m6")])
    for col in ["beta", "se", "ci_lo_boot", "ci_hi_boot"]:
        assert col in fd.columns, f"Missing column: {col}"


def test_fd_bootstrap_ci_straddles_beta(synthetic_waves):
    """ci_lo ≤ β ≤ ci_hi."""
    panel = build_area_panel(synthetic_waves)
    fd = run_fd_regression(panel, wave_pairs=[("2018m6", "2019m6")])
    row = fd.iloc[0]
    assert row["ci_lo_boot"] <= row["beta"] <= row["ci_hi_boot"]


# ---------------------------------------------------------------------------
# Smoke test with real data (requires 2023m6 BID.dta)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not (HND_DIR / "HND_2023m6_BID.dta").exists(),
    reason="HND_2023m6_BID.dta not found — run Stata scripts first"
)
def test_real_data_dept_count():
    """Area panel from real 2023m6 data has ≤ 18 depts and positive N."""
    import pyreadstat
    df, _ = pyreadstat.read_dta(str(HND_DIR / "HND_2023m6_BID.dta"), encoding="latin1")
    df.columns = [c.lower() for c in df.columns]
    df["_wave"] = "2023m6"
    panel = build_area_panel({"2023m6": df})
    assert len(panel) > 0, "area panel is empty"
    assert len(panel) <= 18, f"Expected ≤ 18 geo units, got {len(panel)}"
    assert (panel["n_hh"] > 0).all(), "Some areas have zero HHs"
