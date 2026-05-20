# ESP Dictionary Check — 2018–2024 vs 2025
**Date:** 2026-04-29  
**Tool:** pyreadstat (metadataonly=True) on merged DTAs  
**Python:** `C:\Users\PABLOCOR\OneDrive - ...\Documents\undesa\.venv\Scripts\python.exe`

---

## Source files checked

| Year | File | Cols |
|------|------|------|
| 2018 | `bases armo/raw/esp/ESP_2018a_merged.dta` | 56 |
| 2019 | `bases armo/raw/esp/ESP_2019a_merged.dta` | 56 |
| 2020 | `bases armo/raw/esp/ESP_2020a_merged.dta` | 56 |
| 2021 | `bases armo/raw/esp/ESP_2021a_merged.dta` | 56 |
| 2022 | `bases armo/raw/esp/ESP_2022a_merged.dta` | 56 |
| 2023 | `bases armo/raw/esp/ESP_2023a_merged.dta` | 56 |
| 2024 | `bases armo/raw/esp/ESP_2024a_merged.dta` | 56 |
| 2025 | `bases armo/raw/esp/ESP_2025a_merged.dta` | 56 |

All files: 56 columns.

---

## Column differences vs 2025

| Year | Added vs 2025 | Removed vs 2025 |
|------|---------------|-----------------|
| 2018 | `horash` | `horash1` |
| 2019 | `horash` | `horash1` |
| 2020 | `horash` | `horash1` |
| 2021 | — | — |
| 2022 | — | — |
| 2023 | — | — |
| 2024 | — | — |

**Summary:** The only cross-year difference is `horash` (pre-2021 name for usual/contracted hours in main job) vs `horash1` (2021+ name). All other 55 columns are identical across all years.

---

## Impact on harmonization scripts

The `variablesBID.do` scripts use `horase` (actual hours worked last week) for `horaspri_ci` and `horastot_ci`, and `horeplu` (second-job hours) for the total. **Neither `horash` nor `horash1` is referenced in the harmonization code.** Therefore:

- **2021–2024:** Scripts are identical to `ESP_2025a_variablesBID.do` with `local ANO` changed only.
- **2018–2020:** Scripts are also identical — the `horash`/`horash1` difference does not affect the harmonization.

The SCHEMA NOTE block in each script documents this for future reference.

---

## Full column list (all years)

```
act, acta_ant, actplu, ano, ano_nac, anore, ausent, ayudfa, busca, busotr,
ccaa, ciclo, cursr, desea, dismas, ducon1, ducon2, ducon3, edad1, extna1,
extnpg, extpag, extra, factorel, horase, horash [pre-2021] / horash1 [2021+],
horasp, hordes, horeplu, horhplu, mashor, mes, nac1, ncursr, nforma, nivel,
npers, nvivi, ocup, ocupa_ant, ocuplu, ofemp, paina1, parco1, prona1, prov,
relpp1, rzndish, sexo1, sitplu, situ, situa_ant, sp, traplu, trarem, trimestre
```

---

## HDMF-critical variable status

| HDMF variable | EPA source | Status | Notes |
|---------------|------------|--------|-------|
| `factor_ci` | `factorel / 10000` | STABLE | All years |
| `edad_ci` | `edad1` | STABLE | All years |
| `sexo_ci` | `sexo1` (1=M, **6=F**) | STABLE | Non-standard female code |
| `relacion_ci` | `relpp1` | STABLE | All years |
| `migrante_ci` | `paina1` / `prona1` | STABLE | All years |
| `migrantiguo5_ci` | `anore` | STABLE | Design name ANORE1 pre-2021, but build script normalises to `anore` |
| `mig_pais_ci` | `paina1` (ISO 3166-1 numeric) | STABLE | All years |
| `condocup_ci` | `trarem`, `ayudfa`, `ausent`, `busca`, `desea` | STABLE | All years |
| `formal_ci` | `situ` (proxy) | STABLE | No SS question in EPA |
| `tipocontrato_ci` | `ducon1` | STABLE | All years |
| `horaspri_ci` | `horase` | STABLE | All years |
| `horastot_ci` | `horase` + `horeplu` | STABLE | All years (horeplu present in all) |
| `aedu_ci` | `nforma` (CNED-2014) | STABLE | All years |
| `edu_isced` | `nforma` | STABLE | All years |
| `edu_hdmf` | `nforma` | STABLE | Cat. 8 (univ. incomplete) missing — not in NFORMA |
| `ylm_ci`…`remesas_ch` | — | NOT AVAILABLE | EPA has no income module |
| `cotizando_ci`, `afiliado_ci` | — | NOT AVAILABLE | EPA has no SS question |

---

## Known issues in build_epa_annual.py (do not affect harmonization)

1. **BUSCA pre-2021 position:** `COLS_PRE2021` reads BUSCA at 0-indexed (149,150) = position 150-150, but design says pre-2021 BUSCA is at 142-142. This may cause unemployment classification errors for 2018-2020. **Not fixed yet** — requires build script update and re-merge.
2. **OCUPLU pre-2021 position:** Script reads (122,124); design says 125-126. Affects secondary-job occupation code only. Minor issue.

These issues are in `build_epa_annual.py`, not in the `variablesBID.do` scripts.
