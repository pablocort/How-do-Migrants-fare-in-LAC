# HND — Remittances & Income Variable Assessment
**Date:** 2026-05-26  
**Branch:** `remittances`  
**Sources:** Excel/CSV dictionaries (2021–2025) + pyreadstat DTA inspection (2018, 2019); cross-validated against existing do-files.

---

## 1. OIH Module availability (non-labor income + remittances source vars)

The Honduras EPHPM collects other-income household (OIH) variables covering pensions, rents, transfers, government programs, and remittances. The module was **restructured in 2022** and then **restored in 2023**.

| Wave | OIH module | Period convention | Exchange rate local | Notes |
|------|---|---|---|---|
| 2018m6 | ✅ `oih01–oih17` | Quarterly → divide by 3 | `tc_c1 = 23.68` | Confirmed via raw DTA |
| 2019m6 | ✅ `oih01–oih17` | Quarterly → divide by 3 | `tc_c1 = 24.08` | Confirmed via raw DTA |
| 2021m6 | ✅ `OIH01–OIH17` (UPPERCASE) | **Already monthly — do NOT divide by 3** | `tc_c1 ≈ 24.50` | Script has rename loop; OIH16/OIH17 = "Efectivo" (cash transfers) |
| 2022m6 | ❌ **Absent** | — | — | Module removed entirely from 2022 questionnaire; confirmed via 2022 dictionary (no OIH vars) |
| 2023m6 | ✅ `oih01–oih20` | Quarterly → divide by 3 | `tc_c1 = 24.7285` | Expanded vs 2018–2019: adds oih16 (Bono Rosa), oih17 (energy subsidy), oih18 (fuel subsidy), oih19 (government programs), oih20 (otros) |
| 2024m6 | ✅ `OIH01–OIH20` (UPPERCASE) | Quarterly → divide by 3 | `tc_c1 = 25.12562814` | Confirmed via 2024 dictionary; script has rename loop |
| 2025m7 | ✅ `OIH01–OIH21` (UPPERCASE) | Quarterly → divide by 3 | `tc_c1 = 26.00` | OIH21 = "Otros" (new item); script has rename loop |

---

## 2. Remittances variables in detail

### Primary remittances source variables (OIH12 family)

| Variable name | Label | Currency | Present in |
|---|---|---|---|
| `oih12_lps` / `OIH12_LPS` | Remesas del exterior en Lempiras | HNL (cash) | 2018, 2019, 2021, 2023, 2024, 2025 |
| `oih12_us` / `OIH12_US` | Remesas del exterior en Dólares | USD (cash) | 2018, 2019, 2021, 2023, 2024, 2025 |
| `oih12_lps_esp` / `OIH12_LPS_ESP` | Remesas del exterior Lempiras Especies | HNL (in-kind) | 2018, 2019, 2021, 2023, 2024, 2025 |
| `oih12_us_esp` / `OIH12_US_ESP` | Remesas del exterior en Dólares Especies | USD (in-kind) | 2018, 2019, 2021, 2023, 2024, 2025 |
| **None** | — | — | **2022 — no remittances variable exists** |

### Additional remittances-specific variables (from 2023 onward)

| Variable | Label | Waves |
|---|---|---|
| `ME02` | Algún miembro de este hogar recibió remesas el mes pasado (yes/no) | 2023, 2024, 2025 |
| `OI002` / `OI002_1`…`OI002_12` | Destino de las remesas recibidas en los últimos 3 meses (usage) | 2023 (12 binary vars), 2024–2025 (single coded var) |
| `OI004` | Frecuencia con que recibe remesas en los últimos 12 meses | 2023, 2024, 2025 |
| `YHREME` / `yhReme` | Ingreso del hogar por remesas (INE aggregate) | 2018, 2019, 2023, 2024, 2025 |

### `remesas_ci` construction formula

For waves with quarterly data (2018, 2019, 2023, 2024, 2025):
```
remesas_ci = (oih12_lps + oih12_lps_esp + oih12_us * tc_c1 + oih12_us_esp * tc_c1) / 3
```

For 2021 (already monthly):
```
remesas_ci = oih12_lps + oih12_lps_esp + oih12_us * tc_c1 + oih12_us_esp * tc_c1
```

For 2022: `remesas_ci = .` (no source data)

---

## 3. Non-labor income (`ynlm_ci`) construction

### OIH component mapping (all waves with OIH module)

