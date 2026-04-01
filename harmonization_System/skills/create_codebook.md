# Skill: Create Harmonization Codebook

## Purpose

Produce a `harmonization_codebook_[ISO3]_[PERIOD].md` file that documents, for a specific country-year, how each HDMF standard variable was constructed from the raw survey. The codebook combines three sources:

1. **`inputs/variable_codebook.md`** — canonical HDMF variable definitions, types, and valid ranges
2. **The country's data dictionary** — raw variable names, labels, and category codes from the survey questionnaire or `.dta`
3. **The reference `.do` file** — the actual Stata harmonization script (e.g., `COL_2025t3_variablesBID.do`) that encodes all transformation decisions

The output is the authoritative, human-readable reference for that country-year: what each HDMF variable means, where it comes from, and exactly how it was built.

---

## Required inputs

Before starting, confirm all three are available:

- [ ] `inputs/variable_codebook.md` (standard HDMF definitions)
- [ ] Data dictionary for the target country-year (questionnaire PDF, Excel codebook, or `describe` output from Stata — any format)
- [ ] Reference `.do` file: `[ISO3]_[PERIOD]_variablesBID.do`

If the `.do` file is missing, stop and notify — the codebook cannot be built without the actual transformation logic.

---

## Process

### Step 1 — Extract the transformation logic from the .do file

Read the `.do` file and extract, for each HDMF variable:

