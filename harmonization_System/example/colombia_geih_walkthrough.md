# Worked Example: Colombia GEIH Harmonization

This document walks through the harmonization of the Colombian Gran Encuesta Integrada de Hogares (GEIH), covering all available waves (2023–2025 Q3), and serves as the reference example for the full pipeline.

---

## Step 0 — Choose Scope and Check Inputs

### 0a. Chosen scope

```
Country:  Colombia (COL)
Survey:   Gran Encuesta Integrada de Hogares (GEIH) — DANE
Waves:    2023 Q3 (2023t3), 2024 Q3 (2024t3), 2025 Q3 (2025t3)
Goal:     Produce COL_2023t3_BID.dta, COL_2024t3_BID.dta, COL_2025t3_BID.dta
          in bases armo/armo/ (root, not subdirectory)
```

### 0b. Input check — Colombia GEIH

| Wave | Raw file | Merge script | Variables script | Output in `armo/` | Status |
|------|----------|-------------|-----------------|-------------------|--------|
| 2023 Q3 | `raw/col/COL_2023t3.dta` ✅ | not needed | ❌ missing | ❌ missing | ❌ Script must be written |
| 2024 Q3 | `raw/col/COL_2024t3.dta` ✅ | `COL_2024t3_mergeBID.do` ✅ | `COL_2024t3_variablesBID.do` ✅ | ⚠️ in `armo/col/` (wrong path) | ⚠️ Move output to `armo/` root |
| 2025 Q3 | `raw/col/COL_2025t3.dta` ✅ | `COL_2025t3_mergeBID.do` ✅ | `COL_2025t3_variablesBID.do` ✅ | `COL_2025t3_BID.dta` ✅ | ✅ Done |

**Lookup files (shared across all COL waves):**
- `raw/col/mig_pais_code.dta` ✅ — country-of-origin codes for `mig_pais_ci`
- `raw/col/ciuo_cod.xlsx` ✅ — CIUO occupation codes
- `raw/col/code_pais.csv` ✅ — country codes

**Actions before continuing:**
1. **Claude creates `COL_2023t3_variablesBID.do`** by cloning `COL_2025t3_variablesBID.do` and changing 3 year references (see GUIDE.md Step 6B). ✅ Done 2026-04-01.
2. **Claude creates `COL_2024t3_variablesBID_local.do`** the same way (year 2024). ✅ Done 2026-04-01.
3. ⚠️ **Dictionary check pending** — variable names and category codes for 2023 and 2024 waves have NOT been verified against the 2025 reference script. Must be done before running (see Step 0c below).
4. Run each script in Stata to produce `COL_2023t3_BID.dta` and `COL_2024t3_BID.dta` in `bases armo/armo/`.
5. Move existing `bases armo/armo/col/COL_2024t3_BID.dta` → `bases armo/armo/COL_2024t3_BID.dta` (or discard once new script runs).

---

### 0c. Reference codes — Colombia GEIH (pipeline Step 3)

Coding decisions confirmed for all COL waves (based on 2025 Q3 as reference):

| Domain | Variable | Source | Decision |
|--------|----------|--------|----------|
| Migrant status | `migrante_ci` | `p3373` | 1 if p3373==3 (foreign-born non-Colombian); 0 otherwise |
| Origin country | `mig_pais_ci` | `p3373s3` + `mig_pais_code.dta` | merge on p3373s3; use `pais` string from lookup |
| LAC migrants | `miglac_ci` | `p3373s3` | ISO numeric codes listed in script (32 countries) |
| Migrant seniority | `migrantiguo5_ci` | `p3382` | 1 if p3382 ∈ {2,3}; 0 if p3382==4; missing if native |
| Education level | `edu_hdmf` | `p3042` + `p3042s1` + `p3043` | 10-category scheme; p3043 can upgrade level (never downgrade) |
| Years of education | `aedu_ci` | `p3042` + `p3042s1` | 0 if ninguno/preescolar; primary/secondary = p3042s1; tertiary = 11+p3042s1 |
| Education field | `cinef13_ci` | `p3042s2` | ISCED-F 2013, 2-digit aggregation |
| Occupation status | `condocup_ci` | `oci`, `dsi`, `fft` | 1=Employed, 2=Unemployed, 3=Inactive; age 15–64 only |
| Formality | `formal_ci` | `cotizando_ci` OR `afiliado_ci` | 1 if contributes to pension OR affiliated to health (employed only) |
| Household ID | `idh_ch` | `idh` | tostring(idh) |
| Weight | `factor_ci` | `fex_c18` | direct copy |

