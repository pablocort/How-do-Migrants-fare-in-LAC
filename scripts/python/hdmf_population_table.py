"""
hdmf_population_table.py
────────────────────────────────────────────────────────────────
Population table: Venezuelan migrants across LAC-4 countries.

For each country x wave (early 2017-18 and recent 2024-25), reports:
  1. Total Venezuelans according to R4V (humanitarian estimate)
  2. Total Venezuelans according to UNDESA IMS (statistical estimate):
       Early panel  -> UNDESA IMS 2020 (closest published year to 2017-18 waves)
       Recent panel -> UNDESA IMS 2024
  3. Venezuelans in the household survey (weighted count)
  4. Venezuelans aged 15-65 in the household survey (WAP)

UNDESA source: UN DESA, International Migrant Stock 2024 (and 2020).
  Downloaded from: https://www.un.org/development/desa/pd/content/international-migrant-stock
  File used: undesa_pd_2020_ims_stock_by_sex_destination_and_origin.xlsx (Table 1)
             undesa_pd_2024_ims_stock_by_sex_and_origin.xlsx (Statista extract)
  All figures are mid-year estimates, Venezuelan-born by destination country.

Outputs
  out/venezuela_vs_native/[DATE_TAG]/population_table.xlsx

Usage
  py hdmf_population_table.py

Generated with the Claude HDMF system — 2026-04-29
"""

import os
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR = os.path.join(BASE_DIR, 'bases armo', 'armo')
DATE_TAG = '2026-04-29'
OUT_DIR  = os.path.join(BASE_DIR, 'out', 'venezuela_vs_native', DATE_TAG)
os.makedirs(OUT_DIR, exist_ok=True)

# ── Wave config ────────────────────────────────────────────────────────────────
LAC4 = ['COL', 'PER', 'CHL', 'ECU']
COUNTRY_LABELS = {'COL': 'Colombia', 'PER': 'Peru', 'CHL': 'Chile', 'ECU': 'Ecuador'}

RECENT_WAVES = {'COL': '2025t3', 'PER': '2024a', 'CHL': '2024a',  'ECU': '2025m12'}
EARLY_WAVES  = {'COL': '2018t3', 'PER': '2018a', 'CHL': '2017a',  'ECU': '2018m12'}

RECENT_LABEL = 'Recent (2024–25)'
EARLY_LABEL  = 'Early (2017–18)'

# ── R4V figures ────────────────────────────────────────────────────────────────
# Source: Plataforma R4V (r4v.info) — verify dates match each survey wave.
# None renders as "N/A" in the table.
#
# Early period: figures circa the survey reference period (Q3 2018 / annual 2017-18)
# Recent period: figures circa the survey reference period (2024 / Q3 2025)
#
R4V = {
    # (country_code, period_label) -> integer count
    ('COL', EARLY_LABEL):  1_032_016,   # R4V Colombia, end-2018 — VERIFY
    ('PER', EARLY_LABEL):    506_000,   # R4V Peru, end-2018      — VERIFY
    ('CHL', EARLY_LABEL):    102_000,   # R4V Chile, end-2018     — VERIFY
    ('ECU', EARLY_LABEL):    221_000,   # R4V Ecuador, end-2018   — VERIFY
    ('COL', RECENT_LABEL): 2_906_000,   # R4V Colombia, end-2024  — VERIFY
    ('PER', RECENT_LABEL): 1_542_000,   # R4V Peru, end-2024      — VERIFY
    ('CHL', RECENT_LABEL):   547_000,   # R4V Chile, end-2024     — VERIFY
    ('ECU', RECENT_LABEL):   474_000,   # R4V Ecuador, end-2024   — VERIFY
}

# ── UNDESA International Migrant Stock ────────────────────────────────────────
# Source: UN DESA, International Migrant Stock dataset (Venezuelan-born by destination).
# Downloaded from: https://www.un.org/development/desa/pd/content/international-migrant-stock
# Extracted from: undesa_pd_2020_ims_stock_by_sex_destination_and_origin.xlsx  (Table 1)
#                 undesa_pd_2024_ims_stock_by_sex_and_origin.xlsx
# All figures are mid-year estimates, both sexes combined.
#
# UNDESA IMS 2020 — used for early panel (2017-18 waves).
# Closest published year: UNDESA publishes at 5-year intervals (1990,1995,...,2015,2020,2024).
# 2020 is 2 years from the 2018 early waves; 2015 predates the Venezuelan crisis entirely.
UNDESA_2020 = {
    'COL': 1_780_486,
    'PER':   941_889,
    'CHL':   523_553,
    'ECU':   388_861,
}

