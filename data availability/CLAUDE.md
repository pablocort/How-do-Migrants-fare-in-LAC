# Data Availability — Survey Feasibility Project

## Project goal

Map what is **analytically possible** across LAC household surveys without loading the microdata.
The core question: for each country and survey, which HDMF variables can be constructed, which require workarounds, and which are simply unavailable?

All conclusions must be grounded in **metadata only**: variable dictionaries, questionnaires, codebooks, and documentation files stored in this folder. Do not attempt to read or load the actual survey databases.

---

## Folder layout

```
data availability/
├── CLAUDE.md          ← this file
├── arg/               ← Argentina  — EPH
├── blz/               ← Belize     — (pending)
├── bol/               ← Bolivia    — EH
├── bra/               ← Brazil     — PNADC
├── chl/               ← Chile      — CASEN
├── col/               ← Colombia   — GEIH
├── cri/               ← Costa Rica — ENAHO
├── dom/               ← Dominican Republic
├── ecu/               ← Ecuador    — ENEMDU
├── gtm/               ← Guatemala  — ENEIC
├── guy/               ← Guyana     — GLFS
├── hnd/               ← Honduras   — EPHPM
├── hti/               ← Haiti      — DHS
├── jam/               ← Jamaica    — (pending)
└── mex/               ← Mexico     — ENOE
```

Each subfolder contains one or more of:
- **Excel/ODS dictionaries** (variable names, labels, value codes)
- **PDF questionnaires** (question wording, skip logic)
- **PDF/Word codebooks** (field descriptions, universe filters)

---

## HDMF standard variables to assess

These are the variables every harmonized dataset must contain. The feasibility analysis asks: can each one be built from the available dictionary?

| Domain | Variables |
|--------|-----------|
| Identifiers & weights | `pais_c`, `idh_ch`, `idp_ci`, `factor_ci`, `factor_ch` |
| Demographics | `edad_ci`, `sexo_ci`, `relacion_ci`, `miembros_ci` |
| Migration | `migrante_ci`, `mig_pais_ci`, `migrantiguo5_ci` |
| Employment status | `condocup_ci`, `emp_ci`, `desemp_ci`, `pea_ci` |
| Job characteristics | `formal_ci`, `tipocontrato_ci`, `horaspri_ci`, `horastot_ci`, `cotizando_ci`, `afiliado_ci` |
| Education | `aedu_ci`, `edu_isced`, `edu_hdmf` |
| Income | `ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`, `remesas_ci`, `remesas_ch` |

Full definitions: `../harmonization_System/inputs/variable_codebook.md`

---

## Feasibility classification

For each variable × country, assign one of four statuses:

| Status | Meaning |
|--------|---------|
| **DIRECT** | A raw variable maps to the HDMF target with no transformation |
| **DERIVED** | The variable must be constructed from two or more raw variables, but the inputs exist |
| **ALTERNATIVE** | The exact concept is missing; a proxy variable can substitute (document the proxy) |
| **NOT AVAILABLE** | The concept is absent from the survey with no viable substitute |

---

## How to conduct a feasibility assessment

### Step 1 — Read all dictionaries for the country
Open every file in the country subfolder. For Excel/ODS: read column headers and a sample of rows. For PDF: scan the variable list or question index.

### Step 2 — Match raw variables to HDMF targets
Go through each HDMF standard variable. Search the dictionary for variables covering the same concept. Use label text, not just variable names.

### Step 3 — Classify and document
For each HDMF variable record:
- Status (DIRECT / DERIVED / ALTERNATIVE / NOT AVAILABLE)
- Raw variable name(s) in the source survey
- Notes on category codes, universe restrictions, or caveats
- If ALTERNATIVE: what proxy is used and why

### Step 4 — Produce a feasibility report
Output a structured markdown table with one row per HDMF variable and columns:
`variable | status | raw_source | notes`

### Step 5 — Summarize coverage
After the table, write a short paragraph: which analytical comparisons are feasible for this country, and which are not.

---

## Key constraints and conventions

