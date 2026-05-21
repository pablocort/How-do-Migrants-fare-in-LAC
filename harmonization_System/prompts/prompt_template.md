# Prompt Template — Run Harmonization Pipeline (Steps 1–7)

Use this prompt to ask Claude to run the harmonization pipeline for a new country-year. Replace the bracketed fields with the actual values.

---

## Template

```
In the following pipeline:
1. Choose scope          → country + period(s)
2. Check inputs          → raw data, merge .do, variables .do, lookup files
3. Select reference codes → migration, education, labor, ID coding decisions (document them)
4. Prepare metadata      → fill inputs/survey_metadata_template.md
4.5. Dictionary check   → output file documenting any potential variable changes between waves
5. Map variables         → use agent: survey_mapper (calls skill modules)
6. Generate Stata script → use agent: stata_generator (new survey) OR clone+edit existing (same survey, new wave)
7. Run & validate        → use agent: validator

Run the harmonization for [ISO3] [PERIOD_1] and [PERIOD_2].
The reference wave is [ISO3] [REFERENCE_PERIOD].

After the preparation of the metadata (step 4), produce a dictionary check document
(step 4.5) listing all key source variables, their expected codes from the reference wave,
and a verification column for each target wave so I can confirm or flag any changes before running.

After the dictionary check, confirm the .do files are complete and provide run instructions.
Do not run step 8 (analysis).
```

---

## Example (as used for COL 2023t3 and 2024t3)

```
In the following pipeline:
1. Choose scope          → country + period(s)
2. Check inputs          → raw data, merge .do, variables .do, lookup files
3. Select reference codes → migration, education, labor, ID coding decisions (document them)
4. Prepare metadata      → fill inputs/survey_metadata_template.md
4.5. Dictionary check   → output file documenting any potential variable changes between waves
5. Map variables         → use agent: survey_mapper (calls skill modules)
6. Generate Stata script → use agent: stata_generator (new survey) OR clone+edit existing (same survey, new wave)
7. Run & validate        → use agent: validator

Run the harmonization for COL 2023t3 and 2024t3.
The reference wave is COL 2025t3.

After the preparation of the metadata (step 4), produce a dictionary check document
(step 4.5) listing all key source variables, their expected codes from the reference wave,
and a verification column for each target wave so I can confirm or flag any changes before running.

After the dictionary check, confirm the .do files are complete and provide run instructions.
Do not run step 8 (analysis).
```

---

## Fields to replace

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `[ISO3]` | Country ISO3 code | `COL`, `ECU`, `PER` |
| `[PERIOD_1]` | First target wave | `2023t3`, `2024m12`, `2024a` |
| `[PERIOD_2]` | Second target wave (omit if only one) | `2024t3` |
| `[REFERENCE_PERIOD]` | Most recent harmonized wave of the same survey | `2025t3`, `2025m12` |

---

## Example (as used for PER 2018a–2023a, April 2026)

```
In the following pipeline:
1. Choose scope          → country + period(s)
2. Check inputs          → raw data, merge .do, variables .do, lookup files
3. Select reference codes → migration, education, labor, ID coding decisions (document them)
4. Prepare metadata      → fill inputs/survey_metadata_template.md
4.5. Dictionary check   → output file documenting any potential variable changes between waves
5. Map variables         → use agent: survey_mapper (calls skill modules)
6. Generate Stata script → use agent: stata_generator (new survey) OR clone+edit existing (same survey, new wave)
7. Run & validate        → use agent: validator

Run the harmonization for PER 2018a, 2019a, 2020a, 2021a, 2022a, and 2023a.
The reference wave is PER 2024a (script: do armo/per/PER_2024_variablesBID.do).

Scope: same variables as PER 2024a — demographics, labor, education, migration, remesas.
Do NOT include the income module (ylm_ci, ylnm_ci, ynlm_ci, ytot_ci, etc.) — it is commented
out in the reference file and should remain excluded in all cloned waves.

Raw data: bases armo/raw/per/PER_[YEAR]a.dta (2018–2023, all present).
No merge step needed (datasets are pre-merged).
Alternative do files: bases armo/raw/per/alternatives_do_files/ (PER_2018a through PER_2024a).
Data dictionaries: bases armo/raw/per/Diccionario[YEAR].pdf (2018–2024, all present).
Output folder: bases armo/armo/PER/ (create if it doesn't exist).

After the preparation of the metadata (step 4), produce a dictionary check document
(step 4.5) listing all key source variables, their expected codes from the reference wave,
and a verification column for each target wave so I can confirm or flag any changes before running.

After the dictionary check, confirm the .do files are complete and provide run instructions.
Do not run step 8 (analysis).
```

---

## Notes

- If harmonizing only one wave, remove `and [PERIOD_2]` from the prompt.
- If it is a new country/survey (no reference wave), replace the clone path with: *"Use agent: stata_generator to generate the script from the variable mapping."*
- Step 4.5 (dictionary check) applies only to cloned scripts (same survey, new wave). For new surveys, skip it.
- Step 8 (analysis with hdmf_2.py) is intentionally excluded from this template. Add it back explicitly if needed.
- **Income exclusion**: When the user says "same variables as [reference], no income module", wrap all income blocks in `/* ... */` in every cloned script.
