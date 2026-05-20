"""
build_dom_trends.py  --  DOM trend charts for Jeremy's Caribbean branch
========================================================================
Generates single-panel trend PNGs for the Dominican Republic (DOM).
DOM has 7 waves (2018t4-2024t4): enough for a meaningful trend series.
Uses migrante_ci (Native / Migrant) disaggregation and Inter font.

Indicators:
  trend_dom_participation.png
  trend_dom_unemployment.png
  trend_dom_inactivity.png
  trend_dom_formality.png
  trend_dom_higher_edu.png

Output: out/jeremy/2026-05-13/
"""

import os, pickle
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.font_manager as fm
from matplotlib.patches import Patch
from pathlib import Path

# ---------------------------------------------------------------------------
# Font -- Inter
# ---------------------------------------------------------------------------
INTER_PATH = r"C:\Windows\Fonts\Inter.ttc"
if os.path.exists(INTER_PATH):
    fm.fontManager.addfont(INTER_PATH)
    plt.rcParams["font.family"] = "Inter"

# ---------------------------------------------------------------------------
# Paths & config
# ---------------------------------------------------------------------------
BASE = Path(__file__).parent.parent
CACHE_FILE = BASE / "bases armo" / "armo" / "_hdmf_cache.pkl"
DATE_TAG   = "2026-05-13"
OUT_DIR    = BASE / "out" / "jeremy" / DATE_TAG
OUT_DIR.mkdir(parents=True, exist_ok=True)

COUNTRY = "DOM"
LABEL   = "Dominican Republic"

C_NAVY      = "#1D3557"
C_SLATE     = "#6B7C93"
TREND_C_MIG = "#C0392B"
TREND_C_NAT = "#1A5276"

DPI = 150

# ---------------------------------------------------------------------------
# Load cache
# ---------------------------------------------------------------------------
print("Loading cache ...")
with open(CACHE_FILE, "rb") as fh:
    _cache = pickle.load(fh)
_data = _cache["data"]
print(f"  {len(_data):,} rows loaded")

dom_periods = sorted(_data[_data["pais_c"] == COUNTRY]["periodo_c"].dropna().unique())
print(f"  DOM periods: {dom_periods}")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _period_to_float(period: str) -> float:
    yr = int(period[:4])
    if "t" in period:
        q = int(period[5:])
        return yr + (q - 1) / 4 + 0.125
    elif "m" in period:
        m = int(period[5:])
        return yr + (m - 1) / 12 + 1 / 24
    else:
        return yr + 0.5


def _wavg_se(series, weights):
    y = pd.to_numeric(series, errors="coerce").to_numpy(float)
    w = pd.to_numeric(weights, errors="coerce").to_numpy(float)
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0)
    if mask.sum() == 0:
        return np.nan, np.nan
    y, w = y[mask], w[mask]
    W = w.sum()
    p = float(np.dot(y, w) / W)
    var_p = float(np.dot(w ** 2, (y - p) ** 2)) / (W ** 2)
    return p, float(np.sqrt(var_p))


def _strip_spines(ax):
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(length=0)


# ---------------------------------------------------------------------------
# Build trend series
# ---------------------------------------------------------------------------
def _build_trend_series(ind_key: str, value_col: str, denom_group: str):
    dfc = _data[
        (_data["pais_c"] == COUNTRY) &
        (_data["migrante_ci"].isin(["Native", "Migrant"]))
    ].copy()

    if value_col == "formal_ci":
        dfc["_yval"] = 1 - pd.to_numeric(dfc[value_col], errors="coerce")
        dfc.loc[dfc[value_col].isna(), "_yval"] = np.nan
    elif value_col == "higher_edu_ci":
        dfc["_yval"] = (pd.to_numeric(dfc["edu_hdmf"], errors="coerce") >= 7).astype(float)
        dfc.loc[dfc["edu_hdmf"].isna(), "_yval"] = np.nan
    else:
        dfc["_yval"] = pd.to_numeric(dfc.get(value_col, pd.Series(dtype=float)),
                                     errors="coerce")

    rows = []
    for period in dfc["periodo_c"].dropna().unique():
        dfp = dfc[dfc["periodo_c"] == period]
        for grp in ["Native", "Migrant"]:
            g = dfp[dfp["migrante_ci"] == grp]
            if denom_group == "wapc":
                sub = g[g["edad_ci"].between(16, 64)]
            elif denom_group == "peac":
                sub = g[g["edad_ci"].between(16, 64) & (g["pea_ci"] == 1)]
            elif denom_group == "empc":
                sub = g[g["emp_ci"] == 1]
            else:
                sub = g
            p, se = _wavg_se(sub["_yval"], sub["factor_ci"])
            if np.isnan(p):
                continue
            rows.append({
                "x":      _period_to_float(period),
                "period": period,
                "group":  grp,
                "p":      p * 100,
                "ci_lo":  max(0.0, (p - 1.96 * se) * 100),
                "ci_hi":  min(100.0, (p + 1.96 * se) * 100),
            })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("x")


