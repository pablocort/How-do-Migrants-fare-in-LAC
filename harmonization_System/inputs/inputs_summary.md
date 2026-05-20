# HDMF — Input Databases Summary

Pipeline goal: harmonize raw household/labor surveys into `*_BID.dta` files stored in `bases armo/armo/[ISO3]/` (one subfolder per country), then processed by `hdmf_2.py` to produce indicator tables and figures.

---

## Main Input Databases (2023–2025)

| # | Country | Code | Survey | Year | Period | Raw file(s) | Format | Merge step | Harmonization script | Output (`armo/`) | Status |
|---|---------|------|--------|------|--------|-------------|--------|------------|---------------------|------------------|--------|
| 1 | Brazil | BRA | SISMIGRA | 2025 | Jan–Dec | `raw/bra/sismigra_janeiro_dezembro_2025.xlsx` | XLSX | — | *(none)* | *(none)* | ❌ Not started |
| 2 | Chile | CHL | CASEN | 2024 | Annual | `raw/chl/casen_2024.dta` | DTA | — | `chl/CHL_2024_variablesBID.do` | `CHL/CHL_2024a_BID.dta` | ✅ Done |
| 3a | Colombia | COL | GEIH | 2018 | Q3 | `raw/col/COL_2018t3.dta` | DTA | — | `COL_2018t3_variablesBID.do` | `COL/COL_2018t3_BID.dta` | ✅ Done (alt constructions) |
| 3b | Colombia | COL | GEIH | 2019 | Q3 | `raw/col/COL_2019t3.dta` | DTA | — | `COL_2019t3_variablesBID.do` | `COL/COL_2019t3_BID.dta` | ✅ Done (alt constructions) |
| 3c | Colombia | COL | GEIH | 2020 | Q3 | `raw/col/COL_2020t3.dta` | DTA | — | `COL_2020t3_variablesBID.do` | `COL/COL_2020t3_BID.dta` | ✅ Done (alt constructions) |
| 3d | Colombia | COL | GEIH | 2021 | Q3 | `raw/col/COL_2021t3.dta` | DTA | — | `COL_2021t3_variablesBID.do` | `COL/COL_2021t3_BID.dta` | ✅ Done (alt constructions) |
| 3e | Colombia | COL | GEIH | 2022 | Q3 | `raw/col/COL_2022t3.dta` | DTA | — | `COL_2022t3_variablesBID.do` | `COL/COL_2022t3_BID.dta` | ✅ Done |
| 3f | Colombia | COL | GEIH | 2023 | Q3 | `raw/col/COL_2023t3.dta` | DTA | — | `COL_2023t3_variablesBID.do` | `COL/COL_2023t3_BID.dta` | ✅ Done |
| 3g | Colombia | COL | GEIH | 2024 | Q3 | `raw/col/COL_2024t3.dta` | DTA | — | `COL_2024t3_variablesBID_local.do` | `COL/COL_2024t3_BID.dta` | ✅ Done |
| 3h | Colombia | COL | GEIH | 2025 | Q3 | `raw/col/COL_2025t3.dta` | DTA | — | `not_clean/COL_2025t3_variablesBID.do` | `COL/COL_2025t3_BID.dta` | ✅ Done (no income vars in raw) |
| 4a | Ecuador | ECU | ENEMDU | 2018 | Dec (m12) | `raw/ecu/ECU_2018m12.dta` | DTA | — | `ecu/ECU_2018m12_variablesBID.do` | `ECU/ECU_2018m12_BID.dta` | ⏳ Script ready — pending run |
| 4b | Ecuador | ECU | ENEMDU | 2019 | Dec (m12) | `raw/ecu/ECU_2019m12.dta` | DTA | — | `ecu/ECU_2019m12_variablesBID.do` | `ECU/ECU_2019m12_BID.dta` | ⏳ Script ready — pending run |
| 4c | Ecuador | ECU | ENEMDU | 2020 | Dec (m12) | `raw/ecu/ECU_2020m12.dta` | DTA | — | `ecu/ECU_2020m12_variablesBID.do` | `ECU/ECU_2020m12_BID.dta` | ⏳ Script ready — pending run |
| 4d | Ecuador | ECU | ENEMDU | 2021 | Dec (m12) | `raw/ecu/ECU_2021m12.dta` | DTA | — | `ecu/ECU_2021m12_variablesBID.do` | `ECU/ECU_2021m12_BID.dta` | ⏳ Script ready — pending run |
| 4e | Ecuador | ECU | ENEMDU | 2022 | Dec (m12) | `raw/ecu/ECU_2022m12.dta` | DTA | — | `ecu/ECU_2022m12_variablesBID.do` | `ECU/ECU_2022m12_BID.dta` | ⏳ Script ready — pending run |
| 4f | Ecuador | ECU | ENEMDU | 2023 | Dec (m12) | `raw/ecu/ECU_2023m12.dta` | DTA | — | `ecu/ECU_2023m12_variablesBID.do` | `ECU/ECU_2023m12_BID.dta` | ⏳ Script ready — pending run |
| 4g | Ecuador | ECU | ENEMDU | 2024 | Dec (m12) | `raw/ecu/ECU_2024m12.dta` | DTA | — | `ecu/ECU_2024m12_variablesBID.do` | `ECU/ECU_2024m12_BID.dta` | ⏳ Script ready — pending run |
| 4h | Ecuador | ECU | ENEMDU | 2025 | Dec (m12) | `raw/ecu/ECU_2025m12.dta` (merged from SAV modules) | DTA | `ECU_2025m12_mergeBID.do` | `ECU_2025m12_variablesBID.do` | `ECU/ECU_2025m12_BID.dta` | ✅ Done |
| 5a | Spain | ESP | EPA | 2018 | Annual (Q1–Q4) | `raw/esp/ESP_2018a_merged.dta` (merged from 4 quarterly txt files by `build_epa_annual.py`) | DTA | `build_epa_annual.py` (Python) | `esp/ESP_2018a_variablesBID.do` | `ESP/ESP_2018a_BID.dta` | ✅ Done (2026-04-29) |
| 5b | Spain | ESP | EPA | 2019 | Annual (Q1–Q4) | `raw/esp/ESP_2019a_merged.dta` | DTA | `build_epa_annual.py` | `esp/ESP_2019a_variablesBID.do` | `ESP/ESP_2019a_BID.dta` | ✅ Done (2026-04-29) |
| 5c | Spain | ESP | EPA | 2020 | Annual (Q1–Q4) | `raw/esp/ESP_2020a_merged.dta` | DTA | `build_epa_annual.py` | `esp/ESP_2020a_variablesBID.do` | `ESP/ESP_2020a_BID.dta` | ✅ Done (2026-04-29) |
| 5d | Spain | ESP | EPA | 2021 | Annual (Q1–Q4) | `raw/esp/ESP_2021a_merged.dta` | DTA | `build_epa_annual.py` | `esp/ESP_2021a_variablesBID.do` | `ESP/ESP_2021a_BID.dta` | ✅ Done (2026-04-29) |
| 5e | Spain | ESP | EPA | 2022 | Annual (Q1–Q4) | `raw/esp/ESP_2022a_merged.dta` | DTA | `build_epa_annual.py` | `esp/ESP_2022a_variablesBID.do` | `ESP/ESP_2022a_BID.dta` | ✅ Done (2026-04-29) |
| 5f | Spain | ESP | EPA | 2023 | Annual (Q1–Q4) | `raw/esp/ESP_2023a_merged.dta` | DTA | `build_epa_annual.py` | `esp/ESP_2023a_variablesBID.do` | `ESP/ESP_2023a_BID.dta` | ✅ Done (2026-04-29) |
| 5g | Spain | ESP | EPA | 2024 | Annual (Q1–Q4) | `raw/esp/ESP_2024a_merged.dta` | DTA | `build_epa_annual.py` | `esp/ESP_2024a_variablesBID.do` | `ESP/ESP_2024a_BID.dta` | ✅ Done (2026-04-29) |
| 5h | Spain | ESP | EPA | 2025 | Annual (Q1–Q4) | `raw/esp/ESP_2025a_merged.dta` | DTA | `build_epa_annual.py` | `esp/ESP_2025a_variablesBID.do` | `ESP/ESP_2025a_BID.dta` | ✅ Done (2026-04-29; reference script) |
| 9 | Mexico | MEX | ENOE | 2025 | Q4 | `raw/mex/MEX_2025t4.dta` (merged from 5 modules) | DTA | `MEX_2025t4_mergeBID.do` | *(none — missing)* | *(none)* | ⚠️ Merge done, variables script missing |
| 10a | Peru | PER | ENAHO | 2018 | Annual | `raw/per/PER_2018a.dta` | DTA | — | `PER_2018a_variablesBID.do` | `PER/PER_2018a_BID.dta` | ⏳ In progress (script pending) |
| 10b | Peru | PER | ENAHO | 2019 | Annual | `raw/per/PER_2019a.dta` | DTA | — | `PER_2019a_variablesBID.do` | `PER/PER_2019a_BID.dta` | ⏳ In progress (script pending) |
| 10c | Peru | PER | ENAHO | 2020 | Annual | `raw/per/PER_2020a.dta` | DTA | — | `PER_2020a_variablesBID.do` | `PER/PER_2020a_BID.dta` | ⏳ In progress (script pending) |
| 10d | Peru | PER | ENAHO | 2021 | Annual | `raw/per/PER_2021a.dta` | DTA | — | `PER_2021a_variablesBID.do` | `PER/PER_2021a_BID.dta` | ⏳ In progress (script pending) |
| 10e | Peru | PER | ENAHO | 2022 | Annual | `raw/per/PER_2022a.dta` | DTA | — | `PER_2022a_variablesBID.do` | `PER/PER_2022a_BID.dta` | ⏳ In progress (script pending) |
| 10f | Peru | PER | ENAHO | 2023 | Annual | `raw/per/PER_2023a.dta` | DTA | — | `PER_2023a_variablesBID.do` | `PER/PER_2023a_BID.dta` | ⏳ In progress (script pending) |
| 10g | Peru | PER | ENAHO | 2024 | Annual | `raw/per/PER_2024a.dta` | DTA | — | `PER_2024_variablesBID.do` | `PER/PER_2024a_BID.dta` | ✅ Done |
| 11 | United States | USA | IPUMS Census | 2024 | Annual | `raw/usa/usa_00004.dta` | DTA | — | `USA_2024_variablesBID.do` | `USA/USA_2024_BID.dta` | ✅ Done |
| 12 | Belize | BLZ | LFS | 2024 | Sep (m9) | `raw/blz/BLZ_2024m9.dta` | DTA | — | `blz/BLZ_2024m9_variablesBID.do` | `BLZ/BLZ_2024m9_BID.dta` | ✅ Done (2026-05-13) — single wave; migrant sample very small (round-number pcts), interpret with caution |
| 13 | Barbados | BRB | LFS | 2023 | Annual | `raw/brb/BRB_2023a.dta` | DTA | — | `brb/BRB_2023a_variablesBID.do` | `BRB/BRB_2023a_BID.dta` | ✅ Done (2026-05-13) — single wave; `migrante_ci` from nationality (`CNTRY_CD`), not birthplace; `formal_ci` not available (LFS) |
| 14 | Dominican Republic | DOM | ENFT | 2018–2024 | Q4 | `armo/DOM/DOM_*_BID.dta` | DTA | — | `dom/DOM_*_variablesBID.do` | `DOM/DOM_*_BID.dta` | ✅ Done — 7 waves (2018t4–2024t4) |
| 15 | Suriname | SUR | ABS | 2022 | Annual | `raw/sur/SUR_2022a.dta` *(user to place)* | DTA | — | `sur/SUR_2022a_variablesBID.do` | `SUR/SUR_2022a_BID.dta` | ⏳ Script written (2026-05-13) — waiting for raw DTA file |

