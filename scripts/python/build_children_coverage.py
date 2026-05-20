#!/usr/bin/env python3
"""
build_children_coverage.py
Population coverage chart for Venezuelan-origin children.

Produces out/scl_full/YYYY-MM-DD/children_coverage.png

Two bar types per country:
  1. Venezuelan children  — edad_ci < 18, born in Venezuela
  2. Children w/ Ven head — edad_ci < 18, household head born in Venezuela
                            (computed on-the-fly from relacion_ci + mig_pais_ci)

Usage:
    py build_children_coverage.py
    py build_children_coverage.py --out-dir out/scl_full/2026-05-19
"""

import argparse
import os
import re
from datetime import date

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Inter", "Arial", "DejaVu Sans"]
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

# =============================================================================
# CONFIG
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ARMO_DIR = os.path.join(BASE_DIR, "bases armo", "armo")

# Most-recent wave per country (folder / filename)
WAVES = {
    "COL": ("col", "COL_2025t3_BID.dta",  "2025t3"),
    "ECU": ("ecu", "ECU_2025m12_BID.dta", "2025m12"),
    "PER": ("per", "PER_2024a_BID.dta",   "2024a"),
    "CHL": ("chl", "CHL_2024a_BID.dta",   "2024a"),
    "ESP": ("ESP", "ESP_2025a_BID.dta",   "2025a"),
    "USA": ("usa", "USA_2024_BID.dta",    "2024a"),
}

COUNTRY_FULL = {
    "COL": "Colombia",
    "ECU": "Ecuador",
    "PER": "Peru",
    "CHL": "Chile",
    "ESP": "Spain",
    "USA": "United States",
}

# Survey upscale factors (same as scl_presentation.py)
SURVEY_UPSCALE = {
    "PER": round(1_600_000 / 188_083, 3),
    "ECU": round(  440_400 / 130_649, 3),
}

# R4V order for x-axis (COL largest → ECU smallest)
COUNTRY_ORDER = ["COL", "PER", "USA", "CHL", "ESP", "ECU"]

DPI = 150

C_VEN_CHILD   = "#B84A2A"   # burnt sienna — Venezuelan children (union)
C_VEN_HEAD    = "#2171A0"   # steel blue — children with Venezuelan head

# =============================================================================
# HELPERS
# =============================================================================

def _is_ven(s):
    """Return True if mig_pais_ci string refers to Venezuela (any variant)."""
    if pd.isna(s) or str(s).strip() == "":
        return False
    return "venezuela" in str(s).lower()


def _wave_year(period: str) -> str:
    m = re.search(r"\d{4}", str(period))
    return m.group(0) if m else str(period)


def _fmt_pop(v):
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}k"
    return str(int(v))


def _strip_spines(ax):
    for sp in ax.spines.values():
        sp.set_visible(False)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_country(iso: str):
    """Load BID.dta for the most-recent wave of a country.
    Returns a DataFrame with columns needed for children analysis.
    Also computes hhd_ven_head on-the-fly from relacion_ci + mig_pais_ci.
    """
    folder, fname, period = WAVES[iso]
    path = os.path.join(ARMO_DIR, folder, fname)
    if not os.path.exists(path):
        print(f"  [SKIP] {iso}: file not found — {path}")
        return None, period

    needed = ["idh_ch", "edad_ci", "factor_ci", "mig_pais_ci", "jefe_ci", "relacion_ci", "idp_ci"]
    # Read without column filter first so we can check what exists
    df = pd.read_stata(path, convert_categoricals=False)
    missing = [c for c in needed if c not in df.columns]
    if missing:
        print(f"  [WARN] {iso}: missing columns {missing}")
    # USA fallback: idh_ch absent because 'cap egen idh_ch = serial' silently fails
    if "idh_ch" not in df.columns:
        for alt in ("serial", "hhid", "folio"):
            if alt in df.columns:
                df["idh_ch"] = df[alt].astype(str)
                print(f"  [INFO] {iso}: using '{alt}' as idh_ch")
                break
        else:
            df["idh_ch"] = df.index.astype(str)  # last resort: each person unique HH
            print(f"  [WARN] {iso}: no household ID found — hhd_ven_head will be 0")

    df["pais_c"] = iso

    # Decode string column if stored as bytes
    for col in ["mig_pais_ci", "idh_ch"]:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].apply(
                lambda x: x.decode("utf-8", errors="replace") if isinstance(x, bytes) else str(x) if pd.notna(x) else ""
            )

    # Identify household head using jefe_ci; fallback to relacion_ci==1 or idp_ci==1 (IPUMS)
    if "jefe_ci" in df.columns and df["jefe_ci"].notna().any():
        head_mask = (df["jefe_ci"] == 1) & df["mig_pais_ci"].apply(_is_ven)
    elif "relacion_ci" in df.columns and df["relacion_ci"].notna().any():
        head_mask = (df["relacion_ci"] == 1) & df["mig_pais_ci"].apply(_is_ven)
        print(f"  [INFO] {iso}: jefe_ci absent — using relacion_ci==1")
    elif "idp_ci" in df.columns:
        head_mask = (df["idp_ci"] == 1) & df["mig_pais_ci"].apply(_is_ven)
        print(f"  [INFO] {iso}: jefe_ci absent — using idp_ci==1 (IPUMS fallback)")
    else:
        head_mask = pd.Series(False, index=df.index)
        print(f"  [WARN] {iso}: cannot identify household head")

    # Propagate Venezuelan-head flag to all household members
    df["_head_ven"] = head_mask.astype(int)
    df["hhd_ven_head"] = df.groupby("idh_ch")["_head_ven"].transform("max")
    df.drop(columns=["_head_ven"], inplace=True)

    # Venezuelan-born flag
    df["ven_born"] = df["mig_pais_ci"].apply(_is_ven).astype(int)

    return df, period


