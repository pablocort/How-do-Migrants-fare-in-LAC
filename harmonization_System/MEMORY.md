# HDMF — Project Memory

This file captures lessons, decisions, and data quirks discovered across work sessions that are not documented in the GUIDE, codebook, walkthrough, or .do files. It is a living document — append entries as new things are learned. Never delete entries; mark them as superseded if they become outdated.

**Format for new entries:**
```
### [Short title]
- **Date:** YYYY-MM-DD
- **Scope:** [country-wave, all countries, Python pipeline, system, etc.]
- **Finding:** What was discovered or decided.
- **Why it matters:** How this affects future work.
- **Source:** Where the evidence came from (file, line, empirical check, etc.).
```

---

## Education

### edu_hdmf: implementation uses 8 categories, codebook defines 10
- **Date:** 2026-04-01
- **Scope:** All countries — COL 2025t3 confirmed
- **Finding:** `variable_codebook.md` defines `edu_hdmf` with 10 categories (1=No schooling, 2=Primary incomplete, 3=Primary complete, 4=Lower secondary incomplete, 5=Lower secondary complete, 6=Upper secondary complete, 7=Technical/vocational, 8=University incomplete, 9=University complete, 10=Postgraduate). The actual COL script implements only 8 categories (1=Menos de primaria, 2=Primaria incompleta, 3=Primaria completa, 4=Media incompleta, 5=Media completa, 6=Técnica, 7=Universitaria completa, 8=Posgrado). "University incomplete" (codebook cat. 8) and "Upper secondary complete" (codebook cat. 6) are collapsed differently in the script.
- **Why it matters:** Any cross-country comparison using `edu_hdmf` must use the 8-category implementation, not the 10-category codebook. The codebook needs to be updated to match the scripts, or vice versa — a deliberate decision is needed. Until resolved, always check which scheme a given script uses before interpreting results.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` lines 356–408 vs. `inputs/variable_codebook.md` section 6.

### edu_hdmf: p3043 diploma variable only upgrades, never downgrades
- **Date:** 2026-04-01
- **Scope:** COL GEIH (confirmed); likely applies to surveys with similar diploma questions
- **Finding:** `p3043` records the highest diploma/title received. The rule is: if p3043 indicates a completed credential at a lower level than `p3042` (current enrollment), use `p3043` to upgrade `edu_hdmf`. But p3043 never forces edu_hdmf down. This asymmetric logic is a project convention, not a standard rule.
- **Why it matters:** When cloning the COL script for other surveys that have a similar "diploma received" variable, apply this same upgrade-only logic.
- **Source:** Comment in `COL_2025t3_variablesBID [Recovered] march3.do` line 359; also noted in `example/colombia_geih_walkthrough.md`.

### aedu_ci: tertiary education years computed as 11 + p3042s1
- **Date:** 2026-04-01
- **Scope:** COL GEIH
- **Finding:** For all tertiary levels (p3042 ∈ {7,8,9,10,11,12,13}), years of education = 11 + p3042s1. This stacks tertiary years on top of 11 years of completed secondary, regardless of actual path taken.
- **Why it matters:** Creates a floor of 11 years for any tertiary-enrolled individual, which may overstate education for those who skipped secondary grades. Consistent within COL waves but may differ in other countries.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` lines 275–286.

---

## Migration

### migrante_ci: Colombian returnees (p3373==2) coded as native
- **Date:** 2026-04-01
- **Scope:** COL GEIH
- **Finding:** GEIH p3373 has three values: 1=born in Colombia, 2=born abroad (Colombian national), 3=born abroad (foreign national). HDMF codes `migrante_ci = 1` only for p3373==3. Colombian returnees (p3373==2) are coded as native (0). This is an analytical choice — the project focuses on immigrants in the receiving-country labor market, not returnees.
- **Why it matters:** Document clearly when reporting migrant shares. If a different research question requires including returnees, the coding must change. Do not assume all surveys have this three-way split.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` line 430; `example/colombia_geih_walkthrough.md` note on migrante_ci.

### migrantiguo5_ci: uses p3382 categorical codes, not year of arrival
- **Date:** 2026-04-01
- **Scope:** COL GEIH
- **Finding:** COL uses p3382 (categorical: 1=less than 1 year, 2=1–5 years, 3=more than 5 years, 4=born here but returned). Code: 1 if p3382 ∈ {2,3}; 0 if p3382==4; missing for natives. Note: p3382==1 (less than 1 year) maps to `migrantiguo5_ci = 0` by exclusion but is not explicitly coded — verify this is intentional.
- **Why it matters:** Some surveys use year-of-arrival; COL uses a duration category. The `map_migration.md` skill shows patterns for both. When cloning for other waves, confirm p3382 category codes haven't changed.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` lines 435–437.

