# Survey Metadata — PER ENAHO 2024a

| Field | Value |
|-------|-------|
| **Country name** | Peru |
| **ISO3 code** | PER |
| **Survey name** | Encuesta Nacional de Hogares sobre Condiciones de Vida y Pobreza |
| **Survey acronym** | ENAHO |
| **Producing institution** | Instituto Nacional de Estadística e Informática (INEI) |
| **Reference period** | Annual 2024 → `2024a` |
| **HDMF file code** | `PER_2024a` |

---

## Files

| Field | Value |
|-------|-------|
| **Raw file location** | `bases armo/raw/per/` |
| **Raw file name** | `PER_2024a.dta` |
| **Number of modules** | Pre-merged (single DTA) |
| **Merge key variables** | conglome + vivienda + hogar + codperso |
| **Data dictionary** | `Diccionario2024.pdf` |

---

## Survey design

| Field | Value |
|-------|-------|
| **Individual weight variable** | `facpob07` |
| **Household weight variable** | `factor07` |
| **Reference week** | Last 7 days (labor module) |

**Sampling design:** Multi-stage cluster, stratified

---

## Population coverage

| Field | Value |
|-------|-------|
| **Minimum survey age** | 0 (all ages recorded) |
| **Labor age cutoff** | 15–64 (applied in condocup_ci construction) |
| **Target population** | National (urban + rural) |

---

## Migration module

**Source module:** Módulo 400 (Salud) — p401 series

| Field | Value |
|-------|-------|
| **Migration variable** | `p401g2` — district code of mother's residence at respondent's birth |
| **Codes** | codes < 10000 → born in foreign country → `migrante_ci = 1` |
| **Migration duration** | `p401f` — 5 years ago, did you live in this district? + `p401g` |
| **Country code variable** | `p401g2` (numeric district/country code) |
| **Country name** | Hard-coded: Venezuela = 4037; others not fully mapped in reference |

**migrantiguo5_ci construction:**
```stata
gen migrantiguo5_ci = (migrante_ci==1 & (p401f==1 | (p401g>10000 & p401g!=.))) ///
    if migrante_ci!=. & p401f!=3 & p401g!=999999 & p401f!=. & !inrange(edad_ci,0,4)
```

---

## Education module

| Field | Value |
|-------|-------|
| **Level variable** | `p301a` — educational level attained |
| **Years variable** | `p301b` — grade/year within level |
| **Completion indicator** | `p301c` — grades completed within level |
| **p301a codes** | 1=Sin nivel, 2=Inicial, 3=Primaria incompleta, 4=Primaria completa, 5=Secundaria incompleta, 6=Secundaria completa, 7=Superior no univ. incompleta, 8=Superior no univ. completa, 9=Superior univ. incompleta, 10=Superior univ. completa, 11=Maestría/Doctorado, 12=Básica Especial |

---

## Labor module

| Field | Value |
|-------|-------|
| **Employment variables** | `p501` (worked last week), `p502` (has fixed job), `p503` (has business) |
| **Inactivity classification** | `p5041`–`p50411` (reason for not seeking work) |
| **Inactivity reason** | `p546` — main activity (1=pensioner, 4=student, 5=housework, 6=retired) |
| **Hours primary** | `p513t` — hours worked in primary occupation last week |
| **Hours secondary** | `p518` — hours worked in secondary occupation(s) |
| **Occupation category** | `p507` — 1=employer, 2=self-employed, 3=employee, 4=laborer, 5=unpaid, 6=domestic, 7=other |
| **Contract type** | `p511a` — 1=indefinite, 2=fixed-term, 3=trial, 4=apprenticeship, 5=professional fees, 6=CAS, 7=no contract, 8=other |
| **Cotizando variable** | `p558a1`–`p558a4` (pension system affiliation) + `p558b2` (year of last contribution) |
| **condocup_ci construction** | Derived: p501==1 OR p502==1 OR p503==1 → occupied; p501==2 & p502==2 & p503==2 → unemployed; unemployed + all p5041-p50411==2 → inactive |

---

## Income module

**EXCLUDED from harmonization** — income variables are commented out in the reference script (`PER_2024_variablesBID.do`) and should remain excluded in all waves.

Remittances (`remesas_ci`, `remesas_ch`) are included:
- `remesas_ci` = `d5563c/12` (domestic) + `d5563e/12` (foreign)

---

## Known issues

- `condocup_ci` is limited to ages 15–64 (`!inrange(edad_ci, 15,64)` → missing)
- `mig_pais_ci` is only partially mapped (only Venezuela code 4037 is labeled; others → "Otro")
- `cotizando_ci` requires contribution in current year (p558b2==2024)

---

## Status

| Field | Value |
|-------|-------|
| **Script** | `do armo/per/PER_2024_variablesBID.do` |
| **Output** | `bases armo/armo/per/PER_2024a_BID.dta` ✅ |
| **Date harmonized** | Prior to 2026-04-10 |
| **Responsible** | HDMF team (Steffanny R.) |
