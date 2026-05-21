"""
build_caribbean_ppt_table.py
============================
Produces a compact, presentation-ready Excel table for Caribbean countries
showing migration variable availability (last year per country).

Output: output/caribbean_migration_ppt.xlsx

Columns: Country | Survey | Year | Identifies migrants? | 5yr in country?
- Green  : variable found  → variable name + question label
- Orange : not found       → "Not found"
- Gray   : no docs / not decodable → "No documentation" / "Not decodable"
"""

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
OUTPUT_DIR     = DATA_AVAIL_DIR / "output"

# ---------------------------------------------------------------------------
# Country metadata
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
# Keyword search
# ---------------------------------------------------------------------------
MIG_KW = [
    "lugar de nac", "pais de nac", "país de nac",
    "donde nació", "donde nacio", "dónde nació",
    "¿dónde nació", "¿donde nacio",
    "país de origen", "pais de origen",
    "zona de nacimiento",
    "entidad o país de nac", "entidad o pais de nac",
    "migrante", "migrant", "inmigrante", "immigr",
    "naturalidad", "nascimento", "naturalidade", "estrangeiro",
    "born abroad", "foreign born",
    "nacionalidad del", "país de nacionalidad", "pais de nacionalidad",
    "nationality", "naturalization",
    "country of birth", "place of birth", "birthplace",
    "were you born", "country were you born",
]
MIG_EXCLUDE = [
    "recién nacido", "recien nacido", "al nacer",
    "internacional", "jubilaci",
    "renta nacional", "ingreso nacional", "deuda nacional",
    "financiamiento nacional", "donaci", "sistema nac", "programa nac",
    "plan nac", "caja nac", "politica nac", "política nac",
    "hijas e hijos nacidos", "hijos nacidos", "nacidos vivos",
]
TIME_KW = [
    "tiempo de resid", "tiempo reside",
    "cuánto tiempo reside", "cuanto tiempo reside",
    "hace 5 años", "hace cinco años",
    "vivía hace", "vivia hace",
    "año de llegada", "mes de llegada", "fecha de llegada",
    "desde qué año vive", "desde que año vive",
    "desde cuándo vive", "desde cuando vive",
    "período llegó", "periodo llegó", "periodo llego",
    "llegó a vivir", "llego a vivir",
    "tempo de resid", "morando há", "chegada ao",
    "year of arrival", "date of arrival", "years of residence",
    "length of residence", "time of residence",
    "year arrived", "when did you arrive",
    # English keywords for Caribbean English-speaking surveys
    "been residing", "five years ago", "years in present residence",
]
TIME_EXCLUDE = [
    "trabajando", "trabajo", "empleo", "buscando",
    "ausencia", "espera regresar",
]


def search_vars(variables, keywords, excludes=None):
    excludes = excludes or []
    hits = []
    for v in variables:
        text = (v.get("name", "") + " " + v.get("label", "")).lower()
        if any(kw in text for kw in keywords):
            if not any(ex in text for ex in excludes):
                hits.append((v["name"], v.get("label", "")[:60]))
    return hits


def classify_labels(variables):
    labels = [v.get("label", "") for v in variables if v.get("label", "")]
    if not labels:
        return False
    return sum(len(l) for l in labels) / len(labels) > 5


