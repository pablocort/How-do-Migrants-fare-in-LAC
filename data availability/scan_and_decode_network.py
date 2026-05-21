"""
scan_and_decode_network.py
===========================
Scans the IDB network share for all LAC countries/surveys (2015+),
picks the best available documentation file per year/period,
decodes it using the existing parsers, and saves the results to
decoded_ts/[ISO3]_[YEAR][PERIOD]_dictionary.json

Usage:
  python scan_and_decode_network.py                  # all countries
  python scan_and_decode_network.py --country COL    # one country
  python scan_and_decode_network.py --list           # show manifest only
  python scan_and_decode_network.py --force          # overwrite existing JSONs
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

NETWORK_BASE = Path("//sapidbshares.file.core.windows.net/idbshares/SURVEYS/survey")
DATA_AVAIL_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_AVAIL_DIR / "decoded_ts"

# ---------------------------------------------------------------------------
# Country → primary survey mapping (labor force / household survey, 2015+)
# ---------------------------------------------------------------------------

NETWORK_MAP = {
    "ARG": {"survey": "EPHC",  "name": "Argentina"},
    "BOL": {"survey": "ECH",   "name": "Bolivia"},
    "BRA": {"survey": "PNADC", "name": "Brazil"},
    "CHL": {"survey": "CASEN", "name": "Chile"},
    "COL": {"survey": "GEIH",  "name": "Colombia"},
    "CRI": {"survey": "ENAHO", "name": "Costa Rica"},
    "DOM": {"survey": "ENCFT", "name": "Dominican Rep."},
    "ECU": {"survey": "ENEMDU","name": "Ecuador"},
    "GTM": {"survey": "ENEIC", "name": "Guatemala"},
    "GUY": {"survey": "LFS",   "name": "Guyana"},
    "HND": {"survey": "EPHPM", "name": "Honduras"},
    "JAM": {"survey": "LFS",   "name": "Jamaica"},
    "MEX": {"survey": "ENOE",  "name": "Mexico"},
    "PER": {"survey": "ENAHO", "name": "Peru"},
    "PRY": {"survey": "EPH",   "name": "Paraguay"},
    "SLV": {"survey": "EHPM",  "name": "El Salvador"},
    "URY": {"survey": "ECH",   "name": "Uruguay"},
    "VEN": {"survey": "EHM",   "name": "Venezuela"},
    # Caribbean additions
    "BLZ": {"survey": "LFS",   "name": "Belize"},
    "BRB": {"survey": "CLFS",  "name": "Barbados"},
    "HTI": {"survey": "DHS",   "name": "Haiti"},
    "SUR": {"survey": "SLC",   "name": "Suriname"},
    "TTO": {"survey": "CSSP",  "name": "Trinidad & Tobago"},
}

START_YEAR = 2015

# Period preference when a year has multiple options (first match wins)
PERIOD_PREF = ["a", "t4", "t3", "t2", "t1",
               "m12", "m9", "m6", "m3",
               "s2", "s1"]

# ---------------------------------------------------------------------------
# File ranking: pick the best documentation file from a docs/ folder
# ---------------------------------------------------------------------------

def _rank_file(fname: str) -> int:
    """Lower rank = better. Returns 99 to skip."""
    n = fname.lower()
    ext = os.path.splitext(n)[1]

    is_dict_name = any(kw in n for kw in ("diccionario", "dictionary", "dicionario",
                                           "codebook", "libro_de_codigo", "libro de codigos"))
    is_quest_name = any(kw in n for kw in ("cuestionario", "formulario",
                                            "questionnaire", "formulaire"))
    is_ficha = any(kw in n for kw in ("ficha", "fichatecnica"))

    if ext in (".xlsx", ".xls"):
        if is_dict_name:
            return 1   # XLSX variable dictionary — best
        return 3       # generic XLSX
    if ext == ".ods":
        return 2       # ODS (ECU style)
    if ext == ".pdf":
        if is_dict_name:
            return 4   # PDF dictionary
        if is_quest_name:
            return 5   # questionnaire PDF
        if is_ficha:
            return 6   # technical fact-sheet
        return 10      # generic PDF (bulletin etc.) — lowest
    return 99          # skip everything else (zip, sav, etc.)


def pick_best_doc(docs_path: Path) -> tuple[Path | None, str]:
    """Return (best_file_path, doc_type_label) or (None, '')."""
    try:
        entries = list(docs_path.iterdir())
    except Exception:
        return None, ""

    ranked = []
    for e in entries:
        if e.is_file():
            r = _rank_file(e.name)
            if r < 99:
                ranked.append((r, e))
    if not ranked:
        return None, ""

    ranked.sort(key=lambda x: x[0])
    best_rank, best_file = ranked[0]
    type_labels = {1: "DICT_XLSX", 2: "ODS", 3: "XLSX", 4: "DICT_PDF",
                   5: "QUESTIONNAIRE_PDF", 6: "FICHA_PDF", 10: "PDF"}
    return best_file, type_labels.get(best_rank, "FILE")

# ---------------------------------------------------------------------------
# Period selection: pick preferred period for each year
# ---------------------------------------------------------------------------

def pick_period(year_path: Path) -> str | None:
    """
    Return the period subdirectory with the best documentation file.
    Prefers the period whose best doc has the lowest rank (DICT_XLSX wins over
    questionnaire PDF). Ties are broken by PERIOD_PREF order.
    Returns None if no period has any decodable file.
    """
    try:
        available = [d.name for d in year_path.iterdir() if d.is_dir()]
    except Exception:
        return None
    if not available:
        return None

    # Score each available period: (best_file_rank, pref_order)
    candidates = []
    for p in available:
        docs_path = year_path / p / "docs"
        best_file, _ = pick_best_doc(docs_path)
        if best_file is None:
            file_rank = 999
        else:
            file_rank = _rank_file(best_file.name)
        pref_order = PERIOD_PREF.index(p) if p in PERIOD_PREF else 99
        candidates.append((file_rank, pref_order, p))

    candidates.sort()
    best_file_rank, _, best_period = candidates[0]
    if best_file_rank >= 99:
        return None   # no decodable file in any period
    return best_period

# ---------------------------------------------------------------------------
# Manifest builder: list all (year, period, best_doc) for a country
# ---------------------------------------------------------------------------

def build_manifest(iso3: str, meta: dict) -> list[dict]:
    survey = meta["survey"]
    base = NETWORK_BASE / iso3 / survey
    if not base.exists():
        return []

    manifest = []
    try:
        year_dirs = sorted(
            [d for d in base.iterdir() if d.is_dir() and re.fullmatch(r"\d{4}", d.name)],
            key=lambda d: int(d.name)
        )
    except Exception:
        return []

    for yr_dir in year_dirs:
        year = int(yr_dir.name)
        if year < START_YEAR:
            continue

        period = pick_period(yr_dir)
        if period is None:
            continue

        docs_path = yr_dir / period / "docs"
        best_doc, doc_type = pick_best_doc(docs_path)
        if best_doc is None:
            continue

        manifest.append({
            "year":     year,
            "period":   period,
            "doc_path": str(best_doc),
            "doc_name": best_doc.name,
            "doc_type": doc_type,
        })
    return manifest

# ---------------------------------------------------------------------------
# Decode one file using the existing parsers
# ---------------------------------------------------------------------------

def decode_file(doc_path: Path, doc_type: str) -> dict:
    """Run appropriate parser and return partial result dict."""
    ext = doc_path.suffix.lower()
    try:
        if ext in (".xlsx", ".xls"):
            from parsers.parse_xlsx import parse as parse_xlsx
            return parse_xlsx(doc_path)
        elif ext == ".ods":
            from parsers.parse_ods import parse as parse_ods
            return parse_ods(doc_path)
        elif ext == ".pdf":
            from parsers.parse_pdf import parse as parse_pdf
            return parse_pdf(doc_path)
        else:
            return {"variables": [], "tables": [], "decode_notes": [f"Unsupported format: {ext}"]}
    except Exception as e:
        return {"variables": [], "tables": [], "decode_notes": [f"ERROR: {e}"]}

# ---------------------------------------------------------------------------
# Period normalizer: make a short key for the JSON filename
# ---------------------------------------------------------------------------

def period_key(period: str) -> str:
    """Shorten multi-month periods (m11_m12_m1 → a, t4_t3 → t4) for filenames."""
    if re.match(r"m\d{1,2}_m\d{1,2}_m\d{1,2}", period):
        return "a"
    if re.match(r"t\d_t\d", period):
        return period.split("_")[0]
    return period

# ---------------------------------------------------------------------------
# Main decode loop
# ---------------------------------------------------------------------------

def process_country(iso3: str, meta: dict, force: bool = False, list_only: bool = False) -> list[dict]:
    manifest = build_manifest(iso3, meta)
    if not manifest:
        print(f"  {iso3}: no data found on network share (2015+)")
        return []

    summary = []
    for entry in manifest:
        year    = entry["year"]
        period  = entry["period"]
        pkey    = period_key(period)
        out_name = f"{iso3}_{year}{pkey}_dictionary.json"
        out_path = OUTPUT_DIR / out_name
        status   = "EXISTS" if out_path.exists() else "NEW"

        if list_only:
            print(f"  {iso3} {year}/{period} [{entry['doc_type']}] {entry['doc_name']} → {out_name} ({status})")
            summary.append({**entry, "out_name": out_name, "status": status})
            continue

        if out_path.exists() and not force:
            print(f"  {iso3} {year}/{period} — skip (already decoded)")
            summary.append({**entry, "out_name": out_name, "status": "SKIPPED"})
            continue

        print(f"  {iso3} {year}/{period} [{entry['doc_type']}] decoding {entry['doc_name']} ...", end=" ", flush=True)
        result = decode_file(Path(entry["doc_path"]), entry["doc_type"])
        n = len(result.get("variables", []))

        full = {
            "iso3":         iso3,
            "survey":       meta["survey"],
            "period":       pkey,
            "year":         year,
            "source_files": [entry["doc_name"]],
            "doc_type":     entry["doc_type"],
            "tables":       result.get("tables", []),
            "variables":    result.get("variables", []),
            "decode_notes": result.get("decode_notes", []),
        }

        OUTPUT_DIR.mkdir(exist_ok=True)
        out_path.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"→ {n} vars saved to {out_name}")
        summary.append({**entry, "out_name": out_name, "status": "DECODED", "n_vars": n})

    return summary

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Scan network share and decode survey docs (2015+)")
    ap.add_argument("--country", help="Decode a single country (ISO3)")
    ap.add_argument("--list",    action="store_true", help="List manifest without decoding")
    ap.add_argument("--force",   action="store_true", help="Overwrite existing JSONs")
    args = ap.parse_args()

    if not NETWORK_BASE.exists():
        print(f"ERROR: network share not accessible: {NETWORK_BASE}")
        sys.exit(1)

    countries = {}
    if args.country:
        iso3 = args.country.upper()
        if iso3 not in NETWORK_MAP:
            print(f"ERROR: {iso3} not in NETWORK_MAP. Available: {', '.join(NETWORK_MAP)}")
            sys.exit(1)
        countries = {iso3: NETWORK_MAP[iso3]}
    else:
        countries = NETWORK_MAP

    all_summary = {}
    for iso3, meta in countries.items():
        print(f"\n{'='*60}")
        print(f"{iso3} — {meta['name']} ({meta['survey']})")
        summary = process_country(iso3, meta, force=args.force, list_only=args.list)
        all_summary[iso3] = summary

    if not args.list:
        print(f"\n{'='*60}")
        print("Done. JSONs saved to:", OUTPUT_DIR)
        total = sum(len(v) for v in all_summary.values())
        decoded = sum(
            sum(1 for e in v if e.get("status") == "DECODED")
            for v in all_summary.values()
        )
        print(f"Total waves found: {total}  |  Newly decoded: {decoded}")

if __name__ == "__main__":
    main()