# ---------------------------------------------------------------------------
# Legend handles
# ---------------------------------------------------------------------------
def _legend_handles():
    return [
        mlines.Line2D([], [], color=TREND_C_MIG, linewidth=2, marker="o",
                      markersize=7, markeredgecolor="white", label="Migrant"),
        mlines.Line2D([], [], color=TREND_C_NAT, linewidth=2, marker="o",
                      markersize=7, markeredgecolor="white", label="Native"),
        Patch(color=TREND_C_MIG, alpha=0.18, label="95% CI -- Migrant"),
        Patch(color=TREND_C_NAT, alpha=0.18, label="95% CI -- Native"),
    ]


# ---------------------------------------------------------------------------
# Generate single-panel chart
# ---------------------------------------------------------------------------
def plot_dom_trend(ind_key: str, value_col: str, denom_group: str,
                   title: str, filename: str, y_max: float = 100):
    ts = _build_trend_series(ind_key, value_col, denom_group)

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fig.subplots_adjust(bottom=0.18)

    if ts.empty:
        ax.text(0.5, 0.5, "no data", ha="center", va="center",
                transform=ax.transAxes, color=C_SLATE, fontsize=12)
        ax.axis("off")
    else:
        ax.set_facecolor("#FAFBFC")
        _strip_spines(ax)
        ax.yaxis.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", zorder=0)
        ax.set_axisbelow(True)

        for grp, color in [("Migrant", TREND_C_MIG), ("Native", TREND_C_NAT)]:
            sub = ts[ts["group"] == grp].sort_values("x")
            if sub.empty:
                continue
            ax.fill_between(sub["x"], sub["ci_lo"], sub["ci_hi"],
                            color=color, alpha=0.12, zorder=1)
            ax.plot(sub["x"], sub["p"],
                    color=color, linewidth=2.0, zorder=3,
                    marker="o", markersize=6, markeredgecolor="white",
                    markeredgewidth=0.8, label=grp)

        all_x = ts["x"].values
        year_ints = sorted(set(int(x) for x in all_x))
        ax.set_xticks(year_ints)
        ax.set_xticklabels([str(y) for y in year_ints], fontsize=10, rotation=45, ha="right")
        ax.tick_params(axis="y", labelsize=10)
        ax.set_xlim(min(all_x) - 0.3, max(all_x) + 0.3)
        ax.set_ylim(0, y_max)
        ax.set_title(LABEL, fontsize=12, fontweight="bold", color=C_NAVY, pad=8)

    fig.legend(handles=_legend_handles(), loc="lower center",
               bbox_to_anchor=(0.5, -0.01), ncol=4, frameon=False,
               fontsize=10, handlelength=2.0, columnspacing=2.5)

    fig.suptitle(title, fontsize=14, fontweight="bold", color=C_NAVY, y=1.01)
    fig.tight_layout(rect=[0, 0.06, 1, 1])

    path = OUT_DIR / filename
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
CHARTS = [
    ("participation", "pea_ci",       "wapc",  "Participation Rate (%) -- Dominican Republic, Working-Age Pop. (16-64)", "trend_dom_participation.png", 100),
    ("unemployment",  "desemp_ci",    "peac",  "Unemployment Rate (%) -- Dominican Republic, Active Pop. (16-64)",       "trend_dom_unemployment.png",   40),
    ("inactivity",    "inactivo_ci",  "wapc",  "Inactivity Rate (%) -- Dominican Republic, Working-Age Pop. (16-64)",    "trend_dom_inactivity.png",    100),
    ("formality",     "formal_ci",    "empc",  "Informality Rate (%) -- Dominican Republic, Employed Pop.",              "trend_dom_formality.png",     100),
    ("higher_edu",    "higher_edu_ci","wapc",  "Tertiary Education Rate (%) -- Dominican Republic, WAP (16-64)",         "trend_dom_higher_edu.png",     70),
]

