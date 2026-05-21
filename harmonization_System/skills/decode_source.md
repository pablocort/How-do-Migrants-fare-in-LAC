# Skill: Decode Source Dictionary

## Purpose

Given a single country folder in `data availability/`, choose the correct parser, run the decode script for that country, verify the output JSON is valid, and report what was decoded. This skill is the single-country focused version of the dictionary_decoder agent workflow.

## When to invoke

- The dictionary_decoder agent is processing one country at a time and needs step-by-step verification
- The orchestrator needs dictionary metadata for a country before running survey_mapper
- The feasibility assessment agent needs a JSON that does not yet exist
- Troubleshooting a parse failure for a specific country

---

## Step 1 — Check for existing output

```python
# Check: does decoded/[ISO3]_dictionary.json exist and is non-empty?
import json
from pathlib import Path
p = Path("data availability/decoded/[ISO3]_dictionary.json")
if p.exists() and p.stat().st_size > 100:
    data = json.loads(p.read_text(encoding="utf-8"))
    print(f"Existing output: {len(data['variables'])} variables")
```

If output exists and `variables` is non-empty → **skip to Step 4** (verify and report).  
If output exists but `variables` is empty (NO_DOCUMENTATION) → report and stop.  
If output does not exist → proceed to Step 2.

---

## Step 2 — Inspect the source folder

List all files in `data availability/[iso3]/`.

```bash
ls "data availability/[iso3]/"
```

Classify by extension:
- `.xlsx` / `.xls` → XLSX/XLS parser
- `.ods` → ODS parser (requires `odfpy`)
- `.pdf` → PDF parser (requires `pdfplumber`)

If folder is **empty** → record as NO_DOCUMENTATION, stop, and report:
> "No documentation files found for [ISO3]. Obtain a dictionary or questionnaire file before proceeding."

---

## Step 3 — Run the decoder

```bash
python "data availability/decode_dictionaries.py" --country [ISO3] --verbose
```

Add `--force` only if overwriting an existing output was confirmed with the user.

Capture the stdout. Flag any lines containing `ERROR` or `WARNING`.

**If a library is missing** (pdfplumber / odfpy), run first:
```bash
pip install pdfplumber odfpy
```
Then re-run the decoder.

---

## Step 4 — Verify output

Open `data availability/decoded/[ISO3]_dictionary.json` and check:

| Check | Expected |
|-------|----------|
| JSON is parseable | No JSON decode error |
| `iso3` field | Matches the target country |
| `variables` array | Non-empty (if source files were present) |
| At least one variable has `value_codes` non-empty | Confirms code parsing worked (for XLSX sources) |
| `decode_notes` | Contains at least one note about files processed |
| No `decode_notes` entry starting with `ERROR` | Or if errors present, list them |

---

## Step 5 — Report

Return a structured summary:

| Field | Value |
|-------|-------|
| ISO3 | [code] |
| Survey | [from JSON `survey`] |
| Period | [from JSON `period`] |
| Source files | [from JSON `source_files`] |
| Variables decoded | N |
| Variables with value codes | N |
| Tables/modules | [list from JSON `tables`] |
| HDMF pre-check | See `decoded/[ISO3]_dictionary_summary.md` |
| Warnings | [any decode_notes starting with ERROR or WARNING] |
| JSON path | `data availability/decoded/[ISO3]_dictionary.json` |

---

## After completing this skill

The JSON output is ready for downstream use. Reference it as:
```
data availability/decoded/[ISO3]_dictionary.json
```

- **For the feasibility assessment agent:** pass this path as the input dictionary to evaluate which HDMF variables can be constructed.
- **For the survey_mapper agent:** this JSON provides the raw variable list to map against HDMF targets; it replaces the need to manually open the raw dictionary file.
- **For the orchestrator:** confirm that `variables` is non-empty before proceeding to harmonization. If empty (NO_DOCUMENTATION), flag the country as not yet ready.

---

## Troubleshooting common issues

| Symptom | Likely cause | Action |
|---------|-------------|--------|
| `variables: []` and no ERROR notes | Folder empty or all files unsupported | Add documentation files to `data availability/[iso3]/` |
| `UNKNOWN layout` in decode_notes | XLSX column headers don't match any known pattern | Open the file manually, identify columns, report to update `parse_xlsx.py` |
| Very low variable count for an XLSX | Header row not detected correctly | Check `_find_header_row` scan limit; may need to adjust `max_scan` |
| PDF gives 0 variables | Classified as BULLETIN | Open PDF manually; if it's a questionnaire or has a variable table, report classification error |
| `odfpy` ImportError | Library not installed | `pip install odfpy` |
| `pdfplumber` ImportError | Library not installed | `pip install pdfplumber` |