### miglac_ci: 31 LAC country ISO numeric codes hardcoded in COL script
- **Date:** 2026-04-01
- **Scope:** COL GEIH — applies to any survey using ISO numeric country codes
- **Finding:** `miglac_ci` is built with `inlist(p3373s3, 32, 68, 76, ...)` — a list of 31 ISO-3166-1 numeric codes for LAC countries (Argentina through Curaçao). This list should be the same across all countries that use ISO numeric codes. If a survey uses a different country coding system (alphabetic, national codes), the lookup must be adapted.
- **Why it matters:** If a new country in the LAC region needs to be added (or removed from the analytical scope), this hardcoded list must be updated in every script. Consider creating a shared lookup file.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` lines 444–481.

---

## Labor market

### factor_ci: multiplied by 3 in quarterly COL scripts
- **Date:** 2026-04-01
- **Scope:** COL GEIH quarterly waves (2024t3, 2025t3)
- **Finding:** `factor_ci = fex_c18 * 3` in the COL scripts. This is because three monthly files are appended (July + August + September for Q3), and the monthly weight `fex_c18` would triple-count the population if not divided. Multiplying by 3 is the DANE convention for annualizing a quarterly dataset from 3 months. Do NOT apply this multiplier for annual datasets.
- **Why it matters:** If future COL scripts use a different number of months (e.g., 4 months for a non-standard quarter), the multiplier must change. Always check what period is actually covered before setting the factor.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` lines 79–80; confirmed in walkthrough lessons.

### condocup_ci: age restriction 15–64 applied in COL
- **Date:** 2026-04-01
- **Scope:** COL GEIH — verify for each new country
- **Finding:** `condocup_ci` is set to missing for ages outside [15, 64]. This is the working-age definition used in COL. Other countries may use different bounds (e.g., 15–65, 14–70). Always check the survey documentation and document the bound used.
- **Why it matters:** Affects labor force participation rates. A different age restriction changes who enters the denominator.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` line 94.

---

## Income

### Income variables blocked out in COL 2025t3 script
- **Date:** 2026-04-01
- **Scope:** COL GEIH 2025t3
- **Finding:** The income section (`ylmpri_ci`, `ylmsec_ci`, `ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`) is entirely commented out under `/* ... */` in the reference script. `remesas_ci` and `remesas_ch` are active. Income harmonization for COL is incomplete.
- **Why it matters:** `hdmf_2.py` will find these variables missing in the COL output file. Any indicator that uses labor income will be missing for COL. Must be completed before any cross-country income comparison.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` lines 176–244.

### remesas_ci: annual amount divided by 12
- **Date:** 2026-04-01
- **Scope:** COL GEIH
- **Finding:** `remesas_ci = p7510s2a1 / 12` — the source variable is annual remittances; dividing by 12 converts to monthly, consistent with all other income variables. The condition `p7510s2a1 > 9999` filters out values below 10,000 COP (likely noise/rounding).
- **Why it matters:** If other surveys report remittances monthly, do NOT divide by 12. Always check the source variable's reference period.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` line 415.

---

## Pipeline / system

### COL 2024t3 output is in armo/col/ subdirectory, not armo/ root
- **Date:** 2026-04-01
- **Scope:** COL 2024t3
- **Finding:** `COL_2024t3_BID.dta` was saved in `bases armo/armo/col/` instead of `bases armo/armo/`. `hdmf_2.py` reads only from the root, so this file is invisible to the analysis pipeline.
- **Why it matters:** Must be moved to `bases armo/armo/COL_2024t3_BID.dta` (or the new script writes it to the correct path) before COL 2024 data can be used in analysis.
- **Source:** `inputs/inputs_summary.md` footnote 1.

### mig_pais_code.dta merge uses absolute path (hardcoded to PABLOCOR)
- **Date:** 2026-04-01
- **Scope:** COL GEIH scripts
- **Finding:** The `merge m:1 p3373s3 using "C:\Users\PABLOCOR\..."` line in the COL script uses an absolute path hardcoded to the PABLOCOR user profile. The script will fail on any other machine or user account.
- **Why it matters:** If another team member runs the script, the path must be updated. Consider replacing with a relative path using a global macro (e.g., `$ruta`) consistent with the rest of the script.
- **Source:** `COL_2025t3_variablesBID [Recovered] march3.do` line 498.

### Dictionary check is required before running cloned scripts — not optional
- **Date:** 2026-04-01
- **Scope:** All cloned scripts (same survey, new wave)
- **Finding:** The 2023 and 2024 COL scripts were cloned from 2025 without a dictionary check. Variable names and category codes were not verified. This creates a silent risk: the script may run without errors but produce wrong values if codes changed between waves.
- **Why it matters:** Dictionary check must happen BEFORE running any cloned script in Stata. Flag in the walkthrough and GUIDE (already done). Treat this as a blocking step, not advisory.
- **Source:** `example/colombia_geih_walkthrough.md` Step 0b, item 3 (pending check noted).

---

## Python analysis pipeline

### hdmf_2.py loads all .dta files from armo/ root automatically
- **Date:** 2026-04-01
- **Scope:** Analysis pipeline
- **Finding:** The script uses `os.listdir(folder_path)` filtered to `.dta` extension — it loads every `.dta` file in `bases armo/armo/` without a whitelist. Adding a file to that folder automatically includes it in the analysis. Removing it excludes it. No manual registration in a list is needed.
- **Why it matters:** No need to edit `hdmf_2.py` to add a new country — just ensure the `.dta` is in the right folder with the right name. The walkthrough's instruction to "add the file path to hdmf_2.py" is outdated.
- **Source:** `bases armo/armo/hdmf_2.py` lines 29–34.
