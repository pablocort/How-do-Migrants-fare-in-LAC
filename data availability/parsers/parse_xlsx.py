"""
XLSX / XLS parser for HDMF survey dictionaries.

Supports five distinct column layouts found across LAC surveys:
  COL_GEIH   — 10-col hierarchical (Colombia GEIH)
  DOM_ENFT   — long-format with value codes per row (Dominican Republic)
  HND_EPHPM  — two-sheet SPSS-style Variables + Valores (Honduras)
  GTM_ENEIC  — minimal 4-col (Guatemala)
  BRA_PNADC  — fixed-width record layout in XLS (Brazil PNADC)
  UNKNOWN    — best-effort heuristic fallback
"""

import re
import unicodedata
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# Accent stripping helper
# ---------------------------------------------------------------------------

def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _norm(s) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    if not isinstance(s, str):
        return ""
    return _strip_accents(s).lower().strip()


# ---------------------------------------------------------------------------
# Column-role mapper
# ---------------------------------------------------------------------------

def _normalize_col_map(columns: list[str], keywords: dict[str, list[str]]) -> dict[str, str | None]:
    """
    Map abstract roles to actual column names via substring matching.

    keywords = {"name": ["variable", "nombre"], "label": ["etiqueta", "descripcion"]}
    Returns {"name": "Nombre de la variable", "label": "Etiqueta", ...}
    Unmatched roles → None.
    """
    normed = {_norm(c): c for c in columns}
    result = {}
    for role, kws in keywords.items():
        result[role] = None
        for kw in kws:
            for normed_col, orig_col in normed.items():
                if kw in normed_col:
                    result[role] = orig_col
                    break
            if result[role] is not None:
                break
    return result


# ---------------------------------------------------------------------------
# Layout detection
# ---------------------------------------------------------------------------

def detect_layout(columns: list[str], all_sheet_names: list[str] | None = None) -> str:
    """
    Score a sheet's column headers against known layout signatures.
    Returns layout key or "UNKNOWN".
    """
    normed_cols = [_norm(c) for c in columns]
    col_set = set(normed_cols)
    n = len(columns)

    def has(kw):
        return any(kw in c for c in normed_cols)

    def has_all(*kws):
        return all(has(k) for k in kws)

    # BRA_PNADC — fixed-width record format (Portuguese)
    if has_all("posic", "quesito") and n <= 10:
        return "BRA_PNADC"

    # DOM_ENFT — long-format with CAMPO + VALOR + DESCRIPCION
    if has_all("campo", "valor", "descripcion") and n <= 12:
        return "DOM_ENFT"

    # COL_GEIH — 10-col hierarchical with tabla + variable + descripcion
    col_str = " ".join(normed_cols)
    if (("nombre" in col_str and "variable" in col_str) or
            has("id variable") or has("nombre variable")) and has("descripcion") and n >= 5:
        return "COL_GEIH"

    # GTM_ENEIC — minimal: Variable + Etiqueta + Nivel
    if has_all("variable", "etiqueta") and (has("nivel") or has("medicion")) and n <= 7:
        return "GTM_ENEIC"

    # HND_EPHPM — detected at file level (two sheets), not per-sheet
    # But if we see a single sheet with etiqueta + tipo + ancho, flag it
    if has_all("etiqueta", "tipo") and (has("ancho") or has("posicion") or has("formato")):
        return "HND_EPHPM_VARS"

    if has_all("valor", "etiqueta") and n <= 6 and not has("campo"):
        return "HND_EPHPM_VALS"

    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Layout-specific extractors
# ---------------------------------------------------------------------------

