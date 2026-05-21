"""
Migration variable availability table — strictly from decoded JSONs only.
No general survey knowledge. If a variable wasn't found in the decoded JSON, it is NOT_FOUND.
"""
import json, os, sys
from pathlib import Path

DATA_AVAIL_DIR = Path(__file__).resolve().parent
OUTPUT_DIR     = DATA_AVAIL_DIR / "output"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("pip install openpyxl"); sys.exit(1)

# ── Keyword lists ─────────────────────────────────────────────────────────────
# Cast wide — we filter false positives manually after seeing results

MIG_KW = [
    # Place/country of birth — specific enough to avoid false positives
    "lugar de nac",       # lugar de nacimiento
    "pais de nac",        # pais de nacimiento
    "país de nac",
    "donde nació", "donde nacio", "dónde nació",
    "¿dónde nació", "¿donde nacio",   # EPH-style question format
    "país de origen", "pais de origen",
    "lugar de origen", "procedencia",
    "zona de nacimiento",
    "entidad o país de nac", "entidad o pais de nac",   # MEX ENOE style
    "país dónde vivía su",   # CHL r1b: country where parent lived at birth
    "pais donde vivia su",
    # Explicit migrant/foreign identifiers
    "migrante", "migrant", "inmigrante", "immigr",
    "naturalidad",        # naturalidade (PT)
    "nascimento",         # PT: place of birth
    "naturalidade",
    "estrangeiro",        # PT: foreigner
    "born abroad", "foreign born",
    # Nationality
    "nacionalidad del",   # avoids "nacional" false positives
    "país de nacionalidad",  # CHL r1a style
    "pais de nacionalidad",
    "nationality",
    "naturalization",
]

# Exclude phrases that produce false positives
MIG_EXCLUDE = [
    "recién nacido", "recien nacido",  # newborn
    "al nacer",                         # at birth (sex at birth)
    "internacioanl",
    "internacional",
    "jubilaci",                         # pension from abroad
    # Specific "nacional" false positives (keep "nacionalidad" as it is migration-related)
    "renta nacional",
    "ingreso nacional",
    "deuda nacional",
    "financiamiento nacional",
    "donaci",                           # donación (often paired with "nac" short)
    "sistema nac",                      # sistema nacional (health, etc.)
    "programa nac",                     # programa nacional
    "plan nac",
    "caja nac",                         # caja nacional (health fund)
    "politica nac", "política nac",
    "nación pueblo",                    # indigenous nation (not nationality)
    "nacion pueblo",
    "pueblos indígena", "pueblos indigena",   # indigenous peoples
    "discriminado",                     # discrimination question listing categories
    "discriminaci",
    "fecha de su\nnacimiento", "fecha de su nacimiento",  # birth date (not place)
    "hijas e hijos nacidos",            # children born alive
    "hijos nacidos",
    "hija o hijo nacido",
    "hijos nacidos vivos",
    "nacidos vivos",
]

TIME_KW = [
    # Explicit residence-time questions
    "tiempo de resid",
    "tiempo reside",
    "cuánto tiempo reside", "cuanto tiempo reside",
    "hace cuánto tiempo reside", "hace cuanto tiempo reside",
    "hace 5 años", "hace cinco años",
    "vivía hace", "vivia hace",
    "año de llegada", "mes de llegada", "fecha de llegada",
    "desde qué año vive", "desde que año vive",
    "desde qué año y mes vive", "desde que año y mes vive",  # BOL s01b_13a
    "desde qué año", "desde que año",   # broader BOL match
    "desde cuándo vive", "desde cuando vive",
    "años viviendo en", "anos viviendo en",
    "tiempo de permanencia",
    "permanencia en el país", "permanencia en el pais",
    # Arrival period / year of arrival
    "período llegó", "periodo llegó", "periodo llego",
    "llegó a vivir", "llego a vivir",
    "cuándo llegó", "cuando llegó", "cuando llego",
    "año en que llegó", "año de llegada al",
    # Portuguese
    "tempo de resid",
    "morando há",
    "anos de resid",
    "chegada ao",
]

