# Skill: Variable Alternatives

## Purpose

When a standard HDMF source variable is missing from a raw dataset, **do not immediately set the target variable to missing**. The variable usually exists under a different name, in a different module, or requires a different construction logic. This skill defines the workflow for finding and documenting alternatives.

This is one of the most important skills for multi-wave harmonization: surveys redesign their questionnaires over time, renaming variables, splitting or merging questions, and restructuring modules. The variable you need almost always existed in some form — the work is to find it.

---

## Inputs this skill can use

### 1. Reference do-file package (primary source)
The project maintains a **reference package of do files** from prior harmonization runs (IDB/SCL/MECOVI historical scripts). These files show exactly how each variable was built in a given country and year. When a variable is missing using the standard approach, **check the reference package first**.

Location: will be specified when provided. Check `harmonization_System/inputs/inputs_summary.md` for current status.

How to use:
- Search the reference package for the country (e.g., `COL`) and the target variable name (e.g., `migrante_ci`)
- Read how it was built — which raw variables were used, what conditions were applied
- Verify those raw variables exist in the current wave's dictionary check
- Adapt the logic to the HDMF standard if needed

### 2. Survey codebook / data dictionary (PDF, Excel, Word, DTA)
The raw survey codebook lists all variables, their question text, and category codes. When the standard variable name is missing, search the codebook for the underlying **concept** (e.g., "lugar de nacimiento", "años de educación") and find what variable holds it.

### 3. Dictionary check output
The dictionary check (`[ISO3]_dictionary_check_[PERIODS].md`) lists all variables present in each wave. Use it to find which variables exist in the problem wave and cross-reference against the codebook.

---

## Workflow: what to do when a variable is missing

```
1. Run dictionary check → confirm variable truly missing (not a typo)
2. Check reference package → search for same country, same variable, nearby year
3. Check codebook → search for the concept in the codebook, find the raw variable
4. Verify alternative exists in the raw data → confirm via dictionary check or describe
5. Construct with alternative → adapt code to match HDMF definition
6. Document → add inline comment explaining the substitution and why
7. Flag for mapping_checker → mark as MEDIUM or HIGH RISK in the mapping report
```

---

## Pattern library: confirmed alternatives in COL GEIH

All alternatives below are **confirmed from the reference do-file package** located at `bases armo/raw/[ISO3]/alternative_do_files/`. Always check that folder first before consulting the codebook.

---

### Expansion factor

#### `fex_c18` — pre-2022 GEIH

| Waves | Variable | Notes |
|-------|----------|-------|
| 2022–2025 | `fex_c18` | Monthly expansion factor; sum ≈ 50–52M |
| **2018–2021** | **`fex_c_2011`** | **Confirmed in reference package** |

```stata
**** factor_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): g factor_ci = fex_c18
* Source for this wave (2018–2021): fex_c_2011 — fex_c18 not in dataset
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****
g factor_ci = fex_c_2011
g factor_ch = fex_c_2011
```

---

### Employment

#### `fft` / `ini` (inactive population flag) — pre-2022 GEIH

| Waves | Variable | Meaning |
|-------|----------|---------|
| 2022–2025 | `fft` | Pre-computed DANE inactive flag |
| **2018–2021** | **`ini`** | **Confirmed in reference package** |

```stata
**** condocup_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): oci / dsi / fft
* Source for this wave (2018–2021): oci / dsi / ini — fft not in dataset
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****
gen condocup_ci = .
replace condocup_ci = 1 if oci == 1
replace condocup_ci = 2 if dsi == 1
replace condocup_ci = 3 if ini == 1
replace condocup_ci = 4 if edad_ci < 10
replace condocup_ci = . if !inrange(edad_ci, 15, 64)
label define condocup_ci 1 "Ocupado" 2 "Desocupado" 3 "Inactivo" 4 "Menor que 10"
label value condocup_ci condocup_ci
```

> **Note:** `emp_ci` and `desemp_ci` are derived the same way in both period groups:
> `gen emp_ci = (condocup_ci == 1)` and `gen desemp_ci = (condocup_ci == 2)` — no `if` restriction needed when derived directly from condocup_ci.

---

### Education

#### `p3042` module — pre-2022 GEIH

| Waves | Variables | Notes |
|-------|-----------|-------|
| 2022–2025 | `p3042`, `p3042s1`, `p3043` | Level + grade + diploma |
| **2018–2021** | **`p6210`, `p6210s1`** | **Confirmed in reference package** |

`aedu_ci` construction from reference package (`COL_2018t3_variablesBID.do`):

```stata
**** aedu_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): p3042 + p3042s1
* Source for this wave (2018–2021): p6210 + p6210s1 — p3042 not in dataset
* p6210:   nivel educativo (1=ninguno, 2=preescolar, 3=primaria, 4=secundaria,
*           5=media, 6=superior/universitaria)
* p6210s1: último año/grado aprobado dentro del nivel
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****
replace p6210s1 = . if p6210s1 == 99
replace p6210   = . if p6210 == 9
g aedu_ci = .
replace aedu_ci = 0  if p6210 == 1 | p6210 == 2
replace aedu_ci = 0  if p6210 == 3 & p6210s1 == 0
replace aedu_ci = 1  if p6210 == 3 & p6210s1 == 1
replace aedu_ci = 2  if p6210 == 3 & p6210s1 == 2
replace aedu_ci = 3  if p6210 == 3 & p6210s1 == 3
replace aedu_ci = 4  if p6210 == 3 & p6210s1 == 4
replace aedu_ci = 5  if p6210 == 3 & p6210s1 == 5
replace aedu_ci = 5  if p6210 == 4 & p6210s1 == 0
replace aedu_ci = 6  if p6210 == 4 & p6210s1 == 6
replace aedu_ci = 7  if p6210 == 4 & p6210s1 == 7
replace aedu_ci = 8  if p6210 == 4 & p6210s1 == 8
replace aedu_ci = 9  if p6210 == 4 & p6210s1 == 9
replace aedu_ci = 10 if p6210 == 5 & p6210s1 == 10
replace aedu_ci = 11 if p6210 == 5 & p6210s1 == 11
replace aedu_ci = 11 if p6210 == 6 & p6210s1 == 0
replace aedu_ci = 12 if p6210 == 5 & p6210s1 == 12
replace aedu_ci = 13 if p6210 == 5 & p6210s1 == 13
replace aedu_ci = 11 + p6210s1 if p6210 == 6
replace aedu_ci = .  if p6210 == .
```

