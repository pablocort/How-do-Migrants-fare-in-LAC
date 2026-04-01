# Skill: Map Labor Market Variables

## Purpose
Map raw household survey variables related to employment status, formality, hours worked, and contract type to HDMF standard variables.

## HDMF target variables

| HDMF Variable | Type | Description |
|---------------|------|-------------|
| `condocup_ci` | categorical (1/2/3) | Employment condition: 1=Employed, 2=Unemployed, 3=Inactive |
| `emp_ci` | binary | Currently employed |
| `desemp_ci` | binary | Currently unemployed |
| `pea_ci` | binary | In labor force (employed OR unemployed) |
| `formal_ci` | binary | Formal employment (contributes to social security/pension) |
| `tipocontrato_ci` | categorical (1/2/3) | Contract: 1=Written, 2=Verbal, 3=No contract |
| `horaspri_ci` | continuous | Hours worked in primary job (weekly) |
| `horastot_ci` | continuous | Total hours worked (primary + secondary, weekly) |
| `cotizando_ci` | binary | Contributing to pension |
| `afiliado_ci` | binary | Affiliated to health/social security |

---

## Mapping checklist

### Employment condition (condocup_ci)

Find the variable that asks about labor force status. Common survey question types:
- **Direct classification**: "Last week, did you work / look for work / neither?" → direct mapping
- **Derived**: Must combine occupation status + job search activity

**Typical source variables:**
- OCC/OCUP: occupation code (non-missing = employed in some surveys)
- PEA/ACTIVO: labor force participation flag
- BUSCTRA/BUSQUEDA: job search flag

**Logic:**
```stata
gen condocup_ci = .
replace condocup_ci = 1 if [worked at least 1 hour last week]
replace condocup_ci = 2 if [did not work BUT searched for work last week]
replace condocup_ci = 3 if [did not work AND did not search]
replace condocup_ci = . if edad_ci < [min_age] | edad_ci > 65
```

**Derive binary dummies consistently:**
```stata
gen emp_ci    = (condocup_ci == 1) if !missing(condocup_ci)
gen desemp_ci = (condocup_ci == 2) if !missing(condocup_ci)
gen pea_ci    = (condocup_ci == 1 | condocup_ci == 2) if !missing(condocup_ci)
```

---

### Formality (formal_ci)

**Preferred definition (LAC standard):** Worker contributes to pension OR is affiliated to health/social security.

```stata
gen cotizando_ci = .
replace cotizando_ci = 1 if [pension contribution question == yes]
replace cotizando_ci = 0 if [pension contribution question == no] & emp_ci == 1

gen afiliado_ci = .
replace afiliado_ci = 1 if [health affiliation == yes]
replace afiliado_ci = 0 if [health affiliation == no] & emp_ci == 1

gen formal_ci = .
replace formal_ci = 1 if cotizando_ci == 1 | afiliado_ci == 1
replace formal_ci = 0 if cotizando_ci == 0 & afiliado_ci == 0 & emp_ci == 1
replace formal_ci = . if emp_ci != 1
```

**If only one social security indicator is available:** use it alone and document in the mapping notes.

**USA / OECD countries:** Formal employment may be defined differently (e.g., employee with tax withholding). Document the alternative definition used.

---

### Hours worked (horaspri_ci, horastot_ci)

- Report **weekly** hours
- If survey reports daily hours: multiply by days worked per week
- If the survey only has total hours without primary/secondary split: set `horaspri_ci = horastot_ci`
- Cap at 168 hours/week maximum (flag values > 100 as suspicious)

```stata
gen horaspri_ci = [hours_primary_variable]
replace horaspri_ci = . if horaspri_ci < 0
replace horaspri_ci = . if emp_ci != 1

gen horastot_ci = [hours_primary] + [hours_secondary]
replace horastot_ci = horaspri_ci if missing([hours_secondary])
replace horastot_ci = . if emp_ci != 1
```

---

### Contract type (tipocontrato_ci)

**HDMF codes:**
- 1 = Written (formal contract)
- 2 = Verbal (informal agreement)
- 3 = No contract

```stata
gen tipocontrato_ci = .
replace tipocontrato_ci = 1 if [source_var == written_contract_code]
replace tipocontrato_ci = 2 if [source_var == verbal_contract_code]
replace tipocontrato_ci = 3 if [source_var == no_contract_code]
replace tipocontrato_ci = . if emp_ci != 1
```

If the survey does not distinguish verbal from no contract, use:
- 1 = Written
- 2 = Any other (and document)

---

## Population restriction notes

| Variable | Apply to |
|----------|----------|
| condocup_ci, emp_ci, desemp_ci, pea_ci | Working-age population (age ≥ lower bound) |
| formal_ci, tipocontrato_ci | Employed only (emp_ci == 1) |
| horaspri_ci, horastot_ci | Employed only (emp_ci == 1) |
| cotizando_ci, afiliado_ci | Employed only (emp_ci == 1) |

**Working age lower bound by country:**
- Colombia GEIH: 12 years
- Chile CASEN: 15 years
- Ecuador ENEMDU: 15 years
- Peru ENAHO: 14 years
- USA IPUMS: 16 years
- Spain EPA: 16 years
- Mexico ENOE: 14 years

---

## Output table format

| HDMF Variable | Source Variable | Value Codes | Transformation | Population Restriction | Notes |
|---------------|----------------|-------------|----------------|----------------------|-------|
| condocup_ci | | | | | |
| emp_ci | | | Derived from condocup_ci | | |
| desemp_ci | | | Derived from condocup_ci | | |
| pea_ci | | | Derived from condocup_ci | | |
| formal_ci | | | | emp_ci == 1 | |
| tipocontrato_ci | | | | emp_ci == 1 | |
| horaspri_ci | | | | emp_ci == 1 | |
| horastot_ci | | | | emp_ci == 1 | |
| cotizando_ci | | | | emp_ci == 1 | |
| afiliado_ci | | | | emp_ci == 1 | |