> ¹ `COL_2024t3_BID.dta` should be in `armo/COL/` per the new structure. Re-run the script to regenerate it in the correct location.

---

## Status Summary

| Status | Count | Countries / waves |
|--------|-------|-------------------|
| ✅ Done (output in `armo/[ISO3]/`) | 17+ | CHL 2024a, COL 2025t3, ECU 2025m12, PER 2024a, USA 2024, ESP 2018a–2025a, BLZ 2024m9, BRB 2023a, DOM 2018t4–2024t4 |
| ⚠️ Script exists, needs re-run | 1 | COL 2024t3 — re-run to save to `armo/COL/` |
| ⚠️ In progress / incomplete | 3 | ECU 2024m12 (data zipped), MEX 2025t4 (variables script missing), SUR 2022a (script ready, waiting for raw DTA) |
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

## Reference Do-File Package (alternative constructions)

Each country's `raw/[ISO3]/alternative_do_files/` folder contains historical harmonization scripts from IDB/SCL/MECOVI. These are the **primary source** when a standard variable is missing in a given wave.

| Country | Location | Waves available |
|---------|----------|----------------|
| COL | `raw/col/alternative_do_files/` | 2018t3–2024t3 (7 files) |
| ECU | `raw/ecu/alternative_do_files/` | 2018m12–2024m12 (7 files) |
| BLZ | `raw/blz/alternative_do_files/` | 2024m9 (1 file) |
| BRB | `raw/brb/alternative_do_files/` | 2023a (1 file) |
| SUR | `raw/sur/alternative_do_files/` | 2022a (1 file) |

