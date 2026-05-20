"""
hdmf_venezuela_bycountry.py
────────────────────────────
Dumbbell chart: Venezuelan migrants vs. Natives by country.
One figure per indicator (5 figures), 4 countries on y-axis.

Each country row shows TWO dumbbell pairs:
  • Upper sub-row (solid line)  — most recent wave (2024–25)
  • Lower sub-row (dashed line) — earliest available wave (2017–18)

Legend arranged in 2 columns: Early (left) | Recent (right).
Grid lines every 10 percentage points.
Excel export: one sheet per indicator + one summary sheet.

Usage
──────
  py hdmf_venezuela_bycountry.py
"""

import os
import pickle
from functools import reduce

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator
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
LAC4   = ['COL', 'PER', 'CHL', 'ECU', 'ESP']
GROUPS = ['Venezuela', 'Native']

RECENT_WAVES = {'COL': '2025t3', 'PER': '2024a', 'CHL': '2024a',  'ECU': '2025m12', 'ESP': '2025a'}
EARLY_WAVES  = {'COL': '2018t3', 'PER': '2018a', 'CHL': '2017a',  'ECU': '2018m12', 'ESP': '2018a'}

RECENT_LABEL = 'Recent (2024–25)'
EARLY_LABEL  = 'Early (2017–18)'

COLOR_VEN = '#C0392B'   # vivid crimson — all Venezuelan (both periods)
COLOR_NAT = '#1A5276'   # deep navy     — all Native    (both periods)

LINE_COLOR_GAP = '#999999'   # gap line (period distinguished by solid/dashed)

DOT_SIZE   = 120
LINE_WIDTH = 2.2

COUNTRY_LABELS = {'COL': 'Colombia', 'PER': 'Peru', 'CHL': 'Chile', 'ECU': 'Ecuador', 'ESP': 'Spain'}

# Fixed x-axis limits per indicator (consistent scale across charts)
X_AXIS_MAX = {
    'unemployment_rate':  30,
    'inactivity_rate':   100,
    'informality':       100,
    'higher_education':  100,
    'long_hours_50plus': 100,
}

INDICATORS = [
    'Unemployment rate\n(% of active pop.)',
    'Inactivity rate\n(% of working-age pop.)',
    'Informality\n(% of employed pop.)',
    'Higher education\n(% of pop., post-secondary+)',
    'Long hours (50+)\n(% of employed pop.)',
]

PANEL_TITLES = [
    'Unemployment rate\n(% of economically active pop., 16–64)',
    'Inactivity rate\n(% of working-age pop., 16–64)',
    'Informality\n(% of employed pop.)',
    'Higher education\n(% of total pop., post-secondary+)',
    'Long hours (50+ hrs/week)\n(% of employed pop.)',
]

FILE_SLUGS = [
    'unemployment_rate',
    'inactivity_rate',
    'informality',
    'higher_education',
    'long_hours_50plus',
]

CLEAN_IND = [
    'Unemployment rate (% active pop.)',
    'Inactivity rate (% working-age pop.)',
    'Informality (% employed pop.)',
    'Higher education (% pop., post-sec.+)',
    'Long hours 50+ (% employed pop.)',
]

