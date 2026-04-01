# Survey Metadata Template

Fill out this form before harmonizing a new survey. Provide it to the `orchestrator` and `survey_mapper` agents as the first input.

---

## 1. Identification

| Field | Value |
|-------|-------|
| **Country name** | |
| **ISO3 code** | |
| **Survey name** | |
| **Survey acronym** | |
| **Producing institution** | |
| **Reference period** | e.g. 2025 Q3 → `2025t3` / Dec 2025 → `2025m12` / Annual → `2024a` |
| **HDMF file code** | `[ISO3]_[PERIOD]` e.g. `MEX_2025t4` |

---

## 2. Files

| Field | Value |
|-------|-------|
| **Raw file location** | `bases armo/raw/[country_folder]/` |
| **Raw file name(s)** | |
| **Number of modules** | |
| **Merge key variables** | e.g. `folio + n_hog + n_ren` |
| **Stata version** | only if compatibility issues |

**File format**
- [ ] Stata `.dta`
- [ ] SPSS `.sav`
- [ ] CSV

**If multiple modules**, describe structure:

| Module | File name | Contents |
|--------|-----------|----------|
| 1 | | demographics / labor / income / … |
| 2 | | |
| Merge type | | `1:1 on [key variables]` |

---

## 3. Survey design

| Field | Value |
|-------|-------|
| **Individual weight variable** | e.g. `fex_c18` |
| **Household weight variable** | e.g. `fex_h` |
| **PSU variable** | if available |
| **Strata variable** | if available |
| **Reference week** | e.g. "last week / last 7 days" |
| **Reference month (income)** | e.g. "last month" |

**Sampling design**
- [ ] Simple random
- [ ] Stratified
- [ ] Multi-stage cluster

---

## 4. Population coverage

| Field | Value |
|-------|-------|
| **Minimum survey age** | e.g. `12` — affects working-age lower bound |
| **Target population** | e.g. civilian non-institutionalized population 12+ |
| **Excluded groups** | e.g. military, remote indigenous communities |
| **Rotating panel** | Yes / No — if yes, describe structure |

**Geographic coverage**
- [ ] National (urban + rural)
- [ ] Urban only
- [ ] Other: _______________

---

## 5. Migration module

**Has birthplace question?**
- [ ] Yes
- [ ] No → skip this section

| Field | Value |
|-------|-------|
| **Migration question wording** | paste exact question text |
| **Source variable name** | e.g. `p3373` |
| **Source variable codes** | e.g. `1=This country`, `2=Abroad-national`, `3=Abroad-foreign` |
| **Country-of-birth variable** | variable name + how countries are coded |
| **Migration duration variable** | variable name + codes, if available |

**Has country-of-birth variable?**
- [ ] Yes
- [ ] No

**Has year/duration of migration?**
- [ ] Yes
- [ ] No

---

## 6. Education module

**Education question type**
- [ ] Level + completion status (two variables)
- [ ] Years of schooling (one variable)
- [ ] Both

| Field | Value |
|-------|-------|
| **Level variable name** | e.g. `p10a` |
| **Level codes** | e.g. `0=None`, `1=Primary`, `2=Secondary`, `3=University` |
| **Completion variable name** | e.g. `p10b` |
| **Diploma/degree variable** | e.g. `p3043` — if available |
| **Years of schooling variable** | if available |

---

## 7. Labor module

**Labor force question type**
- [ ] Direct (single question classifies employed / unemployed / inactive)
- [ ] Derived (must combine multiple questions)

| Field | Value |
|-------|-------|
| **Main labor status variable** | variable name + codes |
| **Minimum working age** | e.g. "only asked of persons 12 and older" |
| **Hours worked — primary job** | variable name |
| **Hours worked — secondary job** | variable name, if available |
| **Pension contribution variable** | variable name + yes/no codes |
| **Health affiliation variable** | variable name + yes/no codes |
| **Contract type variable** | variable name + codes |

**Hours frequency**
- [ ] Weekly
- [ ] Daily
- [ ] Other: _______________

---

## 8. Income module

**Income reference period**
- [ ] Monthly
- [ ] Weekly
- [ ] Annual
- [ ] Other: _______________

| Field | Value |
|-------|-------|
| **Primary job wage variable** | |
| **Secondary job wage variable** | if available |
| **Self-employment income variable** | if available |
| **In-kind income variable** | if available |
| **Non-labor income variables** | list: pension var, transfer var, rent var, … |
| **Remittances variable name** | |
| **Currency** | e.g. Colombian Peso (COP), Peruvian Sol (PEN) |

**Remittances available at**
- [ ] Individual level
- [ ] Household level
- [ ] Not available

---

## 9. Known issues and special considerations

**Known problems**

> _e.g. "Income data has extreme outliers in the top 0.1%"_
> _e.g. "Migration module only asked of persons 18+"_

**Comparability with prior waves**

> _e.g. "Education coding changed in 2023 — codes 7 and 8 were split"_

**Country-specific notes**

> _Anything that makes this survey different from standard LAC surveys_

---

## 10. Documentation

| Field | Value |
|-------|-------|
| **Survey questionnaire** | file name in `bases armo/raw/` or URL |
| **Methodology document** | file name or URL |
| **Previous harmonization notes** | reference to prior HDMF wave if applicable |
| **Responsible researcher** | |
| **Date completed** | YYYY-MM-DD |

**Questionnaire available?**
- [ ] Yes
- [ ] No
