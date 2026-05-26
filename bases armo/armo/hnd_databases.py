"""
hnd_databases.py
Build two Honduras EPHPM output databases from harmonized BID.dta files.

Outputs:
  out/hnd/HND_all_waves.csv        -- all 7 waves stacked, one row per person
  out/hnd/HND_panel_geo_year.csv   -- geographic unit x year panel
"""

import os
import sys
import numpy as np
import pandas as pd
import pyreadstat

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root
DTA_DIR = os.path.join(PROJ, "bases armo", "armo", "HND")
OUT_DIR = os.path.join(PROJ, "out", "remittances", "data")
os.makedirs(OUT_DIR, exist_ok=True)

WAVES = [
    "HND_2018m6_BID.dta",
    "HND_2019m6_BID.dta",
    "HND_2021m6_BID.dta",
    "HND_2022m6_BID.dta",
    "HND_2023m6_BID.dta",
    "HND_2024m6_BID.dta",
    "HND_2025m7_BID.dta",
]

# ---------------------------------------------------------------------------
# Load all waves
# ---------------------------------------------------------------------------
print("Loading DTA files...")
frames = []
for fname in WAVES:
    path = os.path.join(DTA_DIR, fname)
    try:
        df, meta = pyreadstat.read_dta(path)
        loader = "pyreadstat"
    except Exception:
        # saveold format uses legacy encoding; fall back to pandas
        df = pd.read_stata(path, convert_categoricals=False)
        loader = "pandas"
    print(f"  {fname}: {len(df):,} rows, {len(df.columns)} cols [{loader}]")
    frames.append(df)

all_waves = pd.concat(frames, ignore_index=True, sort=False)
print(f"\nTotal stacked: {len(all_waves):,} rows, {len(all_waves.columns)} cols")

# ---------------------------------------------------------------------------
# Database 1 — full stacked CSV
# ---------------------------------------------------------------------------
out_csv = os.path.join(OUT_DIR, "HND_all_waves.csv")
all_waves.to_csv(out_csv, index=False)
print(f"\nDatabase 1 saved: {out_csv}")
print(f"  Size: {os.path.getsize(out_csv)/1e6:.1f} MB")

# ---------------------------------------------------------------------------
# Database 2 — geographic panel
# ---------------------------------------------------------------------------

def weighted_mean(values, weights):
    mask = ~(np.isnan(values) | np.isnan(weights)) & (weights > 0)
    if mask.sum() == 0:
        return np.nan
    v, w = values[mask], weights[mask]
    return np.average(v, weights=w)

def weighted_median(values, weights):
    mask = ~(np.isnan(values) | np.isnan(weights)) & (weights > 0)
    if mask.sum() == 0:
        return np.nan
    v, w = values[mask], weights[mask]
    idx = np.argsort(v)
    v, w = v[idx], w[idx]
    cumw = np.cumsum(w)
    midpoint = cumw[-1] / 2.0
    return float(v[cumw >= midpoint][0])

def wmean(df, col, wt="factor_ci"):
    if col not in df.columns:
        return np.nan
    return weighted_mean(df[col].values.astype(float), df[wt].values.astype(float))

def wmedian(df, col, wt="factor_ci"):
    if col not in df.columns:
        return np.nan
    return weighted_median(df[col].values.astype(float), df[wt].values.astype(float))

def wsum(df, col):
    mask = ~np.isnan(df[col].values.astype(float)) & ~np.isnan(df["factor_ci"].values.astype(float))
    if mask.sum() == 0:
        return np.nan
    return (df.loc[mask, col].astype(float) * df.loc[mask, "factor_ci"].astype(float)).sum()

# Build geo_unit column
df = all_waves.copy()

# For 2021/2022: no region_c (dept) — use upm_ci (dominio 1-5)
df["geo_unit"] = df["region_c"].copy()
df["geo_type"] = "depto"

# 2021, 2022, 2023 have no department — use upm_ci (dominio 1-5)
mask_no_dept = df["anio_c"].isin([2021, 2022, 2023])
df.loc[mask_no_dept, "geo_unit"] = df.loc[mask_no_dept, "upm_ci"]
df.loc[mask_no_dept, "geo_type"] = "dominio"

