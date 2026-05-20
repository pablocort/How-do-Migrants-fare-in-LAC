#!/usr/bin/env python3
"""
hdmf_build.py -- Build and cache the HDMF analytical dataset.

Reads *_BID.dta files from country subfolders and saves a prepared
pickle cache for use by hdmf_2.py (standard indicators) and
hdmf_trends.py (time-series indicators).

Usage:
    py hdmf_build.py                                        # all available files
    py hdmf_build.py --countries COL                        # all COL waves
    py hdmf_build.py --countries COL --periods 2018t3 2019t3 2020t3
    py hdmf_build.py --countries COL CHL ECU PER USA        # multiple countries
    py hdmf_build.py --output my_cache.pkl                  # custom output path
"""

import argparse
import os
import pickle
import re
import unicodedata

import numpy as np
import pandas as pd
from pandas.io.stata import StataReader

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE_DIR, 'bases armo', 'armo')
CACHE_FILE = os.path.join(ARMO_DIR, '_hdmf_cache.pkl')

COLS_TO_KEEP = list(dict.fromkeys([
    'pais_c', 'mig_pais_ci', 'migrante_ci', 'sexo_ci', 'factor_ci', 'edad_ci', 'idh_ch',
    'relacion_ci', 'jefe_ci',
    'emp_ci', 'desemp_ci', 'pea_ci', 'condocup_ci',
    'ytot_ci', 'ylm_ci', 'horastot_ci', 'horaspri_ci',
    'formal_ci', 'tipocontrato_ci', 'parcial_ci', 'aedu_ci', 'edu_hdmf',
]))

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _fix_mojibake(s):
    try:
        return s.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def normalize_country_name(x):
    if pd.isna(x):
        return x
    s = _fix_mojibake(str(x).strip())
    s = re.sub(r"\s+", " ", unicodedata.normalize("NFC", s))
    # Normalize to title case so ALL-CAPS (2017/2020) and title-case (2022/2024) match
    s = s.title()
    aliases = {
        "Estados Unidos":         "Estados Unidos De America",
        "Eeuu":                   "Estados Unidos De America",
        "Usa":                    "Estados Unidos De America",
        "U.S.A.":                 "Estados Unidos De America",
        "Republica Dominicana":   "República Dominicana",
        "República Dominicana":   "República Dominicana",
        "Haiti":                  "Haití",
        "Peru":                   "Perú",
        "Mexico":                 "México",
        "Brasil":                 "Brasil",
        # IPUMS ACS bpld decode label for Venezuela
        "Venezuela, N.S.":        "Venezuela",
        "Venezuela, N. S.":       "Venezuela",
    }
    return aliases.get(s, s)


