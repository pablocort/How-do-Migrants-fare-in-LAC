#!/usr/bin/env python3
"""
build_epa_annual.py
Imports INE EPA quarterly fixed-width text files (208 positions per record)
and appends Q1-Q4 into one annual DTA file per year (2018-2025).

Output: bases armo/raw/esp/ESP_[YEAR]a_merged.dta (8 files)

Two schemas are handled automatically:
  - Pre-2021 ("Pet-2014"):  152 variables, some positions differ
  - 2021+   ("EPA-TRIM-2021"): 138 variables, new standard positions
"""

import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

ESP_RAW = Path(__file__).parent
PROJECT_ROOT = ESP_RAW.parent.parent.parent  # How-do-Migrants-fare-in-LAC/

# ─────────────────────────────────────────────────────────────────────────────
# Variable column specs (1-indexed from design docs → converted to 0-indexed
# half-open intervals for pandas read_fwf: (start-1, end))
#
# We read a SUBSET of columns relevant to HDMF harmonization + identifiers.
# Full 208-position record is read; non-selected columns are dropped.
# ─────────────────────────────────────────────────────────────────────────────

# Common variables: identical positions in ALL years (2018-2025)
# Format: (var_name, col_start_0indexed, col_end_exclusive)
COLS_COMMON = [
    ("CICLO",    0,   3),   # Period (YYYY + Q digit encoded)
    ("CCAA",     3,   5),   # Autonomous community
    ("PROV",     5,   7),   # Province
    ("NVIVI",    7,  12),   # Household number
    ("NIVEL",   12,  13),   # Record level (should always be 2 = person)
    ("NPERS",   13,  15),   # Person number within household
    ("MES",     15,  17),   # Birth month
    ("ANO_NAC", 17,  21),   # Birth year (4 digits) — renamed to avoid collision with survey year 'ano'
    ("EDAD1",   21,  24),   # Age (years)
    ("RELPP1",  24,  25),   # Relationship to reference person
    ("SEXO1",   25,  26),   # Sex (1=male, 6=female)
    ("PRONA1",  34,  36),   # Province of birth (if Spain)
    ("PAINA1",  36,  39),   # Country of birth (if abroad, ISO-3 code)
    ("NAC1",    39,  40),   # Nationality (1=Spanish, 2=other EU, 3=other)
    ("EXTNA1",  40,  43),   # Country of foreign nationality (ISO-3)
    ("ANORE",   43,  45),   # Years of residence in Spain
    ("NFORMA",  45,  47),   # Education level (CNED 2014 codes)
    ("CURSR",   52,  53),   # Currently enrolled in formal education
    ("NCURSR",  53,  55),   # Level of formal education being pursued
    ("TRAREM",  63,  64),   # Did paid work last week
    ("AYUDFA",  64,  65),   # Unpaid family work last week
    ("AUSENT",  65,  66),   # Absent but has job
    ("OCUP",    71,  73),   # Main occupation (CNO-2011, 2-digit)
    ("ACT",     73,  75),   # Main activity (CNAE-2009, 2-digit)
    ("SITU",    75,  77),   # Employment status
    ("SP",      77,  78),   # Public/private sector
    ("DUCON1",  78,  79),   # Contract type: permanent(1) or temporary(2)
    ("DUCON2",  79,  80),   # Permanent: indefinite(1) or fixed-term(2)
    ("DUCON3",  80,  82),   # Temporary contract sub-type
    ("PARCO1",  97,  98),   # Full(1) or part-time(2)
    ("HORASP", 100, 104),   # Contracted hours (HHMM)
    ("HORASE", 108, 112),   # Effective hours last week (HHMM)
    ("EXTRA",  112, 113),   # Worked overtime last week
    ("EXTPAG", 113, 117),   # Paid overtime hours (HHMM)
    ("EXTNPG", 117, 121),   # Unpaid overtime hours (HHMM)
    ("OCUPA_ANT", 171, 173),# Last job occupation (if left <= 1 year ago)
    ("ACTA_ANT", 173, 175), # Last job activity (if left <= 1 year ago)
    ("SITUA_ANT",175, 177), # Last job status (if left <= 1 year ago)
    ("OFEMP",  177, 178),   # Registered with employment office
    ("FACTOREL",201, 208),  # Expansion weight (integer, divide by 10^4 if needed)
]

