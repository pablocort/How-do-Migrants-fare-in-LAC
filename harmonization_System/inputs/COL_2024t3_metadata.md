# Survey Metadata — COL 2024t3

---

## 1. Identification

| Field | Value |
|-------|-------|
| **Country name** | Colombia |
| **ISO3 code** | COL |
| **Survey name** | Gran Encuesta Integrada de Hogares |
| **Survey acronym** | GEIH |
| **Producing institution** | DANE (Departamento Administrativo Nacional de Estadística) |
| **Reference period** | 2024 Q3 — July, August, September 2024 |
| **HDMF file code** | `COL_2024t3` |

---

## 2. Files

| Field | Value |
|-------|-------|
| **Raw file location** | `bases armo/raw/col/` |
| **Raw file name(s)** | `COL_2024t3.dta` (pre-merged) |
| **Number of modules** | 1 (already merged via `COL_2024t3_mergeBID.do`) |
| **Merge key variables** | N/A — single merged file |
| **Stata version** | 17 |

**File format**
- [x] Stata `.dta`

**Note:** A prior output file exists at `bases armo/armo/col/COL_2024t3_BID.dta` (wrong subdirectory). The new script (`COL_2024t3_variablesBID_local.do`) saves directly to `bases armo/armo/` root. The old file in `armo/col/` can be discarded once the new script runs successfully.

---

## 3. Survey design

| Field | Value |
|-------|-------|
| **Individual weight variable** | `fex_c18` |
| **Household weight variable** | `fex_c18` (head's weight used for household) |
| **PSU variable** | Not used in harmonization |
| **Strata variable** | Not used in harmonization |
| **Reference week** | Last week (labor) |
| **Reference month (income)** | Last month |

**Weight note:** `factor_ci = fex_c18 * 3` — monthly weight multiplied by 3 for three pooled months.

**Sampling design**
- [x] Multi-stage cluster

---

## 4. Population coverage

| Field | Value |
|-------|-------|
| **Minimum survey age** | 0 (all household members) |
| **Working-age restriction** | `condocup_ci` only for ages 15–64 |
| **Target population** | Civilian non-institutionalized population, national |
| **Excluded groups** | Remote indigenous communities (some departments) |
| **Rotating panel** | No |

**Geographic coverage**
- [x] National (urban + rural)

---

## 5. Migration module

**Has birthplace question?**
- [x] Yes

| Field | Value |
|-------|-------|
| **Migration question wording** | "¿En qué país nació?" / "¿Es usted...?" |
| **Source variable name** | `p3373` |
| **Source variable codes** | `1` = Nacido en Colombia, `2` = Nacido en otro país (colombiano), `3` = Nacido en otro país (extranjero) |
| **Country-of-birth variable** | `p3373s3` — numeric ISO-3166-1 codes |
| **Migration duration variable** | `p3382` — categorical: `1`=<1 year, `2`=1–5 years, `3`=>5 years, `4`=born here/returned |

**Has country-of-birth variable?**
- [x] Yes

**Has year/duration of migration?**
- [x] Yes (categorical, not year of arrival)

**Lookup file:** `mig_pais_code.dta` in `bases armo/raw/col/` — maps `p3373s3` numeric codes to country names.

---

## 6. Education module

**Education question type**
- [x] Level + completion status (two variables)

| Field | Value |
|-------|-------|
| **Level variable name** | `p3042` |
| **Level codes** | `1`=Ninguno, `2`=Preescolar, `3`=Básica primaria, `4`=Básica secundaria, `5`=Media académica, `6`=Media técnica, `7`=Normalista, `8`=Técnica profesional, `9`=Tecnológica, `10`=Universitaria, `11`=Especialización, `12`=Maestría, `13`=Doctorado, `99`=No sabe |
| **Last grade completed** | `p3042s1` — years within current level |
| **Diploma/degree variable** | `p3043` — diploma received (used to upgrade edu_hdmf) |
| **Field of study variable** | `p3042s2` — ISCED-F 2013 numeric codes |
| **Years of schooling variable** | Derived: not directly asked |

---

## 7. Labor module

**Labor force question type**
- [x] Derived — DANE provides pre-computed flags

| Field | Value |
|-------|-------|
| **Main labor status variable** | `oci` (employed), `dsi` (unemployed), `fft` (inactive) — DANE flags |
| **Minimum working age** | 15 (applied in script: `!inrange(edad_ci, 15, 64)` → missing) |
| **Hours worked — primary job** | `p6800` (weekly) |
| **Hours worked — secondary job** | `p7045` (weekly) |
| **Pension contribution variable** | `p6920` — `1`=Yes, `2`=No |
| **Health affiliation variable** | `p6090` — `1`–`4`=Affiliated (various types), `9`=Not affiliated |
| **Contract type variable** | `p6460` (`1`=Written, `2`=Verbal); `p6450` and `p6440` for no-contract cases |

**Hours frequency**
- [x] Weekly

---

## 8. Income module

**Income reference period**
- [x] Monthly

| Field | Value |
|-------|-------|
| **Primary job wage variable** | Not yet harmonized (commented out in script) |
| **Secondary job wage variable** | Not yet harmonized |
| **In-kind income variable** | Not yet harmonized |
| **Non-labor income variables** | Not yet harmonized |
| **Remittances variable name** | `p7510s2a1` (annual — divided by 12 in script) |
| **Currency** | Colombian Peso (COP) |

**Remittances available at**
- [x] Individual level

---

## 9. Known issues and special considerations

**Known problems**
- Income variables are not yet coded in this wave (commented-out block in script). Only `remesas_ci` and `remesas_ch` are active.
- A prior output exists at `armo/col/COL_2024t3_BID.dta`. This is the wrong path — `hdmf_2.py` will not load it. The new run will save to `armo/COL_2024t3_BID.dta` (root). The old file can be deleted after the new one is verified.
- Dictionary check required: variable names and codes for 2024 GEIH have not been verified against the 2025 reference. See `COL_dictionary_check_2023_2024.md`.

**Comparability with prior waves**
- 2024t3 is intermediate between 2023t3 (oldest) and 2025t3 (reference). Any changes identified in the dictionary check for 2024 are candidates for the same change in 2023.

**Country-specific notes**
- `mig_pais_code.dta` merge uses an absolute path hardcoded to PABLOCOR. Update path if running on a different machine.

---

## 10. Documentation

| Field | Value |
|-------|-------|
| **Survey questionnaire** | Refer to DANE GEIH 2024 documentation |
| **Previous harmonization notes** | Reference script: `COL_2025t3_variablesBID [Recovered] march3.do` |
| **Dictionary check** | `harmonization_System/inputs/COL_dictionary_check_2023_2024.md` |
| **Responsible researcher** | Pablo Cortés Sánchez |
| **Date completed** | 2026-04-01 |
