"""
build_jeremy_wap_edu.py  --  Education distribution of the Working-Age Population
==================================================================================
Output: out/jeremy/2026-05-13/jeremy_wap_edu.xlsx

For each country, among persons aged 15-64 (WAP), what share holds each education
level — separately for Natives and Migrants.

Universe  : WAP = edad_ci in [15, 64]
Breakdown : edu_hdmf → 3 categories (Primary or less | Secondary | Higher education)
Groups    : Native (migrante_ci == 0) | Migrant (migrante_ci == 1)

Countries : BLZ (2024m9), BRB (2023a), SUR (2022a), GUY (2021t3) — single-wave snapshot
            DOM (2018t4–2024t4) — full 7-wave trend

Sheets    : wap_edu_pct  — % share within group (sums to 100 per group)
            wap_edu_abs  — weighted population count
"""

import os, pickle, numpy as np, pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

BASE = Path(__file__).parent.parent
CACHE_FILE = BASE / "bases armo" / "armo" / "_hdmf_cache.pkl"
DATE_TAG   = "2026-05-13"
OUT_DIR    = BASE / "out" / "jeremy" / DATE_TAG
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE   = OUT_DIR / "jeremy_wap_edu.xlsx"

SNAP_COUNTRIES = ["BLZ", "BRB", "SUR", "GUY"]
DOM            = "DOM"
ALL_COUNTRIES  = SNAP_COUNTRIES + [DOM]
RECENT_WAVES   = {"BLZ": "2024m9", "BRB": "2023a", "SUR": "2022a",
                  "GUY": "2021t3",  "DOM": "2024t4"}
GROUPS         = ["Native", "Migrant"]
GROUP_COL      = "migrante_ci"

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
    7: "Higher education", 8: "Higher education",
    9: "Higher education", 10: "Higher education",
}
EDU_CATS  = ["Primary or less", "Secondary", "Higher education"]
EDU_TOTAL = "Total"
EDU_ORDER = EDU_CATS + [EDU_TOTAL]

# ---------------------------------------------------------------------------
# Load cache — keep only WAP (15–64)
# ---------------------------------------------------------------------------
print("Loading cache ...")
with open(CACHE_FILE, "rb") as fh:
    _cache = pickle.load(fh)
data = _cache["data"]

df = data[data["pais_c"].isin(ALL_COUNTRIES)].copy()
df = df[df["edad_ci"].between(15, 64)]          # restrict to WAP
df["edu_3cat"] = pd.to_numeric(df["edu_hdmf"], errors="coerce").map(EDU_3CAT_MAP)

print(f"  WAP rows (15-64): {len(df):,}")
for c in ALL_COUNTRIES:
    sub = df[df["pais_c"] == c]
    print(f"    {c}: {len(sub):,} rows, periods: {sorted(sub['periodo_c'].unique())}")

# ---------------------------------------------------------------------------
# Compute education shares — weighted
# ---------------------------------------------------------------------------
def compute_edu(dfp):
    """Return (abs_dict, pct_dict) keyed by (edu_cat, group)."""
    abs_d, pct_d = {}, {}
    for grp in GROUPS:
        dfg   = dfp[(dfp[GROUP_COL] == grp) & dfp["edu_3cat"].notna() & dfp["factor_ci"].notna()]
        total = dfg["factor_ci"].sum()
        for cat in EDU_CATS:
            cat_w = dfg.loc[dfg["edu_3cat"] == cat, "factor_ci"].sum()
            abs_d[(cat, grp)] = int(round(cat_w))
            pct_d[(cat, grp)] = round(cat_w / total * 100, 2) if total > 0 else np.nan
        abs_d[(EDU_TOTAL, grp)] = int(round(total))
        pct_d[(EDU_TOTAL, grp)] = 100.0 if total > 0 else np.nan
    return abs_d, pct_d

print("\nComputing WAP education distributions ...")

# Single-wave snapshot
snap_abs = []   # list of (label, abs_dict, country_code)
snap_pct = []