# Variables that DIFFER between pre-2021 and 2021+ schemas
# Pre-2021: positions 128-143 were used for secondary employment (old layout)
# 2021+: secondary employment variables shifted right
COLS_PRE2021 = [
    ("HORASH",  104, 108),  # Usual hours main job (HHMM) — renamed in 2023
    # BUSCA/DESEA/BUSOTR: corrected positions verified against Q1-2018 raw file.
    # Old positions (149-150, 150-151, 142-143) were wrong — the EPA 2021 redesign
    # moved these variables and the original script used the post-2021 positions
    # for the pre-2021 schema, resulting in near-zero unemployment counts.
    ("BUSOTR",  140, 141),  # Looking for another job (while employed) — CORRECTED from 142-143
    ("BUSCA",   141, 142),  # Looked for work in last 4 weeks — CORRECTED from 149-150
    ("DESEA",   142, 143),  # Desires employment (asked only of busca==6 respondents) — CORRECTED from 150-151
    ("TRAPLU",  121, 122),  # Has second job
    ("OCUPLU",  122, 124),  # Second job occupation (was at 125-126, use 122-124 per design)
    ("ACTPLU",  124, 126),  # Second job activity
    ("SITPLU",  126, 128),  # Second job status
    ("HOREPLU", 128, 132),  # Effective hours second job (HHMM)
    ("HORHPLU", 132, 136),  # Usual hours second job (HHMM)
    ("MASHOR",  136, 137),  # Would like more hours
    ("DISMAS",  137, 138),  # Available to work more hours
    ("RZNDISH", 138, 140),  # Reason cannot work more
]

COLS_2021PLUS = [
    ("HORASH1", 104, 108),  # Usual hours main job (HHMM) — new name in 2023
    ("TRAPLU",  127, 128),  # Has second job
    ("OCUPLU",  128, 130),  # Second job occupation
    ("ACTPLU",  130, 132),  # Second job activity
    ("SITPLU",  132, 134),  # Second job status
    ("HOREPLU", 134, 138),  # Effective hours second job (HHMM)
    ("HORHPLU", 138, 142),  # Usual hours second job (HHMM)
    ("MASHOR",  142, 143),  # Would like more hours
    ("DISMAS",  143, 144),  # Available to work more hours
    ("RZNDISH", 144, 146),  # Reason cannot work more
    ("HORDES",  146, 148),  # Desired hours (2-digit: just HH in 2021+)
    ("BUSOTR",  148, 149),  # Looking for another job
    ("BUSCA",   149, 150),  # Looked for work in last 4 weeks
    ("DESEA",   150, 151),  # Desires employment
]


# ─────────────────────────────────────────────────────────────────────────────
# Raw file inventory: year → quarter → path
# Files are plain text, fixed-width, no extension or .txt
# ─────────────────────────────────────────────────────────────────────────────

_UNC = r"\\?\ "[:-1]   # "\\?\" — Windows extended-path prefix (avoids escape-seq warning)

def _long(p: Path) -> Path:
    """Return Windows extended-length path (UNC prefix) to bypass MAX_PATH=260."""
    s = str(p.absolute())
    return Path(_UNC + s) if not s.startswith(_UNC) else p


def _readable(p: Path) -> bool:
    try:
        return p.exists() or _long(p).exists()
    except Exception:
        return False


def _open_path(p: Path):
    """Return a path or file object that can be opened despite long paths."""
    if p.exists():
        return p
    lp = _long(p)
    if lp.exists():
        return lp
    return p  # let caller handle FileNotFoundError


