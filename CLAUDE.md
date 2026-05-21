# HDMF — How do Migrants Fare in LAC

## Project goal

Compare labor market outcomes, education, and income of **migrants vs. native-born** populations across Latin American and Caribbean (LAC) countries. The analytical question is: **"How do migrants fare in LAC?"**

The pipeline harmonizes heterogeneous national household surveys into a single common structure, then runs a Python analysis to produce indicator tables and figures.

---

## Repository layout

```
How-do-Migrants-fare-in-LAC/
├── bases armo/
│   ├── raw/                    ← Raw survey data by country (col/, chl/, ecu/, per/, usa/, ...)
│   └── armo/                   ← Harmonized output files, one subfolder per country (COL/, CHL/, ...) + hdmf_2.py
├── do armo/                    ← Stata harmonization scripts by country
│   ├── col/                    ← COL_*_mergeBID.do  +  COL_*_variablesBID.do
│   ├── chl/, ecu/, per/, usa/, esp/, mex/
├── harmonization_System/       ← AI-assisted workflow system (agents, skills, reference docs)
│   ├── GUIDE.md                ← Full pipeline documentation — read this first
│   ├── agents/                 ← Agent system prompts (orchestrator, survey_mapper, stata_generator, validator, indicator_analyst)
│   ├── skills/                 ← Focused skill modules (map_labor, map_education, map_migration, map_demographics, map_income)
│   ├── inputs/                 ← variable_codebook.md, survey_metadata_template.md, inputs_summary.md
│   └── example/                ← colombia_geih_walkthrough.md (end-to-end reference)
├── data availability/          ← Survey feasibility & migration variable availability project
│   ├── CLAUDE.md               ← Data availability project instructions
│   ├── PROCEDURES.md           ← System documentation (parsers, keyword logic)
│   ├── decode_dictionaries.py  ← Decode local country folders → decoded/ (single-year, per country)
│   ├── build_migration_table_v2.py ← Build migration_variable_availability_v2.xlsx from decoded/
│   ├── scan_and_decode_network.py  ← NEW: scan IDB network share → decoded_ts/ (time series, all countries)
│   ├── build_timeseries_table.py   ← NEW: build migration_timeseries_table.xlsx from decoded_ts/ + raw N obs
│   ├── decoded/                ← Single-year decoded JSONs (one per country)
│   ├── decoded_ts/             ← Time-series decoded JSONs (one per country-year-period)
│   ├── [iso3]/                 ← Local documentation files per country
│   └── parsers/                ← PDF/XLSX/ODS parser modules
└── out/                        ← Output indicators and figures
```

### Network share (IDB) — survey documentation
```
\\sapidbshares.file.core.windows.net\idbshares\SURVEYS\survey\[ISO3]\[SURVEY]\[YEAR]\[PERIOD]\docs\
```
Accessible from bash as `//sapidbshares.file.core.windows.net/idbshares/SURVEYS/survey/`.
Contains variable dictionaries, questionnaires, and codebooks for 27 LAC countries.
Used by `scan_and_decode_network.py` to build the time-series availability table.

---

## Countries and status

| Country | Code | Survey | Period | Status |
|---------|------|--------|--------|--------|
| Chile | CHL | CASEN | 2024a | Done |
| Colombia | COL | GEIH | 2024t3 | Done (output in subdirectory — needs move) |
| Colombia | COL | GEIH | 2025t3 | Done |
| Ecuador | ECU | ENEMDU | 2025m12 | Done |
| Peru | PER | ENAHO | 2024a | Done |
| United States | USA | IPUMS ACS | 2024a | Done |
| Ecuador | ECU | ENEMDU | 2024m12 | In progress (data still zipped) |
| Spain | ESP | EPA | 2025t3 | In progress (script has errors) |
| Mexico | MEX | ENOE | 2025t4 | In progress (variables script missing) |
| Colombia | COL | GEIH | 2023t3 | Not started (raw exists, no script) |
| Brazil | BRA | SISMIGRA | 2025 | Not started |

> Full details and pending actions: `harmonization_System/inputs/inputs_summary.md`

---

## Parallelism — always run independent tasks simultaneously

Claude must run all independent tasks in parallel, not sequentially. This makes the session significantly faster and is always preferred.

| Situation | What to do |
|-----------|-----------|
| Multiple Stata `.do` files for different countries | Launch all as separate background processes at once |
| Multiple Stata `.do` files for the same country (different waves) | Launch all at once — they read/write different files |
| `hdmf_trends.py` for multiple countries | Run all `--country` calls simultaneously in background |
| `hdmf_trends_charts.py` for multiple countries | Run all `--country` calls simultaneously in background |
| Editing files + running a background script | Do both in the same response |
| Reading multiple independent files | Issue all `Read` calls in one message |