⚠️ **Dictionary check required before running 2023/2024 scripts:**
Confirm that `p3042`, `p3042s1`, `p3042s2`, `p3043`, `p3373`, `p3373s3`, `p3382`,
`oci`, `dsi`, `fft`, `fex_c18`, and `idh` exist with the same names and codes
in `COL_2023t3.dta` and `COL_2024t3.dta`. If any differ, update the clone and
add an inline comment documenting the change.

---

## Step 1 — Survey Metadata

```
Country name:          Colombia
ISO3 country code:     COL
Survey name:           Gran Encuesta Integrada de Hogares (GEIH)
Survey acronym:        GEIH
Producing institution: DANE (Departamento Administrativo Nacional de Estadística)
Reference period:      2025 Q3 = 2025t3 (July + August + September)
HDMF file code:        COL_2025t3

Raw file location:     bases armo/raw/col/
Raw files:
  - julio/Características generales, seguridad social en salud y educación.DTA
  - agosto/Características generales, seguridad social en salud y educación.DTA
  - septiembre/Características generales, seguridad social en salud y educación.DTA
  (+ occupation, income modules from each month)

File format:           Stata .dta
Modules:               Multiple — merge on DIRECTORIO + SECUENCIA_P + ORDEN

Survey design:         Multi-stage cluster
Individual weight:     fex_c18
Household weight:      fex_h (use head's fex_c18 if not available)
Reference week:        Last week
Reference month:       Last month (for income)
```

---

## Step 2 — Variable Mapping

### Demographics mapping

| HDMF Variable | Source Variable | Source Codes | Transformation |
|---------------|----------------|-------------|----------------|
| pais_c | — | — | Constant: "COL" |
| idh_ch | DIRECTORIO + SECUENCIA_P | — | `string(DIRECTORIO)+"-"+string(SECUENCIA_P)` |
| idp_ci | ORDEN | — | Direct copy |
| factor_ci | fex_c18 | — | Direct copy |
| factor_ch | fex_h | — | From household module |
| edad_ci | p6040 | — | Direct copy |
| sexo_ci | p6020 | 1=Hombre, 2=Mujer | Direct copy (same coding) |
| relacion_ci | p6050 | 1=Jefe, 2=Pareja, 3=Hijo, 4=Nieto, 5=Padre, 6=Suegro, 7=Hermano, 8=Otro pariente, 9=Empleado, 10=Pensionista, 11=Otro no pariente | Recode → 1–6 |
| miembros_ci | p6070 | 1=Sí, 2=No | Recode: 1→1, 2→0 |

### Migration mapping

| HDMF Variable | Source Variable | Source Codes | Transformation |
|---------------|----------------|-------------|----------------|
| migrante_ci | p3373 | 1=Este país, 2=Otro país (colombiano), 3=Otro país (extranjero) | 0 if p3373==1\|2, 1 if p3373==3 |
| mig_pais_ci | p3374 | Numeric country codes | Convert to string country name |
| migrantiguo5_ci | p3375 | Year of arrival | `= 1 if (2025 - p3375) > 5` |

**Note on migrante_ci:** GEIH p3373==2 are Colombians born abroad (returnees). They are coded as native (0) in HDMF since the analytical interest is in immigrants receiving country labor markets.

### Education mapping

| HDMF Variable | Source Variable(s) | Transformation |
|---------------|-------------------|----------------|
| edu_hdmf | p3042 (level), p3043 (diploma) | See logic below |
| aedu_ci | p3147 (years) or derived | Direct if available, else derive from edu_hdmf |
| edu_isced | — | Derived from edu_hdmf |

**edu_hdmf logic for GEIH:**
```
p3042 codes: 1=Ninguno, 2=Preescolar, 3=Primaria, 4=Secundaria, 5=Media,
             6=Superior/Universitaria, 7=Postgrado
p3044: completion indicator (1=complete, 2=incomplete)
p3043: diploma codes for upgrade
```

### Labor mapping

| HDMF Variable | Source Variable | Notes |
|---------------|----------------|-------|
| condocup_ci | oc (current occupation module) | 1=Employed if worked; derived for unemployed/inactive |
| emp_ci | Derived from condocup_ci | |
| desemp_ci | Derived from condocup_ci | |
| pea_ci | Derived from condocup_ci | |
| formal_ci | cotizando_ci OR afiliado_ci | |
| cotizando_ci | p6920 | 1=Yes, 2=No → recode |
| afiliado_ci | p6090 | 1=EPS, 2=ARS, ... → 1 if affiliated |
| tipocontrato_ci | p6460 | 1=Written, 2=Verbal, 3=No contract |
| horaspri_ci | p6800 | Weekly hours (direct) |
| horastot_ci | p6800 + p7045 | Primary + secondary job hours |

