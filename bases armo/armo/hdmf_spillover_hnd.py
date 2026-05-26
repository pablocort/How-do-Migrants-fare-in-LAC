"""
HND Remittances Spillover Analysis
===================================
Tests whether remittance inflows have local spending spillover effects:
do non-receiving households in high-remittance departments earn more?

Pipeline:
  load_waves()         → load all HND BID.dta files
  build_area_panel()   → dept × wave panel of remittance intensity + non-receiver income
  run_correlations()   → Pearson/Spearman ρ per wave and pooled
  run_fd_regression()  → first-differences regression Δincome ~ Δremit_intensity
  plot_all()           → exports figures to out/remittances/figures/

Usage:
  python "bases armo/armo/hdmf_spillover_hnd.py"
"""

import os
import glob
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats

warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]  # project root
HND_DIR = Path(__file__).parent / "HND"
OUT_DIR = ROOT / "out" / "remittances"
FIGS_DIR = OUT_DIR / "figures"
TABS_DIR = OUT_DIR / "tables"

# Exchange rates USD→HNL used per wave (for IV instrument)
EXCHANGE_RATES = {
    "2018m6": 23.68,
    "2019m6": 24.08,
    "2021m6": 24.50,
    "2022m6": None,   # no OIH module
    "2023m6": 24.7285,
    "2024m6": 25.12562814,
    "2025m7": 26.00,
}

# Waves to skip (no remittances data)
SKIP_WAVES = {"2022m6"}

# Geography variable name per wave (after harmonization)
# 2021/2022/2023 only have dominio (5-category) — use as fallback
GEO_VAR = {
    "2018m6": "region_c",   # department 1–18
    "2019m6": "region_c",
    "2021m6": "dominio",    # urban/rural 5 bins — fallback
    "2023m6": "dominio",    # fallback
    "2024m6": "region_c",
    "2025m7": "region_c",
}

# Waves where geo_var is department-level (18 units) vs. dominio (5 units)
DEPT_WAVES = {"2018m6", "2019m6", "2024m6", "2025m7"}


# ---------------------------------------------------------------------------
# 1. Load waves
# ---------------------------------------------------------------------------

def load_waves(hnd_dir: Path = HND_DIR) -> dict[str, pd.DataFrame]:
    """
    Load all HND_*_BID.dta files.  Returns dict keyed by period string.
    Skips waves in SKIP_WAVES.
    """
    pattern = str(hnd_dir / "HND_*_BID.dta")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No BID.dta files found in {hnd_dir}")

    waves = {}
    for fpath in files:
        period = Path(fpath).stem.replace("HND_", "").replace("_BID", "")
        if period in SKIP_WAVES:
            print(f"  skip {period} (no remittances module)")
            continue
        df, meta = pyreadstat.read_dta(fpath)
        df.columns = [c.lower() for c in df.columns]
        df["_wave"] = period
        waves[period] = df
        print(f"  loaded {period}: {len(df):,} obs, {df.columns.tolist().count('remesas_ch')} remesas_ch col")

    return waves


# ---------------------------------------------------------------------------
# 2. Build area-level panel
# ---------------------------------------------------------------------------

def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights > 0)
    if mask.sum() == 0:
        return np.nan
    w = weights[mask]
    v = values[mask]
    return float(np.average(v, weights=w))


def _weighted_share(flag: pd.Series, weights: pd.Series) -> float:
    """Weighted share of flag == 1 among non-missing observations."""
    mask = flag.notna() & weights.notna() & (weights > 0)
    if mask.sum() == 0:
        return np.nan
    w = weights[mask]
    f = flag[mask].astype(float)
    return float(np.average(f, weights=w))