# =============================================================================
# COMPUTE COUNTS
# =============================================================================

def compute_counts():
    results = []
    for iso in COUNTRY_ORDER:
        if iso not in WAVES:
            continue
        df, period = load_country(iso)
        if df is None:
            continue

        scale = SURVEY_UPSCALE.get(iso, 1.0)
        children = df[df["edad_ci"] < 18].copy()

        # Weighted counts
        w_ven    = children.loc[children["ven_born"]    == 1, "factor_ci"].sum()
        w_head   = children.loc[children["hhd_ven_head"] == 1, "factor_ci"].sum()
        w_union  = children.loc[
            (children["ven_born"] == 1) | (children["hhd_ven_head"] == 1),
            "factor_ci"
        ].sum()
        # v2: non-Venezuelan children living with a Venezuelan head
        w_nonven_head = children.loc[
            (children["ven_born"] == 0) & (children["hhd_ven_head"] == 1),
            "factor_ci"
        ].sum()

        total_pop_survey = df["factor_ci"].sum()
        n_survey         = len(df)
        n_ven_survey     = (df["ven_born"] == 1).sum()
        ven_pop_survey   = df.loc[df["ven_born"] == 1, "factor_ci"].sum()

        results.append({
            "iso":              iso,
            "period":           period,
            "label":            f"{COUNTRY_FULL.get(iso, iso)}\n({_wave_year(period)})",
            "ven_child":        w_ven          * scale,
            "ven_head":         w_head         * scale,
            "union":            w_union        * scale,
            "nonven_head":      w_nonven_head  * scale,
            "scale":            scale,
            "n_survey":         n_survey,
            "total_pop_survey": total_pop_survey,   # unscaled — survey weights already represent full country
            "n_ven_survey":     n_ven_survey,
            "ven_pop_survey":   ven_pop_survey,
            "ven_pop_scaled":   ven_pop_survey * scale,  # scale only applied to Venezuelan count
        })
        print(f"  {iso:4s}  ven_children={w_ven*scale:,.0f}  w_head={w_head*scale:,.0f}  union={w_union*scale:,.0f}  (scale={scale:.2f})")

    return results


# =============================================================================
# POPULATION TABLE
# =============================================================================

def print_population_table(results, out_dir: str):
    """Print and save a verification table of total and Venezuelan population per country."""
    rows = []
    for r in results:
        ven_pct = r["ven_pop_scaled"] / r["total_pop_survey"] * 100 if r["total_pop_survey"] > 0 else np.nan
        rows.append({
            "Country":           COUNTRY_FULL.get(r["iso"], r["iso"]),
            "Period":            r["period"],
            "Survey n":          f"{r['n_survey']:,}",
            "Total pop":         f"{r['total_pop_survey']/1e6:.2f}M",
            "Ven n (survey)":    f"{r['n_ven_survey']:,}",
            "Ven pop (survey)":  f"{r['ven_pop_survey']/1e6:.2f}M",
            "Ven scale":         f"{r['scale']:.3f}",
            "Ven pop (scaled)":  f"{r['ven_pop_scaled']/1e6:.2f}M",
            "Ven % of total":    f"{ven_pct:.1f}%",
        })
    df_tbl = pd.DataFrame(rows)

    print()
    print("=" * 90)
    print("POPULATION VERIFICATION TABLE")
    print("=" * 90)
    print(df_tbl.to_string(index=False))
    print("=" * 90)
    print("Note: 'Total pop' = survey-weighted total (no upscale). 'Ven pop (scaled)' applies R4V/survey ratio to Venezuelan count only (PER x8.51, ECU x3.37).")
    print()

    csv_path = os.path.join(out_dir, "population_verification.csv")
    df_tbl.to_csv(csv_path, index=False)
    print(f"  Table saved: {csv_path}")


