"""
HDMF Dictionary Check — PER ENAHO version
==========================================
Checks ENAHO variable existence and category codes across annual waves 2018–2024.
Extends dictionary_check.py with PER-specific TARGET_VARS.

Usage:
    python dictionary_check_PER.py --waves 2018a 2019a 2020a 2021a 2022a 2023a 2024a

Output:
    bases armo/armo/per/intermediate_harmo_output/PER_dictionary_check_2018a_2024a.md
"""

import sys
import os

# ── Reuse helpers from the main dictionary_check module ──────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from dictionary_check import (
    read_dta, check_wave, tabulate_categorical,
    weight_summary, grep_reference_do, build_existence_table,
)

import argparse
from pathlib import Path
from datetime import date

# ── Project paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT     = PROJECT_ROOT / "bases armo" / "raw"
OUTPUT_DIR   = PROJECT_ROOT / "bases armo" / "armo" / "per" / "intermediate_harmo_output"

# ── PER ENAHO target variables by domain ─────────────────────────────────────
TARGET_VARS = {
    "IDs & weights": [
        "conglome", "vivienda", "hogar", "codperso",
        "factor07", "facpob07",
    ],
    "Demographics": [
        "p203",    # household relationship
        "p208a",   # age in years
    ],
    "Employment": [
        "p501",    # worked last week
        "p502",    # has fixed job
        "p503",    # has business
        "p5041", "p5042", "p5043", "p5044", "p5045",
        "p5046", "p5047", "p5048", "p5049", "p50410", "p50411",  # inactivity reasons
        "p546",    # main activity when inactive
        "p513t",   # hours primary job
        "p518",    # hours secondary job(s)
        "p507",    # occupation category
        "p511a",   # contract type
        "p558a1", "p558a2", "p558a3", "p558a4",  # pension affiliation
        "p558b2",  # year of last pension contribution
    ],
    "Education": [
        "p301a",   # educational level
        "p301b",   # grade within level (years)
        "p301c",   # completed grades within level
    ],
    "Migration": [
        "p401g2",  # mother's district/country code at birth (< 10000 = foreign)
        "p401f",   # 5 years ago, lived in this district?
        "p401g",   # district/country of residence 5 years ago
    ],
    "Remittances": [
        "d5563c",  # domestic remittances received (annual)
        "d5563e",  # foreign remittances received (annual)
    ],
}

ALL_TARGET_VARS = [v for vlist in TARGET_VARS.values() for v in vlist]

CATEGORICAL_VARS = [
    "p203",    # household relationship
    "p501",    # worked last week
    "p507",    # occupation category
    "p511a",   # contract type
    "p301a",   # education level
    "p401f",   # migration duration
]


def run_check_per(waves: list):
    iso3u = "PER"
    iso3l = "per"
    raw_dir = RAW_ROOT / iso3l
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nHDMF Dictionary Check — {iso3u} ENAHO — waves: {', '.join(waves)}")
    print("=" * 65)

    # ── 1. Load each wave ─────────────────────────────────────────
    wave_results = {}
    wave_dfs     = {}
    wave_metas   = {}

    for wave in waves:
        dta_path = raw_dir / f"{iso3u}_{wave}.dta"
        if not dta_path.exists():
            print(f"  SKIP {wave}: not found at {dta_path}")
            continue
        print(f"  Reading {dta_path.name} ...", end=" ", flush=True)
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
    weight_candidates = ["facpob07", "factor07"]
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
        hits = grep_reference_do(iso3u, v, RAW_ROOT)
        if hits:
            alt_hits[v] = hits

    # ── 6. Build markdown report ──────────────────────────────────
    first, last = waves[0], waves[-1]
    md_path = OUTPUT_DIR / f"PER_dictionary_check_{first}_{last}.md"

    with open(md_path, "w", encoding="utf-8") as f:

        f.write(f"# Dictionary Check: PER ENAHO ({first} – {last})\n")
        f.write(f"Date: {date.today().isoformat()}\n")
        f.write(f"Tool: `harmonization_System/inputs/dictionary_check_PER.py`\n")
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
        for row in weight_rows:
            f.write(f"| {row['wave']} | {row['N']:,} | `{row['weight_var']}` | {row['sum']} | {row['min']} | {row['max']} |\n")
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
                for h in hits[:10]:
                    f.write(f"- **{h['file']}** line {h['line']}: `{h['text'].strip()}`\n")
                f.write("\n")
        else:
            f.write("No alternative constructions found in reference package for missing variables.\n\n")

        # Section 5: Structural breaks
        f.write("## Structural break detection\n\n")
        f.write("Variables that appear in some waves but not others:\n\n")
        f.write("| Variable | First present | Last present | Absent waves |\n")
        f.write("|---|---|---|---|\n")
        wlist = list(wave_results.keys())
        for v in ALL_TARGET_VARS:
            present = [w for w in wlist if wave_results.get(w, {}).get(v, {}).get("exists")]
            absent  = [w for w in wlist if not wave_results.get(w, {}).get(v, {}).get("exists")]
            if present and absent:
                f.write(f"| `{v}` | {present[0]} | {present[-1]} | {', '.join(absent)} |\n")
        f.write("\n")

    print(f"\n  Report written to: {md_path}")
    return md_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HDMF Dictionary Check — PER ENAHO")
    parser.add_argument("--waves", required=True, nargs="+",
                        help="Wave identifiers, e.g. 2018a 2019a 2020a 2021a 2022a 2023a 2024a")
    args = parser.parse_args()
    run_check_per(waves=args.waves)