def extract_col_geih(df: pd.DataFrame, sheet_name: str) -> tuple[list[dict], list[str]]:
    """
    10-col hierarchical layout (Colombia GEIH).
    Table context is carried by rows where the 'tabla' column is filled
    and the variable column is empty.
    """
    notes = [f"Sheet '{sheet_name}': COL_GEIH layout, {len(df)} rows"]
    col_map = _normalize_col_map(
        df.columns.tolist(),
        {
            "table": ["nombre tabla", "nombre de la tabla", "tabla"],
            "name": ["nombre variable", "nombre de la variable", "nombre_variable", "id variable"],
            "label": ["descripcion de la variable", "descripcion variable", "descripcion"],
            "type": ["tipo de dato", "tipo"],
        }
    )

    variables = []
    current_table = sheet_name

    for _, row in df.iterrows():
        # Track table context
        if col_map["table"]:
            tval = str(row.get(col_map["table"], "")).strip()
            if tval and tval.lower() not in ("nan", "none", ""):
                current_table = tval

        name_col = col_map["name"]
        if not name_col:
            continue
        name = str(row.get(name_col, "")).strip()
        if not name or name.lower() in ("nan", "none", ""):
            continue

        label = ""
        if col_map["label"]:
            label = str(row.get(col_map["label"], "")).strip()
            label = "" if label.lower() in ("nan", "none") else label

        dtype = ""
        if col_map["type"]:
            dtype = str(row.get(col_map["type"], "")).strip()
            dtype = "" if dtype.lower() in ("nan", "none") else dtype

        variables.append({
            "name": name,
            "label": label,
            "type": dtype,
            "table": current_table,
            "value_codes": {},
        })

    notes.append(f"  → {len(variables)} variables extracted")
    return variables, notes


def extract_dom_enft(df: pd.DataFrame, sheet_name: str) -> tuple[list[dict], list[str]]:
    """
    Long-format layout (Dominican Republic).
    Each CAMPO has multiple rows — one per VALOR/DESCRIPCION pair.
    """
    notes = [f"Sheet '{sheet_name}': DOM_ENFT layout, {len(df)} rows"]
    col_map = _normalize_col_map(
        df.columns.tolist(),
        {
            "name": ["campo"],
            "label": ["texto"],
            "table": ["seccion", "des_seccion"],
            "value": ["valor"],
            "value_label": ["descripcion"],
        }
    )

    if not col_map["name"]:
        notes.append("  WARNING: 'campo' column not found — skipping sheet")
        return [], notes

    variables = []
    seen = {}  # name → index in variables list

    for _, row in df.iterrows():
        name = str(row.get(col_map["name"], "")).strip()
        if not name or name.lower() in ("nan", "none", ""):
            continue

        if name not in seen:
            label = ""
            if col_map["label"]:
                label = str(row.get(col_map["label"], "")).strip()
                label = "" if label.lower() in ("nan", "none") else label

            table = sheet_name
            if col_map["table"]:
                tval = str(row.get(col_map["table"], "")).strip()
                if tval and tval.lower() not in ("nan", "none", ""):
                    table = tval

            variables.append({
                "name": name,
                "label": label,
                "type": "",
                "table": table,
                "value_codes": {},
            })
            seen[name] = len(variables) - 1

        idx = seen[name]
        if col_map["value"] and col_map["value_label"]:
            code = row.get(col_map["value"], None)
            desc = row.get(col_map["value_label"], None)
            if pd.notna(code) and pd.notna(desc):
                code_str = str(int(code)) if isinstance(code, float) and code == int(code) else str(code)
                variables[idx]["value_codes"][code_str] = str(desc).strip()

    notes.append(f"  → {len(variables)} variables extracted")
    return variables, notes


def extract_hnd_ephpm(vars_df: pd.DataFrame, vals_df: pd.DataFrame) -> tuple[list[dict], list[str]]:
    """
    Two-sheet SPSS layout (Honduras EPHPM).
    vars_df: Variables sheet; vals_df: Valores sheet.
    """
    notes = ["HND_EPHPM layout: two-sheet SPSS style"]

    var_col_map = _normalize_col_map(
        vars_df.columns.tolist(),
        {
            "name": ["variable"],
            "label": ["etiqueta"],
            "type": ["tipo", "nivel"],
            "width": ["ancho"],
        }
    )
    val_col_map = _normalize_col_map(
        vals_df.columns.tolist(),
        {
            "name": ["variable"],
            "value": ["valor", "codigo"],
            "value_label": ["etiqueta", "descripcion"],
        }
    )

    # Build value_codes lookup
    value_lookup: dict[str, dict] = {}
    if val_col_map["name"] and val_col_map["value"] and val_col_map["value_label"]:
        for _, row in vals_df.iterrows():
            var_name = str(row.get(val_col_map["name"], "")).strip()
            code = row.get(val_col_map["value"], None)
            lbl = row.get(val_col_map["value_label"], None)
            if var_name and pd.notna(code) and pd.notna(lbl):
                code_str = str(int(code)) if isinstance(code, float) and code == int(code) else str(code)
                value_lookup.setdefault(var_name, {})[code_str] = str(lbl).strip()

    variables = []
    if not var_col_map["name"]:
        notes.append("  WARNING: variable name column not found in Variables sheet")
        return variables, notes

    for _, row in vars_df.iterrows():
        name = str(row.get(var_col_map["name"], "")).strip()
        if not name or name.lower() in ("nan", "none", ""):
            continue

        label = ""
        if var_col_map["label"]:
            label = str(row.get(var_col_map["label"], "")).strip()
            label = "" if label.lower() in ("nan", "none") else label

        dtype = ""
        if var_col_map["type"]:
            dtype = str(row.get(var_col_map["type"], "")).strip()
            dtype = "" if dtype.lower() in ("nan", "none") else dtype

        variables.append({
            "name": name,
            "label": label,
            "type": dtype,
            "table": "main",
            "value_codes": value_lookup.get(name, {}),
        })

    notes.append(f"  → {len(variables)} variables, {len(value_lookup)} with value codes")
    return variables, notes