# UNDESA IMS 2024 — used for recent panel (2024-25 waves).
UNDESA_2024 = {
    'COL': 2_904_873,
    'PER': 1_596_667,
    'CHL':   427_821,
    'ECU':   487_871,
}

# ── Helpers ────────────────────────────────────────────────────────────────────
COLS = ['mig_pais_ci', 'migrante_ci', 'factor_ci', 'edad_ci']

def _dta_path(iso3, wave):
    iso3_lower = iso3.lower()
    return os.path.join(ARMO_DIR, iso3_lower, f'{iso3}_{wave}_BID.dta')


def _load(iso3, wave):
    path = _dta_path(iso3, wave)
    if not os.path.exists(path):
        print(f'  [MISSING] {path}')
        return None
    df = pd.read_stata(path, columns=COLS, convert_categoricals=True)
    return df


def _ven_counts(df):
    """Return (total_ven_weighted, wap_ven_weighted) for a loaded dataframe."""
    if df is None:
        return np.nan, np.nan
    mask_ven = df['mig_pais_ci'].astype(str).str.strip().str.lower() == 'venezuela'
    ven       = df[mask_ven].copy()
    total     = ven['factor_ci'].sum()
    wap       = ven.loc[(ven['edad_ci'] >= 15) & (ven['edad_ci'] <= 65), 'factor_ci'].sum()
    return total, wap


# ── Build table ────────────────────────────────────────────────────────────────
rows = []

for period_label, waves in [(EARLY_LABEL, EARLY_WAVES), (RECENT_LABEL, RECENT_WAVES)]:
    for iso3 in LAC4:
        wave = waves[iso3]
        print(f'Loading {iso3} {wave} ...')
        df = _load(iso3, wave)
        total_ven, wap_ven = _ven_counts(df)
        r4v_val = R4V.get((iso3, period_label))
        if period_label == EARLY_LABEL:
            undesa_val  = UNDESA_2020.get(iso3)
            undesa_year = 2020
        else:
            undesa_val  = UNDESA_2024.get(iso3)
            undesa_year = 2024
        rows.append({
            'Period':                        period_label,
            'Country':                       COUNTRY_LABELS[iso3],
            'ISO3':                          iso3,
            'Survey wave':                   wave,
            'R4V (total)':                   r4v_val,
            'UNDESA year':                   undesa_year,
            'UNDESA (total)':                undesa_val,
            'Survey (total weighted)':       total_ven,
            'Survey (WAP 15-65 weighted)':   wap_ven,
        })

table = pd.DataFrame(rows)
print('\n', table.to_string(index=False))

# ── Excel export ───────────────────────────────────────────────────────────────
HDMF_BLUE  = '004B87'
HDMF_LIGHT = 'E6F1FA'
WHITE      = 'FFFFFF'
GRAY_FONT  = '646464'

thin = Side(style='thin', color='AAAAAA')
med  = Side(style='medium', color='004B87')

def _border(left=None, right=None, top=None, bottom=None):
    return Border(left=left or Side(), right=right or Side(),
                  top=top or Side(), bottom=bottom or Side())

wb = Workbook()
ws = wb.active
ws.title = 'Population Table'

# ── Headers ────────────────────────────────────────────────────────────────────
headers = [
    'Period', 'Country', 'Survey wave',
    'R4V — total\n(humanitarian estimate)',
    'UNDESA year',
    'UNDESA IMS\n(statistical estimate, mid-year)',
    'Household survey\nVenezuelans (weighted)',
    'Household survey\nVenezuelans WAP 15-65 (weighted)',
]
col_widths = [16, 14, 14, 22, 12, 30, 26, 34]

for ci, (h, w) in enumerate(zip(headers, col_widths), start=1):
    cell = ws.cell(row=1, column=ci, value=h)
    cell.font      = Font(bold=True, color=WHITE, size=10)
    cell.fill      = PatternFill('solid', fgColor=HDMF_BLUE)
    cell.alignment = Alignment(horizontal='center', vertical='center',
                               wrap_text=True)
    cell.border    = _border(left=med, right=med, top=med, bottom=med)
    ws.column_dimensions[get_column_letter(ci)].width = w

ws.row_dimensions[1].height = 36