RAW_FILES = {
    2018: {
        1: ESP_RAW / "2018" / "EPA2digitosT0118",
        2: ESP_RAW / "2018" / "EPA2digitosT0218",
        3: ESP_RAW / "2018" / "EPA2digitosT0318",
        4: ESP_RAW / "2018" / "EPA2digitosT0418",
    },
    2019: {
        1: ESP_RAW / "2019" / "EPA2digitosT0119",
        2: ESP_RAW / "2019" / "EPA2digitosT0219",
        3: ESP_RAW / "2019" / "EPA2digitosT0319",
        4: ESP_RAW / "2019" / "E572E.PEL208.QC.T0419",
    },
    2020: {
        1: ESP_RAW / "2020" / "EPA2digitosT0120",
        2: ESP_RAW / "2020" / "EPA2digitos.T0220",
        3: ESP_RAW / "2020" / "EPA2digitosT0320",
        4: ESP_RAW / "2020" / "EPA2digitosT0420",
    },
    2021: {
        1: ESP_RAW / "2021" / "T0121EPA2digitos",
        2: ESP_RAW / "2021" / "T0221EPA2digitos",
        3: ESP_RAW / "2021" / "EPAT0321",
        4: ESP_RAW / "2021" / "T0421",
    },
    2022: {
        1: ESP_RAW / "2022" / "T0122",
        2: ESP_RAW / "2022" / "T0222",
        3: ESP_RAW / "2022" / "T0322",
        4: ESP_RAW / "2022" / "T0422",
    },
    2023: {
        1: ESP_RAW / "2023" / "T0123",
        2: ESP_RAW / "2023" / "T0223",
        3: ESP_RAW / "2023" / "T0323",
        4: ESP_RAW / "2023" / "T0423",
    },
    2024: {
        1: ESP_RAW / "2024" / "T0124",
        2: ESP_RAW / "2024" / "T0224",
        3: ESP_RAW / "2024" / "T0324",
        4: ESP_RAW / "2024" / "T0424",
    },
    2025: {
        1: ESP_RAW / "2025" / "T0125.txt",
        2: ESP_RAW / "2025" / "T0225",
        3: ESP_RAW / "2025" / "T0325.txt",
        4: ESP_RAW / "2025" / "T0425.txt",
    },
}


def colspecs_and_names(year: int):
    """Return (colspecs, names) for pandas read_fwf based on schema year."""
    if year < 2021:
        extra = COLS_PRE2021
    else:
        extra = COLS_2021PLUS

    all_cols = COLS_COMMON + extra
    # Remove duplicates (keep first occurrence by name)
    seen = set()
    deduped = []
    for name, s, e in all_cols:
        if name not in seen:
            seen.add(name)
            deduped.append((name, s, e))

    deduped.sort(key=lambda x: x[1])  # sort by start position
    colspecs = [(s, e) for _, s, e in deduped]
    names    = [n    for n, _, _ in deduped]
    return colspecs, names


