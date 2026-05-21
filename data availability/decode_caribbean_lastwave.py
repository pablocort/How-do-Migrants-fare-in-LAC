"""
decode_caribbean_lastwave.py
============================
Decodes the last available wave for each Caribbean country.

Strategy:
  - Countries with no usable docs file: read .dta variable metadata via pyreadstat
    (variable names + labels + value codes — NO actual microdata is loaded)
  - DOM 2024t4: parse the Diccionario.xlsx using parse_xlsx
  - HTI 2016_2017: parse DHS7_Household_QRE PDF using parse_pdf

Saves results to decoded_ts/ in the same JSON format as scan_and_decode_network.py.

Usage:
  py decode_caribbean_lastwave.py
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_AVAIL_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_AVAIL_DIR / "decoded_ts"

try:
    import pyreadstat
    HAS_PYREADSTAT = True
except ImportError:
    HAS_PYREADSTAT = False
    print("ERROR: pyreadstat not installed. Run: pip install pyreadstat")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Countries to decode via .dta metadata
# ---------------------------------------------------------------------------

LAST_WAVES_DTA = {
    "BLZ": {
        "year": 2024, "period": "m9", "survey": "LFS",
        "dta": Path("Z:/survey/BLZ/LFS/2024/m9/data_merge/BLZ_2024m9.dta"),
    },
    "BRB": {
        "year": 2016, "period": "m1_m6", "survey": "CLFS",
        "dta": Path("Z:/survey/BRB/CLFS/2016/m1_m6/data_merge/BRB_2016m1_m6.dta"),
    },
    "GUY": {
        "year": 2021, "period": "t3", "survey": "LFS",
        "dta": Path("Z:/survey/GUY/LFS/2021/t3/data_merge/GUY_2021t3.dta"),
    },
    "JAM": {
        "year": 2020, "period": "m1", "survey": "LFS",
        "dta": Path("Z:/survey/JAM/LFS/2020/m1/data_orig/JAM_2020m1.dta"),
    },
    "SUR": {
        "year": 2022, "period": "a", "survey": "SLC",
        "dta": Path("Z:/survey/SUR/SLC/2022/a/data_merge/SUR_2022a.dta"),
    },
    "TTO": {
        "year": 2023, "period": "a", "survey": "CSSP",
        "dta": Path("Z:/survey/TTO/CSSP/2023/a/data_orig/Individuals_2023.dta"),
    },
}

# ---------------------------------------------------------------------------
# Countries to decode via docs file (XLSX or PDF)
# ---------------------------------------------------------------------------

LAST_WAVES_DOC = {
    "DOM": {
        "year": 2024, "period": "t4", "survey": "ENCFT",
        "doc": Path("Z:/survey/DOM/ENCFT/2024/t4/docs/Diccionario.xlsx"),
        "doc_type": "XLSX",
    },
    "HTI": {
        "year": 2017, "period": "m11_m4", "survey": "DHS",
        "doc": Path("Z:/survey/HTI/DHS/2016_2017/m11_m4/docs/DHS7_Household_QRE_EN_16Mar2017_DHSQ7.pdf"),
        "doc_type": "PDF",
    },
}

# ---------------------------------------------------------------------------
# Decode .dta metadata
# ---------------------------------------------------------------------------

def decode_dta(iso3: str, info: dict) -> None:
    dta_path = info["dta"]
    print(f"  {iso3}: reading metadata from {dta_path.name} ...", end=" ", flush=True)

    if not dta_path.exists():
        print(f"NOT FOUND at {dta_path}")
        return

    try:
        _, meta = pyreadstat.read_dta(str(dta_path), metadataonly=True)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    variables = []
    names  = meta.column_names or []
    labels = meta.column_labels or []
    # pad labels list if shorter than names
    labels = list(labels) + [""] * (len(names) - len(labels))

    for name, label in zip(names, labels):
        vvc = meta.variable_value_labels.get(name, {})
        variables.append({
            "name":        name,
            "label":       label or "",
            "type":        "DTA",
            "table":       "",
            "value_codes": {str(k): str(v) for k, v in vvc.items()},
        })

    out = {
        "iso3":         iso3,
        "survey":       info["survey"],
        "period":       info["period"],
        "year":         info["year"],
        "source_files": [dta_path.name + " (variable metadata — no microdata loaded)"],
        "doc_type":     "DTA_METADATA",
        "tables":       [],
        "variables":    variables,
        "decode_notes": [
            f"{len(variables)} variables extracted from .dta metadata using pyreadstat",
            f"Source: {dta_path}",
        ],
    }

    out_name = f"{iso3}_{info['year']}{info['period']}_dictionary.json"
    out_path = OUTPUT_DIR / out_name
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(variables)} vars → {out_name}")

# ---------------------------------------------------------------------------
# Decode docs file (XLSX or PDF)
# ---------------------------------------------------------------------------

def decode_doc(iso3: str, info: dict) -> None:
    doc_path = info["doc"]
    print(f"  {iso3}: parsing {doc_path.name} ({info['doc_type']}) ...", end=" ", flush=True)

    if not doc_path.exists():
        print(f"NOT FOUND at {doc_path}")
        return

    sys.path.insert(0, str(DATA_AVAIL_DIR))
    try:
        if info["doc_type"] in ("XLSX", "XLS"):
            from parsers.parse_xlsx import parse
        elif info["doc_type"] == "PDF":
            from parsers.parse_pdf import parse
        else:
            print(f"Unsupported doc type: {info['doc_type']}")
            return
        result = parse(doc_path)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    variables = result.get("variables", [])
    out = {
        "iso3":         iso3,
        "survey":       info["survey"],
        "period":       info["period"],
        "year":         info["year"],
        "source_files": [doc_path.name],
        "doc_type":     info["doc_type"],
        "tables":       result.get("tables", []),
        "variables":    variables,
        "decode_notes": result.get("decode_notes", []),
    }

    out_name = f"{iso3}_{info['year']}{info['period']}_dictionary.json"
    out_path = OUTPUT_DIR / out_name
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(variables)} vars → {out_name}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n── .dta metadata decoding ──────────────────────────────────")
    for iso3, info in LAST_WAVES_DTA.items():
        decode_dta(iso3, info)

    print("\n── docs file decoding ──────────────────────────────────────")
    for iso3, info in LAST_WAVES_DOC.items():
        decode_doc(iso3, info)

    print("\nDone. Run build_caribbean_timeseries_table.py to rebuild Excel.")
