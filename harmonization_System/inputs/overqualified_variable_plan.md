# Plan: Add `overqualified_ci` to All HDMF Harmonized Waves

## Context

The HDMF project aims to compare migrant vs. native-born labor market outcomes in LAC. A key dimension not yet captured is **overqualification** (aka skill mismatch): workers whose educational attainment exceeds what their occupation requires. This is particularly relevant for migrants, who often face downgrading into low-skill jobs despite high education. The task is to (1) diagnose feasibility per country-wave, and (2) implement the variable across all "Done" waves.

---

## Feasibility Diagnostic

### Definition chosen: Normative approach
- `overqualified_ci = 1` if employed (`emp_ci == 1`) AND tertiary education (`edu_hdmf >= 6`: Technical, University complete, or Postgraduate) AND in a low-skill occupation (`ocupa_ci >= 4`: Clerical support, Service/sales, Agriculture, Craft, Plant/machine operators, Elementary)
- `overqualified_ci = 0` if employed AND (`edu_hdmf < 6` OR `ocupa_ci <= 3`)
- `overqualified_ci = .` if not employed OR `edu_hdmf` or `ocupa_ci` missing

This uses ISCO-08 major groups 1–3 as "matched/high-skill" and 4–9 as "low-skill". The threshold `ocupa_ci >= 4` is the standard in ILO and LAC migration literature.

### `ocupa_ci` in the codebook (already a standard HDMF variable)
The codebook defines `ocupa_ci` as CIUO-08/ISCO-08 major groups (1–9). It IS listed in the standard variable set but its implementation is **inconsistent** across countries:

| Country | Wave | `ocupa_ci` in .do? | Source in raw | Action needed |
|---------|------|-------------------|---------------|---------------|
| **COL** | 2024t3, 2025t3 | ✅ Yes — built from `oficio_c8` (CIUO-08 2-digit) | `oficio_c8` | None — already harmonized |
| **CHL** | 2024a | ❌ Not in .do | CASEN has `oficio` (CIUO-08) | Add `ocupa_ci` block |
| **ECU** | 2025m12 | ❌ Commented out — `p41` present in raw | `p41` (CIUO-08) noted in comments | Uncomment + harmonize |
| **PER** | 2024a | ❌ Not in .do | ENAHO `p507` (CIUO-88, not 08) | Add `ocupa_ci` block; note CIUO-88 vs 08 caveat |
| **USA** | 2024a | ❌ Not in .do | IPUMS `occ` (SOC 2010) | Map OCC → ISCO-08 major groups |
| **MEX** | 2025t4 | ❌ Not in .do (variables script missing) | ENOE `p4a` (SINCO, maps to ISCO-08) | Defer to when MEX script is created |
| **ESP** | 2025t3 | ❌ Not in .do | EPA `cno11` (CNO-2011 → ISCO-08) | Add `ocupa_ci` block + `overqualified_ci` |

### Cross-time comparability
- **Within country**: CIUO-08 adopted by COL (~2015), ECU (~2012), CHL (~2015), PER used CIUO-88 (pre-2016) — **Peru's classification is not ISCO-08**; older waves will have a structural break. Flag this in the variable label.
- **Across countries**: All LAC countries eventually adopted CIUO-08 (same as ISCO-08), so the `ocupa_ci >= 4` threshold is internationally comparable.
- **Spain**: CNO-2011 maps cleanly to ISCO-08 at 1-digit level.
- **USA**: SOC → ISCO-08 crosswalk is available (ILO crosswalk). At 1-digit level the mapping is reliable.
- **Conclusion**: Comparable across COL, CHL, ECU, ESP (all CIUO-08/ISCO-08). USA is comparable at 1-digit. PER is partially comparable (CIUO-88 major groups mostly align at 1-digit but with caveats for groups 6-8).

---

## Implementation Plan

### Step 0 — Update `variable_codebook.md`
Add formal definition of `overqualified_ci`:
- Domain: Job characteristics (after `ocupa_ci`)
- Type: binary, employed only
- Values: 1=overqualified, 0=not overqualified, .=not employed or missing
- Definition string for Stata label: `"Overqualified (tertiary educ + low-skill occ, ISCO-08 4-9)"`

**File:** `harmonization_System/inputs/variable_codebook.md`

### Step 1 — Colombia (COL 2024t3 and 2025t3) — READY
`ocupa_ci` already built. Just append `overqualified_ci` block after `ocupa_ci` in each .do file.

**Files to edit:**
- `do armo/col/COL_2024t3_variablesBID_local.do`
- `do armo/col/COL_2025t3_variablesBID [Recovered] march3.do`

**Stata block to add (after `ocupa_ci` section):**
```stata
***********
* overqualified_ci
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified"
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (tertiary educ + low-skill occ, ISCO-08 4-9)"
```

### Step 2 — Chile (CHL 2024a) — ADD `ocupa_ci` FIRST
CASEN 2024 has variable `oficio` (CIUO-08 4-digit). Need to add `ocupa_ci` mapping then `overqualified_ci`.

