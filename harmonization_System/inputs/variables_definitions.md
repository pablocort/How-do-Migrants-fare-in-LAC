# HDMF Standard Variable Codebook

**Project:** How do Migrants Fare in LAC (HDMF)
**Version:** 2.0 (2025)
**Reference pipeline:** `bases armo/armo/hdmf_2.py`

This codebook defines all standard variables that must be present in every harmonized `*_BID.dta` dataset. Naming follows the SEDLAC/CEDLAS convention with suffixes `_ci` (individual) and `_ch` (household).

---

## 1. Identifiers and Weights

### pais_c
- **Type:** String (3 characters)
- **Description:** ISO 3166-1 alpha-3 country code for the survey country
- **Values:** COL, CHL, ECU, PER, USA, ESP, MEX, BRA, ARG, ...
- **Missing:** Not allowed

### idh_ch
- **Type:** String
- **Description:** Unique household identifier (constructed from geographic + household codes)
- **Missing:** Not allowed
- **Note:** Must uniquely identify households within the dataset

### idp_ci
- **Type:** Numeric or string
- **Description:** Person identifier within the household (usually order number)
- **Missing:** Not allowed
- **Note:** `idh_ch` + `idp_ci` must uniquely identify each observation

### factor_ci
- **Type:** Continuous, strictly positive
- **Description:** Individual sampling weight (expansion factor)
- **Valid range:** > 0
- **Missing:** Not allowed
- **Note:** Used in all weighted statistics in `hdmf_2.py`

### factor_ch
- **Type:** Continuous, strictly positive
- **Description:** Household sampling weight
- **Valid range:** > 0
- **Note:** If not available, use head's `factor_ci` for all household members

---

## 2. Demographics

### edad_ci
- **Type:** Integer
- **Description:** Age in completed years at time of survey
- **Valid range:** 0–120 (flag > 100)
- **Missing:** Allowed (< 2% threshold)

### sexo_ci
- **Type:** Categorical
- **Description:** Biological sex
- **Values:** 1 = Male, 2 = Female
- **Missing:** Allowed (< 1% threshold)

### relacion_ci
- **Type:** Categorical
- **Description:** Relationship to household head
- **Values:**
  - 1 = Household head
  - 2 = Spouse / partner
  - 3 = Child / stepchild
  - 4 = Parent / in-law
  - 5 = Other relative
  - 6 = Non-relative / domestic worker / visitor

### miembros_ci
- **Type:** Binary
- **Description:** Is a current member of the household (excludes visitors/absent members in some surveys)
- **Values:** 1 = Yes, 0 = No

---

## 3. Migration

### migrante_ci
- **Type:** Binary
- **Description:** Foreign-born individual (born outside the survey country)
- **Values:** 1 = Foreign-born, 0 = Native-born
- **Definition:** Based on place of birth, not nationality
- **Missing:** Allowed (< 2% threshold)

### mig_pais_ci
- **Type:** String
- **Description:** Country of birth (for migrants); missing for natives
- **Values:** Standardized country names (e.g., "Venezuela", "Colombia", "Haiti")
- **Missing:** Required for `migrante_ci == 1`, leave missing for `migrante_ci == 0`

### migrantiguo5_ci
- **Type:** Binary
- **Description:** Migrant residing in the country for more than 5 years
- **Values:** 1 = More than 5 years, 0 = 5 years or less
- **Missing:** Acceptable for natives and when duration not available

---

## 4. Employment Status

All labor variables apply to the **working-age population** (see survey-specific lower bound). Set to missing for children and elderly outside working age.

### condocup_ci
- **Type:** Categorical
- **Description:** Employment condition (labor force status)
- **Values:**
  - 1 = Employed (worked at least 1 hour in reference week)
  - 2 = Unemployed (did not work but searched for work)
  - 3 = Inactive (did not work and did not search)
- **Missing:** Allowed for outside working age

### emp_ci
- **Type:** Binary
- **Description:** Currently employed
- **Values:** 1 = Employed, 0 = Not employed (unemployed or inactive)
- **Consistency:** `emp_ci == 1` ↔ `condocup_ci == 1`

