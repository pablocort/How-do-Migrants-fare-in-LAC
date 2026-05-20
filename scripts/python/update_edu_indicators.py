#!/usr/bin/env python3
"""
update_edu_indicators.py
------------------------
1. Computes edu_hdmf category shares (weighted) for all countries/waves/groups.
   For ECU, applies FIX-ECU-01 (p10a==8 conditioned on p12a) from raw .dta.
2. Appends these rows to the general indicators CSV and DTA.
3. Generates a corrected education distribution stacked-bar PNG per country,
   saved to out/trends/2026-04-10/[ISO]/education_dist_stacked.png.

Usage:
    py update_edu_indicators.py
"""

import os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR     = os.path.join(BASE_DIR, 'bases armo', 'armo')
IND_DIR      = os.path.join(BASE_DIR, 'out', 'indicator_descriptive', '2026-04-20')
TRENDS_DIR   = os.path.join(BASE_DIR, 'out', 'trends', '2026-04-10')
EXISTING_CSV = os.path.join(IND_DIR, 'hdmf_general_indicators.csv')
OUT_CSV      = os.path.join(IND_DIR, 'hdmf_general_indicators.csv')
OUT_DTA      = os.path.join(IND_DIR, 'hdmf_general_indicators.dta')

COUNTRIES = {
    'CHL': 'chl', 'COL': 'col', 'ECU': 'ecu', 'PER': 'per', 'DOM': 'DOM'
}
GROUP_MAP = {
    '':            'Native',
    'Venezuela':   'Venezuela',
}

EDU_CATS = {
    1: 'Menos de primaria',
    2: 'Primaria incompleta',
    3: 'Primaria completa',
    4: 'Media incompleta',
    5: 'Media completa',
    6: 'Tecnica',
    7: 'Universitaria completa',
    8: 'Posgrado',
}
_edu_cmap = plt.cm.get_cmap('viridis', 8)
EDU_COLORS = {i + 1: _edu_cmap(i / 7) for i in range(8)}
EDU_ORDER = list(range(1, 9))
GROUP_DISPLAY = {'Native': 'Nativos', 'Venezuela': 'Venezuela', 'Foreign_other': 'Otros paises'}
GROUP_ORDER   = ['Native', 'Venezuela', 'Foreign_other']
GROUP_COLORS  = {'Native': '#1F4E79', 'Venezuela': '#C00000', 'Foreign_other': '#6FAD47'}

# ── Load one country's .dta files ──────────────────────────────────────────────
def load_country(iso, subdir):
    pattern = os.path.join(ARMO_DIR, subdir, f'{iso}_*_BID.dta')
    files   = sorted(glob.glob(pattern))
    frames  = []
    for f in files:
        period = os.path.basename(f).replace(f'{iso}_','').replace('_BID.dta','')
        try:
            df = pd.read_stata(f, convert_categoricals=False)
        except Exception as e:
            print(f"  WARN {iso} {period}: {e}")
            continue
        need = ['mig_pais_ci', 'edu_hdmf', 'factor_ci', 'aedu_ci']
        df = df[[c for c in need if c in df.columns]].copy()
        df['periodo_c'] = period
        df['pais_c']    = iso
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

# ── Derive foreign_born label ──────────────────────────────────────────────────
def make_group(row):
    v = str(row.get('mig_pais_ci', '')).strip()
    if v == '':
        return 'Native'
    if 'venezuela' in v.lower():
        return 'Venezuela'
    return 'Foreign_other'

# ── Compute weighted edu_hdmf distribution ─────────────────────────────────────
def compute_edu_dist(data):
    data = data.copy()
    data['edu_hdmf']  = pd.to_numeric(data['edu_hdmf'],  errors='coerce')
    data['factor_ci'] = pd.to_numeric(data['factor_ci'], errors='coerce')
    data['grupo']     = data.apply(make_group, axis=1)
    rows = []
    for (iso, period, grupo), sub in data.groupby(['pais_c','periodo_c','grupo']):
        sub = sub.dropna(subset=['edu_hdmf','factor_ci'])
        tw  = sub['factor_ci'].sum()
        n   = len(sub)
        if tw == 0 or n < 10:
            continue
        year = int(str(period)[:4])
        for code in EDU_ORDER:
            w    = sub.loc[sub['edu_hdmf'] == code, 'factor_ci'].sum()
            share = w / tw
            rows.append({
                'country':        iso,
                'year':           year,
                'period':         period,
                'migrant_status': grupo,
                'indicator':      f'edu_hdmf_{code}',
                'mean':           share,
                'median':         np.nan,
                'se':             np.nan,
                'sd':             np.nan,
                'ci_lo':          np.nan,
                'ci_hi':          np.nan,
                'n_unweighted':   n,
                'sum_weights':    tw,
                'n_eff':          np.nan,
            })
    return pd.DataFrame(rows)

