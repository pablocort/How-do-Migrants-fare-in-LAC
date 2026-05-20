"""
build_informality_chart_fixed.py
---------------------------------------------------------------------------
Informality dumbbell chart: Venezuelan migrants vs. Natives.
Countries: COL, PER, CHL, ECU  (Spain not included).
Same style as hdmf_venezuela_bycountry.py.

Output: out/venezuela_vs_native/YYYY-MM-DD/venezuela_vs_native_ind_informality.png

Generated with the Claude HDMF system -- 2026-05-18
"""

import os
import pickle
from datetime import date
from functools import reduce

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator

# -- Paths ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE_DIR, 'bases armo', 'armo')
CACHE_FILE = os.path.join(ARMO_DIR, '_hdmf_cache.pkl')
DATE_TAG   = date.today().strftime('%Y-%m-%d')
OUT_DIR    = os.path.join(BASE_DIR, 'out', 'venezuela_vs_native', DATE_TAG)
os.makedirs(OUT_DIR, exist_ok=True)

# -- Config --------------------------------------------------------------------
COUNTRIES = ['COL', 'PER', 'CHL', 'ECU']
GROUPS    = ['Venezuela', 'Native']

RECENT_WAVES = {'COL': '2025t3', 'PER': '2024a', 'CHL': '2024a', 'ECU': '2025m12'}
EARLY_WAVES  = {'COL': '2018t3', 'PER': '2018a', 'CHL': '2017a', 'ECU': '2018m12'}

RECENT_LABEL = 'Recent (2024-25)'
EARLY_LABEL  = 'Early (2017-18)'

COLOR_VEN    = '#C0392B'
COLOR_NAT    = '#1A5276'
LINE_COLOR   = '#999999'
DOT_SIZE     = 120
LINE_WIDTH   = 2.2
MIN_GAP_INLINE = 4.0
Y_OFF_RECENT =  0.19
Y_OFF_EARLY  = -0.19
LABEL_V_OFF  =  0.13
LABEL_H_OFF  =  1.0

COUNTRY_LABELS = {
    'COL': 'Colombia', 'PER': 'Peru', 'CHL': 'Chile', 'ECU': 'Ecuador',
}

IND_KEY   = 'informality'
PANEL_TTL = 'Venezuelan migrants vs. Natives\nInformality\n(% of employed pop.)'

# -- Load cache ----------------------------------------------------------------
print(f'Loading cache: {CACHE_FILE}')
with open(CACHE_FILE, 'rb') as fh:
    _cache = pickle.load(fh)
data = _cache['data']
print(f'Loaded {len(data):,} rows')

# -- Filter helpers ------------------------------------------------------------
def filter_waves(df, wave_map):
    masks = [
        (df['pais_c'] == c) & (df['periodo_c'] == p)
        for c, p in wave_map.items()
    ]
    combined = reduce(lambda a, b: a | b, masks)
    return df[combined & df['foreign_born'].isin(GROUPS)].copy()


df_recent = filter_waves(data, RECENT_WAVES)
df_early  = filter_waves(data, EARLY_WAVES)

