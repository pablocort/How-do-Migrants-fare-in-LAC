#!/usr/bin/env python3
"""
hdmf_edu_crosscountry.py — Cross-country education distribution chart.

Compares the education distribution of Natives vs. Venezuelans across the 4
LAC countries (COL, CHL, ECU, PER) using each country's most recent period.
Uses 3 aggregate categories built from the 10-category edu_hdmf variable:

    Primary or less   — edu_hdmf 1-3  (no schooling, primary incomplete/complete)
    High school       — edu_hdmf 4-6  (lower secondary incomplete/complete, upper secondary)
    Higher education  — edu_hdmf 7-10 (technical/vocational, university incomplete/complete, postgraduate)

Chart layout: 2 stacked-bar panels side by side (left = Natives, right = Venezuelans).
X-axis: 4 countries labelled with their most recent period.
Y-axis: share (%).

Colors use the Wong (2011) colorblind-safe palette.

Output folder: out/trends/{DATE_TAG}/
  - education_distribution.png    (2-panel stacked bar chart)
  - education_distribution.xlsx   (full data: all groups + 3-cat + 10-cat)

Usage:
    py hdmf_edu_crosscountry.py
"""

import os
import pickle
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE_DIR, 'bases armo', 'armo')
CACHE_FILE = os.path.join(ARMO_DIR, '_hdmf_cache.pkl')
DATE_TAG   = '2026-04-28'

LAC4 = ['COL', 'CHL', 'ECU', 'PER']

COUNTRY_NAMES = {
    'COL': 'Colombia',
    'CHL': 'Chile',
    'ECU': 'Ecuador',
    'PER': 'Peru',
}

# 3-category mapping from 10-category edu_hdmf
# 1 = No schooling / less than primary
# 2 = Primary incomplete
# 3 = Primary complete
# 4 = Lower secondary incomplete
# 5 = Lower secondary complete
# 6 = Upper secondary complete
# 7 = Technical / vocational (post-secondary)
# 8 = University incomplete
# 9 = University complete
# 10 = Postgraduate (master's, doctorate)
EDU_3CAT_MAP = {
    1:  'Primary or less',
    2:  'Primary or less',
    3:  'Primary or less',
    4:  'High school',
    5:  'High school',
    6:  'High school',
    7:  'Higher education',
    8:  'Higher education',
    9:  'Higher education',
    10: 'Higher education',
}
EDU_3CAT_ORDER = ['Primary or less', 'High school', 'Higher education']

# Wong (2011) colorblind-safe palette
EDU_COLORS = {
    'Primary or less':  '#E69F00',   # amber
    'High school':      '#56B4E9',   # sky blue
    'Higher education': '#0072B2',   # dark blue
}

# Group labels: raw cache value → display label
FB_LABELS_RAW = {
    'Native':        'Native',
    'Venezuela':     'Venezuelan',
    'Foreign_other': 'Other countries',
}
FB_ORDER     = ['Native', 'Venezuelan', 'Other countries']
CHART_GROUPS = ['Native', 'Venezuelan']   # plotted; Other countries in Excel only

CHART_GROUP_TITLES = {
    'Native':    'Natives',
    'Venezuelan':'Venezuelans',
}

# =============================================================================
# UTILITIES
# =============================================================================

def apply_fb_labels(df, col='foreign_born'):
    df = df.copy()
    df[col] = df[col].replace(FB_LABELS_RAW)
    df[col] = pd.Categorical(df[col], categories=FB_ORDER, ordered=True)
    return df


def weighted_edu_shares_3cat(df):
    """Weighted share of each 3-category education level by country × group."""
    rows = []
    for (country, grp), g in df.groupby(['pais_c', 'foreign_born'], dropna=False):
        if pd.isna(grp):
            continue
        w = pd.to_numeric(g['factor_ci'], errors='coerce').fillna(0.0)
        total_w = 0.0
        cat_w   = {}
        for cat in EDU_3CAT_ORDER:
            mask       = g['edu_3cat'] == cat
            cw         = float(w[mask].sum())
            cat_w[cat] = cw
            total_w   += cw
        n_valid = int(g['edu_3cat'].notna().sum())
        for cat in EDU_3CAT_ORDER:
            rows.append({
                'country':      country,
                'group':        str(grp),
                'edu_3cat':     cat,
                'share':        cat_w[cat] / total_w if total_w > 0 else np.nan,
                'n_weighted':   cat_w[cat],
                'n_unweighted': n_valid,
            })
    return pd.DataFrame(rows)


