"""
build_jeremy_edu_labor_unweighted.py  --  Unweighted education × labor cross-tab
==================================================================================
Output: out/jeremy/2026-05-13/jeremy_edu_labor_unweighted.xlsx

Identical structure to jeremy_edu_labor.xlsx but computations use raw observation
counts (N) instead of survey weights (factor_ci).

Each cell shows:
  Rate (%) : unweighted mean of the indicator (simple proportion of N obs)
  N        : number of non-missing observations used

Sheet layout: one sheet per indicator, same double-header structure,
but each education × migration group now has TWO columns: % and N.
"""

import os, pickle, numpy as np, pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = Path(__file__).parent.parent
CACHE_FILE = BASE / "bases armo" / "armo" / "_hdmf_cache.pkl"
DATE_TAG   = "2026-05-13"
OUT_DIR    = BASE / "out" / "jeremy" / DATE_TAG
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE   = OUT_DIR / "jeremy_edu_labor_unweighted.xlsx"

CARIBBEAN    = ["BLZ", "BRB", "SUR", "GUY"]
DOM          = "DOM"
RECENT_WAVES = {"BLZ": "2024m9", "BRB": "2023a", "SUR": "2022a", "GUY": "2021t3"}
GROUPS       = ["Native", "Migrant"]
GROUP_COL    = "migrante_ci"

COUNTRY_LABEL = {
    "BLZ": "Belize",
    "BRB": "Barbados",
    "SUR": "Suriname",
    "GUY": "Guyana",
    "DOM": "Dominican Republic",
}

EDU_3CAT_MAP = {
    1: "Primary or less", 2: "Primary or less", 3: "Primary or less",
    4: "Secondary",       5: "Secondary",       6: "Secondary",
    7: "Higher ed", 8: "Higher ed", 9: "Higher ed", 10: "Higher ed",
}
EDU_CATS  = ["Primary or less", "Secondary", "Higher ed"]
EDU_TOTAL = "Total"

# ---------------------------------------------------------------------------
# Load cache
# ---------------------------------------------------------------------------
print("Loading cache ...")
with open(CACHE_FILE, "rb") as fh:
    _cache = pickle.load(fh)
data = _cache["data"]

all_carib = CARIBBEAN + [DOM]
df = data[data["pais_c"].isin(all_carib)].copy()
df["year"] = df["periodo_c"].str.extract(r"(\d{4})").astype(int)

print(f"  Caribbean + DOM rows: {len(df):,}")
for c in all_carib:
    sub = df[df["pais_c"] == c]
    print(f"    {c}: {len(sub):,}  periods: {sorted(sub['periodo_c'].unique())}")

df["edu_3cat"] = pd.to_numeric(df["edu_hdmf"], errors="coerce").map(EDU_3CAT_MAP)

# ---------------------------------------------------------------------------
# Derived indicators
# ---------------------------------------------------------------------------
wa_mask = df["edad_ci"].between(16, 64)

df["wap_ci"]   = df["edad_ci"].between(15, 64).astype(int)
df["inact_ci"] = df["inactivo_ci"].where(wa_mask, np.nan)
df["desemp_r"] = (df["desemp_ci"]
                  .where(wa_mask, np.nan)
                  .where(df["pea_ci"] == 1, np.nan))
df["informal"] = np.where(
    (df["emp_ci"] == 1) & wa_mask,
    1 - pd.to_numeric(df["formal_ci"], errors="coerce"),
    np.nan
)
df["occup_ci"] = np.where(wa_mask, pd.to_numeric(df["emp_ci"], errors="coerce"), np.nan)

INDICATORS = {
    "unemployment": ("desemp_r",  "Unemployment rate — unweighted % (N obs)"),
    "informality":  ("informal",  "Informality rate — unweighted % (N obs)"),
    "inactivity":   ("inact_ci",  "Inactivity rate — unweighted % (N obs)"),
    "wap":          ("wap_ci",    "Working-age pop. share — unweighted % (N obs)"),
    "occupation":   ("occup_ci",  "Occupation rate — unweighted % of WAP 16-64 employed (N obs)"),
}

# ---------------------------------------------------------------------------
# Unweighted helpers
# ---------------------------------------------------------------------------
def _umean(series):
    v = pd.to_numeric(series, errors="coerce")
    if v.notna().sum() == 0:
        return np.nan
    return float(v.mean())

def _n(series):
    return int(pd.to_numeric(series, errors="coerce").notna().sum())

