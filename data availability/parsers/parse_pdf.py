"""
PDF parser for HDMF survey dictionaries.

Classifies each PDF as one of three types and extracts accordingly:
  TABLE_DICT    — PDF has embedded tables (variable codebooks in tabular form)
  QUESTIONNAIRE — PDF is a questionnaire with numbered questions / variable codes
  BULLETIN      — Statistical report; no structured variable list extractable

Requires: pdfplumber  (pip install pdfplumber)
"""

import re
import unicodedata
from pathlib import Path


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


# ---------------------------------------------------------------------------
# PDF type classification
# ---------------------------------------------------------------------------

def _classify_pdf_type(file_path: Path) -> str:
    """
    Read up to 25 pages (sampling early + middle if doc is long) and classify
    the PDF as TABLE_DICT, QUESTIONNAIRE, or BULLETIN.

    Extended from 4 to 25 pages to catch variable tables that start late
    (e.g. ARG page 6, BOL DDI page 19).
    """
    try:
        import pdfplumber
    except ImportError:
        return "UNAVAILABLE"

    try:
        with pdfplumber.open(file_path) as pdf:
            n_pages = len(pdf.pages)

            # Build a page index: first 25 pages + a mid-document sample
            scan_indices = list(range(min(25, n_pages)))
            if n_pages > 25:
                mid = n_pages // 2
                scan_indices += list(range(mid, min(mid + 5, n_pages)))
            scan_indices = sorted(set(scan_indices))

            # Step 1 — look for embedded tables with variable-like structure
            for pi in scan_indices:
                page = pdf.pages[pi]
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    if not table or len(table[0]) < 3:
                        continue
                    # Check if header row contains dictionary-like keywords
                    header_str = _norm(" ".join(str(c or "") for c in table[0]))
                    has_dict_header = any(
                        kw in header_str
                        for kw in ["variable", "campo", "descripcion", "etiqueta",
                                   "label", "nombre", "quesito", "tipo", "type",
                                   "filter", "question", "coding"]
                    )
                    first_col_cells = [
                        str(row[0] or "").strip()
                        for row in table[1:]
                        if row and row[0]
                    ]
                    if len(first_col_cells) < 3:
                        continue
                    median_len = sorted([len(c) for c in first_col_cells])[len(first_col_cells) // 2]
                    n_unique = len(set(first_col_cells))
                    if has_dict_header and n_unique >= 3:
                        return "TABLE_DICT"
                    if median_len <= 20 and n_unique >= 5:
                        return "TABLE_DICT"

            # Step 2 — extract text from first 10 pages and look for questionnaire signals
            full_text = ""
            for pi in range(min(10, n_pages)):
                t = pdf.pages[pi].extract_text() or ""
                full_text += t + "\n"

            signal_counts = {
                "pcode":    len(re.findall(r"\bP\d{3,4}\b", full_text)),
                "numbered": len(re.findall(r"(?m)^\s*\d{1,3}[\.\)]\s+\w", full_text)),
                "section":  len(re.findall(r"(?i)(secci[oó]n|module|parte\s+\d|cap[íi]tulo)", full_text)),
                "question": len(re.findall(r"¿", full_text)),
                # CHL-style lowercase codes like pco2_b, h7a
                "lower_code": len(re.findall(r"(?m)^[a-z]{1,5}\d{1,3}[a-z_]?\s*[.\-–]", full_text)),
                # DHS-style letter+number codes
                "dhs_code": len(re.findall(r"(?m)^[A-Z]{1,3}\d{1,3}[A-Z]?\s*[.\-–]", full_text)),
                # Numbered variable tables (ARG, MEX style) — digits in short lines
                "short_numbered": len(re.findall(r"(?m)^\d{3,5}\s+\w", full_text)),
            }

            triggered = sum(1 for v in signal_counts.values() if v >= 3)
            if triggered >= 2:
                return "QUESTIONNAIRE"
            if signal_counts["pcode"] >= 5:
                return "QUESTIONNAIRE"
            if signal_counts["lower_code"] >= 5:
                return "QUESTIONNAIRE"

    except Exception:
        pass

    return "BULLETIN"


# ---------------------------------------------------------------------------
# Table dictionary extractor
# ---------------------------------------------------------------------------

def _detect_table_col_roles(headers: list[str]) -> dict:
    """Map column roles to indices from a PDF table header row."""
    result = {"name": None, "label": None, "type": None, "code": None, "code_desc": None}
    for i, h in enumerate(headers):
        hn = _norm(str(h or ""))
        # Name / variable identifier
        if result["name"] is None and any(k in hn for k in [
            "variable", "campo", "codigo", "nombre", "no.", "num",
            "id ", "name", "varname", "quesito", "filter"
        ]):
            result["name"] = i
        # Label / description
        elif result["label"] is None and any(k in hn for k in [
            "descripcion", "etiqueta", "label", "question", "pregunta",
            "contenido", "definicion", "enunciado"
        ]):
            result["label"] = i
        # Type
        elif result["type"] is None and any(k in hn for k in [
            "tipo", "type", "formato", "longitud", "storage"
        ]):
            result["type"] = i
        # Value codes
        elif result["code"] is None and any(k in hn for k in [
            "valor", "value", "codigo respuesta", "cod", "categor", "coding"
        ]):
            result["code"] = i
        # Value labels
        elif result["code_desc"] is None and any(k in hn for k in [
            "respuesta", "categoria", "category", "descripcion", "answer"
        ]):
            result["code_desc"] = i
    return result


def extract_table_dict(file_path: Path) -> tuple[list[dict], list[str]]:
    """Extract variables from a PDF with embedded dictionary tables."""
    import pdfplumber

    notes = ["PDF type: TABLE_DICT — table extraction used"]
    variables = []
    seen_names = {}

    try:
        with pdfplumber.open(file_path) as pdf:
            notes.append(f"  {len(pdf.pages)} pages total")
            prev_col_count = None
            ongoing_rows = []
            col_roles = {}

            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    n_cols = max(len(row) for row in table)

                    first_row_str = " ".join(str(c or "") for c in table[0])
                    is_continuation = (
                        prev_col_count == n_cols
                        and not any(
                            kw in _norm(first_row_str)
                            for kw in ["variable", "campo", "descripcion", "etiqueta",
                                       "label", "filter", "question", "coding"]
                        )
                    )

                    if is_continuation and ongoing_rows:
                        ongoing_rows.extend(table)
                    else:
                        # Flush previous table
                        if ongoing_rows and col_roles.get("name") is not None:
                            _extract_rows_into(ongoing_rows, col_roles, variables, seen_names)

                        # Start new table — detect col roles from header
                        col_roles = _detect_table_col_roles([str(c or "") for c in table[0]])

                        # Fallback: if name not detected, try second row as header
                        if col_roles["name"] is None and len(table) > 1:
                            col_roles2 = _detect_table_col_roles([str(c or "") for c in table[1]])
                            if col_roles2["name"] is not None:
                                col_roles = col_roles2
                                ongoing_rows = table[2:]
                            else:
                                ongoing_rows = table[1:]
                        else:
                            ongoing_rows = table[1:]

                        prev_col_count = n_cols

            # Flush last table
            if ongoing_rows and col_roles.get("name") is not None:
                _extract_rows_into(ongoing_rows, col_roles, variables, seen_names)

    except Exception as e:
        notes.append(f"  ERROR during table extraction: {e}")

    notes.append(f"  → {len(variables)} variables extracted")
    return variables, notes


def _extract_rows_into(rows, col_roles, variables, seen_names):
    """Extract variable records from table rows into the variables list."""
    name_i  = col_roles.get("name")
    label_i = col_roles.get("label")
    code_i  = col_roles.get("code")
    cdesc_i = col_roles.get("code_desc")

    for row in rows:
        if not row:
            continue
        name = str(row[name_i] or "").strip() if name_i is not None and name_i < len(row) else ""
        if not name or name.lower() in ("nan", "none", ""):
            continue

        # Skip rows that are clearly sub-headers or page titles (very long names)
        if len(name) > 60:
            continue

        label = ""
        if label_i is not None and label_i < len(row):
            label = str(row[label_i] or "").strip()
            label = "" if label.lower() in ("nan", "none") else label

        code = None
        code_desc = None
        if code_i is not None and code_i < len(row):
            cv = str(row[code_i] or "").strip()
            code = cv if cv not in ("", "nan", "None") else None
        if cdesc_i is not None and cdesc_i < len(row):
            dv = str(row[cdesc_i] or "").strip()
            code_desc = dv if dv not in ("", "nan", "None") else None

        if name not in seen_names:
            variables.append({
                "name":        name,
                "label":       label,
                "type":        "",
                "table":       "main",
                "value_codes": {},
            })
            seen_names[name] = len(variables) - 1

        idx = seen_names[name]
        if code and code_desc:
            try:
                code_key = str(int(float(code)))
            except (ValueError, OverflowError):
                code_key = code
            variables[idx]["value_codes"][code_key] = code_desc


# ---------------------------------------------------------------------------
# ARG-style text extractor
# Handles EPH registration guide: "CAMPO TIPO DESCRIPCIÓN" text-block format
# ---------------------------------------------------------------------------

_ARG_VAR_PATTERN = re.compile(
    r"(?m)^([A-Z][A-Z0-9_]{1,30})\s+[ANaCn]\s*[\(\d]+.*?\)\s+(.{5,120})$"
)

def _extract_arg_text(full_text: str) -> list[dict]:
    """
    Extract variable rows from ARG EPH-style text lines:
       AGLOMERADO N (2) Código de Aglomerado
       IV1 N (1) Tipo de vivienda
       IV1_Esp C (45) especificar:
    Pattern: VARNAME  [N|C] (length)  Description
    """
    variables = []
    seen = set()
    current_var = None
    lines = full_text.split("\n")
    # VARNAME: starts with uppercase letter, may include digits/underscores, 2-30 chars
    # Type: N or C (numeric/character)
    # Length: digits with optional decimal (e.g. 12.4)
    pat = re.compile(
        r"^([A-Z][A-Z0-9_]{1,29})\s+[NCnc]\s*\(\s*\d+[\.\d]*\s*\)\s+(.{3,120})$"
    )
    # Value code lines: "1 = something" or "1. something"
    val_pat = re.compile(r"^\s*(\d{1,3})\s*[=.]\s*(.{2,80})$")

    for line in lines:
        line = line.strip()
        m = pat.match(line)
        if m:
            name  = m.group(1).strip()
            label = m.group(2).strip()
            if name not in seen:
                seen.add(name)
                current_var = {
                    "name": name, "label": label,
                    "type": "", "table": "main", "value_codes": {}
                }
                variables.append(current_var)
        elif current_var is not None:
            vm = val_pat.match(line)
            if vm:
                current_var["value_codes"][vm.group(1)] = vm.group(2).strip()
    return variables


# ---------------------------------------------------------------------------
# DDI-style extractor (Bolivia EH)
# Handles variable tables: V-number | varname | label | type | description
# ---------------------------------------------------------------------------

def _extract_ddi_tables(file_path: Path) -> tuple[list[dict], list[str]]:
    """
    Extract variables from DDI-format PDF tables.
    DDI tables have columns like: [ID/No., Name/Variable, Label, Type, Description].
    """
    import pdfplumber

    notes = ["PDF type: TABLE_DICT (DDI format) — table extraction used"]
    variables = []
    seen_names = {}

    try:
        with pdfplumber.open(file_path) as pdf:
            notes.append(f"  {len(pdf.pages)} pages total")

            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # DDI tables: first col is a numeric ID or "V###", second is variable name
                    header = [_norm(str(c or "")) for c in table[0]]
                    header_str = " ".join(header)

                    # Detect DDI header pattern
                    is_ddi = (
                        any(k in header_str for k in ["name", "nombre", "variable", "etiqueta", "label"])
                        and len(header) >= 3
                    )
                    if not is_ddi:
                        continue

                    # Map columns
                    name_i  = None
                    label_i = None
                    type_i  = None
                    for i, h in enumerate(header):
                        if name_i is None and any(k in h for k in ["name", "nombre", "variable"]):
                            name_i = i
                        elif label_i is None and any(k in h for k in ["label", "etiqueta", "descripcion"]):
                            label_i = i
                        elif type_i is None and any(k in h for k in ["type", "tipo", "storage"]):
                            type_i = i

                    if name_i is None:
                        continue

                    for row in table[1:]:
                        if not row or name_i >= len(row):
                            continue
                        name = str(row[name_i] or "").strip()
                        if not name or name.lower() in ("nan", "none", ""):
                            continue
                        if len(name) > 60:
                            continue
                        label = ""
                        if label_i is not None and label_i < len(row):
                            label = str(row[label_i] or "").strip()
                            label = "" if label.lower() in ("nan", "none") else label

                        if name not in seen_names:
                            variables.append({
                                "name": name, "label": label,
                                "type": "", "table": "main", "value_codes": {}
                            })
                            seen_names[name] = len(variables) - 1

    except Exception as e:
        notes.append(f"  ERROR: {e}")

    notes.append(f"  → {len(variables)} variables extracted")
    return variables, notes


# ---------------------------------------------------------------------------
# Questionnaire extractor
# ---------------------------------------------------------------------------

# Patterns for variable codes — ordered most-specific first
_VAR_CODE_PATTERNS = [
    re.compile(r"(?m)^(P\d{2,4}[A-Z]?\d*)\s*[.\-–:]\s*(.{5,120})"),
    re.compile(r"(?m)^(V\d{3,4})\s*[.\-–:]\s*(.{5,120})"),
    re.compile(r"(?m)^([A-Z]{1,2}\d{1,2}[a-z]?)\.\s+(.{5,120})"),
    re.compile(r"(?m)^([A-Z]{1,3}\d{1,3}[A-Z]?)\s*[.\-–]\s*(.{5,120})"),
    # CHL CASEN style: lowercase module codes like pco2_b, h7a, v1
    re.compile(r"(?m)^([a-z]{1,5}\d{1,3}[a-z]?(?:_[a-z]\d*)?)\s*[.\-–]\s*(.{5,120})"),
    # Numbered questions
    re.compile(r"(?m)^\s*(\d{1,3})\.\s+([A-ZÁÉÍÓÚÑ¿].{5,80})"),
]

_SECTION_PATTERN = re.compile(
    r"(?im)^\s*(secci[oó]n\s+\d+|m[oó]dulo\s+[A-Z\d]+|parte\s+\d+|cap[íi]tulo\s+\d+|"
    r"SECTION\s+[A-Z\d]+|MODULE\s+[A-Z\d]+)",
)

_CODE_LINE_PATTERN = re.compile(r"^\s*(\d+)\s*[-–.)\s]+(.{2,60})$")


def extract_questionnaire(file_path: Path) -> tuple[list[dict], list[str]]:
    """
    Extract variable codes from a questionnaire PDF.
    Best-effort: finds P####-style codes, lowercase module codes, or numbered questions.
    """
    import pdfplumber

    notes = ["PDF type: QUESTIONNAIRE — regex extraction; best-effort"]
    full_text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            notes.append(f"  {len(pdf.pages)} pages")
            for page in pdf.pages:
                t = page.extract_text() or ""
                full_text += t + "\n"
    except Exception as e:
        return [], [f"ERROR reading PDF: {e}"]

    variables = []
    seen = set()
    current_section = "main"
    current_var = None

    lines = full_text.split("\n")

    for line in lines:
        # Detect section changes
        sm = _SECTION_PATTERN.match(line)
        if sm:
            current_section = sm.group(1).strip()
            continue

        matched = False
        for pattern in _VAR_CODE_PATTERNS:
            m = pattern.match(line)
            if m:
                var_name  = m.group(1).strip()
                var_label = m.group(2).strip()
                var_label = re.sub(r"\s+", " ", var_label).strip("?¿").strip()
                if var_name not in seen:
                    seen.add(var_name)
                    current_var = {
                        "name":        var_name,
                        "label":       var_label,
                        "type":        "",
                        "table":       current_section,
                        "value_codes": {},
                    }
                    variables.append(current_var)
                matched = True
                break

        if not matched and current_var is not None:
            cm = _CODE_LINE_PATTERN.match(line)
            if cm:
                code = cm.group(1).strip()
                desc = cm.group(2).strip()
                if desc and len(desc) > 2:
                    current_var["value_codes"][code] = desc

    notes.append(f"  → {len(variables)} variables extracted (question codes only)")
    return variables, notes


# ---------------------------------------------------------------------------
# Bulletin extractor
# ---------------------------------------------------------------------------

def extract_bulletin(file_path: Path) -> tuple[list[dict], list[str]]:
    notes = [
        "PDF type: BULLETIN — no structured variable list extractable.",
        "  This file is a statistical report or publication.",
        "  Manual review required to determine variable availability.",
    ]
    return [], notes


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def parse(file_path: Path) -> dict:
    """
    Parse a PDF file. Returns partial result dict:
      {"variables": [...], "tables": [...], "decode_notes": [...]}
    """
    try:
        import pdfplumber  # noqa: F401
    except ImportError:
        return {
            "variables": [],
            "tables": [],
            "decode_notes": [
                f"ERROR: 'pdfplumber' required to read {file_path.name}. "
                "Install with: pip install pdfplumber"
            ],
        }

    pdf_type = _classify_pdf_type(file_path)

    if pdf_type == "UNAVAILABLE":
        return {
            "variables": [],
            "tables": [],
            "decode_notes": [
                f"ERROR: pdfplumber not available — cannot read {file_path.name}. "
                "Install with: pip install pdfplumber"
            ],
        }

    if pdf_type == "TABLE_DICT":
        variables, notes = extract_table_dict(file_path)

        # Check if extracted names look like value codes (all-numeric) rather than
        # real variable names — this happens with ARG EPH where pdfplumber extracts
        # only the header row and the value-code sub-tables look like the main table.
        names = [v["name"] for v in variables]
        looks_like_codes = (
            len(names) > 0
            and sum(1 for n in names if re.fullmatch(r"\d+", n)) / len(names) > 0.4
        )

        # If table extraction found almost nothing or extracted only value codes,
        # try text-based ARG fallback
        if len(variables) < 10 or looks_like_codes:
            try:
                import pdfplumber
                full_text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        full_text += (page.extract_text() or "") + "\n"
                arg_vars = _extract_arg_text(full_text)
                if len(arg_vars) > len(variables):
                    variables = arg_vars
                    notes.append(
                        f"  Switched to ARG text-block extractor: {len(arg_vars)} vars"
                    )
            except Exception:
                pass

        # If still nothing, try DDI extractor
        if len(variables) < 5:
            variables, notes = _extract_ddi_tables(file_path)

    elif pdf_type == "QUESTIONNAIRE":
        variables, notes = extract_questionnaire(file_path)

        # If most extracted "variable names" are pure digits, the regex picked up
        # value-code lines instead of variable identifiers (e.g. ARG EPH style).
        # Try the ARG CAMPO/TIPO/DESCRIPCIÓN text extractor.
        names = [v["name"] for v in variables]
        mostly_digits = (
            len(names) > 0
            and sum(1 for n in names if re.fullmatch(r"\d+", n)) / len(names) > 0.4
        )
        if mostly_digits or len(variables) < 10:
            try:
                import pdfplumber
                full_text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        full_text += (page.extract_text() or "") + "\n"
                arg_vars = _extract_arg_text(full_text)
                if len(arg_vars) > len(variables):
                    variables = arg_vars
                    notes = [
                        "PDF type: QUESTIONNAIRE/TABLE (ARG text-block extractor)",
                        f"  {len(arg_vars)} variables extracted from CAMPO/TIPO/DESCRIPCIÓN lines",
                    ]
            except Exception:
                pass

        # Fallback to DDI table extraction
        if len(variables) < 5:
            ddi_vars, ddi_notes = _extract_ddi_tables(file_path)
            if len(ddi_vars) > len(variables):
                variables, notes = ddi_vars, ddi_notes

    else:
        variables, notes = extract_bulletin(file_path)

    tables = list({v["table"] for v in variables}) if variables else []

    return {
        "variables": variables,
        "tables":    tables,
        "decode_notes": notes,
    }
