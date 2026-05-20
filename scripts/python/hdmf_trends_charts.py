#!/usr/bin/env python3
"""
hdmf_trends_charts.py — Time-series labor market charts by country.

Produces one PNG per labor indicator (employment, unemployment, inactivity,
LFP rate, formality) plus one Excel workbook with all results including CIs.

Changes vs. 2026-04-10:
  - English throughout
  - "Other countries" excluded from charts (included in Excel)
  - 95% CI shaded bands on every chart
  - Fixed y-axis: 0–100 % for all indicators except unemployment (0–30 %)
  - Values displayed as percentages
  - Excel export includes mean, CI low, CI high, SE, N for all groups

Usage:
    py hdmf_trends_charts.py --country COL
    py hdmf_trends_charts.py --country COL --periods 2018t3 2019t3 2020t3 2021t3 2022t3 2023t3 2024t3 2025t3
"""

import argparse
import os
import pickle
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from functions import make_weighted_stats_multi

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE_DIR, 'bases armo', 'armo')
CACHE_FILE = os.path.join(ARMO_DIR, '_hdmf_cache.pkl')
DATE_TAG   = '2026-05-01'

# Group labels (raw cache value → display label)
FB_LABELS = {
    'Native':        'Native',
    'Venezuela':     'Venezuelan',
    'Foreign_other': 'Other countries',
}
FB_ORDER     = ['Native', 'Venezuelan', 'Other countries']
CHART_GROUPS = ['Native', 'Venezuelan']   # plotted; Other countries in Excel only

GROUP_COLOR_MAP = {
    'Native':          (0.122, 0.306, 0.475),   # dark blue  #1F4E79
    'Venezuelan':      (0.753, 0.000, 0.000),   # red        #C00000
    'Other countries': (0.435, 0.678, 0.278),   # green      #6FAD47
}
GROUP_MARKER_MAP = {
    'Native':          'o',
    'Venezuelan':      '^',
    'Other countries': 's',
}

# Internal variable name → English display label
LABOR_VAR_LABELS = {
    'emp_ci':      'Employment rate',
    'desemp_ci':   'Unemployment rate',
    'inactivo_ci': 'Inactivity rate',
    'pea_ci':      'Labor force participation rate',
}
FORMALITY_LABEL = 'Formality rate'

# Y-axis upper limits (percentage points)
Y_MAX = {
    'Employment rate':                   100,
    'Unemployment rate':                  30,
    'Inactivity rate':                   100,
    'Labor force participation rate':    100,
    'Formality rate':                    100,
}

CI_ALPHA  = 0.15                                     # CI band transparency
LINE_ALPHA = 0.80                                    # connecting-line transparency
CI_NOTE   = '95% CI — survey-weighted linearization estimator'

# =============================================================================
# UTILITY
# =============================================================================

def compute_stats(df, group_cols, status_cols):
    return make_weighted_stats_multi(
        df=df, group_cols=group_cols, status_cols=status_cols,
        weight_col='factor_ci',
        include_se=True, include_ci=True, include_neff=True,
        include_n_unweighted=True, include_sum_weights=False,
        output_format='long',
    )


def apply_fb_labels(df, col='foreign_born'):
    df = df.copy()
    df[col] = df[col].replace(FB_LABELS)
    df[col] = pd.Categorical(df[col], categories=FB_ORDER, ordered=True)
    return df


def sort_periods(df, col='periodo_c'):
    df = df.copy()
    unique_vals = sorted(df[col].dropna().unique().tolist())
    df[col] = pd.Categorical(df[col], categories=unique_vals, ordered=True)
    return df.sort_values(col)


def save_fig(fig, path):
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)


# =============================================================================
# CHART BUILDER
# =============================================================================