# Per-chart QA footnotes
CHART_FOOTNOTES = {
    'unemployment_rate': (
        '¹ PER 2017–18: n = 41 unweighted Venezuelan PEA obs. Zero unemployed recorded — '
        'estimate unreliable due to very small sample. Venezuelans in Peru in 2018 appear to '
        'have accepted informal work immediately upon arrival (see Informality chart).\n'
        '² Working-age population: ages 16–64, applied consistently across all countries, '
        'waves, and groups.'
    ),
    'inactivity_rate': (
        '¹ Venezuelan inactivity is consistently lower than native across all countries and '
        'both periods — reflecting strong labor force attachment under adverse conditions.\n'
        '² CHL 2017–18: Venezuelan inactivity (8.2 %) is especially low, consistent with the '
        'highly selected, educated early arrivals (see Higher Education chart).\n'
        '³ Working-age population: ages 16–64.'
    ),
    'informality': (
        '¹ CHL 2017–18: Venezuelan informality (15.1 %) was lower than native (29.8 %) — '
        'gap reversed by 2024–25 (Ven 30.9 % > Nat 22.5 %). Reflects positive selection of '
        'early arrivals: highly educated professionals who accessed formal employment.\n'
        '² PER 2017–18: n = 41 employed Venezuelan obs., all informal (93.4 %). '
        'Estimate unreliable due to very small sample.'
    ),
    'higher_education': (
        '¹ CHL 2017–18: n = 743 Venezuelan obs. (weighted ~180k). Early arrivals were '
        'positively selected professionals; share fell to 30.0 % by 2024–25 as migration '
        'became more diverse. CHL edu_hdmf codes 1–7 only; threshold ≥7 correctly applied.\n'
        '² COL: Venezuelan higher education (6.2 %) is below native (10.7 %) — unique among '
        'LAC-4. Reflects large, diverse cross-border migrant population with lower fixed '
        'migration costs. Pattern is consistent across both waves (2018: 7.3 % vs 8.1 %).'
    ),
    'long_hours_50plus': (
        '¹ COL: ~55 % item non-response in the hours variable (consistent across 2018 and '
        '2025 waves). Effective sample is smaller; no directional bias detected.\n'
        '² PER 2017–18: n = 41 employed Venezuelan obs. High variance — interpret with caution.'
    ),
}

# ── Load cache ─────────────────────────────────────────────────────────────────
print(f'Loading cache: {CACHE_FILE}')
with open(CACHE_FILE, 'rb') as fh:
    _cache = pickle.load(fh)
data = _cache['data']
print(f'Loaded {len(data):,} rows  |  countries: {sorted(data["pais_c"].unique())}')
print(f'Periods: {sorted(data["periodo_c"].unique())}')


# ── Filter helpers ─────────────────────────────────────────────────────────────
def filter_waves(df, wave_map):
    masks = [
        (df['pais_c'] == country) & (df['periodo_c'] == period)
        for country, period in wave_map.items()
    ]
    combined = reduce(lambda a, b: a | b, masks)
    return df[combined & df['foreign_born'].isin(GROUPS)].copy()


df_recent = filter_waves(data, RECENT_WAVES)
df_early  = filter_waves(data, EARLY_WAVES)

print(f'\nRecent rows: {len(df_recent):,}  |  Early rows: {len(df_early):,}')