def weighted_edu_shares_10cat(df):
    """Weighted share of each of the 10 edu_hdmf categories by country × group.
    Used for the full-detail Excel sheet."""
    rows = []
    codes = list(range(1, 11))
    edu_label = {
        1:  'No schooling / less than primary',
        2:  'Primary incomplete',
        3:  'Primary complete',
        4:  'Lower secondary incomplete',
        5:  'Lower secondary complete',
        6:  'Upper secondary complete',
        7:  'Technical / vocational',
        8:  'University incomplete',
        9:  'University complete',
        10: 'Postgraduate',
    }
    for (country, grp), g in df.groupby(['pais_c', 'foreign_born'], dropna=False):
        if pd.isna(grp):
            continue
        edu_num = pd.to_numeric(g['edu_hdmf'], errors='coerce')
        w       = pd.to_numeric(g['factor_ci'], errors='coerce').fillna(0.0)
        total_w = 0.0
        cat_w   = {}
        for code in codes:
            mask       = edu_num == code
            cw         = float(w[mask].sum())
            cat_w[code] = cw
            total_w    += cw
        n_valid = int(edu_num.notna().sum())
        for code in codes:
            rows.append({
                'country':      country,
                'group':        str(grp),
                'edu_hdmf':     code,
                'edu_label':    edu_label[code],
                'edu_3cat':     EDU_3CAT_MAP[code],
                'share':        cat_w[code] / total_w if total_w > 0 else np.nan,
                'n_weighted':   cat_w[code],
                'n_unweighted': n_valid,
            })
    return pd.DataFrame(rows)


# =============================================================================
# CHART
# =============================================================================

def _fmt_n(n):
    """Format large numbers as compact strings: 1_234_567 → '1.2M', 234_567 → '235K'."""
    if n >= 1_000_000:
        return f'{n / 1_000_000:.1f}M'
    elif n >= 1_000:
        return f'{n / 1_000:.0f}K'
    return str(int(n))


def chart_edu_distribution(shares_3cat, country_period_label, out_path):
    """Two side-by-side stacked bar charts: left = Natives, right = Venezuelans."""

    countries = [c for c in LAC4 if c in shares_3cat['country'].unique()]
    x_labels  = [f'{COUNTRY_NAMES.get(c, c)}\n({country_period_label[c]})' for c in countries]
    x_pos     = np.arange(len(countries))
    bar_width = 0.55

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), sharey=True)
    fig.subplots_adjust(wspace=0.06)

    for ax, grp_raw in zip(axes, CHART_GROUPS):
        ax.set_title(
            CHART_GROUP_TITLES[grp_raw],
            fontsize=14, fontweight='bold', pad=12,
        )

        sub = shares_3cat[shares_3cat['group'] == grp_raw].copy()

        bottoms = np.zeros(len(countries))

        for cat in EDU_3CAT_ORDER:
            heights    = []
            n_weighted = []
            for c in countries:
                row = sub[(sub['country'] == c) & (sub['edu_3cat'] == cat)]
                if len(row) and np.isfinite(row['share'].values[0]):
                    heights.append(float(row['share'].values[0]) * 100)
                    n_weighted.append(float(row['n_weighted'].values[0]))
                else:
                    heights.append(0.0)
                    n_weighted.append(0.0)

            heights_arr = np.array(heights)

            ax.bar(
                x_pos, heights_arr, bar_width,
                bottom=bottoms,
                color=EDU_COLORS[cat],
                label=cat,
                zorder=3,
                edgecolor='white',
                linewidth=0.6,
            )

            # Labels inside each segment: % on top line, weighted count below
            for i, (h, b, nw) in enumerate(zip(heights_arr, bottoms, n_weighted)):
                if h >= 5:
                    # Show % and weighted count on two lines
                    ax.text(
                        x_pos[i], b + h / 2,
                        f'{h:.0f}%\n({_fmt_n(nw)})',
                        ha='center', va='center', fontsize=7.5,
                        color='white', fontweight='bold',
                        linespacing=1.25,
                    )
                elif h >= 3:
                    # Only % fits
                    ax.text(
                        x_pos[i], b + h / 2, f'{h:.0f}%',
                        ha='center', va='center', fontsize=7.5,
                        color='white', fontweight='bold',
                    )

            bottoms = bottoms + heights_arr

        # N label below each bar (unweighted obs for the plotted group)
        for i, c in enumerate(countries):
            row = sub[sub['country'] == c]
            n   = int(row['n_unweighted'].values[0]) if len(row) else 0
            ax.text(
                x_pos[i], -4, f'n={n:,}',
                ha='center', va='top', fontsize=8, color='#555555',
            )

        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, fontsize=11)
        ax.set_ylim(-8, 105)
        ax.yaxis.grid(True, linestyle='--', alpha=0.35, color='lightgrey')
        ax.set_axisbelow(True)
        sns.despine(ax=ax, bottom=False)

    axes[0].set_ylabel('Share (%)', fontsize=13, labelpad=10)
    axes[0].tick_params(axis='y', labelsize=11)
    axes[1].tick_params(axis='y', left=False)

    # Legend — show in stack order (bottom first matches visual scan of bars)
    handles, labels_ = axes[0].get_legend_handles_labels()
    fig.legend(
        handles[::-1], labels_[::-1],   # reverse so Higher education is on top
        loc='lower center', bbox_to_anchor=(0.5, 0.01),
        ncol=3, frameon=False, fontsize=12,
        title='Education level', title_fontsize=11,
    )

    fig.suptitle('Educational distribution — most recent available year',
                 fontsize=15, fontweight='bold', y=1.02)

    fig.text(
        0.01, 0.01,
        'Note: survey-weighted shares. Higher education includes technical/vocational, '
        'university (complete and incomplete), and postgraduate. '
        'Only Natives and Venezuelans shown; all groups in Excel export.',
        fontsize=7.5, color='#777777',
    )

    fig.tight_layout(rect=[0, 0.11, 1, 1])
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Chart saved: {out_path}')