**Rule:** before launching any script, ask — does anything else start at the same time? If yes, launch together. Only wait (sequentially) when a script genuinely depends on the output of a previous one (e.g., `hdmf_trends.py` requires `hdmf_build.py` to finish first).

---

## Tool split: Python vs Stata

| Phase | Tool | Rationale |
|-------|------|-----------|
| Pre-harmonization (variable check, codebook parsing, cross-wave comparison) | **Python** | `dictionary_check.py` reads .dta without Stata; greps reference package; produces structured reports |
| Harmonization (producing `_BID.dta`) | **Stata** | All `_variablesBID.do` scripts |
| Analysis (indicators, charts) | **Python** | `hdmf_2.py` |

## Session startup — read all MD files first

At the start of every session, Claude **must** read all `.md` files in the project before doing anything else:
- `CLAUDE.md` (this file)
- `harmonization_System/GUIDE.md`
- `harmonization_System/inputs/variable_codebook.md`
- `harmonization_System/inputs/inputs_summary.md`
- Any `harmonization_System/inputs/*_metadata.md` relevant to the active country/period
- Any `harmonization_System/codebooks/harmonization_codebook_*.md` relevant to the active country/period

If the user specifies a particular MD file, read that one. Otherwise read **all** of the above by default. Never skip this step — these files contain the authoritative decisions, variable definitions, and pipeline status.

---

## Harmonization pipeline (overview)

```
0. Read all MD files     → CLAUDE.md, GUIDE.md, variable_codebook.md, inputs_summary.md,
                           any country metadata and codebook files (see Session startup above)
1. Choose scope          → country + period(s)
2. Check inputs          → raw data, merge .do, variables .do, lookup files
                           confirm alternative_do_files/ exists in raw/[ISO3]/
3. Select reference codes → migration, education, labor, ID coding decisions (document them)
4. Prepare metadata      → fill inputs/survey_metadata_template.md → saves as inputs/[ISO3]_[PERIOD]_metadata.md
4.5. Dictionary check   → Python: run dictionary_check.py on all waves
                          → if variable missing: apply skills/variable_alternatives.md
                            (check alternative_do_files/ first, then codebook)
                          → saves as inputs/[ISO3]_dictionary_check_[PERIODS].md
5. Map variables         → use agent: survey_mapper
                          → each entry annotated: STABLE / ALTERNATIVE:[var] / DERIVED / NOT AVAILABLE
6. Generate Stata script → use agent: stata_generator (new survey) OR clone+edit existing (same survey, new wave)
7. Run & validate        → use agent: validator
8. Analyze               → run hdmf_2.py, use agent: indicator_analyst
```

For cloning an existing script (Step 6, same survey new wave):
- Dictionary check first (Python): confirm variable names and category codes are unchanged in the new wave
- Change exactly 3 references: `local ANO`, input path, and output path
- For any missing variable: add ALTERNATIVE construction block using `skills/variable_alternatives.md`
- Document all differences with inline Stata comment blocks (see `variable_alternatives.md` comment format)

Full pipeline with all decision checkpoints: `harmonization_System/GUIDE.md`

---

## Key conventions

### File naming
- Scripts: `[ISO3]_[PERIOD]_variablesBID.do` — e.g., `COL_2025t3_variablesBID.do`
- Output data: `[ISO3]_[PERIOD]_BID.dta` — e.g., `COL_2025t3_BID.dta`
- Period codes: `2024t3` (quarterly), `2024m12` (monthly), `2024a` (annual)
- All output files must be in `bases armo/armo/[ISO3]/` (one subfolder per country, e.g. `armo/COL/`, `armo/CHL/`) — `hdmf_2.py` walks all country subfolders automatically

### Variable naming
- Suffix `_ci`: individual-level variable (e.g., `edad_ci`)
- Suffix `_ch`: household-level variable (e.g., `factor_ch`)
- Binary variables: `1 = yes`, `0 = no`, `.` = missing — never use -1, 99, or 2 for "no"
- Monetary values: nominal local currency units (no deflation at harmonization stage)

### Mandatory line in every generated .do file
Every Stata script created or modified by Claude must include this line immediately after `set more off`:
```stata
di "File created with the Claude HDMF system — YYYY-MM-DD"
```

### Log files
Every harmonization script must open a log file at the start and close it at the end. Log path convention:
```stata
local log_dir "do armo/[iso3 lowercase]/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/[ISO3]_[period]_variablesBID.log", replace
```
Log close at the bottom:
```stata
log close
```
Logs are stored in `do armo/[iso3]/logs/` — **never** in the project root or in `bases armo/`. When a script is run from a different working directory, the relative path `do armo/...` must be adjusted to the absolute equivalent. The `capture mkdir` ensures the folder is created automatically.

