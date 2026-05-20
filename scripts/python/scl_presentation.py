#!/usr/bin/env python3
"""
scl_presentation.py
Generates all charts and the LaTeX Beamer file for the SCL full presentation.

Usage:
    py scl_presentation.py               # generate charts + LaTeX
    py scl_presentation.py --no-latex    # charts only

Output:  out/scl_full/YYYY-MM-DD/
"""

import argparse
import os
import sys
from datetime import date

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Inter", "Arial", "DejaVu Sans"]
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATE_TAG   = date.today().strftime("%Y-%m-%d")
OUT_DIR    = os.path.join(BASE_DIR, "out", "scl_full", DATE_TAG)
CACHE_FILE = os.path.join(BASE_DIR, "bases armo", "armo", "_hdmf_cache.pkl")

# ── Academic-executive colour palette ─────────────────────────────────────────
C_NAVY    = "#1D3557"   # midnight navy — Native, headings, anchor color
C_TEAL    = "#2171A0"   # steel blue — primary accent, Venezuelan survey bars
C_VEN     = "#B84A2A"   # burnt sienna — Venezuelan highlight (warm, distinct)
C_VEN_E   = "#E8A07A"   # light terracotta — Venezuelan early-wave
C_NAT_E   = "#7DAEC9"   # light steel blue — Native early-wave
C_SLATE   = "#6B7C93"   # slate gray — secondary / captions
C_PANEL   = "#EAF0F5"   # very light blue-gray — panel backgrounds
C_RED     = "#B84A2A"   # burnt sienna — age 65+ / accent (same hue as C_VEN)
C_AMBER   = "#C9742A"   # muted amber — age 0-14, primary education
C_GRAY    = "#6B7C93"   # caption / footnote gray

# Population-chart source colours
C_SURVEY  = "#2171A0"   # steel blue (template primary)
C_UNDESA  = "#1D3557"   # midnight navy
C_ADMIN   = "#2E7D5E"   # dark teal-green — administrative records (SISMIGRA)

FIGSIZE_WIDE = (12, 5)
FIGSIZE_STD  = (11, 5)
DPI          = 150

# =============================================================================
# POPULATION COVERAGE DATA
# Sources: household surveys (factor_ci sums), R4V, UNDESA IMS 2020/2024
# UNDESA ESP: undesa_pd_2024_ims_stock_by_sex_destination_and_origin_v2.xlsx
#   Spain + Venezuela (Bolivarian Republic of): y2024=602,539 / y2020=398,098
# R4V: covers LAC only — not available for Spain
# =============================================================================

# Columns: (country, wave_recent, wave_early,
#           survey_recent, r4v_recent, undesa_recent,
#           survey_early,  r4v_early,  undesa_early)
# np.nan = not available
# R4V source: Plataforma R4V "Cifras Mundiales" (r4v.info), Feb 2026 publication.
# USA: US Census Bureau via R4V; BRA: Federal Police via R4V; ESP: UNDESA via R4V.

POPULATION_DATA = [
    # ctry   wave_r      wave_e     surv_r      r4v_r       unes_r      surv_e     r4v_e     unes_e
    ("COL", "2025t3",  "2018t3", 2_069_798, 2_800_000, 2_904_873, 1_230_258, 1_032_016, 1_780_486),
    ("PER", "2024a",   "2018a",    188_083, 1_600_000, 1_596_667,    30_091,   506_000,   941_889),
    ("USA", "ACS 2024", None,      730_000,   987_600,   np.nan,    np.nan,    np.nan,    np.nan),
    ("BRA", "R4V 2024", None,      np.nan,    761_300,   np.nan,    np.nan,    np.nan,    np.nan),
    ("CHL", "2024a",   "2017a",    741_208,   669_400,   427_821,   180_057,   102_000,   523_553),
    ("ESP", "2025a",   "2018a",    753_859,   602_500,   602_539,   222_239,   np.nan,    398_098),
    ("ECU", "2025m12", "2018m12",  130_649,   440_400,   487_871,   100_542,   221_000,   388_861),
]

# Survey names per country (for source footnote)
SURVEY_NAMES = {
    "COL": "GEIH",
    "PER": "ENAHO",
    "CHL": "CASEN",
    "ECU": "ENEMDU",
    "ESP": "EPA",
    "USA": "ACS",
    "BRA": "SISMIGRA",
}

COUNTRY_ORDER = ["COL", "PER", "USA", "BRA", "CHL", "ESP", "ECU"]

# Full names for population chart x-axis labels
COUNTRY_FULL_POP = {
    "COL": "Colombia",
    "PER": "Peru",
    "CHL": "Chile",
    "ECU": "Ecuador",
    "ESP": "Spain",
    "USA": "United States",
    "BRA": "Brazil",
}

# Administrative-records counts (for population coverage chart only).
# Source: SISMIGRA 2025 (Brazil Federal Police), Sheet1 of brazil_datos.xlsx — total row.
ADMIN_RECORDS_DATA = {
    "BRA": 761_833,   # SISMIGRA (Federal Police of Brazil), Jan–Dec 2025
    "ECU": 192_000,   # Administrative records, Ecuador
}

# Survey upscale factors for countries with large household-survey undercoverage.
# Scale = R4V_total / survey_total.  Applied to ABSOLUTE bar heights only;
# percentage dots (shares within the distribution) are unaffected.
SURVEY_UPSCALE = {
    "PER": round(1_600_000 / 188_083, 3),  # 8.507 — ENAHO 2024 captures ~188k vs R4V 1.6M
    "ECU": round(  440_400 / 130_649, 3),  # 3.371 — ENEMDU 2025m12 Venezuelan-born captures ~131k vs R4V 440k
}

# R4V/UNDESA weights for pooled indicator aggregation.
# Built from POPULATION_DATA col 4 (r4v_recent); falls back to col 5 (undesa_recent).
# Only for the 5 analysis countries (DB_COUNTRIES); "last year available" = recent wave.
# Defined here so it can be read at a glance alongside the raw figures.
COUNTRY_R4V_WEIGHTS = {
    "COL": 2_800_000,   # R4V (Migracion Colombia, Feb 2026)
    "PER": 1_600_000,   # R4V (SUNAMI, Feb 2026)
    "CHL":   669_400,   # R4V (INE Census 2024, May 2025)
    "ECU":   440_400,   # R4V (MoG, May 2025)
    "ESP":   602_500,   # UNDESA IMS 2024 (via R4V Cifras Mundiales, May 2025)
}

# =============================================================================
# SHARED STYLE HELPER
# =============================================================================

def _strip_spines(ax):
    """Remove all four frame spines from an axes."""
    for sp in ax.spines.values():
        sp.set_visible(False)


# =============================================================================
# CHART 1 — Population Coverage
# =============================================================================