# ── Weighted mean helper ───────────────────────────────────────────────────────
def wavg(v_series, w_series):
    v = pd.to_numeric(v_series, errors='coerce').to_numpy(dtype=float)
    w = pd.to_numeric(w_series, errors='coerce').to_numpy(dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if mask.sum() == 0:
        return np.nan
    return float(np.average(v[mask], weights=w[mask]))


# ── Compute indicators by country × group for a given filtered df ─────────────
def compute_country(df):
    df = df.copy()
    df['higher_edu_ci'] = (pd.to_numeric(df['edu_hdmf'], errors='coerce') >= 7).astype(float)
    df.loc[df['edu_hdmf'].isna(), 'higher_edu_ci'] = np.nan

    rows = []
    for country in LAC4:
        dfc  = df[df['pais_c'] == country]
        wapc = dfc[dfc['edad_ci'].between(16, 64)]
        peac = wapc[wapc['pea_ci'] == 1]
        empc = dfc[dfc['emp_ci'] == 1].copy()
        empc['longhours_ci'] = (pd.to_numeric(empc['horastot_ci'], errors='coerce') > 50).astype(float)
        empc.loc[empc['horastot_ci'].isna(), 'longhours_ci'] = np.nan

        for grp in GROUPS:
            rows.append({
                'country': country,
                'group':   grp,
                INDICATORS[0]: wavg(peac.loc[peac['foreign_born'] == grp, 'desemp_ci'],
                                    peac.loc[peac['foreign_born'] == grp, 'factor_ci']) * 100,
                INDICATORS[1]: wavg(wapc.loc[wapc['foreign_born'] == grp, 'inactivo_ci'],
                                    wapc.loc[wapc['foreign_born'] == grp, 'factor_ci']) * 100,
                INDICATORS[2]: (1 - wavg(empc.loc[empc['foreign_born'] == grp, 'formal_ci'],
                                         empc.loc[empc['foreign_born'] == grp, 'factor_ci'])) * 100,
                INDICATORS[3]: wavg(dfc.loc[dfc['foreign_born'] == grp, 'higher_edu_ci'],
                                    dfc.loc[dfc['foreign_born'] == grp, 'factor_ci']) * 100,
                INDICATORS[4]: wavg(empc.loc[empc['foreign_born'] == grp, 'longhours_ci'],
                                    empc.loc[empc['foreign_born'] == grp, 'factor_ci']) * 100,
            })
    return pd.DataFrame(rows)


results_recent = compute_country(df_recent)
results_early  = compute_country(df_early)

print('\n-- Recent results -------------------------------------------')
for ind in INDICATORS:
    pivot = results_recent.pivot_table(index='country', columns='group', values=ind)
    pivot['Gap'] = pivot.get('Venezuela', np.nan) - pivot.get('Native', np.nan)
    print(f'\n  {ind.replace(chr(10), " ")}')
    print(pivot.round(1).to_string())

print('\n-- Early results --------------------------------------------')
for ind in INDICATORS:
    pivot = results_early.pivot_table(index='country', columns='group', values=ind)
    pivot['Gap'] = pivot.get('Venezuela', np.nan) - pivot.get('Native', np.nan)
    print(f'\n  {ind.replace(chr(10), " ")}')
    print(pivot.round(1).to_string())


# ── Chart — dual-period dumbbell, one figure per indicator ────────────────────
plt.rcParams.update({'font.family': 'DejaVu Sans'})

COUNTRY_ORDER = LAC4[::-1]   # ECU, CHL, PER, COL → bottom-to-top → COL at top
y_idx         = {c: i for i, c in enumerate(COUNTRY_ORDER)}

Y_OFF_RECENT =  0.19
Y_OFF_EARLY  = -0.19
LABEL_V_OFF  =  0.13
LABEL_H_OFF  =  1.0
MIN_GAP_INLINE = 4.0

# Legend — 3 columns: Venezuelan | Native | Gap
# Layout (ncol=3, 6 items):
#   Row 1:  Venezuelan (●)  |  Native (●)  |  Gap — Recent (—)
#   Row 2:   [spacer]       |  [spacer]    |  Gap — Early  (- -)
_spacer = Patch(visible=False, label='')
handles_legend = [
    mlines.Line2D([], [], color=COLOR_VEN, marker='o', linestyle='None',
                  markersize=9, label='Venezuelan'),
    mlines.Line2D([], [], color=COLOR_NAT, marker='o', linestyle='None',
                  markersize=9, label='Native'),
    mlines.Line2D([], [], color=LINE_COLOR_GAP, linewidth=2.0, linestyle='-',
                  label=f'Gap — {RECENT_LABEL}'),
    _spacer,
    _spacer,
    mlines.Line2D([], [], color=LINE_COLOR_GAP, linewidth=2.0, linestyle='--',
                  label=f'Gap — {EARLY_LABEL}'),
]

for ind, title, slug in zip(INDICATORS, PANEL_TITLES, FILE_SLUGS):

    fig, ax = plt.subplots(figsize=(10, 7.2))
    all_vals = []

    for country in LAC4:
        y = y_idx[country]

        if y % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color='#F5F5F5', zorder=0, linewidth=0)

        for results, y_off, ls in [
            (results_recent, Y_OFF_RECENT, '-' ),
            (results_early,  Y_OFF_EARLY,  '--'),
        ]:
            lc, c_ven, c_nat = LINE_COLOR_GAP, COLOR_VEN, COLOR_NAT
            y_row = y + y_off

            v_row = results[(results['country'] == country) & (results['group'] == 'Venezuela')]
            n_row = results[(results['country'] == country) & (results['group'] == 'Native')]
            v_val = float(v_row[ind].values[0]) if len(v_row) else np.nan
            n_val = float(n_row[ind].values[0]) if len(n_row) else np.nan

            if pd.notna(v_val): all_vals.append(v_val)
            if pd.notna(n_val): all_vals.append(n_val)

            # Gap line
            if pd.notna(v_val) and pd.notna(n_val):
                ax.plot([min(v_val, n_val), max(v_val, n_val)], [y_row, y_row],
                        color=lc, linewidth=LINE_WIDTH, linestyle=ls, zorder=2,
                        solid_capstyle='round', dash_capstyle='round')

            # Dots
            if pd.notna(n_val):
                ax.scatter(n_val, y_row, color=c_nat, s=DOT_SIZE, zorder=4,
                           edgecolors='white', linewidths=0.8)
            if pd.notna(v_val):
                ax.scatter(v_val, y_row, color=c_ven, s=DOT_SIZE, zorder=4,
                           edgecolors='white', linewidths=0.8)

            # Labels
            gap    = abs(v_val - n_val) if (pd.notna(v_val) and pd.notna(n_val)) else np.inf
            inline = gap < MIN_GAP_INLINE

            if inline:
                lo = min(v for v in [v_val, n_val] if pd.notna(v))
                hi = max(v for v in [v_val, n_val] if pd.notna(v))
                if pd.notna(n_val) and pd.notna(v_val):
                    left_c,  left_lbl  = (c_nat, f'{n_val:.1f}') if n_val <= v_val else (c_ven, f'{v_val:.1f}')
                    right_c, right_lbl = (c_ven, f'{v_val:.1f}') if n_val <= v_val else (c_nat, f'{n_val:.1f}')
                    ax.text(lo - LABEL_H_OFF, y_row, left_lbl,
                            ha='right', va='center', fontsize=9, color=left_c,  fontweight='bold')
                    ax.text(hi + LABEL_H_OFF, y_row, right_lbl,
                            ha='left',  va='center', fontsize=9, color=right_c, fontweight='bold')
                elif pd.notna(n_val):
                    ax.text(n_val, y_row, f'{n_val:.1f}',
                            ha='right', va='center', fontsize=9, color=c_nat, fontweight='bold')
                elif pd.notna(v_val):
                    ax.text(v_val, y_row, f'{v_val:.1f}',
                            ha='left',  va='center', fontsize=9, color=c_ven, fontweight='bold')
            else:
                if pd.notna(v_val):
                    ax.text(v_val, y_row + LABEL_V_OFF, f'{v_val:.1f}',
                            ha='center', va='bottom', fontsize=9, color=c_ven, fontweight='bold')
                if pd.notna(n_val):
                    ax.text(n_val, y_row - LABEL_V_OFF, f'{n_val:.1f}',
                            ha='center', va='top',    fontsize=9, color=c_nat, fontweight='bold')

    # ── Axes ──────────────────────────────────────────────────────────────────
    ax.set_yticks(list(y_idx.values()))
    ax.set_yticklabels(['' for _ in COUNTRY_ORDER])
    ax.set_ylim(-0.6, len(LAC4) - 0.4)
    ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', labelsize=9)

    # Country name centred between sub-rows; year labels aligned to each sub-row
    blend = ax.get_yaxis_transform()
    for country in COUNTRY_ORDER:
        y_c = y_idx[country]
        ax.text(-0.02, y_c, COUNTRY_LABELS[country],
                transform=blend, ha='right', va='center',
                fontsize=10, clip_on=False)
        ax.text(-0.02, y_c + Y_OFF_RECENT, RECENT_WAVES[country][:4],
                transform=blend, ha='right', va='center',
                fontsize=7.5, color='#888888', clip_on=False)
        ax.text(-0.02, y_c + Y_OFF_EARLY, EARLY_WAVES[country][:4],
                transform=blend, ha='right', va='center',
                fontsize=7.5, color='#888888', clip_on=False)

    x_max = X_AXIS_MAX.get(slug, 100)
    ax.set_xlim(0, x_max)

    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.grid(True, linestyle='--', alpha=0.35, color='grey', zorder=0)
    ax.set_axisbelow(True)

    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#CCCCCC')

    # ── Legend — 2 columns: Early (left) | Recent (right) ─────────────────────
    fig.legend(
        handles=handles_legend,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.06),
        ncol=3,
        frameon=False,
        fontsize=9,
        handlelength=1.8,
        columnspacing=2.5,
        handletextpad=0.6,
    )

    # ── Title ──────────────────────────────────────────────────────────────────
    fig.suptitle(
        f'Venezuelan migrants vs. Natives\n{title}',
        fontsize=12, fontweight='bold', y=1.03, x=0.02, ha='left',
    )

    fig.subplots_adjust(bottom=0.16)

    chart_path = os.path.join(OUT_DIR, f'venezuela_vs_native_ind_{slug}.png')
    fig.savefig(chart_path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Chart saved -> {chart_path}')


# ── Excel export ──────────────────────────────────────────────────────────────
# openpyxl helpers
def _fill(hex_col):
    return PatternFill('solid', fgColor=hex_col)

def _font(bold=False, size=10, color='000000'):
    return Font(bold=bold, size=size, color=color)

def _side(style='thin', color='CCCCCC'):
    return Side(style=style, color=color)

def _border():
    s = _side()
    return Border(left=s, right=s, top=s, bottom=s)

def _align(h='center', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)


# Color palette matching the chart
HDR_VEN_E  = 'FAE3CA'   # light amber  (early Venezuelan)
HDR_VEN_R  = 'F1C0BB'   # light crimson (recent Venezuelan)
HDR_NAT_E  = 'D5EFD6'   # light green   (early Native)
HDR_NAT_R  = 'BDD7EE'   # light navy    (recent Native)
HDR_GAP    = 'E8DAEF'   # soft purple   (gap)
HDR_IND    = 'D9D9D9'   # grey          (indicator / country)

DATA_VEN_E = 'FDF2E9'
DATA_VEN_R = 'FAEAE8'
DATA_NAT_E = 'EAFAEB'
DATA_NAT_R = 'EBF5FB'
DATA_GAP   = 'F4ECF7'
DATA_IND   = 'F5F5F5'

COUNTRY_ORDER_XL = LAC4   # COL, PER, CHL, ECU — top to bottom in Excel

COL_HEADERS = [
    ('Country',               HDR_IND,   DATA_IND),
    ('Venezuelan — Early',    HDR_VEN_E, DATA_VEN_E),
    ('Native — Early',        HDR_NAT_E, DATA_NAT_E),
    ('Gap Early (V−N)',        HDR_GAP,   DATA_GAP),
    ('Venezuelan — Recent',   HDR_VEN_R, DATA_VEN_R),
    ('Native — Recent',       HDR_NAT_R, DATA_NAT_R),
    ('Gap Recent (V−N)',       HDR_GAP,   DATA_GAP),
]

wb = Workbook()

def write_indicator_sheet(ws, ind_key, clean_name, wave_label_early, wave_label_recent):
    """Write one indicator table: rows = countries, cols = Early/Recent values."""

    # Sub-header rows with wave labels
    ws.merge_cells('B1:D1')
    ws['B1'] = f'Early — {wave_label_early}'
    ws['B1'].fill    = _fill(HDR_VEN_E)
    ws['B1'].font    = _font(bold=True, size=10)
    ws['B1'].alignment = _align()
    ws['B1'].border  = _border()

    ws.merge_cells('E1:G1')
    ws['E1'] = f'Recent — {wave_label_recent}'
    ws['E1'].fill    = _fill(HDR_VEN_R)
    ws['E1'].font    = _font(bold=True, size=10)
    ws['E1'].alignment = _align()
    ws['E1'].border  = _border()

    ws['A1'] = ''
    ws['A1'].border = _border()

    # Column headers (row 2)
    for col_i, (hdr, hdr_bg, _) in enumerate(COL_HEADERS, start=1):
        cell = ws.cell(row=2, column=col_i, value=hdr)
        cell.fill      = _fill(hdr_bg)
        cell.font      = _font(bold=True, size=10)
        cell.alignment = _align()
        cell.border    = _border()

    # Data rows (rows 3–6)
    for row_i, country in enumerate(COUNTRY_ORDER_XL, start=3):
        v_r_row = results_recent[(results_recent['country'] == country) & (results_recent['group'] == 'Venezuela')]
        n_r_row = results_recent[(results_recent['country'] == country) & (results_recent['group'] == 'Native')]
        v_e_row = results_early [(results_early ['country'] == country) & (results_early ['group'] == 'Venezuela')]
        n_e_row = results_early [(results_early ['country'] == country) & (results_early ['group'] == 'Native')]

        v_r = round(float(v_r_row[ind_key].values[0]), 2) if len(v_r_row) else None
        n_r = round(float(n_r_row[ind_key].values[0]), 2) if len(n_r_row) else None
        v_e = round(float(v_e_row[ind_key].values[0]), 2) if len(v_e_row) else None
        n_e = round(float(n_e_row[ind_key].values[0]), 2) if len(n_e_row) else None

        gap_r = round(v_r - n_r, 2) if (v_r is not None and n_r is not None) else None
        gap_e = round(v_e - n_e, 2) if (v_e is not None and n_e is not None) else None

        row_vals_bg = [
            (COUNTRY_LABELS[country], DATA_IND),
            (v_e, DATA_VEN_E),
            (n_e, DATA_NAT_E),
            (gap_e, DATA_GAP),
            (v_r, DATA_VEN_R),
            (n_r, DATA_NAT_R),
            (gap_r, DATA_GAP),
        ]

        for col_i, (val, bg) in enumerate(row_vals_bg, start=1):
            cell = ws.cell(row=row_i, column=col_i, value=val)
            cell.fill      = _fill(bg)
            cell.font      = _font(size=10)
            cell.alignment = _align(h='left' if col_i == 1 else 'center')
            cell.border    = _border()
            if isinstance(val, float):
                cell.number_format = '0.00'

    # Source note
    note_row = len(COUNTRY_ORDER_XL) + 4
    src_cell = ws.cell(row=note_row, column=1,
                       value=f'{clean_name}. Source: HDMF project. '
                             f'Early: COL GEIH 2018t3 · PER ENAHO 2018a · CHL CASEN 2017a · ECU ENEMDU 2018m12 · ESP EPA 2018a. '
                             f'Recent: COL GEIH 2025t3 · PER ENAHO 2024a · CHL CASEN 2024a · ECU ENEMDU 2025m12 · ESP EPA 2025a. '
                             f'Weighted estimates.')
    src_cell.font = _font(size=8, color='666666')
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=7)

    # Chart insertion hint
    hint_row = note_row - 1
    last_data_row = 2 + len(COUNTRY_ORDER_XL)
    hint_cell = ws.cell(row=hint_row, column=1,
                        value=f'→ Select A2:G{last_data_row} → Insert → Bar/Column Chart → Clustered Bar.')
    hint_cell.font = _font(size=9, bold=True, color='444444')
    ws.merge_cells(start_row=hint_row, start_column=1, end_row=hint_row, end_column=7)

    # Column widths
    ws.column_dimensions['A'].width = 14
    for col_letter in ['B', 'C', 'D', 'E', 'F', 'G']:
        ws.column_dimensions[col_letter].width = 22
    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 20