### desemp_ci
- **Type:** Binary
- **Description:** Currently unemployed
- **Values:** 1 = Unemployed, 0 = Otherwise
- **Consistency:** `desemp_ci == 1` ↔ `condocup_ci == 2`

### pea_ci
- **Type:** Binary
- **Description:** In the labor force (economically active)
- **Values:** 1 = In labor force (employed or unemployed), 0 = Inactive
- **Consistency:** `pea_ci == 1` ↔ `emp_ci == 1` OR `desemp_ci == 1`

---

## 5. Job Characteristics

Apply only to employed individuals (`emp_ci == 1`). Set to missing otherwise.

### formal_ci
- **Type:** Binary
- **Description:** Formal employment (contributes to pension or affiliated to social security)
- **Values:** 1 = Formal, 0 = Informal
- **Definition:** `cotizando_ci == 1` OR `afiliado_ci == 1`
- **Note:** Definition varies for USA (see harmonization notes)

### tipocontrato_ci
- **Type:** Categorical
- **Description:** Type of employment contract
- **Values:**
  - 1 = Written contract
  - 2 = Verbal agreement
  - 3 = No contract

### horaspri_ci
- **Type:** Continuous (≥ 0)
- **Description:** Weekly hours worked in primary occupation
- **Valid range:** 0–168 (flag > 100)

### horastot_ci
- **Type:** Continuous (≥ 0)
- **Description:** Total weekly hours worked (primary + secondary jobs)
- **Constraint:** `horastot_ci >= horaspri_ci`

### cotizando_ci
- **Type:** Binary
- **Description:** Currently contributing to a pension system
- **Values:** 1 = Yes, 0 = No

### afiliado_ci
- **Type:** Binary
- **Description:** Affiliated to the health/social security system
- **Values:** 1 = Yes, 0 = No

---

## 6. Education

### aedu_ci
- **Type:** Continuous (≥ 0)
- **Description:** Years of completed education
- **Valid range:** 0–25 (flag > 22)

### edu_isced
- **Type:** Categorical
- **Description:** Highest ISCED-2011 attainment level
- **Values:** 0 (early childhood) to 8 (doctorate)

### edu_hdmf
- **Type:** Categorical
- **Description:** HDMF project education classification
- **Values:**
  - 1 = No schooling / less than primary
  - 2 = Primary incomplete
  - 3 = Primary complete
  - 4 = Lower secondary incomplete
  - 5 = Lower secondary complete
  - 6 = Upper secondary complete
  - 7 = Technical / vocational (post-secondary)
  - 8 = University incomplete
  - 9 = University complete
  - 10 = Postgraduate (master's, doctorate)

---

## 7. Income

All income variables in **monthly nominal local currency units (LCU)**.

### ylm_ci
- **Type:** Continuous (≥ 0)
- **Description:** Monthly labor income (cash): primary + secondary job wages/profits
- **Missing:** Only for non-employed

### ylnm_ci
- **Type:** Continuous (≥ 0)
- **Description:** Monthly labor income in-kind (food, housing, transport provided by employer)
- **Missing:** Only for non-employed; set to 0 if survey does not ask

### ynlm_ci
- **Type:** Continuous (≥ 0)
- **Description:** Monthly non-labor income (pensions, government transfers, rent, interests)
- **Missing:** Allowed

### ytot_ci
- **Type:** Continuous (≥ 0)
- **Description:** Total monthly individual income (`ylm_ci + ylnm_ci + ynlm_ci`)
- **Constraint:** `ytot_ci >= ylm_ci`

### remesas_ci
- **Type:** Continuous (≥ 0)
- **Description:** Monthly remittances received by the individual
- **Missing:** Allowed when survey does not ask at individual level

### remesas_ch
- **Type:** Continuous (≥ 0)
- **Description:** Total monthly remittances received by the household
- **Construction:** Sum of `remesas_ci` across household members, or household-level question

---

## Missing value protocol

- **Stata missing:** Use `.` (dot) for all missing values
- **Never use:** 99, 999, -1, -9, 9 as missing codes
- **Boolean variables:** Only 0, 1, or `.` — never 2 for "no"
- **Out-of-scope:** Use `.` when a variable does not apply (e.g., labor variables for children)
