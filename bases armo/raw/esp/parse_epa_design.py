#!/usr/bin/env python3
"""
parse_epa_design.py
Reads INE EPA design Excel files, extracts variable column specifications,
compares across schema versions (2018-2020 vs 2021+), and writes
epa_variable_dictionary.md with all positions and HDMF relevance flags.
"""

import sys
import re
from pathlib import Path

import pandas as pd

ESP_RAW = Path(__file__).parent

def _glob_first(folder: Path, glob_pattern: str) -> Path:
    """Return first file matching glob_pattern in folder, or a non-existent sentinel."""
    if not folder.exists():
        return folder / glob_pattern
    matches = sorted(folder.glob(glob_pattern))
    return matches[0] if matches else (folder / glob_pattern)


DESIGN_FILES = {
    "2018": _glob_first(ESP_RAW / "2018", "*pet-2014-2018*"),
    "2019": _glob_first(ESP_RAW / "2019", "*pet-2014-2019*"),
    "2020": _glob_first(ESP_RAW / "2020", "*pet-2014-2020*"),
    "2021": _glob_first(ESP_RAW / "2021", "*EPA-TRIM-2021*"),
    "2023": _glob_first(ESP_RAW / "ficheros" / "56748_documents", "*EPATRIM2023*"),
    "2025": _glob_first(ESP_RAW / "2025", "*EPA-TRIM-2021*"),
    "ref":  ESP_RAW / "archive" / "dr_EPA_2021.xlsx",
}

# HDMF-relevant variable keywords (partial match on name or description)
HDMF_KEYWORDS = {
    "EDAD": "edad_ci (age)",
    "SEXO": "sexo_ci (sex)",
    "PARH": "relacion_ci (household relationship)",
    "NFOR": "edu_hdmf / aedu_ci (education level)",
    "ESTU": "edu_hdmf (level of studies)",
    "SITU": "condocup_ci (employment status)",
    "OCUP": "employment / occupation",
    "HORAS": "horaspri_ci / horastot_ci (hours worked)",
    "DUCON": "tipocontrato_ci (contract type)",
    "COTI": "cotizando_ci (social security contribution)",
    "NACIO": "mig_pais_ci (nationality / birth country)",
    "PAISE": "mig_pais_ci (country of birth — migration)",
    "NACOC": "migrante_ci (born in Spain or abroad)",
    "PROCE": "mig_pais_ci (country of origin)",
    "LLEGA": "migrantiguo5_ci (year of arrival)",
    "ANOLL": "migrantiguo5_ci (year of arrival)",
    "FACTP": "factor_ci / factor_ch (expansion weight)",
    "NVIVI": "idh_ch (household ID component)",
    "NHOG":  "idh_ch (household ID component)",
    "NPERSONA": "idp_ci (person ID)",
    "CICLO": "survey cycle (identifier)",
    "PROV":  "region / province",
}


def normalise_col(c):
    if c is None:
        return ""
    return str(c).strip().upper().replace("\n", " ").replace("  ", " ")


def find_columns(df):
    """
    Auto-detect which columns hold variable name, start pos, end pos, type, description.
    Returns a dict with keys: name, start, end, length, type, desc (or None if not found).
    """
    cols = {normalise_col(c): c for c in df.columns}

    def pick(*candidates):
        for cand in candidates:
            for norm, orig in cols.items():
                if cand in norm:
                    return orig
        return None

    return {
        "name":   pick("NOMBRE", "CAMPO", "VARIABLE", "DENOMINACION", "DENOMINACIÓ"),
        "start":  pick("INICIO", "POSICIÓN INICIAL", "POSICION INICIAL", "POS. INI", "INI"),
        "end":    pick("FIN", "POSICIÓN FINAL", "POSICION FINAL", "POS. FIN", "FINAL"),
        "length": pick("LONGITUD", "LONG", "ANCHURA", "ANCHO"),
        "type":   pick("TIPO", "TYPE", "FORMAT"),
        "desc":   pick("DESCRIPCION", "DESCRIPCIÓN", "ETIQUETA", "CONTENIDO", "LABEL"),
    }


def _long_path(p: Path) -> Path:
    """Return a Windows extended-length path (\\?\) to bypass MAX_PATH=260."""
    abs_str = str(p.absolute())
    if abs_str.startswith("\\\\?\\"):
        return p
    return Path("\\\\?\\" + abs_str)


def _file_readable(p: Path) -> bool:
    """Check if file is readable, handling long paths on Windows."""
    try:
        return p.exists() or _long_path(p).exists()
    except Exception:
        return False