# ---------------------------------------------------------------------------
# Load last wave per country
# ---------------------------------------------------------------------------
def load_last_waves() -> list[dict]:
    if not DECODED_TS_DIR.exists():
        print(f"ERROR: decoded_ts/ not found at {DECODED_TS_DIR}")
        sys.exit(1)

    pattern = re.compile(r"^([A-Z]{3})_(\d{4})([a-z0-9_]+)_dictionary\.json$")
    last: dict[str, dict] = {}

    for fpath in sorted(DECODED_TS_DIR.glob("*_dictionary.json")):
        m = pattern.match(fpath.name)
        if not m:
            continue
        iso3 = m.group(1)
        if iso3 not in CARIBBEAN_ISO3:
            continue

        year   = int(m.group(2))
        period = m.group(3)

        d            = json.loads(fpath.read_text(encoding="utf-8"))
        variables    = d.get("variables", [])
        decode_notes = d.get("decode_notes", [])
        source_files = d.get("source_files", [])

        is_no_doc = any("NO_DOCUMENTATION" in note for note in decode_notes)

        if is_no_doc or (len(variables) == 0 and not source_files):
            status = "NO_DOC"
        elif len(variables) == 0:
            status = "NOT_DECODED"
        elif not classify_labels(variables):
            status = "POOR_LABELS"
        else:
            status = "DECODED"

        mig_hits  = search_vars(variables, MIG_KW,  MIG_EXCLUDE) if status == "DECODED" else []
        time_hits = search_vars(variables, TIME_KW, TIME_EXCLUDE) if status == "DECODED" else []

        entry = {
            "iso3":    iso3,
            "year":    year,
            "period":  period,
            "status":  status,
            "n_vars":  len(variables),
            "mig":     mig_hits,
            "time":    time_hits,
        }

        prev = last.get(iso3)
        if prev is None or (year, period) > (prev["year"], prev["period"]):
            last[iso3] = entry

    # Sort alphabetically by ISO3 (BHS, BLZ, BRB, DOM, GUY, HTI, JAM, SUR, TTO)
    return sorted(last.values(), key=lambda w: w["iso3"])


# ---------------------------------------------------------------------------
# Excel styles
# ---------------------------------------------------------------------------
GREEN_FILL  = PatternFill("solid", fgColor="C6EFCE")
ORANGE_FILL = PatternFill("solid", fgColor="FFD966")
GRAY_FILL   = PatternFill("solid", fgColor="D9D9D9")
HEADER_FILL = PatternFill("solid", fgColor="1F497D")   # IDB dark blue
TITLE_FILL  = PatternFill("solid", fgColor="2E75B6")   # IDB medium blue
ROW_ALT     = PatternFill("solid", fgColor="F2F7FF")   # very light blue
ROW_WHITE   = PatternFill("solid", fgColor="FFFFFF")

GREEN_FONT  = Font(bold=False, color="276221", size=11)
ORANGE_FONT = Font(bold=False, color="7B4F00", size=11)
GRAY_FONT   = Font(bold=False, color="595959", size=11, italic=True)
HEADER_FONT = Font(bold=True,  color="FFFFFF", size=11)
TITLE_FONT  = Font(bold=True,  color="FFFFFF", size=13)
BODY_FONT   = Font(size=11)
BODY_BOLD   = Font(bold=True, size=11)

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)

thin  = Side(style="thin",   color="BFBFBF")
thick = Side(style="medium", color="9E9E9E")
THIN_BORDER  = Border(left=thin,  right=thin,  top=thin,  bottom=thin)
THICK_BORDER = Border(left=thick, right=thick, top=thick, bottom=thick)

NCOLS = 5  # Country | Survey | Year | Identifies migrants? | 5yr in country?

COL_WIDTHS = [22, 8, 6, 32, 32]
COL_HEADERS = [
    "Country",
    "Survey",
    "Year",
    "Identifies migrants?\n(country of birth / nationality)",
    "5+ years in country?\n(year of arrival / length of residence)",
]


def _clean_label(label: str) -> str:
    """Strip leading 'N. ' number-prefix (e.g. '7. nationality') and trailing '?'."""
    import re
    label = re.sub(r"^\d+\.\s*", "", label).strip().rstrip("?").strip()
    return label