# ── Data rows ──────────────────────────────────────────────────────────────────
data_cols = [
    'Period', 'Country', 'Survey wave',
    'R4V (total)',
    'UNDESA year',
    'UNDESA (total)',
    'Survey (total weighted)',
    'Survey (WAP 15-65 weighted)',
]

prev_period = None
for ri, (_, row) in enumerate(table.iterrows(), start=2):
    period = row['Period']
    fill_color = HDMF_LIGHT if period == EARLY_LABEL else WHITE

    # Separator line between early and recent blocks
    top_border = med if (period != prev_period and prev_period is not None) else thin
    prev_period = period

    for ci, col in enumerate(data_cols, start=1):
        v = row[col]

        cell = ws.cell(row=ri, column=ci)
        if isinstance(v, float) and np.isnan(v):
            cell.value = 'N/A'
        elif isinstance(v, float) and not np.isnan(v):
            cell.value = round(v)
            cell.number_format = '#,##0'
        elif isinstance(v, int):
            cell.value = v
            cell.number_format = '#,##0'
        else:
            cell.value = v

        cell.fill      = PatternFill('solid', fgColor=fill_color)
        cell.alignment = Alignment(horizontal='center' if ci > 2 else 'left',
                                   vertical='center')
        cell.font      = Font(size=10)
        cell.border    = Border(
            left   = med if ci == 1 else _border().left,
            right  = med if ci == len(data_cols) else Side(style='thin', color='DDDDDD'),
            top    = Side(style='medium' if top_border == med else 'thin',
                          color='004B87' if top_border == med else 'AAAAAA'),
            bottom = Side(style='thin', color='DDDDDD'),
        )
    ws.row_dimensions[ri].height = 18

# ── Notes row ─────────────────────────────────────────────────────────────────
note_row = len(table) + 2
note = (
    'Notes: R4V = Plataforma R4V (r4v.info) humanitarian estimates — verify dates match survey reference periods. '
    'UNDESA = UN Dept. of Economic and Social Affairs, International Migrant Stock dataset; '
    'Venezuelan-born population by destination country, mid-year estimates, both sexes. '
    'Early panel uses UNDESA IMS 2020 (closest published year to 2017-18 waves; '
    'UNDESA publishes at 5-year intervals: 2015 predates the crisis, 2020 is 2 years from the 2018 waves). '
    'Recent panel uses UNDESA IMS 2024. '
    'Source: https://www.un.org/development/desa/pd/content/international-migrant-stock. '
    'Survey counts use factor_ci survey weights. WAP = ages 15-65. '
    'Venezuelan migrants identified via mig_pais_ci = "Venezuela".'
)
ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=len(headers))
note_cell = ws.cell(row=note_row, column=1, value=note)
note_cell.font      = Font(size=8, color=GRAY_FONT, italic=True)
note_cell.alignment = Alignment(horizontal='left', wrap_text=True)
ws.row_dimensions[note_row].height = 40

out_path = os.path.join(OUT_DIR, 'population_table.xlsx')
wb.save(out_path)
print(f'\nSaved: {out_path}')

# ── Console summary ────────────────────────────────────────────────────────────
print('\n-- Population table summary ------------------------------------------')
for period_label in [EARLY_LABEL, RECENT_LABEL]:
    print(f'\n{period_label}')
    sub = table[table['Period'] == period_label]
    for _, r in sub.iterrows():
        r4v    = f"{r['R4V (total)']:>12,.0f}"          if pd.notna(r['R4V (total)'])          else '         N/A'
        undesa_yr = int(r['UNDESA year'])
        undesa = f"{r['UNDESA (total)']:>12,.0f}"  if pd.notna(r['UNDESA (total)'])  else '         N/A'
        surv   = f"{r['Survey (total weighted)']:>12,.0f}" if pd.notna(r['Survey (total weighted)']) else '         N/A'
        wap    = f"{r['Survey (WAP 15-65 weighted)']:>12,.0f}" if pd.notna(r['Survey (WAP 15-65 weighted)']) else '         N/A'
        ratio  = ''
        if pd.notna(r['UNDESA (total)']) and pd.notna(r['Survey (total weighted)']) and r['UNDESA (total)'] > 0:
            ratio = f"  (survey/UNDESA{undesa_yr} = {r['Survey (total weighted)'] / r['UNDESA (total)']:.1%})"
        print(f"  {r['Country']:<12}  R4V:{r4v}  UNDESA{undesa_yr}:{undesa}  Survey:{surv}  WAP:{wap}{ratio}")
