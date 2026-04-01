# Skill: Map Income Variables

## Purpose
Map raw household survey income variables to HDMF standard monthly income measures at both individual and household level.

## HDMF target variables

| HDMF Variable | Type | Description |
|---------------|------|-------------|
| `ylm_ci` | continuous (≥0) | Monthly labor income, primary + secondary job (cash) |
| `ylnm_ci` | continuous (≥0) | Monthly labor income in-kind (food, housing, etc.) |
| `ynlm_ci` | continuous (≥0) | Monthly non-labor income (transfers, pensions, rent) |
| `ytot_ci` | continuous (≥0) | Total monthly income (ylm + ylnm + ynlm) |
| `remesas_ci` | continuous (≥0) | Monthly remittances received (individual) |
| `remesas_ch` | continuous (≥0) | Monthly remittances received (household total) |

All values in **nominal local currency units (LCU)**, monthly frequency.

---

## Mapping checklist

### ylm_ci — Labor income (cash)

Includes: wages, salaries, bonuses, profits from self-employment.
Excludes: in-kind payments, social security contributions paid by employer.

```stata
gen ylm_ci = .
* Primary job:
replace ylm_ci = ingreso_primario if !missing(ingreso_primario)
* Add secondary job income:
replace ylm_ci = ylm_ci + ingreso_secundario if !missing(ingreso_secundario)
replace ylm_ci = ylm_ci + 0 if missing(ingreso_secundario) & emp_ci == 1
replace ylm_ci = . if emp_ci != 1

label variable ylm_ci "Monthly labor income (cash), LCU"
```

**Frequency conversions:**
```stata
* Weekly → monthly:
replace ylm_ci = ylm_ci * (52/12)
* Biweekly → monthly:
replace ylm_ci = ylm_ci * 2
* Annual → monthly:
replace ylm_ci = ylm_ci / 12
* Daily → monthly (use actual workdays or 30 days):
replace ylm_ci = ylm_ci * 30
```

**Valid values:**
- `ylm_ci = 0`: valid for employed with no earnings (own-account workers in bad periods, unpaid family workers)
- `ylm_ci = .`: for non-employed
- Never negative

---

### ylnm_ci — Labor income in-kind

```stata
gen ylnm_ci = 0 if emp_ci == 1   // default to zero (most workers receive no in-kind payment)
replace ylnm_ci = ingreso_especie if !missing(ingreso_especie) & emp_ci == 1
replace ylnm_ci = . if emp_ci != 1
label variable ylnm_ci "Monthly labor income in-kind, LCU"
```

If the survey does not ask about in-kind payments: set `ylnm_ci = 0` for all employed and document.

---

### ynlm_ci — Non-labor income

Includes: retirement pensions, government transfers (Bolsa Família, Ingreso Solidario, etc.), rental income, interests, dividends.
Excludes: labor income, remittances (tracked separately).

```stata
gen ynlm_ci = 0
replace ynlm_ci = pension_ci if !missing(pension_ci)
replace ynlm_ci = ynlm_ci + transferencias_ci if !missing(transferencias_ci)
replace ynlm_ci = ynlm_ci + renta_ci if !missing(renta_ci)
label variable ynlm_ci "Monthly non-labor income, LCU"
```

---

### ytot_ci — Total income

```stata
gen ytot_ci = .
replace ytot_ci = 0
replace ytot_ci = ytot_ci + ylm_ci  if !missing(ylm_ci)
replace ytot_ci = ytot_ci + ylnm_ci if !missing(ylnm_ci)
replace ytot_ci = ytot_ci + ynlm_ci if !missing(ynlm_ci)
replace ytot_ci = . if missing(ylm_ci) & missing(ylnm_ci) & missing(ynlm_ci)
label variable ytot_ci "Total monthly income, LCU"
```

---

### remesas_ci / remesas_ch — Remittances

**remesas_ci:** remittances received by the individual in the last month.
**remesas_ch:** total household remittances (sum of all individuals, or household-level question).

```stata
gen remesas_ci = .
replace remesas_ci = remesas_mensuales if !missing(remesas_mensuales)
replace remesas_ci = remesas_anuales / 12 if !missing(remesas_anuales)
replace remesas_ci = 0 if recibe_remesas == 0    // household says no remittances
label variable remesas_ci "Monthly remittances received, individual, LCU"

* Aggregate to household level if needed:
bysort idh_ch: egen remesas_ch = total(remesas_ci)
label variable remesas_ch "Monthly remittances received, household, LCU"
```

**If survey asks only at household level:**
```stata
gen remesas_ch = remesas_hogar_mensual
gen remesas_ci = .   // cannot disaggregate to individual level
```

---

## Cross-country comparability notes

Income variables are **not PPP-adjusted** at the harmonization stage. Conversion to a common currency (USD PPP) happens in the analysis pipeline (`hdmf_2.py`). The harmonization only ensures:
1. Monthly frequency
2. Nominal LCU
3. Consistent component coverage

**If cross-country income comparison is desired**, the `indicator_analyst` agent will apply PPP conversion factors from the World Bank ICP.

---

## Quality checks for income

```stata
* No negative incomes:
assert ylm_ci >= 0 if !missing(ylm_ci)
assert ytot_ci >= 0 if !missing(ytot_ci)

* ytot >= ylm:
assert ytot_ci >= ylm_ci if !missing(ytot_ci) & !missing(ylm_ci)

* Flag extreme outliers (p99 > 100x median):
sum ylm_ci if emp_ci == 1, detail
di "Median: " r(p50) "  p99: " r(p99) "  Ratio: " r(p99)/r(p50)
if r(p99)/r(p50) > 100 {
    di "WARNING: extreme income outliers detected"
}

* Missing rate among employed:
count if emp_ci == 1 & missing(ylm_ci)
di "Missing labor income among employed: " r(N)
```

---

## Output table format

| HDMF Variable | Source Variable(s) | Frequency | Components included | Notes |
|---------------|-------------------|-----------|---------------------|-------|
| ylm_ci | | | | |
| ylnm_ci | | | | |
| ynlm_ci | | | | |
| ytot_ci | | | Derived | |
| remesas_ci | | | | |
| remesas_ch | | | | |
