# HDMF — Indicator Descriptions

**Project:** How do Migrants Fare in LAC (HDMF)
**Pipeline:** `bases armo/armo/hdmf_2.py`
**Output file:** `out/indicator_descriptive/hdmf_indicators.xlsx`

All indicators are computed from harmonized `*_BID.dta` files. Statistics are weighted using `factor_ci`. The main comparison groups are:

| Group label | Definition |
|-------------|-----------|
| Nativos | `migrante_ci == 0` (native-born) |
| Migrantes de Venezuela | `migrante_ci == 1` and `mig_pais_ci == "Venezuela"` |
| Migrantes de otros países | `migrante_ci == 1` and `mig_pais_ci != "Venezuela"` |

---

## Module 1 — Population (`population_origin`)

### 1a. Origin of the migrant population
- **What it measures:** Weighted count and percentage share of migrants by country of birth, for each host country. Top 20 origin countries per host country.
- **Source variable:** `mig_pais_ci`
- **Population:** Foreign-born individuals (`migrante_ci == 1`)
- **Unit:** Weighted headcount and share (%) of total migrant stock
- **Analytical dimension:** Origin country × host country
- **Output sheet:** `population_origin`
- **Chart:** `population_migrants_share.png` — share of migrants in total population (Venezuelan vs other foreign-born) by country

### 1b. Population aggregates
- **What it measures:** Total and working-age (16–64) population by migration status group
- **Source variables:** `factor_ci`, `edad_ci`, `mig_pais_ci`
- **Population:** All individuals; subset 16–64 for working-age
- **Unit:** Weighted headcount; also columns for Venezuelan + other combined and total
- **Analytical dimension:** Host country × migration status group

### 1c. Age distribution of migrant groups
- **What it measures:** Share of each age group (0–17, 18–34, 35–64, 65+) within each migration status group
- **Source variables:** `edad_ci`, `factor_ci`, `mig_pais_ci`
- **Unit:** Share (%) within group
- **Chart:** `population_venezuelans_age.png` — age structure of Venezuelan migrants by host country

---

## Module 2 — Labor Market (`labor_status`, `labor_wages_hours`)

### 2a. Employment, unemployment, inactivity, and PEA rates
- **What it measures:** Weighted rates of four labor market statuses:
  - Employment rate (`emp_ci`): share of working-age population currently employed
  - Unemployment rate (`desemp_ci`): share looking for work among the working-age population
  - Inactivity rate (`inactivo_ci`): share neither working nor searching
  - PEA participation rate (`pea_ci`): share economically active (employed + unemployed)
- **Source variables:** `emp_ci`, `desemp_ci`, `pea_ci`, `condocup_ci`
- **Population:** Working-age population, ages 16–64
- **Unit:** Rate (0–1), with standard error, 95% confidence interval, effective N
- **Analytical dimension:** Host country × migration status group × indicator
- **Output sheet:** `labor_status`
- **Charts:**
  - `labor_employed_bar.png` — employment rate + PEA bar chart by group and country
  - `labor_employment_rate.png` — employment rate scatter by country and group
  - `labor_unemployment_rate.png` — unemployment rate scatter by country and group

### 2b. Income and working hours
- **What it measures:**
  - Weighted average total monthly income (`ytot_ci`), in nominal local currency units
  - Weighted average total weekly hours worked (`horastot_ci`)
- **Source variables:** `ytot_ci`, `horastot_ci`
- **Population:** Working-age population, ages 16–64
- **Unit:** Weighted mean (LCU per month; hours per week)
- **Analytical dimension:** Host country × migration status group
- **Output sheet:** `labor_wages_hours`
- **Note:** Income is in nominal local currency units (no PPP adjustment at this stage). Cross-country comparisons require deflation or conversion.

---

## Module 3 — Formality (`formality`, `contract_type`)

### 3a. Formal employment rate
- **What it measures:** Share of employed workers who are formal (contribute to pension or affiliated to social security)
- **Definition:** `formal_ci == 1` — derived as `cotizando_ci == 1 OR afiliado_ci == 1` (definition may vary slightly by country)
- **Source variable:** `formal_ci`
- **Population:** Employed individuals (`condocup_ci == 1`), LAC countries only (USA excluded)
- **Unit:** Rate (0–1), with standard error and 95% CI
- **Analytical dimension:** Host country × migration status group
- **Output sheet:** `formality`
- **Chart:** `formality_rate.png` — formality rate scatter by country and group