> `edu_isced` and `edu_hdmf` can then be derived from `aedu_ci` using the same breakpoint logic as the 2022+ script, since years-of-education are the common currency.

---

### Migration

#### `migrante_ci` — pre-2022 GEIH

| Waves | Variables | Definition |
|-------|-----------|-----------|
| 2022–2025 | `p3373 == 3` | Born abroad (birthplace only) |
| **2018–2021** | **`p6074 == 2 & p756 == 3`** | **Born abroad + habitual residence abroad** |

```stata
**** migrante_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): gen migrante_ci = (p3373 == 3)
* Source for this wave (2018–2021): p6074==2 (born in another country)
*   AND p756==3 (habitual residence abroad) — p3373 not in dataset
* Note: definition differs — 2018–2021 requires both birthplace AND residence
*   criteria; 2022+ uses birthplace only. Migrant share 2018–2021 may be
*   slightly lower due to stricter definition.
* Reference: COL_2018t3_variablesBID.do, SCL/MIG Fernando Morales
**** END ALTERNATIVE ****
gen migrante_ci = (p6074 == 2 & p756 == 3) if p6074 != . & p756 != .
label var migrante_ci "=1 si es migrante"
```

#### `migrantiguo5_ci` — pre-2022 GEIH

| Waves | Variable | Notes |
|-------|----------|-------|
| 2022–2025 | `p3382` codes 2,3 | Categorical recency variable |
| **2018–2021** | **`p755` codes 2,3** | **Confirmed in reference package** |

```stata
**** migrantiguo5_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): inlist(p3382, 2, 3)
* Source for this wave (2018–2021): inlist(p755, 2, 3) — p3382 not in dataset
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****
gen migrantiguo5_ci = (migrante_ci == 1 & inlist(p755, 2, 3)) ///
    if migrante_ci != . & p755 != 1
replace migrantiguo5_ci = 0 if p755 == 4 & migrante_ci == 1 & p755 != 1
replace migrantiguo5_ci = . if migrante_ci == 0
label var migrantiguo5_ci "=1 si es migrante antiguo (5 anos o mas)"
```

#### `mig_pais_ci` — pre-2022 GEIH

In 2022+: built from `p3373s3` merged to `mig_pais_code.dta`.
In 2018–2021: check reference package for country-of-birth sub-variable (likely `p6074s1`).

#### `miglac_ci` — pre-2022 GEIH

In 2018–2021: `migrantelac_ci` is set to missing (`.`) in the reference package — the country-of-origin codes are not available in those waves. Document as NOT AVAILABLE.

---

### Demographics

#### `sexo_ci` — COL GEIH: structural break 2021→2022

| Waves | Variable | Notes |
|-------|----------|-------|
| 2018–2021 | `p6020` | Label: "Sexo" |
| **2022–2025** | **`p3271`** | Label: "P3271" — confirmed from dictionary check |

```stata
* 2018–2021:
gen sexo_ci = p6020
* p6020: 1 = Hombre, 2 = Mujer

* 2022–2025:
gen sexo_ci = p3271
* p3271: 1 = Hombre, 2 = Mujer
```

> Codes are identical (1=male, 2=female) — only the variable name changed.

---

## How to document alternatives in the do file

Every time an alternative variable is used, add an inline comment block:

```stata
**** [variable] — ALTERNATIVE CONSTRUCTION ****
* Standard source (YYYY+): [standard variable and condition]
* Source for this wave ([YEAR]): [alternative variable] — [reason for substitution]
* Reference: [do file in reference package] or [codebook page/section]
**** END ALTERNATIVE ****
```

Example for migration in 2019t3:
```stata
**** migrante_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): gen migrante_ci = (p3373 == 3)
* Source for this wave (2019t3): p6074==2 & p756==3 — p3373 not in dataset
* Reference: COL_2019_MIG_SCL_FMoreales.do (reference package)
**** END ALTERNATIVE ****
gen migrante_ci = (p6074 == 2 & p756 == 3) if p6074 != . & p756 != .
```

---

## Integration with survey_mapper and mapping_checker

When the `survey_mapper` agent produces a mapping for a wave with missing standard variables:

1. For each missing variable, apply this skill's workflow (reference package → codebook → construct alternative)
2. Mark the mapping entry as **"ALTERNATIVE — [reason]"** instead of "MISSING"
3. When handing to `mapping_checker`, flag all alternative constructions as **MEDIUM RISK** minimum
4. The `mapping_checker` will verify:
   - That the conceptual definition matches the HDMF standard despite the different source variable
   - That the category codes are compatible (especially for migration and education)
   - That the population restriction (if any) is correctly applied

---

## After completing this skill

Update `harmonization_System/inputs/[ISO3]_dictionary_check_[PERIODS].md`:
- Replace all "❌ NOT FOUND → all-missing" entries with the alternative construction documented here
- Mark resolved items as **"✅ ALTERNATIVE: [variable]"**
