"""
hdmf_venezuela_vs_native.py
────────────────────────────
Horizontal bar chart + Excel table comparing Venezuelan migrants vs. Natives
across COL, PER, CHL, ECU (pooled LAC4 aggregate).

Shows two time points per group:
  • Bars  — most recent wave  (COL 2025t3 · PER 2024a · CHL 2024a · ECU 2025m12)
  • Markers — earliest available wave (COL 2018t3 · PER 2018a · CHL 2017a · ECU 2018m12)

Indicators
──────────
  1. Unemployment rate         (% of economically active population, 16-64)
  2. Inactivity rate           (% of working-age population, 16-64)
  3. Informality               (% of employed population)
  4. Higher education          (% of population, post-secondary+)
  5. Long hours (50+)          (% of employed population)

Usage
──────
  py hdmf_venezuela_vs_native.py
"""

import os
import pickle
from functools import reduce

import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE_DIR, 'bases armo', 'armo')
CACHE_FILE = os.path.join(ARMO_DIR, '_hdmf_cache.pkl')
DATE_TAG   = '2026-05-01'
OUT_DIR    = os.path.join(BASE_DIR, 'out', 'venezuela_vs_native', DATE_TAG)
os.makedirs(OUT_DIR, exist_ok=True)

# ── Config ─────────────────────────────────────────────────────────────────────
LAC4   = ['COL', 'PER', 'CHL', 'ECU']   # pooled chart: LAC-4 only (Spain not LAC)
ALL_COUNTRIES = ['COL', 'PER', 'CHL', 'ECU', 'ESP']   # country breakdown incl. Spain
GROUPS = ['Venezuela', 'Native']

RECENT_WAVES = {'COL': '2025t3', 'PER': '2024a', 'CHL': '2024a',  'ECU': '2025m12', 'ESP': '2025a'}
EARLY_WAVES  = {'COL': '2018t3', 'PER': '2018a', 'CHL': '2017a',  'ECU': '2018m12', 'ESP': '2018a'}

RECENT_LABEL = 'Recent (2024–2025)'
EARLY_LABEL  = 'Early (2017–2018)'

# Color palette — paired hues: dark (recent bars) vs light (early markers)
# Venezuela: dark crimson → light salmon   |   Native: dark blue → light sky-blue
COLOR_VEN_RECENT = '#C0392B'   # dark crimson   — Venezuelan recent bars
COLOR_NAT_RECENT = '#1A5276'   # dark navy blue — Native recent bars
COLOR_VEN_EARLY  = '#F1948A'   # light salmon   — Venezuelan early markers (same red family)
COLOR_NAT_EARLY  = '#7FB3D3'   # light sky blue — Native early markers (same blue family)

MARKER_VEN = 'D'   # diamond for Venezuela early
MARKER_NAT = 's'   # square for Native early
MARKER_SIZE = 180

INDICATORS = [
    'Unemployment rate\n(% of active pop.)',
    'Inactivity rate\n(% of working-age pop.)',
    'Informality\n(% of employed pop.)',
    'Higher education\n(% of pop., post-secondary+)',
    'Long hours (50+)\n(% of employed pop.)',
]

CLEAN_NAMES = {
    'Unemployment rate\n(% of active pop.)':             'Unemployment rate (% active pop.)',
    'Inactivity rate\n(% of working-age pop.)':          'Inactivity rate (% working-age pop.)',
    'Informality\n(% of employed pop.)':                  'Informality (% employed pop.)',
    'Higher education\n(% of pop., post-secondary+)':    'Higher education (% pop., post-sec.+)',
    'Long hours (50+)\n(% of employed pop.)':            'Long hours 50+ (% employed pop.)',
}

# ── Load cache ─────────────────────────────────────────────────────────────────
print(f'Loading cache: {CACHE_FILE}')
with open(CACHE_FILE, 'rb') as fh:
    _cache = pickle.load(fh)
data = _cache['data']
print(f'Loaded {len(data):,} rows  |  countries: {sorted(data["pais_c"].unique())}')
print(f'Periods: {sorted(data["periodo_c"].unique())}')

# ── Filter helpers ──────────────────────────────────────────────────────────────
def filter_waves(df, wave_map):
    """Keep rows where (pais_c, periodo_c) matches wave_map."""
    masks = [
        (df['pais_c'] == country) & (df['periodo_c'] == period)
        for country, period in wave_map.items()
    ]
    combined = reduce(lambda a, b: a | b, masks)
    return df[combined & df['foreign_born'].isin(GROUPS)].copy()