# -- Weighted mean -------------------------------------------------------------
def wavg(v_series, w_series):
    v = pd.to_numeric(v_series, errors='coerce').to_numpy(dtype=float)
    w = pd.to_numeric(w_series, errors='coerce').to_numpy(dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if mask.sum() == 0:
        return np.nan
    return float(np.average(v[mask], weights=w[mask]))


# -- Compute informality by country x group ------------------------------------
def compute_informality(df):
    rows = []
    for country in COUNTRIES:
        dfc  = df[df['pais_c'] == country]
        empc = dfc[dfc['emp_ci'] == 1].copy()
        for grp in GROUPS:
            val = (1 - wavg(
                empc.loc[empc['foreign_born'] == grp, 'formal_ci'],
                empc.loc[empc['foreign_born'] == grp, 'factor_ci'],
            )) * 100
            rows.append({'country': country, 'group': grp, IND_KEY: val})
    return pd.DataFrame(rows)


results_recent = compute_informality(df_recent)
results_early  = compute_informality(df_early)

print('\nInformality results:')
for label, df_r in [('Recent', results_recent), ('Early', results_early)]:
    pivot = df_r.pivot_table(index='country', columns='group', values=IND_KEY)
    print(f'\n{label}:\n{pivot.round(1).to_string()}')

# -- Chart ---------------------------------------------------------------------
plt.rcParams.update({'font.family': 'DejaVu Sans'})

COUNTRY_ORDER = COUNTRIES[::-1]   # ECU, CHL, PER, COL -> bottom-to-top
y_idx = {c: i for i, c in enumerate(COUNTRY_ORDER)}

_spacer = Patch(visible=False, label='')
handles_legend = [
    mlines.Line2D([], [], color=COLOR_VEN, marker='o', linestyle='None',
                  markersize=9, label='Venezuelan'),
    mlines.Line2D([], [], color=COLOR_NAT, marker='o', linestyle='None',
                  markersize=9, label='Native'),
    mlines.Line2D([], [], color=LINE_COLOR, linewidth=2.0, linestyle='-',
                  label=f'Gap -- {RECENT_LABEL}'),
    _spacer,
    _spacer,
    mlines.Line2D([], [], color=LINE_COLOR, linewidth=2.0, linestyle='--',
                  label=f'Gap -- {EARLY_LABEL}'),
]

fig, ax = plt.subplots(figsize=(10, 5.5))

for country in COUNTRIES:
    y = y_idx[country]

    if y % 2 == 0:
        ax.axhspan(y - 0.5, y + 0.5, color='#F5F5F5', zorder=0, linewidth=0)

    for results, y_off, ls in [
        (results_recent, Y_OFF_RECENT, '-'),
        (results_early,  Y_OFF_EARLY,  '--'),
    ]:
        y_row = y + y_off

        v_row = results[(results['country'] == country) & (results['group'] == 'Venezuela')]
        n_row = results[(results['country'] == country) & (results['group'] == 'Native')]
        v_val = float(v_row[IND_KEY].values[0]) if len(v_row) else np.nan
        n_val = float(n_row[IND_KEY].values[0]) if len(n_row) else np.nan

        if pd.notna(v_val) and pd.notna(n_val):
            ax.plot([min(v_val, n_val), max(v_val, n_val)], [y_row, y_row],
                    color=LINE_COLOR, linewidth=LINE_WIDTH, linestyle=ls,
                    zorder=2, solid_capstyle='round', dash_capstyle='round')

        if pd.notna(n_val):
            ax.scatter(n_val, y_row, color=COLOR_NAT, s=DOT_SIZE, zorder=4,
                       edgecolors='white', linewidths=0.8)
        if pd.notna(v_val):
            ax.scatter(v_val, y_row, color=COLOR_VEN, s=DOT_SIZE, zorder=4,
                       edgecolors='white', linewidths=0.8)

        gap    = abs(v_val - n_val) if (pd.notna(v_val) and pd.notna(n_val)) else np.inf
        inline = gap < MIN_GAP_INLINE

        if inline:
            lo = min(v for v in [v_val, n_val] if pd.notna(v))
            hi = max(v for v in [v_val, n_val] if pd.notna(v))
            if pd.notna(n_val) and pd.notna(v_val):
                left_c,  left_lbl  = (COLOR_NAT, f'{n_val:.1f}') if n_val <= v_val else (COLOR_VEN, f'{v_val:.1f}')
                right_c, right_lbl = (COLOR_VEN, f'{v_val:.1f}') if n_val <= v_val else (COLOR_NAT, f'{n_val:.1f}')
                ax.text(lo - LABEL_H_OFF, y_row, left_lbl,
                        ha='right', va='center', fontsize=9, color=left_c, fontweight='bold')
                ax.text(hi + LABEL_H_OFF, y_row, right_lbl,
                        ha='left',  va='center', fontsize=9, color=right_c, fontweight='bold')
        else:
            if pd.notna(v_val):
                ax.text(v_val, y_row + LABEL_V_OFF, f'{v_val:.1f}',
                        ha='center', va='bottom', fontsize=9, color=COLOR_VEN, fontweight='bold')
            if pd.notna(n_val):
                ax.text(n_val, y_row - LABEL_V_OFF, f'{n_val:.1f}',
                        ha='center', va='top',    fontsize=9, color=COLOR_NAT, fontweight='bold')

# -- Axes ----------------------------------------------------------------------
ax.set_yticks(list(y_idx.values()))
ax.set_yticklabels(['' for _ in COUNTRY_ORDER])
ax.set_ylim(-0.6, len(COUNTRIES) - 0.4)
ax.tick_params(axis='y', length=0)
ax.tick_params(axis='x', labelsize=9)

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

ax.set_xlim(0, 100)
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.xaxis.grid(True, linestyle='--', alpha=0.35, color='grey', zorder=0)
ax.set_axisbelow(True)
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_color('#CCCCCC')

# -- Legend --------------------------------------------------------------------
fig.legend(
    handles=handles_legend,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.04),
    ncol=3,
    frameon=False,
    fontsize=9,
    handlelength=1.8,
    columnspacing=2.5,
    handletextpad=0.6,
)

fig.subplots_adjust(bottom=0.18)

out_path = os.path.join(OUT_DIR, 'venezuela_vs_native_ind_informality.png')
fig.savefig(out_path, dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print(f'\nSaved: {out_path}')