# ── Per-indicator sheets ──────────────────────────────────────────────────────
first_sheet = True
for ind_key, clean_name, slug in zip(INDICATORS, CLEAN_IND, FILE_SLUGS):
    sheet_name = clean_name[:31]   # Excel sheet name max 31 chars
    if first_sheet:
        ws = wb.active
        ws.title = sheet_name
        first_sheet = False
    else:
        ws = wb.create_sheet(title=sheet_name)

    wave_early_label  = 'COL 2018t3 · PER 2018a · CHL 2017a · ECU 2018m12 · ESP 2018a'
    wave_recent_label = 'COL 2025t3 · PER 2024a · CHL 2024a · ECU 2025m12 · ESP 2025a'
    write_indicator_sheet(ws, ind_key, clean_name, wave_early_label, wave_recent_label)


# ── Summary sheet — all indicators stacked ────────────────────────────────────
ws_sum = wb.create_sheet(title='All indicators')

# Summary column headers
SUM_HEADERS = [
    ('Indicator',             HDR_IND,   DATA_IND),
    ('Country',               HDR_IND,   DATA_IND),
    ('Venezuelan — Early',    HDR_VEN_E, DATA_VEN_E),
    ('Native — Early',        HDR_NAT_E, DATA_NAT_E),
    ('Gap Early (V−N)',        HDR_GAP,   DATA_GAP),
    ('Venezuelan — Recent',   HDR_VEN_R, DATA_VEN_R),
    ('Native — Recent',       HDR_NAT_R, DATA_NAT_R),
    ('Gap Recent (V−N)',       HDR_GAP,   DATA_GAP),
]