def plot_population_coverage(out_dir: str) -> str:
    """
    Grouped bar chart: R4V + Household Survey + Administrative Records per country.
    Bars sorted descending by R4V value.
    Third bar type (Administrative Records, green) shown only for BRA (SISMIGRA).
    """
    sorted_data = sorted(
        POPULATION_DATA,
        key=lambda row: -(row[4] if not (isinstance(row[4], float) and np.isnan(row[4])) else 0),
    )

    n_countries = len(sorted_data)
    x_idx = np.arange(n_countries)

    # Three source types: (label, colour, col_idx_or_None, admin_dict_or_None)
    # Col 4 = r4v_recent; Col 3 = survey_recent
    sources = [
        ("R4V",                    C_UNDESA, 4,    None),
        ("Household Survey",       C_SURVEY, 3,    None),
        ("Administrative Records", C_ADMIN,  None, ADMIN_RECORDS_DATA),
    ]
    n_src   = len(sources)
    width   = 0.25
    offsets = np.linspace(-(n_src - 1) * width / 2, (n_src - 1) * width / 2, n_src)

    fig, ax = plt.subplots(figsize=(15, 5.5))

    # Determine y-axis range from all available values
    all_vals = []
    for row in sorted_data:
        for col in (3, 4):
            v = row[col]
            if not (isinstance(v, float) and np.isnan(v)):
                all_vals.append(v)
        admin_v = ADMIN_RECORDS_DATA.get(row[0])
        if admin_v:
            all_vals.append(admin_v)
    y_max = max(all_vals) * 1.28
    ax.set_ylim(0, y_max)
    lbl_offset = y_max * 0.022

    import re as _re
    def _wave_year(wave):
        m = _re.search(r"\d{4}", str(wave))
        return m.group(0) if m else str(wave)

    for s_i, (label, color, r_col, admin_dict) in enumerate(sources):
        offs = offsets[s_i]
        for xi, row in zip(x_idx + offs, sorted_data):
            val = admin_dict.get(row[0]) if admin_dict is not None else row[r_col]
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            ax.bar(xi, val, width=width, color=color, alpha=0.88, zorder=3)
            ax.text(xi, val + lbl_offset, _fmt_pop(val),
                    ha="center", va="bottom", fontsize=8,
                    color="black", fontweight="bold")

    ax.set_xticks(x_idx)
    ax.set_xticklabels(
        [f"{COUNTRY_FULL_POP.get(row[0], row[0])}\n({_wave_year(row[1])})" for row in sorted_data],
        fontsize=10,
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_pop(v)))
    ax.set_ylabel("Venezuelan-born population", fontsize=11)
    ax.set_title(
        "Venezuelan Migrants: Population Estimates by Source",
        fontsize=12, pad=10,
    )
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    _strip_spines(ax)

    source_handles = [
        Patch(facecolor=c, alpha=0.88, label=lbl)
        for lbl, c, _, _ in sources
    ]
    fig.legend(
        handles=source_handles,
        loc="lower center", bbox_to_anchor=(0.5, 0.02),
        ncol=3, frameon=False, fontsize=10,
    )

    fig.tight_layout(rect=[0, 0.10, 1, 1])

    path = os.path.join(out_dir, "population_coverage.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


import pickle
import seaborn as sns
from functools import reduce
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

# Countries included in the two new slides (LAC-4 + Spain)
LAC5 = ["COL", "PER", "CHL", "ECU", "ESP"]
COUNTRY_FULL = {
    "COL": "Colombia", "PER": "Peru", "CHL": "Chile",
    "ECU": "Ecuador",  "ESP": "Spain",
}

# =============================================================================
# SHARED: load cache and prepare most-recent data for LAC5
# =============================================================================

_cache_df = None   # module-level cache so we load once
_ven_df   = None   # Venezuelan-only cache (all ages, most-recent wave)

def _load_cache() -> pd.DataFrame:
    global _cache_df
    if _cache_df is None:
        with open(CACHE_FILE, "rb") as fh:
            raw = pickle.load(fh)
        df = raw["data"]
        df = df[df["pais_c"].isin(LAC5)].copy()
        # Keep Native vs Venezuelan migrants only
        df = df[df["migrante_ci"].isin(["Native", "Migrant"])].copy()
        df["group"] = df["migrante_ci"].map({"Native": "Native", "Migrant": "Venezuelan"})
        # Most recent period per country
        most_recent = (
            df.groupby("pais_c")["periodo_c"]
            .apply(lambda s: sorted(s.dropna().unique())[-1])
            .to_dict()
        )
        keep = pd.Series(False, index=df.index)
        for country, period in most_recent.items():
            keep |= (df["pais_c"] == country) & (df["periodo_c"] == period)
        df = df[keep].copy()
        df["_period"] = df["pais_c"].map(most_recent)
        _cache_df = df
    return _cache_df


def _load_venezuelan() -> pd.DataFrame:
    """Venezuelan-born only, ALL ages, most-recent wave per country."""
    global _ven_df
    if _ven_df is None:
        with open(CACHE_FILE, "rb") as fh:
            raw = pickle.load(fh)
        df = raw["data"]
        df = df[df["pais_c"].isin(LAC5)].copy()
        # Identify Venezuelan migrants
        if "foreign_born" in df.columns:
            df = df[df["foreign_born"] == "Venezuela"].copy()
        else:
            df = df[df["migrante_ci"] == "Migrant"].copy()
        # Most recent wave per country (across all ages)
        most_recent = (
            df.groupby("pais_c")["periodo_c"]
            .apply(lambda s: sorted(s.dropna().unique())[-1])
            .to_dict()
        )
        keep = pd.Series(False, index=df.index)
        for country, period in most_recent.items():
            keep |= (df["pais_c"] == country) & (df["periodo_c"] == period)
        df = df[keep].copy()
        df["_period"] = df["pais_c"].map(most_recent)
        _ven_df = df
    return _ven_df


def _period_year(period: str) -> str:
    """Extract 4-digit year from a period code (e.g. '2025t3' → '2025', '2024m12' → '2024')."""
    import re as _re
    m = _re.search(r"\d{4}", str(period))
    return m.group(0) if m else str(period)


def _x_label(country: str, df: pd.DataFrame) -> str:
    period = df.loc[df["pais_c"] == country, "_period"].iloc[0]
    return f"{COUNTRY_FULL[country]}\n({_period_year(period)})"


# =============================================================================
# CHART 2 — Age Distribution
# =============================================================================

AGE3_ORDER  = ["0-14", "15-64", "65+"]
AGE3_COLORS = {
    "0-14":  C_AMBER,   # amber/orange
    "15-64": C_TEAL,    # template primary teal
    "65+":   C_RED,     # red
}


def _age3(age: float) -> str:
    if age < 15:  return "0-14"
    if age <= 64: return "15-64"
    return "65+"


def plot_age_distribution(out_dir: str) -> str:
    """Dual-axis chart: stacked absolute bars (left) + % of 15-64 dot (right).
    Venezuelan migrants only.  Age groups: 0–14 / 15–64 / 65+.
    Includes LAC5 survey data (from cache), Brazil (SISMIGRA 2025), and USA (ACS 2024).
    Countries sorted descending by total Venezuelan population."""
    df = _load_venezuelan()
    df = df[df["edad_ci"].notna()].copy()
    df["age3"] = df["edad_ci"].apply(_age3)

    # ── Build unified entries list ─────────────────────────────────────────────
    # Each entry: dict with label, source, age_data (thousands), total, pct_1564
    entries = []

    for c in LAC5:
        if c not in df["pais_c"].unique():
            continue
        cdf    = df[df["pais_c"] == c]
        period = cdf["_period"].iloc[0]
        label  = f"{COUNTRY_FULL.get(c, c)}\n({_period_year(period)})"
        scale  = SURVEY_UPSCALE.get(c, 1.0)
        age_data = {
            cat: cdf.loc[cdf["age3"] == cat, "factor_ci"].sum() / 1_000 * scale
            for cat in AGE3_ORDER
        }
        total = sum(age_data.values())
        # pct_1564 is scale-invariant (scale cancels in numerator/denominator)
        pct   = age_data["15-64"] / total * 100 if total > 0 else np.nan
        entries.append({"code": c, "label": label, "source": "survey",
                        "age_data": age_data, "total": total, "pct_1564": pct})

    # External: Brazil — SISMIGRA 2025 (known ages only; 217k obs. with unknown age excluded)
    # Raw groups: 0-15: 151,018 | 15-25: 130,666 | 25-40: 145,155 | 40-65: 99,184 | 65+: 18,769
    _bra_age = {"0-14": 151.018, "15-64": 375.005, "65+": 18.769}
    _bra_tot = sum(_bra_age.values())   # 544,792 known-age obs.
    _bra_missing_k = round(ADMIN_RECORDS_DATA["BRA"] / 1_000 - _bra_tot, 3)  # ~217k unknown age
    entries.append({
        "code":     "BRA",
        "label":    "Brazil*\n(2025)",
        "source":   "admin",
        "age_data": _bra_age,
        "total":    _bra_tot,
        "pct_1564": _bra_age["15-64"] / _bra_tot * 100,
    })

    # External: United States — ACS 2024 (bpld='venezuela', weighted by perwt)
    # Pre-computed: 0-14: 80,213 | 15-24: 88,285 | 25-39: 213,034 | 40-64: 284,233 | 65+: 63,193
    _usa_age = {"0-14": 80.213, "15-64": 585.552, "65+": 63.193}
    _usa_tot = sum(_usa_age.values())
    entries.append({
        "code":     "USA",
        "label":    "United States\n(2024)",
        "source":   "survey",
        "age_data": _usa_age,
        "total":    _usa_tot,
        "pct_1564": _usa_age["15-64"] / _usa_tot * 100,
    })

    # Order by COUNTRY_ORDER (same as population_coverage chart: R4V descending)
    _rank = {c: i for i, c in enumerate(COUNTRY_ORDER)}
    entries.sort(key=lambda e: _rank.get(e["code"], 99))

    n     = len(entries)
    x_pos = np.arange(n)
    bar_w = 0.55

    fig, ax1 = plt.subplots(figsize=(max(13, n * 2.0), 6))
    ax2 = ax1.twinx()

    C_MISSING = "#BBBBBB"   # light gray for unknown-age segment

    bottoms   = np.zeros(n)
    seg_15_64 = []

    for cat in AGE3_ORDER:
        heights = np.array([e["age_data"][cat] for e in entries])
        for xi, e, h, b in zip(x_pos, entries, heights, bottoms):
            ax1.bar(xi, h, bar_w, bottom=b,
                    color=AGE3_COLORS[cat], zorder=3,
                    edgecolor="white", linewidth=0.8)
        if cat == "15-64":
            seg_15_64 = list(zip(x_pos, heights, bottoms))
        bottoms = bottoms + heights

    # Missing-age bar on top of BRA stacked bars
    _bra_idx = next((i for i, e in enumerate(entries) if e["code"] == "BRA"), None)
    if _bra_idx is not None:
        ax1.bar(_bra_idx, _bra_missing_k, bar_w, bottom=bottoms[_bra_idx],
                color=C_MISSING, zorder=3, edgecolor="white", linewidth=0.8)
        bottoms[_bra_idx] += _bra_missing_k

    bar_tops  = bottoms.copy()
    pct_15_64 = [e["pct_1564"] for e in entries]

    # Calibrate left axis so every dot clears its own bar
    valid_ratios = [
        bar_tops[i] / (pct_15_64[i] / 100)
        for i in range(n)
        if not np.isnan(pct_15_64[i]) and pct_15_64[i] > 0
    ]
    ax1_max = max(valid_ratios) * 1.18
    ax1.set_ylim(0, ax1_max)
    ax2.set_ylim(0, 100)

    # Number label inside 15-64 segment
    for xi, h, b in seg_15_64:
        if h > 0:
            ax1.text(xi, b + h / 2, f"{h:,.0f}",
                     ha="center", va="center", fontsize=11,
                     color="white", fontweight="bold")

    # Right-axis dots
    ax2.scatter(x_pos, pct_15_64, color=C_NAVY, s=100, zorder=6,
                marker="o", edgecolors="white", linewidths=1.5)
    for xi, pct in zip(x_pos, pct_15_64):
        if not np.isnan(pct):
            ax2.text(xi, pct + 2.5, f"{pct:.0f}%",
                     ha="center", va="bottom", fontsize=9,
                     color=C_NAVY, fontweight="bold")

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([e["label"] for e in entries], fontsize=11)
    ax1.set_ylabel("Venezuelans (thousands)", fontsize=12)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax1.yaxis.grid(True, linestyle="--", alpha=0.35)
    ax1.set_axisbelow(True)
    ax1.set_title("Age Composition of Venezuelan Migrants — most recent wave",
                  fontsize=13, fontweight="bold", pad=12)

    ax2.set_ylabel("Share aged 15–64 among Venezuelans (%)", fontsize=11, color=C_NAVY)
    ax2.tick_params(axis="y", labelcolor=C_NAVY)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    _strip_spines(ax1)
    _strip_spines(ax2)

    age_handles   = [Patch(facecolor=AGE3_COLORS[c], label=c) for c in reversed(AGE3_ORDER)]
    dot_handle    = Line2D([0], [0], marker="o", color="w",
                           markerfacecolor=C_NAVY, markeredgecolor="white", markersize=9,
                           label="% aged 15–64 (right axis)")
    missing_handle = Patch(facecolor=C_MISSING, label="Unknown age (BRA*)")

    fig.legend(handles=age_handles + [dot_handle, missing_handle],
               loc="lower center", bbox_to_anchor=(0.5, 0.0),
               ncol=5, frameon=False, fontsize=10)

    fig.tight_layout(rect=[0, 0.09, 1, 1])

    path = os.path.join(out_dir, "age_distribution.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# =============================================================================
# CHART 3 — Education Distribution (LAC-4 + Spain)
# =============================================================================

EDU_3CAT_MAP = {
    1: "Primary or less", 2: "Primary or less", 3: "Primary or less",
    4: "Secondary",       5: "Secondary",       6: "Secondary",
    7: "Higher education",8: "Higher education",
}
EDU_3CAT_ORDER = ["Primary or less", "Secondary", "Higher education"]
EDU_COLORS = {
    "Primary or less":  C_AMBER,   # amber — template
    "Secondary":        C_TEAL,    # teal — template primary
    "Higher education": C_NAVY,    # dark navy — template
}


def plot_education_distribution(out_dir: str) -> str:
    """Stacked absolute bars (thousands) + floating dot above each bar showing % tertiary.
    Venezuelan working-age migrants only (15–64).
    Includes LAC5 survey data (from cache), USA (ACS 2024, external).
    Peru and Ecuador bars scaled by SURVEY_UPSCALE to approximate R4V totals (proportions unchanged).
    Countries sorted descending by total working-age Venezuelan population."""
    df = _load_venezuelan()
    df = df[df["edu_hdmf"].notna() & df["edad_ci"].notna()].copy()
    df = df[(df["edad_ci"] >= 15) & (df["edad_ci"] <= 64)].copy()
    df["edu_3cat"] = df["edu_hdmf"].astype(int).map(EDU_3CAT_MAP)
    df = df[df["edu_3cat"].notna()].copy()

    # ── Build unified entries list ─────────────────────────────────────────────
    entries = []

    for c in LAC5:
        if c not in df["pais_c"].unique():
            continue
        cdf    = df[df["pais_c"] == c]
        period = cdf["_period"].iloc[0]
        label  = f"{COUNTRY_FULL.get(c, c)}\n({_period_year(period)})"
        scale  = SURVEY_UPSCALE.get(c, 1.0)
        edu_data = {
            cat: cdf.loc[cdf["edu_3cat"] == cat, "factor_ci"].sum() / 1_000 * scale
            for cat in EDU_3CAT_ORDER
        }
        total    = sum(edu_data.values())
        # pct_higher is scale-invariant (scale cancels in ratio)
        pct_high = edu_data["Higher education"] / total * 100 if total > 0 else np.nan
        entries.append({"code": c, "label": label, "source": "survey",
                        "edu_data": edu_data, "total": total, "pct_higher": pct_high})

    # External: United States — ACS 2024, working-age (15–64) Venezuelan-born (bpld='venezuela')
    # educ mapping: ≤ grade 8 → Primary; grades 9–12 → Secondary; any college → Higher
    # Pre-computed perwt sums: Primary 23,792 | Secondary 179,034 | Higher 382,726
    _usa_edu = {
        "Primary or less":  23.792,
        "Secondary":       179.034,
        "Higher education": 382.726,
    }
    _usa_tot = sum(_usa_edu.values())   # 585,552
    entries.append({
        "code":       "USA",
        "label":      "United States\n(2024)",
        "source":     "survey",
        "edu_data":   _usa_edu,
        "total":      _usa_tot,
        "pct_higher": _usa_edu["Higher education"] / _usa_tot * 100,
    })

    # External: Brazil — CAGED/RAIS 2025 (formal employment), OBMigra
    # Source: BID_Venezuelanos.xlsx > "Data for chart", column 2025
    # Primary or less : Sem educ./fund.incompleto (27908) + Fund.completo (20355)
    # Secondary       : Médio incompleto (15693) + Médio completo (119305)
    # Higher education: Superior incompleto (3272) + Superior completo (15441)
    _bra_edu = {
        "Primary or less":  (27_908 + 20_355) / 1_000,
        "Secondary":        (15_693 + 119_305) / 1_000,
        "Higher education": (3_272  + 15_441)  / 1_000,
    }
    _bra_edu_tot = sum(_bra_edu.values())
    entries.append({
        "code":       "BRA",
        "label":      "Brazil*\n(2025)",
        "source":     "admin",
        "edu_data":   _bra_edu,
        "total":      _bra_edu_tot,
        "pct_higher": _bra_edu["Higher education"] / _bra_edu_tot * 100,
    })

    # Order by COUNTRY_ORDER (same as population_coverage chart: R4V descending)
    _rank = {c: i for i, c in enumerate(COUNTRY_ORDER)}
    entries.sort(key=lambda e: _rank.get(e["code"], 99))

    n     = len(entries)
    x_pos = np.arange(n)
    bar_w = 0.55

    fig, ax = plt.subplots(figsize=(max(13, n * 2.0), 6.5))
    ax2 = ax.twinx()

    bottoms      = np.zeros(n)
    seg_higher   = []
    seg_secondary = []

    for cat in EDU_3CAT_ORDER:
        heights = np.array([e["edu_data"][cat] for e in entries])
        for xi, e, h, b in zip(x_pos, entries, heights, bottoms):
            ax.bar(xi, h, bar_w, bottom=b,
                   color=EDU_COLORS[cat], zorder=3,
                   edgecolor="white", linewidth=0.8)
        if cat == "Secondary":
            seg_secondary = list(zip(x_pos, heights, bottoms))
        if cat == "Higher education":
            seg_higher = list(zip(x_pos, heights, bottoms))
        bottoms = bottoms + heights

    bar_tops = bottoms.copy()
    max_bar  = max(bar_tops) if len(bar_tops) > 0 else 1
    pct_higher = [e["pct_higher"] for e in entries]

    # Number label inside Secondary segment
    for xi, h, b in seg_secondary:
        if h > max_bar * 0.04:
            ax.text(xi, b + h / 2, f"{h:,.0f}",
                    ha="center", va="center", fontsize=10,
                    color="white", fontweight="bold")

    # Number label inside Higher education segment
    for xi, h, b in seg_higher:
        if h > max_bar * 0.04:
            ax.text(xi, b + h / 2, f"{h:,.0f}",
                    ha="center", va="center", fontsize=10,
                    color="white", fontweight="bold")

    ax2.set_ylim(0, 100)
    ax2.scatter(x_pos, pct_higher, color=C_NAVY, s=110, zorder=6,
                marker="o", edgecolors="white", linewidths=1.5)
    for xi, pct in zip(x_pos, pct_higher):
        if not np.isnan(pct):
            ax2.text(xi, pct + 3, f"{pct:.0f}%",
                     ha="center", va="bottom", fontsize=9,
                     color=C_NAVY, fontweight="bold")
    ax2.set_ylabel("% with higher education (right axis)", fontsize=11, color=C_NAVY)
    ax2.tick_params(axis="y", labelcolor=C_NAVY)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))

    ax.set_xticks(x_pos)
    ax.set_xticklabels([e["label"] for e in entries], fontsize=11)
    ax.set_ylabel("Venezuelans aged 15–64 (thousands)", fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylim(0, max_bar * 1.20)
    ax.yaxis.grid(True, linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    ax.set_title(
        "Education Level of Venezuelan Migrants (Working-Age, 15–64) — most recent wave",
        fontsize=13, fontweight="bold", pad=12,
    )
    _strip_spines(ax)
    _strip_spines(ax2)

    edu_handles = [Patch(facecolor=EDU_COLORS[c], label=c) for c in reversed(EDU_3CAT_ORDER)]
    dot_handle  = Line2D([0], [0], marker="o", color="w",
                         markerfacecolor=C_NAVY, markeredgecolor="white", markersize=9,
                         label="% with higher education (right axis)")
    fig.legend(handles=edu_handles + [dot_handle],
               loc="lower center", bbox_to_anchor=(0.5, 0.0),
               ncol=4, frameon=False, fontsize=10)

    fig.tight_layout(rect=[0, 0.09, 1, 1])

    path = os.path.join(out_dir, "education_distribution.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# =============================================================================
# DUMBBELL (SLIDE 7-STYLE) INDICATOR CHARTS
# =============================================================================

DB_COUNTRIES = ["COL", "PER", "CHL", "ECU", "ESP"]
DB_COUNTRY_LBL = {
    "COL": "Colombia", "PER": "Peru", "CHL": "Chile",
    "ECU": "Ecuador",  "ESP": "Spain",
}
DB_RECENT_WAVES = {"COL": "2025t3", "PER": "2024a", "CHL": "2024a", "ECU": "2025m12", "ESP": "2025a"}
DB_EARLY_WAVES  = {"COL": "2018t3", "PER": "2018a", "CHL": "2017a", "ECU": "2018m12", "ESP": "2018a"}
DB_RECENT_LBL   = "2024–25"
DB_EARLY_LBL    = "2017–18"

DB_C_VEN       = C_VEN       # Venezuelan recent bar (burnt sienna)
DB_C_NAT       = C_NAVY      # Native recent bar (midnight navy)
DB_C_VEN_EARLY = C_VEN_E     # Venezuelan early marker (light terracotta)
DB_C_NAT_EARLY = C_NAT_E     # Native early marker (light steel blue)
DB_MARKER_VEN  = "D"         # diamond
DB_MARKER_NAT  = "s"         # square
DB_MARKER_S    = 60
DB_BAR_H       = 0.30

# Indicators with known harmonization gaps for Spain — mask as NaN
ESP_MASKED = {"informality", "unemployment"}

INDICATORS_A = [
    ("working_age",   "Working age (15–64)\n% of pop."),
    ("participation", "Participation rate\n% of 16–64"),
    ("tertiary",      "Tertiary education\n% of 16–64"),
]
INDICATORS_B1 = [
    ("unemployment",  "Unemployment\n% of active pop."),
    ("inactivity",    "Inactivity\n% of 16–64"),
    ("informality",   "Informality\n% of employed"),
]
INDICATORS_B2 = [
    ("parttime",      "Part-time\n% of employed"),
    ("long_hours",    "Long hours (50+)\n% of employed"),
]
INDICATORS_B = INDICATORS_B1 + INDICATORS_B2   # kept for Excel export


def _wavg(v_series, w_series):
    v = pd.to_numeric(v_series, errors="coerce").to_numpy(float)
    w = pd.to_numeric(w_series, errors="coerce").to_numpy(float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    return float(np.average(v[mask], weights=w[mask])) if mask.sum() > 0 else np.nan


_db_cache = None

def _get_dumbbell_data():
    global _db_cache
    if _db_cache is not None:
        return _db_cache
    with open(CACHE_FILE, "rb") as fh:
        raw = pickle.load(fh)
    df = raw["data"]
    df = df[df["pais_c"].isin(DB_COUNTRIES) & df["foreign_born"].isin(["Venezuela", "Native"])].copy()
    df["higher_edu_ci"] = (pd.to_numeric(df["edu_hdmf"], errors="coerce") >= 7).astype(float)
    df.loc[df["edu_hdmf"].isna(), "higher_edu_ci"] = np.nan
    df["longhours_ci"] = (pd.to_numeric(df["horastot_ci"], errors="coerce") > 50).astype(float)
    df.loc[df["horastot_ci"].isna(), "longhours_ci"] = np.nan

    results = {}
    for period_label, wave_map in [("recent", DB_RECENT_WAVES), ("early", DB_EARLY_WAVES)]:
        masks = [(df["pais_c"] == c) & (df["periodo_c"] == p) for c, p in wave_map.items()]
        df_p  = df[reduce(lambda a, b: a | b, masks)].copy()
        res_p = {}
        for country in DB_COUNTRIES:
            dfc  = df_p[df_p["pais_c"] == country]
            wapc = dfc[dfc["edad_ci"].between(16, 64)]
            peac = wapc[wapc["pea_ci"] == 1]
            empc = dfc[dfc["emp_ci"] == 1]
            wa15 = dfc[dfc["edad_ci"].between(15, 64)]
            res_c = {}
            for grp in ["Venezuela", "Native"]:
                g_all = dfc[dfc["foreign_born"] == grp]
                g_wa  = wapc[wapc["foreign_born"] == grp]
                g_pea = peac[peac["foreign_born"] == grp]
                g_emp = empc[empc["foreign_born"] == grp]
                g_15  = wa15[wa15["foreign_born"] == grp]
                tot_w = g_all["factor_ci"].sum()
                res_c[grp] = {
                    "working_age":   (g_15["factor_ci"].sum() / tot_w * 100) if tot_w > 0 else np.nan,
                    "participation": _wavg(g_wa["pea_ci"],        g_wa["factor_ci"]) * 100,
                    "tertiary":      _wavg(g_wa["higher_edu_ci"], g_wa["factor_ci"]) * 100,
                    "unemployment":  _wavg(g_pea["desemp_ci"],    g_pea["factor_ci"]) * 100,
                    "inactivity":    _wavg(g_wa["inactivo_ci"],   g_wa["factor_ci"]) * 100,
                    "informality":   (1 - _wavg(g_emp["formal_ci"],  g_emp["factor_ci"])) * 100,
                    "parttime":      _wavg(g_emp["parcial_ci"],   g_emp["factor_ci"]) * 100,
                    "long_hours":    _wavg(g_emp["longhours_ci"], g_emp["factor_ci"]) * 100,
                }
            res_p[country] = res_c
        results[period_label] = res_p
    # Mask Spain indicators with known harmonization gaps
    for period in ("recent", "early"):
        for grp in ("Venezuela", "Native"):
            for ind_key in ESP_MASKED:
                results[period]["ESP"][grp][ind_key] = np.nan

    _db_cache = results
    return results


def _draw_bar_panel(ax, results, ind_key, show_yticks=True):
    """Horizontal bar (recent) + marker (early) panel for one indicator."""
    country_order = DB_COUNTRIES
    y_idx = {c: i for i, c in enumerate(reversed(country_order))}
    all_vals = []

    SPECS = [
        # group,       y_off,  bar_color,  early_color,       marker
        ("Venezuela",  0.17,   DB_C_VEN,   DB_C_VEN_EARLY,    DB_MARKER_VEN),
        ("Native",    -0.17,   DB_C_NAT,   DB_C_NAT_EARLY,    DB_MARKER_NAT),
    ]

    for country in country_order:
        y = y_idx[country]
        if y % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="#F5F5F5", zorder=0, linewidth=0)

        for grp, y_off, c_bar, c_early, mkr in SPECS:
            y_row   = y + y_off
            v_r     = results["recent"][country][grp][ind_key]
            v_e     = results["early"][country][grp][ind_key]

            # Bar — recent value
            if pd.notna(v_r):
                ax.barh(y_row, v_r, height=DB_BAR_H, color=c_bar,
                        edgecolor="none", zorder=3)
                all_vals.append(v_r)

            # Marker — early value
            if pd.notna(v_e):
                ax.scatter(v_e, y_row, marker=mkr, s=DB_MARKER_S,
                           color=c_early, edgecolors="white",
                           linewidths=0.6, zorder=5)
                all_vals.append(v_e)

    # Set xlim, then add bar-end labels with correct offset
    if all_vals:
        x_max = max(all_vals) * 1.45
        ax.set_xlim(0, x_max)
        label_pad = x_max * 0.015
        # Re-draw labels now that xlim is known
        for country in country_order:
            y = y_idx[country]
            for grp, y_off, c_bar, c_early, mkr in SPECS:
                y_row = y + y_off
                v_r   = results["recent"][country][grp][ind_key]
                if pd.notna(v_r):
                    ax.text(v_r + label_pad, y_row, f"{v_r:.1f}",
                            va="center", ha="left", fontsize=6.5,
                            fontweight="bold", color=c_bar)

    ax.set_yticks(list(y_idx.values()))
    if show_yticks:
        ax.set_yticklabels(
            [DB_COUNTRY_LBL[c] for c in reversed(country_order)], fontsize=9)
    else:
        ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(country_order) - 0.4)
    ax.xaxis.grid(True, linestyle="--", alpha=0.3, color="grey", zorder=0)
    ax.set_axisbelow(True)
    _strip_spines(ax)
    ax.tick_params(axis="x", labelsize=7.5)


def _plot_bar_multi(out_dir, results, indicators, filename, figsize):
    n = len(indicators)
    fig, axes = plt.subplots(1, n, figsize=figsize, sharey=True)
    if n == 1:
        axes = [axes]
    fig.subplots_adjust(wspace=0.08)

    for i, (ax, (ind_key, ind_title)) in enumerate(zip(axes, indicators)):
        _draw_bar_panel(ax, results, ind_key, show_yticks=(i == 0))
        ax.set_title(ind_title, fontsize=8.5, fontweight="bold", pad=8)

    leg_handles = [
        Patch(color=DB_C_VEN,       label=f"Venezuelan — {DB_RECENT_LBL}"),
        Patch(color=DB_C_NAT,       label=f"Native — {DB_RECENT_LBL}"),
        mlines.Line2D([], [], color=DB_C_VEN_EARLY, marker=DB_MARKER_VEN,
                      ls="None", ms=8, label=f"Venezuelan — {DB_EARLY_LBL}"),
        mlines.Line2D([], [], color=DB_C_NAT_EARLY, marker=DB_MARKER_NAT,
                      ls="None", ms=8, label=f"Native — {DB_EARLY_LBL}"),
    ]
    fig.legend(handles=leg_handles, loc="lower center", bbox_to_anchor=(0.5, 0.0),
               ncol=2, frameon=False, fontsize=8, handlelength=1.8,
               handletextpad=0.8, columnspacing=2.0)
    fig.tight_layout(rect=[0, 0.08, 1, 1])

    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


def plot_indicators_a(out_dir: str, results: dict) -> str:
    return _plot_bar_multi(out_dir, results, INDICATORS_A, "indicators_a.png", figsize=(13, 6.5))


def plot_indicators_b(out_dir: str, results: dict) -> str:
    return _plot_bar_multi(out_dir, results, INDICATORS_B, "indicators_b.png", figsize=(18, 6.5))


# =============================================================================
# POOLED INDICATOR CHARTS (slide 7 style — bars + markers, single chart)
# =============================================================================

POOLED_A = [
    ("working_age",   "Working age (15–64)\n(% of total pop.)"),
    ("participation", "Participation rate\n(% of working-age pop., 16–64)"),
    ("employment",    "Employment rate\n(% of working-age pop., 16–64)"),
    ("tertiary",      "Tertiary education\n(% of working-age pop., post-secondary+)"),
]

POOLED_B = [
    ("unemployment",  "Unemployment rate\n(% of active pop., LAC-4)"),
    ("inactivity",    "Inactivity rate\n(% of working-age pop.)"),
    ("informality",   "Informality\n(% of employed pop., LAC-4)"),
    ("parttime",      "Part-time work\n(% of employed pop.)"),
    ("long_hours",    "Long hours (50+)\n(% of employed pop.)"),
]

_pooled_cache = None


def _get_pooled_data():
    """Pooled statistics weighted by R4V/UNDESA country-level Venezuelan population.

    Approach: compute each indicator per country first (survey-weighted internally),
    then aggregate across countries using COUNTRY_R4V_WEIGHTS as country weights.
    This ensures Colombia (2.8M) contributes proportionally more than Ecuador (440k),
    reflecting actual diaspora composition — not sampling accidents.
    R4V/UNDESA weights from the most recent year available (see COUNTRY_R4V_WEIGHTS).
    """
    global _pooled_cache
    if _pooled_cache is not None:
        return _pooled_cache

    with open(CACHE_FILE, "rb") as fh:
        raw = pickle.load(fh)
    df = raw["data"]
    df = df[df["pais_c"].isin(DB_COUNTRIES) & df["foreign_born"].isin(["Venezuela", "Native"])].copy()
    df["higher_edu_ci"] = (pd.to_numeric(df["edu_hdmf"], errors="coerce") >= 7).astype(float)
    df.loc[df["edu_hdmf"].isna(), "higher_edu_ci"] = np.nan
    df["longhours_ci"] = (pd.to_numeric(df["horastot_ci"], errors="coerce") > 50).astype(float)
    df.loc[df["horastot_ci"].isna(), "longhours_ci"] = np.nan

    LAC4_RECENT = {c: p for c, p in DB_RECENT_WAVES.items() if c != "ESP"}
    LAC4_EARLY  = {c: p for c, p in DB_EARLY_WAVES.items()  if c != "ESP"}

    def _filter(wave_map):
        masks = [(df["pais_c"] == c) & (df["periodo_c"] == p) for c, p in wave_map.items()]
        return df[reduce(lambda a, b: a | b, masks)].copy()

    def _compute_one_country(dfc, grp):
        """Survey-weighted statistics for one country and one group."""
        wapc = dfc[dfc["edad_ci"].between(16, 64)]
        wa15 = dfc[dfc["edad_ci"].between(15, 64)]
        peac = wapc[wapc["pea_ci"] == 1]
        empc = dfc[dfc["emp_ci"] == 1]
        g_all = dfc[dfc["foreign_born"] == grp]
        g_wa  = wapc[wapc["foreign_born"] == grp]
        g_15  = wa15[wa15["foreign_born"] == grp]
        g_pea = peac[peac["foreign_born"] == grp]
        g_emp = empc[empc["foreign_born"] == grp]
        tot_w = g_all["factor_ci"].sum()
        return {
            "working_age":   g_15["factor_ci"].sum() / tot_w * 100 if tot_w > 0 else np.nan,
            "participation": _wavg(g_wa["pea_ci"],        g_wa["factor_ci"]) * 100,
            "employment":    _wavg(g_wa["emp_ci"],        g_wa["factor_ci"]) * 100,
            "tertiary":      _wavg(g_wa["higher_edu_ci"], g_wa["factor_ci"]) * 100,
            "unemployment":  _wavg(g_pea["desemp_ci"],    g_pea["factor_ci"]) * 100,
            "inactivity":    _wavg(g_wa["inactivo_ci"],   g_wa["factor_ci"]) * 100,
            "informality":   (1 - _wavg(g_emp["formal_ci"], g_emp["factor_ci"])) * 100,
            "parttime":      _wavg(g_emp["parcial_ci"],   g_emp["factor_ci"]) * 100,
            "long_hours":    _wavg(g_emp["longhours_ci"], g_emp["factor_ci"]) * 100,
        }

    def _r4v_pool(data, grp, wave_map, masked=None):
        """Compute per-country stats then aggregate with R4V/UNDESA country weights."""
        masked = masked or set()
        per_country = {c: _compute_one_country(data[data["pais_c"] == c], grp) for c in wave_map}
        ind_keys = list(next(iter(per_country.values())).keys())
        pooled = {}
        for ind_key in ind_keys:
            vals, wts = [], []
            for c in wave_map:
                v = per_country[c][ind_key]
                w = COUNTRY_R4V_WEIGHTS.get(c, 0)
                if ind_key in masked and c == "ESP":
                    w = 0
                if pd.notna(v) and w > 0:
                    vals.append(v)
                    wts.append(w)
            pooled[ind_key] = float(np.average(vals, weights=wts)) if vals else np.nan
        return pooled

    pooled = {}
    for period_lbl, w_all5, w_lac4 in [
        ("recent", DB_RECENT_WAVES, LAC4_RECENT),
        ("early",  DB_EARLY_WAVES,  LAC4_EARLY),
    ]:
        df_all5 = _filter(w_all5)
        df_lac4 = _filter(w_lac4)
        p = {}
        for grp in ["Venezuela", "Native"]:
            pool5 = _r4v_pool(df_all5, grp, w_all5)
            pool4 = _r4v_pool(df_lac4, grp, w_lac4, masked=ESP_MASKED)
            merged = {k: (pool4[k] if k in ESP_MASKED else pool5[k]) for k in pool5}
            p[grp] = merged
        pooled[period_lbl] = p

    _pooled_cache = pooled
    return pooled


_pooled_survey_cache = None


def _get_pooled_data_survey_only():
    """Pooled statistics using ONLY survey weights (factor_ci), no R4V country-level step.

    All survey respondents across countries are pooled together; each person contributes
    proportionally to their survey weight.  Colombia dominates because it has the most
    Venezuelan migrants in-sample.  Compare with _get_pooled_data() (R4V-weighted) to see
    how sensitive the LAC-5 aggregate is to the weighting choice.
    """
    global _pooled_survey_cache
    if _pooled_survey_cache is not None:
        return _pooled_survey_cache

    with open(CACHE_FILE, "rb") as fh:
        raw = pickle.load(fh)
    df = raw["data"]
    df = df[df["pais_c"].isin(DB_COUNTRIES) & df["foreign_born"].isin(["Venezuela", "Native"])].copy()
    df["higher_edu_ci"] = (pd.to_numeric(df["edu_hdmf"], errors="coerce") >= 7).astype(float)
    df.loc[df["edu_hdmf"].isna(), "higher_edu_ci"] = np.nan
    df["longhours_ci"] = (pd.to_numeric(df["horastot_ci"], errors="coerce") > 50).astype(float)
    df.loc[df["horastot_ci"].isna(), "longhours_ci"] = np.nan

    LAC4_RECENT = {c: p for c, p in DB_RECENT_WAVES.items() if c != "ESP"}
    LAC4_EARLY  = {c: p for c, p in DB_EARLY_WAVES.items()  if c != "ESP"}

    def _filter(wave_map):
        masks = [(df["pais_c"] == c) & (df["periodo_c"] == p) for c, p in wave_map.items()]
        return df[reduce(lambda a, b: a | b, masks)].copy()

    def _compute_survey_pool(dfc, grp):
        """Survey-weighted statistics for a pooled multi-country dataset (one group)."""
        g = dfc[dfc["foreign_born"] == grp]
        wapc = g[g["edad_ci"].between(16, 64)]
        wa15 = g[g["edad_ci"].between(15, 64)]
        peac = wapc[wapc["pea_ci"] == 1]
        empc = g[g["emp_ci"] == 1]
        tot_w = g["factor_ci"].sum()
        return {
            "working_age":   wa15["factor_ci"].sum() / tot_w * 100 if tot_w > 0 else np.nan,
            "participation": _wavg(wapc["pea_ci"],              wapc["factor_ci"]) * 100,
            "employment":    _wavg(wapc["emp_ci"],              wapc["factor_ci"]) * 100,
            "tertiary":      _wavg(wapc["higher_edu_ci"],       wapc["factor_ci"]) * 100,
            "unemployment":  _wavg(peac["desemp_ci"],           peac["factor_ci"]) * 100,
            "inactivity":    _wavg(wapc["inactivo_ci"],         wapc["factor_ci"]) * 100,
            "informality":   (1 - _wavg(empc["formal_ci"],      empc["factor_ci"])) * 100,
            "parttime":      _wavg(empc["parcial_ci"],          empc["factor_ci"]) * 100,
            "long_hours":    _wavg(empc["longhours_ci"],        empc["factor_ci"]) * 100,
        }

    pooled = {}
    for period_lbl, w_all5, w_lac4 in [
        ("recent", DB_RECENT_WAVES, LAC4_RECENT),
        ("early",  DB_EARLY_WAVES,  LAC4_EARLY),
    ]:
        df_all5 = _filter(w_all5)
        df_lac4 = _filter(w_lac4)
        p = {}
        for grp in ["Venezuela", "Native"]:
            pool5 = _compute_survey_pool(df_all5, grp)
            pool4 = _compute_survey_pool(df_lac4, grp)
            # For ESP-masked indicators use LAC-4 (no ESP), same logic as R4V version
            merged = {k: (pool4[k] if k in ESP_MASKED else pool5[k]) for k in pool5}
            p[grp] = merged
        pooled[period_lbl] = p

    _pooled_survey_cache = pooled
    return pooled


def _plot_pooled(out_dir, results, indicators_def, filename, figsize):
    """Horizontal bar + marker chart matching the existing LAC-4 pooled slide."""
    _CV_R = "#C0392B"   # vivid crimson — Venezuelan recent
    _CN_R = "#1A5276"   # deep navy — Native recent
    _CV_E = "#F1948A"   # light red — Venezuelan early
    _CN_E = "#7FB3D3"   # light navy blue — Native early
    MKR_VEN = "D"
    MKR_NAT = "s"
    MKR_S   = 300
    LABEL_PAD  = 0.9
    LABEL_ZONE = 6.0
    bar_h  = 0.55
    gap    = 0.80

    ind_keys   = [k for k, _ in indicators_def]
    ind_labels = [lbl for _, lbl in indicators_def]
    n_ind      = len(ind_keys)

    y_pos     = {}
    y_mid     = []
    current_y = 0.0
    for ind_key in reversed(ind_keys):
        y_ven = current_y + bar_h
        y_nat = current_y
        y_pos[(ind_key, "Venezuela")] = y_ven + bar_h / 2
        y_pos[(ind_key, "Native")]    = y_nat + bar_h / 2
        y_mid.insert(0, (y_nat + y_ven + bar_h) / 2)
        current_y += 2 * bar_h + gap

    fig, ax = plt.subplots(figsize=figsize)

    all_vals = []
    for ind_key, _ in indicators_def:
        for grp in ["Venezuela", "Native"]:
            for period in ("recent", "early"):
                v = results[period][grp][ind_key]
                if pd.notna(v):
                    all_vals.append(v)

    for ind_key, _ in indicators_def:
        for grp, c_bar, c_mkr, mkr in [
            ("Venezuela", _CV_R, _CV_E, MKR_VEN),
            ("Native",    _CN_R, _CN_E, MKR_NAT),
        ]:
            val_r = results["recent"][grp][ind_key]
            val_e = results["early"][grp][ind_key]
            y     = y_pos[(ind_key, grp)]

            if pd.notna(val_r):
                ax.barh(y, val_r, height=bar_h, color=c_bar, edgecolor="none", zorder=3)
                ax.text(val_r / 2, y, f"{val_r:.1f}",
                        va="center", ha="center", fontsize=23, fontweight="bold",
                        color="white", zorder=4)

            if pd.notna(val_e):
                ax.scatter(val_e, y, marker=mkr, s=MKR_S,
                           color=c_mkr, edgecolors="white", linewidths=1.5, zorder=5)

    ax.set_yticks(y_mid)
    ax.set_yticklabels(ind_labels, fontsize=22, ha="right", va="center", linespacing=1.4)
    ax.tick_params(axis="y", length=0, pad=16)
    ax.tick_params(axis="x", labelsize=20)

    if all_vals:
        ax.set_xlim(0, max(all_vals) * 1.28)
    ax.xaxis.grid(True, linestyle="--", alpha=0.30, color="grey", zorder=0)
    ax.set_axisbelow(True)
    _strip_spines(ax)

    leg_handles = [
        mpatches.Patch(color=_CV_R, label=f"Venezuelan — Recent ({DB_RECENT_LBL})"),
        mpatches.Patch(color=_CN_R, label=f"Native — Recent ({DB_RECENT_LBL})"),
        mlines.Line2D([], [], color=_CV_E, marker=MKR_VEN, linestyle="None",
                      markersize=16, label=f"Venezuelan — Early ({DB_EARLY_LBL})"),
        mlines.Line2D([], [], color=_CN_E, marker=MKR_NAT, linestyle="None",
                      markersize=16, label=f"Native — Early ({DB_EARLY_LBL})"),
    ]
    # Legend outside the plot area, centred below the axes
    ax.legend(handles=leg_handles,
              loc="upper center", bbox_to_anchor=(0.5, -0.04),
              frameon=False, fontsize=20, ncol=2,
              handlelength=2.0, handletextpad=1.0, columnspacing=2.0)

    fig.tight_layout(rect=[0, 0.10, 1, 1])
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


def plot_pooled_a(out_dir: str, results: dict) -> str:
    total_h = len(POOLED_A) * (2 * 0.55 + 0.80)
    return _plot_pooled(out_dir, results, POOLED_A, "pooled_a.png",
                        figsize=(24, max(10, total_h * 1.4)))


def plot_pooled_b(out_dir: str, results: dict) -> str:
    total_h = len(POOLED_B) * (2 * 0.55 + 0.80)
    return _plot_pooled(out_dir, results, POOLED_B, "pooled_b.png",
                        figsize=(24, max(10, total_h * 1.4)))


def _fmt_pop(v: float) -> str:
    """Format population as compact string: 2.9M, 547K, etc."""
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return f"{v:.0f}"


# =============================================================================
# ANNEX — Country-level dumbbell slides (dot-and-line style)
# =============================================================================

DB_C_VEN_ANN   = "#C0392B"   # vivid crimson — Venezuelan
DB_C_NAT_ANN   = "#1A5276"   # deep navy — Native
DB_C_GAP_ANN   = "#999999"   # gap connector line
DB_Y_OFF_R     =  0.19       # recent sub-row offset
DB_Y_OFF_E     = -0.19       # early sub-row offset
DB_LABEL_V     =  0.12       # vertical label offset (stacked labels)
DB_LABEL_H     =  1.0        # horizontal label offset (inline)
# gap below this → labels go left/right of cluster instead of above/below dots
# indicator-aware: text spans ~6 pp at xlim=100, ~2 pp at xlim=25 (unemployment)
# ── SAVED CONFIG ── DB_MIN_GAP_INL = 4.0 (old fixed threshold); xlim = dynamic max*1.40
DB_MIN_GAP_INL_DEFAULT = 6.0   # regular indicators (xlim=100)
DB_MIN_GAP_INL_UNEMP   = 2.0   # unemployment (xlim=25)
# fixed x-axis limits per indicator type (saved: None → dynamic max*1.40)
DB_XLIM_DEFAULT    = 100
DB_XLIM_UNEMP      =  25
# (ind_key, country) pairs forced to endpoint labels regardless of gap size
_DB_FORCE_ENDPOINT = {
    ("working_age",   "COL"), ("participation", "COL"), ("tertiary",      "COL"),
    ("participation", "PER"), ("participation", "ESP"),
    ("inactivity",    "COL"), ("inactivity",    "PER"), ("inactivity",    "ESP"),
    ("parttime",      "COL"), ("parttime",      "ESP"),
    ("long_hours",    "COL"), ("long_hours",    "CHL"),
    ("long_hours",    "ECU"), ("long_hours",    "ESP"),
}


def _dumbbell_panel(ax, results, ind_key, countries_rev, first_panel=False):
    """Draw one dumbbell panel (one indicator) on ax."""
    y_idx  = {c: i for i, c in enumerate(countries_rev)}
    all_vals = []

    for country in DB_COUNTRIES:
        y = y_idx[country]
        if y % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="#F5F5F5", zorder=0, linewidth=0)

        for period_key, y_off, ls in [
            ("early",  DB_Y_OFF_R, "--"),   # early year on top
            ("recent", DB_Y_OFF_E, "-"),    # recent year on bottom
        ]:
            y_row = y + y_off
            v_val = results[period_key][country]["Venezuela"][ind_key]
            n_val = results[period_key][country]["Native"][ind_key]

            if pd.notna(v_val): all_vals.append(v_val)
            if pd.notna(n_val): all_vals.append(n_val)

            # Gap line
            if pd.notna(v_val) and pd.notna(n_val):
                ax.plot([min(v_val, n_val), max(v_val, n_val)], [y_row, y_row],
                        color=DB_C_GAP_ANN, linewidth=2.0, linestyle=ls, zorder=2,
                        solid_capstyle="round", dash_capstyle="round")

            # Dots (native behind Venezuelan)
            if pd.notna(n_val):
                ax.scatter(n_val, y_row, color=DB_C_NAT_ANN, s=80, zorder=4,
                           edgecolors="white", linewidths=0.8)
            if pd.notna(v_val):
                ax.scatter(v_val, y_row, color=DB_C_VEN_ANN, s=80, zorder=4,
                           edgecolors="white", linewidths=0.8)

            # Value labels: gap-threshold logic with targeted endpoint overrides.
            # _DB_FORCE_ENDPOINT cases always use left/right endpoint positioning.
            # Labels ≤ 0.05 are dropped (would fall off the x-axis).
            _min_gap = DB_MIN_GAP_INL_UNEMP if ind_key == "unemployment" else DB_MIN_GAP_INL_DEFAULT
            gap = abs(v_val - n_val) if (pd.notna(v_val) and pd.notna(n_val)) else np.inf
            use_endpoint = (gap < _min_gap) or ((ind_key, country) in _DB_FORCE_ENDPOINT)
            if use_endpoint and pd.notna(v_val) and pd.notna(n_val):
                lo_c = DB_C_NAT_ANN if n_val <= v_val else DB_C_VEN_ANN
                hi_c = DB_C_VEN_ANN if n_val <= v_val else DB_C_NAT_ANN
                lo_v = min(v_val, n_val); hi_v = max(v_val, n_val)
                if lo_v > 0.05:
                    ax.text(lo_v - DB_LABEL_H, y_row, f"{lo_v:.1f}",
                            ha="right", va="center", fontsize=7.5,
                            color=lo_c, fontweight="bold")
                ax.text(hi_v + DB_LABEL_H, y_row, f"{hi_v:.1f}",
                        ha="left",  va="center", fontsize=7.5,
                        color=hi_c, fontweight="bold")
            else:
                if pd.notna(v_val) and v_val > 0.05:
                    ax.text(v_val, y_row + DB_LABEL_V, f"{v_val:.1f}",
                            ha="center", va="bottom", fontsize=7.5,
                            color=DB_C_VEN_ANN, fontweight="bold")
                if pd.notna(n_val) and n_val > 0.05:
                    ax.text(n_val, y_row - DB_LABEL_V, f"{n_val:.1f}",
                            ha="center", va="top",    fontsize=7.5,
                            color=DB_C_NAT_ANN, fontweight="bold")

    ax.set_yticks(list(y_idx.values()))
    ax.set_yticklabels([""] * len(countries_rev))
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(DB_COUNTRIES) - 0.4)

    if first_panel:
        blend = ax.get_yaxis_transform()
        for country in countries_rev:
            y_c = y_idx[country]
            ax.text(-0.06, y_c, DB_COUNTRY_LBL[country],
                    transform=blend, ha="right", va="center",
                    fontsize=9.5, clip_on=False, fontweight="bold")
            ax.text(-0.06, y_c + DB_Y_OFF_R, DB_EARLY_WAVES[country][:4],
                    transform=blend, ha="right", va="center",
                    fontsize=7.5, color="#888888", clip_on=False)
            ax.text(-0.06, y_c + DB_Y_OFF_E, DB_RECENT_WAVES[country][:4],
                    transform=blend, ha="right", va="center",
                    fontsize=7.5, color="#888888", clip_on=False)

    _xlim = DB_XLIM_UNEMP if ind_key == "unemployment" else DB_XLIM_DEFAULT
    ax.set_xlim(0, _xlim)
    ax.xaxis.grid(True, linestyle="--", alpha=0.35, color="grey", zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=8)
    _strip_spines(ax)