- **Source variable(s):** the raw variable name(s) used (e.g., `p3042`, `p6920`, `oci`)
- **Source codes:** the category values in the raw variable and what they mean (pull from comments or data dictionary)
- **Transformation rule:** the `gen`/`replace` logic, in plain language
- **Edge cases:** any `if` conditions, `inlist`, `inrange`, or special replacements (e.g., age restrictions, treatment of 99 / don't know)

If the variable block is commented out in the `.do` file (e.g., income variables under `/* */`), note it as "not harmonized in this wave" and state the reason if visible in comments.

### Step 2 — Cross-reference with variable_codebook.md

For each variable extracted in Step 1, look up its canonical definition in `variable_codebook.md` and add:

- HDMF type (binary / categorical / continuous / string)
- Valid range or allowed values
- Missing value rule
- Any cross-variable consistency constraints (e.g., `emp_ci == 1` ↔ `condocup_ci == 1`)

Flag any deviation: if the `.do` file constructs the variable differently from the codebook definition, mark it with `⚠️ Deviation` and explain.

### Step 3 — Enrich with data dictionary

Use the survey data dictionary to fill in the `Source codes` column with full category labels in the original survey language, plus an English translation. This is what transforms a bare code reference (`p3042 == 3`) into a meaningful entry (`p3042 == 3 → "Básica primaria (grades 1–5)"`).

### Step 4 — Write the codebook file

Produce the markdown file following the output format below. Save it as:

```
harmonization_System/codebooks/harmonization_codebook_[ISO3]_[PERIOD].md
```

If the `codebooks/` directory does not exist, create it.

---

## Output format

```markdown
# Harmonization Codebook — [COUNTRY] [SURVEY] [PERIOD]

**Country:** [Full name] ([ISO3])
**Survey:** [Survey full name] ([acronym])
**Period:** [PERIOD] (e.g., 2025 Q3 = July–September 2025)
**Reference script:** [ISO3]_[PERIOD]_variablesBID.do
**Date built:** [YYYY-MM-DD]

---

## 1. Identifiers and Weights

### pais_c
- **HDMF type:** String (3 chars)
- **Source variable:** —
- **Transformation:** Constant `"[ISO3]"` assigned to all observations
- **Source codes:** N/A
- **Notes:** —

### idh_ch
- **HDMF type:** String
- **Source variable:** [raw var(s)]
- **Transformation:** [plain-language description, e.g., "tostring of idh"]
- **Source codes:** N/A
- **Notes:** [e.g., "must be unique within dataset"]

### idp_ci
...

### factor_ci
- **HDMF type:** Continuous > 0
- **Source variable:** [e.g., fex_c18]
- **Transformation:** [e.g., "direct copy × 3 (three months pooled)"]
- **Source codes:** N/A
- **Notes:** —

### factor_ch
...

---

## 2. Demographics

### edad_ci
- **HDMF type:** Integer, 0–120
- **Source variable:** [e.g., p6040]
- **Transformation:** Direct copy
- **Source codes:** N/A
- **Notes:** —

### sexo_ci
- **HDMF type:** Categorical (1=Male, 2=Female)
- **Source variable:** [raw var]
- **Transformation:** [e.g., "direct copy — same coding as HDMF"]
- **Source codes:**
  | Raw code | Raw label | HDMF value |
  |----------|-----------|------------|
  | 1 | Hombre | 1 (Male) |
  | 2 | Mujer | 2 (Female) |
- **Notes:** —

### relacion_ci
...

---

## 3. Migration

### migrante_ci
- **HDMF type:** Binary (1=Foreign-born, 0=Native)
- **Source variable:** [raw var, e.g., p3373]
- **Transformation:** [plain language, e.g., "1 if p3373==3 (foreign national born abroad); 0 if p3373==1 or 2"]
- **Source codes:**
  | Raw code | Raw label | HDMF value |
  |----------|-----------|------------|
  | 1 | Nacido en este país | 0 |
  | 2 | Nacido en otro país (colombiano) | 0 |
  | 3 | Nacido en otro país (extranjero) | 1 |
- **Notes:** [e.g., "p3373==2 (Colombian returnees) coded as native per HDMF analytical definition"]
- **Deviation:** [if any, with ⚠️]

### mig_pais_ci
...

### migrantiguo5_ci
...

---

## 4. Employment Status

### condocup_ci
- **HDMF type:** Categorical (1=Employed, 2=Unemployed, 3=Inactive)
- **Source variable:** [e.g., oci, dsi, fft — DANE-computed flags]
- **Transformation:** 1 if oci==1; 2 if dsi==1; 3 if fft==1; missing if age outside [15,64]
- **Source codes:**
  | Flag | Meaning |
  |------|---------|
  | oci==1 | Ocupado (employed) |
  | dsi==1 | Desocupado (unemployed) |
  | fft==1 | Fuera de la fuerza de trabajo (inactive) |
- **Notes:** [e.g., "age restriction 15–64 applied"]

### emp_ci
- **HDMF type:** Binary
- **Source variable:** Derived from condocup_ci
- **Transformation:** `emp_ci = (condocup_ci == 1)` where condocup_ci is not missing
- **Notes:** Consistency: emp_ci==1 ↔ condocup_ci==1

### desemp_ci
...

### pea_ci
...

---

## 5. Job Characteristics

### formal_ci
- **HDMF type:** Binary (1=Formal, 0=Informal)
- **Source variable:** cotizando_ci, afiliado_ci (derived)
- **Transformation:** 1 if (cotizando_ci==1 OR afiliado_ci==1) AND emp_ci==1; 0 if both are 0 AND emp_ci==1; missing otherwise
- **Notes:** —

### cotizando_ci
...

### afiliado_ci
...

### tipocontrato_ci
...

### horaspri_ci
...

### horastot_ci
...

---

## 6. Education

### aedu_ci
- **HDMF type:** Continuous ≥ 0 (years)
- **Source variable:** [e.g., p3042, p3042s1]
- **Transformation:** [describe the years-of-education derivation logic]
- **Source codes:**
  | p3042 | Survey label | Years assigned |
  |-------|-------------|----------------|
  | 1 | Ninguno | 0 |
  | 2 | Preescolar | 0 |
  | 3 | Básica primaria | p3042s1 |
  | 4 | Básica secundaria | 5 + p3042s1 |
  | 5 | Media académica | 9 + p3042s1 |
  | 6 | Media técnica | 9 + p3042s1 |
  | 7–13 | Tertiary and above | 11 + p3042s1 |
  | 99 | No sabe | . (missing) |
- **Notes:** [any deviation or special case]

### edu_isced
...

### edu_hdmf
- **HDMF type:** Categorical (1–10)
- **Source variable:** [e.g., p3042, p3043]
- **Transformation:** [describe 10-category scheme and p3043 upgrade logic]
- **Source codes:**
  | HDMF code | Label | Source condition |
  |-----------|-------|-----------------|
  | 1 | No schooling / less than primary | p3042==1\|2 |
  | 2 | Primary incomplete | p3042==3 & p3043 missing/not completed |
  | ... | ... | ... |
  | 10 | Postgraduate | p3042==12\|13 |
- **Notes:** [e.g., "p3043 diploma variable can upgrade edu_hdmf but never downgrade"]

---

## 7. Income

### ylm_ci
- **HDMF type:** Continuous ≥ 0 (monthly nominal LCU)
- **Source variable:** [raw var(s)]
- **Transformation:** [formula]
- **Status:** [Harmonized / Not harmonized in this wave]
- **Notes:** —

[Repeat for ylnm_ci, ynlm_ci, ytot_ci, remesas_ci, remesas_ch]

---

## 8. Variables not harmonized in this wave

List any HDMF standard variables for which the script has no active code (commented out or explicitly set to missing), with the reason:

| Variable | Reason |
|----------|--------|
| [var] | [e.g., "income module not yet coded"] |

---

## 9. Deviations from variable_codebook.md

Summarize all `⚠️ Deviation` entries found above:

| Variable | Codebook definition | Actual implementation | Impact |
|----------|--------------------|-----------------------|--------|
| | | | |

---

## 10. Data quality notes

Document anything found in the `.do` file comments or data dictionary that affects quality:
- Known issues (e.g., encoding problems, duplicate IDs)
- Variables flagged for revision in comments
- Expected plausibility benchmarks (from validator or walkthrough notes)
```

---

## Rules for filling the codebook

1. **Source codes table is mandatory** for every categorical variable. Do not leave it blank.
2. **Transformation must be in plain language**, not raw Stata syntax. A reader who does not know Stata must understand it.
3. **If a variable block is commented out** in the `.do` file, do not silently skip it — add it to Section 8 (not harmonized).
4. **Deviations must be explicit.** If the `.do` file differs from `variable_codebook.md` (different coding, different age range, different formality definition), flag it with `⚠️` and explain.
5. **Do not invent logic.** If the `.do` file is ambiguous or a source variable is undocumented, write "unclear — verify against questionnaire" rather than guessing.
6. **Income variables:** always state whether they were harmonized or not in this wave. Income is frequently left as a placeholder (`/* */` block) in initial scripts.