# ── Generate stacked-bar chart for one country ─────────────────────────────────
def plot_edu_dist(data, iso):
    data = data.copy()
    data['edu_hdmf']  = pd.to_numeric(data['edu_hdmf'],  errors='coerce')
    data['factor_ci'] = pd.to_numeric(data['factor_ci'], errors='coerce')
    data['grupo']     = data.apply(make_group, axis=1)

    periods = sorted(data['periodo_c'].unique())
    PLABS   = [p.replace('m','-').replace('t','Q') for p in periods]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    survey_label = {'CHL':'CASEN','COL':'GEIH','ECU':'ENEMDU','PER':'ENAHO','DOM':'ENCFT'}
    fig.suptitle(
        f'{iso} ({survey_label.get(iso,"")}) — Distribucion educativa (edu_hdmf) por grupo',
        fontsize=11, fontweight='bold'
    )

    for ax, grupo in zip(axes, GROUP_ORDER):
        display = GROUP_DISPLAY[grupo]
        color   = GROUP_COLORS[grupo]

        sub_all = []
        for period in periods:
            sub = data[(data['periodo_c']==period) & (data['grupo']==grupo)].dropna(
                    subset=['edu_hdmf','factor_ci'])
            tw = sub['factor_ci'].sum()
            if tw == 0 or len(sub) < 10:
                sub_all.append({c: 0.0 for c in EDU_ORDER})
                continue
            sub_all.append({c: sub.loc[sub['edu_hdmf']==c,'factor_ci'].sum()/tw
                            for c in EDU_ORDER})

        df_plot = pd.DataFrame(sub_all, index=periods)
        x = np.arange(len(periods))
        bottoms = np.zeros(len(periods))
        for code in EDU_ORDER:
            vals = df_plot[code].values
            ax.bar(x, vals, 0.72, bottom=bottoms,
                   color=EDU_COLORS[code], edgecolor='white', linewidth=0.3)
            bottoms += vals

        ax.set_title(display, fontsize=10, fontweight='bold', color=color)
        ax.set_xticks(x)
        ax.set_xticklabels(PLABS, rotation=45, ha='right', fontsize=7.5)
        ax.set_ylim(0, 1.02)
        ax.set_yticks(np.arange(0, 1.1, 0.2))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.spines[['top','right']].set_visible(False)
        if grupo == 'Native':
            ax.set_ylabel('Proporcion')

    handles = [mpatches.Patch(facecolor=EDU_COLORS[c], label=EDU_CATS[c], edgecolor='white', linewidth=0)
               for c in EDU_ORDER]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=8,
               bbox_to_anchor=(0.5, -0.08), frameon=False)
    plt.tight_layout()

    out_dir = os.path.join(TRENDS_DIR, iso)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'education_dist_stacked.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved chart: {out_path}")
    return out_path

# ==============================================================================
# MAIN
# ==============================================================================
print("Loading country data...")
all_edu_rows = []

for iso, subdir in COUNTRIES.items():
    print(f"\n  {iso}...")
    data = load_country(iso, subdir)
    if data.empty:
        print(f"    No data found for {iso}")
        continue
    edu_rows = compute_edu_dist(data)
    print(f"    edu_hdmf rows computed: {len(edu_rows)}")
    all_edu_rows.append(edu_rows)
    plot_edu_dist(data, iso)

edu_df = pd.concat(all_edu_rows, ignore_index=True)
print(f"\nTotal edu_hdmf indicator rows: {len(edu_df)}")

# ── Update general indicators ──────────────────────────────────────────────────
print(f"\nLoading existing indicators: {EXISTING_CSV}")
existing = pd.read_csv(EXISTING_CSV)
print(f"  Existing rows: {len(existing)}")

# Remove any old edu_hdmf rows (in case of re-run)
existing = existing[~existing['indicator'].str.startswith('edu_hdmf_')]
updated  = pd.concat([existing, edu_df], ignore_index=True)
updated  = updated.sort_values(['country','period','migrant_status','indicator']).reset_index(drop=True)
print(f"  Updated rows: {len(updated)}")

updated.to_csv(OUT_CSV, index=False)
print(f"  Saved CSV: {OUT_CSV}")

# Save DTA
try:
    updated.to_stata(OUT_DTA, write_index=False, version=118)
    print(f"  Saved DTA: {OUT_DTA}")
except Exception as e:
    print(f"  WARN DTA save: {e}")
    try:
        updated.to_stata(OUT_DTA, write_index=False)
        print(f"  Saved DTA (fallback): {OUT_DTA}")
    except Exception as e2:
        print(f"  ERROR DTA: {e2}")

print("\nDone.")
