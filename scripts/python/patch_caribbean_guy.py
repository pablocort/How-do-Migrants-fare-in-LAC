"""
patch_caribbean_guy.py
======================
Patches the existing jeremy_caribbean.xlsx to add Guyana (GUY 2021t3)
WITHOUT recreating the file — user's charts and formatting are preserved.

Uses openpyxl load_workbook (keeps all embedded charts).
GUY row goes at row 8 in labor snapshot tables (currently empty gap row).
GUY education table goes at row 35 in education sheets.
"""

import pickle, numpy as np, pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).parent.parent
CACHE_FILE = BASE / "bases armo" / "armo" / "_hdmf_cache.pkl"
DATE_TAG   = "2026-05-13"
OUT_FILE   = BASE / "out" / "jeremy" / DATE_TAG / "jeremy_caribbean.xlsx"

GUY_COUNTRY    = "GUY"
GUY_PERIOD     = "2021t3"
GUY_LABEL      = "Guyana"
GUY_FILL_HEX   = "E8EAF6"    # light indigo — distinct from BLZ/BRB/SUR/DOM

GROUP_COL = "migrante_ci"
GROUPS    = ["Native", "Migrant"]

# ---------------------------------------------------------------------------
# Style helpers (mirrors build_jeremy_caribbean.py)
# ---------------------------------------------------------------------------
def _fill(hex_col):
    return PatternFill("solid", fgColor=hex_col)

def _thin():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def _med_bottom():
    med = Side(style="medium", color="888888")
    thn = Side(style="thin",   color="CCCCCC")
    return Border(left=thn, right=thn, top=thn, bottom=med)

C_NAVY = "1D3557"

# ---------------------------------------------------------------------------
# Load cache
# ---------------------------------------------------------------------------
print("Loading cache ...")
with open(CACHE_FILE, "rb") as fh:
    _cache = pickle.load(fh)
data = _cache["data"]

guy = data[data["pais_c"] == GUY_COUNTRY].copy()
guy_wave = guy[guy["periodo_c"] == GUY_PERIOD].copy()
print(f"  GUY rows: {len(guy):,}  |  period {GUY_PERIOD}: {len(guy_wave):,}")

if len(guy_wave) == 0:
    raise RuntimeError(
        f"No GUY data found in cache for period {GUY_PERIOD}. "
        "Run hdmf_build.py first to rebuild the cache with GUY_2021t3_BID.dta."
    )