def extract_periodo(filename):
    """
    Extract period code from filename.
    COL_2024t3_BID.dta  -> '2024t3'
    ECU_2025m12_BID.dta -> '2025m12'
    CHL_2024a_BID.dta   -> '2024a'
    USA_2024_BID.dta    -> '2024a'
    """
    name = os.path.basename(filename)
    # Quarterly/monthly/annual with explicit letter: 2024t3, 2025m12, 2024a
    m = re.search(r'_(\d{4}(?:t\d|m\d{1,2}|a))_BID\.dta$', name, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    # Year only (no letter suffix) -> treat as annual
    m = re.search(r'_(\d{4})_BID\.dta$', name, re.IGNORECASE)
    if m:
        return m.group(1) + 'a'
    return 'unknown'


def discover_files(armo_dir):
    """
    Collect all *_BID.dta paths. Subfolder version wins over root duplicate.
    """
    file_paths = {}
    # Pass 1: root-level files
    for entry in os.scandir(armo_dir):
        if entry.is_file() and entry.name.lower().endswith('_bid.dta'):
            file_paths[entry.name] = entry.path
    # Pass 2: subfolders overwrite root duplicates (canonical location)
    for entry in os.scandir(armo_dir):
        if entry.is_dir() and not entry.name.startswith('_'):
            for f in os.scandir(entry.path):
                if f.name.lower().endswith('_bid.dta') and f.is_file():
                    file_paths[f.name] = f.path
    return file_paths


# =============================================================================
# MAIN
# =============================================================================

def main():
    import time
    t_start = time.time()

    parser = argparse.ArgumentParser(description='Build HDMF cache from _BID.dta files')
    parser.add_argument('--countries', nargs='+', default=None, metavar='ISO3',
                        help='Country codes to include (e.g. COL CHL). Default: all.')
    parser.add_argument('--periods', nargs='+', default=None, metavar='PERIOD',
                        help='Period codes to include (e.g. 2018t3 2019t3). Default: all.')
    parser.add_argument('--output', default=CACHE_FILE, metavar='PATH',
                        help='Output cache pickle path.')
    args = parser.parse_args()

    # ── Discover all available files ──────────────────────────────────────────
    all_files = discover_files(ARMO_DIR)

    # ── Apply country / period filters ────────────────────────────────────────
    countries_filter = {c.upper() for c in args.countries} if args.countries else None
    periods_filter   = {p.lower() for p in args.periods}   if args.periods   else None

    file_paths = {}
    for fname, fpath in all_files.items():
        country = fname.split('_')[0].upper()
        period  = extract_periodo(fname)
        if countries_filter and country not in countries_filter:
            continue
        if periods_filter and period not in periods_filter:
            continue
        file_paths[fname] = fpath

    if not file_paths:
        print('No matching files found. Check --countries and --periods.')
        print(f'Available files: {sorted(all_files)}')
        return

    print(f'Files to load ({len(file_paths)}):')
    for f in sorted(file_paths):
        print(f'  {f}  [{extract_periodo(f)}]')

    # ── Load each file ────────────────────────────────────────────────────────
    dfs = []
    value_labels_by_var = {}

    for fname in sorted(file_paths):
        fpath   = file_paths[fname]
        periodo = extract_periodo(fname)
        print(f'  Reading {fname} ...')

        with StataReader(fpath) as reader:
            val_lbl = reader.value_labels() or {}
            for var, labels in val_lbl.items():
                if isinstance(labels, dict):
                    value_labels_by_var.setdefault(var, {}).update(labels)
            df = reader.read(convert_categoricals=False)

        df.columns = df.columns.str.lower()

        missing  = [c for c in COLS_TO_KEEP if c not in df.columns]
        existing = [c for c in COLS_TO_KEEP if c in df.columns]
        if missing:
            print(f'  [WARN] {fname} missing: {missing}')

        df = df[existing].copy()
        for c in missing:
            df[c] = np.nan

        df['periodo_c'] = periodo
        dfs.append(df[COLS_TO_KEEP + ['periodo_c']])

    # ── Concatenate & prepare ─────────────────────────────────────────────────
    data = pd.concat(dfs, ignore_index=True)
    data = data[data['pais_c'] != ''].dropna(subset=['migrante_ci'])

    data['mig_pais_ci']     = data['mig_pais_ci'].apply(normalize_country_name)
    data['inactivo_ci']     = (data['condocup_ci'] == 3).astype(int)
    data['migrante_ci']     = data['migrante_ci'].replace({1: 'Migrant', 0: 'Native'})

    # Derive parcial_ci from horaspri_ci where missing (handles ESP 2018–2024 and any
    # wave where parcial_ci was not yet defined in the Stata do file)
    mask = (
        data['parcial_ci'].isna()
        & data['horaspri_ci'].notna()
        & (data['emp_ci'] == 1)
    )
    data.loc[mask, 'parcial_ci'] = (data.loc[mask, 'horaspri_ci'] < 35).astype(float)
    data['tipocontrato_ci'] = data['tipocontrato_ci'].replace(
        {'Sin_contrato/verbal': 'Sin contrato/verbal'}
    )
    data['foreign_born'] = data['mig_pais_ci'].apply(
        lambda x: 'Native' if x == '' else ('Venezuela' if x == 'Venezuela' else 'Foreign_other')
    )
    data['age_group'] = pd.cut(
        data['edad_ci'], bins=[0, 18, 35, 64, np.inf],
        labels=['0-17', '18-34', '35-64', '65+'], right=False,
    )

    print(f'\nCountries : {data.pais_c.value_counts().to_dict()}')
    print(f'Periods   : {sorted(data.periodo_c.unique())}')
    print(f'Migration : {data.migrante_ci.value_counts().to_dict()}')
    print(f'Total rows: {len(data):,}')

    # ── Save cache ────────────────────────────────────────────────────────────
    out_path = args.output
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print(f'\nSaving cache -> {out_path}')
    with open(out_path, 'wb') as fh:
        pickle.dump(
            {'data': data, 'value_labels_by_var': value_labels_by_var},
            fh, protocol=pickle.HIGHEST_PROTOCOL,
        )
    elapsed = time.time() - t_start
    print(f'Cache saved. Total time: {elapsed/60:.1f} min ({elapsed:.0f} s)')


if __name__ == '__main__':
    main()
