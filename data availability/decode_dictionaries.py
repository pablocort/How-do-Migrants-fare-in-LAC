"""
HDMF Survey Dictionary Decoder
===============================
Converts survey dictionaries (PDF, XLSX, XLS, ODS) stored in the
'data availability/' country subfolders into standardized JSON files.

Output per country:
  decoded/[ISO3]_dictionary.json     — full variable list with value codes
  decoded/[ISO3]_dictionary_summary.md — HDMF feasibility pre-check table

Usage:
  python decode_dictionaries.py --country COL
  python decode_dictionaries.py --all
  python decode_dictionaries.py --list
  python decode_dictionaries.py --country COL --force   (overwrite existing)
  python decode_dictionaries.py --all --verbose

Exit codes:
  0  — success (even if some files had parse errors — see decode_notes)
  1  — fatal error (bad country code, output dir cannot be created)
"""

import argparse
import json
import sys
from pathlib import Path

DATA_AVAIL_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_AVAIL_DIR / "decoded"

# ---------------------------------------------------------------------------
# Country registry
# ---------------------------------------------------------------------------

COUNTRY_REGISTRY: dict[str, dict] = {
    "ARG": {"survey": "EPH",    "folder": "raw/arg", "period": "2023"},
    "BLZ": {"survey": "—",      "folder": "raw/blz", "period": "—"},
    "BOL": {"survey": "EH",     "folder": "raw/bol", "period": "2024"},
    "BRA": {"survey": "PNADC",  "folder": "raw/bra", "period": "2025"},
    "CHL": {"survey": "CASEN",  "folder": "raw/chl", "period": "2024"},
    "COL": {"survey": "GEIH",   "folder": "raw/col", "period": "2025"},
    "CRI": {"survey": "ENAHO",  "folder": "raw/cri", "period": "2025"},
    "DOM": {"survey": "ENFT",   "folder": "raw/dom", "period": "2024"},
    "ECU": {"survey": "ENEMDU", "folder": "raw/ecu", "period": "2025"},
    "GTM": {"survey": "ENEIC",  "folder": "raw/gtm", "period": "2025"},
    "GUY": {"survey": "GLFS",   "folder": "raw/guy", "period": "2021"},
    "HND": {"survey": "EPHPM",  "folder": "raw/hnd", "period": "2025"},
    "HTI": {"survey": "DHS",    "folder": "raw/hti", "period": "2017"},
    "JAM": {"survey": "—",      "folder": "raw/jam", "period": "—"},
    "MEX": {"survey": "ENOE",   "folder": "raw/mex", "period": "2024"},
}

# ---------------------------------------------------------------------------
# HDMF standard variables for pre-check table
# ---------------------------------------------------------------------------

HDMF_TARGET_VARS: dict[str, list[str]] = {
    "Identifiers & weights": ["pais_c", "idh_ch", "idp_ci", "factor_ci", "factor_ch"],
    "Demographics":          ["edad_ci", "sexo_ci", "relacion_ci", "miembros_ci"],
    "Migration":             ["migrante_ci", "mig_pais_ci", "migrantiguo5_ci"],
    "Employment status":     ["condocup_ci", "emp_ci", "desemp_ci", "pea_ci"],
    "Job characteristics":   ["formal_ci", "tipocontrato_ci", "horaspri_ci",
                              "horastot_ci", "cotizando_ci", "afiliado_ci"],
    "Education":             ["aedu_ci", "edu_isced", "edu_hdmf"],
    "Income":                ["ylm_ci", "ylnm_ci", "ynlm_ci", "ytot_ci",
                             "remesas_ci", "remesas_ch"],
}

