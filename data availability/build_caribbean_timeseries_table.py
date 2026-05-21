"""
build_caribbean_timeseries_table.py
=====================================
Reads decoded_ts/[ISO3]_[YEAR][PERIOD]_dictionary.json files for Caribbean
countries, searches for migration-identification and 5-year-residence variables,
and writes caribbean_migration_timeseries.xlsx.

Caribbean countries covered: BLZ, BRB, DOM, GUY, HTI, JAM, SUR, TTO

Usage:
  python build_caribbean_timeseries_table.py
  python build_caribbean_timeseries_table.py --out my_output.xlsx
"""

import argparse
import json
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

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_AVAIL_DIR = Path(__file__).resolve().parent
DECODED_TS_DIR = DATA_AVAIL_DIR / "decoded_ts"

# ---------------------------------------------------------------------------
# Caribbean country metadata
# ---------------------------------------------------------------------------

COUNTRY_META = {
    "BHS": {"name": "Bahamas",            "survey": "LFS"},
    "BLZ": {"name": "Belize",             "survey": "LFS"},
    "BRB": {"name": "Barbados",           "survey": "CLFS"},
    "DOM": {"name": "Dominican Rep.",     "survey": "ENCFT"},
    "GUY": {"name": "Guyana",             "survey": "LFS"},
    "HTI": {"name": "Haiti",              "survey": "DHS"},
    "JAM": {"name": "Jamaica",            "survey": "LFS"},
    "SUR": {"name": "Suriname",           "survey": "SLC"},
    "TTO": {"name": "Trinidad & Tobago",  "survey": "CSSP"},
}

CARIBBEAN_ISO3 = set(COUNTRY_META.keys())

# ---------------------------------------------------------------------------
# Migration keyword search (identical to build_timeseries_table.py)
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
    # English keywords for Caribbean English-speaking surveys
    "country of birth", "place of birth", "birthplace", "born in",
    "were you born", "country were you born",
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
    # English keywords for Caribbean English-speaking surveys
    "year of arrival", "date of arrival", "years of residence",
    "length of residence", "time of residence",
    "been residing", "five years ago", "years in present residence",
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
# Read Caribbean decoded_ts JSONs
# ---------------------------------------------------------------------------

def load_caribbean_waves(last_only: bool = True) -> list[dict]:
    """Return wave dicts for Caribbean countries only, sorted by iso3 + year.
    If last_only=True (default), return only the most recent wave per country."""
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
        iso3 = m.group(1)
        if iso3 not in CARIBBEAN_ISO3:
            continue

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

    if last_only:
        # Keep only the last (highest year, then last period alphabetically) wave per country
        last: dict[str, dict] = {}
        for w in waves:
            prev = last.get(w["iso3"])
            if prev is None or (w["year"], w["period"]) > (prev["year"], prev["period"]):
                last[w["iso3"]] = w
        waves = sorted(last.values(), key=lambda w: w["iso3"])

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

    return {
        "country":  meta["name"],
        "iso3":     iso3,
        "survey":   meta["survey"],
        "year":     wave["year"],
        "period":   wave["period"],
        "mig_av":   mig_av,
        "mig_var":  mig_var,
        "mig_q":    mig_q,
        "time_av":  time_av,
        "time_var": time_var,
        "time_q":   time_q,
        "note":     note,
    }

# ---------------------------------------------------------------------------
# Excel output (12 columns — no N obs column)
# ---------------------------------------------------------------------------

GREEN  = "C6EFCE"
ORANGE = "FCE4D6"
GRAY   = "EDEDED"
BLUE_H = "1F4E79"
DARK_G = "375623"
BLUE2  = "2E75B6"
HEADER = "2F5496"

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
    ws.title = "Caribbean Migration"

    # ── Row 1: title ──────────────────────────────────────────────────────
    ws.merge_cells("A1:L1")
    c = ws["A1"]
    c.value = "Migration Variable Availability — Caribbean Household Surveys (Time Series 2015+)"
    c.font = Font(bold=True, size=13, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=BLUE_H)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    # ── Row 2: data source note ───────────────────────────────────────────
    ws.merge_cells("A2:L2")
    c = ws["A2"]
    c.value = (
        "Source: Decoded docs from IDB network share (SURVEYS/survey/[ISO3]/[SURVEY]/[YEAR]/[PERIOD]/docs/). "
        "'Not found' means the keyword was absent from the decoded file — not necessarily that the variable is unavailable."
    )
    c.font = Font(italic=True, size=8, color="444444")
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[2].height = 28

    # ── Row 3: section headers ────────────────────────────────────────────
    ws.merge_cells("A3:E3")

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

    ws.row_dimensions[3].height = 18

    # ── Row 4: column headers ─────────────────────────────────────────────
    COLS = [
        "Country", "ISO3", "Survey", "Year", "Period",
        "Available?", "Variable(s)", "Question wording",
        "Available?", "Variable(s)", "Question wording",
        "Notes (decoder)",
    ]
    hfont = Font(bold=True, color="FFFFFF", size=9)
    for ci, h in enumerate(COLS, 1):
        cell = ws.cell(row=4, column=ci, value=h)
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
        c_cell = ws.cell(row=r, column=1, value=lbl)
        c_cell.fill = PatternFill("solid", fgColor=color)
        c_cell.font = Font(bold=True, size=8)
        c_cell.border = thin_border()
        dc = ws.cell(row=r, column=2, value=desc)
        dc.font = Font(size=8)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)

    # ── Column widths ─────────────────────────────────────────────────────
    widths = [20, 6, 9, 6, 8,  16, 26, 40,  16, 26, 40,  52]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "F5"

    wb.save(out_path)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Build Caribbean migration time-series Excel from decoded_ts/"
    )
    ap.add_argument("--out", default="caribbean_migration_timeseries.xlsx",
                    help="Output Excel filename (default: caribbean_migration_timeseries.xlsx)")
    ap.add_argument("--all-years", action="store_true",
                    help="Include all years per country instead of last year only")
    args = ap.parse_args()

    print("Loading Caribbean waves from", DECODED_TS_DIR)
    waves = load_caribbean_waves(last_only=not args.all_years)
    print(f"Found {len(waves)} wave(s) across {len(set(w['iso3'] for w in waves))} countries")

    if not waves:
        print("No Caribbean JSONs found in decoded_ts/.")
        print("Run scan_and_decode_network.py --country BLZ (BRB, HTI, SUR, TTO) first.")
        sys.exit(1)

    print("\nBuilding rows...")
    rows = [build_row(w) for w in waves]

    found_mig  = sum(1 for r in rows if r["mig_av"]  == "FOUND")
    found_time = sum(1 for r in rows if r["time_av"] == "FOUND")
    print(f"  Migrant ID found:     {found_mig}/{len(rows)} waves")
    print(f"  5yr residence found:  {found_time}/{len(rows)} waves")

    out_path = DATA_AVAIL_DIR / "output" / args.out
    out_path.parent.mkdir(exist_ok=True)
    build_excel(rows, out_path)


if __name__ == "__main__":
    main()
