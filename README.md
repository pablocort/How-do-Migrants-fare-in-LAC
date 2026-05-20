# How do Migrants Fare in LAC?

**A reproducible harmonization and analysis system for comparing labor market outcomes, education, and income of migrants vs. native-born populations across Latin America and the Caribbean.**

Developed at the Inter-American Development Bank (IDB) — Pablo Cortés Sánchez.

---

## What this repo does

This system takes heterogeneous national household surveys from 12+ countries across LAC and the United States, harmonizes them into a single common schema, and produces comparable indicators across migrant and native-born populations.

The core analytical question: **how do migrants fare in the LAC labor market relative to natives?** — across employment, formality, education, occupation, overqualification, and income dimensions.

The pipeline is two-stage:
1. **Stata harmonization** — country-specific `.do` scripts transform raw survey microdata into a standard `*_BID.dta` file
2. **Python analysis** — `scripts/python/hdmf_2.py` loads all harmonized files, computes weighted indicators, and writes output tables and charts

---

## Countries and surveys covered

| Country | Code | Survey | Waves harmonized | Status |
|---------|------|--------|-----------------|--------|
| Colombia | COL | GEIH (DANE) | 2018t3 – 2025t3 (8 waves) | Done |
| Chile | CHL | CASEN | 2024a | Done |
| Ecuador | ECU | ENEMDU | 2025m12 (+ 2018–2024 scripts ready) | Done |
| Peru | PER | ENAHO | 2024a | Done |
| United States | USA | IPUMS ACS | 2024a | Done |
| Spain | ESP | EPA | 2018a – 2025a (8 waves) | Done |
| Dominican Republic | DOM | ENFT | 2018t4 – 2024t4 (7 waves) | Done |
| Belize | BLZ | LFS | 2024m9 | Done |
| Barbados | BRB | LFS | 2023a | Done |
| Mexico | MEX | ENOE | 2025t4 | In progress |
| Suriname | SUR | ABS | 2022a | In progress |
| Brazil | BRA | SISMIGRA | 2025 | Not started |

Period codes: `a` = annual, `t3` = Q3, `m12` = December.

---

## Repository structure

```
How-do-Migrants-fare-in-LAC/
├── harmonization_System/          ← AI-assisted harmonization workflow
│   ├── GUIDE.md                   ← Full pipeline documentation (start here)
│   ├── agents/                    ← Agent prompts: orchestrator, survey_mapper, stata_generator, validator, qa_analyst
│   ├── skills/                    ← Skill modules: demographics, labor, education, migration, income, anomaly detection
│   ├── inputs/                    ← variable_codebook.md, survey metadata templates, inputs_summary.md
│   ├── codebooks/                 ← Harmonization decisions per country-wave
│   └── example/                   ← Colombia GEIH end-to-end walkthrough
├── do armo/                       ← Stata harmonization scripts by country
│   ├── col/                       ← COL_*_variablesBID.do (8 waves)
│   ├── chl/, ecu/, per/, usa/, esp/, mex/, blz/, brb/, dom/, sur/
├── scripts/python/                ← Analysis and utility Python scripts
│   ├── hdmf_build.py              ← Builds the analytical cache (_hdmf_cache.pkl) from all *_BID.dta files
│   ├── hdmf_2.py                  ← Main analysis pipeline: weighted indicators + charts
│   ├── hdmf_trends.py             ← Time-series indicator tables by country
│   ├── hdmf_trends_charts.py      ← Trend charts per country
│   └── functions.py               ← Shared utility functions (weighted stats, pivots, charts)
├── bases armo/armo/               ← Harmonized output .dta files (gitignored — derived from licensed data)
│   └── [ISO3]/                    ← One subfolder per country: COL/, CHL/, ECU/, PER/, USA/, ESP/, DOM/, BLZ/, BRB/
├── bases armo/raw/                ← Raw survey data (gitignored — licensed microdata)
├── data availability/             ← Survey feasibility & migration variable availability project
│   ├── decode_dictionaries.py     ← Decode country variable dictionaries
│   └── build_migration_table_v2.py ← Build migration variable availability matrix
└── out/                           ← Output indicators and figures
```

---

## Standard HDMF variable schema

Every harmonized dataset (`*_BID.dta`) contains these variables:

| Domain | Variables |
|--------|-----------|
| Identifiers & weights | `pais_c`, `idh_ch`, `idp_ci`, `factor_ci`, `factor_ch` |
| Demographics | `edad_ci`, `sexo_ci`, `relacion_ci`, `miembros_ci` |
| Migration | `migrante_ci`, `mig_pais_ci`, `migrantiguo5_ci` |
| Employment status | `condocup_ci`, `emp_ci`, `desemp_ci`, `pea_ci` |
| Job characteristics | `formal_ci`, `tipocontrato_ci`, `horaspri_ci`, `horastot_ci`, `cotizando_ci`, `afiliado_ci`, `ocupa_ci`, `overqualified_ci` |
| Education | `aedu_ci`, `edu_isced`, `edu_hdmf` |
| Income | `ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`, `remesas_ci`, `remesas_ch` |

Full definitions, valid ranges, and country-specific notes: [`harmonization_System/inputs/variable_codebook.md`](harmonization_System/inputs/variable_codebook.md)