# Concept keywords that suggest a raw variable covers an HDMF concept
# (used in the markdown pre-check to flag likely matches in the decoded JSON)
CONCEPT_KEYWORDS: dict[str, list[str]] = {
    "edad_ci":        ["edad", "age", "anos"],
    "sexo_ci":        ["sexo", "sex", "genero", "gender"],
    "relacion_ci":    ["relacion", "parentesco", "jefe", "relationship"],
    "miembros_ci":    ["miembro", "member", "personas en el hogar"],
    "migrante_ci":    ["migrante", "migrant", "nacido", "born", "pais de nacimiento",
                       "pais nacimiento", "lugar de nacimiento", "extranjero"],
    "mig_pais_ci":    ["pais de nacimiento", "pais nacimiento", "nationality", "nacionalidad"],
    "migrantiguo5_ci":["años de residencia", "tiempo de residencia", "anos residencia",
                       "llegada", "arrival"],
    "condocup_ci":    ["condicion de ocupacion", "condicion ocupacion", "ocupado",
                       "desocupado", "inactivo", "actividad"],
    "emp_ci":         ["empleo", "empleado", "trabajo", "ocupado", "employed"],
    "desemp_ci":      ["desempleo", "desocupado", "busca trabajo", "unemployed"],
    "pea_ci":         ["pea", "economicamente activo", "fuerza laboral", "labor force"],
    "formal_ci":      ["formal", "seguridad social", "afiliado", "cotiza"],
    "tipocontrato_ci":["contrato", "contract", "tipo de contrato"],
    "horaspri_ci":    ["horas trabajadas", "horas de trabajo", "hours worked"],
    "horastot_ci":    ["horas totales", "total hours"],
    "cotizando_ci":   ["cotiza", "cotizacion", "contribucion", "pension"],
    "afiliado_ci":    ["afiliado", "afiliacion", "salud", "health insurance"],
    "aedu_ci":        ["anos de educacion", "anos de estudio", "anos escolaridad",
                       "nivel educativo", "education"],
    "edu_isced":      ["nivel educativo", "grado", "nivel de instruccion", "education level"],
    "edu_hdmf":       ["nivel educativo", "grado", "instruccion"],
    "ylm_ci":         ["ingreso laboral", "salario", "wage", "income labor", "sueldo"],
    "ylnm_ci":        ["ingreso no monetario", "ingreso en especie", "non-monetary"],
    "ynlm_ci":        ["ingreso no laboral", "renta", "pension", "non-labor income"],
    "ytot_ci":        ["ingreso total", "total income", "ingreso del hogar"],
    "remesas_ci":     ["remesa", "remittance", "transferencia del exterior"],
    "remesas_ch":     ["remesa hogar", "remittance household"],
    "factor_ci":      ["factor de expansion", "factor de ponderacion", "peso", "weight"],
    "factor_ch":      ["factor hogar", "factor de expansion hogar"],
}


# ---------------------------------------------------------------------------
# File scanner
# ---------------------------------------------------------------------------

def get_country_files(country_dir: Path) -> dict[str, list[Path]]:
    """Scan a country folder and group files by extension type."""
    result: dict[str, list[Path]] = {"xlsx": [], "xls": [], "ods": [], "pdf": []}
    if not country_dir.exists():
        return result
    for f in sorted(country_dir.iterdir()):
        if f.is_dir() or f.name.startswith(".") or f.name == "CLAUDE.md":
            continue
        ext = f.suffix.lower().lstrip(".")
        if ext in result:
            result[ext].append(f)
    return result


# ---------------------------------------------------------------------------
# File dispatcher
# ---------------------------------------------------------------------------

def dispatch_file(file_path: Path, iso3: str, verbose: bool = False) -> dict | None:
    """Route a file to the correct parser. Returns partial result or None on failure."""
    ext = file_path.suffix.lower()
    if verbose:
        print(f"    Parsing: {file_path.name}")

    try:
        if ext in (".xlsx", ".xls"):
            from parsers import parse_xlsx
            return parse_xlsx.parse(file_path)
        elif ext == ".ods":
            from parsers import parse_ods
            return parse_ods.parse(file_path)
        elif ext == ".pdf":
            from parsers import parse_pdf
            return parse_pdf.parse(file_path)
        else:
            return {
                "variables": [],
                "tables": [],
                "decode_notes": [f"Unsupported file type: {file_path.name}"],
            }
    except Exception as e:
        return {
            "variables": [],
            "tables": [],
            "decode_notes": [f"ERROR dispatching {file_path.name}: {e}"],
        }