def _plot_dumbbell_annex(out_dir, results, indicators, filename, figsize):
    """Multi-panel dumbbell chart (dot-and-line) for the annex slides."""
    n_ind = len(indicators)
    countries_rev = list(reversed(DB_COUNTRIES))  # bottom-to-top

    fig, axes = plt.subplots(1, n_ind, figsize=figsize, sharey=True)
    if n_ind == 1:
        axes = [axes]
    fig.subplots_adjust(wspace=0.14)

    for i, (ax, (ind_key, ind_title)) in enumerate(zip(axes, indicators)):
        _dumbbell_panel(ax, results, ind_key, countries_rev, first_panel=(i == 0))
        ax.set_title(ind_title, fontsize=9, fontweight="bold", pad=8)

    _spacer = Patch(visible=False, label="")
    leg_handles = [
        mlines.Line2D([], [], color=DB_C_VEN_ANN, marker="o", linestyle="None",
                      markersize=8, label="Venezuelan"),
        mlines.Line2D([], [], color=DB_C_NAT_ANN, marker="o", linestyle="None",
                      markersize=8, label="Native"),
        mlines.Line2D([], [], color=DB_C_GAP_ANN, linewidth=2, linestyle="--",
                      label=f"Gap — {DB_EARLY_LBL} (top)"),
        _spacer, _spacer,
        mlines.Line2D([], [], color=DB_C_GAP_ANN, linewidth=2, linestyle="-",
                      label=f"Gap — {DB_RECENT_LBL} (bottom)"),
    ]
    fig.legend(handles=leg_handles, loc="lower center", bbox_to_anchor=(0.5, 0.01),
               ncol=3, frameon=False, fontsize=8.5, handlelength=1.8,
               handletextpad=0.8, columnspacing=2.5)
    fig.tight_layout(rect=[0, 0.09, 1, 1])

    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