def extract_gtm_eneic(df: pd.DataFrame, sheet_name: str) -> tuple[list[dict], list[str]]:
    """
    Minimal 4-col layout (Guatemala ENEIC).
    Variable, Posición, Etiqueta, Nivel de medición.
    """
    notes = [f"Sheet '{sheet_name}': GTM_ENEIC layout, {len(df)} rows"]
    col_map = _normalize_col_map(
        df.columns.tolist(),
        {
            "name": ["variable"],
            "label": ["etiqueta"],
            "level": ["nivel", "medicion"],
        }
    )

    variables = []
    for _, row in df.iterrows():
        if not col_map["name"]:
            break
        name = str(row.get(col_map["name"], "")).strip()
        if not name or name.lower() in ("nan", "none", ""):
            continue

        label = ""
        if col_map["label"]:
            label = str(row.get(col_map["label"], "")).strip()
            label = "" if label.lower() in ("nan", "none") else label

        nivel = ""
        if col_map["level"]:
            nivel = str(row.get(col_map["level"], "")).strip()

        # Derive type from nivel
        dtype = "STRING" if "nominal" in _norm(nivel) else "NUMBER"

        variables.append({
            "name": name,
            "label": label,
            "type": dtype,
            "table": sheet_name,
            "value_codes": {},
        })

    notes.append(f"  → {len(variables)} variables extracted")
    return variables, notes


def extract_bra_pnadc(df: pd.DataFrame, sheet_name: str) -> tuple[list[dict], list[str]]:
    """
    Fixed-width record layout (Brazil PNADC XLS).
    Columns: Posição inicial, Tamanho, Código da variável, Quesito, Categorias.
    Categorias contains multi-line text with "code - label" pairs.
    """
    notes = [f"Sheet '{sheet_name}': BRA_PNADC layout, {len(df)} rows"]
    col_map = _normalize_col_map(
        df.columns.tolist(),
        {
            "name": ["codigo", "cod"],
            "label": ["quesito", "descricao", "descri"],
            "categories": ["categori"],
        }
    )

    # Fallback: if no 'codigo' col, try positional
    if not col_map["name"] and len(df.columns) >= 3:
        col_map["name"] = df.columns[2]
    if not col_map["label"] and len(df.columns) >= 5:
        col_map["label"] = df.columns[4]
    if not col_map["categories"] and len(df.columns) >= 7:
        col_map["categories"] = df.columns[6]

    variables = []
    for _, row in df.iterrows():
        name_val = row.get(col_map["name"]) if col_map["name"] else None
        name = str(name_val).strip() if pd.notna(name_val) else ""
        if not name or name.lower() in ("nan", "none", "") or not re.match(r"[A-Za-z]", name):
            continue

        label = ""
        if col_map["label"]:
            lv = row.get(col_map["label"])
            label = str(lv).strip() if pd.notna(lv) else ""
            label = "" if label.lower() in ("nan", "none") else label

        value_codes = {}
        if col_map["categories"]:
            cats_raw = row.get(col_map["categories"])
            if pd.notna(cats_raw):
                cats_text = str(cats_raw)
                for line in re.split(r"[\n\r]+", cats_text):
                    m = re.match(r"^\s*(\d+)\s*[-–]\s*(.+)$", line.strip())
                    if m:
                        value_codes[m.group(1)] = m.group(2).strip()

        variables.append({
            "name": name,
            "label": label,
            "type": "NUMBER",
            "table": sheet_name,
            "value_codes": value_codes,
        })

    notes.append(f"  → {len(variables)} variables extracted")
    return variables, notes


