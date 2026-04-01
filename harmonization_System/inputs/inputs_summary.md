# HDMF — Input Databases Summary

Pipeline goal: harmonize raw household/labor surveys into `*_BID.dta` files stored in `bases armo/armo/`, then processed by `hdmf_2.py` to produce indicator tables and figures.

---

## Main Input Databases (2023–2025)

| # | Country | Code | Survey | Year | Period | Raw file(s) | Format | Merge step | Harmonization script | Output (`armo/`) | Status |
|---|---------|------|--------|------|--------|-------------|--------|------------|---------------------|------------------|--------|
| 1 | Brazil | BRA | SISMIGRA | 2025 | Jan–Dec | `raw/bra/sismigra_janeiro_dezembro_2025.xlsx` | XLSX | — | *(none)* | *(none)* | ❌ Not started |
| 2 | Chile | CHL | CASEN | 2024 | Annual | `raw/chl/casen_2024.dta` | DTA | — | `chl/CHL_2024_variablesBID.do` | `CHL_2024a_BID.dta` | ✅ Done |
| 3 | Colombia | COL | GEIH | 2023 | Q3 | `raw/col/COL_2023t3.dta` | DTA | — | *(none)* | *(none)* | ❌ Raw only, no script |
| 4 | Colombia | COL | GEIH | 2024 | Q3 | `raw/col/COL_2024t3.dta` | DTA | `COL_2024t3_mergeBID.do` | `COL_2024t3_variablesBID.do` | `col/COL_2024t3_BID.dta` ¹ | ✅ Done |
| 5 | Colombia | COL | GEIH | 2025 | Q3 | `raw/col/COL_2025t3.dta` | DTA | `COL_2025t3_mergeBID.do` | `COL_2025t3_variablesBID.do` | `COL_2025t3_BID.dta` | ✅ Done |
| 6 | Ecuador | ECU | ENEMDU | 2024 | Dec (m12) | `raw/ecu/1_BDD_ENEMDU_2024_SPSS.zip` | ZIP/SAV | — | `ECU_2024m12_variablesBID.do` | *(none)* | ⚠️ Script exists, data still zipped |
| 7 | Ecuador | ECU | ENEMDU | 2025 | Dec (m12) | `raw/ecu/ECU_2025m12.dta` (merged from SAV modules) | DTA | `ECU_2025m12_mergeBID.do` | `ECU_2025m12_variablesBID.do` | `ECU_2025m12_BID.dta` | ✅ Done |
| 8 | Spain | ESP | EPA | 2025 | Q3 | `raw/esp/EPA_2025T3.dta` | DTA | — | `ESP_2025t3_variablesBID.do` | *(none)* | ⚠️ Script has errors |
| 9 | Mexico | MEX | ENOE | 2025 | Q4 | `raw/mex/MEX_2025t4.dta` (merged from 5 modules) | DTA | `MEX_2025t4_mergeBID.do` | *(none — missing)* | *(none)* | ⚠️ Merge done, variables script missing |
| 10 | Peru | PER | ENAHO | 2024 | Annual | `raw/per/PER_2024a.dta` | DTA | `PER_2024a_mergeBID.do` | `PER_2024a_variablesBID.do` | `PER_2024a_BID.dta` | ✅ Done |
| 11 | United States | USA | IPUMS Census | 2024 | Annual | `raw/usa/usa_00004.dta` | DTA | — | `USA_2024_variablesBID.do` | `USA_2024_BID.dta` | ✅ Done |

> ¹ `COL_2024t3_BID.dta` is saved in `armo/col/` (subdirectory), not in `armo/` root. `hdmf_2.py` reads only from `armo/` root, so this file is **not picked up** by the analysis pipeline unless moved.

---

## Status Summary

| Status | Count | Countries / waves |
|--------|-------|-------------------|
| ✅ Done (output in `armo/`) | 5 | CHL 2024a, COL 2025t3, ECU 2025m12, PER 2024a, USA 2024 |
| ✅ Done (output in subdirectory) | 1 | COL 2024t3 — needs move to `armo/` root |
| ⚠️ In progress / incomplete | 3 | ECU 2024m12 (data zipped), ESP 2025t3 (script errors), MEX 2025t4 (variables script missing) |
| ❌ Not started | 2 | BRA 2025 (no script), COL 2023t3 (no script) |

---

## Auxiliary / Lookup Files

| File | Location | Purpose |
|------|----------|---------|
| `mig_pais_code.dta` | `raw/col/` | Country-of-origin codes (used in COL migration variable) |
| `code_pais.csv` | `raw/col/` | Country codes lookup |
| `ciuo_cod.xlsx` | `raw/col/` | Occupation codes (CIUO) |
| `codigos_formacion.dta` / `.xlsx` | `raw/` | Education/training codes (shared) |
| `dr_EPA_2021.xlsx` | `raw/esp/` | EPA 2021 reference table |

---

## Mexico — Raw Module Files (5 modules → merged into `MEX_2025t4.dta`)

| Module | File | Content |
|--------|------|---------|
| COE1 | `ENOE_COE1T425.dta` | Labor conditions (individual, part 1) |
| COE2 | `ENOE_COE2T425.dta` | Labor conditions (individual, part 2) |
| SDEM | `ENOE_SDEMT425.dta` | Sociodemographic characteristics |
| HOG | `ENOE_HOGT425.dta` | Household data |
| VIV | `ENOE_VIVT425.dta` | Housing data |

Merge script: `do armo/mex/MEX_2025t4_mergeBID.do`

---

## Ecuador — Raw Module Files (3 modules → merged into `ECU_2025m12.dta`)

| Module | File | Content |
|--------|------|---------|
| Persona | `enemdu_persona_2025_12.sav` | Individual / person level |
| Consumidor | `enemdu_consumidor_2025_12.sav` | Consumer expenditure |
| Vivienda-Hogar | `enemdu_vivienda_hogar_2025_12.sav` | Housing and household |

Source directory: `raw/ecu/1_BDD_ENEMDU_2025_12_SPSS/`  
Merge script: `do armo/ecu/ECU_2025m12_mergeBID.do`

---

## Pending Actions

1. **COL 2023t3** — Raw data exists (`COL_2023t3.dta`). Write harmonization script following `COL_2024t3_variablesBID.do` as template.
2. **ECU 2024m12** — Unzip `1_BDD_ENEMDU_2024_SPSS.zip`, run merge step, then run `ECU_2024m12_variablesBID.do`.
3. **MEX 2025t4** — Write `MEX_2025t4_variablesBID.do` (merge is done; no variables script exists).
4. **ESP 2025t3** — Fix copy-paste errors in `ESP_2025t3_variablesBID.do` (script contains COL variable references).
5. **BRA 2025** — SISMIGRA data is a migration registry (not a household survey); decide scope and write script.
6. **COL 2024t3** — Move `armo/col/COL_2024t3_BID.dta` to `armo/` root so `hdmf_2.py` can load it.