def plot_annex_indicators_a(out_dir: str, results: dict) -> str:
    return _plot_dumbbell_annex(
        out_dir, results, INDICATORS_A,
        "annex_indicators_a.png", figsize=(13, 6.5)
    )


def plot_annex_indicators_b1(out_dir: str, results: dict) -> str:
    return _plot_dumbbell_annex(
        out_dir, results, INDICATORS_B1,
        "annex_indicators_b1.png", figsize=(14, 6.5)
    )


def plot_annex_indicators_b2(out_dir: str, results: dict) -> str:
    return _plot_dumbbell_annex(
        out_dir, results, INDICATORS_B2,
        "annex_indicators_b2.png", figsize=(11, 6.5)
    )


# =============================================================================
# ANNEX — Labor market trend charts from data (with 95% CI)
# =============================================================================

TREND_COUNTRIES = ["COL", "PER", "CHL", "ECU", "ESP"]
TREND_COUNTRY_LBL = {
    "COL": "Colombia", "PER": "Peru", "CHL": "Chile",
    "ECU": "Ecuador",  "ESP": "Spain",
}
TREND_C_VEN = "#C0392B"    # Venezuelan line
TREND_C_NAT = "#1A5276"    # Native line

# (ind_key, display_title, value_col, denom_group, multiplier)
TREND_TYPES = [
    ("participation", "Participation Rate (%)",   "pea_ci",     "wapc", 1),
    ("unemployment",  "Unemployment Rate (%)",    "desemp_ci",  "peac", 1),
    ("inactivity",    "Inactivity Rate (%)",      "inactivo_ci","wapc", 1),
    ("formality",     "Formality Rate (%)",       "formal_ci",  "empc", 1),
]