def read_design(path: Path, label: str):
    """
    Read one design Excel file and return a DataFrame with standardised columns:
    var_name, start, end, length, type_, desc.
    """
    if not _file_readable(path):
        print(f"  [SKIP] {label}: file not found — {path.name}")
        return None

    # Use extended path prefix to bypass Windows MAX_PATH=260
    open_path = _long_path(path) if not path.exists() else path
    print(f"  Reading {label}: {path.name}")
    try:
        xl = pd.ExcelFile(open_path, engine="xlrd" if path.suffix == ".xls" else "openpyxl")
    except Exception as e:
        print(f"  [ERROR] Could not open {path.name}: {e}")
        return None

    print(f"    Sheets: {xl.sheet_names}")

    best_df = None
    best_score = -1

    keywords = ["NOMBRE", "CAMPO", "VARIABLE", "INICIO", "INI", "POSICI",
                "FIN", "LONG", "TIPO", "DESCRIPCI", "ETIQUETA"]

    # Strongly prefer sheets whose name contains "diseño de registro"
    def sheet_priority(s):
        sl = s.lower()
        if "dise" in sl and "regist" in sl:
            return 0
        if "dise" in sl:
            return 1
        if "regist" in sl:
            return 2
        return 9

    sheet_order = sorted(xl.sheet_names, key=sheet_priority)

    for sheet in sheet_order:
        try:
            df = xl.parse(sheet, header=None)
        except Exception:
            continue

        # Try to find a header row in the first 20 rows
        for hrow in range(min(20, len(df))):
            header = [normalise_col(v) for v in df.iloc[hrow]]
            score = sum(1 for k in keywords if any(k in h for h in header))
            # Give a big bonus to high-priority sheets so they win over
            # high-scoring low-priority sheets
            priority_bonus = (9 - sheet_priority(sheet)) * 10
            adjusted = score + priority_bonus
            if adjusted > best_score:
                best_score = adjusted
                best_sheet = sheet
                best_hrow = hrow

    if best_score < 2:
        print(f"    [WARN] Could not identify a variable dictionary sheet (best score={best_score})")
        # Dump first sheet preview for debugging
        df0 = xl.parse(xl.sheet_names[0], header=None)
        print("    Preview (first 5 rows, first 8 cols):")
        print(df0.iloc[:5, :8].to_string())
        return None

    df = xl.parse(best_sheet, header=best_hrow)
    df.columns = [normalise_col(c) for c in df.columns]
    df = df.dropna(how="all")

    col_map = find_columns(df)
    print(f"    Sheet '{best_sheet}', header row {best_hrow}, detected cols: {col_map}")

    # Build standardised output
    rows = []
    for _, row in df.iterrows():
        name = str(row.get(col_map["name"], "")).strip() if col_map["name"] else ""
        if not name or name.upper() in ("NAN", "NOMBRE", "CAMPO", "VARIABLE", ""):
            continue
        start  = row.get(col_map["start"],  None) if col_map["start"]  else None
        end    = row.get(col_map["end"],    None) if col_map["end"]    else None
        length = row.get(col_map["length"], None) if col_map["length"] else None
        type_  = str(row.get(col_map["type"], "")).strip() if col_map["type"] else ""
        desc   = str(row.get(col_map["desc"], "")).strip() if col_map["desc"] else ""

        try:
            start = int(float(start)) if start is not None and str(start).strip() not in ("", "nan") else None
        except Exception:
            start = None
        try:
            end = int(float(end)) if end is not None and str(end).strip() not in ("", "nan") else None
        except Exception:
            end = None
        try:
            length = int(float(length)) if length is not None and str(length).strip() not in ("", "nan") else None
        except Exception:
            length = None

        # Derive missing positions from the two available values
        if end is None and start is not None and length is not None:
            end = start + length - 1
        if start is None and end is not None and length is not None:
            start = end - length + 1
        if length is None and start is not None and end is not None:
            length = end - start + 1

        rows.append({
            "var_name": name.upper(),
            "start": start,
            "end": end,
            "length": length,
            "type_": type_.upper()[:1] if type_ else "",
            "desc": desc[:120],
        })

    out = pd.DataFrame(rows).drop_duplicates(subset=["var_name"])
    print(f"    Extracted {len(out)} variables")
    return out


def hdmf_flag(var_name, desc):
    name_upper = var_name.upper()
    desc_upper = desc.upper()
    for kw, label in HDMF_KEYWORDS.items():
        if kw in name_upper or kw in desc_upper:
            return label
    return ""


def compare_schemas(schemas: dict):
    """
    Given dict {label: DataFrame}, return a comparison DataFrame showing
    start/end for each variable across all schema versions.
    """
    all_vars = set()
    for df in schemas.values():
        if df is not None:
            all_vars.update(df["var_name"].tolist())
    all_vars = sorted(all_vars)

    rows = []
    for var in all_vars:
        row = {"var_name": var}
        starts, ends = [], []
        for label, df in schemas.items():
            if df is None:
                row[f"{label}_start"] = "N/A"
                row[f"{label}_end"]   = "N/A"
                continue
            match = df[df["var_name"] == var]
            if match.empty:
                row[f"{label}_start"] = "absent"
                row[f"{label}_end"]   = "absent"
            else:
                s = match.iloc[0]["start"]
                e = match.iloc[0]["end"]
                def _safe_int(v):
                    try:
                        return int(v) if v is not None and str(v) not in ("", "nan", "None") else "?"
                    except Exception:
                        return "?"
                s_int = _safe_int(s)
                e_int = _safe_int(e)
                row[f"{label}_start"] = s_int
                row[f"{label}_end"]   = e_int
                if s_int != "?":
                    starts.append(s_int)
                if e_int != "?":
                    ends.append(e_int)
        # Flag if positions differ across schema versions
        row["position_break"] = (
            "YES" if (len(set(str(x) for x in starts)) > 1 or
                      len(set(str(x) for x in ends))   > 1) else ""
        )
        rows.append(row)
    return pd.DataFrame(rows)