# =============================================================================
# CHART
# =============================================================================

def plot_children_coverage(results, out_dir: str) -> str:
    n   = len(results)
    x   = np.arange(n)
    w   = 0.30
    off = [-w * 0.55, w * 0.55]

    sources = [
        ("Venezuelan children (born in VEN)",          C_VEN_CHILD,  "union"),
        ("Children with Venezuelan household head",    C_VEN_HEAD,   "ven_head"),
    ]

    fig, ax = plt.subplots(figsize=(max(12, n * 2.2), 5.5))

    all_vals = [r[k] for r in results for k in ("union", "ven_head") if r[k] > 0]
    y_max = max(all_vals) * 1.30 if all_vals else 1
    ax.set_ylim(0, y_max)
    lbl_off = y_max * 0.022

    for si, (label, color, key) in enumerate(sources):
        for xi, row in zip(x + off[si], results):
            val = row[key]
            if val <= 0:
                continue
            ax.bar(xi, val, w, color=color, alpha=0.88, zorder=3)
            ax.text(xi, val + lbl_off, _fmt_pop(val),
                    ha="center", va="bottom", fontsize=8,
                    color="black", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([r["label"] for r in results], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_pop(v)))
    ax.set_ylabel("Children (age 0–17)", fontsize=11)
    ax.set_title(
        "Venezuelan-Origin Children: Population Estimates by Country",
        fontsize=12, pad=10,
    )
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    _strip_spines(ax)

    handles = [Patch(facecolor=c, alpha=0.88, label=lbl) for lbl, c, _ in sources]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.01),
               ncol=3, frameon=False, fontsize=9)

    fig.tight_layout(rect=[0, 0.08, 1, 1])

    path = os.path.join(out_dir, "children_coverage.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {path}")
    return path


def plot_children_coverage_v2(results, out_dir: str) -> str:
    """v2: Bar 1 = Venezuelan-born children; Bar 2 = non-Venezuelan children with Venezuelan head."""
    n   = len(results)
    x   = np.arange(n)
    w   = 0.30
    off = [-w * 0.55, w * 0.55]

    C_VEN_CHILD_V2 = "#B84A2A"   # burnt sienna — Venezuelan-born children
    C_NONVEN_HEAD  = "#5B9E6E"   # green — non-Venezuelan children, Venezuelan head

    sources = [
        ("Venezuelan children (born in VEN)",                      C_VEN_CHILD_V2, "ven_child"),
        ("Non-Venezuelan children with Venezuelan household head",  C_NONVEN_HEAD,  "nonven_head"),
    ]

    fig, ax = plt.subplots(figsize=(max(12, n * 2.2), 5.5))

    all_vals = [r[k] for r in results for k in ("ven_child", "nonven_head") if r[k] > 0]
    y_max = max(all_vals) * 1.30 if all_vals else 1
    ax.set_ylim(0, y_max)
    lbl_off = y_max * 0.022

    for si, (label, color, key) in enumerate(sources):
        for xi, row in zip(x + off[si], results):
            val = row[key]
            if val <= 0:
                continue
            ax.bar(xi, val, w, color=color, alpha=0.88, zorder=3)
            ax.text(xi, val + lbl_off, _fmt_pop(val),
                    ha="center", va="bottom", fontsize=8,
                    color="black", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([r["label"] for r in results], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _fmt_pop(v)))
    ax.set_ylabel("Children (age 0–17)", fontsize=11)
    ax.set_title(
        "Venezuelan-Origin Children: Population Estimates by Country",
        fontsize=12, pad=10,
    )
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    _strip_spines(ax)

    handles = [Patch(facecolor=c, alpha=0.88, label=lbl) for lbl, c, _ in sources]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.01),
               ncol=2, frameon=False, fontsize=9)

    fig.tight_layout(rect=[0, 0.08, 1, 1])

    path = os.path.join(out_dir, "children_coverage_v2.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {path}")
    return path


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=None,
                        help="Output directory (default: out/scl_full/YYYY-MM-DD)")
    args = parser.parse_args()

    date_tag = date.today().strftime("%Y-%m-%d")
    out_dir  = args.out_dir or os.path.join(BASE_DIR, "out", "scl_full", date_tag)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Output: {out_dir}\n")
    print("Loading country data...")
    results = compute_counts()

    if not results:
        print("No data loaded — check BID.dta paths.")
        return

    print_population_table(results, out_dir)

    print("\nGenerating: children_coverage")
    plot_children_coverage(results, out_dir)
    print("\nGenerating: children_coverage_v2")
    plot_children_coverage_v2(results, out_dir)
    print("Done.")


if __name__ == "__main__":
    main()