| OIH item | Label | Variants |
|---|---|---|
| oih01 | Pensión (social security pension) | `_lps`, `_us` |
| oih02 | Jubilación (retirement pension) | `_lps`, `_us` |
| oih03 | Alquileres (rental income) | `_lps`, `_us` |
| oih04 | Descuento adulto mayor (elderly discount) | scalar |
| oih05 | Pensión alimenticia/divorcio | `_lps`, `_us` |
| oih06 | Ayudas familiares (family transfers) | `_lps`, `_us`, `_lps_esp`, `_us_esp` |
| oih07 | Ayudas particulares (private transfers) | `_lps`, `_us`, `_lps_esp`, `_us_esp` |
| oih08 | Alimentación escolar / Merienda | scalar (2021–2025), `_lps`/`_us` (2018–2019) |
| oih09 | Útiles/Bolsón escolar | scalar |
| oih10 | Uniformes escolares | scalar |
| oih11 | Becas (scholarships) | scalar |
| **oih12** | **Remesas** — included in ynlm_ci but also computed separately as `remesas_ci` | `_lps`, `_us`, `_lps_esp`, `_us_esp` |
| oih13 | Bono Esperanza / Bono Vida Mejor | scalar |
| oih14 | Bono personas con discapacidad / adultos mayores | scalar |
| oih15 | Bono tecnológico / Bolsa solidaria | scalar |
| oih16 | Bono Rosa / Otros Programas Gobierno | `_lps`, `_us` (varies by wave) |
| oih17 | Subsidio energía / Otros | `_lps`, `_us` (varies) |
| oih18 | Subsidio combustible | scalar (2023+) |
| oih19 | Otros programas de gobierno | `_lps`, `_lps_esp` (2023+) |
| oih20 | Otros | `_lps`, `_lps_esp` (2023+); `Bono Red Solidaria` in 2025 |
| oih21 | Otros (new item) | `_lps`, `_lps_esp` (2025 only) |

**Note on double-counting:** `oih12` (remittances) is added to **both** `ynlm_ci` and `remesas_ci`. This follows the existing 2023m6 design. `ytot_ci = ylm_ci + ylnm_ci + ynlm_ci + remesas_ci` therefore double-counts remittances. This is a known design choice in the current pipeline — flagged for QA review.

---

## 4. Geographic variables

| Wave | Department var | Values | Municipality var | Notes |
|------|---|---|---|---|
| 2018m6 | `depto` | 1–18 (all 18 departments) | `municipio` | Both confirmed in raw DTA |
| 2019m6 | `depto` | 1–18 | ❌ not available | Confirmed via DTA; `ine01` used in current script is **wrong** |
| 2021m6 | ❌ none | — | ❌ | Only geographic var is `DOMINIO` (1=Tegucigalpa, 2=SPS, 3=Ciudades Medianas, 4=Ciudades Pequeñas, 5=Rural) |
| 2022m6 | ❌ none | — | ❌ | Not in 2022 dictionary |
| 2023m6 | ❌ (current residence) | — | ❌ | CD02_DEPT = birth dept; CD04_DEPT = previous residence dept; neither is current residence |
| 2024m6 | `DEPMUESTRA` | 1–18 | ❌ | "Departamento de muestra" — current residence ✅ |
| 2025m7 | `DEPTO` | 1–18 | ❌ | After rename loop: `depto` ✅ |

---

## 5. Issues found in current do-files

| # | Wave | Issue | Impact | Fix needed |
|---|------|--------|--------|------------|
| 1 | 2018m6 | `municipio` exists in raw data but is not captured in the do-file | `municipio_c` would have data for ~26K observations | Add `gen municipio_c = .` + `capture clonevar municipio_c = municipio` |
| 2 | 2019m6 | `region_c` uses `capture clonevar region_c = ine01` but `ine01` is NOT in the raw DTA (raw has `depto`) | region_c = missing for all 2019 observations | Change source to `depto` |
| 3 | 2021m6 | `remesas_ci` omits USD variants (`oih12_us`, `oih12_us_esp`); `ynlm_ci` omits all USD oih variants | Under-counts remittances and non-labor income for USD-denominated flows | Add USD oih components (no /3 — 2021 is already monthly) |
| 4 | 2024m6 | `ynlm_ci = .` and `remesas_ci = .` despite OIH01–20 being present in raw data | Entire non-labor income module is missing from 2024 BID file | Add full oih01–20 block (/3) following 2023m6 pattern |
| 5 | 2025m7 | Same as 2024; also missing new `oih21_lps` | Same impact | Add full oih01–21 block (/3) |

---

## 6. Summary: variable count in `remesas_ci` and `ynlm_ci` by wave

| Wave | `remesas_ci` components used | `ynlm_ci` OIH items | `ytot_ci` complete? |
|------|---|---|---|
| 2018m6 | 4 (lps + us + lps_esp + us_esp) /3 | oih01–15 /3 | ✅ |
| 2019m6 | 4 /3 | oih01–15 /3 | ✅ |
| 2021m6 | 2 only (lps + lps_esp) — **missing USD** | oih01–15 LPS only — **missing USD** | ⚠️ partial |
| 2022m6 | `.` (no data) | `.` (no data) | `.` |
| 2023m6 | 4 /3 | oih01–20 /3 | ✅ |
| 2024m6 | `.` (data exists, not calculated) | `.` (data exists, not calculated) | ⚠️ labor only |
| 2025m7 | `.` (data exists, not calculated) | `.` (data exists, not calculated) | ⚠️ labor only |

---

## 7. Recommended fixes (for next session)

Priority order:
1. **2024m6** — add full ynlm_ci + remesas_ci (most recent complete wave, highest analytical value)
2. **2025m7** — same, adds oih21
3. **2021m6** — add USD oih components
4. **2019m6** — fix `region_c` source variable
5. **2018m6** — add `municipio_c`

See plan file for exact Stata code blocks.