def extract_unknown_layout(df: pd.DataFrame, sheet_name: str) -> tuple[list[dict], list[str]]:
    """
    Heuristic best-effort extraction for unrecognized layouts.
    Tries to identify a variable-name column (short cells, high cardinality)
    and a label column (longer cells).
    """
    notes = [f"Sheet '{sheet_name}': UNKNOWN layout — best-effort extraction"]

    if df.empty or len(df.columns) < 2:
        return [], notes + ["  No extractable data found"]

    # Score each column as a candidate for "variable name"
    best_name_col = None
    best_name_score = -1
    for col in df.columns:
        vals = df[col].dropna().astype(str)
        if len(vals) == 0:
            continue
        avg_len = vals.str.len().mean()
        n_unique = vals.nunique()
        # Good variable name column: short values, many unique values
        score = n_unique / max(avg_len, 1)
        if score > best_name_score:
            best_name_score = score
            best_name_col = col

    # Label column: the column with longest average cell length (different from name col)
    best_label_col = None
    best_label_len = 0
    for col in df.columns:
        if col == best_name_col:
            continue
        vals = df[col].dropna().astype(str)
        if len(vals) == 0:
            continue
        avg_len = vals.str.len().mean()
        if avg_len > best_label_len:
            best_label_len = avg_len
            best_label_col = col

    variables = []
    for _, row in df.iterrows():
        name = str(row.get(best_name_col, "")).strip()
        if not name or name.lower() in ("nan", "none", ""):
            continue
        label = ""
        if best_label_col:
            label = str(row.get(best_label_col, "")).strip()
            label = "" if label.lower() in ("nan", "none") else label
        variables.append({
            "name": name,
            "label": label,
            "type": "",
            "table": sheet_name,
            "value_codes": {},
        })

    notes.append(f"  → {len(variables)} variables (best-effort — verify manually)")
    return variables, notes


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def parse(file_path: Path) -> dict:
    """
    Parse an XLSX or XLS file. Returns a partial result dict:
      {"variables": [...], "tables": [...], "decode_notes": [...]}
    """
    suffix = file_path.suffix.lower()
    engine = "openpyxl" if suffix == ".xlsx" else "xlrd"

    try:
        sheets: dict[str, pd.DataFrame] = pd.read_excel(
            file_path, sheet_name=None, header=None, engine=engine, dtype=str
        )
    except Exception as e:
        return {
            "variables": [],
            "tables": [],
            "decode_notes": [f"ERROR reading {file_path.name}: {e}"],
        }

    all_variables = []
    all_tables = []
    all_notes = [f"Source: {file_path.name} ({len(sheets)} sheet(s))"]

    sheet_names = list(sheets.keys())

    # Detect HND_EPHPM two-sheet pattern at file level
    vars_sheet = None
    vals_sheet = None
    for sname, sdf in sheets.items():
        # Find header row (first row with multiple non-null cells)
        header_row = _find_header_row(sdf)
        if header_row is None:
            continue
        sdf_clean = sdf.iloc[header_row:].copy()
        raw_cols = sdf_clean.iloc[0].astype(str).tolist()
        seen_hnd: dict[str, int] = {}
        deduped_hnd = []
        for c in raw_cols:
            if c in seen_hnd:
                seen_hnd[c] += 1
                deduped_hnd.append(f"{c}.{seen_hnd[c]}")
            else:
                seen_hnd[c] = 0
                deduped_hnd.append(c)
        sdf_clean.columns = deduped_hnd
        sdf_clean = sdf_clean.iloc[1:].reset_index(drop=True)
        layout = detect_layout(sdf_clean.columns.tolist(), sheet_names)
        if layout == "HND_EPHPM_VARS":
            vars_sheet = (sname, sdf_clean)
        elif layout == "HND_EPHPM_VALS":
            vals_sheet = (sname, sdf_clean)

    if vars_sheet and vals_sheet:
        vars_df, vals_df = vars_sheet[1], vals_sheet[1]
        variables, notes = extract_hnd_ephpm(vars_df, vals_df)
        all_variables.extend(variables)
        all_notes.extend(notes)
        all_tables = list({v["table"] for v in variables})
        return {"variables": all_variables, "tables": all_tables, "decode_notes": all_notes}

    # Process each sheet independently
    for sname, sdf in sheets.items():
        # Skip sheets that are purely instructional (no variable data)
        sname_n = _norm(sname)
        skip_keywords = ["instruc", "readme", "template"]
        # "plantilla" alone is a template; "plantilla diccionario" or "plantilla datos" is data
        is_plain_plantilla = "plantilla" in sname_n and not any(
            w in sname_n for w in ["diccionario", "datos", "variable"]
        )
        if any(kw in sname_n for kw in skip_keywords) or is_plain_plantilla:
            all_notes.append(f"Skipped sheet '{sname}' (instructions/template)")
            continue

        header_row = _find_header_row(sdf)
        if header_row is None:
            all_notes.append(f"Skipped sheet '{sname}' (no header row found)")
            continue

        sdf_clean = sdf.iloc[header_row:].copy()
        raw_cols = sdf_clean.iloc[0].astype(str).tolist()
        # Deduplicate column names (avoids df[col] returning a DataFrame)
        seen: dict[str, int] = {}
        deduped = []
        for c in raw_cols:
            if c in seen:
                seen[c] += 1
                deduped.append(f"{c}.{seen[c]}")
            else:
                seen[c] = 0
                deduped.append(c)
        sdf_clean.columns = deduped
        sdf_clean = sdf_clean.iloc[1:].reset_index(drop=True)
        # Drop completely empty rows
        sdf_clean = sdf_clean.dropna(how="all").reset_index(drop=True)

        if sdf_clean.empty:
            all_notes.append(f"Skipped sheet '{sname}' (empty after header)")
            continue

        layout = detect_layout(sdf_clean.columns.tolist(), sheet_names)

        if layout == "COL_GEIH":
            variables, notes = extract_col_geih(sdf_clean, sname)
        elif layout == "DOM_ENFT":
            variables, notes = extract_dom_enft(sdf_clean, sname)
        elif layout == "GTM_ENEIC":
            variables, notes = extract_gtm_eneic(sdf_clean, sname)
        elif layout == "BRA_PNADC":
            variables, notes = extract_bra_pnadc(sdf_clean, sname)
        else:
            variables, notes = extract_unknown_layout(sdf_clean, sname)

        all_variables.extend(variables)
        all_notes.extend(notes)
        for v in variables:
            if v["table"] not in all_tables:
                all_tables.append(v["table"])

    return {
        "variables": all_variables,
        "tables": all_tables,
        "decode_notes": all_notes,
    }