def _status_cell(ws, row, col, status, hits):
    """Write a status cell with color coding."""
    cell = ws.cell(row=row, column=col)
    if status == "NO_DOC":
        cell.value       = "×  Not available"
        cell.fill        = ORANGE_FILL
        cell.font        = ORANGE_FONT
    elif status in ("NOT_DECODED", "POOR_LABELS"):
        cell.value       = "Not decodable"
        cell.fill        = GRAY_FILL
        cell.font        = GRAY_FONT
    elif hits:
        label = _clean_label(hits[0][1])
        cell.value       = f"✓  {label}"
        cell.fill        = GREEN_FILL
        cell.font        = GREEN_FONT
    else:
        cell.value       = "×  Not available"
        cell.fill        = ORANGE_FILL
        cell.font        = ORANGE_FONT
    cell.alignment   = LEFT
    cell.border      = THIN_BORDER


# ---------------------------------------------------------------------------
# Build Excel
# ---------------------------------------------------------------------------
def build_ppt_table(out_path: Path):
    waves = load_last_waves()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Caribbean"

    # ---- Title row (row 1) ----
    ws.row_dimensions[1].height = 28
    ws.merge_cells(f"A1:{get_column_letter(NCOLS)}1")
    title = ws["A1"]
    title.value     = "Caribbean — Migration Variable Availability (Latest Survey Year)"
    title.fill      = TITLE_FILL
    title.font      = TITLE_FONT
    title.alignment = CENTER

    # ---- Header row (row 2) ----
    ws.row_dimensions[2].height = 40
    for c, (w, h) in enumerate(zip(COL_WIDTHS, COL_HEADERS), start=1):
        cell = ws.cell(row=2, column=c)
        cell.value     = h
        cell.fill      = HEADER_FILL
        cell.font      = HEADER_FONT
        cell.alignment = CENTER
        cell.border    = THIN_BORDER
        ws.column_dimensions[get_column_letter(c)].width = w

    # ---- Data rows ----
    for r_idx, w in enumerate(waves, start=1):
        row = r_idx + 2  # offset by 2 header rows
        ws.row_dimensions[row].height = 38

        row_fill = ROW_ALT if r_idx % 2 == 0 else ROW_WHITE
        meta = COUNTRY_META.get(w["iso3"], {"name": w["iso3"], "survey": "?"})

        # Country
        c1 = ws.cell(row=row, column=1, value=meta["name"])
        c1.fill      = row_fill
        c1.font      = BODY_BOLD
        c1.alignment = LEFT
        c1.border    = THIN_BORDER

        # Survey
        c2 = ws.cell(row=row, column=2, value=meta["survey"])
        c2.fill      = row_fill
        c2.font      = BODY_FONT
        c2.alignment = CENTER
        c2.border    = THIN_BORDER

        # Year
        c3 = ws.cell(row=row, column=3, value=w["year"])
        c3.fill      = row_fill
        c3.font      = BODY_FONT
        c3.alignment = CENTER
        c3.border    = THIN_BORDER
        c3.number_format = "0"

        # Identifies migrants?
        _status_cell(ws, row, 4, w["status"], w["mig"])

        # 5yr in country?
        _status_cell(ws, row, 5, w["status"], w["time"])

    # ---- Footer / note row ----
    note_row = len(waves) + 3
    ws.row_dimensions[note_row].height = 18
    ws.merge_cells(f"A{note_row}:{get_column_letter(NCOLS)}{note_row}")
    note = ws.cell(row=note_row, column=1)
    note.value = (
        "Source: IDB network share survey documentation. "
        "Decoding based on variable dictionaries and .dta metadata (variable labels only, no microdata). "
        "✓ = keyword match found in decoded variables.  ✗ = no match.  Gray = no usable documentation."
    )
    note.font      = Font(size=8, italic=True, color="595959")
    note.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # ---- Freeze header ----
    ws.freeze_panes = "A3"

    OUTPUT_DIR.mkdir(exist_ok=True)
    wb.save(out_path)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    out = OUTPUT_DIR / "caribbean_migration_ppt.xlsx"
    build_ppt_table(out)