for col_i, (hdr, hdr_bg, _) in enumerate(SUM_HEADERS, start=1):
    cell = ws_sum.cell(row=1, column=col_i, value=hdr)
    cell.fill      = _fill(hdr_bg)
    cell.font      = _font(bold=True, size=10)
    cell.alignment = _align()
    cell.border    = _border()

# Alternating row colors by indicator group
IND_BAND_COLORS = [
    ('FAEAE8', 'EBF5FB'),   # unemployment — light red / blue
    ('FDF2E9', 'EAFAEB'),   # inactivity — amber / green
    ('F1C0BB', 'D5EFD6'),   # informality — stronger red / green
    ('FAE3CA', 'BDD7EE'),   # higher edu — amber / navy
    ('E8DAEF', 'D5EFD6'),   # long hours — purple / green
]

data_row = 2
for ind_i, (ind_key, clean_name) in enumerate(zip(INDICATORS, CLEAN_IND)):
    bg_ven, bg_nat = IND_BAND_COLORS[ind_i % len(IND_BAND_COLORS)]

    for country in COUNTRY_ORDER_XL:
        v_r_row = results_recent[(results_recent['country'] == country) & (results_recent['group'] == 'Venezuela')]
        n_r_row = results_recent[(results_recent['country'] == country) & (results_recent['group'] == 'Native')]
        v_e_row = results_early [(results_early ['country'] == country) & (results_early ['group'] == 'Venezuela')]
        n_e_row = results_early [(results_early ['country'] == country) & (results_early ['group'] == 'Native')]

        v_r = round(float(v_r_row[ind_key].values[0]), 2) if len(v_r_row) else None
        n_r = round(float(n_r_row[ind_key].values[0]), 2) if len(n_r_row) else None
        v_e = round(float(v_e_row[ind_key].values[0]), 2) if len(v_e_row) else None
        n_e = round(float(n_e_row[ind_key].values[0]), 2) if len(n_e_row) else None

        gap_r = round(v_r - n_r, 2) if (v_r is not None and n_r is not None) else None
        gap_e = round(v_e - n_e, 2) if (v_e is not None and n_e is not None) else None

        row_vals = [clean_name, COUNTRY_LABELS[country], v_e, n_e, gap_e, v_r, n_r, gap_r]
        row_bgs  = [DATA_IND, DATA_IND, DATA_VEN_E, DATA_NAT_E, DATA_GAP, DATA_VEN_R, DATA_NAT_R, DATA_GAP]

        for col_i, (val, bg) in enumerate(zip(row_vals, row_bgs), start=1):
            cell = ws_sum.cell(row=data_row, column=col_i, value=val)
            cell.fill      = _fill(bg)
            cell.font      = _font(size=10)
            cell.alignment = _align(h='left' if col_i <= 2 else 'center')
            cell.border    = _border()
            if isinstance(val, float):
                cell.number_format = '0.00'

        data_row += 1

    data_row += 1  # blank separator row between indicators

# Column widths for summary sheet
ws_sum.column_dimensions['A'].width = 36
ws_sum.column_dimensions['B'].width = 12
for col_letter in ['C', 'D', 'E', 'F', 'G', 'H']:
    ws_sum.column_dimensions[col_letter].width = 22
ws_sum.row_dimensions[1].height = 20

# Save
table_path = os.path.join(OUT_DIR, 'venezuela_vs_native_bycountry_table.xlsx')
wb.save(table_path)
print(f'\nExcel saved -> {table_path}')
print(f'Done. All outputs in: {OUT_DIR}')