def chart_labor_ci(df_long, variable_name, ylabel, out_dir, country, fname):
    """Time-series chart with 95% CI bands.

    Only CHART_GROUPS (Native, Venezuelan) are plotted.
    Other countries are excluded from the chart but included in Excel export.
    Values are displayed as percentages; y-axis fixed per Y_MAX dict.
    """
    sub = df_long[df_long['variable'] == variable_name].copy()
    sub_plot = sub[sub['foreign_born'].isin(CHART_GROUPS)].copy()
    sub_plot = sort_periods(sub_plot)

    if sub_plot.empty:
        print(f'  [SKIP] {fname} — no data')
        return

    y_max = Y_MAX.get(variable_name, 100)

    # Convert proportions → percentages
    for col in ['mean', 'ci_lo', 'ci_hi']:
        if col in sub_plot.columns:
            sub_plot[col] = sub_plot[col] * 100

    # Clip CI to plausible range
    sub_plot['ci_lo'] = sub_plot['ci_lo'].clip(lower=0.0)
    sub_plot['ci_hi'] = sub_plot['ci_hi'].clip(upper=float(y_max))

    periods = [str(p) for p in sub_plot['periodo_c'].cat.categories]
    x_idx   = {p: i for i, p in enumerate(periods)}

    fig, ax = plt.subplots(figsize=(12, 6))

    for grp in CHART_GROUPS:
        grp_data = sub_plot[sub_plot['foreign_born'] == grp]
        if grp_data.empty:
            continue
        g     = grp_data.sort_values('periodo_c')
        xp    = [x_idx[str(p)] for p in g['periodo_c']]
        color = GROUP_COLOR_MAP[grp]
        mkr   = GROUP_MARKER_MAP[grp]

        # 95% CI shaded band
        if 'ci_lo' in g.columns and 'ci_hi' in g.columns:
            ax.fill_between(xp, g['ci_lo'], g['ci_hi'],
                            color=color, alpha=CI_ALPHA, zorder=1)

        # Connecting line
        ax.plot(xp, g['mean'], color=color, linewidth=1.8,
                alpha=LINE_ALPHA, zorder=2)

        # Points
        ax.scatter(xp, g['mean'], color=color, s=200, zorder=4,
                   marker=mkr, edgecolors='white', linewidths=1.0, label=grp)

        # Value labels (above each point)
        label_offset = y_max * 0.018
        for xi, yi in zip(xp, g['mean']):
            if pd.notna(yi):
                ax.text(xi, yi + label_offset, f'{yi:.1f}',
                        ha='center', va='bottom', fontsize=9,
                        color=color, fontweight='semibold')

    # Axes
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, rotation=0, ha='center', fontsize=11)
    ax.set_ylabel(f'{ylabel} (%)', fontsize=13, labelpad=10)
    ax.set_ylim(0, y_max)
    ax.tick_params(axis='y', labelsize=11)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, color='lightgrey')
    ax.xaxis.grid(True, linestyle='--', alpha=0.4, color='lightgrey')
    ax.set_axisbelow(True)
    ax.set_title(f'{ylabel} — {country}', fontsize=15, pad=14, fontweight='bold')

    # CI note (bottom-left, small grey)
    ax.text(0.01, 0.01, CI_NOTE, transform=ax.transAxes,
            fontsize=8, color='#888888', va='bottom')

    sns.despine(ax=ax)

    handles, labels_ = ax.get_legend_handles_labels()
    fig.legend(handles, labels_, loc='lower center', bbox_to_anchor=(0.5, 0.0),
               ncol=2, frameon=False, fontsize=12)
    fig.tight_layout(rect=[0, 0.08, 1, 1])

    save_fig(fig, os.path.join(out_dir, fname))
    print(f'  Saved: {fname}  [y: 0–{y_max}%]')


# =============================================================================
# EXCEL EXPORT
# =============================================================================

def export_labor_excel(labor_long, formality_long, out_dir, country):
    """Export all labor indicators — including Other countries — with CIs.

    One wide sheet per indicator (rows = periods, columns = group × stat).
    One summary long-format sheet with all indicators stacked.
    """
    frames = []

    for label in LABOR_VAR_LABELS.values():
        sub = labor_long[labor_long['variable'] == label].copy()
        sub['indicator'] = label
        frames.append(sub)

    if formality_long is not None and not formality_long.empty:
        sub = formality_long[formality_long['variable'] == 'formal_ci'].copy()
        sub['indicator'] = FORMALITY_LABEL
        frames.append(sub)

    combined = pd.concat(frames, ignore_index=True)

    # Convert to percentages
    pct_cols = ['mean', 'ci_lo', 'ci_hi', 'se']
    for col in pct_cols:
        if col in combined.columns:
            combined[col] = (combined[col] * 100).round(2)
    if 'n_eff' in combined.columns:
        combined['n_eff'] = combined['n_eff'].round(1)

    excel_path = os.path.join(out_dir, f'labor_indicators_ci_{country}.xlsx')

    stat_display = {
        'mean':         'Mean (%)',
        'ci_lo':        'CI low (%)',
        'ci_hi':        'CI high (%)',
        'se':           'SE (%)',
        'n_unweighted': 'N (unweighted)',
    }
    stat_order = [s for s in stat_display if s in combined.columns]

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:

        # ── Wide sheet per indicator ──────────────────────────────────────────
        for ind_label in list(LABOR_VAR_LABELS.values()) + [FORMALITY_LABEL]:
            sub = combined[combined['indicator'] == ind_label].copy()
            if sub.empty:
                continue
            sub = sort_periods(sub)

            rows = []
            for period in [str(p) for p in sub['periodo_c'].cat.categories]:
                row = {'Period': period}
                for grp in FB_ORDER:
                    g = sub[(sub['periodo_c'].astype(str) == period) &
                            (sub['foreign_born'] == grp)]
                    for sc in stat_order:
                        col_name = f'{grp} — {stat_display[sc]}'
                        row[col_name] = g[sc].values[0] if not g.empty else np.nan
                rows.append(row)

            df_wide = pd.DataFrame(rows)
            sheet   = ind_label[:31]
            df_wide.to_excel(writer, sheet_name=sheet, index=False)

        # ── Summary long-format sheet ─────────────────────────────────────────
        keep = ['indicator', 'periodo_c', 'foreign_born'] + stat_order + \
               [c for c in ['n_eff'] if c in combined.columns]
        long_df = combined[[c for c in keep if c in combined.columns]].copy()
        long_df = long_df.sort_values(['indicator', 'foreign_born', 'periodo_c'])
        long_df = long_df.rename(columns={
            'periodo_c':    'Period',
            'foreign_born': 'Group',
            'mean':         'Mean (%)',
            'ci_lo':        'CI low (%)',
            'ci_hi':        'CI high (%)',
            'se':           'SE (%)',
            'n_unweighted': 'N (unweighted)',
            'n_eff':        'N effective (Kish)',
        })
        long_df.to_excel(writer, sheet_name='All indicators (long)', index=False)

    print(f'  Excel saved: {excel_path}')