# Drop rows where geo_unit is still missing (should not happen)
df = df[~df["geo_unit"].isna()].copy()
df["geo_unit"] = df["geo_unit"].astype(int)

# Universe masks
def age_mask(d, lo, hi):
    return (d["edad_ci"] >= lo) & (d["edad_ci"] <= hi)

records = []
for (year, geo, geo_type), g in df.groupby(["anio_c", "geo_unit", "geo_type"]):
    w15_64 = g[age_mask(g, 15, 64)]
    w15p   = g[age_mask(g, 15, 200)]
    w_emp  = g[g["emp_ci"] == 1]
    w_pea  = g[(g["pea_ci"] == 1) & age_mask(g, 15, 64)]

    rec = {
        "anio_c":   year,
        "geo_unit": geo,
        "geo_type": geo_type,
        # Population
        "pop_total":        g["factor_ci"].sum() if "factor_ci" in g.columns else np.nan,
        # Demographics (all ages)
        "pct_urban":        wmean(g, "zona_c"),
        "age_mean":         wmean(g, "edad_ci"),
        "pct_female":       weighted_mean((g["sexo_ci"] == 2).values.astype(float),
                                          g["factor_ci"].values.astype(float))
                            if "sexo_ci" in g.columns else np.nan,
        "pct_migrant":      wmean(g, "migrante_ci"),
        # Labor (15-64)
        "pea_rate":         wmean(w15_64, "pea_ci"),
        "emp_rate":         wmean(w15_64, "emp_ci"),
        "unemp_rate":       wmean(w_pea,  "desemp_ci"),
        "formal_rate":      wmean(w_emp,  "formal_ci"),
        "cotizando_rate":   wmean(w_emp,  "cotizando_ci"),
        # Education (15-64)
        "aedu_mean":        wmean(w15_64, "aedu_ci"),
        "pct_tertiary":     weighted_mean((w15_64["edu_hdmf"] >= 6).values.astype(float),
                                          w15_64["factor_ci"].values.astype(float))
                            if ("edu_hdmf" in w15_64.columns and len(w15_64) > 0) else np.nan,
        # Income — employed
        "ylm_mean":         wmean(w_emp,  "ylm_ci"),
        "ylm_median":       wmedian(w_emp, "ylm_ci"),
        # Total income — 15+
        "ytot_mean":        wmean(w15p,   "ytot_ci"),
        "ytot_median":      wmedian(w15p,  "ytot_ci"),
        # Remittances — all ages
        "remesas_mean":     wmean(g,       "remesas_ci"),
        "remesas_median":   wmedian(g,     "remesas_ci"),
        "pct_remesas":      weighted_mean((g["remesas_ci"] > 0).values.astype(float),
                                          g["factor_ci"].values.astype(float))
                            if "remesas_ci" in g.columns else np.nan,
        # Poverty / diversity — all ages
        "pobre_rate":       wmean(g, "pobre_ine_ci"),
        "pct_afro":         wmean(g, "afro_ci"),
        "pct_ind":          wmean(g, "ind_ci"),
        "pct_dis":          wmean(g, "dis_ci"),
    }
    records.append(rec)

panel = pd.DataFrame(records).sort_values(["anio_c", "geo_type", "geo_unit"]).reset_index(drop=True)

out_panel = os.path.join(OUT_DIR, "HND_panel_geo_year.csv")
panel.to_csv(out_panel, index=False)
print(f"\nDatabase 2 saved: {out_panel}")
print(f"  Rows: {len(panel):,}  |  Cols: {len(panel.columns)}")
print(f"  Years: {sorted(panel['anio_c'].unique())}")
print(f"  Geo types: {panel['geo_type'].value_counts().to_dict()}")
print(f"\nSample rows:")
print(panel[panel["geo_type"] == "depto"].head(3).to_string(index=False))
print()
print(panel[panel["geo_type"] == "dominio"].head(3).to_string(index=False))
print("\nDone.")
