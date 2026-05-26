# How do Migrants Fare in LAC?

**A reproducible harmonization and analysis system for comparing labor market outcomes, education, and income of migrants vs. native-born populations across Latin America and the Caribbean.**

Developed at the Inter-American Development Bank (IDB) — Pablo Cortés Sánchez.

---

## This repository contains two related but independent projects

### Project 1 — HDMF: Migrant vs. Native Labor Market Comparison (main branch)

Harmonizes national household surveys from 12+ LAC countries into a single schema and produces comparable indicators across migrant and native-born populations. The core question: **how do migrants fare in the LAC labor market relative to natives?**

→ [Full documentation below](#hdmf-project)

### Project 2 — Remittances Spillover Analysis (branch: `remittances-spillover`)

Uses the HDMF-harmonized Honduras EPHPM microdata (7 waves, 2018–2025) to test whether remittance inflows generate **local spending multiplier effects** — i.e., do non-receiving households in high-remittance areas earn more? This is a separate analytical question from the migrant/native comparison.

→ [Jump to remittances sub-project](#remittances-spillover-sub-project)

---

## HDMF Project

### What it does

Takes heterogeneous national household surveys and harmonizes them into a single common schema (`*_BID.dta`), then runs a Python analysis pipeline to produce weighted indicator tables and charts comparing migrants vs. native-born workers.

**Pipeline:**
1. **Stata harmonization** — `do armo/[iso3]/[ISO3]_[PERIOD]_variablesBID.do` transforms raw survey data into a standard BID file
2. **Python analysis** — `scripts/python/hdmf_build.py` + `hdmf_2.py` load all harmonized files and produce output tables and charts

### Countries and surveys

| Country | Code | Survey | Waves harmonized | Status |
|---------|------|--------|-----------------|--------|
| Colombia | COL | GEIH (DANE) | 2018t3 – 2025t3 (8 waves) | Done |
| Chile | CHL | CASEN | 2024a | Done |
| Ecuador | ECU | ENEMDU | 2025m12 | Done |
| Peru | PER | ENAHO | 2024a | Done |
| United States | USA | IPUMS ACS | 2024a | Done |
| Spain | ESP | EPA | 2018a – 2025a (8 waves) | Done |
| Dominican Republic | DOM | ENFT | 2018t4 – 2024t4 (7 waves) | Done |
| Belize | BLZ | LFS | 2024m9 | Done |
| Barbados | BRB | LFS | 2023a | Done |
| Mexico | MEX | ENOE | 2025t4 | In progress |
| Suriname | SUR | ABS | 2022a | In progress |
| Brazil | BRA | SISMIGRA | 2025 | Not started |

### Repository structure

```
How-do-Migrants-fare-in-LAC/
├── harmonization_System/          ← AI-assisted harmonization workflow
│   ├── GUIDE.md                   ← Full pipeline documentation (start here)
│   ├── agents/                    ← Agent prompts (orchestrator, survey_mapper, stata_generator, validator, qa_analyst)
│   ├── skills/                    ← Skill modules (demographics, labor, education, migration, income, anomaly detection)
│   ├── inputs/                    ← variable_codebook.md, survey metadata, inputs_summary.md
│   ├── codebooks/                 ← Harmonization decisions per country-wave
│   └── example/                   ← Colombia GEIH end-to-end walkthrough
├── do armo/                       ← Stata harmonization scripts by country
│   ├── col/                       ← COL_*_variablesBID.do (8 waves)
│   ├── hnd/                       ← HND_*_variablesBID.do (7 waves, 2018–2025)
│   ├── chl/, ecu/, per/, usa/, esp/, mex/, blz/, brb/, dom/, sur/
├── scripts/python/                ← Analysis and utility Python scripts
│   ├── hdmf_build.py              ← Builds analytical cache from all *_BID.dta files
│   ├── hdmf_2.py                  ← Main analysis: weighted indicators + charts
│   ├── hdmf_trends.py             ← Time-series indicator tables by country
│   └── functions.py               ← Shared utility functions
├── bases armo/armo/               ← Harmonized *_BID.dta files (gitignored — derived from licensed data)
│   ├── [ISO3]/                    ← One subfolder per country
│   └── hnd_databases.py          ← Builds HND stacked CSV + geographic panel (remittances sub-project)
├── bases armo/raw/                ← Raw survey microdata (gitignored — licensed)
├── data availability/             ← Survey feasibility and migration variable availability project
└── out/                           ← All outputs (gitignored — regenerate with scripts)
```

### Standard HDMF variable schema

Every harmonized dataset (`*_BID.dta`) contains:

| Domain | Variables |
|--------|-----------|
| Identifiers & weights | `pais_c`, `idh_ch`, `idp_ci`, `factor_ci`, `factor_ch` |
| Demographics | `edad_ci`, `sexo_ci`, `relacion_ci`, `miembros_ci` |
| Migration | `migrante_ci`, `mig_pais_ci`, `migrantiguo5_ci` |
| Employment status | `condocup_ci`, `emp_ci`, `desemp_ci`, `pea_ci` |
| Job characteristics | `formal_ci`, `tipocontrato_ci`, `horaspri_ci`, `horastot_ci`, `cotizando_ci`, `afiliado_ci`, `ocupa_ci`, `overqualified_ci` |
| Education | `aedu_ci`, `edu_isced`, `edu_hdmf` |
| Income | `ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`, `remesas_ci`, `remesas_ch` |

Full definitions: [`harmonization_System/inputs/variable_codebook.md`](harmonization_System/inputs/variable_codebook.md)

### Harmonization pipeline (8 steps)

Documented in [`harmonization_System/GUIDE.md`](harmonization_System/GUIDE.md):

```
1. Choose scope          → country + period(s)
2. Check inputs          → raw data, merge .do, variables .do, lookup files
3. Select reference codes → migration, education, labor, ID decisions
4. Prepare metadata      → fill survey_metadata_template.md
4.5 Dictionary check    → Python: cross-wave variable existence check
5. Map variables         → survey_mapper agent → variable crosswalk
6. Generate Stata script → stata_generator (new survey) or clone+edit (new wave)
7. Run & validate        → validator agent
8. Analyze               → hdmf_build.py → hdmf_2.py → indicator tables + charts
```

### AI agent system

| Agent | File | Role |
|-------|------|------|
| Orchestrator | `agents/orchestrator.md` | Master coordinator |
| Survey mapper | `agents/survey_mapper.md` | Raw → HDMF variable crosswalk |
| Stata generator | `agents/stata_generator.md` | Generates Stata .do scripts |
| Validator | `agents/validator.md` | Validates harmonized datasets |
| QA Analyst | `agents/qa_analyst.md` | Detects anomalies in trend outputs, proposes fixes |
| Indicator analyst | `agents/indicator_analyst.md` | Interprets output indicators |

### Quick start

```bash
git clone https://github.com/pablocort/How-do-Migrants-fare-in-LAC.git
cd How-do-Migrants-fare-in-LAC

pip install pandas pyreadstat matplotlib openpyxl scipy

# Build analytical cache (requires harmonized *_BID.dta files)
python scripts/python/hdmf_build.py

# Run analysis pipeline
python scripts/python/hdmf_2.py
```

Output tables and charts are written to `out/indicator_descriptive/[DATE]/`.

---

## Remittances Spillover Sub-project

**Branch:** `remittances-spillover`

**Goal:** Test whether remittance inflows into Honduran departments generate **local spending multiplier effects** — do households in the same department that do *not* receive remittances earn more when remittance intensity in the department is higher?

This is a **separate analytical question** from the main HDMF project. It does not compare migrants vs. natives. It uses the same harmonized HND microdata as its input, but runs a different analysis: area-level panel regressions exploiting geographic variation in remittance penetration across 18 Honduran departments and 7 survey waves (2018–2025).

### Data foundation

The sub-project builds directly on 7 HDMF-harmonized Honduras EPHPM waves:

| Wave | Geographic unit | Remittances | Notes |
|------|----------------|-------------|-------|
| 2018m6 | Department (18) + Municipality | Available | Most granular |
| 2019m6 | Department (18) | Available | |
| 2021m6 | Dominio (5 zones) | Available | No department in raw |
| 2022m6 | Dominio (5 zones) | Not in survey | OIH module absent |
| 2023m6 | Dominio (5 zones) | Available | No department in raw |
| 2024m6 | Department (18) | Available | Fixed this branch |
| 2025m7 | Department (18) | Available | Fixed this branch |

### Output databases (gitignored — regenerate with script)

Two flat files are produced from `bases armo/armo/hnd_databases.py` and stored locally in `out/remittances/data/` (not committed — ~430 MB):

| File | Description | Rows |
|------|-------------|------|
| `HND_all_waves.csv` | All 7 waves stacked, one row per person | 231,029 |
| `HND_panel_geo_year.csv` | Geographic unit × year panel with weighted indicators | 81 |

The panel has 66 department×year rows (2018/2019/2024/2025) and 15 dominio×year rows (2021/2022/2023), with columns covering employment rates, income, remittances, education, poverty, and demographics — all survey-weighted.

To regenerate:
```bash
py "bases armo/armo/hnd_databases.py"
```

### Analysis plan

See [`harmonization_System/inputs/HND_spillover_analysis_plan.md`](harmonization_System/inputs/HND_spillover_analysis_plan.md) for the full design:

- **Step A** — Department-level panel: remittance intensity (`pct_remit_dept`) + non-receiver income (`mean_ylm_nonrecv`)
- **Step B** — Descriptive: scatter plots, correlation table, department ranking
- **Step C** — Panel first-differences regression: Δ income ~ Δ remittance intensity (18 depts, 2018→2019 and 2024→2025)
- **Step D** — IV robustness: Bartik instrument using exchange rate depreciation × pre-existing remittance share
- **Step E** — Heterogeneity by urban/rural, formal/informal, gender of household head

### What was fixed in this branch

All 7 HND harmonization scripts were corrected before running the spillover analysis:

| Wave | Fix |
|------|-----|
| 2018m6 | Added `municipio_c` (municipality identifier) |
| 2019m6 | Fixed `region_c` source: `ine01` → `depto` |
| 2021m6 | Added USD oih components to `ynlm_ci` and `remesas_ci` |
| 2024m6 | Added full OIH income block (was stub `.`) — `ynlm_ci`, `remesas_ci`, `ytot_ci` |
| 2025m7 | Same as 2024 + adds `oih21_lps` (new item in 2025 survey) |
| All 2021–2025 | Fixed systematic `capture clonevar` → `capture replace` bug (variables pre-initialized with `gen X = .` made all `capture clonevar` silently fail) |
| All 2019–2025 | Changed `saveold` → `save, replace` for Stata 19 format compatibility with pyreadstat |

---

## Data availability

Raw survey microdata is **not included** — it is licensed from national statistical offices.

| Country | Survey | Source |
|---------|--------|--------|
| Colombia GEIH | DANE | [microdatos.dane.gov.co](https://microdatos.dane.gov.co) |
| Chile CASEN | MDS | [observatorio.ministeriodesarrollosocial.gob.cl](https://observatorio.ministeriodesarrollosocial.gob.cl) |
| Ecuador ENEMDU | INEC | [anda.inec.gob.ec](https://anda.inec.gob.ec) |
| Peru ENAHO | INEI | [iinei.inei.gob.pe/microdatos](http://iinei.inei.gob.pe/microdatos/) |
| USA ACS | IPUMS | [ipums.org/usa](https://ipums.org/usa) |
| Spain EPA | INE | [ine.es](https://www.ine.es) |
| Dominican Republic ENFT | ONE | [one.gob.do](https://www.one.gob.do) |
| Honduras EPHPM | INE Honduras | [ine.gob.hn](https://www.ine.gob.hn) |

---

## Tech stack

- **Stata** — harmonization scripts (`*_variablesBID.do`)
- **Python** — cache builder, analysis pipeline, spillover regressions
- **Claude Code** — AI-assisted variable mapping, script generation, validation, and QA
- **Git** — version control; `main` for HDMF pipeline, `remittances-spillover` for the HND spillover analysis

---

## Citation

If you use this system or build on it, please cite:

> Cortés Sánchez, P. (2026). *How do Migrants Fare in LAC? A harmonized household survey system for comparative migration analysis*. Inter-American Development Bank. GitHub: https://github.com/pablocort/How-do-Migrants-fare-in-LAC

---

## License

MIT License — see [LICENSE](LICENSE) for details.

The license covers code and documentation in this repository. Survey microdata is governed by the terms of each national statistical office.
