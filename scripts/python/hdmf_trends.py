#!/usr/bin/env python3
"""
hdmf_trends.py -- Time-series indicators by country and period.

Loads the HDMF cache built by hdmf_build.py and computes all standard
indicators for every period, allowing cross-wave comparison.

Usage:
    py hdmf_trends.py --country COL
    py hdmf_trends.py --country COL --periods 2018t3 2019t3 2020t3 2021t3 2022t3 2023t3 2024t3 2025t3
    py hdmf_trends.py --country COL --cache col_cache.pkl
"""

import argparse
import os
import pickle

import numpy as np
import pandas as pd

from functions import make_weighted_stats_multi, fix_orthography

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE_DIR, 'bases armo', 'armo')
CACHE_FILE = os.path.join(ARMO_DIR, '_hdmf_cache.pkl')
DATE_TAG   = '2026-04-10'

FB_LABELS = {
    'Native':        'Nativos',
    'Venezuela':     'Migrantes de Venezuela',
    'Foreign_other': 'Migrantes de otros países',
}
FB_ORDER = ['Nativos', 'Migrantes de Venezuela', 'Migrantes de otros países']

LABOR_LABELS = {
    'emp_ci':      'Tasa de empleo',
    'desemp_ci':   'Tasa de desempleo',
    'inactivo_ci': 'Tasa de inactividad',
    'pea_ci':      'Tasa PEA',
}

EDU_BASICA_CATS = [
    'Menos de primaria', 'Primaria incompleta', 'Primaria completa',
    'Media incompleta',  'Media completa',
]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _norm_code(x):
    try:
        xf = float(x)
        return int(xf) if xf.is_integer() else xf
    except Exception:
        return x


def compute_stats(df, group_cols, status_cols, weight_col='factor_ci'):
    return make_weighted_stats_multi(
        df=df, group_cols=group_cols, status_cols=status_cols, weight_col=weight_col,
        include_se=True, include_ci=True, include_neff=True,
        include_n_unweighted=True, include_sum_weights=True, output_format="long",
    )


def wavg(g, value_col, weight_col='factor_ci'):
    v = pd.to_numeric(g[value_col], errors='coerce').to_numpy()
    w = pd.to_numeric(g[weight_col], errors='coerce').to_numpy()
    m = np.isfinite(v) & np.isfinite(w) & (w > 0)
    return np.average(v[m], weights=w[m]) if m.sum() else np.nan


def apply_fb_labels(df, col='foreign_born'):
    df = df.copy()
    df[col] = df[col].replace(FB_LABELS)
    df[col] = pd.Categorical(df[col], categories=FB_ORDER, ordered=True)
    return df


def pivot_trends(df, value_col='mean', index_cols=('foreign_born', 'variable')):
    """Pivot to wide format: rows = groups, columns = periodo_c."""
    return df.pivot_table(
        index=list(index_cols), columns='periodo_c', values=value_col,
    ).sort_index(axis=1)


# =============================================================================
# MAIN
# =============================================================================

