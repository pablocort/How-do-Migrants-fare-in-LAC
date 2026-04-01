# HDMF Harmonization System — User Guide

## What is this system?

This ecosystem provides AI-assisted workflows to harmonize household surveys from different countries into a common analytical structure. The goal is to answer: **"How do migrants fare in LAC countries?"**

The system supports the **How do Migrants Fare (HDMF)** project, which compares labor market outcomes, education, and income across native and migrant populations in Latin America and the Caribbean.

---

## Architecture

```
harmonization_System/
├── GUIDE.md                        ← You are here
├── MEMORY.md                       ← Lessons, quirks, decisions not in other files
├── agents/                         ← AI agent system prompts
│   ├── orchestrator.md             ← Master coordinator
│   ├── survey_mapper.md            ← Maps raw variables to HDMF standard
│   ├── stata_generator.md          ← Generates Stata .do harmonization scripts
│   ├── validator.md                ← Validates harmonized datasets
│   └── indicator_analyst.md        ← Interprets output indicators
├── skills/                         ← Focused prompt modules (called by agents)
│   ├── map_education.md
│   ├── map_labor.md
│   ├── map_migration.md
│   ├── map_demographics.md
│   ├── map_income.md
│   └── create_codebook.md          ← Builds harmonization_codebook_[ISO3]_[PERIOD].md
├── inputs/                         ← Templates and reference documents
│   ├── variable_codebook.md        ← HDMF standard variable definitions
│   └── survey_metadata_template.md ← Fill this out for each new survey
├── codebooks/                      ← Output: one harmonization_codebook per country-year
└── example/
    └── colombia_geih_walkthrough.md ← End-to-end worked example
```

---

## Harmonization Pipeline

```
1. CHOOSE SCOPE
   Decide which country and year/period combinations to harmonize.
   - Pick country (ISO3 code) and one or more waves (year + period)
   - Period format: 2024t3 (quarterly), 2024m12 (monthly), 2024a (annual)
   - Example: COL — 2023t3, 2024t3, 2025t3
   Reference: inputs/inputs_summary.md for available waves per country.

2. CHECK INPUTS
   For each selected wave, verify all required inputs exist before proceeding.
   Required per wave:
     [ ] Raw data file(s) present in bases armo/raw/[country]/
     [ ] Merge .do script exists (if survey has multiple modules)
     [ ] Variables .do script exists: [ISO3]_[PERIOD]_variablesBID.do
     [ ] Output file does NOT already exist (or is intentionally being rebuilt)
     [ ] Lookup files present (e.g. mig_pais_code.dta, ciuo_cod.xlsx)
   If any input is missing → resolve before continuing to Step 3.
   See inputs/inputs_summary.md for current status of all waves.

3. SELECT REFERENCE CODES
   Before any mapping or script generation, decide which classification systems
   and lookup tables will be used. This is an analytical decision — document it.

   For each domain, confirm the coding scheme to apply:

   MIGRATION
     [ ] Which variable identifies immigrants (e.g. p3373==3 for GEIH)
     [ ] Which lookup table maps origin-country codes to names
         → mig_pais_code.dta (bases armo/raw/col/)
     [ ] Which countries are included in miglac_ci (LAC country list)
     [ ] Definition of migrantiguo5_ci (which variable/codes mark >5 years)

   EDUCATION
     [ ] Which source variable(s) map to edu_hdmf (e.g. p3042 + p3042s1 + p3043)
     [ ] Confirm the 10-category edu_hdmf scheme applies (or document changes)
     [ ] Which variable maps to aedu_ci (years of education)
     [ ] Field-of-study lookup: codigos_formacion.dta / ciuo_cod.xlsx

   LABOR
     [ ] Which flags identify employed/unemployed/inactive
         (e.g. oci, dsi, fft for GEIH — confirm these exist in the raw file)
     [ ] Definition of formal_ci (cotizando + afiliado, or other)
     [ ] Occupation code system: CIUO-08, ISCED-F 2013, or other

   DEMOGRAPHICS / IDENTIFIERS
     [ ] Household ID construction (e.g. idh or DIRECTORIO+SECUENCIA_P)
     [ ] Expansion weight variable (e.g. fex_c18)
     [ ] Age variable (e.g. p6040)

   Output: a short decision record — even a bullet list — confirming the
   coding choices before work begins. Update it if anything changes.

4. PREPARE INPUTS
   Fill out inputs/survey_metadata_template.md with:
   - Country, survey name, reference period
   - Available raw variables and their codes
   - Survey documentation / questionnaire

5. MAP VARIABLES
   Use agent: survey_mapper
   Skills called: map_demographics, map_labor, map_education,
                  map_migration, map_income
   Output: variable_mapping.md (raw var → HDMF var crosswalk)

6. GENERATE STATA CODE
   Two paths depending on whether a prior wave of the same survey exists:

   A) NEW country/survey (no prior .do file):
      Use agent: stata_generator
      Input: variable_mapping.md + survey_metadata
      Output: [COUNTRY]_[PERIOD]_variablesBID.do

   B) SAME survey, new wave (e.g. COL 2023t3 when COL 2025t3 exists):

      BEFORE cloning — dictionary check (required):
        Compare the raw .dta variable list of the new wave against the
        reference script. For each key variable, confirm:
          [ ] Variable name unchanged (e.g. p3042, p6040, fex_c18, oci)
          [ ] Category codes unchanged (esp. education p3042, migration p3373)
          [ ] Derived flags exist (oci, dsi, fft — DANE-computed, may vary)
          [ ] Lookup files are compatible (mig_pais_code.dta codes still valid)
        If any difference found → update the relevant section in the clone
        and document the change with an inline comment in the .do file.

      AFTER dictionary check — clone and edit:
        Clone the most recent wave's variablesBID.do and change 3 references:
          - local ANO "[YEAR]"          ← header section
          - use "...COL_[YEAR]t3.dta"   ← if c(username) block (input path)
          - local ANO "[YEAR]"          ← save section (output path)

   REQUIRED for ALL generated scripts (both paths A and B):
   Add the following line immediately after "set more off":
      di "File created with the Claude HDMF system — [YYYY-MM-DD]"
   Use the actual creation date. This line must appear in every .do file
   generated or modified by Claude.

7. RUN & VALIDATE
   Use agent: validator
   Input: harmonized .dta file
   Output: validation report (ranges, missing rates, label checks)

8. ANALYZE INDICATORS
   Use hdmf_2.py (Python pipeline)
   Use agent: indicator_analyst for interpretation
```

