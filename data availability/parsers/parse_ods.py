"""
ODS parser for HDMF survey dictionaries.

Handles ODS files (LibreOffice Calc format) as used by Ecuador ENEMDU.
These files often have an institutional metadata block at the top
before the actual variable listing begins.

Requires: odfpy  (pip install odfpy)
"""

import pandas as pd
from pathlib import Path


def _norm(s) -> str:
    if not isinstance(s, str):
        return ""
    return s.lower().strip()


def _find_table_start(df: pd.DataFrame) -> int:
    """
    Scan rows to find the index where the variable listing starts.
    Skips long title/metadata rows; returns the first row that looks like
    a short variable name or a column header row.
    """
    for i in range(min(30, len(df))):
        # Use positional access (iloc) since column labels may be arbitrary
        cell = str(df.iloc[i, 0]).strip()
        if cell in ("", "nan", "None"):
            continue
        # Skip very long cells (titles, institutional descriptions)
        if len(cell) > 60:
            continue
        # Skip all-caps section headers with spaces
        if cell.isupper() and " " in cell and len(cell) > 15:
            continue
        # Accept: short alphanumeric cell = likely a variable name or column header
        if len(cell) <= 50 and any(c.isalnum() for c in cell):
            return i
    return 0


def parse(file_path: Path) -> dict:
    """
    Parse an ODS file. Returns partial result dict:
      {"variables": [...], "tables": [...], "decode_notes": [...]}
    """
    all_variables = []
    all_tables = []
    all_notes = [f"Source: {file_path.name}"]

    try:
        sheets_raw = pd.read_excel(
            file_path, sheet_name=None, header=None, engine="odf", dtype=str
        )
    except ImportError:
        msg = (
            f"ERROR: 'odfpy' library required to read {file_path.name}. "
            "Install with: pip install odfpy"
        )
        return {"variables": [], "tables": [], "decode_notes": [msg]}
    except Exception as e:
        return {
            "variables": [],
            "tables": [],
            "decode_notes": [f"ERROR reading {file_path.name}: {e}"],
        }

    # Normalize sheet names to strings (ODS may return numeric keys)
    sheets = {str(k): v for k, v in sheets_raw.items()}
    all_notes.append(f"  {len(sheets)} sheet(s): {', '.join(sheets.keys())}")

    for sheet_name, df in sheets.items():
        if df.empty:
            all_notes.append(f"  Skipped sheet '{sheet_name}' (empty)")
            continue

        # Drop fully empty rows, then fully empty columns (by position)
        df = df.dropna(how="all").reset_index(drop=True)
        keep_cols = [i for i in range(len(df.columns)) if df.iloc[:, i].notna().any()]
        if not keep_cols:
            all_notes.append(f"  Skipped sheet '{sheet_name}' (all columns empty)")
            continue
        df = df.iloc[:, keep_cols].copy()
        # Normalize column labels to sequential strings '0','1','2',...
        df.columns = [str(i) for i in range(len(df.columns))]

        if df.shape[1] < 2:
            all_notes.append(f"  Skipped sheet '{sheet_name}' (too few columns)")
            continue

        # Find where the variable table starts
        start = _find_table_start(df)
        all_notes.append(f"  Sheet '{sheet_name}': table starts at row {start}")

        data = df.iloc[start:].reset_index(drop=True)
        if data.empty:
            all_notes.append(f"  Skipped sheet '{sheet_name}' (no data after header scan)")
            continue

        # Try to use first row as header if it contains column label keywords
        first_row = data.iloc[0].tolist()
        first_row_str = [str(v).strip() if pd.notna(v) else "" for v in first_row]
        joined = " ".join(first_row_str).lower()
        looks_like_header = any(
            kw in joined
            for kw in ["variable", "campo", "nombre", "etiqueta", "field", "descripcion"]
        )

        if looks_like_header:
            # Use first row as column names (string-safe)
            new_cols = []
            for j, v in enumerate(first_row_str):
                new_cols.append(v if v not in ("", "nan", "None") else str(j))
            data.columns = new_cols
            data = data.iloc[1:].reset_index(drop=True)
        # else: columns are already '0','1','2',... — positional access works

        cols = data.columns.tolist()  # already strings

        # Identify name and label columns by keyword or fall back to first two
        name_col = _pick_col(cols, ["nombre del campo", "campo", "variable", "nombre"])
        label_col = _pick_col(cols, ["descripcion del campo", "descripcion", "etiqueta", "label"])

        if name_col is None:
            name_col = cols[0]
            all_notes.append(f"    name_col fallback → '{cols[0]}'")
        if label_col is None and len(cols) >= 2:
            label_col = cols[1]
            all_notes.append(f"    label_col fallback → '{cols[1]}'")

        variables = []
        for _, row in data.iterrows():
            name_raw = row.get(name_col, "")
            name = str(name_raw).strip() if pd.notna(name_raw) else ""
            if not name or name.lower() in ("nan", "none", "") or len(name) > 60:
                continue

            label = ""
            if label_col:
                label_raw = row.get(label_col, "")
                label = str(label_raw).strip() if pd.notna(label_raw) else ""
                label = "" if label.lower() in ("nan", "none") else label

            variables.append({
                "name": name,
                "label": label,
                "type": "",
                "table": sheet_name,
                "value_codes": {},
            })

        all_variables.extend(variables)
        if sheet_name not in all_tables:
            all_tables.append(sheet_name)
        all_notes.append(f"    → {len(variables)} variables")

    return {
        "variables": all_variables,
        "tables": all_tables,
        "decode_notes": all_notes,
    }


def _pick_col(cols: list[str], keywords: list[str]) -> str | None:
    """Return first column whose lowercased name contains any of the keywords."""
    for kw in keywords:
        for col in cols:
            if kw in str(col).lower():
                return col
    return None