_HEADER_KEYWORDS = [
    "variable", "tabla", "nombre", "descripcion", "descripci",
    "etiqueta", "campo", "codigo", "id ", "tipo", "valor",
    "label", "field", "name", "code", "section",
]


def _find_header_row(df: pd.DataFrame, max_scan: int = 20) -> int | None:
    """
    Find the index of the row that looks most like a column header.

    Strategy: score each row by how many cells contain column-header keywords.
    Skip rows where any cell is very long (title/intro paragraphs).
    Return the highest-scoring row within max_scan rows.
    If no keyword match, fall back to the first row with >= 2 non-null short cells.
    """
    best_row = None
    best_score = 0
    fallback_row = None

    for i in range(min(max_scan, len(df))):
        row = df.iloc[i]
        str_cells = [str(v).strip() for v in row if str(v).strip() not in ("", "nan")]
        if not str_cells:
            continue

        # Skip rows containing very long cells (titles, legal text, intro paragraphs)
        max_cell_len = max(len(c) for c in str_cells)
        if max_cell_len > 120:
            continue

        # Fallback: first row with >= 2 short non-null cells
        if fallback_row is None and len(str_cells) >= 2:
            fallback_row = i

        # Score row by header keyword presence
        score = 0
        for cell in str_cells:
            cell_n = _norm(cell)
            for kw in _HEADER_KEYWORDS:
                if kw in cell_n:
                    score += 1
                    break  # count each cell once

        if score > best_score:
            best_score = score
            best_row = i

    # Require at least 2 keyword hits to trust the scored row
    if best_score >= 2:
        return best_row
    return fallback_row
