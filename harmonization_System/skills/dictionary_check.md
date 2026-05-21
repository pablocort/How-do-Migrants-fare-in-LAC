# Skill: Dictionary Check

## Purpose

Systematically compare raw survey data dictionaries across multiple waves of the same survey before cloning or writing a harmonization script. The goal is to detect:

- Variables that were **renamed** between waves
- Categorical variables whose **codes or labels changed**
- Variables that were **added or dropped** in a given wave
- Changes in **variable type** (e.g., numeric → string) that would break existing code
- Changes in **expansion factor** structure

This skill is required at **Step 4.5** of the HDMF pipeline when working on a "clone + edit" script for a new wave of a known survey. It is also useful as the first step in `survey_mapper` when no prior harmonization exists.

---

## When to invoke this skill

- You are about to clone an existing `.do` script for a new wave of the same survey
- You are harmonizing multiple waves of the same survey in a single session
- The survey documentation mentions a redesign or variable change between waves
- The inputs checklist flags a "dictionary check required" note

---

## Primary tool: Python (`dictionary_check.py`)

**Use Python for all `.dta` inspection and cross-wave comparison.** The script `harmonization_System/inputs/dictionary_check.py` handles this automatically.

```bash
cd "...How-do-Migrants-fare-in-LAC"
python harmonization_System/inputs/dictionary_check.py --country COL --waves 2018t3 2019t3 2020t3 2021t3 2022t3 2023t3 2024t3 2025t3
```

**Why Python, not Stata, for pre-harmonization checks:**
- `capture tab` in Stata suppresses all output, not just errors — tabulation results are lost
- Python reads `.dta` with `pyreadstat` / `pandas.read_stata` without opening Stata
- Produces clean cross-wave comparison tables as DataFrames
- Automatically greps the `alternative_do_files/` package for missing variable constructions
- Detects structural breaks (variable appears/disappears between waves) systematically
- Runs in seconds; no Stata license required

The Python script outputs a structured `.md` report to `harmonization_System/inputs/`.

**Use Stata only for harmonization itself** (the `_variablesBID.do` files that produce `_BID.dta`).

---

## Input types this skill can work with

| Dictionary format | How to handle |
|---|---|
| Stata `.dta` (raw data file) | **Python first**: run `dictionary_check.py`. Fall back to Stata `describe`/`tab` only if Python is unavailable. |
| PDF data dictionary | Read with the Read tool (use `pages` param for large PDFs); extract variable names, question text, and category codes |
| Excel codebook (`.xlsx`) | Read with the Read tool or Python `openpyxl`/`pandas.read_excel` |
| Word/DOCX codebook | Read with the Read tool; parse tables or plain text |
| SPSS `.sav` | Convert to `.dta` via Stata `import spss`, then run Python script |
| CSV variable list | `pandas.read_csv` — compare directly |
| Reference do-files | `dictionary_check.py` greps these automatically; or use Grep tool for targeted searches |

---

## Stata workflow (for `.dta` raw data files)

Write a Stata `.do` file named `[ISO3]_dictionary_check_[PERIODS].do` and save it in `harmonization_System/inputs/`. The script must include:

### Step A — Variable existence matrix

```stata
* For each wave, check which target variables are present
foreach wave of local waves {
    use "`root'/[ISO3]_`wave'.dta", clear
    di ">>> WAVE: `wave'  (N = `=_N',  vars = `=c(k)')"
    foreach v of local allvars {
        capture confirm variable `v'
        if _rc == 0 {
            local vtype: type `v'
            local vlbl:  variable label `v'
            di "  EXISTS   `v'  [`vtype']  `vlbl'"
        }
        else {
            di "  MISSING  `v'"
        }
    }
}
```

### Step B — Categorical variable codebook

For every variable that is used as a categorical source in the harmonization script, run:

```stata
capture tab [variable], missing
capture label list `: value label [variable]'
```

This confirms that category codes (e.g., `p3373==3` for born-abroad) have not changed.

### Step C — Expansion factor summary

```stata
quietly sum fex_c18   /* or the relevant weight variable */
di "min=`r(min)'  mean=`r(mean)'  max=`r(max)'  sum=`r(sum)'"
```

The sum should approximate the country's working-age or total population for the reference period. Flag if the sum doubles or halves unexpectedly between waves.

### Step D — Migration module deep dive (required for GEIH / surveys with migration modules)

```stata
* Check birthplace variable and categories
tab p3373, missing
count if p3373 == 3   /* code for "born abroad" */