def hhmm_to_hours(series: pd.Series) -> pd.Series:
    """
    Convert HHMM integer column to decimal hours.
    EPA stores hours as 4-digit HHMM (e.g. 4030 = 40h 30min = 40.5h).
    Values of 0 remain 0; missing (blanks read as NaN) stay NaN.
    """
    s = pd.to_numeric(series, errors="coerce")
    hh = (s // 100).astype("Int64")
    mm = (s %  100).astype("Int64")
    result = hh + mm / 60.0
    result[s.isna()] = pd.NA
    return result


def read_quarter(path: Path, year: int, quarter: int) -> pd.DataFrame:
    """Read one quarterly fixed-width file and return a DataFrame."""
    colspecs, names = colspecs_and_names(year)

    open_p = _open_path(path)

    try:
        df = pd.read_fwf(
            open_p,
            colspecs=colspecs,
            names=names,
            header=None,
            dtype=str,           # read everything as string first
            encoding="latin-1",  # INE files are ISO-8859-1
            na_values=[""],
        )
    except FileNotFoundError:
        print(f"    [WARN] File not found: {path.name} — skipping Q{quarter}")
        return pd.DataFrame()
    except Exception as e:
        print(f"    [ERROR] {path.name}: {e}")
        return pd.DataFrame()

    df["trimestre"] = quarter
    df["ano"]       = year

    # NIVEL=1: adults (16+) with full employment/education data
    # NIVEL=2: children under 16 (blank employment variables)
    # Keep ALL records; harmonization script will handle age filters.
    # (No NIVEL filter here — let variablesBID.do decide the age cutoff)

    print(f"    Q{quarter}: {len(df):>7,} records from {path.name}")
    return df


def convert_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Convert known numeric columns; convert hours from HHMM to decimal."""
    hours_cols = ["HORASP", "HORASH", "HORASH1", "HORASE",
                  "EXTPAG", "EXTNPG", "HOREPLU", "HORHPLU"]
    numeric_cols = [
        "CICLO", "CCAA", "PROV", "NVIVI", "NPERS", "MES", "ANO",
        "EDAD1", "RELPP1", "SEXO1", "PRONA1", "PAINA1",
        "NAC1", "EXTNA1", "ANORE", "NFORMA", "CURSR", "NCURSR",
        "TRAREM", "AYUDFA", "AUSENT", "OCUP", "ACT", "SITU",
        "SP", "DUCON1", "DUCON2", "DUCON3", "PARCO1",
        "EXTRA", "TRAPLU", "OCUPLU", "ACTPLU", "SITPLU",
        "MASHOR", "DISMAS", "RZNDISH", "HORDES", "BUSOTR", "BUSCA",
        "DESEA", "OFEMP", "FACTOREL",
        "OCUPA_ANT", "ACTA_ANT", "SITUA_ANT",
    ]

    for col in hours_cols:
        if col in df.columns:
            df[col] = hhmm_to_hours(df[col])

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def build_year(year: int) -> pd.DataFrame:
    """Read all 4 quarters for a year and return the appended DataFrame."""
    quarters = RAW_FILES.get(year, {})
    parts = []
    for q in [1, 2, 3, 4]:
        path = quarters.get(q)
        if path is None:
            print(f"    Q{q}: no path defined — skipping")
            continue
        df = read_quarter(path, year, q)
        if not df.empty:
            parts.append(df)

    if not parts:
        print(f"  [WARN] No quarters loaded for {year}")
        return pd.DataFrame()

    annual = pd.concat(parts, ignore_index=True)
    annual = convert_numeric(annual)
    print(f"  -> {len(annual):>8,} total records for {year}")
    return annual


def save_dta(df: pd.DataFrame, year: int):
    """Save DataFrame as Stata DTA file."""
    out_name = f"ESP_{year}a_merged.dta"
    out_path = ESP_RAW / out_name

    # pyreadstat needs string path; use extended path if needed
    out_str = str(out_path.absolute())
    if len(out_str) > 255:
        out_str = _UNC + out_str

    # Convert all column names to lowercase (Stata convention)
    df.columns = [c.lower() for c in df.columns]

    # Float64 → float32 where possible to reduce file size
    for col in df.select_dtypes("float64").columns:
        df[col] = df[col].astype("float64")

    try:
        pyreadstat.write_dta(df, out_str)
        print(f"  Saved: {out_name}  ({out_path.stat().st_size / 1e6:.1f} MB)")
    except Exception as e:
        print(f"  [ERROR] Could not save {out_name}: {e}")
        # Fallback: save as CSV
        csv_path = ESP_RAW / f"ESP_{year}a_merged.csv"
        df.to_csv(str(csv_path.absolute()), index=False, encoding="utf-8-sig")
        print(f"  Fallback CSV saved: {csv_path.name}")


def print_summary(df: pd.DataFrame, year: int):
    """Print quick descriptive stats for key HDMF variables."""
    print(f"\n  --- Summary for {year} ---")
    n = len(df)
    print(f"  Observations: {n:,}")

    checks = {
        "sexo1":    ("Sex (1=M 6=F)", lambda s: s.value_counts().to_dict()),
        "situ":     ("Emp status", lambda s: s.value_counts().nlargest(5).to_dict()),
        "nforma":   ("Education", lambda s: s.value_counts().nlargest(5).to_dict()),
        "nac1":     ("Nationality (1=ES)", lambda s: s.value_counts().to_dict()),
        "factorel": ("Weight non-null", lambda s: f"{s.notna().sum():,}/{n:,}"),
        "edad1":    ("Age range", lambda s: f"{s.min():.0f}–{s.max():.0f}, mean={s.mean():.1f}"),
        "horase":   ("Hours worked (mean)", lambda s: f"{s[s>0].mean():.1f}h"),
    }
    for col, (label, fn) in checks.items():
        if col in df.columns:
            try:
                print(f"  {label}: {fn(df[col])}")
            except Exception:
                pass


def main():
    years = list(range(2018, 2026))
    print("=" * 60)
    print("EPA Annual Builder — importing quarterly files")
    print(f"Years: {years[0]}–{years[-1]}")
    print("=" * 60)

    for year in years:
        schema = "Pre-2021" if year < 2021 else "2021+"
        print(f"\n[{year}] Schema: {schema}")
        df = build_year(year)
        if df.empty:
            print(f"  [SKIP] No data for {year}")
            continue
        print_summary(df, year)
        save_dta(df, year)

    print("\n" + "=" * 60)
    print("Done. Output files:")
    for year in years:
        out = ESP_RAW / f"ESP_{year}a_merged.dta"
        if _readable(out):
            size = out.stat().st_size / 1e6
            print(f"  ESP_{year}a_merged.dta  ({size:.1f} MB)")
        else:
            out_csv = ESP_RAW / f"ESP_{year}a_merged.csv"
            if _readable(out_csv):
                print(f"  ESP_{year}a_merged.csv  (fallback)")
            else:
                print(f"  ESP_{year}a_merged  [NOT CREATED]")


if __name__ == "__main__":
    main()