def write_dictionary(schemas: dict, comparison: pd.DataFrame, out_path: Path):
    lines = [
        "# EPA Variable Dictionary — INE Spain (2018–2025)",
        "",
        "Auto-generated by `parse_epa_design.py`. Do not edit manually.",
        "",
        "## Schema versions read",
        "",
    ]
    for label, df in schemas.items():
        n = len(df) if df is not None else 0
        lines.append(f"- **{label}**: {n} variables extracted")
    lines += ["", "---", ""]

    # --- Position-break warnings ---
    breaks = comparison[comparison["position_break"] == "YES"]
    if breaks.empty:
        lines.append("**No position breaks detected across schema versions.** All variables have consistent column positions.\n")
    else:
        lines.append(f"## Position breaks detected ({len(breaks)} variables)\n")
        lines.append("| Variable | Notes |")
        lines.append("|----------|-------|")
        for _, row in breaks.iterrows():
            lines.append(f"| {row['var_name']} | positions differ — check design docs |")
        lines.append("")

    lines += ["---", "", "## Full variable dictionary", ""]

    # Use the most recent complete schema as the reference
    ref_label = None
    ref_df = None
    for label in ["2025", "2023", "2021", "ref", "2020", "2019", "2018"]:
        if label in schemas and schemas[label] is not None and len(schemas[label]) > 0:
            ref_label = label
            ref_df = schemas[label]
            break

    if ref_df is None:
        lines.append("*No variable data extracted — check design file parsing.*")
    else:
        lines.append(f"Reference schema: **{ref_label}**")
        lines.append("")
        lines.append("| Variable | Start | End | Len | Type | HDMF target | Description |")
        lines.append("|----------|-------|-----|-----|------|-------------|-------------|")
        for _, row in ref_df.sort_values("start", na_position="last").iterrows():
            flag = hdmf_flag(row["var_name"], row["desc"])
            hdmf_cell = f"**{flag}**" if flag else ""
            lines.append(
                f"| {row['var_name']} "
                f"| {row['start'] if row['start'] is not None else '?'} "
                f"| {row['end']   if row['end']   is not None else '?'} "
                f"| {row['length'] if row['length'] is not None else '?'} "
                f"| {row['type_']} "
                f"| {hdmf_cell} "
                f"| {row['desc']} |"
            )

    lines += ["", "---", ""]

    # --- Cross-version comparison for HDMF-relevant variables ---
    lines.append("## Cross-version positions for HDMF-relevant variables\n")
    hdmf_vars = [
        r["var_name"] for _, r in comparison.iterrows()
        if hdmf_flag(r["var_name"], "") != ""
    ]
    if not hdmf_vars:
        lines.append("*No HDMF-relevant variables found (check keyword list in parse_epa_design.py).*\n")
    else:
        schema_labels = [k for k in schemas.keys()]
        header = "| Variable | " + " | ".join(f"{l} start–end" for l in schema_labels) + " | Break? | HDMF target |"
        sep    = "|----------|" + "|".join(["------"] * len(schema_labels)) + "|--------|-------------|"
        lines.append(header)
        lines.append(sep)
        for var in hdmf_vars:
            row = comparison[comparison["var_name"] == var]
            if row.empty:
                continue
            row = row.iloc[0]
            cells = []
            for label in schema_labels:
                s = row.get(f"{label}_start", "?")
                e = row.get(f"{label}_end",   "?")
                cells.append(f"{s}–{e}")
            flag = hdmf_flag(var, "")
            lines.append(f"| {var} | " + " | ".join(cells) + f" | {row['position_break']} | {flag} |")

    lines += ["", "---", ""]
    lines.append("*Generated by `parse_epa_design.py`*")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nDictionary written to: {out_path}")


def main():
    print("=" * 60)
    print("EPA Design Parser — extracting variable column specs")
    print("=" * 60)

    schemas = {}
    for label, path in DESIGN_FILES.items():
        print(f"\n[{label}]")
        schemas[label] = read_design(path, label)

    print("\n" + "=" * 60)
    print("Comparing positions across schema versions...")
    comparison = compare_schemas(schemas)

    breaks = comparison[comparison["position_break"] == "YES"]
    print(f"Position breaks detected: {len(breaks)}")
    if not breaks.empty:
        print(breaks[["var_name"]].to_string(index=False))

    out_path = ESP_RAW / "epa_variable_dictionary.md"
    write_dictionary(schemas, comparison, out_path)

    # Also save raw comparison as CSV for reference
    csv_path = ESP_RAW / "epa_schema_comparison.csv"
    comparison.to_csv(csv_path, index=False)
    print(f"Schema comparison CSV: {csv_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