# ---------------------------------------------------------------------------
# Weighted mean helper
# ---------------------------------------------------------------------------
def _wavg(series, weights):
    v = pd.to_numeric(series, errors="coerce").to_numpy(float)
    w = pd.to_numeric(weights, errors="coerce").to_numpy(float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if mask.sum() == 0:
        return np.nan
    v_, w_ = v[mask], w[mask]
    return float(np.dot(w_, v_) / w_.sum())

# ---------------------------------------------------------------------------
# Compute GUY labor indicators (same logic as build_jeremy_caribbean.py)
# ---------------------------------------------------------------------------
wa_mask = guy_wave["edad_ci"].between(16, 64)

guy_wave = guy_wave.copy()
guy_wave["wap_ci"]   = guy_wave["edad_ci"].between(15, 64).astype(int)
guy_wave["inact_ci"] = guy_wave["inactivo_ci"].where(wa_mask, np.nan)
guy_wave["desemp_r"] = (
    guy_wave["desemp_ci"]
    .where(wa_mask, np.nan)
    .where(guy_wave["pea_ci"] == 1, np.nan)
)
guy_wave["informal"] = np.where(
    (guy_wave["emp_ci"] == 1) & wa_mask,
    1 - pd.to_numeric(guy_wave["formal_ci"], errors="coerce"),
    np.nan
)

INDICATORS = {
    "unemployment": "desemp_r",
    "informality":  "informal",
    "inactivity":   "inact_ci",
    "wap":          "wap_ci",
}

guy_ind = {}
for ind_key, col in INDICATORS.items():
    row = {}
    for grp in GROUPS:
        sub = guy_wave[guy_wave[GROUP_COL] == grp]
        mu  = _wavg(sub[col], sub["factor_ci"])
        row[grp] = round(mu * 100, 2) if pd.notna(mu) else np.nan
    guy_ind[ind_key] = row
    print(f"  {ind_key}: Native={row['Native']:.2f}%  Migrant={row.get('Migrant', float('nan')):.2f}%"
          if pd.notna(row.get("Native")) else f"  {ind_key}: no data")

# ---------------------------------------------------------------------------
# Compute GUY education distribution
# ---------------------------------------------------------------------------
EDU_3CAT_MAP = {
    1: "Primary or less", 2: "Primary or less", 3: "Primary or less",
    4: "Secondary",       5: "Secondary",       6: "Secondary",
    7: "Higher education", 8: "Higher education",
    9: "Higher education", 10: "Higher education",
}
EDU_ORDER = ["Primary or less", "Secondary", "Higher education", "Total"]

dfc = guy_wave.copy()
dfc["edu_3cat"] = pd.to_numeric(dfc["edu_hdmf"], errors="coerce").map(EDU_3CAT_MAP)
dfc = dfc[dfc["edu_3cat"].notna() & dfc["factor_ci"].notna()]

abs_rows, pct_rows = [], []
for cat in EDU_ORDER[:-1]:
    abs_row = {"Education level": cat}
    pct_row = {"Education level": cat}
    for grp in GROUPS:
        dfg   = dfc[dfc[GROUP_COL] == grp]
        total = dfg["factor_ci"].sum()
        cat_w = dfg.loc[dfg["edu_3cat"] == cat, "factor_ci"].sum()
        abs_row[grp] = int(round(cat_w))
        pct_row[grp] = round(cat_w / total * 100, 2) if total > 0 else np.nan
    abs_rows.append(abs_row)
    pct_rows.append(pct_row)

abs_tot = {"Education level": "Total"}
pct_tot = {"Education level": "Total"}
for grp in GROUPS:
    dfg = dfc[dfc[GROUP_COL] == grp]
    tot = dfg["factor_ci"].sum()
    abs_tot[grp] = int(round(tot))
    pct_tot[grp] = 100.0
abs_rows.append(abs_tot)
pct_rows.append(pct_tot)

guy_edu_abs = pd.DataFrame(abs_rows).set_index("Education level")
guy_edu_pct = pd.DataFrame(pct_rows).set_index("Education level")

print("\nGUY education %:")
print(guy_edu_pct.to_string())

# ---------------------------------------------------------------------------
# Open existing Excel (preserves user's charts)
# ---------------------------------------------------------------------------
print(f"\nOpening: {OUT_FILE}")
wb = load_workbook(OUT_FILE)

# ---------------------------------------------------------------------------
# Patch labor indicator sheets
# ---------------------------------------------------------------------------
IND_COLORS = {
    "unemployment": ("FDE9D9", "C55A11"),
    "informality":  ("DEEAF1", "2E75B6"),
    "inactivity":   ("E8F4F8", "1A7A6E"),
    "wap":          ("F2E7FA", "7030A0"),
}

for ind_key in INDICATORS:
    if ind_key not in wb.sheetnames:
        print(f"  WARNING: sheet '{ind_key}' not found, skipping")
        continue

    ws = wb[ind_key]
    hdr_color = IND_COLORS[ind_key][1]

    # Update snapshot title (row 3, col 1) to include GUY
    title_cell = ws.cell(3, 1)
    title_cell.value = "BLZ / BRB / SUR / GUY  —  Single-wave snapshot"
    # Re-apply formatting (value changed, keep existing style)

    # Write GUY at row 8 (currently empty gap row)
    dr = 8
    nat_val = guy_ind[ind_key].get("Native",  np.nan)
    mig_val = guy_ind[ind_key].get("Migrant", np.nan)

    lbl_cell = ws.cell(dr, 1, f"{GUY_LABEL}  ({GUY_PERIOD})")
    lbl_cell.font      = Font(size=9)
    lbl_cell.fill      = _fill(GUY_FILL_HEX)
    lbl_cell.alignment = Alignment(horizontal="left", vertical="center")
    lbl_cell.border    = _thin()
    ws.row_dimensions[dr].height = 14

    for ci, val in enumerate([nat_val, mig_val], start=2):
        dc = ws.cell(dr, ci, val if pd.notna(val) else None)
        dc.font          = Font(size=9)
        dc.fill          = _fill(GUY_FILL_HEX)
        dc.alignment     = Alignment(horizontal="right", vertical="center")
        dc.number_format = "0.00"
        dc.border        = _thin()

    print(f"  Patched sheet '{ind_key}' — GUY row 8: Native={nat_val}  Migrant={mig_val}")

# ---------------------------------------------------------------------------
# Patch education sheets
# ---------------------------------------------------------------------------
EDU_COLOR_HDR = "7F6000"

for sheet_label, df_table, num_fmt in [
    ("education_abs", guy_edu_abs, "#,##0"),
    ("education_pct", guy_edu_pct, "0.00"),
]:
    if sheet_label not in wb.sheetnames:
        print(f"  WARNING: sheet '{sheet_label}' not found, skipping")
        continue

    ws = wb[sheet_label]
    start_row = 35

    # Title row
    ws.cell(start_row, 1, f"{GUY_LABEL}  ({GUY_PERIOD})").font      = Font(bold=True, size=11, color="FFFFFF")
    ws.cell(start_row, 1).fill                                        = _fill(C_NAVY)
    ws.cell(start_row, 1).alignment                                   = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[start_row].height                               = 20
    for c in range(2, 4):
        ws.cell(start_row, c).fill = _fill(C_NAVY)

    # Header row
    hr = start_row + 1
    for ci, lbl in enumerate(["Education level", "Native", "Migrant"], start=1):
        cell = ws.cell(hr, ci, lbl)
        cell.font      = Font(bold=True, size=10, color="FFFFFF")
        cell.fill      = _fill(EDU_COLOR_HDR)
        cell.alignment = Alignment(
            horizontal="left" if ci == 1 else "center", vertical="center"
        )
        cell.border = _thin()
    ws.row_dimensions[hr].height = 18

    # Data rows
    for ri, (idx, row) in enumerate(df_table.iterrows()):
        dr       = hr + 1 + ri
        shade    = GUY_FILL_HEX if ri % 2 == 0 else "FFFFFF"
        is_total = str(idx) == "Total"

        lbl_cell = ws.cell(dr, 1, str(idx))
        lbl_cell.font      = Font(bold=is_total, size=9)
        lbl_cell.fill      = _fill("F0F0F0") if is_total else _fill(shade)
        lbl_cell.alignment = Alignment(horizontal="left", vertical="center")
        lbl_cell.border    = _med_bottom() if is_total else _thin()

        for ci, val in enumerate(row, start=2):
            dc = ws.cell(dr, ci, val if pd.notna(val) else None)
            dc.font          = Font(bold=is_total, size=9)
            dc.fill          = _fill("F0F0F0") if is_total else _fill(shade)
            dc.alignment     = Alignment(horizontal="right", vertical="center")
            dc.number_format = num_fmt
            dc.border        = _med_bottom() if is_total else _thin()
        ws.row_dimensions[dr].height = 14

    print(f"  Patched sheet '{sheet_label}' — GUY rows {start_row}-{hr + len(df_table)}")

# ---------------------------------------------------------------------------
# Save back (preserves all other content including user's chart)
# ---------------------------------------------------------------------------
wb.save(OUT_FILE)
print(f"\nSaved: {OUT_FILE}")
print("Charts and existing content preserved via load_workbook().")
