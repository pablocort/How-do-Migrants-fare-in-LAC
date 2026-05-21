"""
build_timeseries_table.py
==========================
Reads all decoded_ts/[ISO3]_[YEAR][PERIOD]_dictionary.json files,
searches for migration-identification and 5-year-residence variables,
adds N observations from HDMF raw .dta files for HDMF countries,
and writes migration_timeseries_table.xlsx.

Usage:
  python build_timeseries_table.py
  python build_timeseries_table.py --out my_output.xlsx
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("pip install openpyxl"); sys.exit(1)

try:
    import pyreadstat
    HAS_PYREADSTAT = True
except ImportError:
    HAS_PYREADSTAT = False
    print("WARNING: pyreadstat not available — N observations will be blank.")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_AVAIL_DIR = Path(__file__).resolve().parent
DECODED_TS_DIR = DATA_AVAIL_DIR / "decoded_ts"

# Root of the HDMF project (two levels up from data availability/)
HDMF_ROOT = DATA_AVAIL_DIR.parent
RAW_DIR = HDMF_ROOT / "bases armo" / "raw"

# ---------------------------------------------------------------------------
# HDMF country metadata for N obs lookup
# ---------------------------------------------------------------------------

# Countries where we have raw HDMF microdata
HDMF_COUNTRIES = {"COL", "ECU", "PER", "CHL", "MEX", "USA", "ESP"}

# Country-level name/survey labels (for the Excel output)
COUNTRY_META = {
    "ARG": {"name": "Argentina",       "survey": "EPH"},
    "BOL": {"name": "Bolivia",         "survey": "ECH"},
    "BRA": {"name": "Brazil",          "survey": "PNADC"},
    "CHL": {"name": "Chile",           "survey": "CASEN"},
    "COL": {"name": "Colombia",        "survey": "GEIH"},
    "CRI": {"name": "Costa Rica",      "survey": "ENAHO"},
    "DOM": {"name": "Dominican Rep.",  "survey": "ENCFT"},
    "ECU": {"name": "Ecuador",         "survey": "ENEMDU"},
    "GTM": {"name": "Guatemala",       "survey": "ENEIC"},
    "GUY": {"name": "Guyana",          "survey": "LFS"},
    "HND": {"name": "Honduras",        "survey": "EPHPM"},
    "JAM": {"name": "Jamaica",         "survey": "LFS"},
    "MEX": {"name": "Mexico",          "survey": "ENOE"},
    "PER": {"name": "Peru",            "survey": "ENAHO"},
    "PRY": {"name": "Paraguay",        "survey": "EPH"},
    "SLV": {"name": "El Salvador",     "survey": "EHPM"},
    "URY": {"name": "Uruguay",         "survey": "ECH"},
    "VEN": {"name": "Venezuela",       "survey": "EHM"},
    "USA": {"name": "United States",   "survey": "ACS"},
    "ESP": {"name": "Spain",           "survey": "EPA"},
}

# ---------------------------------------------------------------------------
# N obs lookup from HDMF raw data
# ---------------------------------------------------------------------------

def _norm_period(period: str) -> str:
    """Normalize period for filename matching (m11_m12_m1 → a etc.)"""
    if re.match(r"m\d{1,2}_m\d{1,2}", period):
        return "a"
    return period


def _scan_raw_files() -> dict[tuple[str, str, str], Path]:
    """
    Scan RAW_DIR for all .dta files and build a lookup:
    {(iso3_upper, year, period_norm): filepath}

    Patterns handled:
      COL_2024t3.dta        → (COL, 2024, t3)
      ECU_2019m12.dta       → (ECU, 2019, m12)
      PER_2024a.dta         → (PER, 2024, a)
      CHL_2017m11_m12_m1.dta→ (CHL, 2017, a)
      casen_2024.dta        → (CHL, 2024, a)
      ESP_2022a_merged.dta  → (ESP, 2022, a)
      usa_00004.dta         → (USA, 2024, a)   [hardcoded]
      MEX_2025t4.dta        → (MEX, 2025, t4)
    """
    lookup = {}
    if not RAW_DIR.exists():
        return lookup

    for country_folder in RAW_DIR.iterdir():
        if not country_folder.is_dir():
            continue
        iso3 = country_folder.name.upper()

        for f in country_folder.glob("*.dta"):
            name = f.stem.lower()

            # Pattern: [ISO3]_[YEAR][PERIOD]  (may have _merged or other suffix)
            m = re.match(
                r"([a-z]{3})_(\d{4})"
                r"(t[1-4]|m\d{1,2}|a|m\d{1,2}_m\d{1,2}_m\d{1,2})"
                r"(?:_.*)?$",
                name
            )
            if m:
                file_iso = m.group(1).upper()
                year     = m.group(2)
                period   = _norm_period(m.group(3))
                lookup[(file_iso, year, period)] = f
                continue

            # casen_2024.dta
            m2 = re.match(r"casen_(\d{4})", name)
            if m2:
                lookup[("CHL", m2.group(1), "a")] = f
                continue

            # usa_XXXXX.dta — assume 2024 annual
            if iso3 == "USA" and name.startswith("usa_"):
                lookup[("USA", "2024", "a")] = f
                continue

    return lookup


RAW_LOOKUP: dict[tuple[str, str, str], Path] = {}


def get_n_obs(iso3: str, year: int, period: str) -> int | None:
    """Return number of rows from the raw HDMF .dta file, or None."""
    if iso3 not in HDMF_COUNTRIES or not HAS_PYREADSTAT:
        return None
    global RAW_LOOKUP
    if not RAW_LOOKUP:
        RAW_LOOKUP.update(_scan_raw_files())

    key = (iso3, str(year), _norm_period(period))
    fpath = RAW_LOOKUP.get(key)
    if fpath is None:
        return None
    try:
        _, meta = pyreadstat.read_dta(str(fpath), metadataonly=True)
        return meta.number_rows
    except Exception as e:
        print(f"  WARNING: could not read {fpath.name}: {e}")
        return None

# ---------------------------------------------------------------------------
# Migration keyword search (identical to build_migration_table_v2.py)
# ---------------------------------------------------------------------------

MIG_KW = [
    "lugar de nac", "pais de nac", "país de nac",
    "donde nació", "donde nacio", "dónde nació",
    "¿dónde nació", "¿donde nacio",
    "país de origen", "pais de origen",
    "lugar de origen", "procedencia",
    "zona de nacimiento",
    "entidad o país de nac", "entidad o pais de nac",
    "país dónde vivía su", "pais donde vivia su",
    "migrante", "migrant", "inmigrante", "immigr",
    "naturalidad", "nascimento", "naturalidade", "estrangeiro",
    "born abroad", "foreign born",
    "nacionalidad del", "país de nacionalidad", "pais de nacionalidad",
    "nationality", "naturalization",
]
MIG_EXCLUDE = [
    "recién nacido", "recien nacido", "al nacer",
    "internacioanl", "internacional", "jubilaci",
    "renta nacional", "ingreso nacional", "deuda nacional",
    "financiamiento nacional", "donaci", "sistema nac", "programa nac",
    "plan nac", "caja nac", "politica nac", "política nac",
    "nación pueblo", "nacion pueblo", "pueblos indígena", "pueblos indigena",
    "discriminado", "discriminaci",
    "fecha de su\nnacimiento", "fecha de su nacimiento",
    "hijas e hijos nacidos", "hijos nacidos", "hija o hijo nacido",
    "hijos nacidos vivos", "nacidos vivos",
]
TIME_KW = [
    "tiempo de resid", "tiempo reside",
    "cuánto tiempo reside", "cuanto tiempo reside",
    "hace cuánto tiempo reside", "hace cuanto tiempo reside",
    "hace 5 años", "hace cinco años",
    "vivía hace", "vivia hace",
    "año de llegada", "mes de llegada", "fecha de llegada",
    "desde qué año vive", "desde que año vive",
    "desde qué año y mes vive", "desde que año y mes vive",
    "desde qué año", "desde que año",
    "desde cuándo vive", "desde cuando vive",
    "años viviendo en", "anos viviendo en",
    "tiempo de permanencia", "permanencia en el país", "permanencia en el pais",
    "período llegó", "periodo llegó", "periodo llego",
    "llegó a vivir", "llego a vivir",
    "cuándo llegó", "cuando llegó", "cuando llego",
    "año en que llegó", "año de llegada al",
    "tempo de resid", "morando há", "anos de resid", "chegada ao",
]
TIME_EXCLUDE = [
    "trabajando", "trabajo", "empleo", "buscando",
    "ausencia", "espera regresar", "télefono", "telefo",
    "desde qué año y mes fue",
]


def search_vars(variables, keywords, excludes=None):
    excludes = excludes or []
    hits = []
    for v in variables:
        text = (v.get("name", "") + " " + v.get("label", "")).lower()
        if any(kw in text for kw in keywords):
            if not any(ex in text for ex in excludes):
                hits.append((v["name"], v.get("label", "")[:80]))
    return hits


def classify_labels(variables):
    labels = [v.get("label", "") for v in variables if v.get("label", "")]
    if not labels:
        return False
    return sum(len(l) for l in labels) / len(labels) > 5

# ---------------------------------------------------------------------------
# Read all decoded_ts JSONs
# ---------------------------------------------------------------------------

def load_all_waves() -> list[dict]:
    """Return list of wave dicts sorted by iso3 + year."""
    if not DECODED_TS_DIR.exists():
        print(f"ERROR: decoded_ts/ not found at {DECODED_TS_DIR}")
        print("Run scan_and_decode_network.py first.")
        sys.exit(1)

    waves = []
    pattern = re.compile(r"^([A-Z]{3})_(\d{4})([a-z0-9_]+)_dictionary\.json$")

    for fpath in sorted(DECODED_TS_DIR.glob("*_dictionary.json")):
        m = pattern.match(fpath.name)
        if not m:
            continue
        iso3   = m.group(1)
        year   = int(m.group(2))
        period = m.group(3)

        d = json.loads(fpath.read_text(encoding="utf-8"))
        variables    = d.get("variables", [])
        decode_notes = d.get("decode_notes", [])
        source_files = d.get("source_files", [])
        n_vars       = len(variables)

        is_bulletin = any("BULLETIN" in note for note in decode_notes)
        is_no_doc   = any("NO_DOCUMENTATION" in note for note in decode_notes)

        if is_no_doc or (n_vars == 0 and not source_files):
            status = "NO_DOC"
        elif n_vars == 0:
            status = "NOT_DECODED"
        elif not classify_labels(variables):
            status = "POOR_LABELS"
        else:
            status = "DECODED"

        mig_hits  = search_vars(variables, MIG_KW,  MIG_EXCLUDE)  if status == "DECODED" else []
        time_hits = search_vars(variables, TIME_KW, TIME_EXCLUDE) if status == "DECODED" else []

        waves.append({
            "iso3":         iso3,
            "year":         year,
            "period":       period,
            "status":       status,
            "n_vars":       n_vars,
            "mig":          mig_hits,
            "time":         time_hits,
            "is_bulletin":  is_bulletin,
            "source_files": source_files,
            "decode_notes": decode_notes,
        })

    waves.sort(key=lambda w: (w["iso3"], w["year"], w["period"]))
    return waves

# ---------------------------------------------------------------------------
# Build one Excel row per wave
# ---------------------------------------------------------------------------

AVAIL_LABELS = {
    "FOUND":       "Yes — found",
    "NOT_FOUND":   "Not found",
    "NOT_DECODED": "Not decodable",
    "POOR_LABELS": "Not decodable",
    "NO_DOC":      "No documentation",
}


def build_row(wave: dict) -> dict:
    iso3   = wave["iso3"]
    year   = wave["year"]
    period = wave["period"]
    n_vars = wave["n_vars"]
    sf     = ", ".join(wave["source_files"]) if wave["source_files"] else "—"

    meta = COUNTRY_META.get(iso3, {"name": iso3, "survey": "?"})

    if wave["status"] == "NO_DOC":
        mig_av = time_av = "NO_DOC"
        mig_var = mig_q = time_var = time_q = "—"
        note = "No documentation file in docs/ folder."

    elif wave["status"] in ("NOT_DECODED", "POOR_LABELS"):
        reason = ("PDF classified as bulletin — 0 variables extracted."
                  if wave["is_bulletin"]
                  else f"Decoder returned {n_vars} variables but labels not descriptive.")
        mig_av = time_av = wave["status"]
        mig_var = mig_q = time_var = time_q = "—"
        note = f"Source: {sf}. {reason}"

    else:
        if wave["mig"]:
            mig_av  = "FOUND"
            mig_var = "; ".join(v[0] for v in wave["mig"][:3])
            mig_q   = wave["mig"][0][1] if wave["mig"] else "—"
        else:
            mig_av  = "NOT_FOUND"
            mig_var = "—"
            mig_q   = "—"

        if wave["time"]:
            time_av  = "FOUND"
            time_var = "; ".join(v[0] for v in wave["time"][:3])
            time_q   = wave["time"][0][1] if wave["time"] else "—"
        else:
            time_av  = "NOT_FOUND"
            time_var = "—"
            time_q   = "—"

        note = f"{n_vars} vars decoded from {sf}."

    n_obs = get_n_obs(iso3, year, period)

    return {
        "country":  meta["name"],
        "iso3":     iso3,
        "survey":   meta["survey"],
        "year":     year,
        "period":   period,
        "mig_av":   mig_av,
        "mig_var":  mig_var,
        "mig_q":    mig_q,
        "time_av":  time_av,
        "time_var": time_var,
        "time_q":   time_q,
        "n_obs":    n_obs,
        "note":     note,
    }

# ---------------------------------------------------------------------------
# Excel output
# ---------------------------------------------------------------------------

GREEN  = "C6EFCE"
ORANGE = "FCE4D6"
GRAY   = "EDEDED"
BLUE_H = "1F4E79"
DARK_G = "375623"
BLUE2  = "2E75B6"
HEADER = "2F5496"
PURPLE = "7030A0"   # N obs column header

FILL = {
    "FOUND":       PatternFill("solid", fgColor=GREEN),
    "NOT_FOUND":   PatternFill("solid", fgColor=ORANGE),
    "NOT_DECODED": PatternFill("solid", fgColor=GRAY),
    "POOR_LABELS": PatternFill("solid", fgColor=GRAY),
    "NO_DOC":      PatternFill("solid", fgColor=GRAY),
}


def thin_border():
    s = Side(style="thin", color="BBBBBB")
    return Border(left=s, right=s, top=s, bottom=s)


def build_excel(rows: list[dict], out_path: Path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Migration Time Series"

    # ── Row 1: title ──────────────────────────────────────────────────────
    ws.merge_cells("A1:M1")
    c = ws["A1"]
    c.value = "Migration Variable Availability — LAC Household Surveys (Time Series 2015+)"
    c.font = Font(bold=True, size=13, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=BLUE_H)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    # ── Row 2: data source note ───────────────────────────────────────────
    ws.merge_cells("A2:M2")
    c = ws["A2"]
    c.value = (
        "Source: Decoded docs from IDB network share (SURVEYS/survey/[ISO3]/[SURVEY]/[YEAR]/[PERIOD]/docs/). "
        "N observations from HDMF raw microdata (COL, ECU, PER, CHL, MEX, USA, ESP). "
        "'Not found' means the keyword was absent from the decoded file — not necessarily that the variable is unavailable."
    )
    c.font = Font(italic=True, size=8, color="444444")
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[2].height = 28

    # ── Row 3: section headers ────────────────────────────────────────────
    ws.merge_cells("A3:E3")    # Country + identifiers

    ws.merge_cells("F3:H3")
    h1 = ws["F3"]
    h1.value = "Identify migrant population"
    h1.font = Font(bold=True, size=10, color="FFFFFF")
    h1.fill = PatternFill("solid", fgColor=BLUE2)
    h1.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells("I3:K3")
    h2 = ws["I3"]
    h2.value = "5+ years in country"
    h2.font = Font(bold=True, size=10, color="FFFFFF")
    h2.fill = PatternFill("solid", fgColor=DARK_G)
    h2.alignment = Alignment(horizontal="center", vertical="center")

    # L and M standalone
    for col_letter in ("L3", "M3"):
        ws[col_letter].fill = PatternFill("solid", fgColor=PURPLE)

    ws.row_dimensions[3].height = 18

    # ── Row 4: column headers ─────────────────────────────────────────────
    COLS = [
        "Country", "ISO3", "Survey", "Year", "Period",
        "Available?", "Variable(s)", "Question wording",
        "Available?", "Variable(s)", "Question wording",
        "N Observations", "Notes (decoder)",
    ]
    hfont = Font(bold=True, color="FFFFFF", size=9)
    for ci, h in enumerate(COLS, 1):
        cell = ws.cell(row=4, column=ci, value=h)
        if ci in (12,):
            cell.fill = PatternFill("solid", fgColor=PURPLE)
        else:
            cell.fill = PatternFill("solid", fgColor=HEADER)
        cell.font = hfont
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border()
    ws.row_dimensions[4].height = 28

    # ── Data rows ─────────────────────────────────────────────────────────
    prev_iso3 = None
    shade_toggle = False

    for ri, row in enumerate(rows, 5):
        if row["iso3"] != prev_iso3:
            shade_toggle = not shade_toggle
            prev_iso3 = row["iso3"]

        row_bg = "EBF3FB" if shade_toggle else "FFFFFF"

        vals = [
            row["country"], row["iso3"], row["survey"],
            row["year"],    row["period"],
            AVAIL_LABELS[row["mig_av"]],  row["mig_var"],  row["mig_q"],
            AVAIL_LABELS[row["time_av"]], row["time_var"], row["time_q"],
            row["n_obs"],
            row["note"],
        ]

        for ci, val in enumerate(vals, 1):
            cell = ws.cell(row=ri, column=ci, value=val)
            cell.border = thin_border()
            cell.font = Font(size=9)
            cell.alignment = Alignment(vertical="center", wrap_text=True)

            if ci == 6:   # migrant ID available?
                cell.fill = FILL[row["mig_av"]]
                cell.font = Font(bold=True, size=9)
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif ci == 9:  # 5yr available?
                cell.fill = FILL[row["time_av"]]
                cell.font = Font(bold=True, size=9)
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif ci == 12:  # N obs
                cell.font = Font(size=9)
                cell.alignment = Alignment(horizontal="right", vertical="center")
                if val is not None:
                    cell.number_format = "#,##0"
            elif ci == 1:
                cell.font = Font(bold=True, size=9)
            else:
                if cell.fill.fgColor.rgb in ("00000000", "FFFFFFFF", ""):
                    cell.fill = PatternFill("solid", fgColor=row_bg)

        ws.row_dimensions[ri].height = 36

    # ── Legend ────────────────────────────────────────────────────────────
    lr = len(rows) + 7
    ws.cell(row=lr, column=1, value="Legend").font = Font(bold=True, size=9)
    items = [
        ("Yes — found",      GREEN,  "Variable confirmed in the decoded dictionary/questionnaire"),
        ("Not found",        ORANGE, "Dictionary decoded but no keyword match found (may still exist)"),
        ("Not decodable",    GRAY,   "Decoder returned 0 vars or labels are not descriptive"),
        ("No documentation", GRAY,   "No suitable file found in docs/ for this year"),
    ]
    for i, (lbl, color, desc) in enumerate(items):
        r = lr + 1 + i
        c = ws.cell(row=r, column=1, value=lbl)
        c.fill = PatternFill("solid", fgColor=color)
        c.font = Font(bold=True, size=8)
        c.border = thin_border()
        dc = ws.cell(row=r, column=2, value=desc)
        dc.font = Font(size=8)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)

    # ── Column widths ─────────────────────────────────────────────────────
    widths = [18, 6, 9, 6, 8,  16, 26, 40,  16, 26, 40,  14, 52]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "F5"

    wb.save(out_path)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Build migration time-series Excel from decoded_ts/")
    ap.add_argument("--out", default="migration_timeseries_table.xlsx",
                    help="Output Excel filename (default: migration_timeseries_table.xlsx)")
    args = ap.parse_args()

    print("Loading decoded waves from", DECODED_TS_DIR)
    waves = load_all_waves()
    print(f"Found {len(waves)} wave(s) across {len(set(w['iso3'] for w in waves))} countries")

    if not waves:
        print("No JSONs found in decoded_ts/. Run scan_and_decode_network.py first.")
        sys.exit(1)

    print("\nBuilding rows and looking up N observations...")
    rows = [build_row(w) for w in waves]

    # Print summary
    found_mig  = sum(1 for r in rows if r["mig_av"]  == "FOUND")
    found_time = sum(1 for r in rows if r["time_av"] == "FOUND")
    has_nobs   = sum(1 for r in rows if r["n_obs"] is not None)
    print(f"  Migrant ID found:         {found_mig}/{len(rows)} waves")
    print(f"  5yr residence found:      {found_time}/{len(rows)} waves")
    print(f"  N observations available: {has_nobs}/{len(rows)} waves")

    out_path = DATA_AVAIL_DIR / "output" / args.out
    out_path.parent.mkdir(exist_ok=True)
    build_excel(rows, out_path)


if __name__ == "__main__":
    main()
