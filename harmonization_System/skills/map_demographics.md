# Skill: Map Demographic Variables

## Purpose
Map raw household survey variables for identifiers, sampling weights, age, sex, and household relationship to HDMF standard variables.

## HDMF target variables

| HDMF Variable | Type | Description |
|---------------|------|-------------|
| `pais_c` | string (3-char) | ISO3 country code |
| `idh_ch` | string | Unique household identifier |
| `idp_ci` | numeric/string | Person identifier within household |
| `factor_ci` | continuous (>0) | Individual sampling weight |
| `factor_ch` | continuous (>0) | Household sampling weight |
| `edad_ci` | integer (0–120) | Age in completed years |
| `sexo_ci` | binary (1/2) | Sex: 1=Male, 2=Female |
| `relacion_ci` | categorical (1–9) | Relationship to household head |
| `miembros_ci` | binary | Is a current household member |

---

## Mapping checklist

### pais_c — Country code

Always set as a constant string:
```stata
gen pais_c = "COL"   // or PER, CHL, ECU, USA, ESP, MEX, BRA, etc.
label variable pais_c "Country ISO3 code"
```

Use ISO 3166-1 alpha-3 codes:
- Colombia: COL | Chile: CHL | Ecuador: ECU | Peru: PER
- United States: USA | Spain: ESP | Mexico: MEX | Brazil: BRA
- Venezuela: VEN | Argentina: ARG | Bolivia: BOL

---

### idh_ch — Household identifier

Must uniquely identify each household. Usually constructed from area/PSU codes + household number:

```stata
* Pattern A: concatenate geographic + household codes
gen idh_ch = string(directorio) + "-" + string(secuencia_p)

* Pattern B: single household ID variable
gen idh_ch = string(folio_viv)

* Pattern C: multiple geographic levels
gen idh_ch = string(region) + "-" + string(provincia) + "-" + string(hogar)
```

**Verify uniqueness at household level:**
```stata
duplicates report idh_ch
* Expected: 0 duplicates when collapsed to 1 obs per household
```

---

### idp_ci — Person identifier

```stata
* Usually the order number within the household:
gen idp_ci = orden_persona   // or numper, nper, etc.
* Or construct:
gen idp_ci = _n              // only if data is already sorted by person within household
```

**Verify uniqueness of idh_ch + idp_ci:**
```stata
duplicates report idh_ch idp_ci
```

---

### factor_ci — Individual sampling weight

```stata
gen factor_ci = fex_c    // or peso, factor, wt, etc.
replace factor_ci = . if factor_ci <= 0
label variable factor_ci "Individual sampling weight"
```

**Common weight variable names:** `fex_c18`, `fexp`, `factor`, `wt`, `pw`, `pondera`, `factor_expansion`

**For USA IPUMS:** use `perwt` for individual weight, `hhwt` for household weight.

**Check:**
```stata
sum factor_ci
assert r(min) > 0
```

---

### factor_ch — Household sampling weight

```stata
gen factor_ch = fex_h    // or hhwt, peso_hog, etc.
* If not available, use factor_ci of the household head:
bysort idh_ch: gen factor_ch = factor_ci if relacion_ci == 1
bysort idh_ch: replace factor_ch = factor_ch[1]
label variable factor_ch "Household sampling weight"
```

---

### edad_ci — Age

```stata
gen edad_ci = p6040     // or edad, age, etc.
replace edad_ci = . if edad_ci < 0 | edad_ci > 120
label variable edad_ci "Age in completed years"
```

**If only year of birth is available:**
```stata
gen edad_ci = [survey_year] - anio_nacimiento
replace edad_ci = edad_ci - 1 if [survey_month] < mes_nacimiento  // birthday not yet passed
```

---

### sexo_ci — Sex

**HDMF coding:** 1 = Male, 2 = Female (matches most LAC surveys)

```stata
gen sexo_ci = p6020
label variable sexo_ci "Sex"
label define sexo 1 "Male" 2 "Female"
label values sexo_ci sexo
```

**If source uses 0/1 or M/F:**
```stata
gen sexo_ci = .
replace sexo_ci = 1 if source_sex == 0 | source_sex == "M"
replace sexo_ci = 2 if source_sex == 1 | source_sex == "F"
```

---

### relacion_ci — Relationship to household head

**HDMF codes:**
| Code | Relationship |
|------|-------------|
| 1 | Household head |
| 2 | Spouse / partner |
| 3 | Child / stepchild |
| 4 | Parent / in-law |
| 5 | Other relative |
| 6 | Non-relative / domestic worker |

```stata
gen relacion_ci = .
replace relacion_ci = 1 if p6050 == 1
replace relacion_ci = 2 if p6050 == 2
replace relacion_ci = 3 if p6050 == 3 | p6050 == 4
replace relacion_ci = 4 if p6050 == 5 | p6050 == 6
replace relacion_ci = 5 if p6050 >= 7 & p6050 <= 9
replace relacion_ci = 6 if p6050 == 10 | p6050 == 11
label variable relacion_ci "Relationship to household head"
```

---

### miembros_ci — Current household member

Excludes domestic workers, visitors, or absent members if the survey distinguishes them.

```stata
gen miembros_ci = 1    // by default, all observations are members
replace miembros_ci = 0 if relacion_ci == 6 & [domestic_worker_indicator]
label variable miembros_ci "Current household member"
```

If the survey does not distinguish: set `miembros_ci = 1` for all and document.

---

## Output table format

| HDMF Variable | Source Variable | Source Codes | HDMF Codes | Notes |
|---------------|----------------|-------------|-----------|-------|
| pais_c | — | — | "COL" (constant) | |
| idh_ch | | | | Concatenation logic: |
| idp_ci | | | | |
| factor_ci | | | | |
| factor_ch | | | | |
| edad_ci | | | | |
| sexo_ci | | | 1=Male, 2=Female | |
| relacion_ci | | | 1–6 | |
| miembros_ci | | | 0/1 | |