# ---------------------------------------------------------------------------
# Core: compute unweighted indicator + N by edu_cat x group
# ---------------------------------------------------------------------------
def _compute_row(dfp, ind_col):
    """Return dict: {(edu_cat, group, 'pct'): value, (edu_cat, group, 'n'): value}"""
    result = {}
    for edu in EDU_CATS:
        dfe = dfp[dfp["edu_3cat"] == edu]
        for grp in GROUPS:
            sub = dfe[dfe[GROUP_COL] == grp]
            s   = sub[ind_col]
            mu  = _umean(s)
            result[(edu, grp, "pct")] = round(mu * 100, 2) if pd.notna(mu) else np.nan
            result[(edu, grp, "n")]   = _n(s)
    for grp in GROUPS:
        sub = dfp[dfp[GROUP_COL] == grp]
        s   = sub[ind_col]
        mu  = _umean(s)
        result[(EDU_TOTAL, grp, "pct")] = round(mu * 100, 2) if pd.notna(mu) else np.nan
        result[(EDU_TOTAL, grp, "n")]   = _n(s)
    return result

# ---------------------------------------------------------------------------
# Build data tables
# ---------------------------------------------------------------------------
print("\nComputing unweighted education × labor cross-tabs ...")

snapshot_data = {k: [] for k in INDICATORS}
dom_data      = {k: [] for k in INDICATORS}

for ind_key, (ind_col, _) in INDICATORS.items():
    for country in CARIBBEAN:
        period = RECENT_WAVES[country]
        dfp    = df[(df["pais_c"] == country) & (df["periodo_c"] == period)]
        row    = _compute_row(dfp, ind_col)
        label  = f"{COUNTRY_LABEL[country]}  ({period})"
        snapshot_data[ind_key].append((label, row, country))

    dom_df = df[df["pais_c"] == DOM]
    for period in sorted(dom_df["periodo_c"].unique()):
        dfp = dom_df[dom_df["periodo_c"] == period]
        row = _compute_row(dfp, ind_col)
        dom_data[ind_key].append((period, row))

print("\nUnemployment — Primary or less (unweighted):")
for label, row, _ in snapshot_data["unemployment"]:
    nat_pct = row.get(("Primary or less", "Native",  "pct"), np.nan)
    nat_n   = row.get(("Primary or less", "Native",  "n"),   0)
    mig_pct = row.get(("Primary or less", "Migrant", "pct"), np.nan)
    mig_n   = row.get(("Primary or less", "Migrant", "n"),   0)
    print(f"  {label}: Native={nat_pct}% (N={nat_n})  Migrant={mig_pct}% (N={mig_n})")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
C_NAVY   = "1D3557"
C_ORANGE = "C55A11"
C_BLUE   = "2E75B6"
C_TEAL   = "1A7A6E"
C_PURPLE = "7030A0"

C_GREEN  = "2D6A4F"

IND_HDR_COLOR = {
    "unemployment": C_ORANGE,
    "informality":  C_BLUE,
    "inactivity":   C_TEAL,
    "wap":          C_PURPLE,
    "occupation":   C_GREEN,
}

EDU_HEADER_FILLS = {
    "Primary or less": "FFF2CC",
    "Secondary":       "DEEAF1",
    "Higher ed":       "E2EFDA",
    EDU_TOTAL:         "F2F2F2",
}
EDU_HEADER_FONTS = {
    "Primary or less": "7F6000",
    "Secondary":       "2E75B6",
    "Higher ed":       "375623",
    EDU_TOTAL:         "404040",
}

COUNTRY_FILLS = {
    "BLZ": "E8F5E9",
    "BRB": "FFF3E0",
    "SUR": "FCE4EC",
    "GUY": "E8EAF6",
    "DOM": "E3F2FD",
}

def _fill(hex_col):
    return PatternFill("solid", fgColor=hex_col)

def _thin():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

# Column structure:
# col 1 = Country/Period
# then per edu group: [%_Native, N_Native, %_Migrant, N_Migrant]  = 4 cols per group
# 4 groups × 4 = 16 data cols + 1 label = 17 total columns
EDU_ORDER_FULL = EDU_CATS + [EDU_TOTAL]
N_EDU          = len(EDU_ORDER_FULL)    # 4
SUBCOLS        = [("Native", "pct"), ("Native", "n"), ("Migrant", "pct"), ("Migrant", "n")]
N_SUBCOLS      = len(SUBCOLS)           # 4
N_COLS_DATA    = N_EDU * N_SUBCOLS      # 16
N_COLS_TOTAL   = 1 + N_COLS_DATA        # 17

SUBCOL_HDRS = ["Native %", "Native N", "Migrant %", "Migrant N"]
SUBCOL_FMTS = ["0.00", "#,##0", "0.00", "#,##0"]

def _col_for(edu_idx, sub_idx):
    """1-based column: label=1, data starts at 2."""
    return 2 + edu_idx * N_SUBCOLS + sub_idx

# ---------------------------------------------------------------------------
# Write Excel
# ---------------------------------------------------------------------------
wb = Workbook()
wb.remove(wb.active)