### 3b. Contract type distribution
- **What it measures:** Distribution of employed workers across contract types and formality status
- **Source variable:** `tipocontrato_ci`
  - 1 = Written contract
  - 2 = Verbal agreement
  - 3 = No contract
- **Population:** Employed individuals, LAC countries only
- **Unit:** Weighted counts and rates
- **Analytical dimension:** Host country × migration status group × contract type
- **Output sheet:** `contract_type`

---

## Module 4 — Education (`education_level`, `education_years`)

### 4a. Education level distribution
- **What it measures:** Share of the population at each HDMF education level
- **Source variable:** `edu_hdmf` (10-category classification)
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
- **Population:** All individuals with valid `edu_hdmf`
- **Unit:** Share (0–1) within group for each education category
- **Analytical dimension:** Host country × migration status group × education level
- **Output sheet:** `education_level`
- **Charts:**
  - `education_bar.png` — lower secondary incomplete vs university complete by group and country
  - `education_university_rate.png` — university completion rate scatter
  - `education_basic_or_less.png` — share with basic education or less (sum of categories 1–5)

### 4b. Average years of schooling
- **What it measures:** Weighted average years of completed education
- **Source variable:** `aedu_ci`
- **Population:** All individuals with valid `aedu_ci`
- **Unit:** Years (weighted mean)
- **Analytical dimension:** Host country × migration status group
- **Output sheet:** `education_years`

---

## Output summary

| Sheet name | Module | Main variable(s) | Population | Groups |
|------------|--------|-----------------|------------|--------|
| `population_origin` | Population | `mig_pais_ci` | Migrants | Top-20 origin countries per host |
| `labor_status` | Labor | `emp_ci`, `desemp_ci`, `inactivo_ci`, `pea_ci` | Ages 16–64 | Nativos / Venezuela / Otros |
| `labor_wages_hours` | Labor | `ytot_ci`, `horastot_ci` | Ages 16–64 | Nativos / Venezuela / Otros |
| `formality` | Formality | `formal_ci` | Employed, LAC only | Nativos / Venezuela / Otros |
| `contract_type` | Formality | `tipocontrato_ci` | Employed, LAC only | Nativos / Venezuela / Otros |
| `education_level` | Education | `edu_hdmf` | All | Nativos / Venezuela / Otros |
| `education_years` | Education | `aedu_ci` | All | Nativos / Venezuela / Otros |

### Charts produced (`out/indicator_descriptive/`)

| File | Content |
|------|---------|
| `population_migrants_share.png` | Share of migrants in total population by host country |
| `population_venezuelans_age.png` | Age distribution of Venezuelan migrants by host country |
| `labor_employed_bar.png` | Employment rate + PEA rate (bars + points) by group and country |
| `labor_employment_rate.png` | Employment rate scatter: native vs Venezuelan vs other |
| `labor_unemployment_rate.png` | Unemployment rate scatter: native vs Venezuelan vs other |
| `formality_rate.png` | Formality rate scatter by host country and migration group |
| `education_bar.png` | Lower secondary incomplete and university complete by group |
| `education_university_rate.png` | University completion rate scatter |
| `education_basic_or_less.png` | Share with basic education or less |

---

## Methodological notes

- **Weights:** All rates and averages are weighted by `factor_ci` (individual expansion factor).
- **Standard errors:** Computed for all rates; confidence intervals at 95% level.
- **Working-age definition:** 16–64 years old for all labor market indicators.
- **LAC restriction:** Formality indicators exclude the USA because `formal_ci` is not defined using the same social security framework.
- **Income:** Reported in nominal local currency units at the time of the survey. No PPP or CPI deflation is applied at the harmonization stage.
- **Migrant groups:** The three-way split (native / Venezuelan / other foreign-born) is the primary analytical dimension. Venezuelan migrants are disaggregated separately because they represent the largest recent migration flow in most LAC countries in scope.
- **Source file:** See `bases armo/armo/hdmf_2.py` for all computation details.
- **Input codebook:** See `harmonization_System/inputs/variables_definitions.md` for harmonized variable definitions.