print(f"\nGenerating {len(CHARTS)} DOM trend charts -> {OUT_DIR}\n")
for ind_key, value_col, denom, title, fname, ymax in CHARTS:
    print(f"  {fname} ...")
    plot_dom_trend(ind_key, value_col, denom, title, fname, y_max=ymax)


# ---------------------------------------------------------------------------
# 2×2 grid — 4 labor trend indicators
# ---------------------------------------------------------------------------
def _plot_panel(ax, ts, y_max, panel_title):
    """Draw one trend panel on the given Axes (mirrors plot_dom_trend styling)."""
    if ts.empty:
        ax.text(0.5, 0.5, "no data", ha="center", va="center",
                transform=ax.transAxes, color=C_SLATE, fontsize=10)
        ax.axis("off")
        ax.set_title(panel_title, fontsize=11, fontweight="bold", color=C_NAVY, pad=6)
        return

    ax.set_facecolor("#FAFBFC")
    _strip_spines(ax)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", zorder=0)
    ax.set_axisbelow(True)

    for grp, color in [("Migrant", TREND_C_MIG), ("Native", TREND_C_NAT)]:
        sub = ts[ts["group"] == grp].sort_values("x")
        if sub.empty:
            continue
        ax.fill_between(sub["x"], sub["ci_lo"], sub["ci_hi"],
                        color=color, alpha=0.12, zorder=1)
        ax.plot(sub["x"], sub["p"],
                color=color, linewidth=2.0, zorder=3,
                marker="o", markersize=6, markeredgecolor="white",
                markeredgewidth=0.8)

    all_x = ts["x"].values
    year_ints = sorted(set(int(x) for x in all_x))
    ax.set_xticks(year_ints)
    ax.set_xticklabels([str(y) for y in year_ints], fontsize=9, rotation=45, ha="right")
    ax.tick_params(axis="y", labelsize=9)
    ax.set_xlim(min(all_x) - 0.3, max(all_x) + 0.3)
    ax.set_ylim(0, y_max)
    ax.set_title(panel_title, fontsize=11, fontweight="bold", color=C_NAVY, pad=6)


GRID_CHARTS = [
    ("participation", "pea_ci",      "wapc", "Participation Rate (%)",  100),
    ("unemployment",  "desemp_ci",   "peac", "Unemployment Rate (%)",    40),
    ("inactivity",    "inactivo_ci", "wapc", "Inactivity Rate (%)",     100),
    ("formality",     "formal_ci",   "empc", "Informality Rate (%)",    100),
]


def plot_dom_trend_grid():
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(f"Dominican Republic — Labor Market Trends (2018–2024)\nNative vs. Migrant",
                 fontsize=14, fontweight="bold", color=C_NAVY, y=1.01)

    for idx, (ind_key, value_col, denom, panel_title, y_max) in enumerate(GRID_CHARTS):
        ax  = axes[idx // 2][idx % 2]
        ts  = _build_trend_series(ind_key, value_col, denom)
        _plot_panel(ax, ts, y_max, panel_title)

    fig.legend(handles=_legend_handles(), loc="lower center",
               bbox_to_anchor=(0.5, -0.02), ncol=4, frameon=False,
               fontsize=10, handlelength=2.0, columnspacing=2.5)

    fig.tight_layout(rect=[0, 0.06, 1, 1])
    path = OUT_DIR / "trend_dom_labor_grid.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


print("\n  trend_dom_labor_grid.png ...")
plot_dom_trend_grid()

print("\nDone.")
