"""
export_intermediate_data.py
Exports two datasets to bases armo/intermediate_data/[DATE_TAG]/:

  1. individual_data_[DATE_TAG].csv / .dta
     Full country-year analytical dataset at individual level (from cache).

  2. hdmf_indicators_[DATE_TAG].csv / .dta
     General indicators panel (from out/indicator_descriptive/[DATE_TAG]/).

Usage:
    py export_intermediate_data.py
    py export_intermediate_data.py --date 2026-05-11
"""

import argparse
import os
import pickle
import time

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE, "bases armo", "armo")
CACHE_FILE = os.path.join(ARMO_DIR, "_hdmf_cache.pkl")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-05-11",
                        help="Date tag for subfolder and filenames (default: 2026-05-11)")
    args = parser.parse_args()
    date_tag = args.date

    out_dir      = os.path.join(BASE, "bases armo", "intermediate_data", date_tag)
    indicators_src_dir = os.path.join(BASE, "out", "indicator_descriptive", date_tag)
    os.makedirs(out_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # 1. Individual-level data
    # -----------------------------------------------------------------------
    print(f"Loading cache: {CACHE_FILE}")
    t0 = time.time()
    with open(CACHE_FILE, "rb") as fh:
        _cache = pickle.load(fh)
    data = _cache["data"]
    print(f"  Loaded {len(data):,} rows, {data['pais_c'].nunique()} countries  "
          f"({time.time()-t0:.0f}s)")

    # Convert age_group (Categorical) to string to avoid Stata export issues
    if "age_group" in data.columns:
        data = data.copy()
        data["age_group"] = data["age_group"].astype(str)

    ind_csv = os.path.join(out_dir, f"individual_data_{date_tag}.csv")
    ind_dta = os.path.join(out_dir, f"individual_data_{date_tag}.dta")

    print(f"Writing CSV ({len(data):,} rows) -> {ind_csv}")
    t1 = time.time()
    data.to_csv(ind_csv, index=False)
    print(f"  Done ({time.time()-t1:.0f}s)  {os.path.getsize(ind_csv)/1e9:.2f} GB")

    print(f"Writing DTA -> {ind_dta}")
    t2 = time.time()
    # Convert object columns with mixed types to string before Stata export
    dta_data = data.copy()
    for col in dta_data.select_dtypes(include="object").columns:
        dta_data[col] = dta_data[col].fillna("").astype(str)
    dta_data.to_stata(ind_dta, write_index=False, version=118)
    print(f"  Done ({time.time()-t2:.0f}s)  {os.path.getsize(ind_dta)/1e9:.2f} GB")

    # -----------------------------------------------------------------------
    # 2. HDMF indicators panel
    # -----------------------------------------------------------------------
    src_csv = os.path.join(indicators_src_dir, "hdmf_general_indicators.csv")
    src_dta = os.path.join(indicators_src_dir, "hdmf_general_indicators.dta")

    ind_out_csv = os.path.join(out_dir, f"hdmf_indicators_{date_tag}.csv")
    ind_out_dta = os.path.join(out_dir, f"hdmf_indicators_{date_tag}.dta")

    if os.path.exists(src_csv):
        import shutil
        shutil.copy2(src_csv, ind_out_csv)
        print(f"Copied indicators CSV -> {ind_out_csv}")
    else:
        print(f"[WARN] Source CSV not found: {src_csv}")

    if os.path.exists(src_dta):
        import shutil
        shutil.copy2(src_dta, ind_out_dta)
        print(f"Copied indicators DTA -> {ind_out_dta}")
    else:
        print(f"[WARN] Source DTA not found: {src_dta}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print()
    print("=== Exported files ===")
    for f in sorted(os.listdir(out_dir)):
        fpath = os.path.join(out_dir, f)
        size_mb = os.path.getsize(fpath) / 1e6
        print(f"  {f}  ({size_mb:,.0f} MB)")

    total = time.time() - t0
    print(f"\nTotal time: {total/60:.1f} min ({total:.0f}s)")


if __name__ == "__main__":
    main()