---

## Standard HDMF variables (all harmonized datasets must contain these)

| Domain | Variables |
|--------|-----------|
| Identifiers & weights | `pais_c`, `idh_ch`, `idp_ci`, `factor_ci`, `factor_ch` |
| Demographics | `edad_ci`, `sexo_ci`, `relacion_ci`, `miembros_ci` |
| Migration | `migrante_ci`, `mig_pais_ci`, `migrantiguo5_ci` |
| Employment status | `condocup_ci`, `emp_ci`, `desemp_ci`, `pea_ci` |
| Job characteristics | `formal_ci`, `tipocontrato_ci`, `horaspri_ci`, `horastot_ci`, `cotizando_ci`, `afiliado_ci` |
| Education | `aedu_ci`, `edu_isced`, `edu_hdmf` |
| Income | `ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`, `remesas_ci`, `remesas_ch` |

Full definitions and valid ranges: `harmonization_System/inputs/variable_codebook.md`

---

## Analysis pipeline — hdmf_2.py

Located at `bases armo/armo/hdmf_2.py`. Loads all `*_BID.dta` files from `bases armo/armo/` root, computes weighted indicators, and writes output to `out/indicator_descriptive/`.

Key functions imported from `functions.py`:
- `make_weighted_stats_multi` — weighted statistics by group
- `make_weighted_pivot_multi` — pivot tables
- `plot_scatter_stats`, `plot_labor_stats` — standard charts
- `check_update` — data freshness checks

Analytical groups used: `migrante_ci` (0=native, 1=migrant), `sexo_ci`, `edu_hdmf`, age brackets.

---

## AI agent system

The `harmonization_System/` directory contains prompt files for AI-assisted harmonization. Agents are invoked by pasting their markdown content into a Claude conversation.

| Agent | File | Role |
|-------|------|------|
| Orchestrator | `agents/orchestrator.md` | Master coordinator |
| Survey mapper | `agents/survey_mapper.md` | Raw → HDMF variable crosswalk |
| Stata generator | `agents/stata_generator.md` | Generates .do scripts |
| Validator | `agents/validator.md` | Validates harmonized .dta |
| Indicator analyst | `agents/indicator_analyst.md` | Interprets output indicators |
| **QA Analyst** | **`agents/qa_analyst.md`** | **Backward engineering: scans trend outputs for anomalies, diagnoses root cause (harmonization or indicator calc), proposes fixes for user approval** |

Skills are focused prompt modules called within agent conversations:

| Skill | File | Role |
|-------|------|------|
| Map demographics | `skills/map_demographics.md` | Demographics variable mapping |
| Map labor | `skills/map_labor.md` | Labor market variable mapping |
| Map education | `skills/map_education.md` | Education variable mapping |
| Map migration | `skills/map_migration.md` | Migration variable mapping |
| Map income | `skills/map_income.md` | Income variable mapping |
| Create codebook | `skills/create_codebook.md` | Generates `harmonization_codebook_[ISO3]_[PERIOD].md` |
| Dictionary check | `skills/dictionary_check.md` | Cross-wave variable existence check; opens DTA/PDF/Excel/Word dictionaries; produces `[ISO3]_dictionary_check_[PERIODS].md` |
| Variable alternatives | `skills/variable_alternatives.md` | When standard variable is missing: search reference package → codebook → construct alternative; documents substitutions inline |
| **Detect anomalies** | **`skills/detect_anomalies.md`** | **Scans trend Excel for suspicious values (boundary rates, implausible ranges, large jumps); produces Detection Table** |
| **Diagnose harmonization** | **`skills/diagnose_harmonization.md`** | **Given an anomaly, checks Stata .do file and variable dictionary for root cause** |
| **Diagnose indicator** | **`skills/diagnose_indicator.md`** | **Given an anomaly cleared by harmonization check, investigates Python calculation code** |
| **Propose fix** | **`skills/propose_fix.md`** | **Formats approved-or-pending fix proposals as a structured table; coordinates re-run plan** |

Codebook output files are saved in `harmonization_System/codebooks/`.

---

## Key reference files

| File | Purpose |
|------|---------|
| `harmonization_System/GUIDE.md` | Full pipeline with all steps and decision checkpoints |
| `harmonization_System/inputs/variable_codebook.md` | All HDMF variable definitions |
| `harmonization_System/inputs/inputs_summary.md` | Current status of all waves + pending actions |
| `harmonization_System/example/colombia_geih_walkthrough.md` | End-to-end worked example (COL GEIH) |