# =============================================================================
# MAIN
# =============================================================================

def main():
    t_start = time.time()

    parser = argparse.ArgumentParser(description='HDMF labor trend charts with CI')
    parser.add_argument('--country', required=True, metavar='ISO3')
    parser.add_argument('--periods', nargs='+', default=None, metavar='PERIOD')
    parser.add_argument('--cache', default=CACHE_FILE, metavar='PATH')
    args = parser.parse_args()

    country = args.country.upper()

    # ── Load cache ─────────────────────────────────────────────────────────────
    if not os.path.exists(args.cache):
        print(f'Cache not found: {args.cache}\nRun hdmf_build.py first.')
        return

    print(f'Loading cache: {args.cache}')
    with open(args.cache, 'rb') as fh:
        cache = pickle.load(fh)
    data = cache['data']

    if 'periodo_c' not in data.columns:
        print('[ERROR] Cache has no periodo_c column. Rebuild with hdmf_build.py.')
        return

    data = data[data['pais_c'] == country].copy()
    if data.empty:
        print(f'No data for country: {country}')
        return

    if args.periods:
        data = data[data['periodo_c'].isin([p.lower() for p in args.periods])]
    if data.empty:
        print('No data after period filter.')
        return

    periods = sorted(data['periodo_c'].unique())
    print(f'Country : {country}')
    print(f'Periods : {periods}')
    print(f'Rows    : {len(data):,}')

    # ── Output folder ──────────────────────────────────────────────────────────
    out_dir = os.path.join(BASE_DIR, 'out', 'trends', DATE_TAG, country)
    os.makedirs(out_dir, exist_ok=True)
    print(f'Output  : {out_dir}')

    wap = data[data['edad_ci'].between(16, 64)].copy()
    emp = data[data['condocup_ci'] == 1].copy()

    # =========================================================================
    # 1 — LABOR MARKET (WAP 16–64)
    # =========================================================================
    print('\n[1] Labor market...')
    labor = compute_stats(
        wap, group_cols=['periodo_c', 'foreign_born'],
        status_cols=['emp_ci', 'desemp_ci', 'inactivo_ci', 'pea_ci'],
    )
    labor = apply_fb_labels(labor)
    labor['variable'] = labor['variable'].replace(LABOR_VAR_LABELS)

    chart_labor_ci(labor, 'Employment rate',
                   'Employment rate (16–64)',
                   out_dir, country, 'labor_employment_trend.png')

    chart_labor_ci(labor, 'Unemployment rate',
                   'Unemployment rate (16–64)',
                   out_dir, country, 'labor_unemployment_trend.png')

    chart_labor_ci(labor, 'Inactivity rate',
                   'Inactivity rate (16–64)',
                   out_dir, country, 'labor_inactivity_trend.png')

    chart_labor_ci(labor, 'Labor force participation rate',
                   'Labor force participation rate (16–64)',
                   out_dir, country, 'labor_pea_trend.png')

    # =========================================================================
    # 2 — FORMALITY (employed pop.)
    # =========================================================================
    print('\n[2] Formality...')
    formality = compute_stats(
        emp, group_cols=['periodo_c', 'foreign_born'], status_cols=['formal_ci'],
    )
    formality = apply_fb_labels(formality)

    chart_labor_ci(formality, 'formal_ci',
                   'Formality rate',
                   out_dir, country, 'formality_trend.png')

    # =========================================================================
    # 3 — EXCEL EXPORT
    # =========================================================================
    print('\n[3] Excel export...')
    export_labor_excel(labor, formality, out_dir, country)

    # ── Summary ────────────────────────────────────────────────────────────────
    n_charts = sum(
        len([f for f in files if f.endswith('.png')])
        for _, _, files in os.walk(out_dir)
    )
    elapsed = time.time() - t_start
    print(f'\nDone. {n_charts} charts | {elapsed:.0f}s | {out_dir}')


if __name__ == '__main__':
    main()