---

## Harmonization pipeline

The pipeline has 8 steps, fully documented in [`harmonization_System/GUIDE.md`](harmonization_System/GUIDE.md):

```
1. Choose scope          → country + period(s)
2. Check inputs          → raw data, merge .do, variables .do, lookup files
3. Select reference codes → migration, education, labor, ID coding decisions
4. Prepare metadata      → fill survey_metadata_template.md
4.5 Dictionary check    → Python: cross-wave variable existence check
5. Map variables         → survey_mapper agent → variable crosswalk
5.5 Mapping review      → mapping_checker agent → adversarial challenge report
6. Generate Stata script → stata_generator agent (new survey) or clone+edit (new wave)
7. Run & validate        → validator agent
8. Analyze               → hdmf_build.py → hdmf_2.py → indicator tables + charts
```

---

## AI agent system

The `harmonization_System/` directory contains prompt files that activate Claude Code agents at each pipeline step.

| Agent | File | Role |
|-------|------|------|
| Orchestrator | [`agents/orchestrator.md`](harmonization_System/agents/orchestrator.md) | Master coordinator |
| Survey mapper | [`agents/survey_mapper.md`](harmonization_System/agents/survey_mapper.md) | Raw → HDMF variable crosswalk |
| Mapping checker | [`agents/mapping_checker.md`](harmonization_System/agents/mapping_checker.md) | Adversarial review (HIGH/MEDIUM/LOW risk) |
| Stata generator | [`agents/stata_generator.md`](harmonization_System/agents/stata_generator.md) | Generates Stata .do scripts |
| Validator | [`agents/validator.md`](harmonization_System/agents/validator.md) | Validates harmonized datasets |
| QA Analyst | [`agents/qa_analyst.md`](harmonization_System/agents/qa_analyst.md) | Detects anomalies in trend outputs, diagnoses root cause, proposes fixes |
| Indicator analyst | [`agents/indicator_analyst.md`](harmonization_System/agents/indicator_analyst.md) | Interprets output indicators |

Skills (focused modules called within agent conversations):

| Skill | Purpose |
|-------|---------|
| `skills/map_demographics.md` | Demographics variable mapping |
| `skills/map_labor.md` | Labor market variable mapping |
| `skills/map_education.md` | Education variable mapping |
| `skills/map_migration.md` | Migration variable mapping |
| `skills/map_income.md` | Income variable mapping |
| `skills/create_codebook.md` | Generates harmonization codebook per country-wave |
| `skills/variable_alternatives.md` | When standard variable is missing: alternative construction |
| `skills/detect_anomalies.md` | Scans trend Excel for suspicious values |
| `skills/diagnose_harmonization.md` | Root-cause check in Stata .do files |
| `skills/propose_fix.md` | Formats fix proposals as structured table |

---

## Quick start

```bash
git clone https://github.com/pablocort/How-do-Migrants-fare-in-LAC.git
cd How-do-Migrants-fare-in-LAC

# Install Python dependencies
pip install pandas pyreadstat matplotlib openpyxl scipy

# 1. Build the analytical cache (requires harmonized *_BID.dta files)
python scripts/python/hdmf_build.py

# 2. Run the analysis pipeline
python scripts/python/hdmf_2.py
```

Output tables and charts are written to `out/indicator_descriptive/[DATE]/`.

To add a new country or wave: follow the 8-step pipeline in [`harmonization_System/GUIDE.md`](harmonization_System/GUIDE.md).

---

## Data availability

Raw survey microdata is **not included** in this repo — it is licensed from national statistical offices. To reproduce the full analysis you need:

| Country | Survey | Source |
|---------|--------|--------|
| Colombia GEIH | DANE | [microdatos.dane.gov.co](https://microdatos.dane.gov.co) |
| Chile CASEN | MDS | [observatorio.ministeriodesarrollosocial.gob.cl](https://observatorio.ministeriodesarrollosocial.gob.cl) |
| Ecuador ENEMDU | INEC | [anda.inec.gob.ec](https://anda.inec.gob.ec) |
| Peru ENAHO | INEI | [iinei.inei.gob.pe/microdatos](http://iinei.inei.gob.pe/microdatos/) |
| USA ACS | IPUMS | [ipums.org/usa](https://ipums.org/usa) |
| Spain EPA | INE | [ine.es](https://www.ine.es) |
| Dominican Republic ENFT | ONE | [one.gob.do](https://www.one.gob.do) |

---

## Tech stack

- **Stata** — harmonization scripts (`*_variablesBID.do`)
- **Python** — cache builder (`hdmf_build.py`), analysis pipeline (`hdmf_2.py`), trend engine (`hdmf_trends.py`)
- **Claude Code** — AI-assisted variable mapping, script generation, and validation
- **Git** — version control for all code and documentation

---

## Citation

If you use this system or build on it, please cite:

> Cortés Sánchez, P. (2026). *How do Migrants Fare in LAC? A harmonized household survey system for comparative migration analysis*. Inter-American Development Bank. GitHub: https://github.com/pablocort/How-do-Migrants-fare-in-LAC

---

## License

MIT License — see [LICENSE](LICENSE) for details.

The license covers code and documentation in this repository. Survey microdata is governed by the terms of each national statistical office.