import re as _re

def _period_to_float(p: str) -> float:
    """Convert HDMF period code to fractional year for sorting/plotting."""
    m = _re.match(r"(\d{4})(t(\d)|m(\d+)|a)?", str(p))
    if not m:
        return 0.0
    year = int(m.group(1))
    if m.group(3):                      # quarterly: t1/t2/t3/t4
        q = int(m.group(3))
        return year + (q * 2 - 1) / 8
    if m.group(4):                      # monthly: m12 etc.
        mon = int(m.group(4))
        return year + (mon - 0.5) / 12
    return year + 0.5                   # annual


def _wavg_se(y_col: pd.Series, w_col: pd.Series):
    """Weighted proportion + linearized SE (Taylor series).  Returns (p, se)."""
    y = pd.to_numeric(y_col, errors="coerce").to_numpy(float)
    w = pd.to_numeric(w_col, errors="coerce").to_numpy(float)
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0)
    if mask.sum() < 5:
        return np.nan, np.nan
    y, w = y[mask], w[mask]
    W = w.sum()
    p = float(np.dot(y, w) / W)
    # Linearized variance: var(p̂) = Σ(wᵢ²(yᵢ−p̂)²) / W²
    var_p = float(np.dot(w ** 2, (y - p) ** 2)) / (W ** 2)
    return p, float(np.sqrt(var_p))


def _build_trend_series(country: str, ind_key: str, value_col: str, denom_group: str):
    """Return DataFrame with columns [x_float, period, group, p, ci_lo, ci_hi]."""
    with open(CACHE_FILE, "rb") as fh:
        raw = pickle.load(fh)
    df = raw["data"]
    dfc = df[(df["pais_c"] == country) &
             df["foreign_born"].isin(["Venezuela", "Native"])].copy()

    if value_col == "formal_ci":
        # informality derived: 1 - formal
        dfc["_yval"] = 1 - pd.to_numeric(dfc[value_col], errors="coerce")
        dfc.loc[dfc[value_col].isna(), "_yval"] = np.nan
    elif value_col == "higher_edu_ci":
        # tertiary education: edu_hdmf >= 7
        dfc["_yval"] = (pd.to_numeric(dfc["edu_hdmf"], errors="coerce") >= 7).astype(float)
        dfc.loc[dfc["edu_hdmf"].isna(), "_yval"] = np.nan
    else:
        dfc["_yval"] = pd.to_numeric(dfc.get(value_col, pd.Series(dtype=float)),
                                     errors="coerce")
    if ind_key == "formality":
        dfc["_yval"] = pd.to_numeric(dfc[value_col], errors="coerce")

    rows = []
    for period in dfc["periodo_c"].dropna().unique():
        dfp = dfc[dfc["periodo_c"] == period]
        for grp in ["Venezuela", "Native"]:
            g = dfp[dfp["foreign_born"] == grp]
            # Select denominator
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
    ts = pd.DataFrame(rows).sort_values("x")
    return ts


def _plot_one_trend_panel(ax, country: str, ind_key: str, value_col: str,
                          denom_group: str, title_prefix: str, y_max: float = 100):
    """Draw a single-country trend panel with CI on ax."""
    ts = _build_trend_series(country, ind_key, value_col, denom_group)
    if ts.empty:
        ax.text(0.5, 0.5, "no data", ha="center", va="center",
                transform=ax.transAxes, color=C_SLATE, fontsize=11)
        ax.axis("off")
        return

    ax.set_facecolor("#FAFBFC")
    _strip_spines(ax)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", zorder=0)
    ax.set_axisbelow(True)

    for grp, color in [("Venezuelan", TREND_C_VEN), ("Native", TREND_C_NAT)]:
        grp_key = "Venezuela" if grp == "Venezuelan" else "Native"
        sub = ts[ts["group"] == grp_key].sort_values("x")
        if sub.empty:
            continue
        ax.fill_between(sub["x"], sub["ci_lo"], sub["ci_hi"],
                        color=color, alpha=0.12, zorder=1)
        ax.plot(sub["x"], sub["p"],
                color=color, linewidth=2.0, zorder=3,
                marker="o", markersize=5, markeredgecolor="white",
                markeredgewidth=0.8, label=grp)

    # X-axis: integer years
    all_x = ts["x"].values
    year_ints = sorted(set(int(x) for x in all_x))
    ax.set_xticks(year_ints)
    ax.set_xticklabels([str(y) for y in year_ints], fontsize=8, rotation=45, ha="right")
    ax.tick_params(axis="y", labelsize=8)
    ax.set_xlim(min(all_x) - 0.3, max(all_x) + 0.3)
    ax.set_ylim(0, y_max)

    ax.set_title(TREND_COUNTRY_LBL[country], fontsize=11, fontweight="bold",
                 color=C_NAVY, pad=5)


TREND_Y_MAX = {"unemployment": 40}   # override; all others default to 100


def plot_trend_from_data(out_dir: str, ind_key: str, value_col: str,
                         denom_group: str, trend_title: str, filename: str) -> str:
    """Generate a 2×3 trend grid for all TREND_COUNTRIES from the cache data."""
    y_max = TREND_Y_MAX.get(ind_key, 100)
    fig, axes = plt.subplots(2, 3, figsize=(20, 9))
    fig.subplots_adjust(hspace=0.38, wspace=0.28)

    for ax, country in zip(axes.flatten(), TREND_COUNTRIES):
        _plot_one_trend_panel(ax, country, ind_key, value_col, denom_group, trend_title,
                              y_max=y_max)

    axes.flatten()[5].axis("off")   # hide unused 6th panel

    # Shared legend at the bottom
    leg_handles = [
        mlines.Line2D([], [], color=TREND_C_VEN, linewidth=2, marker="o",
                      markersize=7, markeredgecolor="white", label="Venezuelan"),
        mlines.Line2D([], [], color=TREND_C_NAT, linewidth=2, marker="o",
                      markersize=7, markeredgecolor="white", label="Native"),
        Patch(color=TREND_C_VEN, alpha=0.18, label="95% CI — Venezuelan"),
        Patch(color=TREND_C_NAT, alpha=0.18, label="95% CI — Native"),
    ]
    fig.legend(handles=leg_handles, loc="lower center", bbox_to_anchor=(0.5, -0.01),
               ncol=4, frameon=False, fontsize=10, handlelength=2.0, columnspacing=2.5)

    fig.suptitle(trend_title, fontsize=15, fontweight="bold", color=C_NAVY, y=1.01)
    fig.tight_layout(rect=[0, 0.05, 1, 1])

    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