# ---------------------------------------------------------------------------
# Result merger
# ---------------------------------------------------------------------------

def merge_results(partial_results: list[dict], meta: dict) -> dict:
    """
    Combine per-file parse results into one canonical result dict.
    Deduplicates variables by name (last file wins, with a note).
    """
    all_vars: dict[str, dict] = {}
    all_tables: list[str] = []
    all_notes: list[str] = []
    source_files: list[str] = meta.get("source_files", [])

    for partial in partial_results:
        for note in partial.get("decode_notes", []):
            all_notes.append(note)
        for table in partial.get("tables", []):
            if table not in all_tables:
                all_tables.append(table)
        for var in partial.get("variables", []):
            name = var.get("name", "")
            if not name:
                continue
            if name in all_vars:
                all_notes.append(f"  Duplicate variable '{name}' — later file takes precedence")
            all_vars[name] = var

    return {
        "iso3": meta["iso3"],
        "survey": meta["survey"],
        "period": meta["period"],
        "source_files": source_files,
        "tables": all_tables,
        "variables": list(all_vars.values()),
        "decode_notes": all_notes,
    }


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------

def _check_hdmf_coverage(variables: list[dict]) -> dict[str, str]:
    """
    For each HDMF target variable, check if a matching raw variable exists.
    Returns {hdmf_var: status} where status is "LIKELY_FOUND" or "NOT_FOUND".
    """
    all_names = {v["name"].lower() for v in variables}
    all_labels = {v.get("label", "").lower() for v in variables}
    combined_text = all_names | all_labels

    coverage = {}
    for domain_vars in HDMF_TARGET_VARS.values():
        for hdmf_var in domain_vars:
            keywords = CONCEPT_KEYWORDS.get(hdmf_var, [])
            found = any(
                any(kw in text for kw in keywords)
                for text in combined_text
                if text
            )
            coverage[hdmf_var] = "LIKELY_FOUND" if found else "NOT_FOUND"
    return coverage


def write_outputs(result: dict, output_dir: Path) -> tuple[Path, Path]:
    """Write JSON and markdown summary. Returns (json_path, md_path)."""
    iso3 = result["iso3"]
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON output
    json_path = output_dir / f"{iso3}_dictionary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Markdown summary
    md_path = output_dir / f"{iso3}_dictionary_summary.md"
    coverage = _check_hdmf_coverage(result["variables"])

    n_vars = len(result["variables"])
    n_tables = len(result["tables"])
    n_with_codes = sum(1 for v in result["variables"] if v.get("value_codes"))

    lines = [
        f"# Dictionary Summary: {iso3} — {result['survey']} {result['period']}",
        "",
        f"**Source files:** {', '.join(result['source_files']) if result['source_files'] else 'none'}  ",
        f"**Variables decoded:** {n_vars}  ",
        f"**Variables with value codes:** {n_with_codes}  ",
        f"**Tables/modules:** {n_tables} ({', '.join(result['tables'][:8])}{'...' if n_tables > 8 else ''})  ",
        "",
        "---",
        "",
        "## HDMF Variable Coverage Pre-Check",
        "",
        "Status is based on keyword matching against variable names and labels.",
        "LIKELY_FOUND means a concept keyword appeared — manual verification still required.",
        "",
        "| Domain | HDMF Variable | Status |",
        "|--------|---------------|--------|",
    ]

    for domain, domain_vars in HDMF_TARGET_VARS.items():
        for var in domain_vars:
            status = coverage.get(var, "NOT_FOUND")
            icon = "✓" if status == "LIKELY_FOUND" else "✗"
            lines.append(f"| {domain} | `{var}` | {icon} {status} |")

    n_found = sum(1 for s in coverage.values() if s == "LIKELY_FOUND")
    n_total = len(coverage)
    lines += [
        "",
        f"**Coverage: {n_found}/{n_total} HDMF variables likely found ({100*n_found//n_total}%)**",
        "",
        "---",
        "",
        "## Decode Notes",
        "",
    ]
    for note in result["decode_notes"]:
        lines.append(f"- {note}")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return json_path, md_path