def main():
    import time
    t_start = time.time()

    parser = argparse.ArgumentParser(description='HDMF time-series indicators')
    parser.add_argument('--country', required=True, metavar='ISO3',
                        help='Country code (e.g. COL)')
    parser.add_argument('--periods', nargs='+', default=None, metavar='PERIOD',
                        help='Period codes to include (e.g. 2018t3 2019t3). Default: all in cache.')
    parser.add_argument('--cache', default=CACHE_FILE, metavar='PATH',
                        help='Path to _hdmf_cache.pkl')
    args = parser.parse_args()

    country = args.country.upper()

    # ── Load cache ────────────────────────────────────────────────────────────
    if not os.path.exists(args.cache):
        print(f'Cache not found: {args.cache}')
        print('Run hdmf_build.py first.')
        return

    print(f'Loading cache: {args.cache}')
    with open(args.cache, 'rb') as fh:
        cache = pickle.load(fh)
    data               = cache['data']
    value_labels_by_var = cache['value_labels_by_var']

    if 'periodo_c' not in data.columns:
        print('[ERROR] Cache does not have periodo_c column.')
        print('Rebuild the cache with hdmf_build.py (updated version).')
        return

    # ── Filter by country and periods ─────────────────────────────────────────
    data = data[data['pais_c'] == country].copy()
    if data.empty:
        print(f'No data found for country: {country}')
        print(f'Available: {cache["data"]["pais_c"].unique().tolist()}')
        return

    if args.periods:
        periods_filter = [p.lower() for p in args.periods]
        data = data[data['periodo_c'].isin(periods_filter)]
        if data.empty:
            print(f'No data for periods {periods_filter} in {country}.')
            return

    periods = sorted(data['periodo_c'].unique())
    print(f'Country  : {country}')
    print(f'Periods  : {periods}')
    print(f'Rows     : {len(data):,}')

    # ── Output path ───────────────────────────────────────────────────────────
    out_dir = os.path.join(BASE_DIR, 'out', 'indicator_descriptive', DATE_TAG)
    os.makedirs(out_dir, exist_ok=True)
    out_xlsx = os.path.join(out_dir, f'hdmf_trends_{country}.xlsx')

    # ── Analytical subsets ────────────────────────────────────────────────────
    wap     = data[data['edad_ci'].between(16, 64)].copy()
    emp     = data[data['condocup_ci'] == 1].copy()

    # =========================================================================
    # 1 — POPULATION
    # =========================================================================

    pop = (
        data.groupby(['periodo_c', 'foreign_born'])['factor_ci']
        .sum().reset_index(name='population')
    )
    pop_total = pop.groupby('periodo_c')['population'].transform('sum')
    pop['share'] = pop['population'] / pop_total
    pop = apply_fb_labels(pop)
    pop_pivot_n     = pop.pivot_table(index='foreign_born', columns='periodo_c', values='population')
    pop_pivot_share = pop.pivot_table(index='foreign_born', columns='periodo_c', values='share')

    # =========================================================================
    # 2 — LABOR MARKET (WAP 16-64)
    # =========================================================================

    labor = compute_stats(
        wap, group_cols=['periodo_c', 'foreign_born'],
        status_cols=['emp_ci', 'desemp_ci', 'inactivo_ci', 'pea_ci'],
    )
    labor = apply_fb_labels(labor)
    labor['variable'] = labor['variable'].replace(LABOR_LABELS)

    labor_mean = pivot_trends(labor, value_col='mean')
    labor_se   = pivot_trends(labor, value_col='std')
    labor_n    = pivot_trends(labor, value_col='n_unweighted')

    # =========================================================================
    # 3 — WAGES AND HOURS (WAP 16-64, weighted averages)
    # =========================================================================

    wages = (
        wap.groupby(['periodo_c', 'foreign_born'])
        .apply(lambda g: pd.Series({
            'ingreso_total_wavg': wavg(g, 'ytot_ci'),
            'horas_totales_wavg': wavg(g, 'horastot_ci'),
        }))
        .reset_index()
    )
    wages = apply_fb_labels(wages)
    wages_pivot = wages.pivot_table(
        index='foreign_born', columns='periodo_c', values=['ingreso_total_wavg', 'horas_totales_wavg'],
    )

    # =========================================================================
    # 4 — FORMALITY (employed population)
    # =========================================================================

    formality = compute_stats(
        emp, group_cols=['periodo_c', 'foreign_born'], status_cols=['formal_ci'],
    )
    formality = apply_fb_labels(formality)
    formality['variable'] = formality['variable'].replace({np.nan: 'Missing'})

    formality_mean = pivot_trends(formality, value_col='mean')
    formality_n    = pivot_trends(formality, value_col='n_unweighted')

    # =========================================================================
    # 5 — EDUCATION DISTRIBUTION
    # =========================================================================

    edu_label_map = {
        _norm_code(k): v
        for k, v in value_labels_by_var.get("edu_hdmf", {}).items()
    }
    edu_codes   = pd.to_numeric(data['edu_hdmf'], errors='coerce')
    edu_dummies = pd.get_dummies(edu_codes, dtype=int, dummy_na=True)
    edu_dummies = edu_dummies.rename(columns={
        code: edu_label_map.get(_norm_code(code), f'code {_norm_code(code)}')
        for code in edu_dummies.columns
    })
    edu_dummies.columns = edu_dummies.columns.map(fix_orthography)

    data_edu = pd.concat(
        [data[['periodo_c', 'foreign_born', 'factor_ci']], edu_dummies], axis=1
    )

    edu_dist = compute_stats(
        data_edu, group_cols=['periodo_c', 'foreign_born'],
        status_cols=edu_dummies.columns.tolist(),
    )
    edu_dist = apply_fb_labels(edu_dist)
    edu_dist['variable'] = edu_dist['variable'].replace({np.nan: 'Missing'})

    edu_mean = pivot_trends(edu_dist, value_col='mean')
    edu_n    = pivot_trends(edu_dist, value_col='n_unweighted')

    # =========================================================================
    # 6 — YEARS OF SCHOOLING (weighted average)
    # =========================================================================

    edu_years = (
        data.groupby(['periodo_c', 'foreign_born'])
        .apply(lambda g: pd.Series({'anios_edu_wavg': wavg(g, 'aedu_ci')}))
        .reset_index()
    )
    edu_years = apply_fb_labels(edu_years)
    edu_years_pivot = edu_years.pivot_table(
        index='foreign_born', columns='periodo_c', values='anios_edu_wavg',
    )

    # =========================================================================
    # 7 — EXPORT TO EXCEL
    # =========================================================================

    print(f'Exporting -> {out_xlsx}')
    with pd.ExcelWriter(out_xlsx) as writer:
        pop_pivot_n.to_excel(writer,     sheet_name='population_n')
        pop_pivot_share.to_excel(writer, sheet_name='population_share')
        labor_mean.to_excel(writer,      sheet_name='labor_rate')
        labor_se.to_excel(writer,        sheet_name='labor_se')
        labor_n.to_excel(writer,         sheet_name='labor_n')
        wages_pivot.to_excel(writer,     sheet_name='wages_hours')
        formality_mean.to_excel(writer,  sheet_name='formality_rate')
        formality_n.to_excel(writer,     sheet_name='formality_n')
        edu_mean.to_excel(writer,        sheet_name='education_dist')
        edu_n.to_excel(writer,           sheet_name='education_n')
        edu_years_pivot.to_excel(writer, sheet_name='education_years')

    elapsed = time.time() - t_start
    print(f'Done. Output: {out_xlsx}')
    print(f'Total time: {elapsed/60:.1f} min ({elapsed:.0f} s)')


if __name__ == '__main__':
    main()