# Exclude phrases that produce false positives
TIME_EXCLUDE = [
    "trabajando",    # work tenure
    "trabajo",       # job duration
    "empleo",        # employment duration
    "buscando",      # job search time
    "ausencia",      # absence from work
    "espera regresar",  # expected return to work
    "télefono", "telefo",  # phone
    "desde qué año y mes fue",   # year event occurred, not residence
]

# ── Country registry ──────────────────────────────────────────────────────────
REGISTRY = {
    "ARG": {"name": "Argentina",       "survey": "EPH",    "period": "2023"},
    "BLZ": {"name": "Belize",          "survey": "—",      "period": "—"},
    "BOL": {"name": "Bolivia",         "survey": "EH",     "period": "2024"},
    "BRA": {"name": "Brazil",          "survey": "PNADC",  "period": "2025"},
    "CHL": {"name": "Chile",           "survey": "CASEN",  "period": "2024"},
    "COL": {"name": "Colombia",        "survey": "GEIH",   "period": "2025"},
    "CRI": {"name": "Costa Rica",      "survey": "ENAHO",  "period": "2025"},
    "DOM": {"name": "Dominican Rep.",  "survey": "ENFT",   "period": "2024"},
    "ECU": {"name": "Ecuador",         "survey": "ENEMDU", "period": "2025"},
    "GTM": {"name": "Guatemala",       "survey": "ENEIC",  "period": "2025"},
    "GUY": {"name": "Guyana",          "survey": "GLFS",   "period": "2021"},
    "HND": {"name": "Honduras",        "survey": "EPHPM",  "period": "2025"},
    "HTI": {"name": "Haiti",           "survey": "DHS",    "period": "2017"},
    "JAM": {"name": "Jamaica",         "survey": "—",      "period": "—"},
    "MEX": {"name": "Mexico",          "survey": "ENOE",   "period": "2024"},
}

# ── Search decoded JSONs ──────────────────────────────────────────────────────

def search_vars(variables, keywords, excludes=None):
    """Return list of (name, label) for vars matching any keyword but no exclude phrase."""
    excludes = excludes or []
    hits = []
    for v in variables:
        text = (v.get("name", "") + " " + v.get("label", "")).lower()
        if any(kw in text for kw in keywords):
            if not any(ex in text for ex in excludes):
                hits.append((v["name"], v.get("label", "")[:80]))
    return hits

def classify_labels(variables):
    """
    Check if extracted labels are meaningful (not just question numbers like '1','2','3').
    Returns True if labels look descriptive.
    """
    labels = [v.get("label", "") for v in variables if v.get("label", "")]
    if not labels:
        return False
    # If average label length < 5 chars, labels are just numbers — not useful
    avg_len = sum(len(l) for l in labels) / len(labels)
    return avg_len > 5

DECODED_DIR = DATA_AVAIL_DIR / "decoded"
results = {}

for iso in REGISTRY:
    path = DECODED_DIR / f"{iso}_dictionary.json"
    if not path.exists():
        results[iso] = {"status": "NO_FILE", "n_vars": 0, "mig": [], "time": [], "notes": "JSON file not found"}
        continue

    d = json.load(open(path, encoding="utf-8"))
    variables = d.get("variables", [])
    n = len(variables)
    source_files = d.get("source_files", [])
    decode_notes = d.get("decode_notes", [])

    # Determine decode quality
    has_useful_labels = classify_labels(variables)
    is_bulletin = any("BULLETIN" in note for note in decode_notes)
    is_no_doc   = any("NO_DOCUMENTATION" in note for note in decode_notes)

    if is_no_doc or n == 0 and not source_files:
        status = "NO_DOC"
    elif n == 0:
        status = "NOT_DECODED"   # file existed but parser returned nothing
    elif not has_useful_labels:
        status = "POOR_LABELS"   # vars extracted but labels not meaningful
    else:
        status = "DECODED"

    mig_hits  = search_vars(variables, MIG_KW,  MIG_EXCLUDE)  if status == "DECODED" else []
    time_hits = search_vars(variables, TIME_KW, TIME_EXCLUDE) if status == "DECODED" else []

    results[iso] = {
        "status":       status,
        "n_vars":       n,
        "source_files": source_files,
        "mig":          mig_hits,
        "time":         time_hits,
        "is_bulletin":  is_bulletin,
        "decode_notes": decode_notes,
    }