# ---------------------------------------------------------------------------
# Per-country pipeline
# ---------------------------------------------------------------------------

def run_country(iso3: str, force: bool = False, verbose: bool = False) -> dict:
    """
    Full pipeline for one country.
    Returns status dict: {iso3, status, n_vars, n_tables, json_path, md_path, errors}
    """
    iso3 = iso3.upper()
    if iso3 not in COUNTRY_REGISTRY:
        print(f"ERROR: '{iso3}' not in country registry. Use --list to see available countries.")
        sys.exit(1)

    meta = COUNTRY_REGISTRY[iso3]
    country_dir = DATA_AVAIL_DIR / meta["folder"]
    json_path = OUTPUT_DIR / f"{iso3}_dictionary.json"

    if json_path.exists() and not force:
        if verbose:
            print(f"  {iso3}: output already exists — skipping (use --force to overwrite)")
        return {
            "iso3": iso3,
            "status": "SKIPPED",
            "n_vars": None,
            "n_tables": None,
            "json_path": str(json_path),
            "md_path": str(OUTPUT_DIR / f"{iso3}_dictionary_summary.md"),
            "errors": [],
        }

    files = get_country_files(country_dir)
    all_files = files["xlsx"] + files["xls"] + files["ods"] + files["pdf"]

    if not all_files:
        result = {
            "iso3": iso3,
            "survey": meta["survey"],
            "period": meta["period"],
            "source_files": [],
            "tables": [],
            "variables": [],
            "decode_notes": ["NO_DOCUMENTATION — folder is empty or contains no supported files"],
        }
        jp, mp = write_outputs(result, OUTPUT_DIR)
        return {
            "iso3": iso3,
            "status": "NO_DOCUMENTATION",
            "n_vars": 0,
            "n_tables": 0,
            "json_path": str(jp),
            "md_path": str(mp),
            "errors": [],
        }

    partial_results = []
    errors = []
    source_files = []

    for f in all_files:
        source_files.append(f.name)
        partial = dispatch_file(f, iso3, verbose=verbose)
        if partial:
            partial_results.append(partial)
            # Collect errors from decode_notes
            for note in partial.get("decode_notes", []):
                if note.startswith("ERROR"):
                    errors.append(note)

    merged = merge_results(
        partial_results,
        {**meta, "iso3": iso3, "source_files": source_files}
    )
    jp, mp = write_outputs(merged, OUTPUT_DIR)

    return {
        "iso3": iso3,
        "status": "OK" if not errors else "PARTIAL",
        "n_vars": len(merged["variables"]),
        "n_tables": len(merged["tables"]),
        "json_path": str(jp),
        "md_path": str(mp),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------

def run_all(force: bool = False, verbose: bool = False) -> list[dict]:
    """Run the decoder for every country in the registry."""
    print(f"HDMF Dictionary Decoder — processing {len(COUNTRY_REGISTRY)} countries")
    print("=" * 65)

    results = []
    for iso3 in COUNTRY_REGISTRY:
        if verbose:
            print(f"\n{iso3}:")
        r = run_country(iso3, force=force, verbose=verbose)
        results.append(r)

        # Print progress line
        if r["status"] == "NO_DOCUMENTATION":
            line = f"  {iso3:<5} {'—':<8} {'—':<6} {'—':<12} {'—':>20}   [NO DOCUMENTATION]"
        elif r["status"] == "SKIPPED":
            line = f"  {iso3:<5} {'—':<8} {'—':<6} {'—':<12} {'—':>20}   [SKIPPED — exists]"
        else:
            meta = COUNTRY_REGISTRY[iso3]
            warn = " [WARN — errors]" if r["status"] == "PARTIAL" else ""
            n_vars = r["n_vars"] or 0
            n_tabs = r["n_tables"] or 0
            line = (
                f"  {iso3:<5} {meta['survey']:<8} {meta['period']:<6}"
                f"  → {n_vars:>4} vars, {n_tabs:>2} tables{warn}"
            )
        print(line)

    print("=" * 65)
    ok = sum(1 for r in results if r["status"] in ("OK", "PARTIAL"))
    no_doc = sum(1 for r in results if r["status"] == "NO_DOCUMENTATION")
    total_vars = sum(r["n_vars"] or 0 for r in results)
    print(f"  Total: {len(results)} countries / {ok} decoded / {no_doc} no documentation")
    print(f"  {total_vars} variables across all decoded countries")
    print(f"  Output: {OUTPUT_DIR}")
    return results


# ---------------------------------------------------------------------------
# List command
# ---------------------------------------------------------------------------

def list_countries() -> None:
    """Print registry and current decode status."""
    print(f"{'ISO3':<6} {'Survey':<10} {'Period':<8} {'Decoded?':<10} {'Variables'}")
    print("-" * 55)
    for iso3, meta in COUNTRY_REGISTRY.items():
        json_path = OUTPUT_DIR / f"{iso3}_dictionary.json"
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                n = len(data.get("variables", []))
                status = f"YES ({n} vars)"
            except Exception:
                status = "YES (unreadable)"
        else:
            status = "NO"
        print(f"  {iso3:<5} {meta['survey']:<10} {meta['period']:<8} {status}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Force UTF-8 output on Windows consoles that default to cp1252
    import sys as _sys
    if hasattr(_sys.stdout, "reconfigure"):
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="decode_dictionaries.py",
        description="HDMF Survey Dictionary Decoder — converts PDF/XLSX/ODS to JSON",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--country", metavar="ISO3", help="Decode a single country (e.g. COL)")
    group.add_argument("--all", action="store_true", help="Decode all countries in the registry")
    group.add_argument("--list", action="store_true", dest="list_countries",
                       help="List countries and current decode status, then exit")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing decoded JSON files")
    parser.add_argument("--verbose", action="store_true",
                        help="Print per-file progress during parsing")

    args = parser.parse_args()

    # Ensure we're resolving parsers relative to this script
    import sys as _sys
    _sys.path.insert(0, str(DATA_AVAIL_DIR))

    if args.list_countries:
        list_countries()
        return

    if args.all:
        run_all(force=args.force, verbose=args.verbose)
    else:
        r = run_country(args.country, force=args.force, verbose=args.verbose)
        meta = COUNTRY_REGISTRY.get(args.country.upper(), {})
        if r["status"] == "NO_DOCUMENTATION":
            print(f"{args.country.upper()}: No documentation found in folder.")
        elif r["status"] == "SKIPPED":
            print(f"{args.country.upper()}: Output already exists — use --force to overwrite.")
            print(f"  JSON: {r['json_path']}")
        else:
            print(f"{args.country.upper()} [{meta.get('survey','')} {meta.get('period','')}]: "
                  f"{r['n_vars']} variables, {r['n_tables']} tables")
            print(f"  JSON: {r['json_path']}")
            print(f"  Summary: {r['md_path']}")
            if r["errors"]:
                print(f"  Warnings ({len(r['errors'])} file(s) had errors):")
                for e in r["errors"][:5]:
                    print(f"    {e}")


if __name__ == "__main__":
    main()