# All countries (incl. Spain) — used for country-level Excel breakdown
df_recent = filter_waves(data, RECENT_WAVES)
df_early  = filter_waves(data, EARLY_WAVES)

# LAC4 only — used for pooled chart (Spain is not LAC)
LAC4_RECENT_WAVES = {c: v for c, v in RECENT_WAVES.items() if c in LAC4}
LAC4_EARLY_WAVES  = {c: v for c, v in EARLY_WAVES.items()  if c in LAC4}
df_recent_lac4 = filter_waves(data, LAC4_RECENT_WAVES)
df_early_lac4  = filter_waves(data, LAC4_EARLY_WAVES)

print(f'\nRecent period rows (all): {len(df_recent):,}  |  LAC4: {len(df_recent_lac4):,}')
print(f'Early  period rows (all): {len(df_early):,}   |  LAC4: {len(df_early_lac4):,}')
for name, dfw in [('Recent', df_recent), ('Early', df_early)]:
    print(f'\n{name} — weighted obs by country/group:')
    print(dfw.groupby(['pais_c', 'foreign_born'])['factor_ci'].sum()
              .unstack().map(lambda x: f'{x:,.0f}' if pd.notna(x) else '—'))

# ── Weighted mean helper ───────────────────────────────────────────────────────
def wavg(v_series, w_series):
    v = pd.to_numeric(v_series, errors='coerce').to_numpy(dtype=float)
    w = pd.to_numeric(w_series, errors='coerce').to_numpy(dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if mask.sum() == 0:
        return np.nan
    return float(np.average(v[mask], weights=w[mask]))


# ── Compute pooled indicators ─────────────────────────────────────────────────
def compute_pooled(df):
    df = df.copy()
    df['higher_edu_ci'] = (pd.to_numeric(df['edu_hdmf'], errors='coerce') >= 7).astype(float)
    df.loc[df['edu_hdmf'].isna(), 'higher_edu_ci'] = np.nan

    wap = df[df['edad_ci'].between(16, 64)].copy()
    pea = wap[wap['pea_ci'] == 1].copy()
    emp = df[df['emp_ci'] == 1].copy()
    emp['longhours_ci'] = (pd.to_numeric(emp['horastot_ci'], errors='coerce') > 50).astype(float)
    emp.loc[emp['horastot_ci'].isna(), 'longhours_ci'] = np.nan

    result = {}
    for grp in GROUPS:
        unemp  = wavg(pea.loc[pea['foreign_born'] == grp, 'desemp_ci'],
                      pea.loc[pea['foreign_born'] == grp, 'factor_ci']) * 100
        inact  = wavg(wap.loc[wap['foreign_born'] == grp, 'inactivo_ci'],
                      wap.loc[wap['foreign_born'] == grp, 'factor_ci']) * 100
        infml  = (1 - wavg(emp.loc[emp['foreign_born'] == grp, 'formal_ci'],
                           emp.loc[emp['foreign_born'] == grp, 'factor_ci'])) * 100
        edu_hi = wavg(df.loc[df['foreign_born'] == grp, 'higher_edu_ci'],
                      df.loc[df['foreign_born'] == grp, 'factor_ci']) * 100
        lhrs   = wavg(emp.loc[emp['foreign_born'] == grp, 'longhours_ci'],
                      emp.loc[emp['foreign_born'] == grp, 'factor_ci']) * 100
        result[grp] = {
            'Unemployment rate\n(% of active pop.)':             unemp,
            'Inactivity rate\n(% of working-age pop.)':          inact,
            'Informality\n(% of employed pop.)':                  infml,
            'Higher education\n(% of pop., post-secondary+)':    edu_hi,
            'Long hours (50+)\n(% of employed pop.)':            lhrs,
        }
    return result


pooled_recent = compute_pooled(df_recent_lac4)
pooled_early  = compute_pooled(df_early_lac4)

print('\n-- Pooled LAC4 results --')
for ind in INDICATORS:
    vr = pooled_recent['Venezuela'][ind]
    nr = pooled_recent['Native'][ind]
    ve = pooled_early['Venezuela'][ind]
    ne = pooled_early['Native'][ind]
    print(f'  {CLEAN_NAMES[ind][:42]:42s}'
          f'  Ven_recent={vr:.1f}  Nat_recent={nr:.1f}'
          f'  Ven_early={ve:.1f}   Nat_early={ne:.1f}')


# ── Country-level breakdown ────────────────────────────────────────────────────
def compute_country_rows(df, label):
    rows = []
    df = df.copy()
    df['higher_edu_ci'] = (pd.to_numeric(df['edu_hdmf'], errors='coerce') >= 7).astype(float)
    df.loc[df['edu_hdmf'].isna(), 'higher_edu_ci'] = np.nan

    for country in ALL_COUNTRIES:
        dfc  = df[df['pais_c'] == country]
        wapc = dfc[dfc['edad_ci'].between(16, 64)]
        peac = wapc[wapc['pea_ci'] == 1]
        empc = dfc[dfc['emp_ci'] == 1].copy()
        empc['longhours_ci'] = (pd.to_numeric(empc['horastot_ci'], errors='coerce') > 50).astype(float)
        empc.loc[empc['horastot_ci'].isna(), 'longhours_ci'] = np.nan

        for grp in GROUPS:
            rows.append({
                'Period':  label,
                'Country': country,
                'Group':   grp,
                'Unemployment rate (% active pop.)':     wavg(
                    peac.loc[peac['foreign_born'] == grp, 'desemp_ci'],
                    peac.loc[peac['foreign_born'] == grp, 'factor_ci']) * 100,
                'Inactivity rate (% working-age pop.)':  wavg(
                    wapc.loc[wapc['foreign_born'] == grp, 'inactivo_ci'],
                    wapc.loc[wapc['foreign_born'] == grp, 'factor_ci']) * 100,
                'Informality (% employed pop.)':         (1 - wavg(
                    empc.loc[empc['foreign_born'] == grp, 'formal_ci'],
                    empc.loc[empc['foreign_born'] == grp, 'factor_ci'])) * 100,
                'Higher education (% pop., post-sec.+)': wavg(
                    dfc.loc[dfc['foreign_born'] == grp, 'higher_edu_ci'],
                    dfc.loc[dfc['foreign_born'] == grp, 'factor_ci']) * 100,
                'Long hours 50+ (% employed pop.)':      wavg(
                    empc.loc[empc['foreign_born'] == grp, 'longhours_ci'],
                    empc.loc[empc['foreign_born'] == grp, 'factor_ci']) * 100,
            })
    return rows


country_rows = (compute_country_rows(df_recent, RECENT_LABEL) +
                compute_country_rows(df_early,  EARLY_LABEL))
country_df = pd.DataFrame(country_rows)


# ── Chart — IDB-style, landscape presentation format ──────────────────────────
plt.rcParams.update({'font.family': 'DejaVu Sans'})

bar_h     = 0.55
gap       = 0.80        # generous vertical gap between indicator groups
n_ind     = len(INDICATORS)

y_pos     = {}
y_mid     = []
current_y = 0.0

for ind in reversed(INDICATORS):
    y_ven = current_y + bar_h
    y_nat = current_y
    y_pos[(ind, 'Venezuela')] = y_ven + bar_h / 2
    y_pos[(ind, 'Native')]    = y_nat + bar_h / 2
    y_mid.insert(0, (y_nat + y_ven + bar_h) / 2)
    current_y += 2 * bar_h + gap

# Landscape: wide and moderately tall — slides typically 16:9
total_data_height = n_ind * (2 * bar_h + gap)
fig_height = max(10, total_data_height * 1.4)   # landscape-friendly for slides
fig, ax = plt.subplots(figsize=(24, fig_height))

# — Bars: recent year —
LABEL_PAD   = 0.9
LABEL_ZONE  = 6.0   # horizontal range (in data units) where an early marker collides

for ind in INDICATORS:
    for grp in GROUPS:
        val       = pooled_recent[grp][ind]
        val_early = pooled_early[grp][ind]
        y         = y_pos[(ind, grp)]
        color     = COLOR_VEN_RECENT if grp == 'Venezuela' else COLOR_NAT_RECENT
        ax.barh(y, val, height=bar_h, color=color, edgecolor='none', zorder=3)

        # Shift label up if an early marker falls in the label zone
        collides = (np.isfinite(val_early) and
                    val - 1 < val_early < val + LABEL_ZONE)
        label_y  = y + bar_h * 0.52 if collides else y
        label_va = 'bottom' if collides else 'center'

        ax.text(val + LABEL_PAD, label_y, f'{val:.1f}',
                va=label_va, ha='left', fontsize=23, fontweight='bold', color=color)

# — Markers: early year — label just above, centered on marker x
for ind in INDICATORS:
    for grp in GROUPS:
        val = pooled_early[grp][ind]
        if not np.isfinite(val):
            continue
        y      = y_pos[(ind, grp)]
        color  = COLOR_VEN_EARLY  if grp == 'Venezuela' else COLOR_NAT_EARLY
        marker = MARKER_VEN       if grp == 'Venezuela' else MARKER_NAT
        ax.scatter(val, y, marker=marker, s=300,
                   color=color, edgecolors='white', linewidths=1.5, zorder=5)

# ── Axes ──────────────────────────────────────────────────────────────────────
ax.set_yticks(y_mid)
ax.set_yticklabels(INDICATORS, fontsize=22, ha='right', va='center',
                   linespacing=1.4)
ax.tick_params(axis='y', length=0, pad=16)
ax.tick_params(axis='x', labelsize=20)

all_vals = [pooled_recent[g][i] for g in GROUPS for i in INDICATORS]
all_vals += [pooled_early[g][i] for g in GROUPS for i in INDICATORS
             if np.isfinite(pooled_early[g][i])]
max_val = max(all_vals)
ax.set_xlim(0, max_val * 1.25)

ax.xaxis.grid(True, linestyle='--', alpha=0.30, color='grey', zorder=0)
ax.set_axisbelow(True)
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_color('#BBBBBB')

# Title intentionally omitted — provided by the LaTeX slide frame title

# ── Legend ────────────────────────────────────────────────────────────────────
leg_handles = [
    mpatches.Patch(color=COLOR_VEN_RECENT, label=f'Venezuelan — {RECENT_LABEL}'),
    mpatches.Patch(color=COLOR_NAT_RECENT, label=f'Native — {RECENT_LABEL}'),
    mlines.Line2D([], [], color=COLOR_VEN_EARLY, marker=MARKER_VEN,
                  linestyle='None', markersize=16,
                  label=f'Venezuelan — {EARLY_LABEL}'),
    mlines.Line2D([], [], color=COLOR_NAT_EARLY, marker=MARKER_NAT,
                  linestyle='None', markersize=16,
                  label=f'Native — {EARLY_LABEL}'),
]
ax.legend(handles=leg_handles, loc='lower right', frameon=False,
          fontsize=20, ncol=2, handlelength=2.0,
          handletextpad=1.0, columnspacing=2.0)

fig.tight_layout()

# ── Footnotes (QA caveats) ─────────────────────────────────────────────────────
_fn = (
    "¹ PER 2018a — Venezuelan early estimates: n = 81 unweighted observations "
    "(weighted N ≈30,000). High sampling variance; treat PER early values for the Venezuelan "
    "group with caution. Some Venezuelans may be classified as ‘Other country’ due to "
    "upstream survey aggregation in ENAHO 2018.\n"
    "² COL long hours (50+) — ~55 % item non-response in the hours-worked variable "
    "(consistent across 2018 and 2025 waves). Effective sample is smaller; no directional bias detected.\n"
    "³ Working-age population defined as ages 16–64, applied consistently across all groups "
    "and waves. Source: COL GEIH 2018t3 & 2025t3 · PER ENAHO 2018a & 2024a "
    "· CHL CASEN 2017a & 2024a · ECU ENEMDU 2018m12 & 2025m12. "
    "Pooled weighted averages."
)
fig.text(0.02, -0.02, _fn, fontsize=14, color='#666666',
         va='top', ha='left', linespacing=1.6,
         transform=fig.transFigure)

chart_path = os.path.join(OUT_DIR, 'venezuela_vs_native_chart.png')
fig.savefig(chart_path, dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print(f'\nChart saved -> {chart_path}')


# ── Excel table ───────────────────────────────────────────────────────────────
def _fill(hex_col):
    return PatternFill('solid', fgColor=hex_col)

def _font(bold=False, size=10, color='000000'):
    return Font(bold=bold, size=size, color=color)

def _side(style='thin', color='CCCCCC'):
    return Side(style=style, color=color)

def _border_all():
    s = _side()
    return Border(left=s, right=s, top=s, bottom=s)

def _align(h='center', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)


# Header fills — match new palette
HDR_VEN_R = 'F1C0BB'   # light crimson
HDR_NAT_R = 'BDD7EE'   # light navy
HDR_VEN_E = 'FAE3CA'   # light amber
HDR_NAT_E = 'D6EAF8'   # light sky blue
HDR_IND   = 'D9D9D9'   # grey
HDR_DIF   = 'E8DAEF'   # soft purple for difference

DATA_VEN_R = 'FAEAE8'
DATA_NAT_R = 'EBF5FB'
DATA_VEN_E = 'FDF2E9'
DATA_NAT_E = 'EAF4FB'
DATA_IND   = 'F5F5F5'
DATA_DIF   = 'F4ECF7'

wb = Workbook()

# ── Sheet 1: Pooled summary ───────────────────────────────────────────────────
ws1 = wb.active
ws1.title = 'Pooled LAC4'

headers_s1    = ['Indicator',
                 'Venezuelan — Recent', 'Native — Recent',
                 'Venezuelan — Early',  'Native — Early',
                 'Diff Recent (V−N)',   'Diff Early (V−N)']
hdr_colors_s1 = [HDR_IND, HDR_VEN_R, HDR_NAT_R, HDR_VEN_E, HDR_NAT_E, HDR_DIF, HDR_DIF]

for col_i, (h, hc) in enumerate(zip(headers_s1, hdr_colors_s1), start=1):
    cell = ws1.cell(row=1, column=col_i, value=h)
    cell.fill = _fill(hc); cell.font = _font(bold=True)
    cell.alignment = _align(); cell.border = _border_all()

data_colors_s1 = [DATA_IND, DATA_VEN_R, DATA_NAT_R, DATA_VEN_E, DATA_NAT_E, DATA_DIF, DATA_DIF]

for row_i, ind in enumerate(INDICATORS, start=2):
    vr = pooled_recent['Venezuela'][ind]
    nr = pooled_recent['Native'][ind]
    ve = pooled_early['Venezuela'][ind]
    ne = pooled_early['Native'][ind]
    vals = [CLEAN_NAMES[ind], round(vr, 2), round(nr, 2), round(ve, 2), round(ne, 2),
            round(vr - nr, 2), round(ve - ne, 2) if np.isfinite(ve) and np.isfinite(ne) else '']
    for col_i, (val, dc) in enumerate(zip(vals, data_colors_s1), start=1):
        cell = ws1.cell(row=row_i, column=col_i, value=val)
        cell.fill = _fill(dc); cell.font = _font()
        cell.alignment = _align(h='left' if col_i == 1 else 'right')
        cell.border = _border_all()
        if col_i > 1 and isinstance(val, float):
            cell.number_format = '0.00'

ws1.column_dimensions['A'].width = 42
for col_letter in ['B', 'C', 'D', 'E', 'F', 'G']:
    ws1.column_dimensions[col_letter].width = 20
ws1.row_dimensions[1].height = 22

note_row = len(INDICATORS) + 3
ws1.cell(row=note_row, column=1,
         value='Source: HDMF project. Recent: COL GEIH 2025t3, PER ENAHO 2024a, '
               'CHL CASEN 2024a, ECU ENEMDU 2025m12. '
               'Early: COL GEIH 2018t3, PER ENAHO 2018a, CHL CASEN 2017a, ECU ENEMDU 2018m12. '
               'Weighted estimates. Informality = 1 − formal_ci.')
ws1.cell(row=note_row, column=1).font = _font(size=8, color='666666')

# ── Sheet 2: Country breakdown ────────────────────────────────────────────────
ws2 = wb.create_sheet('Country breakdown')

country_df_export = country_df.copy()
for col in country_df_export.select_dtypes(float).columns:
    country_df_export[col] = country_df_export[col].round(2)

cols2 = list(country_df_export.columns)
for col_i, h in enumerate(cols2, start=1):
    cell = ws2.cell(row=1, column=col_i, value=h)
    cell.fill = _fill(HDR_IND); cell.font = _font(bold=True)
    cell.alignment = _align(); cell.border = _border_all()

for row_i, row in enumerate(country_df_export.itertuples(index=False), start=2):
    period_label = row[0]
    grp = row[2]
    if period_label == RECENT_LABEL:
        row_color = DATA_VEN_R if grp == 'Venezuela' else DATA_NAT_R
    else:
        row_color = DATA_VEN_E if grp == 'Venezuela' else DATA_NAT_E
    for col_i, val in enumerate(row, start=1):
        cell = ws2.cell(row=row_i, column=col_i, value=val)
        cell.fill = _fill(row_color); cell.font = _font()
        cell.alignment = _align(h='left' if col_i <= 3 else 'right')
        cell.border = _border_all()
        if col_i > 3 and isinstance(val, float):
            cell.number_format = '0.00'

ws2.column_dimensions['A'].width = 20
ws2.column_dimensions['B'].width = 10
ws2.column_dimensions['C'].width = 14
for col_i in range(4, len(cols2) + 1):
    ws2.column_dimensions[get_column_letter(col_i)].width = 26
ws2.row_dimensions[1].height = 22

# ── Sheet 3: Chart-ready data (minimal — select A1:E6 → Insert Chart) ─────────
# Indicators reversed: Excel bar charts plot from bottom up, so reversing here
# makes Unemployment appear at the top of the Excel chart automatically.
ws3 = wb.create_sheet('Chart Data')

# Series column headers — match chart colors
CHART_HEADERS = [
    ('Indicator',                  'D9D9D9', '000000'),
    ('Venezuelan (2024–2025)',     'C0392B', 'FFFFFF'),   # dark crimson
    ('Native (2024–2025)',         '1A5276', 'FFFFFF'),   # dark navy
    ('Venezuelan (2017–2018)',     'E67E22', 'FFFFFF'),   # orange
    ('Native (2017–2018)',         '1E8449', 'FFFFFF'),   # forest green
]

for col_i, (label, bg, fg) in enumerate(CHART_HEADERS, start=1):
    cell = ws3.cell(row=1, column=col_i, value=label)
    cell.fill      = _fill(bg)
    cell.font      = Font(bold=True, size=11, color=fg)
    cell.alignment = _align(h='center')
    cell.border    = _border_all()

# Data rows — reversed order so Excel bar chart reads top-to-bottom correctly
row_bg_light = ['F5F5F5', 'FAEAE8', 'EBF5FB', 'FDF2E9', 'EAF4FB']

for row_i, ind in enumerate(reversed(INDICATORS), start=2):
    vr = round(pooled_recent['Venezuela'][ind], 1)
    nr = round(pooled_recent['Native'][ind],    1)
    ve = round(pooled_early['Venezuela'][ind],  1)
    ne = round(pooled_early['Native'][ind],     1)
    row_vals = [CLEAN_NAMES[ind], vr, nr, ve, ne]

    for col_i, val in enumerate(row_vals, start=1):
        cell = ws3.cell(row=row_i, column=col_i, value=val)
        cell.font      = _font(size=11)
        cell.alignment = _align(h='left' if col_i == 1 else 'center')
        cell.border    = _border_all()
        # Subtle tint matching the series color family
        tints = ['F5F5F5', 'FAEAE8', 'EBF5FB', 'FDF2E9', 'EAF4FB']
        cell.fill = _fill(tints[col_i - 1])
        if col_i > 1 and isinstance(val, float):
            cell.number_format = '0.0'

# Column widths
ws3.column_dimensions['A'].width = 38
for col_letter in ['B', 'C', 'D', 'E']:
    ws3.column_dimensions[col_letter].width = 22
ws3.row_dimensions[1].height = 24

# Usage note
note_r = len(INDICATORS) + 3
ws3.cell(row=note_r, column=1,
         value='→ Select A1:E6 → Insert → Bar/Column Chart → Clustered Bar.'
               '  Axis is already reversed for correct top-to-bottom order.')
ws3.cell(row=note_r, column=1).font = _font(size=9, color='444444', bold=True)
ws3.merge_cells(start_row=note_r, start_column=1,
                end_row=note_r, end_column=5)

src_r = note_r + 1
ws3.cell(row=src_r, column=1,
         value='Source: HDMF project. Recent: COL GEIH 2025t3 · PER ENAHO 2024a · '
               'CHL CASEN 2024a · ECU ENEMDU 2025m12. '
               'Early: COL GEIH 2018t3 · PER ENAHO 2018a · CHL CASEN 2017a · ECU ENEMDU 2018m12. '
               'Weighted estimates.')
ws3.cell(row=src_r, column=1).font = _font(size=8, color='666666')
ws3.merge_cells(start_row=src_r, start_column=1,
                end_row=src_r, end_column=5)

table_path = os.path.join(OUT_DIR, 'venezuela_vs_native_table.xlsx')
wb.save(table_path)
print(f'Table saved -> {table_path}')
print(f'\nDone. Outputs in: {OUT_DIR}')