---

## Countries currently in the system

| Country | Survey | Period | Status |
|---------|--------|--------|--------|
| Colombia (COL) | GEIH | 2024a, 2025a | Harmonized |
| Chile (CHL) | CASEN | 2024a | Harmonized |
| Ecuador (ECU) | ENEMDU | 2024a, 2025m12 | Harmonized |
| Peru (PER) | ENAHO | 2024a | Harmonized |
| USA | IPUMS ACS | 2024a | Harmonized |
| Spain (ESP) | EPA | 2025a | Pending |
| Mexico (MEX) | ENOE | 2024a, 2025a | Pending |

**Colombia note:** GEIH is harmonized using the full annual dataset (all 12 months pooled). The period code is `a` (annual), e.g. `COL_2024a`. This uses DANE's `anual_homologado_DANE` base for income variables and appends all 12 monthly module files (m1–m12) for labor market variables. Do not use quarterly subsets (t3) for new waves.

---

## Standard HDMF Variables

All harmonized datasets must contain these variables. See `inputs/variable_codebook.md` for full definitions.

**Identifiers:** `pais_c`, `idh_ch`, `idp_ci`, `factor_ci`, `factor_ch`
**Demographics:** `edad_ci`, `sexo_ci`, `relacion_ci`
**Labor market:** `condocup_ci`, `emp_ci`, `desemp_ci`, `pea_ci`, `formal_ci`, `tipocontrato_ci`, `horaspri_ci`, `horastot_ci`
**Social security:** `cotizando_ci`, `afiliado_ci`
**Education:** `aedu_ci`, `edu_isced`, `edu_hdmf`
**Migration:** `migrante_ci`, `mig_pais_ci`, `migrantiguo5_ci`
**Income:** `ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`, `remesas_ci`, `remesas_ch`

---

## Naming conventions

- Files: `[ISO3]_[PERIOD]_variablesBID.do` and `[ISO3]_[PERIOD]_BID.dta`
- Period format: `2024t3` (quarterly), `2024m12` (monthly), `2024a` (annual)
- All variable names use suffix `_ci` (individual) or `_ch` (household)
- Binary variables: `1 = yes`, `0 = no`, `.` = missing (never use -1 or 99)
- Monetary values: local currency units, nominal (no deflation at harmonization stage)

---

## How to use agents

Each agent in `agents/` is a system prompt. To use one:

1. Open a new Claude conversation
2. Paste the agent's full markdown content as the system prompt (or first user message)
3. Provide the required inputs described in the agent file
4. Follow the output format specified

Agents can call **skills** — paste the relevant skill content into the conversation when the agent requests it.

---

## Quick start: Adding a new country

1. Choose scope — country + waves (pipeline Step 1)
2. Check inputs for each wave (pipeline Step 2) — resolve any missing files
3. Select reference codes — document migration, education, labor, and ID coding decisions (pipeline Step 3)
4. Obtain raw survey data + questionnaire; fill in `inputs/survey_metadata_template.md` (pipeline Step 4)
5. Start a conversation with `agents/survey_mapper.md` (pipeline Step 5)
6. Pass the output to `agents/stata_generator.md` (pipeline Step 6A)
7. Run the generated .do file in Stata
8. Validate with `agents/validator.md` (pipeline Step 7)
9. Add the harmonized `.dta` path to `hdmf_2.py` (pipeline Step 8)

See `example/colombia_geih_walkthrough.md` for a complete demonstration.
