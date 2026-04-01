# Dictionary Check — COL GEIH 2023t3 and 2024t3

**Purpose:** Before running any cloned GEIH script, verify that the key source variables exist with the same names and category codes as the 2025t3 reference. This document is the output of Step 4.5 of the harmonization pipeline. Fill in the `2023` and `2024` columns by running the Stata verification commands on each raw `.dta` file. Flag any difference; update the script and add an inline comment if a change is found.

**Reference wave:** COL_2025t3 (`COL_2025t3_variablesBID [Recovered] march3.do`)
**Waves being checked:** COL_2023t3, COL_2024t3
**Date opened:** 2026-04-01
**Completed by:** _______________

---

## How to use this document

1. Open each raw .dta file in Stata: `use "bases armo/raw/col/COL_202Xt3.dta", clear`
2. For each variable below, run the verification command shown.
3. Compare the output to the **Expected (2025t3 reference)** column.
4. Mark the result in the **2023** and **2024** columns: `✅ Same` / `⚠️ Different — see note` / `❌ Variable missing`.
5. If `⚠️` or `❌`: update the relevant script block and note the change in the **Notes** column.

---

## Section 1 — Identifiers and Weights

| Variable | Verification command | Expected (2025t3 reference) | 2023 result | 2024 result | Notes |
|----------|---------------------|--------------------------|-------------|-------------|-------|
| `idh` | `codebook idh` | Numeric, unique per household | | | Used as `idh_ch` via tostring |
| `orden` | `codebook orden` | Integer, person order within household | | | Used as `idp_ci` |
| `fex_c18` | `sum fex_c18` | Continuous > 0, no missing | | | factor_ci = fex_c18 * 3 |

---

## Section 2 — Demographics

| Variable | Verification command | Expected (2025t3 reference) | 2023 result | 2024 result | Notes |
|----------|---------------------|--------------------------|-------------|-------------|-------|
| `p6040` | `tab p6040 if p6040 > 110` | Integer age, range 0–120 | | | Direct copy → edad_ci |
| `p6050` | `tab p6050` | 1=Jefe, 2=Pareja, 3=Hijo, 4=Nieto, 5=Padre, 6=Suegro, 7=Hermano, 8=Otro pariente, 9=Empleado, 10=Pensionista, 11=Otro no pariente, 12–13=other | | | → relacion_ci recoded to 1–6 |

---

## Section 3 — Labor market

| Variable | Verification command | Expected (2025t3 reference) | 2023 result | 2024 result | Notes |
|----------|---------------------|--------------------------|-------------|-------------|-------|
| `oci` | `tab oci` | Binary: 1=Ocupado, 0 or missing otherwise | | | DANE pre-computed flag |
| `dsi` | `tab dsi` | Binary: 1=Desocupado, 0 or missing otherwise | | | DANE pre-computed flag |
| `fft` | `tab fft` | Binary: 1=Fuera de fuerza de trabajo, 0 or missing otherwise | | | DANE pre-computed flag |
| `p7450` | `tab p7450` | 1=Hogar, 2=Estudiante, 3=Pensionado, 4=Incapacitado, 5=Otra razón | | | Used for categoinac_ci |
| `p6240` | `tab p6240` | Activity last week: 3=Estudiante, 4=Oficios del hogar | | | Used for categoinac_ci |
| `p6800` | `sum p6800` | Continuous 0–168, weekly hours primary job | | | → horaspri_ci |
| `p7045` | `sum p7045` | Continuous 0–168, weekly hours secondary job | | | → horastot_ci component |
| `p6920` | `tab p6920` | 1=Sí cotiza, 2=No cotiza | | | → cotizando_ci |
| `p6090` | `tab p6090` | 1–4=Affiliated (EPS contributiva/subsidiada/etc), 9=Ninguna | | | → afiliado_ci; codes 1–4 = affiliated |
| `p6460` | `tab p6460` | 1=Escrito, 2=Verbal | | | → tipocontrato_ci codes 1–2 |
| `p6450` | `tab p6450` | 1=No tiene contrato | | | → tipocontrato_ci = 3 |
| `p6440` | `tab p6440` | 2=No tiene contrato | | | → tipocontrato_ci = 3 (alternative path) |

---

## Section 4 — Education

| Variable | Verification command | Expected (2025t3 reference) | 2023 result | 2024 result | Notes |
|----------|---------------------|--------------------------|-------------|-------------|-------|
| `p3042` | `tab p3042` | 1=Ninguno, 2=Preescolar, 3=Primaria, 4=Secundaria, 5=Media académica, 6=Media técnica, 7=Normalista, 8=Técnica prof., 9=Tecnológica, 10=Universitaria, 11=Especialización, 12=Maestría, 13=Doctorado, 99=No sabe | | | ⚠️ High risk: DANE has changed education codes between waves before |
| `p3042s1` | `sum p3042s1` | Integer 0–10 (years within level) | | | → aedu_ci component |
| `p3042s2` | `codebook p3042s2` | Numeric ISCED-F 2013 codes (2–3 digit) | | | → profesion_ci / cinef13_ci |
| `p3043` | `tab p3043` | Diploma codes — see label in reference script | | | Upgrade-only rule for edu_hdmf |

---

## Section 5 — Migration

| Variable | Verification command | Expected (2025t3 reference) | 2023 result | 2024 result | Notes |
|----------|---------------------|--------------------------|-------------|-------------|-------|
| `p3373` | `tab p3373` | 1=Nacido en Colombia, 2=Nacido en otro país (colombiano), 3=Nacido en otro país (extranjero) | | | → migrante_ci = 1 iff p3373==3 |
| `p3373s3` | `tab p3373s3` | Numeric ISO-3166-1 country codes (e.g. 862=Venezuela, 218=Ecuador) | | | Must be destring before merge |
| `p3382` | `tab p3382` | 1=<1 año, 2=1–5 años, 3=>5 años, 4=Nació aquí/retornado | | | → migrantiguo5_ci: 1 if {2,3}, 0 if {4} |
| `mig_pais_code.dta` | `use "raw/col/mig_pais_code.dta", clear` then `list` | Contains `p3373s3` (numeric) and `pais` (string country name) | | | Shared lookup — confirm p3373s3 codes match across waves |

---

## Section 6 — Income (remittances only — income not yet harmonized)

| Variable | Verification command | Expected (2025t3 reference) | 2023 result | 2024 result | Notes |
|----------|---------------------|--------------------------|-------------|-------------|-------|
| `p7510s2a1` | `sum p7510s2a1 if p7510s2a1 > 0` | Annual remittances in COP; divided by 12 in script; only values > 9,999 COP kept | | | Condition: `p7510s2a1 > 9999 & p7510s2a1 != .` |

---

## Summary of findings

Fill in after completing all checks above.

| Section | Any differences found? | Waves affected | Action taken |
|---------|----------------------|----------------|--------------|
| Identifiers / weights | | | |
| Demographics | | | |
| Labor market | | | |
| Education | | | |
| Migration | | | |
| Income | | | |

---

## Variables flagged for change

For each `⚠️ Different` finding, document the change here and confirm it was applied to the script.

| Variable | Wave | Difference found | Script updated? | Inline comment added? |
|----------|------|-----------------|-----------------|----------------------|
| | | | | |

---

## Sign-off

| Field | Value |
|-------|-------|
| **Checked by** | |
| **Date** | |
| **Scripts cleared to run** | COL_2023t3: Yes / No — COL_2024t3: Yes / No |