**Workflow**: Run `dictionary_check.py` first — it greps these files automatically. Or use the Grep tool with the variable name to search manually.

## Pre-harmonization tool

```bash
python harmonization_System/inputs/dictionary_check.py --country COL --waves 2018t3 2019t3 ...
```

Produces `[ISO3]_dictionary_check_[FIRST]_[LAST].md`. Save output to `bases armo/armo/[ISO3]/intermediate_harmo_output/` — see below.

---

## Intermediate Harmonization Output — Folder Structure

Country-specific intermediate outputs (dictionary checks, metadata, mapping checker reports, validation reports) are stored **alongside the harmonized data**, not in `harmonization_System/inputs/`.

```
bases armo/armo/[ISO3]/
├── [ISO3]_[WAVE]_BID.dta            ← harmonized output
└── intermediate_harmo_output/
    ├── INDEX.md                      ← navigation guide (what's in each wave subfolder)
    ├── [ISO3]_dictionary_check_*.md  ← multi-wave comparison (top level)
    └── [WAVE]/                       ← e.g., 2019t3/
        ├── [ISO3]_[WAVE]_metadata.md
        ├── [ISO3]_[WAVE]_mapping_checker.md
        └── [ISO3]_[WAVE]_validation.md
```

| Country | Index file | Waves covered |
|---------|-----------|---------------|
| COL | [`bases armo/armo/col/intermediate_harmo_output/INDEX.md`](../../bases%20armo/armo/col/intermediate_harmo_output/INDEX.md) | 2018t3–2025t3 |

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