- **Metadata only.** Never load `.dta`, `.sav`, `.csv`, or any microdata file. All conclusions come from dictionaries and questionnaires.
- **Decoded files only — no general survey knowledge.** Every claim about variable availability must be traceable to a file in this folder (a raw dictionary/questionnaire file or a decoded JSON in `decoded/`). Do NOT use general knowledge about what a survey "typically" includes, what a standard DHS module contains, or what variables "are known to exist" from prior experience. If it is not in a file in this folder, it is NOT FOUND — period. This rule applies to all outputs: Excel tables, markdown reports, and any other deliverable.
- **Language.** Dictionaries may be in Spanish, Portuguese, English, or French. Read them as-is; do not require translation before proceeding.
- **File formats.** Excel (`.xlsx`, `.xls`), ODS, PDF. Use Read for PDF; for Excel/ODS describe what columns and sheets are present before drawing conclusions.
- **Missing files.** If a subfolder is empty or has no dictionary, record the country as `NO DOCUMENTATION` and note what type of file would be needed.
- **Cross-country consistency.** When the same concept is covered differently across surveys, document the difference — this informs how comparable the resulting indicators will be.

---

## Parallelism rule

When assessing multiple countries, read their dictionaries in parallel (one Read call per file, all in the same message). Never process countries sequentially when they are independent.

---

## Output conventions

Feasibility reports are saved in this folder as:
```
[ISO3]_feasibility.md       ← per-country report
summary_feasibility.md      ← cross-country comparison table
```

The cross-country summary table has one column per country and one row per HDMF variable, with the status codes (D / V / A / N) as cell values.

---

## Time-series availability pipeline (network share)

A second pipeline reads documentation files directly from the IDB network share and produces a year-by-year migration variable availability table covering all LAC countries from 2015+.

### Network share path
```
\\sapidbshares.file.core.windows.net\idbshares\SURVEYS\survey\[ISO3]\[SURVEY]\[YEAR]\[PERIOD]\docs\
```
Accessible as a UNC path from bash: `//sapidbshares.file.core.windows.net/idbshares/SURVEYS/survey/`

### Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `scan_and_decode_network.py` | Scan docs/ on network share → decode best file per country-year → save to `decoded_ts/` | `python scan_and_decode_network.py` |
| `build_timeseries_table.py` | Read `decoded_ts/` JSONs + get N obs from HDMF raw data → `migration_timeseries_table.xlsx` | `python build_timeseries_table.py` |

### Country–survey mapping (primary labor force survey per country)

| ISO3 | Country | Survey |
|------|---------|--------|
| ARG | Argentina | EPHC |
| BOL | Bolivia | ECH |
| BRA | Brazil | PNADC |
| CHL | Chile | CASEN |
| COL | Colombia | GEIH |
| CRI | Costa Rica | ENAHO |
| DOM | Dominican Rep. | ENCFT |
| ECU | Ecuador | ENEMDU |
| GTM | Guatemala | ENEIC |
| GUY | Guyana | LFS |
| HND | Honduras | EPHPM |
| JAM | Jamaica | LFS |
| MEX | Mexico | ENOE |
| PER | Peru | ENAHO |
| PRY | Paraguay | EPH |
| SLV | El Salvador | EHPM |
| URY | Uruguay | ECH |
| VEN | Venezuela | EHM |

### File ranking (best doc per docs/ folder)
1. `.xlsx/.xls` with "diccionario"/"dictionary" in name → DICT_XLSX (best)
2. `.ods` → ODS
3. `.xlsx/.xls` (any) → XLSX
4. `.pdf` with "diccionario"/"dictionary" in name → DICT_PDF
5. `.pdf` with "cuestionario"/"formulario" in name → QUESTIONNAIRE_PDF
6. `.pdf` tech sheet → FICHA_PDF
7. `.pdf` other → skipped (bulletins, methodology reports)

Period selection: picks the period whose docs/ folder has the best-ranked file (DICT_XLSX in t3 beats questionnaire PDF in a).

### Decoded outputs
- `decoded_ts/[ISO3]_[YEAR][PERIOD]_dictionary.json` — one JSON per country-year-period
- `migration_timeseries_table.xlsx` — final Excel with time series

### N observations (HDMF countries only)
Populated from raw `.dta` files in `bases armo/raw/` using `pyreadstat.read_dta(metadataonly=True)`.
Countries: COL, ECU, PER, CHL, MEX, USA, ESP.

### How to re-run after new data arrives
```bash
# Re-decode a single country (e.g. after new docs added to network share)
python scan_and_decode_network.py --country COL --force

# Rebuild Excel only (no re-decode needed)
python build_timeseries_table.py
```

---

## Relation to the main HDMF pipeline

This project is upstream of the harmonization pipeline (`../harmonization_System/`). Its outputs inform:
1. Which countries are viable candidates for a new harmonization wave
2. Which HDMF variables will require ALTERNATIVE coding blocks in the Stata scripts
3. Which analytical comparisons can be safely included in cross-country figures

When a country moves to active harmonization, its feasibility report becomes an input to the survey mapper agent (`../harmonization_System/agents/survey_mapper.md`).