for ind_key, (ind_col, ind_label) in INDICATORS.items():
    hdr_color = IND_HDR_COLOR[ind_key]
    ws = wb.create_sheet(title=ind_key)

    # Row 1: sheet title
    ws.cell(1, 1, ind_label).font      = Font(bold=True, size=12, color="FFFFFF")
    ws.cell(1, 1).fill                  = _fill(C_NAVY)
    ws.cell(1, 1).alignment             = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height         = 24
    for c in range(2, N_COLS_TOTAL + 1):
        ws.cell(1, c).fill = _fill(C_NAVY)

    def write_edu_table(start_row, rows_data, section_title, row_label_header):
        # Section title row
        ws.cell(start_row, 1, section_title).font      = Font(bold=True, size=11, color="FFFFFF")
        ws.cell(start_row, 1).fill                      = _fill(C_NAVY)
        ws.cell(start_row, 1).alignment                 = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[start_row].height             = 20
        for c in range(2, N_COLS_TOTAL + 1):
            ws.cell(start_row, c).fill = _fill(C_NAVY)

        # Double header: row A = edu group spans (merged over 4 sub-cols)
        #                row B = Native %, Native N, Migrant %, Migrant N
        hrA = start_row + 1
        hrB = start_row + 2

        ws.cell(hrA, 1, row_label_header).font      = Font(bold=True, size=10, color="FFFFFF")
        ws.cell(hrA, 1).fill                         = _fill(hdr_color)
        ws.cell(hrA, 1).alignment                    = Alignment(horizontal="left", vertical="center")
        ws.cell(hrA, 1).border                       = _thin()
        ws.row_dimensions[hrA].height                = 16
        ws.row_dimensions[hrB].height                = 16

        for ei, edu in enumerate(EDU_ORDER_FULL):
            c1 = _col_for(ei, 0)
            c2 = _col_for(ei, N_SUBCOLS - 1)
            edu_fill = EDU_HEADER_FILLS[edu]
            edu_font = EDU_HEADER_FONTS[edu]

            ws.merge_cells(start_row=hrA, start_column=c1, end_row=hrA, end_column=c2)
            cell = ws.cell(hrA, c1, edu)
            cell.font      = Font(bold=True, size=9, color=edu_font)
            cell.fill      = _fill(edu_fill)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border    = _thin()

            for si, shdr in enumerate(SUBCOL_HDRS):
                c = _col_for(ei, si)
                hcell = ws.cell(hrB, c, shdr)
                hcell.font      = Font(bold=True, size=8, color=edu_font)
                hcell.fill      = _fill(edu_fill)
                hcell.alignment = Alignment(horizontal="center", vertical="center")
                hcell.border    = _thin()

        ws.cell(hrB, 1).fill   = _fill(hdr_color)
        ws.cell(hrB, 1).border = _thin()

        dr = hrB + 1
        for item in rows_data:
            if len(item) == 3:
                label, row_dict, ccode = item
                shade = COUNTRY_FILLS.get(ccode, "FFFFFF")
            else:
                label, row_dict = item
                shade = COUNTRY_FILLS["DOM"]

            lbl_cell = ws.cell(dr, 1, label)
            lbl_cell.font      = Font(size=9)
            lbl_cell.fill      = _fill(shade)
            lbl_cell.alignment = Alignment(horizontal="left", vertical="center")
            lbl_cell.border    = _thin()

            for ei, edu in enumerate(EDU_ORDER_FULL):
                for si, (grp, stat) in enumerate(SUBCOLS):
                    val = row_dict.get((edu, grp, stat), np.nan)
                    c   = _col_for(ei, si)
                    dc  = ws.cell(dr, c, val if pd.notna(val) else None)
                    dc.font          = Font(size=9)
                    dc.fill          = _fill(shade)
                    dc.alignment     = Alignment(horizontal="right", vertical="center")
                    dc.number_format = SUBCOL_FMTS[si]
                    dc.border        = _thin()

            ws.row_dimensions[dr].height = 14
            dr += 1

        return dr + 1

    current_row = write_edu_table(
        start_row        = 3,
        rows_data        = snapshot_data[ind_key],
        section_title    = "BLZ / BRB / SUR / GUY  —  Single-wave snapshot (unweighted)",
        row_label_header = "Country",
    )

    dom_rows = [(period, row) for period, row in dom_data[ind_key]]
    write_edu_table(
        start_row        = current_row,
        rows_data        = dom_rows,
        section_title    = "Dominican Republic  —  All waves 2018t4–2024t4 (unweighted)",
        row_label_header = "Period",
    )

    ws.column_dimensions["A"].width = 26
    for ei in range(N_EDU):
        for si in range(N_SUBCOLS):
            col_letter = get_column_letter(_col_for(ei, si))
            ws.column_dimensions[col_letter].width = 10 if si % 2 == 0 else 9

wb.save(OUT_FILE)
print(f"\nDone -> {OUT_FILE}")
print(f"  Size: {os.path.getsize(OUT_FILE)/1e3:.0f} KB")
print(f"  Sheets: {[s.title for s in wb.worksheets]}")