for country in SNAP_COUNTRIES:
    period = RECENT_WAVES[country]
    dfp    = df[(df["pais_c"] == country) & (df["periodo_c"] == period)]
    a, p   = compute_edu(dfp)
    label  = f"{COUNTRY_LABEL[country]}  ({period})"
    snap_abs.append((label, a, country))
    snap_pct.append((label, p, country))
    print(f"  {COUNTRY_LABEL[country]}: Native WAP={a.get((EDU_TOTAL,'Native'),0):,}  "
          f"Migrant WAP={a.get((EDU_TOTAL,'Migrant'),0):,}")

# DOM — all waves
dom_abs = []    # list of (period, abs_dict)
dom_pct = []

dom_df = df[df["pais_c"] == DOM]
for period in sorted(dom_df["periodo_c"].unique()):
    dfp = dom_df[dom_df["periodo_c"] == period]
    a, p = compute_edu(dfp)
    dom_abs.append((period, a))
    dom_pct.append((period, p))

print(f"  DOM: {len(dom_pct)} waves")

# Print education pct check
print("\nEducation % of WAP — most recent wave:")
for label, p, _ in snap_pct:
    print(f"\n  {label}")
    for cat in EDU_ORDER:
        nat = p.get((cat, "Native"),  np.nan)
        mig = p.get((cat, "Migrant"), np.nan)
        print(f"    {cat:<22} Native={nat}%  Migrant={mig}%")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
C_NAVY   = "1D3557"
C_YELLOW = "7F6000"
C_GREEN  = "375623"
C_BLUE   = "2E75B6"
C_GREY   = "404040"

COUNTRY_FILLS = {
    "BLZ": "E8F5E9",
    "BRB": "FFF3E0",
    "SUR": "FCE4EC",
    "GUY": "E8EAF6",
    "DOM": "E3F2FD",
}

EDU_HEADER_FILLS = {
    "Primary or less":  "FFF2CC",
    "Secondary":        "DEEAF1",
    "Higher education": "E2EFDA",
    EDU_TOTAL:          "F2F2F2",
}
EDU_HEADER_FONTS = {
    "Primary or less":  C_YELLOW,
    "Secondary":        C_BLUE,
    "Higher education": C_GREEN,
    EDU_TOTAL:          C_GREY,
}

def _fill(hex_col):
    return PatternFill("solid", fgColor=hex_col)

def _thin():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def _med_bottom():
    med = Side(style="medium", color="888888")
    thn = Side(style="thin",   color="CCCCCC")
    return Border(left=thn, right=thn, top=thn, bottom=med)

# ---------------------------------------------------------------------------
# Write Excel
# Column layout:
#   col 1 = Country / Period
#   then 2 columns per edu category: Native | Migrant
#   4 categories × 2 = 8 data cols  →  9 total
# ---------------------------------------------------------------------------
N_EDU       = len(EDU_ORDER)   # 4
N_COLS_DATA = N_EDU * 2        # 8
N_COLS_TOT  = 1 + N_COLS_DATA  # 9

def _col(edu_idx, grp_idx):
    """1-based column: label=1, data from col 2."""
    return 2 + edu_idx * 2 + grp_idx   # grp_idx: 0=Native, 1=Migrant