# ── Print diagnostic ──────────────────────────────────────────────────────────
print("=== Diagnostic ===")
for iso, r in results.items():
    print(f"\n{iso} ({REGISTRY[iso]['survey']}) — status={r['status']}, n_vars={r['n_vars']}")
    if r["mig"]:
        print(f"  MIG hits  ({len(r['mig'])}): {r['mig'][:3]}")
    if r["time"]:
        print(f"  TIME hits ({len(r['time'])}): {r['time'][:3]}")

# ── Determine final row values ────────────────────────────────────────────────
# Status codes: FOUND / NOT_FOUND / NOT_DECODED / POOR_LABELS / NO_DOC

def build_row(iso, r):
    meta = REGISTRY[iso]
    n = r["n_vars"]
    sf = ", ".join(r["source_files"]) if r.get("source_files") else "—"

    if r["status"] == "NO_DOC":
        mig_avail  = "NO_DOC"
        time_avail = "NO_DOC"
        mig_var    = "—"
        mig_q      = "—"
        time_var   = "—"
        time_q     = "—"
        note = "No documentation files in country folder."

    elif r["status"] in ("NOT_DECODED", "POOR_LABELS"):
        reason = "PDF classified as bulletin — 0 variables extracted." if r.get("is_bulletin") else \
                 f"Decoder returned {n} variables but labels not descriptive (question numbers only)."
        mig_avail  = "NOT_DECODED"
        time_avail = "NOT_DECODED"
        mig_var = mig_q = time_var = time_q = "—"
        note = f"Source: {sf}. {reason} Cannot assess from decoded data alone."

    else:  # status == DECODED
        # Migration
        if r["mig"]:
            mig_avail = "FOUND"
            mig_var   = "; ".join(v[0] for v in r["mig"][:3])
            mig_q     = r["mig"][0][1] if r["mig"] else "—"
        else:
            mig_avail = "NOT_FOUND"
            mig_var   = "—"
            mig_q     = "—"

        # Time of residence
        if r["time"]:
            time_avail = "FOUND"
            time_var   = "; ".join(v[0] for v in r["time"][:3])
            time_q     = r["time"][0][1] if r["time"] else "—"
        else:
            time_avail = "NOT_FOUND"
            time_var   = "—"
            time_q     = "—"

        note = f"{n} variables decoded from {sf}."

    return (meta["name"], meta["survey"], meta["period"],
            mig_avail, mig_var, mig_q,
            time_avail, time_var, time_q,
            note)

ROWS = [build_row(iso, results[iso]) for iso in REGISTRY]

# ── Excel builder ─────────────────────────────────────────────────────────────
GREEN  = "C6EFCE"
YELLOW = "FFF2CC"
ORANGE = "FCE4D6"
GRAY   = "EDEDED"
BLUE_H = "1F4E79"

FILL = {
    "FOUND":       PatternFill("solid", fgColor=GREEN),
    "NOT_FOUND":   PatternFill("solid", fgColor=ORANGE),
    "NOT_DECODED": PatternFill("solid", fgColor=GRAY),
    "POOR_LABELS": PatternFill("solid", fgColor=GRAY),
    "NO_DOC":      PatternFill("solid", fgColor=GRAY),
}
LABEL = {
    "FOUND":       "Yes — found",
    "NOT_FOUND":   "Not found",
    "NOT_DECODED": "Not decodable",
    "POOR_LABELS": "Not decodable",
    "NO_DOC":      "No documentation",
}

def thin():
    s = Side(style="thin", color="BBBBBB")
    return Border(left=s, right=s, top=s, bottom=s)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Migration Availability"

# Row 1 — title
ws.merge_cells("A1:J1")
c = ws["A1"]
c.value = "Migration Variable Availability — LAC Household Surveys"
c.font = Font(bold=True, size=13, color="FFFFFF")
c.fill = PatternFill("solid", fgColor=BLUE_H)
c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 26

