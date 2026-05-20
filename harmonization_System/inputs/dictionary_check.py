"""
HDMF Dictionary Check — Python version
=======================================
Pre-harmonization tool for comparing variable existence, types, and
category codes across multiple waves of the same survey.

Usage:
    python dictionary_check.py --country COL --waves 2018t3 2019t3 2020t3 2021t3 2022t3 2023t3 2024t3 2025t3

Outputs:
    harmonization_System/inputs/[ISO3]_dictionary_check_[FIRST]_[LAST].md
    harmonization_System/inputs/[ISO3]_dictionary_check_[FIRST]_[LAST].xlsx  (optional)

Advantages over Stata approach:
    - No Stata license required for the inspection phase
    - `capture` does not suppress output (Stata issue)
    - Produces clean comparison tables across all waves simultaneously
    - Can grep reference do-files programmatically for alternative constructions
    - Runs in seconds vs minutes for large .dta files
"""

import pandas as pd
import os
import sys
import re
import argparse
from pathlib import Path
from datetime import date

try:
    import pyreadstat
    USE_PYREADSTAT = True
except ImportError:
    USE_PYREADSTAT = False
    # Fall back to pandas.read_stata (slower, fewer metadata)


# ── Project paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT     = PROJECT_ROOT / "bases armo" / "raw"
ALT_DO_ROOT  = RAW_ROOT  # alternative_do_files folder lives inside raw/[ISO3]/
OUTPUT_DIR   = PROJECT_ROOT / "harmonization_System" / "inputs"

# ── HDMF target variables by domain ──────────────────────────────────────────
TARGET_VARS = {
    "IDs & weights": ["idh", "orden", "fex_c18", "fex_c_2011", "fex_c", "fex"],
    "Demographics":  ["p6050", "p6040", "p6020", "p3016"],
    "Employment":    ["oci", "dsi", "fft", "ini",
                      "p6800", "p7045", "p6920", "p6090",
                      "p6460", "p6450", "p6440", "p7450", "p6240"],
    "Education":     ["p3042", "p3042s1", "p3042s2", "p3043",
                      "p6210", "p6210s1", "p6220"],
    "Migration":     ["p3373", "p3373s3", "p3382",
                      "p6074", "p756", "p755"],
    "Income":        ["impa", "impaes", "isa", "isaes",
                      "imdi", "imdies", "ie", "iees",
                      "iof1", "iof2", "iof3h", "iof3i", "iof6",
                      "iof1es", "iof2es", "iof3hes", "iof3ies", "iof6es",
                      "p7510s2a1"],
}

ALL_TARGET_VARS = [v for vlist in TARGET_VARS.values() for v in vlist]

# ── Variable categories to tabulate ──────────────────────────────────────────
CATEGORICAL_VARS = ["p6050", "p3042", "p3373", "p3382", "p6920", "p6090",
                    "p6074", "p756", "p755", "p6210"]


def read_dta(path: Path):
    """Read a .dta file; return (df, meta) where meta has variable/value labels."""
    if USE_PYREADSTAT:
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                df, meta = pyreadstat.read_dta(str(path), apply_value_formats=False,
                                               encoding=enc)
                return df, meta
            except (UnicodeDecodeError, Exception):
                continue
        # final fallback: pandas (no labels)
        df = pd.read_stata(str(path), convert_categoricals=False)
        return df, None
    else:
        # pandas fallback — no value labels available
        df = pd.read_stata(str(path), convert_categoricals=False)
        return df, None


def check_wave(dta_path: Path, target_vars: list):
    """Return dict of variable → (exists, dtype, label) for one wave."""
    df, meta = read_dta(dta_path)
    existing = {c.lower(): c for c in df.columns}  # case-insensitive lookup

    results = {}
    for v in target_vars:
        col = existing.get(v.lower())
        if col is None:
            results[v] = {"exists": False, "dtype": None, "label": None}
        else:
            dtype = str(df[col].dtype)
            label = ""
            if meta is not None and col in meta.column_names_to_labels:
                label = meta.column_names_to_labels[col]
            results[v] = {"exists": True, "dtype": dtype, "label": label, "_col": col}
    return df, meta, results