def write_sheet(ws, snap_rows, dom_rows, sheet_title, num_fmt):
    """Write one full sheet (pct or abs)."""

    # Row 1 — sheet title banner
    ws.cell(1, 1, sheet_title).font   = Font(bold=True, size=12, color="FFFFFF")
    ws.cell(1, 1).fill                = _fill(C_NAVY)
    ws.cell(1, 1).alignment           = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height       = 24
    for c in range(2, N_COLS_TOT + 1):
        ws.cell(1, c).fill = _fill(C_NAVY)

    def write_section(start_row, rows_data, section_title, row_label_header):
        # Section title
        ws.cell(start_row, 1, section_title).font      = Font(bold=True, size=11, color="FFFFFF")
        ws.cell(start_row, 1).fill                      = _fill(C_NAVY)
        ws.cell(start_row, 1).alignment                 = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[start_row].height             = 20
        for c in range(2, N_COLS_TOT + 1):
            ws.cell(start_row, c).fill = _fill(C_NAVY)

        # Double header: row A = edu category (merged Native+Migrant), row B = Native | Migrant
        hrA = start_row + 1
        hrB = start_row + 2
        ws.row_dimensions[hrA].height = 16
        ws.row_dimensions[hrB].height = 16

        ws.cell(hrA, 1, row_label_header).font      = Font(bold=True, size=10, color="FFFFFF")
        ws.cell(hrA, 1).fill                         = _fill(C_NAVY)
        ws.cell(hrA, 1).alignment                    = Alignment(horizontal="left", vertical="center")
        ws.cell(hrA, 1).border                       = _thin()
        ws.cell(hrB, 1).fill   = _fill(C_NAVY)
        ws.cell(hrB, 1).border = _thin()

        for ei, edu in enumerate(EDU_ORDER):
            c1 = _col(ei, 0)
            c2 = _col(ei, 1)
            edu_fill = EDU_HEADER_FILLS[edu]
            edu_font = EDU_HEADER_FONTS[edu]

            ws.merge_cells(start_row=hrA, start_column=c1, end_row=hrA, end_column=c2)
            cell = ws.cell(hrA, c1, edu)
            cell.font      = Font(bold=True, size=9, color=edu_font)
            cell.fill      = _fill(edu_fill)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border    = _thin()

            for gi, glbl in enumerate(GROUPS):
                hc = ws.cell(hrB, _col(ei, gi), glbl)
                hc.font      = Font(bold=True, size=9, color=edu_font)
                hc.fill      = _fill(edu_fill)
                hc.alignment = Alignment(horizontal="center", vertical="center")
                hc.border    = _thin()

        # Data rows
        dr = hrB + 1
        for item in rows_data:
            if len(item) == 3:
                label, d, ccode = item
                shade = COUNTRY_FILLS.get(ccode, "FFFFFF")
            else:
                label, d = item
                shade = COUNTRY_FILLS[DOM]

            is_total_row = False   # row-level total flag (not used here)

            lbl_cell = ws.cell(dr, 1, label)
            lbl_cell.font      = Font(size=9)
            lbl_cell.fill      = _fill(shade)
            lbl_cell.alignment = Alignment(horizontal="left", vertical="center")
            lbl_cell.border    = _thin()

            for ei, edu in enumerate(EDU_ORDER):
                is_tot = (edu == EDU_TOTAL)
                for gi, grp in enumerate(GROUPS):
                    val = d.get((edu, grp), np.nan)
                    c   = _col(ei, gi)
                    dc  = ws.cell(dr, c, val if pd.notna(val) else None)
                    dc.font          = Font(bold=is_tot, size=9)
                    dc.fill          = _fill("F0F0F0") if is_tot else _fill(shade)
                    dc.alignment     = Alignment(horizontal="right", vertical="center")
                    dc.number_format = num_fmt
                    dc.border        = _med_bottom() if is_tot else _thin()

            ws.row_dimensions[dr].height = 14
            dr += 1

        return dr + 1  # blank gap

    current_row = write_section(
        start_row        = 3,
        rows_data        = snap_rows,
        section_title    = "BLZ / BRB / SUR / GUY  —  Single-wave snapshot",
        row_label_header = "Country",
    )
    write_section(
        start_row        = current_row,
        rows_data        = dom_rows,
        section_title    = "Dominican Republic  —  All waves (2018t4 – 2024t4)",
        row_label_header = "Period",
    )

    # Column widths
    ws.column_dimensions["A"].width = 26
    for ei in range(N_EDU):
        for gi in range(2):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(_col(ei, gi))].width = 13


wb = Workbook()
wb.remove(wb.active)

write_sheet(
    ws          = wb.create_sheet("wap_edu_pct"),
    snap_rows   = snap_pct,
    dom_rows    = dom_pct,
    sheet_title = "Education level of Working-Age Population (15-64) — % share within group",
    num_fmt     = "0.00",
)
write_sheet(
    ws          = wb.create_sheet("wap_edu_abs"),
    snap_rows   = snap_abs,
    dom_rows    = dom_abs,
    sheet_title = "Education level of Working-Age Population (15-64) — weighted population count",
    num_fmt     = "#,##0",
)

wb.save(OUT_FILE)
print(f"\nDone -> {OUT_FILE}")
print(f"  Size: {os.path.getsize(OUT_FILE)/1e3:.0f} KB")
print(f"  Sheets: {[s.title for s in wb.worksheets]}")