def plot_trend_higher_education(out_dir: str) -> str:
    """2×3 grid (5 panels + 1 hidden) for tertiary education trend: COL, PER, CHL, ECU, ESP."""
    countries_5 = ["COL", "PER", "CHL", "ECU", "ESP"]
    fig, axes = plt.subplots(2, 3, figsize=(20, 9))
    fig.subplots_adjust(hspace=0.38, wspace=0.28)

    for ax, country in zip(axes.flatten(), countries_5):
        _plot_one_trend_panel(ax, country, "higher_edu", "higher_edu_ci", "wapc",
                              "Tertiary Education Rate (%)", y_max=70)

    axes.flatten()[5].axis("off")   # hide unused 6th panel

    leg_handles = [
        mlines.Line2D([], [], color=TREND_C_VEN, linewidth=2, marker="o",
                      markersize=7, markeredgecolor="white", label="Venezuelan"),
        mlines.Line2D([], [], color=TREND_C_NAT, linewidth=2, marker="o",
                      markersize=7, markeredgecolor="white", label="Native"),
        Patch(color=TREND_C_VEN, alpha=0.18, label="95% CI — Venezuelan"),
        Patch(color=TREND_C_NAT, alpha=0.18, label="95% CI — Native"),
    ]
    fig.legend(handles=leg_handles, loc="lower center", bbox_to_anchor=(0.5, -0.01),
               ncol=4, frameon=False, fontsize=10, handlelength=2.0, columnspacing=2.5)

    fig.suptitle("Tertiary Education Rate (%) — Working-Age Population (16–64)",
                 fontsize=15, fontweight="bold", color=C_NAVY, y=1.01)
    fig.tight_layout(rect=[0, 0.05, 1, 1])

    path = os.path.join(out_dir, "trend_grid_higher_edu.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# =============================================================================
# LaTeX GENERATION
# =============================================================================

LATEX_HEADER = r"""\documentclass[aspectratio=169, 10pt]{beamer}

% ---------- Theme & colors ----------------------------------
\usetheme{Boadilla}
\usecolortheme{default}

% Academic-executive palette
\definecolor{hdmfteal}{RGB}{33,113,160}      % #2171A0 — steel blue, primary accent
\definecolor{hdmfnavy}{RGB}{29,53,87}        % #1D3557 — midnight navy, title bg
\definecolor{hdmfslate}{RGB}{107,124,147}    % #6B7C93 — slate gray, body text
\definecolor{hdmflight}{RGB}{234,240,245}    % #EAF0F5 — panel backgrounds
\definecolor{hdmfverylight}{RGB}{244,248,251}% #F4F8FB — section backgrounds
\definecolor{hdmfborder}{RGB}{200,215,228}   % #C8D7E4 — borders/lines
\definecolor{hdmfgray}{RGB}{107,124,147}     % #6B7C93 — footnote/caption text
% Chart colours
\definecolor{venred}{RGB}{184,74,42}         % #B84A2A — burnt sienna (Venezuelan)
\definecolor{natblue}{RGB}{29,53,87}         % #1D3557 — midnight navy (Native)
\definecolor{venearly}{RGB}{232,160,122}     % #E8A07A — light terracotta (Ven early)
\definecolor{natearly}{RGB}{125,174,201}     % #7DAEC9 — light steel blue (Nat early)
\definecolor{othergreen}{RGB}{39,174,96}

\setbeamercolor{structure}{fg=hdmfteal}
\setbeamercolor{frametitle}{bg=hdmfteal, fg=white}
\setbeamercolor{title}{fg=white}
\setbeamercolor{subtitle}{fg=white}
\setbeamercolor{author}{fg=white}
\setbeamercolor{institute}{fg=white}
\setbeamercolor{date}{fg=white}
\setbeamercolor{author in head/foot}{fg=white, bg=hdmfteal}
\setbeamercolor{title in head/foot}{fg=hdmflight, bg=hdmfteal}
\setbeamercolor{date in head/foot}{fg=white, bg=hdmfteal}
\setbeamercolor{section in toc}{fg=hdmfteal}
\setbeamercolor{block title}{bg=hdmfteal, fg=white}
\setbeamercolor{block body}{bg=hdmflight}

\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{footline}{%
  \leavevmode%
  \hbox{%
    \begin{beamercolorbox}[wd=.55\paperwidth, ht=2.4ex, dp=1ex, leftskip=0.5em]{author in head/foot}%
      \usebeamerfont{author in head/foot}HDMF --- How do Migrants Fare in LAC \,|\, IDB
    \end{beamercolorbox}%
    \begin{beamercolorbox}[wd=.35\paperwidth, ht=2.4ex, dp=1ex, center]{title in head/foot}%
      \usebeamerfont{title in head/foot}\insertshorttitle
    \end{beamercolorbox}%
    \begin{beamercolorbox}[wd=.10\paperwidth, ht=2.4ex, dp=1ex, right, rightskip=0.5em]{date in head/foot}%
      \usebeamerfont{date in head/foot}\insertframenumber{} / \inserttotalframenumber
    \end{beamercolorbox}%
  }%
}

% ---------- Packages ----------------------------------------
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{multicol}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}

\graphicspath{{./}}

% ---------- Title block -------------------------------------
\title[SCL --- Venezuelan Migrants in LAC]{%
  How do Migrants Fare in LAC?\\[0.3em]
  {\normalsize Venezuelan Migrants vs.\ Natives: Labor Market, Income \& Education Outcomes --- LAC-5 + Spain}}
\subtitle{}
\author{Knowledge and Data Team --- Social Sector (SCL)}
\institute{Inter-American Development Bank}
\date{DATE_PLACEHOLDER}

\begin{document}

{\setbeamercolor{background canvas}{bg=hdmfnavy}
\begin{frame}[plain]
  \vspace{1.2cm}
  \titlepage
\end{frame}}

\begin{frame}{Table of Contents}
  \tableofcontents
\end{frame}
"""

LATEX_FOOTER = r"""
% ---- Back matter -------------------------------------------
{\setbeamercolor{background canvas}{bg=hdmfnavy}
\begin{frame}[plain]
  \vspace{1.8cm}
  \begin{center}
    {\large\color{white}\textbf{Thank you}}\\[0.8em]
    \textcolor{hdmflight}{\rule{0.4\textwidth}{0.4pt}}\\[0.6em]
    {\small\color{white}HDMF --- How do Migrants Fare in LAC}\\
    {\footnotesize\color{hdmflight}Inter-American Development Bank --- Knowledge and Data Team (SCL)}
  \end{center}
\end{frame}}

\end{document}
"""


def build_population_slide(img_rel: str) -> str:
    return rf"""
% ============================================================
\section{{Population Coverage}}
% ============================================================

\begin{{frame}}[t]{{Venezuelan Migrants: Population Coverage}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.78\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Sources: R4V --- Plataforma R4V Cifras Mundiales (Feb 2026): COL/PER/CHL/ECU/BRA from national registries;
    USA from US Census Bureau; ESP from IMS 2024.
    Household surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).
    USA (ACS) and BRA (SISMIGRA) survey estimates not included in this chart.}}}}
\end{{frame}}
"""


def build_age_slide(img_rel: str) -> str:
    return rf"""
% ============================================================
\section{{Age Distribution}}
% ============================================================

\begin{{frame}}[t]{{Age Distribution of Venezuelan Migrants and Natives}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.78\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Survey-weighted shares. Working-age population (18+) shown.
    Most recent available wave per country.
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).}}}}
\end{{frame}}
"""


def build_education_slide(img_rel: str) -> str:
    return rf"""
% ============================================================
\section{{Education}}
% ============================================================

\begin{{frame}}[t]{{Education Distribution --- Most Recent Year}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.78\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Survey-weighted shares. \emph{{Higher education}}: technical/vocational,
    university (complete and incomplete), postgraduate (\texttt{{edu\_hdmf}} 7--8).
    \emph{{High school}}: lower/upper secondary (\texttt{{edu\_hdmf}} 4--6).
    \emph{{Primary or less}}: codes 1--3.
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).}}}}
\end{{frame}}
"""


def build_methodology_slide() -> str:
    return r"""
% ============================================================
\section{Labor Market \& Demographics --- Pooled}
% ============================================================

\begin{frame}{How We Measure and Compare}
  \vspace{-0.3em}
  \begin{columns}[T]

    %% ---- Left: indicator definitions --------------------------------
    \begin{column}{0.54\textwidth}
      \textbf{\textcolor{hdmfteal}{What we measure}}\\[0.4em]
      \footnotesize
      \begin{tabular}{@{}p{3.2cm}p{4.6cm}@{}}
        \textbf{Working-age share}      & Share of total population aged 15--64 \\[3pt]
        \textbf{Labor participation}    & Share of working-age population actively employed or seeking work \\[3pt]
        \textbf{Tertiary education}     & Share of working-age population with any post-secondary qualification \\[3pt]
        \textbf{Unemployment}           & Share of the active labor force currently without work \\[3pt]
        \textbf{Inactivity}             & Share of working-age population neither working nor looking for work \\[3pt]
        \textbf{Informality}            & Share of employed without formal labor conditions \\[3pt]
        \textbf{Part-time / Long hours} & Share working fewer than 35\,h or more than 50\,h per week \\
      \end{tabular}
    \end{column}

    %% ---- Right: weighting rationale ---------------------------------
    \begin{column}{0.42\textwidth}
      \begin{block}{Country weighting}
        \footnotesize
        Indicators are estimated separately for each country and then
        combined into a \textbf{LAC-5 pooled average}.\\[0.5em]
        Each country is weighted by the \textbf{size of its Venezuelan
        community} according to the best available reference estimate
        (R4V when available, UNDESA otherwise --- most recent year).\\[0.5em]
        \begin{tabular}{@{}lr@{}}
          Colombia  & 2.8M \\
          Peru      & 1.6M \\
          Chile     & 0.7M \\
          Spain     & 0.6M \\
          Ecuador   & 0.4M \\
        \end{tabular}\\[0.5em]
        This ensures the pooled figure reflects the \textbf{actual
        diaspora distribution} --- not sampling patterns.
      \end{block}
    \end{column}

  \end{columns}
\end{frame}
"""


def build_pooled_slide_a(img_rel: str) -> str:
    return rf"""
\begin{{frame}}[t]{{Venezuelan Migrants vs.\ Natives --- LAC-5 Pooled}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.80\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Pooled weighted estimates across COL, PER, CHL, ECU, ESP (most recent and earliest available waves).
    Working age: \% of total population aged 15--64.
    Participation and tertiary education: denominator = working-age pop.\ (16--64).
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).}}}}
\end{{frame}}
"""


def build_pooled_slide_b(img_rel: str) -> str:
    return rf"""
\begin{{frame}}[t]{{Venezuelan Migrants vs.\ Natives — LAC-5 Pooled (Labor Quality)}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.80\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Pooled weighted estimates. LAC-4 label: Spain excluded from unemployment and informality
    (harmonization gaps in EPA). Inactivity, part-time, long hours: all 5 countries.
    Part-time = main-job hours $<$35\,h/week. Long hours $>$50\,h/week.
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).}}}}
\end{{frame}}
"""


def build_indicators_slide_a(img_rel: str) -> str:
    return rf"""
% ============================================================
\section{{Labor Market \& Demographics}}
% ============================================================

\begin{{frame}}[t]{{Population and Labor Force Participation}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.78\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Weighted estimates. Working age (15--64): share of total population.
    Participation and tertiary education: denominator = working-age pop.\ (16--64).
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).
    Recent = 2024--25; early = 2017--18.}}}}
\end{{frame}}
"""


def build_indicators_slide_b(img_rel: str) -> str:
    return rf"""
\begin{{frame}}[t]{{Labor Market Outcomes --- Quality and Informality}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.78\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Unemployment: \% of economically active pop.\ (PEA).
    Inactivity: \% of working-age pop.\ (16--64).
    Informality, part-time, long hours (50+\,h/week): \% of employed.
    Part-time = main-job hours $<$35\,h/week.
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).
    Recent = 2024--25; early = 2017--18.}}}}
\end{{frame}}
"""


def build_annex_country_slide_a(img_rel: str) -> str:
    return rf"""
% ============================================================
\appendix
\section{{Annex: Country-Level Breakdown}}
% ============================================================

\begin{{frame}}[t]{{Country Breakdown --- Demographics \& Labor Participation}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.80\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Top row = early wave (2017--18); bottom row = recent wave (2024--25).
    Working age: \% of total pop.\ aged 15--64.
    Participation and tertiary education: denominator = working-age pop.\ (16--64).
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).}}}}
\end{{frame}}
"""


def build_annex_country_slide_b1(img_rel: str) -> str:
    return rf"""
\begin{{frame}}[t]{{Country Breakdown --- Unemployment, Inactivity \& Informality}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.80\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Top row = early wave (2017--18); bottom row = recent wave (2024--25).
    Unemployment: \% of PEA (16--64). Inactivity: \% of working-age pop.\ (16--64).
    Informality: \% of employed. ESP: unemployment and informality not comparable (harmonization gap in EPA).
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).}}}}
\end{{frame}}
"""


def build_annex_country_slide_b2(img_rel: str) -> str:
    return rf"""
\begin{{frame}}[t]{{Country Breakdown --- Part-time \& Long Hours}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.80\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Top row = early wave (2017--18); bottom row = recent wave (2024--25).
    Part-time: main-job hours $<$35\,h/week, \% of employed.
    Long hours: $>$50\,h/week, \% of employed.
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP).}}}}
\end{{frame}}
"""


def build_annex_trend_slide(img_rel: str, trend_title: str, section: bool = False) -> str:
    section_block = r"""
% ============================================================
\section{Annex: Labor Market Trends}
% ============================================================
""" if section else ""
    safe_title = trend_title.replace("%", r"\%")
    return rf"""{section_block}
\begin{{frame}}[t]{{{safe_title} --- Trend by Country (COL, PER, CHL, ECU)}}
  \vspace{{-0.5em}}
  \begin{{center}}
    \includegraphics[width=\linewidth, height=0.82\textheight, keepaspectratio]{{{img_rel}}}
  \end{{center}}
  \vspace{{-0.5em}}
  {{\fontsize{{5}}{{6}}\selectfont\textcolor{{hdmfgray}}{{%
    Survey-weighted trend estimates. Venezuelan migrants vs.\ native-born.
    Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU).}}}}
\end{{frame}}
"""


# =============================================================================
# EXCEL EXPORT — all presentation data in chart-ready format
# =============================================================================

def _xl_hdr(ws, row, col, value, bg="2171A0", fg="FFFFFF", bold=True, fontsize=10):
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.font = Font(bold=bold, color=fg, size=fontsize)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    s = Side(style="thin", color="CCCCCC")
    cell.border = Border(left=s, right=s, top=s, bottom=s)
    return cell


def _xl_data(ws, row, col, value, bg="FFFFFF", fmt=None, bold=False):
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.font = Font(bold=bold, size=10)
    cell.alignment = Alignment(horizontal="center" if not isinstance(value, str) else "left",
                                vertical="center")
    s = Side(style="thin", color="DDDDDD")
    cell.border = Border(left=s, right=s, top=s, bottom=s)
    if fmt:
        cell.number_format = fmt
    return cell


def _xl_note(ws, row, ncols, text):
    from openpyxl.styles import Font, Alignment
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(size=8, color="888888", italic=True)
    cell.alignment = Alignment(wrap_text=True)
    if ncols > 1:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)


# Palette constants for Excel
_BG_VEN_R  = "FAD4CC"   # recent Venezuelan (light red)
_BG_NAT_R  = "C9DEF0"   # recent Native (light blue)
_BG_VEN_E  = "FDE8D8"   # early Venezuelan (lighter)
_BG_NAT_E  = "DCF0FB"   # early Native (lighter)
_BG_HDR_V  = "C0392B"   # Venezuelan header
_BG_HDR_N  = "1A5276"   # Native header
_BG_LABEL  = "F0F0F0"   # row/country labels
_BG_WHITE  = "FFFFFF"


def _sheet_population(wb, sorted_data):
    from openpyxl import Workbook
    ws = wb.create_sheet("Population_Coverage")
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 18
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 22

    # Sub-header row 1
    _xl_hdr(ws, 1, 1, "Country",        bg="1D3557")
    _xl_hdr(ws, 1, 2, "Recent wave",    bg="1D3557")
    _xl_hdr(ws, 1, 3, "R4V (recent)",   bg=_BG_HDR_N)
    _xl_hdr(ws, 1, 4, "Survey (recent)",bg=_BG_HDR_V)
    _xl_hdr(ws, 1, 5, "Early wave",     bg="1D3557")
    _xl_hdr(ws, 1, 6, "R4V (early)",    bg=_BG_HDR_N)
    _xl_hdr(ws, 1, 7, "Survey (early)", bg=_BG_HDR_V)

    import re as _re
    def _yr(w):
        m = _re.search(r"\d{4}", str(w)) if w else None
        return m.group(0) if m else ""

    for r, row in enumerate(sorted_data, start=2):
        bg = _BG_LABEL if r % 2 == 0 else _BG_WHITE
        _xl_data(ws, r, 1, row[0], bg=bg, bold=True)
        _xl_data(ws, r, 2, _yr(row[1]), bg=bg)
        _xl_data(ws, r, 3, row[4] if not (isinstance(row[4], float) and np.isnan(row[4])) else None, bg=_BG_NAT_R, fmt="#,##0")
        _xl_data(ws, r, 4, row[3] if not (isinstance(row[3], float) and np.isnan(row[3])) else None, bg=_BG_VEN_R, fmt="#,##0")
        _xl_data(ws, r, 5, _yr(row[2]) if row[2] else "", bg=bg)
        _xl_data(ws, r, 6, row[7] if not (isinstance(row[7], float) and np.isnan(row[7])) else None, bg=_BG_NAT_E, fmt="#,##0")
        _xl_data(ws, r, 7, row[6] if not (isinstance(row[6], float) and np.isnan(row[6])) else None, bg=_BG_VEN_E, fmt="#,##0")

    _xl_note(ws, len(sorted_data) + 3, 7,
             "Source: R4V — Plataforma R4V Cifras Mundiales (Feb 2026). "
             "Surveys: GEIH (COL), ENAHO (PER), CASEN (CHL), ENEMDU (ECU), EPA (ESP). "
             "Chart tip: select cols C–D, rows 2 onwards → Insert Clustered Bar.")


def _sheet_age(wb, df_ven):
    ws = wb.create_sheet("Age_Distribution")
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 12
    for c in "CDEFGHI":
        ws.column_dimensions[c].width = 16
    ws.row_dimensions[1].height = 30

    headers = ["Country", "Period", "0-14 (thousands)", "15-64 (thousands)",
               "65+ (thousands)", "Total (thousands)", "% aged 15-64"]
    bgs     = ["1D3557","1D3557","2171A0","2171A0","2171A0","1D3557","C0392B"]
    for c, (h, bg) in enumerate(zip(headers, bgs), start=1):
        _xl_hdr(ws, 1, c, h, bg=bg)

    dfc = df_ven[df_ven["edad_ci"].notna()].copy()
    dfc["age3"] = dfc["edad_ci"].apply(_age3)
    avail = [c for c in LAC5 if c in dfc["pais_c"].unique()]
    totals = {c: dfc.loc[dfc["pais_c"] == c, "factor_ci"].sum() for c in avail}
    countries = sorted(avail, key=lambda c: -totals[c])

    for r, country in enumerate(countries, start=2):
        sub = dfc[dfc["pais_c"] == country]
        period = sub["_period"].iloc[0] if "_period" in sub.columns else ""
        bg = _BG_LABEL if r % 2 == 0 else _BG_WHITE
        grp_counts = {g: sub.loc[sub["age3"] == g, "factor_ci"].sum() / 1_000 for g in ["0-14","15-64","65+"]}
        total_k = sum(grp_counts.values())
        pct_1564 = grp_counts["15-64"] / total_k * 100 if total_k > 0 else None
        _xl_data(ws, r, 1, COUNTRY_FULL.get(country, country), bg=bg, bold=True)
        _xl_data(ws, r, 2, str(period), bg=bg)
        _xl_data(ws, r, 3, round(grp_counts["0-14"],   1), bg=_BG_VEN_E,  fmt="0.0")
        _xl_data(ws, r, 4, round(grp_counts["15-64"],  1), bg=_BG_NAT_R,  fmt="0.0")
        _xl_data(ws, r, 5, round(grp_counts["65+"],    1), bg=_BG_VEN_R,  fmt="0.0")
        _xl_data(ws, r, 6, round(total_k,              1), bg=_BG_LABEL,  fmt="0.0")
        _xl_data(ws, r, 7, round(pct_1564, 1) if pct_1564 else None, bg=_BG_NAT_E, fmt="0.0")

    _xl_note(ws, len(countries) + 3, 7,
             "Venezuelan-born only, most recent wave. "
             "Chart tip: select cols C–E for stacked bar; col G for line overlay.")