# =============================================================================
# EXCEL EXPORT
# =============================================================================

def export_excel(shares_3cat, shares_10cat, out_path):
    """Export education distribution data with full detail.

    Sheets:
        chart_data      — 3-cat × country × ALL groups (wide, % ready for charting)
        3cat_long       — 3-cat long format, all groups
        10cat_long      — 10-cat long format, all groups
    """
    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:

        # Wide chart-data sheet: rows = country × group, cols = 3 edu categories
        pct_3 = shares_3cat.copy()
        pct_3['share_pct'] = (pct_3['share'] * 100).round(2)
        wide = pct_3.pivot_table(
            index=['country', 'group'],
            columns='edu_3cat',
            values='share_pct',
            aggfunc='first',
        )
        wide.columns.name = None
        wide = wide.reindex(columns=EDU_3CAT_ORDER)
        # Add n_unweighted
        n_col = (
            shares_3cat.groupby(['country', 'group'])['n_unweighted']
            .first()
        )
        wide = wide.join(n_col)
        wide.to_excel(writer, sheet_name='chart_data')

        # 3-cat long format
        pct_3 = pct_3.sort_values(['country', 'group', 'edu_3cat'])
        pct_3.to_excel(writer, sheet_name='3cat_long', index=False)

        # 10-cat long format
        pct_10 = shares_10cat.copy()
        pct_10['share_pct'] = (pct_10['share'] * 100).round(2)
        pct_10 = pct_10.sort_values(['country', 'group', 'edu_hdmf'])
        pct_10.to_excel(writer, sheet_name='10cat_long', index=False)

    print(f'  Excel saved: {out_path}')


# =============================================================================
# MAIN
# =============================================================================

def main():
    t0 = time.time()

    if not os.path.exists(CACHE_FILE):
        print(f'Cache not found: {CACHE_FILE}\nRun hdmf_build.py first.')
        return

    print(f'Loading cache: {CACHE_FILE}')
    with open(CACHE_FILE, 'rb') as fh:
        cache = pickle.load(fh)
    data = cache['data']

    if 'periodo_c' not in data.columns:
        print('[ERROR] Cache has no periodo_c column. Rebuild with hdmf_build.py.')
        return

    # Filter to LAC4 and apply group labels
    data = data[data['pais_c'].isin(LAC4)].copy()
    data = apply_fb_labels(data)

    # Most recent period per country (lexicographic sort is correct for YYYY* codes)
    most_recent = (
        data.groupby('pais_c')['periodo_c']
        .apply(lambda s: sorted(s.dropna().unique())[-1])
        .to_dict()
    )
    print('Most recent periods per country:')
    for c, p in most_recent.items():
        print(f'  {c}: {p}')

    # Keep only the most recent period per country
    keep = pd.Series(False, index=data.index)
    for country, period in most_recent.items():
        keep |= (data['pais_c'] == country) & (data['periodo_c'] == period)
    data_recent = data[keep].copy()

    print(f'\nRows after most-recent filter: {len(data_recent):,}')
    counts = (
        data_recent
        .groupby(['pais_c', 'periodo_c', 'foreign_born'], observed=True)
        .size()
        .reset_index(name='n')
    )
    print(counts.to_string(index=False))

    # Create 3-category education variable
    data_recent = data_recent.copy()
    data_recent['edu_3cat'] = (
        pd.to_numeric(data_recent['edu_hdmf'], errors='coerce')
        .map(EDU_3CAT_MAP)
    )
    print(f'\nedu_3cat distribution (unweighted):\n'
          f'{data_recent["edu_3cat"].value_counts(dropna=False)}')

    # Weighted shares
    print('\nComputing weighted shares...')
    shares_3cat  = weighted_edu_shares_3cat(data_recent)
    shares_10cat = weighted_edu_shares_10cat(data_recent)

    # Output folder (same date folder as the per-country labor trend charts)
    out_dir = os.path.join(BASE_DIR, 'out', 'trends', DATE_TAG)
    os.makedirs(out_dir, exist_ok=True)
    print(f'\nOutput folder: {out_dir}')

    # Chart
    chart_path = os.path.join(out_dir, 'education_distribution.png')
    chart_edu_distribution(shares_3cat, most_recent, chart_path)

    # Excel export
    excel_path = os.path.join(out_dir, 'education_distribution.xlsx')
    export_excel(shares_3cat, shares_10cat, excel_path)

    elapsed = time.time() - t0
    print(f'\nDone in {elapsed:.1f}s')


if __name__ == '__main__':
    main()