def build_area_panel(waves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    For each wave × geographic unit compute:
      pct_remit    — weighted share of HHs with remesas_ch > 0
      avg_remit    — weighted mean of remesas_ch (all HHs, zeros included)
      mean_ylm_nr  — weighted mean of ylm_ci for NON-receiving HHs only
      med_ylm_nr   — median ylm_ci for non-receiving HHs (unweighted approximation)
      n_hh         — total HHs in area
      n_nonrecv    — non-receiving HHs in area

    One row per (wave, geo_unit).
    """
    records = []

    for period, df in waves.items():
        # --- identify variables ---
        geo_col = GEO_VAR.get(period)
        weight_col = "factor_ch" if "factor_ch" in df.columns else "factor_ci"

        if geo_col not in df.columns:
            print(f"  {period}: geo var '{geo_col}' not found — skipping")
            continue
        if "remesas_ch" not in df.columns:
            print(f"  {period}: remesas_ch missing — skipping")
            continue

        # --- collapse to household level (one row per HH) ---
        hh_cols = [geo_col, weight_col, "remesas_ch", "idh_ch"]
        indiv_cols = ["ylm_ci", "idh_ch"]
        available = [c for c in hh_cols + ["ylm_ci"] if c in df.columns]
        dfw = df[available].copy()

        # household-level income: use head of household if available
        # otherwise average ylm_ci across members per HH
        if "relacion_ci" in df.columns:
            head = df[df["relacion_ci"] == 1][["idh_ch", "ylm_ci"]].rename(columns={"ylm_ci": "ylm_head"})
            dfw = dfw.merge(head, on="idh_ch", how="left")
            ylm_col = "ylm_head"
        else:
            ylm_col = "ylm_ci"

        # deduplicate to one row per HH
        hh_df = dfw.drop_duplicates(subset="idh_ch")

        # --- remit flag ---
        hh_df = hh_df.copy()
        hh_df["remit_hh"] = np.where(
            hh_df["remesas_ch"].isna(), np.nan,
            (hh_df["remesas_ch"] > 0).astype(float)
        )

        # --- aggregate by area ---
        for area_val, grp in hh_df.groupby(geo_col, dropna=True):
            w = grp[weight_col] if weight_col in grp.columns else pd.Series(np.ones(len(grp)), index=grp.index)

            pct_remit = _weighted_share(grp["remit_hh"], w)
            avg_remit = _weighted_mean(grp["remesas_ch"].fillna(0), w)

            nonrecv = grp[grp["remit_hh"] == 0]
            w_nr = w.loc[nonrecv.index] if weight_col in grp.columns else pd.Series(np.ones(len(nonrecv)), index=nonrecv.index)

            if ylm_col in nonrecv.columns:
                mean_ylm_nr = _weighted_mean(nonrecv[ylm_col], w_nr)
            else:
                mean_ylm_nr = np.nan

            records.append({
                "wave": period,
                "geo_type": "dept" if period in DEPT_WAVES else "dominio",
                "geo_unit": area_val,
                "pct_remit": pct_remit,
                "avg_remit": avg_remit,
                "mean_ylm_nr": mean_ylm_nr,
                "n_hh": len(grp),
                "n_nonrecv": len(nonrecv),
                "xr": EXCHANGE_RATES.get(period),
            })

    if not records:
        return pd.DataFrame(columns=["wave", "geo_type", "geo_unit", "pct_remit",
                                     "avg_remit", "mean_ylm_nr", "n_hh", "n_nonrecv", "xr"])
    panel = pd.DataFrame(records)
    panel.sort_values(["wave", "geo_unit"], inplace=True)
    panel.reset_index(drop=True, inplace=True)
    return panel


# ---------------------------------------------------------------------------
# 3. Correlations
# ---------------------------------------------------------------------------

def run_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    """
    For each wave (and pooled), compute Pearson and Spearman ρ between
    pct_remit and mean_ylm_nr.  Returns a summary DataFrame.
    """
    rows = []
    subsets = {w: panel[panel["wave"] == w] for w in panel["wave"].unique()}
    subsets["pooled"] = panel

    for label, sub in subsets.items():
        clean = sub[["pct_remit", "mean_ylm_nr"]].dropna()
        n = len(clean)
        if n < 3:
            continue
        pr, pp = stats.pearsonr(clean["pct_remit"], clean["mean_ylm_nr"])
        sr, sp = stats.spearmanr(clean["pct_remit"], clean["mean_ylm_nr"])
        rows.append({
            "subset": label,
            "n": n,
            "pearson_r": round(pr, 3),
            "pearson_p": round(pp, 3),
            "spearman_r": round(sr, 3),
            "spearman_p": round(sp, 3),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. First-differences regression
# ---------------------------------------------------------------------------

def run_fd_regression(panel: pd.DataFrame, wave_pairs: list[tuple] | None = None) -> pd.DataFrame:
    """
    For each consecutive wave pair, compute first-differences at dept level:
      Δmean_ylm_nr = α + β·Δpct_remit + ε

    Returns DataFrame with one row per wave pair: β, SE (OLS), bootstrap CI.
    Only uses dept-level waves (not dominio).
    """
    if wave_pairs is None:
        wave_pairs = [("2018m6", "2019m6"), ("2024m6", "2025m7")]

    dept_panel = panel[panel["geo_type"] == "dept"].copy()
    results = []

    for w0, w1 in wave_pairs:
        p0 = dept_panel[dept_panel["wave"] == w0][["geo_unit", "pct_remit", "mean_ylm_nr", "xr"]].copy()
        p1 = dept_panel[dept_panel["wave"] == w1][["geo_unit", "pct_remit", "mean_ylm_nr", "xr"]].copy()

        if p0.empty or p1.empty:
            print(f"  FD: {w0}→{w1} skipped (missing wave data)")
            continue

        merged = p0.merge(p1, on="geo_unit", suffixes=("_0", "_1"))
        merged["d_pct_remit"] = merged["pct_remit_1"] - merged["pct_remit_0"]
        merged["d_ylm_nr"] = merged["mean_ylm_nr_1"] - merged["mean_ylm_nr_0"]
        merged["bartik_z"] = merged["pct_remit_0"] * (merged["xr_1"] - merged["xr_0"])

        clean = merged[["d_pct_remit", "d_ylm_nr", "bartik_z"]].dropna()
        n = len(clean)
        if n < 3:
            print(f"  FD: {w0}→{w1} skipped (n={n} after dropna)")
            continue

        # OLS: d_ylm_nr = β * d_pct_remit
        x = clean["d_pct_remit"].values
        y = clean["d_ylm_nr"].values
        beta = float(np.cov(x, y)[0, 1] / np.var(x)) if np.var(x) > 0 else np.nan
        resid = y - beta * x
        se = float(np.std(resid) / (np.std(x) * np.sqrt(n))) if np.std(x) > 0 else np.nan

        # Bootstrap 95% CI (1000 draws)
        rng = np.random.default_rng(42)
        boots = []
        for _ in range(1000):
            idx = rng.integers(0, n, size=n)
            xb, yb = x[idx], y[idx]
            if np.var(xb) > 0:
                boots.append(np.cov(xb, yb)[0, 1] / np.var(xb))
        ci_lo, ci_hi = (np.nanpercentile(boots, 2.5), np.nanpercentile(boots, 97.5)) if boots else (np.nan, np.nan)

        results.append({
            "pair": f"{w0}→{w1}",
            "n_depts": n,
            "beta": round(beta, 2) if not np.isnan(beta) else np.nan,
            "se": round(se, 2) if not np.isnan(se) else np.nan,
            "ci_lo_boot": round(ci_lo, 2),
            "ci_hi_boot": round(ci_hi, 2),
            "sign_positive": beta > 0 if not np.isnan(beta) else None,
        })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# 5. Plots
# ---------------------------------------------------------------------------

def _scatter_remit_vs_income(panel: pd.DataFrame, wave: str, ax: plt.Axes):
    sub = panel[(panel["wave"] == wave)].dropna(subset=["pct_remit", "mean_ylm_nr"])
    if sub.empty:
        ax.set_title(f"{wave} — no data")
        return
    size = np.clip(sub["n_hh"] / sub["n_hh"].max() * 300, 20, 300)
    ax.scatter(sub["pct_remit"] * 100, sub["mean_ylm_nr"], s=size, alpha=0.7, edgecolors="white", linewidths=0.5)
    if len(sub) >= 3:
        m, b, r, p, _ = stats.linregress(sub["pct_remit"], sub["mean_ylm_nr"])
        xs = np.linspace(sub["pct_remit"].min(), sub["pct_remit"].max(), 100)
        ax.plot(xs * 100, m * xs + b, "r--", linewidth=1.2, label=f"ρ={stats.pearsonr(sub['pct_remit'], sub['mean_ylm_nr'])[0]:.2f}")
        ax.legend(fontsize=8)
    for _, row in sub.iterrows():
        ax.annotate(str(int(row["geo_unit"])), (row["pct_remit"] * 100, row["mean_ylm_nr"]), fontsize=6, alpha=0.6)
    ax.set_xlabel("% HHs receiving remittances", fontsize=9)
    ax.set_ylabel("Mean labor income, non-receivers (HNL/month)", fontsize=9)
    ax.set_title(f"HND {wave}", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))


def plot_all(panel: pd.DataFrame, fd_results: pd.DataFrame, corr_results: pd.DataFrame):
    FIGS_DIR.mkdir(parents=True, exist_ok=True)
    TABS_DIR.mkdir(parents=True, exist_ok=True)

    # --- scatter grid (one panel per wave) ---
    dept_waves = sorted(panel[panel["geo_type"] == "dept"]["wave"].unique())
    ncols = min(3, len(dept_waves))
    nrows = -(-len(dept_waves) // ncols)   # ceiling division
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    axes = np.array(axes).flatten()
    for i, w in enumerate(dept_waves):
        _scatter_remit_vs_income(panel, w, axes[i])
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    fig.suptitle("Remittance intensity vs. non-receiver labor income\n(by department, Honduras EPHPM)", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIGS_DIR / "scatter_remit_intensity_vs_income.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved scatter figure")

    # --- FD regression bar chart ---
    if not fd_results.empty:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        x = np.arange(len(fd_results))
        colors = ["steelblue" if s else "firebrick" for s in fd_results["sign_positive"].fillna(False)]
        ax2.bar(x, fd_results["beta"], color=colors, alpha=0.8)
        ax2.errorbar(x,
                     fd_results["beta"],
                     yerr=[fd_results["beta"] - fd_results["ci_lo_boot"],
                           fd_results["ci_hi_boot"] - fd_results["beta"]],
                     fmt="none", color="black", capsize=5)
        ax2.axhline(0, color="black", linewidth=0.8)
        ax2.set_xticks(x)
        ax2.set_xticklabels(fd_results["pair"], fontsize=9)
        ax2.set_ylabel("β  (Δ non-receiver income / Δ % receiving remittances)", fontsize=9)
        ax2.set_title("First-differences regression: spillover effect\n(HNL per 1pp increase in local remittance share)", fontsize=10)
        fig2.tight_layout()
        fig2.savefig(FIGS_DIR / "fd_regression_results.png", dpi=150, bbox_inches="tight")
        plt.close(fig2)
        print(f"  saved FD regression figure")

    # --- save tables ---
    panel.to_csv(OUT_DIR / "hnd_area_panel.csv", index=False)
    corr_results.to_excel(TABS_DIR / "correlation_table.xlsx", index=False)
    fd_results.to_excel(TABS_DIR / "fd_regression_results.xlsx", index=False)
    print(f"  saved tables to {TABS_DIR}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== HND Spillover Analysis ===")
    print(f"Loading waves from {HND_DIR}")
    waves = load_waves()

    print("\nBuilding area panel...")
    panel = build_area_panel(waves)
    print(f"  {len(panel)} rows ({panel['wave'].nunique()} waves × {panel['geo_unit'].nunique()} geo units)")

    print("\nRunning correlations...")
    corr = run_correlations(panel)
    print(corr.to_string(index=False))

    print("\nRunning first-differences regression...")
    fd = run_fd_regression(panel)
    if not fd.empty:
        print(fd.to_string(index=False))
    else:
        print("  No FD pairs available yet (check 2024/2025 BID.dta fixes)")

    print("\nGenerating plots and tables...")
    plot_all(panel, fd, corr)

    print(f"\nDone. Outputs in {OUT_DIR}")


if __name__ == "__main__":
    main()
