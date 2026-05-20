#!/usr/bin/env python3
"""
verify_ecu_education.py
-----------------------
QA verification for FIX-ECU-01 (ECU Técnica bug).

Reads ECU *_BID.dta files directly (no cache needed).
Since p10a and p12a are preserved in the .dta files, this script can
compute BOTH the buggy and corrected edu_hdmf immediately — no Stata
re-run required.

Output:
    out/qa/ecu_education_verification.png   — before/after chart
    out/qa/ecu_edu_tecnica_summary.csv      — numeric summary table

Usage:
    py verify_ecu_education.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECU_DIR = os.path.join(BASE_DIR, 'bases armo', 'armo', 'ecu')
OUT_DIR = os.path.join(BASE_DIR, 'out', 'qa')
os.makedirs(OUT_DIR, exist_ok=True)

EDU_CATS = {
    1: 'Menos de primaria',
    2: 'Primaria incompleta',
    3: 'Primaria completa',
    4: 'Media incompleta',
    5: 'Media completa',
    6: 'Técnica',
    7: 'Universitaria completa',
    8: 'Posgrado',
}
EDU_COLORS = {
    1: '#c0392b',
    2: '#e67e22',
    3: '#f1c40f',
    4: '#7f8c8d',
    5: '#27ae60',
    6: '#16a085',   # teal — Técnica
    7: '#2980b9',
    8: '#8e44ad',
}
EDU_ORDER = list(range(1, 9))

GROUP_MAP = {'Native': 'Nativos', 'Venezuela': 'Venezuela', 'Foreign_other': 'Otros países'}
GROUP_ORDER = ['Nativos', 'Venezuela', 'Otros países']
GROUP_COLORS = {'Nativos': '#1F4E79', 'Venezuela': '#C00000', 'Otros países': '#6FAD47'}

# ── Load ECU .dta files ────────────────────────────────────────────────────────
COLS = ['mig_pais_ci', 'edu_hdmf', 'factor_ci', 'p10a', 'p12a']
dta_files = sorted(glob.glob(os.path.join(ECU_DIR, 'ECU_*_BID.dta')))
if not dta_files:
    raise FileNotFoundError(f"No ECU_*_BID.dta in {ECU_DIR}")

frames = []
for f in dta_files:
    period = os.path.basename(f).replace('ECU_', '').replace('_BID.dta', '')
    df = pd.read_stata(f, convert_categoricals=False)
    available = [c for c in COLS if c in df.columns]
    df = df[available].copy()
    df['periodo_c'] = period
    frames.append(df)
    print(f"  loaded {period}: {len(df):,} rows")

data = pd.concat(frames, ignore_index=True)

# ── Derive foreign_born ────────────────────────────────────────────────────────
data['foreign_born'] = data['mig_pais_ci'].apply(
    lambda x: 'Native' if str(x).strip() == '' else
              ('Venezuela' if 'venezuela' in str(x).lower() else 'Foreign_other')
)
data['grupo'] = data['foreign_born'].map(GROUP_MAP)

# ── Compute CORRECTED edu_hdmf using p10a / p12a ──────────────────────────────
data['p10a']  = pd.to_numeric(data.get('p10a',  pd.Series(dtype=float)), errors='coerce')
data['p12a']  = pd.to_numeric(data.get('p12a',  pd.Series(dtype=float)), errors='coerce')
data['edu_hdmf_orig']    = pd.to_numeric(data['edu_hdmf'], errors='coerce')
data['edu_hdmf_corrected'] = data['edu_hdmf_orig'].copy()

if 'p10a' in data.columns and 'p12a' in data.columns:
    # Fix: p10a==8 & p12a==1 → 6 (técnica completa)
    #      p10a==8 & p12a==2 → 5 (técnica incompleta → media completa)
    mask_complete   = (data['p10a'] == 8) & (data['p12a'] == 1)
    mask_incomplete = (data['p10a'] == 8) & (data['p12a'] == 2)
    mask_no_p12a    = (data['p10a'] == 8) & data['p12a'].isna()
    data.loc[mask_complete,   'edu_hdmf_corrected'] = 6
    data.loc[mask_incomplete, 'edu_hdmf_corrected'] = 5
    data.loc[mask_no_p12a,    'edu_hdmf_corrected'] = 6   # fallback: treat as complete
    n_fixed = mask_complete.sum() + mask_incomplete.sum() + mask_no_p12a.sum()
    print(f"\nRows affected by fix: {n_fixed:,}")
    print(f"  tecnica completa (code 6): {mask_complete.sum():,}")
    print(f"  tecnica incompleta->media  (code 5): {mask_incomplete.sum():,}")
    print(f"  no p12a, fallback->completa: {mask_no_p12a.sum():,}")

data['factor_ci'] = pd.to_numeric(data['factor_ci'], errors='coerce')
periods = sorted(data['periodo_c'].unique())
PERIOD_LABELS = [p.replace('m', '-') for p in periods]

# ── Weighted distribution helper ───────────────────────────────────────────────
def edu_dist(df, edu_col):
    rows = []
    for period in periods:
        for grupo in GROUP_ORDER:
            sub = df[(df['periodo_c'] == period) & (df['grupo'] == grupo)].dropna(
                subset=[edu_col, 'factor_ci'])
            tw = sub['factor_ci'].sum()
            if tw == 0 or len(sub) < 10:
                continue
            for code in EDU_ORDER:
                w = sub.loc[sub[edu_col] == code, 'factor_ci'].sum()
                rows.append({'periodo_c': period, 'grupo': grupo,
                             'edu_hdmf': code, 'share': w / tw})
    return pd.DataFrame(rows)

dist_orig    = edu_dist(data, 'edu_hdmf_orig')
dist_corrected = edu_dist(data, 'edu_hdmf_corrected')

# ── Figure layout: 2 rows (Before / After) × 3 cols (groups) ─────────────────
fig = plt.figure(figsize=(18, 11))
gs  = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.08)
fig.suptitle(
    'Ecuador — Verificación FIX-ECU-01: Distribución educativa (edu_hdmf)\n'
    'Antes (buggy: Técnica=0) vs. Después (corrección: p10a==8 & p12a)',
    fontsize=13, fontweight='bold'
)

ROW_TITLES = ['ANTES del fix  (datos actuales — Técnica = 0%)',
              'DESPUÉS del fix  (corrección aplicada — Técnica visible)']

for row_i, (dist_df, row_label) in enumerate(
        [(dist_orig, ROW_TITLES[0]), (dist_corrected, ROW_TITLES[1])]):

    pivot = dist_df.pivot_table(
        index=['periodo_c', 'grupo'], columns='edu_hdmf',
        values='share', fill_value=0).reset_index()

    for col_i, grupo in enumerate(GROUP_ORDER):
        ax = fig.add_subplot(gs[row_i, col_i])
        sub = pivot[pivot['grupo'] == grupo].sort_values('periodo_c')
        x = np.arange(len(sub))
        bottoms = np.zeros(len(sub))
        for code in EDU_ORDER:
            vals = sub[code].values if code in sub.columns else np.zeros(len(sub))
            ec   = '#003300' if code == 6 else 'white'
            lw   = 1.5      if code == 6 else 0.3
            ax.bar(x, vals, 0.72, bottom=bottoms,
                   color=EDU_COLORS[code], edgecolor=ec, linewidth=lw)
            if code == 6 and row_i == 1:
                for xi, (v, b) in enumerate(zip(vals, bottoms)):
                    if v > 0.012:
                        ax.text(xi, b + v / 2, f'{v:.1%}',
                                ha='center', va='center', fontsize=7,
                                fontweight='bold', color='white')
            bottoms += vals

        if col_i == 0:
            ax.set_ylabel(row_label, fontsize=8.5, color='#333333', labelpad=6)
        if row_i == 0:
            ax.set_title(grupo, fontsize=11, fontweight='bold',
                         color=GROUP_COLORS[grupo])
        ax.set_xticks(x)
        ax.set_xticklabels(PERIOD_LABELS, rotation=45, ha='right', fontsize=7.5)
        ax.set_ylim(0, 1.02)
        ax.set_yticks(np.arange(0, 1.1, 0.2))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.spines[['top', 'right']].set_visible(False)
        # shade after-fix row
        if row_i == 1:
            ax.set_facecolor('#f0fff4')

# legend
handles = [mpatches.Patch(facecolor=EDU_COLORS[c], label=EDU_CATS[c],
                           edgecolor='#003300' if c == 6 else EDU_COLORS[c],
                           linewidth=1.5 if c == 6 else 0)
           for c in EDU_ORDER]
fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9,
           bbox_to_anchor=(0.5, -0.03), frameon=True, framealpha=0.9,
           title='edu_hdmf  — Técnica (teal) highlighted')

out_img = os.path.join(OUT_DIR, 'ecu_education_verification.png')
fig.savefig(out_img, dpi=150, bbox_inches='tight')
print(f"\nSaved chart: {out_img}")

# ── Summary table: Técnica and Media completa shift ───────────────────────────
print("\n" + "="*72)
print("TÉCNICA vs MEDIA COMPLETA — shift per group × wave")
print("="*72)
summary_rows = []
for grupo in GROUP_ORDER:
    o  = dist_orig    [dist_orig    ['grupo'] == grupo]
    c  = dist_corrected[dist_corrected['grupo'] == grupo]
    for period in periods:
        for code, label in [(5, 'Media completa'), (6, 'Técnica')]:
            orig_val = o[(o['periodo_c']==period) & (o['edu_hdmf']==code)]['share']
            corr_val = c[(c['periodo_c']==period) & (c['edu_hdmf']==code)]['share']
            orig_s = float(orig_val.iloc[0]) if len(orig_val) else np.nan
            corr_s = float(corr_val.iloc[0]) if len(corr_val) else np.nan
            summary_rows.append({'grupo': grupo, 'periodo': period,
                                  'categoria': label, 'antes': orig_s, 'despues': corr_s,
                                  'cambio': corr_s - orig_s if pd.notna(orig_s) and pd.notna(corr_s) else np.nan})

summary = pd.DataFrame(summary_rows)
for grupo in GROUP_ORDER:
    sub = summary[summary['grupo'] == grupo].copy()
    sub['label'] = sub['categoria'] + ' | ' + sub['periodo']
    tbl = sub[['periodo','categoria','antes','despues','cambio']].sort_values(['categoria','periodo'])
    print(f"\n{grupo}:")
    for _, r in tbl.iterrows():
        antes  = f"{r['antes']:+.2%}"  if pd.notna(r['antes'])  else 'n/a'
        despues= f"{r['despues']:+.2%}" if pd.notna(r['despues']) else 'n/a'
        cambio = f"{r['cambio']:+.2%}"  if pd.notna(r['cambio'])  else 'n/a'
        print(f"  {r['periodo']:10s}  {r['categoria']:<22s}  antes={antes:>8s}  despues={despues:>8s}  cambio={cambio:>8s}")

csv_path = os.path.join(OUT_DIR, 'ecu_edu_tecnica_summary.csv')
summary.to_csv(csv_path, index=False)
print(f"\nSaved table: {csv_path}")
plt.show()