**File to edit:** `do armo/chl/CHL_2024_variablesBID.do`

Add `ocupa_ci` block (using `substr(oficio, 1, 2)` → destring → map to 1-digit ISCO groups), then add `overqualified_ci` block.

### Step 3 — Ecuador (ECU 2025m12) — UNCOMMENT `p41`
The .do file has commented-out code for `p41` (CIUO-08 occupation code). Uncomment, build `ocupa_ci`, then add `overqualified_ci`.

**File to edit:** `do armo/ecu/ECU_2025m12_variablesBID.do`

Note: Also update `ECU_2024m12_variablesBID.do` if/when that wave is completed.

### Step 4 — Peru (PER 2024a) — ADD with CIUO-88 caveat
ENAHO 2024 uses `p507` (CIUO-88). Major groups 1–9 exist but group boundaries differ from ISCO-08 (especially groups 6–8). Add `ocupa_ci` from CIUO-88 1-digit, add `overqualified_ci`, and document the caveat inline.

**File to edit:** `do armo/per/PER_2024_variablesBID.do`

Inline comment: `/* NOTE: PER uses CIUO-88 (not 08); groups 1-5 and 9 are comparable; groups 6-8 differ slightly */`

### Step 5 — USA (2024a) — MAP SOC → ISCO-08
IPUMS `occ` (SOC 2010 codes). Use ILO's SOC→ISCO-08 crosswalk at 1-digit to assign `ocupa_ci`, then add `overqualified_ci`.

**File to edit:** `do armo/usa/USA_2024_variablesBID.do`

Strategy: Use `occ` first digit (SOC major group) → recode to ISCO-08 1-digit using standard crosswalk table (embed as `recode` in Stata).

### Step 6 — Spain (ESP 2025t3) — MAP CNO-2011 → ISCO-08
EPA uses `cno11` (CNO-2011, Spanish national classification). CNO-2011 is designed to align 1-to-1 with ISCO-08 at 1-digit. Add `ocupa_ci` and `overqualified_ci`.

**File to edit:** `do armo/esp/ESP_2025t3_variablesBID.do`

### Step 7 — Update `hdmf_2.py`
Add computation of `overqualified_ci` indicators (weighted means by `migrante_ci`, `sexo_ci`, country) to the analysis pipeline.

**File to edit:** `bases armo/armo/hdmf_2.py`

Add a new indicator block computing:
- Share overqualified among employed with tertiary education, by migrant status
- Share overqualified among all employed, by migrant status

Use existing `make_weighted_stats_multi()` function from `functions.py`.

### Step 8 — Update `variable_codebook.md` and `inputs_summary.md`
- Add `overqualified_ci` to the standard variable list
- Document the CIUO-88 (PER) vs CIUO-08 caveat
- Update `inputs_summary.md` with implementation status per country

---

## Execution order (parallel where possible)

1. **Parallel**: Edit COL 2024t3, COL 2025t3, CHL 2024a, ECU 2025m12 .do files
2. **Parallel**: Edit PER 2024a, USA 2024a, ESP 2025t3 .do files + update codebook
3. **Sequential**: Re-run all 7 .do files (each country independent → parallel)
4. **Sequential after all re-runs**: Update and run `hdmf_2.py`

---

## Verification

1. After each .do re-run: `tabulate overqualified_ci migrante_ci [aw=factor_ci] if emp_ci==1, col` — confirm plausible rates (~10–40%) and no all-missing columns
2. Check `overqualified_ci` is `.` for all non-employed: `assert missing(overqualified_ci) if emp_ci != 1`
3. In `hdmf_2.py` output: confirm overqualification rate is higher for migrants than natives in at least some countries (expected finding in literature)
4. Cross-country comparison table: COL, CHL, ECU, ESP should be directly comparable; PER and USA noted as "partially comparable"

---

## Files to modify (summary)

| File | Change |
|------|--------|
| `harmonization_System/inputs/variable_codebook.md` | Add `overqualified_ci` definition |
| `do armo/col/COL_2024t3_variablesBID_local.do` | Add `overqualified_ci` block |
| `do armo/col/COL_2025t3_variablesBID [Recovered] march3.do` | Add `overqualified_ci` block |
| `do armo/chl/CHL_2024_variablesBID.do` | Add `ocupa_ci` + `overqualified_ci` blocks |
| `do armo/ecu/ECU_2025m12_variablesBID.do` | Uncomment `p41`, add `ocupa_ci` + `overqualified_ci` |
| `do armo/per/PER_2024_variablesBID.do` | Add `ocupa_ci` (CIUO-88) + `overqualified_ci` with caveat |
| `do armo/usa/USA_2024_variablesBID.do` | Add `ocupa_ci` (SOC→ISCO-08) + `overqualified_ci` |
| `do armo/esp/ESP_2025t3_variablesBID.do` | Add `ocupa_ci` (CNO-2011→ISCO-08) + `overqualified_ci` |
| `bases armo/armo/hdmf_2.py` | Add overqualification indicator computation |
| `harmonization_System/inputs/inputs_summary.md` | Update status |