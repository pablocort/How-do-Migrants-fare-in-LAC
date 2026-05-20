# Dictionary Check: COL_GEIH (2018t3 – 2025t3)
Date: 2026-04-08
Reference script: `do armo/col/COL_2023t3_variablesBID.do`
Waves checked: 2018t3, 2019t3, 2020t3, 2021t3, 2022t3, 2023t3, 2024t3, 2025t3
Source: Stata run on raw `.dta` files in `bases armo/raw/col/`

---

## Variable existence matrix

| Variable | Domain | 2018t3 | 2019t3 | 2020t3 | 2021t3 | 2022t3 | 2023t3 | 2024t3 | 2025t3 |
|----------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| `idh` | ID | ✅ str8 | ✅ str8 | ✅ str8 | ✅ str8 | ✅ str8 | ✅ str8 | ✅ str8 | ✅ str8 |
| `orden` | ID | ✅ byte | ✅ byte | ✅ byte | ✅ byte | ✅ byte | ✅ byte | ✅ byte | ✅ byte |
| **`fex_c18`** | **Weight** | **❌** | **❌** | **❌** | **❌** | **✅** | **✅** | **✅** | **✅** |
| `p6050` | Demo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p6040` | Demo | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int |
| `p3016` | Demo (sexo?) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `oci` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `dsi` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`fft`** | **Employment** | **❌** | **❌** | **❌** | **❌** | **✅** | **✅** | **✅** | **✅** |
| `p6800` | Employment | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int | ✅ int |
| `p7045` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p6920` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p6090` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p6460` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p6450` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p6440` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p7450` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `p6240` | Employment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`p3042`** | **Education** | **❌** | **❌** | **❌** | **❌** | **✅** | **✅** | **✅** | **✅** |
| **`p3042s1`** | **Education** | **❌** | **❌** | **❌** | **❌** | **✅** | **✅** | **✅** | **✅** |
| **`p3042s2`** | **Education** | **❌** | **❌** | **❌** | **❌** | **✅ int** | **✅ int** | **✅ int** | **✅ int** |
| **`p3043`** | **Education** | **❌** | **❌** | **❌** | **❌** | **✅** | **✅** | **✅** | **✅** |
| **`p3373`** | **Migration** | **❌** | **❌** | **❌** | **❌** | **✅** | **✅** | **✅** | **✅** |
| **`p3373s3`** | **Migration** | **❌** | **❌** | **❌** | **❌** | **✅ int** | **✅ int** | **✅ str3** | **✅ str3** |
| **`p3382`** | **Migration** | **❌** | **❌** | **❌** | **❌** | **✅** | **✅** | **✅** | **✅** |
| `impa` | Income | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** |
| `impaes` | Income | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** |
| `isa` | Income | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** |
| `isaes` | Income | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** |
| `imdi`–`iees` | Income | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** |
| `iof1`–`iof6es` | Income | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** |
| `p7510s2a1` | Remittances | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Key structural break: 2021t3 → 2022t3

The data reveal a **hard break between 2021t3 and 2022t3**. All of the following variables are absent in 2018–2021 and present from 2022 onward:

| Variable group | Absent 2018–2021 | Present 2022–2025 |
|---|---|---|
| `fex_c18` | no weight variable found | appears with correct scale |
| `fft` (inactive flag) | absent | present |
| `p3042`/`p3042s1`/`p3042s2`/`p3043` | education module absent | present |
| `p3373`/`p3373s3`/`p3382` | migration module absent | present |

**Implication:** The 2023t3 reference script **cannot be cloned for 2018–2021**. These waves lack the education and migration modules entirely. They require a separate, simpler script structure — and will produce `aedu_ci`, `edu_isced`, `edu_hdmf`, `migrante_ci`, `mig_pais_ci`, `migrantiguo5_ci` as all-missing.

> Note on `p3016` (sexo): missing in ALL 8 waves. The sexo variable likely uses a different name in GEIH. Needs to be identified before scripts for any wave are finalized.

---

## Categorical changes detected

### `p3373s3` — country of birth code: TYPE CHANGE in 2024t3

| Wave | Type | Notes |
|------|------|-------|
| 2022t3 | `int` (numeric) | Matches `mig_pais_code.dta` merge on numeric key |
| 2023t3 | `int` (numeric) | Same |
| **2024t3** | **`str3` (string)** | **BREAKING CHANGE** — `destring p3373s3` in the script handles this, but the merge with `mig_pais_code.dta` (keyed on numeric) requires destring first |
| **2025t3** | **`str3` (string)** | **Same** |

The current scripts already include `destring p3373s3, replace` — this handles the type change correctly for 2024t3 and 2025t3. ✅

### `p3373` categories — STABLE across 2022–2025

| Code | Meaning | 2022t3 | 2023t3 | 2024t3 | 2025t3 |
|------|---------|--------|--------|--------|--------|
| 1 | Born in this municipality | 57.4% | 56.7% | 56.5% | 57.0% |
| 2 | Born in another municipality (Colombia) | 37.7% | 38.8% | 39.1% | 38.9% |
| 3 | **Born abroad** | 4.93% | 4.56% | 4.34% | 4.07% |

`migrante_ci = (p3373==3)` is **stable and correct** for 2022–2025. Migrant share declining slightly over time (~5% → ~4%).

### `p3382` categories — STABLE across 2022–2025

| Code | 2022t3 | 2023t3 | 2024t3 | 2025t3 |
|------|--------|--------|--------|--------|
| 1 | 6.1% | 5.8% | 5.4% | 5.1% |
| 2 | 82.9% | 84.2% | 85.2% | 86.3% |
| 3 | 7.5% | 7.7% | 7.7% | 7.4% |
| 4 | 3.5% | 2.4% | 1.7% | 1.2% |

Categories stable. Code values 2 and 3 (`migrantiguo5_ci` recency mapping) work correctly across all 4 waves.

### `p3042` education categories — STABLE across 2022–2025

Categories 1–13 and 99 present in all 4 waves with consistent proportions. No structural change detected.

---

## Expansion factor summary

| Wave | N obs | `fex_c18` sum | Interpretation |
|------|-------|---------------|----------------|
| 2018t3 | 191,041 | NOT FOUND | Need alternative weight variable |
| 2019t3 | 189,650 | NOT FOUND | Need alternative weight variable |
| 2020t3 | 190,268 | NOT FOUND | Need alternative weight variable |
| 2021t3 | 176,532 | NOT FOUND | Need alternative weight variable |
| 2022t3 | 227,970 | 50,559,093 | ≈ monthly Colombian population ✅ |
| 2023t3 | 215,059 | 51,092,907 | ≈ monthly Colombian population ✅ |
| 2024t3 | 207,425 | 51,614,439 | ≈ monthly Colombian population ✅ |
| 2025t3 | 205,276 | 17,375,445 | ❗ **~1/3 of expected** — likely quarterly weight divided by 3, or a different base population |

**`fex_c18` for 2022–2024 sums to ~50–51M**: consistent with Colombia's total population being surveyed monthly. ✅

**2025t3 sum = 17.4M**: This is approximately 50M ÷ 3. Either:
- (a) `fex_c18` in 2025t3 was already divided to represent a monthly sub-sample, OR
- (b) The GEIH 2025 changed its sampling frame

**Action required**: Compare with DANE population estimates for 2025. If Colombia's working-age population (~38–40M) is the denominator, then 17.4M is too low. The multiplier question for 2025t3 needs verification.

---

## Income variables

| Variable group | 2018–2024 | 2025t3 | Note |
|---|---|---|---|
| `impa`, `isa`, `imdi` (labor income) | ✅ all present | ❌ ALL MISSING | 2025t3 income structure completely changed |
| `ie`, `iees` (in-kind) | ✅ | ❌ | Same |
| `iof1`–`iof6es` (non-labor) | ✅ | ❌ | Same |
| `p7510s2a1` (remittances) | ✅ | ✅ | Stable across all waves |

**The 2025t3 raw `.dta` has no income variables** (except remittances). Income must come from a different module or file in 2025. This confirms the income block being commented out was the right decision — but it also means 2025t3 will produce a dataset with no income, which limits the analysis.

---

## Clone safety assessment

| Wave | Safe to clone from 2023t3? | Required changes |
|------|---------------------------|-----------------|
| **2022t3** | ✅ YES — all vars present, same structure | Change `local ANO "2022"`, input/output paths |
| **2023t3** | ✅ Reference script | — |
| **2024t3** | ✅ YES | Change `local ANO`, paths. `p3373s3` already handled by `destring` |
| **2025t3** | ⚠️ PARTIAL | Change `local ANO`, paths. Income block will silently produce missing (already commented out). Verify `fex_c18` multiplier |
| **2021t3** | ❌ NO | `fft`, `p3042`, `p3373`, `p3382` all missing. Needs custom script |
| **2020t3** | ❌ NO | Same as 2021t3 |
| **2019t3** | ❌ NO | Same |
| **2018t3** | ❌ NO | Same |

---

## Recommended approach for 2018–2021

Since the education and migration modules are absent in 2018–2021, two options:

**Option A — Partial harmonization** (recommended if the goal is labor market comparisons only):
Write a single script `COL_2018_2021_variablesBID_template.do` that:
- Produces all employment, income, demographic variables (fully available)
- Sets `aedu_ci`, `edu_isced`, `edu_hdmf`, `migrante_ci`, `mig_pais_ci`, `migrantiguo5_ci` to `.` with comments explaining absence
- Clones for each year (2018, 2019, 2020, 2021)

**Option B — Skip 2018–2021**:
Use only 2022–2025 for the migration and education analyses. Include 2018–2021 only for labor market trends (employment, formality, hours, income).

> Note: `p3016` (sexo variable) is **missing in all 8 waves**. The sex variable must use a different name in GEIH. This must be identified and added to all scripts before running. Likely candidate: check `describe` output for variables containing "sex" or "genero" in labels.

---

## Open issues before script generation

| # | Issue | Waves affected | Status |
|---|-------|---------------|--------|
| 1 | `fex_c18` absent in 2018–2021 | 2018–2021 | ⚠️ Check reference package for `fex_c` or `fex`; see `skills/variable_alternatives.md` |
| 2 | `fft` (inactive flag) absent in 2018–2021 | 2018–2021 | ⚠️ Alternative: reconstruct from `oci`/`dsi`/`p6240`; see `skills/variable_alternatives.md` |
| 3 | Education module (`p3042`) absent in 2018–2021 | 2018–2021 | ⚠️ Check reference package for `p6210`/`p6210s1`; see `skills/variable_alternatives.md` |
| 4 | Migration module (`p3373`) absent in 2018–2021 | 2018–2021 | ✅ Alternative confirmed: `p6074==2 & p756==3` (from SCL/MIG reference); see `skills/variable_alternatives.md` |
| 5 | `sexo_ci` missing from scripts | 2018–2025 | ✅ Fixed: `p6020` confirmed correct for all GEIH waves; added to all COL scripts |
| 6 | `fex_c18` sum in 2025t3 = 17.4M (vs. 50M in 2022–2024) | 2025t3 | ⚠️ Deferred — easy to verify and correct at population estimation stage |
| 7 | Income variables entirely absent in 2025t3 | 2025t3 | ✅ Confirmed — income block intentionally omitted; 2025t3 will not have income vars |
| 8 | `p3373s3` type `str3` in 2024–2025 vs `int` in 2022–2023 | 2024t3, 2025t3 | ✅ Handled — scripts already include `destring p3373s3, replace` |