1. **COL 2023t3** — Script exists (`COL_2023t3_variablesBID.do`). Run it to produce `armo/COL/COL_2023t3_BID.dta`.
2. **COL 2024t3** — Re-run `COL_2024t3_variablesBID_local.do` to regenerate output in `armo/COL/COL_2024t3_BID.dta`.
3. **ECU 2018m12–2024m12** — All 7 scripts generated (2026-04-14). Run each to produce `armo/ECU/ECU_[YEAR]m12_BID.dta`. See dictionary check: `inputs/ECU_dictionary_check_2018_2024.md`. Key structural notes: 2018 has no `region_c` (ciudad absent); 2019–2023 use legacy ID vars; 2024 uses new string IDs (same as 2025).
4. **MEX 2025t4** — Write `MEX_2025t4_variablesBID.do` (merge is done; no variables script exists).
5. **ESP 2018a–2025a** — ✅ DONE (2026-04-29). All 8 `ESP_[YEAR]a_variablesBID.do` scripts written and run. Output `ESP/ESP_[YEAR]a_BID.dta` (95–133 MB). Reference script: `esp/ESP_2025a_variablesBID.do`. Dictionary check saved: `armo/ESP/intermediate_harmo_output/ESP_dictionary_check_2018_2024.md`. Known issue in `build_epa_annual.py`: BUSCA pre-2021 may be at wrong byte position (142 vs 150) — unemployment rates for 2018–2020 should be validated.
6. **BRA 2025** — SISMIGRA data is a migration registry (not a household survey); decide scope and write script.
7. **SUR 2022a** — Script written: `do armo/sur/SUR_2022a_variablesBID.do`. Place `raw/sur/SUR_2022a.dta` then run script → rebuild cache → rerun `build_jeremy_caribbean.py` to add SUR column.

---

## Jeremy's Caribbean Branch — Output Summary (2026-05-13)

| File | Location | Status |
|------|----------|--------|
| `jeremy_caribbean.xlsx` | `out/jeremy/2026-05-13/` | ✅ Generated — BLZ, BRB, DOM; 6 sheets |
| `trend_dom_participation.png` | `out/jeremy/2026-05-13/` | ✅ Generated |
| `trend_dom_unemployment.png` | `out/jeremy/2026-05-13/` | ✅ Generated |
| `trend_dom_inactivity.png` | `out/jeremy/2026-05-13/` | ✅ Generated |
| `trend_dom_formality.png` | `out/jeremy/2026-05-13/` | ✅ Generated |
| `trend_dom_higher_edu.png` | `out/jeremy/2026-05-13/` | ✅ Generated |

**Notes:**
- BLZ migrant sample is very small → education and inactivity figures show round-number percentages; treat as indicative only
- BRB `migrante_ci` derived from nationality (`CNTRY_CD`), not birthplace — proxy measure
- BRB `formal_ci` not available from LFS → informality column shows NaN
- SUR pending raw data — add once user places `SUR_2022a.dta`