### Income mapping

| HDMF Variable | Source Variable | Notes |
|---------------|----------------|-------|
| ylm_ci | p6500 + p7510s2 | Primary wage + secondary job earnings |
| ylnm_ci | p6590 | In-kind benefits (estimated monetary value) |
| ynlm_ci | multiple | Pension + transfers + rent (from non-labor module) |
| ytot_ci | Derived | ylm + ylnm + ynlm |
| remesas_ci | p7510s5 | Monthly remittances received |
| remesas_ch | Aggregated | Sum of remesas_ci by household |

---

## Step 3 — Key Stata code snippets

### Appending monthly files
```stata
global raw "bases armo/raw/col"

* Append three months
use "$raw/julio/Características generales.DTA", clear
append using "$raw/agosto/Características generales.DTA"
append using "$raw/septiembre/Características generales.DTA"
```

### Household ID
```stata
gen idh_ch = string(DIRECTORIO) + "-" + string(SECUENCIA_P)
gen idp_ci = ORDEN
gen pais_c = "COL"
```

### Migration
```stata
gen migrante_ci = .
replace migrante_ci = 0 if p3373 == 1 | p3373 == 2
replace migrante_ci = 1 if p3373 == 3

gen mig_pais_ci = ""
* [lookup table for country codes in p3374]
replace mig_pais_ci = "Venezuela" if p3374 == 862
replace mig_pais_ci = "Ecuador"   if p3374 == 218
* ... etc.

gen migrantiguo5_ci = .
replace migrantiguo5_ci = 1 if (2025 - p3375) > 5 & migrante_ci == 1
replace migrantiguo5_ci = 0 if (2025 - p3375) <= 5 & migrante_ci == 1
replace migrantiguo5_ci = . if migrante_ci != 1
```

### Formality (Colombia definition)
```stata
* cotizando: contributes to pension
gen cotizando_ci = .
replace cotizando_ci = 1 if p6920 == 1 & emp_ci == 1
replace cotizando_ci = 0 if p6920 == 2 & emp_ci == 1

* afiliado: affiliated to health system
gen afiliado_ci = .
replace afiliado_ci = 1 if p6090 >= 1 & p6090 <= 4 & emp_ci == 1  // EPS or ARS
replace afiliado_ci = 0 if p6090 == 5 & emp_ci == 1               // Not affiliated

gen formal_ci = .
replace formal_ci = 1 if (cotizando_ci == 1 | afiliado_ci == 1) & emp_ci == 1
replace formal_ci = 0 if (cotizando_ci == 0 & afiliado_ci == 0) & emp_ci == 1
```

---

## Step 4 — Validation results (reference)

After running the .do file, expected validation output:

```
Total observations: ~350,000 (three months pooled)
Estimated population (weighted): ~50 million
Share foreign-born (migrante_ci==1): ~4–5%
  of which Venezuelan: ~60–65% of migrants

Key missing rates:
  edad_ci:    0.0%
  sexo_ci:    0.0%
  condocup_ci (working age): ~3%
  migrante_ci: ~1%
  aedu_ci:    ~8%
  ylm_ci (employed): ~12%

Range checks: PASS (all asserts pass)
Formality among employed: ~45% (plausible for Colombia)
```

---

## Step 5 — Integration into hdmf_2.py

After validation, add the file path to the loading section in `hdmf_2.py`:

```python
# In the country loading dictionary:
files = {
    "COL": "bases armo/armo/COL_2025t3_BID.dta",
    "CHL": "bases armo/armo/CHL_2024a_BID.dta",
    # ... other countries
}
```

And verify the country name normalization:
```python
# Colombia should already be handled, but confirm:
country_aliases = {
    "Colombia": "Colombia",
    "COL": "Colombia",
    # ...
}
```

---

## Lessons learned from COL 2025t3

1. **Monthly file encoding:** The GEIH files use Windows-1252 encoding; use `use ..., clear` without explicit encoding — Stata handles this automatically for .dta files.
2. **p6090 for health:** Codes 1–4 are different types of health insurance (EPS contributiva, EPS subsidiada, etc.) — all count as affiliated. Only code 5 ("ninguna") counts as unaffiliated.
3. **Double-counting secondary job income:** p7510s2 already captures secondary earnings — do not add p6500 + p6510 which are primary job components only.
4. **Venezuelan share check:** In 2025 Q3 data, approximately 3.8% of Colombian working-age population was Venezuelan-born. If your estimate is below 2% or above 6%, recheck the `migrante_ci` coding.
