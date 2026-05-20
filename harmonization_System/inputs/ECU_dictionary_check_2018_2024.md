# ECU ENEMDU — Dictionary Check: 2018m12 – 2024m12
**Reference wave:** ECU 2025m12  
**Reference script:** `do armo/ecu/ECU_2025m12_variablesBID.do`  
**Target waves:** 2018m12, 2019m12, 2020m12, 2021m12, 2022m12, 2023m12, 2024m12  
**Date:** 2026-04-14  

---

## Step 2 — Input inventory

| Resource | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Raw `.dta` (`bases armo/raw/ecu/ECU_[YEAR]m12.dta`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Alternative do file (`alternative_do_files/ECU_[YEAR]m12_variablesBID.do`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dictionary — personas | PDF questionnaire only | XLSX (`enemdu_personas_2019_12.xlsx`) | XLSX (`diccionario_enemdu_personas_2020_12.xlsx`) | XLSX (2021) | ODS (2022) | ODS (2023) | ODS (2024) |
| Dictionary — vivienda/hogar | PDF questionnaire only | XLSX | XLSX | XLSX (2021) | ODS (2022) | ODS (2023) | ODS (2024) |
| Dictionary — consumidor | PDF questionnaire only | XLSX | XLSX | XLSX (2021) | ODS (2022) | ODS (2023) | ODS (2024) |
| Metadata | PDF questionnaire only | PDF questionnaire only | XLSX (`202012_Metadatos.xlsx`) | XLSX (2021) | ODS (2022) | — | ODS (2024) |
| No merge step needed (pre-merged .dta) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

> **2018–2019:** Only questionnaire PDFs available (`FORMULARIO ENEMDU ... 2017_web.pdf`, `Formulario ENEMDU ... DICIEMBRE-LXII-2018.pdf`). Variable names confirmed via alternative do files.

---

## Step 3 — Reference code decisions (from ECU 2025m12)

| Domain | Decision |
|--------|----------|
| **Migration** | `migrante_ci = (p15aa == 3)` — born outside Ecuador (not the same as currently residing in Ecuador). Stable across all years. |
| **Country of birth** | `mig_pais_ci` from `p15ab` (ISO numeric codes). Stable across all years. |
| **Recent migration** | `migrantiguo5_ci = .` — questionnaire does not reliably capture time since arrival; left missing in all waves. |
| **Employment status** | Three-category `condocup_ci`: occupied (1), unemployed (2), inactive (3), restricted to ages 15–64. `p20`, `p21`, `p22`, `p32` stable. |
| **Formality** | Dual condition: `cotizando_ci` (active contributor) OR `afiliado_ci` (affiliated). See cotizando note below. |
| **Education** | `aedu_ci` from `p10a` / `p10b` using ENEMDU level-to-years mapping. `edu_hdmf` from `p10a`, `p10b`, `p12a`. Both added to all waves. |
| **Income** | **Excluded** — income module is not in the 2025 reference and is omitted from all cloned waves. |
| **Output folder** | `bases armo/armo/ECU/` |

---

## Step 4 — Metadata summary

| Item | Value (all waves) |
|------|-------------------|
| Survey name | ENEMDU (Encuesta Nacional de Empleo, Desempleo y Subempleo) |
| Country | Ecuador (ECU) |
| Period type | Monthly, December round |
| Survey mode | Pre-merged `.dta` (no merge step) |
| Weight variable | `fexp` |
| Unit of analysis | Individual (household linked by `idh_ch`) |
| Age restriction (labor) | 15–64 |

---

## Step 4.5 — Dictionary check: Key source variables

### Verification legend
- **STABLE** — variable name and codes identical to 2025 reference  
- **ALTERNATIVE:[note]** — variable exists but name or structure differs; note describes the change  
- **NOT AVAILABLE** — variable absent from this wave  
- **FLAG** — verify against dictionary before running

---

### A. Identifiers & weights

| HDMF variable | Source (2025 ref) | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `idh_ch` | `id_vivienda+id_hogar` | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | STABLE |
| `idp_ci` | `id_vivienda+id_hogar+id_persona` | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | ALTERNATIVE:1 | STABLE |
| `factor_ci` | `fexp` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `factor_ch` | `fexp` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `upm_ci` | `upm` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `estrato_ci` | `estrato` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |

> **ALTERNATIVE:1 — Legacy ID structure (2018–2023):**  
> Variables `id_vivienda`, `id_hogar`, `id_persona` do NOT exist.  
> Use: `sort area estrato upm vivienda hogar p01` then `egen idh_ch = group(area estrato upm vivienda hogar)`.  
> `idp_ci` constructed analogously with `p01` (person number) added to group.

---

### B. Geography

| HDMF variable | Source (2025 ref) | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `region_c` | `destring ciudad → _ciudad → int(_ciudad/10000)` | NOT AVAILABLE:2 | ALTERNATIVE:3 | ALTERNATIVE:3 | ALTERNATIVE:3 | ALTERNATIVE:3 | ALTERNATIVE:3 | STABLE |
| `zona_c` | `area` (1=urban, 2=rural) | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `pais_c` | `"ECU"` literal | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |

> **NOT AVAILABLE:2 — 2018 has no `ciudad` variable.**  
> `region_c` set to `.` for all observations. Confirmed in alternative do file (commented block).

> **ALTERNATIVE:3 — 2019–2023: `ciudad` is numeric integer** (no destring needed).  
> Use: `gen region_c = int(ciudad / 10000)` — no `destring` step.

---

### C. Demographics

| HDMF variable | Source (2025 ref) | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `sexo_ci` | `p02` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `edad_ci` | `p03 if p03 < 99` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `relacion_ci` | `p04` (1–6 recode) | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `miembros_ci` | *(not in 2025 ref)* | ALTERNATIVE:4 | ALTERNATIVE:4 | ALTERNATIVE:4 | ALTERNATIVE:4 | ALTERNATIVE:4 | ALTERNATIVE:4 | ALTERNATIVE:4 |

> **ALTERNATIVE:4 — `miembros_ci` missing from 2025 reference script.**  
> Standard HDMF codebook requires it. Add using:  
> 2018–2023: `gen miembros_ci = (relacion_ci >= 1 & relacion_ci <= 5)`  
> 2024: `gen miembros_ci = (relacion_ci >= 1 & relacion_ci < 5)` (note threshold change confirmed in 2024 alternative)  
> FLAG: confirm whether relacion_ci category 5 ("otros no parientes") should be included in household.

---

### D. Migration

| HDMF variable | Source (2025 ref) | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `migrante_ci` | `p15aa == 3` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `mig_pais_ci` | `p15ab` (ISO numeric) | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `migrantiguo5_ci` | `.` (always missing) | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `miglac_ci` | `p15ab inlist(...)` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |

> All migration source variables (`p15aa`, `p15ab`) confirmed present and with identical codes in all 7 waves via alternative do files.

---

### E. Labor market

| HDMF variable | Source (2025 ref) | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `condocup_ci` | `p20`, `p21`, `p22`, `p32` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `emp_ci` | derived from `condocup_ci` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `desemp_ci` | derived from `condocup_ci` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `pea_ci` | derived from `emp_ci + desemp_ci` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `horaspri_ci` | `p51a` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `horastot_ci` | `rsum(p51a p51b p51c)` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `categopri_ci` | `p42` (5=patron,6=cp,≤4/10=emp,7-9=norenum) | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `tipocontrato_ci` | `p43` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `cotizando_ci` | `(p44f==1 \| p61b1<=4)` | ALTERNATIVE:5 | ALTERNATIVE:5 | ALTERNATIVE:5 | ALTERNATIVE:6 | ALTERNATIVE:6 | ALTERNATIVE:6 | STABLE |
| `afiliado_ci` | `p05a <= 4` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `formal_ci` | derived from `cotizando_ci + afiliado_ci` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |

> **ALTERNATIVE:5 — 2018–2020: Old cotizando construction** (pre-2021 questionnaire).  
> Only `p44f==1` condition active in production code; `p61b1` was in commented lines.  
> New scripts will use the simplified 2025 form `gen cotizando_ci = (p44f == 1 | p61b1 <= 4)` — this is the correct HDMF standard. FLAG: verify that `p61b1` exists in 2018–2020 raw data.

> **ALTERNATIVE:6 — 2021–2023:** Both conditions were active but implemented in two separate replace blocks.  
> New scripts will use the simplified 2025 form. Functionally equivalent.

---

### F. Education

| HDMF variable | Source (2025 ref) | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `aedu_ci` | `p10a`, `p10b` | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE | STABLE |
| `edu_hdmf` | `p10a`, `p10b`, `p12a` | DERIVED:7 | DERIVED:7 | DERIVED:7 | DERIVED:7 | DERIVED:7 | DERIVED:7 | STABLE |
| `p3043` (diagnostic `ta`) | `p3043` | NOT AVAILABLE:8 | NOT AVAILABLE:8 | NOT AVAILABLE:8 | NOT AVAILABLE:8 | NOT AVAILABLE:8 | NOT AVAILABLE:8 | NOT AVAILABLE:8 |

> **DERIVED:7 — `edu_hdmf` absent from 2018–2023 alternative scripts** (predates HDMF education framework).  
> Source variables `p10a`, `p10b`, `p12a` are confirmed present in all waves.  
> `edu_hdmf` construction from 2025 reference is fully portable — include in all waves.

> **NOT AVAILABLE:8 — `p3043` not present in any wave including 2024.**  
> Remove the `ta p3043` diagnostic line from all cloned scripts. It does not affect `edu_hdmf` construction.

---

### G. Income (excluded)

Income module (`ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`, `remesas_ci`, `remesas_ch`) is present in the alternative do files but **excluded from all new HDMF scripts**, following the 2025 reference pattern. The alternative scripts can be consulted if income is needed in a later phase.

---

## Summary: structural change blocks per wave

| Block | 2018 | 2019–2023 | 2024 | 2025 (ref) |
|---|---|---|---|---|
| `ciudad` variable | **NOT present** → `region_c = .` | Numeric integer → `int(ciudad/10000)` | String → `destring ciudad, gen(_ciudad)` | String (same as 2024) |
| ID variables | `vivienda hogar` + `p01` (legacy) | `vivienda hogar` + `p01` (legacy) | `id_vivienda id_hogar id_persona` (new) | `id_vivienda id_hogar id_persona` (new) |
| `idh_ch` construction | `egen idh_ch = group(area estrato upm vivienda hogar)` | `egen idh_ch = group(area estrato upm vivienda hogar)` | `id_vivienda+id_hogar` | `id_vivienda+id_hogar` |
| `cotizando_ci` | Old (p44f only, p61b1 commented) | Old (both conditions, two replace blocks) | Simplified OR condition | Simplified OR condition |
| `edu_hdmf` | **Add from ref** (p10a/p10b/p12a available) | **Add from ref** (p10a/p10b/p12a available) | Present | Present |
| `p3043` diagnostic line | **Remove** | **Remove** | **Remove** | Present (reference only) |

---

## Action items before generating scripts

- [ ] **FLAG**: Confirm `p61b1` exists in ECU 2018–2020 raw data (open dictionary or check with `describe` in Stata). If missing, keep only `p44f==1` for cotizando in those years.
- [ ] **FLAG**: Confirm `miembros_ci` threshold for 2018–2023: should category 5 ("otros no parientes") be included (`<= 5`) or excluded (`< 5`)? Current 2018–2023 alternatives use `<= 5`; 2024–2025 use `< 5`.
- [ ] **Confirm output folder**: `bases armo/armo/ECU/` — folder exists and is the correct target.
- [ ] **Confirm scope**: No income module in any wave. Correct?

Once you confirm (or flag any items), scripts for all 7 waves will be generated.