def _sheet_education(wb, df_ven):
    ws = wb.create_sheet("Education_Distribution")
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 12
    for c in "CDEFGHI":
        ws.column_dimensions[c].width = 18
    ws.row_dimensions[1].height = 30

    headers = ["Country", "Period", "Primary or less (th.)", "Secondary (th.)",
               "Higher education (th.)", "Total (th.)", "% Higher education"]
    bgs     = ["1D3557","1D3557","2171A0","2171A0","2171A0","1D3557","C0392B"]
    for c, (h, bg) in enumerate(zip(headers, bgs), start=1):
        _xl_hdr(ws, 1, c, h, bg=bg)

    dfc = df_ven[df_ven["edu_hdmf"].notna() & df_ven["edad_ci"].notna()].copy()
    dfc = dfc[(dfc["edad_ci"] >= 15) & (dfc["edad_ci"] <= 64)].copy()
    dfc["edu_3cat"] = dfc["edu_hdmf"].astype(int).map(EDU_3CAT_MAP)
    dfc = dfc[dfc["edu_3cat"].notna()].copy()
    avail = [c for c in LAC5 if c in dfc["pais_c"].unique()]
    totals = {c: dfc.loc[dfc["pais_c"] == c, "factor_ci"].sum() for c in avail}
    countries = sorted(avail, key=lambda c: -totals[c])

    for r, country in enumerate(countries, start=2):
        sub = dfc[dfc["pais_c"] == country]
        period = sub["_period"].iloc[0] if "_period" in sub.columns else ""
        bg = _BG_LABEL if r % 2 == 0 else _BG_WHITE
        cats = {cat: sub.loc[sub["edu_3cat"] == cat, "factor_ci"].sum() / 1_000
                for cat in EDU_3CAT_ORDER}
        total_k = sum(cats.values())
        pct_hi = cats["Higher education"] / total_k * 100 if total_k > 0 else None
        _xl_data(ws, r, 1, COUNTRY_FULL.get(country, country), bg=bg, bold=True)
        _xl_data(ws, r, 2, str(period), bg=bg)
        _xl_data(ws, r, 3, round(cats["Primary or less"],  1), bg=_BG_VEN_E, fmt="0.0")
        _xl_data(ws, r, 4, round(cats["Secondary"],        1), bg=_BG_NAT_R, fmt="0.0")
        _xl_data(ws, r, 5, round(cats["Higher education"], 1), bg=_BG_NAT_E, fmt="0.0")
        _xl_data(ws, r, 6, round(total_k,                  1), bg=_BG_LABEL, fmt="0.0")
        _xl_data(ws, r, 7, round(pct_hi, 1) if pct_hi else None, bg=_BG_VEN_R, fmt="0.0")

    _xl_note(ws, len(countries) + 3, 7,
             "Venezuelan-born, working-age (15-64), most recent wave. "
             "Chart tip: select cols C–E for stacked bar; col G for overlay.")