def tabulate_categorical(df, col_actual, meta, wave, n=20):
    """Return frequency table for a categorical variable."""
    if col_actual not in df.columns:
        return None
    vc = df[col_actual].value_counts(dropna=False).head(n)
    total = len(df)
    rows = []
    for val, cnt in vc.items():
        label = ""
        if meta is not None:
            vl = getattr(meta, "variable_value_labels", {})
            vlabels = vl.get(col_actual, {})
            label = vlabels.get(val, "")
        rows.append({"value": val, "label": label, "n": cnt, "pct": cnt / total * 100})
    return pd.DataFrame(rows)


def weight_summary(df, weight_vars):
    """Return sum of whichever weight variable exists."""
    for wv in weight_vars:
        col = next((c for c in df.columns if c.lower() == wv.lower()), None)
        if col:
            s = df[col].sum()
            mn = df[col].min()
            mx = df[col].max()
            return wv, s, mn, mx
    return None, None, None, None


def grep_reference_do(iso3: str, variable: str, raw_root: Path):
    """Search alternative do-files for constructions of `variable`."""
    alt_dir = raw_root / iso3.lower() / "alternative_do_files"
    if not alt_dir.exists():
        return []
    hits = []
    pattern = re.compile(rf'\b{re.escape(variable)}\b', re.IGNORECASE)
    for f in sorted(alt_dir.glob("*.do")):
        with open(f, encoding="latin-1", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                if pattern.search(line):
                    hits.append({"file": f.name, "line": i, "text": line.rstrip()})
    return hits


def build_existence_table(wave_results: dict, target_vars: list):
    """Build a DataFrame: rows=variables, cols=waves."""
    rows = []
    for v in target_vars:
        row = {"variable": v}
        for wave, results in wave_results.items():
            info = results.get(v, {})
            if info.get("exists"):
                row[wave] = f"✅ {info['dtype']}"
            else:
                row[wave] = "❌"
        rows.append(row)
    return pd.DataFrame(rows).set_index("variable")


def run_check(iso3: str, waves: list, output_dir: Path, raw_root: Path):
    iso3u = iso3.upper()
    iso3l = iso3.lower()
    raw_dir = raw_root / iso3l

    print(f"\nHDMF Dictionary Check — {iso3u} — waves: {', '.join(waves)}")
    print("=" * 60)

    # ── 1. Load each wave ─────────────────────────────────────────
    wave_results = {}
    wave_dfs     = {}
    wave_metas   = {}

    for wave in waves:
        dta_path = raw_dir / f"{iso3u}_{wave}.dta"
        if not dta_path.exists():
            print(f"  SKIP {wave}: file not found at {dta_path}")
            continue
        print(f"  Reading {dta_path.name} ...", end=" ")
        df, meta, results = check_wave(dta_path, ALL_TARGET_VARS)
        wave_dfs[wave]    = df
        wave_metas[wave]  = meta
        wave_results[wave] = results
        print(f"N={len(df):,}  vars={len(df.columns)}")

    if not wave_results:
        print("No waves loaded. Check paths.")
        return

    # ── 2. Existence table ────────────────────────────────────────
    exist_tbl = build_existence_table(wave_results, ALL_TARGET_VARS)

    # ── 3. Weight summary ─────────────────────────────────────────
    weight_candidates = ["fex_c18", "fex_c_2011", "fex_c", "fex"]
    weight_rows = []
    for wave, df in wave_dfs.items():
        wv, s, mn, mx = weight_summary(df, weight_candidates)
        weight_rows.append({
            "wave": wave, "N": len(df),
            "weight_var": wv or "NOT FOUND",
            "sum": f"{s:,.0f}" if s is not None else "—",
            "min": f"{mn:.3f}" if mn is not None else "—",
            "max": f"{mx:.3f}" if mx is not None else "—",
        })
    weight_df = pd.DataFrame(weight_rows).set_index("wave")

    # ── 4. Categorical checks ─────────────────────────────────────
    cat_tables = {}
    for v in CATEGORICAL_VARS:
        cat_tables[v] = {}
        for wave, df in wave_dfs.items():
            meta = wave_metas[wave]
            col  = next((c for c in df.columns if c.lower() == v.lower()), None)
            if col:
                cat_tables[v][wave] = tabulate_categorical(df, col, meta, wave)

    # ── 5. Reference do-file grep for missing vars ────────────────
    missing_vars = set()
    for v, row in exist_tbl.iterrows():
        if any("❌" in str(x) for x in row.values):
            missing_vars.add(v)

    alt_hits = {}
    for v in sorted(missing_vars):
        hits = grep_reference_do(iso3u, v, raw_root)
        if hits:
            alt_hits[v] = hits

    # ── 6. Build markdown report ──────────────────────────────────
    first, last = waves[0], waves[-1]
    md_path = output_dir / f"{iso3u}_dictionary_check_{first}_{last}.md"

    with open(md_path, "w", encoding="utf-8") as f:

        f.write(f"# Dictionary Check: {iso3u}_GEIH ({first} – {last})\n")
        f.write(f"Date: {date.today().isoformat()}\n")
        f.write(f"Tool: `harmonization_System/inputs/dictionary_check.py`\n")
        f.write(f"Waves checked: {', '.join(wave_results.keys())}\n\n---\n\n")

        # Section 1: Variable existence
        f.write("## Variable existence matrix\n\n")
        f.write("| Variable | Domain | " + " | ".join(wave_results.keys()) + " |\n")
        f.write("|----------|--------|" + "|".join(["---"] * len(wave_results)) + "|\n")
        for domain, vars_ in TARGET_VARS.items():
            for v in vars_:
                if v not in exist_tbl.index:
                    continue
                row = exist_tbl.loc[v]
                cells = " | ".join(str(row[w]) if w in row.index else "—" for w in wave_results)
                f.write(f"| `{v}` | {domain} | {cells} |\n")
        f.write("\n")

        # Section 2: Weight summary
        f.write("## Expansion factor summary\n\n")
        f.write("| Wave | N obs | Weight var | Sum | Min | Max |\n")
        f.write("|------|-------|-----------|-----|-----|-----|\n")
        for wave, row in weight_df.iterrows():
            f.write(f"| {wave} | {row['N']:,} | `{row['weight_var']}` | {row['sum']} | {row['min']} | {row['max']} |\n")
        f.write("\n")

        # Section 3: Key categoricals
        f.write("## Categorical variable checks\n\n")
        for v, wave_tabs in cat_tables.items():
            if not wave_tabs:
                f.write(f"### `{v}` — not present in any wave\n\n")
                continue
            f.write(f"### `{v}`\n\n")
            for wave, tbl in wave_tabs.items():
                if tbl is None or tbl.empty:
                    continue
                f.write(f"**{wave}**\n\n")
                f.write("| Value | Label | N | % |\n|---|---|---|---|\n")
                for _, r in tbl.iterrows():
                    f.write(f"| {r['value']} | {r['label']} | {r['n']:,} | {r['pct']:.1f}% |\n")
                f.write("\n")

        # Section 4: Alternative constructions from reference package
        f.write("## Alternative constructions found in reference package\n\n")
        if alt_hits:
            for v, hits in alt_hits.items():
                f.write(f"### `{v}`\n\n")
                for h in hits[:10]:  # cap at 10 lines per variable
                    f.write(f"- **{h['file']}** line {h['line']}: `{h['text'].strip()}`\n")
                f.write("\n")
        else:
            f.write("No alternative constructions found in reference package for missing variables.\n\n")

        # Section 5: Structural breaks
        f.write("## Structural break detection\n\n")
        f.write("Variables that appear in some waves but not others (candidate break points):\n\n")
        f.write("| Variable | First present | Last present | Absent waves |\n")
        f.write("|---|---|---|---|\n")
        wlist = list(wave_results.keys())
        for v in ALL_TARGET_VARS:
            present = [w for w in wlist if wave_results.get(w, {}).get(v, {}).get("exists")]
            absent  = [w for w in wlist if not wave_results.get(w, {}).get(v, {}).get("exists")]
            if present and absent:
                f.write(f"| `{v}` | {present[0]} | {present[-1]} | {', '.join(absent)} |\n")
        f.write("\n")

    print(f"\n  Report written to: {md_path.name}")
    return md_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HDMF Dictionary Check")
    parser.add_argument("--country", required=True, help="ISO3 country code, e.g. COL")
    parser.add_argument("--waves",   required=True, nargs="+",
                        help="Wave identifiers, e.g. 2018t3 2019t3 2022t3")
    args = parser.parse_args()

    run_check(
        iso3=args.country,
        waves=args.waves,
        output_dir=OUTPUT_DIR,
        raw_root=RAW_ROOT,
    )
