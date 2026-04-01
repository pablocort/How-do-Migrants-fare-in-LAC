# Skill: Map Migration Variables

## Purpose
Map raw household survey variables related to migration status, country of birth/origin, and migration duration to HDMF standard variables.

## HDMF target variables

| HDMF Variable | Type | Description |
|---------------|------|-------------|
| `migrante_ci` | binary | Born outside the survey country (foreign-born) |
| `mig_pais_ci` | string/code | Country of birth or origin |
| `migrantiguo5_ci` | binary | Migrated more than 5 years ago (long-term migrant) |

---

## Mapping checklist

### migrante_ci — Foreign born indicator

**Most common source question:** "Where were you born?" or "What is your nationality?"

**Preferred definition:** Born in a country different from the survey country (place of birth, not citizenship).
- Use place of birth over nationality when both are available
- Children born abroad to foreign parents: `migrante_ci = 1`
- Second-generation (born in country to foreign parents): `migrante_ci = 0`

```stata
gen migrante_ci = .
* Pattern A: direct birthplace question with country codes
replace migrante_ci = 0 if pais_nacimiento == [survey_country_code]
replace migrante_ci = 1 if pais_nacimiento != [survey_country_code] & !missing(pais_nacimiento)

* Pattern B: categorical birthplace (this country / another country)
replace migrante_ci = 0 if p3373 == 1   // born in this country
replace migrante_ci = 1 if p3373 == 2   // born abroad (nationals returning)
replace migrante_ci = 1 if p3373 == 3   // born abroad (foreign nationals)
```

**Note:** Some surveys use p3373 == 3 as "foreign born" and p3373 == 2 as "Colombian/Peruvian born abroad" — in that case, `migrante_ci = 1` only for code 3 (true immigrants), or 1 for both 2 and 3 depending on analytical definition. Document the choice.

---

### mig_pais_ci — Country of origin

Capture the foreign country of birth/origin for migrants.

**Source questions:** "If born abroad, what country?" or "Country of birth"

```stata
gen mig_pais_ci = ""
replace mig_pais_ci = pais_nacimiento_str if migrante_ci == 1
* Or from numeric country code variable:
replace mig_pais_ci = string(cod_pais_nacimiento) if migrante_ci == 1
```

**Standardize country names for Venezuelan migrants** (critical for HDMF analysis):
```stata
replace mig_pais_ci = "Venezuela" if regexm(upper(mig_pais_ci), "VENEZUELA|VEN|862")
replace mig_pais_ci = "Colombia"  if regexm(upper(mig_pais_ci), "COLOMBIA|COL|170")
replace mig_pais_ci = "Peru"      if regexm(upper(mig_pais_ci), "PER[UÚ]|604")
replace mig_pais_ci = "Ecuador"   if regexm(upper(mig_pais_ci), "ECUADOR|ECU|218")
replace mig_pais_ci = "Bolivia"   if regexm(upper(mig_pais_ci), "BOLIVI|BOL|068")
replace mig_pais_ci = "Haiti"     if regexm(upper(mig_pais_ci), "HAIT[IÍ]|HTI|332")
```

**For non-migrants:** leave `mig_pais_ci` as missing (`.` or `""`)

---

### migrantiguo5_ci — Long-term migrant

Captures whether the migrant arrived more than 5 years before the survey reference date.

**Source questions:** "What year did you arrive in [country]?" or "How many years have you lived in [country]?"

```stata
* Pattern A: year of arrival
gen migrantiguo5_ci = .
replace migrantiguo5_ci = 1 if (anio_encuesta - anio_llegada) > 5 & migrante_ci == 1
replace migrantiguo5_ci = 0 if (anio_encuesta - anio_llegada) <= 5 & migrante_ci == 1
replace migrantiguo5_ci = . if migrante_ci != 1

* Pattern B: duration in years
gen migrantiguo5_ci = .
replace migrantiguo5_ci = 1 if anos_residencia > 5 & migrante_ci == 1
replace migrantiguo5_ci = 0 if anos_residencia <= 5 & migrante_ci == 1
replace migrantiguo5_ci = . if migrante_ci != 1

* Pattern C: categorical (< 2 yrs / 2-5 yrs / > 5 yrs)
gen migrantiguo5_ci = .
replace migrantiguo5_ci = 0 if cat_duracion == 1 | cat_duracion == 2
replace migrantiguo5_ci = 1 if cat_duracion == 3
replace migrantiguo5_ci = . if migrante_ci != 1
```

**If the survey does not ask about duration:** set `migrantiguo5_ci = .` for all and document.

---

## Venezuelan migration — special handling

Venezuela is the primary migrant group of interest in HDMF. After constructing `mig_pais_ci`, always verify:

```stata
* Count Venezuelan migrants
count if migrante_ci == 1 & mig_pais_ci == "Venezuela"
di "Venezuelan migrants: " r(N)

* Share of Venezuelans among all migrants
count if migrante_ci == 1
local total_mig = r(N)
count if migrante_ci == 1 & mig_pais_ci == "Venezuela"
di "Venezuelan share of migrants: " %5.1f r(N)/`total_mig'*100 "%"
```

**Plausibility checks by country (approximate 2024 estimates):**
| Survey Country | Expected Venezuelan share of migrants |
|---------------|--------------------------------------|
| Colombia | 50–70% |
| Peru | 40–60% |
| Ecuador | 30–50% |
| Chile | 20–40% |
| USA | < 5% |

---

## Labels

```stata
label variable migrante_ci    "Foreign born (1=yes)"
label variable mig_pais_ci    "Country of birth (migrants only)"
label variable migrantiguo5_ci "Migrated >5 years ago (migrants only)"

label define migrante 0 "Native" 1 "Foreign born"
label values migrante_ci migrante

label define migrantiguo 0 "Recent (<= 5 yrs)" 1 "Long-term (> 5 yrs)"
label values migrantiguo5_ci migrantiguo
```

---

## Output table format

| HDMF Variable | Source Variable | Source Codes | Logic | Notes |
|---------------|----------------|-------------|-------|-------|
| migrante_ci | | | | |
| mig_pais_ci | | | | |
| migrantiguo5_ci | | | | |