def _sheet_pooled(wb, pooled_results):
    ws = wb.create_sheet("Pooled_Indicators")
    ws.column_dimensions["A"].width = 30
    for c in "BCDEFGH":
        ws.column_dimensions[c].width = 18
    ws.row_dimensions[1].height = 15
    ws.row_dimensions[2].height = 30

    # Row 1: period group headers (merged)
    from openpyxl.styles import Alignment as _Aln
    ws.merge_cells("B1:C1"); _xl_hdr(ws, 1, 2, f"Recent ({DB_RECENT_LBL})", bg="1D3557"); ws["B1"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("D1:E1"); _xl_hdr(ws, 1, 4, f"Early ({DB_EARLY_LBL})",   bg="2171A0"); ws["D1"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("F1:G1"); _xl_hdr(ws, 1, 6, "Change (Recent − Early)",   bg="444444"); ws["F1"].alignment = _Aln(horizontal="center", vertical="center")

    col_hdrs = ["Indicator", "Venezuelan (%)", "Native (%)", "Venezuelan (%)", "Native (%)", "Venezuelan", "Native"]
    col_bgs  = ["1D3557", _BG_HDR_V, _BG_HDR_N, _BG_HDR_V, _BG_HDR_N, _BG_HDR_V, _BG_HDR_N]
    for c, (h, bg) in enumerate(zip(col_hdrs, col_bgs), start=1):
        _xl_hdr(ws, 2, c, h, bg=bg)

    all_inds = POOLED_A + POOLED_B
    for r, (ind_key, ind_label) in enumerate(all_inds, start=3):
        bg = _BG_LABEL if r % 2 == 0 else _BG_WHITE
        v_r = pooled_results["recent"]["Venezuela"][ind_key]
        n_r = pooled_results["recent"]["Native"][ind_key]
        v_e = pooled_results["early"]["Venezuela"][ind_key]
        n_e = pooled_results["early"]["Native"][ind_key]
        label = ind_label.replace("\n", " ")
        _xl_data(ws, r, 1, label,  bg=bg, bold=True)
        _xl_data(ws, r, 2, round(v_r, 1) if not np.isnan(v_r) else None, bg=_BG_VEN_R, fmt="0.0")
        _xl_data(ws, r, 3, round(n_r, 1) if not np.isnan(n_r) else None, bg=_BG_NAT_R, fmt="0.0")
        _xl_data(ws, r, 4, round(v_e, 1) if not np.isnan(v_e) else None, bg=_BG_VEN_E, fmt="0.0")
        _xl_data(ws, r, 5, round(n_e, 1) if not np.isnan(n_e) else None, bg=_BG_NAT_E, fmt="0.0")
        dv = round(v_r - v_e, 1) if not (np.isnan(v_r) or np.isnan(v_e)) else None
        dn = round(n_r - n_e, 1) if not (np.isnan(n_r) or np.isnan(n_e)) else None
        _xl_data(ws, r, 6, dv, bg=_BG_VEN_E, fmt="+0.0;-0.0;0.0")
        _xl_data(ws, r, 7, dn, bg=_BG_NAT_E, fmt="+0.0;-0.0;0.0")

    _xl_note(ws, len(all_inds) + 4, 7,
             f"LAC-5 pooled (COL, PER, CHL, ECU, ESP), weighted by R4V Venezuelan population. "
             f"Recent={DB_RECENT_LBL}, Early={DB_EARLY_LBL}. "
             "Chart tip: select cols B–C, rows 3 onwards → Insert Clustered Bar.")


def _sheet_pooled_comparison(wb, r4v_results, survey_results):
    """Side-by-side sheet: R4V-weighted vs. survey-pooled (no R4V) for all indicators × 2 periods.

    Layout (13 columns):
      A: Indicator
      [Recent] B: R4V Ven | C: R4V Nat | D: Survey Ven | E: Survey Nat | F: Diff Ven | G: Diff Nat
      [Early]  H: R4V Ven | I: R4V Nat | J: Survey Ven | K: Survey Nat | L: Diff Ven | M: Diff Nat
    Diff = R4V − Survey (positive means R4V gives higher value).
    """
    from openpyxl.styles import Alignment as _Aln
    ws = wb.create_sheet("Pooled_R4V_vs_Survey")
    ws.column_dimensions["A"].width = 34
    for col in "BCDEFGHIJKLM":
        ws.column_dimensions[col].width = 14
    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 30

    # Row 1: period group headers
    ws.merge_cells("B1:G1")
    _xl_hdr(ws, 1, 2, f"Recent ({DB_RECENT_LBL})", bg="1D3557")
    ws["B1"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("H1:M1")
    _xl_hdr(ws, 1, 8, f"Early ({DB_EARLY_LBL})", bg="2171A0")
    ws["H1"].alignment = _Aln(horizontal="center", vertical="center")

    # Row 2: method sub-group headers
    ws.merge_cells("B2:C2")
    _xl_hdr(ws, 2, 2, "R4V-weighted", bg="1D3557")
    ws["B2"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("D2:E2")
    _xl_hdr(ws, 2, 4, "Survey-pooled (no R4V)", bg="2E7D6B")
    ws["D2"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("F2:G2")
    _xl_hdr(ws, 2, 6, "Difference (R4V − Survey)", bg="555555")
    ws["F2"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("H2:I2")
    _xl_hdr(ws, 2, 8, "R4V-weighted", bg="1D3557")
    ws["H2"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("J2:K2")
    _xl_hdr(ws, 2, 10, "Survey-pooled (no R4V)", bg="2E7D6B")
    ws["J2"].alignment = _Aln(horizontal="center", vertical="center")
    ws.merge_cells("L2:M2")
    _xl_hdr(ws, 2, 12, "Difference (R4V − Survey)", bg="555555")
    ws["L2"].alignment = _Aln(horizontal="center", vertical="center")

    # Row 3: column-level headers
    col_hdrs = [
        "Indicator",
        "Venezuelan (%)", "Native (%)",    # R4V recent
        "Venezuelan (%)", "Native (%)",    # Survey recent
        "Venezuelan",     "Native",        # Diff recent
        "Venezuelan (%)", "Native (%)",    # R4V early
        "Venezuelan (%)", "Native (%)",    # Survey early
        "Venezuelan",     "Native",        # Diff early
    ]
    col_bgs = [
        "1D3557",
        _BG_HDR_V, _BG_HDR_N,
        "5FAD9A", "7DBFB0",
        _BG_HDR_V, _BG_HDR_N,
        _BG_HDR_V, _BG_HDR_N,
        "5FAD9A", "7DBFB0",
        _BG_HDR_V, _BG_HDR_N,
    ]
    for c, (h, bg) in enumerate(zip(col_hdrs, col_bgs), start=1):
        _xl_hdr(ws, 3, c, h, bg=bg)

    # Background colours for data cells
    _BG_SURV_V  = "C8EAE2"   # teal-tinted Venezuelan (survey)
    _BG_SURV_N  = "D8F0EB"   # light teal Native (survey)
    _BG_DIFF_POS = "FFF2CC"  # amber for R4V > Survey
    _BG_DIFF_NEG = "EBF5FB"  # blue-tint for R4V < Survey

    def _diff_bg(v):
        if v is None:
            return "FFFFFF"
        return _BG_DIFF_POS if v > 0.05 else (_BG_DIFF_NEG if v < -0.05 else "F0F0F0")

    all_inds = POOLED_A + POOLED_B
    for r, (ind_key, ind_label) in enumerate(all_inds, start=4):
        bg_row = _BG_LABEL if r % 2 == 0 else _BG_WHITE
        label  = ind_label.replace("\n", " ")
        _xl_data(ws, r, 1, label, bg=bg_row, bold=True)

        for period, base_col in [("recent", 2), ("early", 8)]:
            r4v_v  = r4v_results[period]["Venezuela"][ind_key]
            r4v_n  = r4v_results[period]["Native"][ind_key]
            sur_v  = survey_results[period]["Venezuela"][ind_key]
            sur_n  = survey_results[period]["Native"][ind_key]

            def _fmt(x): return round(x, 1) if pd.notna(x) else None
            def _dif(a, b):
                return round(a - b, 1) if (pd.notna(a) and pd.notna(b)) else None

            dv = _dif(r4v_v, sur_v)
            dn = _dif(r4v_n, sur_n)

            _xl_data(ws, r, base_col + 0, _fmt(r4v_v), bg=_BG_VEN_R, fmt="0.0")
            _xl_data(ws, r, base_col + 1, _fmt(r4v_n), bg=_BG_NAT_R, fmt="0.0")
            _xl_data(ws, r, base_col + 2, _fmt(sur_v), bg=_BG_SURV_V, fmt="0.0")
            _xl_data(ws, r, base_col + 3, _fmt(sur_n), bg=_BG_SURV_N, fmt="0.0")
            _xl_data(ws, r, base_col + 4, dv, bg=_diff_bg(dv), fmt="+0.0;-0.0;0.0")
            _xl_data(ws, r, base_col + 5, dn, bg=_diff_bg(dn), fmt="+0.0;-0.0;0.0")

    note_row = len(all_inds) + 6
    _xl_note(ws, note_row, 13,
             f"R4V-weighted: per-country survey-weighted stats aggregated using R4V Venezuelan population "
             f"(COL=2.8M, PER=1.6M, CHL=669k, ECU=440k, ESP=603k). "
             f"Survey-pooled: all respondents pooled directly using factor_ci survey weights (no country-level re-weighting). "
             f"Difference = R4V − Survey. Yellow = R4V gives value >0.05 pp higher; blue = >0.05 pp lower. "
             f"ESP informality and unemployment excluded from both (harmonization gap). "
             f"Recent={DB_RECENT_LBL}, Early={DB_EARLY_LBL}.")
    # Add country-level per-indicator breakdown tab for transparency
    return ws


def _sheet_country_weights(wb, r4v_results, survey_results):
    """One row per country showing its effective weight under each method, for transparency."""
    from openpyxl.styles import Alignment as _Aln
    ws = wb.create_sheet("Country_Weights")
    ws.column_dimensions["A"].width = 14
    for col in "BCDEF":
        ws.column_dimensions[col].width = 18
    ws.row_dimensions[1].height = 30

    hdrs = ["Country", "R4V weight (k)", "R4V share (%)",
            "Survey Ven obs (k)", "Survey Ven share (%)"]
    bgs  = ["1D3557", _BG_HDR_V, _BG_HDR_V, "5FAD9A", "5FAD9A"]
    for c, (h, bg) in enumerate(zip(hdrs, bgs), start=1):
        _xl_hdr(ws, 1, c, h, bg=bg)

    r4v_total = sum(COUNTRY_R4V_WEIGHTS[c] for c in DB_COUNTRIES)

    # Load cache to get survey Venezuelan counts for recent waves
    with open(CACHE_FILE, "rb") as fh:
        raw = pickle.load(fh)
    df = raw["data"]
    df = df[df["pais_c"].isin(DB_COUNTRIES) & (df["foreign_born"] == "Venezuela")].copy()
    survey_counts = {}
    for c in DB_COUNTRIES:
        wave = DB_RECENT_WAVES[c]
        w = df[(df["pais_c"] == c) & (df["periodo_c"] == wave)]["factor_ci"].sum()
        survey_counts[c] = w
    survey_total = sum(survey_counts.values())

    country_names = {"COL": "Colombia", "PER": "Peru", "CHL": "Chile",
                     "ECU": "Ecuador", "ESP": "Spain"}
    for r, c in enumerate(DB_COUNTRIES, start=2):
        bg = _BG_LABEL if r % 2 == 0 else _BG_WHITE
        r4v_w   = COUNTRY_R4V_WEIGHTS[c]
        r4v_sh  = r4v_w / r4v_total * 100
        sur_w   = survey_counts[c]
        sur_sh  = sur_w / survey_total * 100
        _xl_data(ws, r, 1, country_names.get(c, c), bg=bg, bold=True)
        _xl_data(ws, r, 2, round(r4v_w / 1000, 1), bg=_BG_VEN_E, fmt="0.0")
        _xl_data(ws, r, 3, round(r4v_sh, 1),        bg=_BG_VEN_R, fmt="0.0")
        _xl_data(ws, r, 4, round(sur_w / 1000, 1),  bg="C8EAE2",  fmt="0.0")
        _xl_data(ws, r, 5, round(sur_sh, 1),         bg="5FAD9A",  fmt="0.0")

    _xl_note(ws, len(DB_COUNTRIES) + 4, 5,
             "R4V weights = COUNTRY_R4V_WEIGHTS (most recent year). "
             "Survey Ven obs = sum(factor_ci) for Venezuelan-born in the recent wave. "
             "Both sets of shares should add to 100% across the 5 countries.")
    return ws


def export_weighting_comparison_excel(out_dir: str) -> str:
    """Write scl_pooled_weighting_comparison.xlsx comparing R4V-weighted vs. survey-pooled aggregation."""
    try:
        from openpyxl import Workbook
    except ImportError:
        print("  openpyxl not available — skipping weighting comparison export")
        return ""

    r4v_results    = _get_pooled_data()
    survey_results = _get_pooled_data_survey_only()

    wb = Workbook()
    wb.remove(wb.active)

    _sheet_pooled_comparison(wb, r4v_results, survey_results)
    _sheet_country_weights(wb, r4v_results, survey_results)

    path = os.path.join(out_dir, "scl_pooled_weighting_comparison.xlsx")
    wb.save(path)
    print(f"  Weighting comparison Excel saved: {path}")
    return path


def _sheet_country_breakdown(wb, db_results):
    ws = wb.create_sheet("Country_Breakdown")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 14
    for c in "CDEFGH":
        ws.column_dimensions[c].width = 16
    ws.row_dimensions[1].height = 15
    ws.row_dimensions[2].height = 30

    from openpyxl.styles import Alignment as _Aln
    ws.merge_cells("C1:D1"); _xl_hdr(ws, 1, 3, f"Recent ({DB_RECENT_LBL})", bg="1D3557"); ws["C1"].alignment = _Aln(horizontal="center",vertical="center")
    ws.merge_cells("E1:F1"); _xl_hdr(ws, 1, 5, f"Early ({DB_EARLY_LBL})",   bg="2171A0"); ws["E1"].alignment = _Aln(horizontal="center",vertical="center")
    ws.merge_cells("G1:H1"); _xl_hdr(ws, 1, 7, "Gap: Venezuelan − Native",  bg="444444"); ws["G1"].alignment = _Aln(horizontal="center",vertical="center")

    col_hdrs = ["Indicator", "Country", "Venezuelan (%)", "Native (%)", "Venezuelan (%)", "Native (%)", "Gap Recent", "Gap Early"]
    col_bgs  = ["1D3557","1D3557",_BG_HDR_V,_BG_HDR_N,_BG_HDR_V,_BG_HDR_N,_BG_HDR_V,_BG_HDR_N]
    for c, (h, bg) in enumerate(zip(col_hdrs, col_bgs), start=1):
        _xl_hdr(ws, 2, c, h, bg=bg)

    all_inds = list(INDICATORS_A) + list(INDICATORS_B)
    r = 3
    for ind_key, ind_label in all_inds:
        label = ind_label.replace("\n", " ")
        for ci, country in enumerate(DB_COUNTRIES):
            bg = _BG_LABEL if ci % 2 == 0 else _BG_WHITE
            v_r = db_results["recent"][country]["Venezuela"][ind_key]
            n_r = db_results["recent"][country]["Native"][ind_key]
            v_e = db_results["early"][country]["Venezuela"][ind_key]
            n_e = db_results["early"][country]["Native"][ind_key]
            _xl_data(ws, r, 1, label if ci == 0 else "", bg=bg, bold=(ci==0))
            _xl_data(ws, r, 2, DB_COUNTRY_LBL[country],                         bg=bg, bold=True)
            _xl_data(ws, r, 3, round(v_r,1) if pd.notna(v_r) else None,         bg=_BG_VEN_R, fmt="0.0")
            _xl_data(ws, r, 4, round(n_r,1) if pd.notna(n_r) else None,         bg=_BG_NAT_R, fmt="0.0")
            _xl_data(ws, r, 5, round(v_e,1) if pd.notna(v_e) else None,         bg=_BG_VEN_E, fmt="0.0")
            _xl_data(ws, r, 6, round(n_e,1) if pd.notna(n_e) else None,         bg=_BG_NAT_E, fmt="0.0")
            gap_r = round(v_r-n_r,1) if (pd.notna(v_r) and pd.notna(n_r)) else None
            gap_e = round(v_e-n_e,1) if (pd.notna(v_e) and pd.notna(n_e)) else None
            _xl_data(ws, r, 7, gap_r, bg=_BG_VEN_E, fmt="+0.0;-0.0;0.0")
            _xl_data(ws, r, 8, gap_e, bg=_BG_NAT_E, fmt="+0.0;-0.0;0.0")
            r += 1
        r += 1  # blank separator between indicators

    _xl_note(ws, r + 1, 8,
             "Per-country estimates. ESP: unemployment and informality masked (harmonization gap in EPA). "
             "Chart tip: filter by Indicator → select cols C–D → Insert Dumbbell/Dot Plot.")


def _sheet_trend(wb, ind_key, trend_title, value_col, denom_group):
    ws = wb.create_sheet(f"Trend_{ind_key[:18]}")
    ws.row_dimensions[1].height = 15
    ws.row_dimensions[2].height = 30
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 10
    for c in "CDEFGHI":
        ws.column_dimensions[c].width = 16

    from openpyxl.styles import Alignment as _Aln
    ws.merge_cells("C1:E1"); _xl_hdr(ws, 1, 3, "Venezuelan", bg=_BG_HDR_V); ws["C1"].alignment = _Aln(horizontal="center",vertical="center")
    ws.merge_cells("F1:H1"); _xl_hdr(ws, 1, 6, "Native",     bg=_BG_HDR_N); ws["F1"].alignment = _Aln(horizontal="center",vertical="center")

    col_hdrs = ["Country", "Period", "Value (%)", "CI lower", "CI upper", "Value (%)", "CI lower", "CI upper"]
    col_bgs  = ["1D3557","1D3557",_BG_HDR_V,_BG_HDR_V,_BG_HDR_V,_BG_HDR_N,_BG_HDR_N,_BG_HDR_N]
    for c, (h, bg) in enumerate(zip(col_hdrs, col_bgs), start=1):
        _xl_hdr(ws, 2, c, h, bg=bg)

    r = 3
    for country in TREND_COUNTRIES:
        ts = _build_trend_series(country, ind_key, value_col, denom_group)
        if ts.empty:
            continue
        for _, row in ts.sort_values("x").iterrows():
            grp = row["group"]
            if grp not in ("Venezuela", "Native"):
                continue
            # accumulate per (country, period): both groups on same row
            pass
        # pivot: one row per period, Venezuelan + Native side by side
        periods_sorted = ts.sort_values("x")["period"].unique()
        for period in periods_sorted:
            sub = ts[ts["period"] == period]
            v_row = sub[sub["group"] == "Venezuela"]
            n_row = sub[sub["group"] == "Native"]
            bg = _BG_LABEL if r % 2 == 0 else _BG_WHITE
            _xl_data(ws, r, 1, TREND_COUNTRY_LBL[country], bg=bg, bold=True)
            _xl_data(ws, r, 2, str(period), bg=bg)
            if not v_row.empty:
                _xl_data(ws, r, 3, round(v_row["p"].iloc[0],    1), bg=_BG_VEN_R, fmt="0.0")
                _xl_data(ws, r, 4, round(v_row["ci_lo"].iloc[0],1), bg=_BG_VEN_E, fmt="0.0")
                _xl_data(ws, r, 5, round(v_row["ci_hi"].iloc[0],1), bg=_BG_VEN_E, fmt="0.0")
            if not n_row.empty:
                _xl_data(ws, r, 6, round(n_row["p"].iloc[0],    1), bg=_BG_NAT_R, fmt="0.0")
                _xl_data(ws, r, 7, round(n_row["ci_lo"].iloc[0],1), bg=_BG_NAT_E, fmt="0.0")
                _xl_data(ws, r, 8, round(n_row["ci_hi"].iloc[0],1), bg=_BG_NAT_E, fmt="0.0")
            r += 1
        r += 1  # blank row between countries

    _xl_note(ws, r + 1, 8,
             f"{trend_title}. 95% CI via linearized Taylor SE. "
             "Chart tip: filter by Country → select cols C+F for line chart; cols D–E and G–H for CI error bars.")


def export_excel(out_dir: str, pooled_results: dict, db_results: dict) -> str:
    """Write one workbook with all presentation data, formatted for easy chart recreation."""
    try:
        from openpyxl import Workbook
    except ImportError:
        print("  openpyxl not available — skipping Excel export")
        return ""

    wb = Workbook()
    wb.remove(wb.active)  # remove default blank sheet

    # ── Population coverage ──────────────────────────────────────────────────
    import re as _re
    sorted_pop = sorted(
        POPULATION_DATA,
        key=lambda row: -(row[4] if not (isinstance(row[4], float) and np.isnan(row[4])) else 0),
    )
    _sheet_population(wb, sorted_pop)

    # ── Age distribution ─────────────────────────────────────────────────────
    _sheet_age(wb, _load_venezuelan())

    # ── Education distribution ────────────────────────────────────────────────
    _sheet_education(wb, _load_venezuelan())

    # ── Pooled indicators ─────────────────────────────────────────────────────
    _sheet_pooled(wb, pooled_results)

    # ── Country-level breakdown ───────────────────────────────────────────────
    _sheet_country_breakdown(wb, db_results)

    # ── Trend sheets ──────────────────────────────────────────────────────────
    for ind_key, trend_title, value_col, denom_group, _ in TREND_TYPES:
        _sheet_trend(wb, ind_key, trend_title, value_col, denom_group)

    path = os.path.join(out_dir, "scl_full_data.xlsx")
    wb.save(path)
    print(f"  Excel saved: {path}")
    return path


def write_latex(out_dir: str, slides: list[str], date_str: str) -> str:
    content = LATEX_HEADER.replace("DATE_PLACEHOLDER", date_str)
    for slide in slides:
        content += slide
    content += LATEX_FOOTER

    path = os.path.join(out_dir, "scl_full_presentation.tex")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  LaTeX written: {path}")
    return path


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate SCL full presentation")
    parser.add_argument("--no-latex", action="store_true", help="Skip LaTeX generation")
    parser.add_argument("--output", default=OUT_DIR, help="Output directory")
    args = parser.parse_args()

    out_dir = args.output
    os.makedirs(out_dir, exist_ok=True)
    print(f"Output: {out_dir}")

    slides = []

    # ── Chart 1: Population Coverage ─────────────────────────────────────────
    print("Generating: population_coverage")
    img_path = plot_population_coverage(out_dir)
    # LaTeX path is relative to the .tex file location (same dir)
    img_rel = os.path.basename(img_path)
    slides.append(build_population_slide(img_rel))

    # ── Chart 2: Age Distribution ────────────────────────────────────────────
    print("Generating: age_distribution")
    img_age = plot_age_distribution(out_dir)
    slides.append(build_age_slide(os.path.basename(img_age)))

    # ── Chart 3: Education Distribution (LAC-4 + Spain) ──────────────────────
    print("Generating: education_distribution")
    img_edu = plot_education_distribution(out_dir)
    slides.append(build_education_slide(os.path.basename(img_edu)))

    # ── Methodology slide (before pooled indicators) ─────────────────────────
    slides.append(build_methodology_slide())

    # ── Charts 4a+4b: Pooled indicator slides (slide 7 style) ────────────────
    print("Computing pooled indicator data")
    pooled_results = _get_pooled_data()
    print("Generating: pooled_a")
    img_pa = plot_pooled_a(out_dir, pooled_results)
    slides.append(build_pooled_slide_a(os.path.basename(img_pa)))
    print("Generating: pooled_b")
    img_pb = plot_pooled_b(out_dir, pooled_results)
    slides.append(build_pooled_slide_b(os.path.basename(img_pb)))

    # ── Annex: Country-level dumbbell breakdowns ──────────────────────────────
    print("Computing dumbbell data")
    db_results  = _get_dumbbell_data()
    print("Generating: annex_indicators_a")
    img_ann_a = plot_annex_indicators_a(out_dir, db_results)
    slides.append(build_annex_country_slide_a(os.path.basename(img_ann_a)))
    print("Generating: annex_indicators_b1")
    img_ann_b1 = plot_annex_indicators_b1(out_dir, db_results)
    slides.append(build_annex_country_slide_b1(os.path.basename(img_ann_b1)))
    print("Generating: annex_indicators_b2")
    img_ann_b2 = plot_annex_indicators_b2(out_dir, db_results)
    slides.append(build_annex_country_slide_b2(os.path.basename(img_ann_b2)))

    # ── Annex: Labor market trend grids (from data, with CI) ─────────────────
    for i, (ind_key, trend_title, value_col, denom_group, _) in enumerate(TREND_TYPES):
        print(f"Generating trend (from data): {ind_key}")
        fname = f"trend_grid_{ind_key}.png"
        img_tr = plot_trend_from_data(out_dir, ind_key, value_col, denom_group, trend_title, fname)
        slides.append(
            build_annex_trend_slide(
                os.path.basename(img_tr), trend_title, section=(i == 0)
            )
        )

    # ── Trend: Tertiary education (COL, PER, CHL, ECU, ESP) ──────────────────
    print("Generating trend: higher_edu")
    plot_trend_higher_education(out_dir)

    # ── Excel export ──────────────────────────────────────────────────────────
    print("Generating: Excel data export")
    export_excel(out_dir, pooled_results, db_results)
    print("Generating: Weighting comparison Excel")
    export_weighting_comparison_excel(out_dir)

    # ── LaTeX ─────────────────────────────────────────────────────────────────
    if not args.no_latex:
        date_str = date.today().strftime("%B %d, %Y")
        tex_path = write_latex(out_dir, slides, date_str)

        # Auto-compile if pdflatex is available
        import subprocess
        try:
            for _ in range(2):
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "scl_full_presentation.tex"],
                    cwd=out_dir, check=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            pdf = tex_path.replace(".tex", ".pdf")
            sz = os.path.getsize(pdf) / 1024
            print(f"  PDF compiled: {pdf}  ({sz:.0f} KB)")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"  pdflatex not available or failed ({e}); run manually.")

    print("Done.")


if __name__ == "__main__":
    main()