# Row 2 — data source note
ws.merge_cells("A2:J2")
c = ws["A2"]
c.value = ("Source: Decoded survey dictionaries only (data availability/decoded/*.json).  "
           "Variables not found in the decoded JSON are reported as 'Not found' or 'Not decodable' — "
           "absence here does not imply the survey lacks the concept.")
c.font = Font(italic=True, size=8, color="444444")
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
ws.row_dimensions[2].height = 24

# Row 3 — section headers
ws.merge_cells("A3:C3")
ws.merge_cells("D3:F3")
h1 = ws["D3"]
h1.value = "Identify migrant population"
h1.font = Font(bold=True, size=10, color="FFFFFF")
h1.fill = PatternFill("solid", fgColor="2E75B6")
h1.alignment = Alignment(horizontal="center", vertical="center")

ws.merge_cells("G3:I3")
h2 = ws["G3"]
h2.value = "5+ years in country"
h2.font = Font(bold=True, size=10, color="FFFFFF")
h2.fill = PatternFill("solid", fgColor="375623")
h2.alignment = Alignment(horizontal="center", vertical="center")

ws.merge_cells("J3:J3")
ws.row_dimensions[3].height = 18

# Row 4 — column headers
COLS = ["Country", "Survey", "Period",
        "Available?", "Variable", "Question wording",
        "Available?", "Variable", "Question wording",
        "Notes (decoder)"]
hfill = PatternFill("solid", fgColor="2F5496")
hfont = Font(bold=True, color="FFFFFF", size=9)
for ci, h in enumerate(COLS, 1):
    cell = ws.cell(row=4, column=ci, value=h)
    cell.fill = hfill; cell.font = hfont
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin()
ws.row_dimensions[4].height = 28

# Data rows
for ri, row in enumerate(ROWS, 5):
    (country, survey, period,
     mig_av, mig_var, mig_q,
     time_av, time_var, time_q,
     note) = row

    vals = [country, survey, period,
            LABEL[mig_av],  mig_var, mig_q,
            LABEL[time_av], time_var, time_q,
            note]

    for ci, val in enumerate(vals, 1):
        cell = ws.cell(row=ri, column=ci, value=val)
        cell.border = thin()
        cell.font = Font(size=9)
        cell.alignment = Alignment(vertical="center", wrap_text=True)

        if ci == 4:
            cell.fill = FILL[mig_av]
            cell.font = Font(bold=True, size=9)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        elif ci == 7:
            cell.fill = FILL[time_av]
            cell.font = Font(bold=True, size=9)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        elif ci == 1:
            cell.font = Font(bold=True, size=9)

        # alternate row shade
        if ri % 2 == 0 and ci not in (4, 7):
            if cell.fill.fgColor.rgb in ("00000000", "FFFFFFFF", ""):
                cell.fill = PatternFill("solid", fgColor="F7F7F7")

    ws.row_dimensions[ri].height = 38

# Legend
lr = len(ROWS) + 7
ws.cell(row=lr, column=1, value="Legend").font = Font(bold=True, size=9)
items = [
    ("Yes — found",      GREEN,  "Variable confirmed in the decoded JSON dictionary for this country"),
    ("Not found",        ORANGE, "Dictionary decoded successfully but no matching variable found (may still exist in survey)"),
    ("Not decodable",    GRAY,   "Decoder returned 0 variables or labels were not descriptive (PDF bulletin, question numbers only)"),
    ("No documentation", GRAY,   "No dictionary/questionnaire file found in the country folder"),
]
for i, (lbl, color, desc) in enumerate(items):
    r = lr + 1 + i
    c = ws.cell(row=r, column=1, value=lbl)
    c.fill = PatternFill("solid", fgColor=color)
    c.font = Font(bold=True, size=8); c.border = thin()
    dc = ws.cell(row=r, column=2, value=desc)
    dc.font = Font(size=8)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)

# Column widths
widths = [18, 9, 8, 16, 26, 42, 16, 26, 42, 52]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = "D5"

OUTPUT_DIR.mkdir(exist_ok=True)
out = OUTPUT_DIR / "migration_variable_availability_v2.xlsx"
wb.save(out)
print(f"\nSaved: {out}")