* Check country-of-origin variable
preserve
keep if p3373 == 3
tab p3373s3, sort missing
restore

* Check arrival recency variable
tab p3382, missing
```

### Step E — Income variable availability

List all income source variables and check non-missing counts:

```stata
foreach v of local vars_income {
    capture confirm variable `v'
    if _rc == 0 {
        quietly sum `v'
        di "EXISTS  `v'  (N non-missing: `r(N)'  mean: `r(mean)')"
    }
    else {
        di "MISSING  `v'"
    }
}
```

---

## Output: dictionary check markdown report

After running the Stata script, save the findings as:
`harmonization_System/inputs/[ISO3]_dictionary_check_[PERIODS].md`

Structure the report as follows:

```markdown
# Dictionary Check: [ISO3]_[SURVEY] ([PERIOD_FROM] – [PERIOD_TO])
Date: [today]
Reference script: [ISO3]_[BASE_PERIOD]_variablesBID.do
Waves checked: [list]

---

## Variable existence matrix

| Variable | Domain | 2018t3 | 2019t3 | 2020t3 | 2021t3 | 2022t3 | 2023t3 | 2024t3 | 2025t3 |
|----------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| p6050    | Demo   | ✅ | ✅ | ...
...

---

## Categorical changes detected

List only variables where category codes or labels differ between waves.
If none: write "None detected."

| Variable | Wave | Change observed |
|---|---|---|
| ...

---

## Expansion factor summary

| Wave | N obs | fex_c18 sum | Notes |
|------|-------|-------------|-------|
| ...

---

## Migration module

| Wave | p3373 exists | p3373==3 (born abroad) N | p3373s3 exists | p3382 exists |
|------|-------------|--------------------------|----------------|--------------|
| ...

---

## Income variables

| Variable | Waves where available | Notes |
|---|---|---|
| ...

---

## Clone safety assessment

| Wave | Safe to clone from [BASE_PERIOD]? | Issues requiring inline edits |
|------|----------------------------------|-------------------------------|
| ...

---

## Recommended changes for cloned scripts (if any)

List any variable name substitutions or category code overrides needed per wave.
```

---

## PDF / Excel / Word dictionary workflow

When raw data files are not available and you only have a PDF or Excel codebook:

1. **Read the file** using the Read tool (for PDFs, use `pages` parameter to target variable tables)
2. **Extract for each variable:**
   - Variable name (exact Stata name)
   - Question text
   - Categories (code + label)
3. **Compare against the reference script** (`[ISO3]_[BASE_PERIOD]_variablesBID.do`) line by line for every source variable
4. **Flag any discrepancy** — renamed variable, changed category code, or new/dropped category
5. **Document findings** in the same markdown report format above

For PDFs with many pages, focus extraction on:
- Section headings matching the HDMF domains (employment, education, migration, income)
- Variables already used in the reference harmonization script
- Any "CAMBIOS / MODIFICACIONES" section that explicitly documents inter-wave changes

---

## Variables to always check for GEIH (Colombia)

| Domain | Variables | High-change risk |
|--------|-----------|-----------------|
| IDs & weights | `idh`, `orden`, `fex_c18` | Low |
| Demographics | `p6050`, `p6040`, `p3016` | Low |
| Employment | `oci`, `dsi`, `fft`, `p6800`, `p7045`, `p6920`, `p6090`, `p6460`, `p6450`, `p6440`, `p7450`, `p6240` | Medium (`oci`/`dsi`/`fft` are derived flags — may vary) |
| Education | `p3042`, `p3042s1`, `p3042s2`, `p3043` | Low |
| Migration | `p3373`, `p3373s3`, `p3382` | **HIGH** — module redesigned after 2017 Venezuela wave |
| Income | `impa`, `impaes`, `isa`, `isaes`, `imdi`, `imdies`, `ie`, `iees`, `iof1`–`iof6`, `p7510s2a1` | High — income modules restructured periodically |

---

## Integration with survey_mapper agent

When the `survey_mapper` agent starts a mapping for a new wave of a known survey:

1. **First**: invoke this skill to produce the dictionary check report
2. **Then**: use the check report as the starting point — pre-fill all variables confirmed stable with "STABLE — clone from [BASE_PERIOD]"
3. **Only map from scratch** variables flagged as changed or not found
4. Pass the completed mapping (with stability annotations) to `mapping_checker` before generating any Stata code

---

## After completing this skill

Save the `.md` report to `harmonization_System/inputs/[ISO3]_dictionary_check_[PERIODS].md` and reference it in `inputs_summary.md`.
