# HND Remittances Spillover Analysis — Plan

## Context

Honduras has 7 waves of EPHPM data (2018–2025) already harmonized into `*_BID.dta` files. The goal is to test whether remittance inflows have **local spending spillover effects**: do households in the same geographic area that do *not* receive remittances see higher income when remittance intensity in the area is higher? This is the local multiplier mechanism: receiving households spend more → local wages and business income rise → non-receiving households benefit.

The analysis builds directly on the harmonized HND dataset once the parallel session finishes adding `remesas_ci`/`ynlm_ci` to the 2024 and 2025 waves (bugs #4 and #5 in `HND_remittances_income_assessment_2026.md`).

---

## Data situation

| Wave | Remittances | Geography | Usable for spillover |
|------|------------|-----------|----------------------|
| 2018m6 | ✅ | dept + municipality | ✅ (most granular) |
| 2019m6 | ✅ | dept only | ✅ |
| 2021m6 | ⚠️ partial (no USD) | dominio (5 urban/rural bins) | Limited |
| 2022m6 | ❌ absent | dominio | ❌ skip |
| 2023m6 | ✅ | ❌ no current dept | Limited (dominio only) |
| 2024m6 | ⚠️ bug (fix in other session) | dept (`DEPMUESTRA`) | ✅ after fix |
| 2025m7 | ⚠️ bug (fix in other session) | dept (`DEPTO`) | ✅ after fix |

**Primary analytical panel:** 2018–2019 (dept level) and 2024–2025 (dept level), 18 departments each.  
**Secondary:** dominio-level analysis using 2021 and 2023 to fill gaps.

---

## Recommendations on design

### 1. Unit of analysis — geographic clusters

Use **department** (18 units) as the cluster. This is the finest geography available across multiple waves. Each department becomes the "local labor market" where spillovers propagate.

For 2018 only, a robustness check at **municipality** level is possible (318 municipalities), giving much better statistical power for the cross-section.

**Do not** use individual households as the unit for the spillover regression — the key variation is *area-level remittance intensity*, not household-level status.

### 2. Outcome variable for non-receiving households

Use **`ylm_ci` (monthly labor income)** as the primary outcome for non-receivers, not `ytot_ci`. Reasoning:
- Spillover through labor markets is the theoretically cleanest channel
- `ytot_ci` double-counts remittances in the current pipeline (`oih12` is in both `ynlm_ci` and `remesas_ci`)
- Labor income is uncontaminated by transfers

Secondary outcome: `ynlm_ci` excluding the OIH12 component — captures spillover through local business profits.

### 3. Remittance intensity measure (treatment)

Compute two area-level variables per wave from **all households** in the department:

```
pct_remit_dept  = weighted share of HHs where remesas_ch > 0
avg_remit_dept  = weighted mean of remesas_ch (includes zeros for non-receivers)
```

`pct_remit_dept` is preferable for the main spec — it measures the "dose" of remittance-receiving neighbors a non-receiver is exposed to.

### 4. Analytical steps (in order)

#### Step A — Area-level panel dataset

For each wave × department:
1. Flag receiving HHs: `remit_hh = (remesas_ch > 0 & remesas_ch != .)`
2. Compute `pct_remit_dept` and `avg_remit_dept` (survey-weighted, by dept)
3. For non-receivers only: compute `mean_ylm_nonrecv` and `median_ylm_nonrecv` (survey-weighted)
4. Stack all waves → panel with columns: `wave`, `depto`, `pct_remit_dept`, `avg_remit_dept`, `mean_ylm_nonrecv`, `n_nonrecv`

#### Step B — Descriptive / correlational analysis

- **Scatter plots** (one per wave or pooled): x = `pct_remit_dept`, y = `mean_ylm_nonrecv` (dot size = sample weight or HH count per dept). This directly answers the original question.
- **Correlation table** across waves: Pearson and Spearman ρ between remittance intensity and non-receiver income.
- **Bar chart**: rank departments by `pct_remit_dept`, overlay `mean_ylm_nonrecv` — shows if high-remittance depts have higher non-receiver incomes.

#### Step C — Panel first-differences regression

For the 2018→2019 pair and 2024→2025 pair:

```
Δmean_ylm_nonrecv_dept = α + β·Δpct_remit_dept + ε
```

- `Δ` = change between consecutive waves in same department
- This differences out all time-invariant dept characteristics (soil quality, distance to capital, etc.)
- β > 0 → evidence for positive spillover
- Report β with robust SE (only 18 obs per pair, so also report bootstrap CI)

#### Step D — IV robustness (optional but strong)

The exchange rate (USD/HNL) is an **exogenous shifter** of the HNL value of remittances. Between waves, the Lempira depreciated (23.68 → 24.08 → 24.50 → 24.73 → 25.13 → 26.00). Departments with a higher pre-existing share of remittance-receiving HHs will see a larger HNL income gain from depreciation, independently of local conditions. This gives a Bartik-style instrument:

```
Z_dept_t = pct_remit_dept_(t-1) × Δ(USD/HNL)_t
```

This requires at least two periods, which we have (2018-2019, 2024-2025).

#### Step E — Heterogeneity

Split non-receiving HHs by:
- Urban vs. rural (`dominio`)
- Employment sector (formal vs. informal via `formal_ci`)
- Gender of household head (`sexo_ci`)

Hypothesis: informal workers in urban areas close to high-remittance zones benefit most (more exposed to local consumption demand).

---

## Double-counting fix (prerequisite)

Before running the analysis, resolve the `ytot_ci` double-counting issue in the HND scripts. The cleanest fix is to **not include `oih12` in `ynlm_ci`** when `remesas_ci` is computed separately. This needs to be done consistently across all 7 waves. Flag this in the Stata scripts with a comment block.

For the spillover analysis specifically, side-step the issue by using `ylm_ci` as the outcome (unaffected by double-counting).

---

## Python implementation location

Script: `bases armo/armo/hdmf_spillover_hnd.py` ← **already created**

Dependencies: `pyreadstat`, `pandas`, `numpy`, `matplotlib`, `scipy`

Structure:
```
hdmf_spillover_hnd.py
  ├── load_waves()          — load all HND BID.dta files
  ├── build_area_panel()    — dept-level remittance intensity + non-receiver income
  ├── run_correlations()    — Step B
  ├── run_fd_regression()   — Step C
  ├── run_iv_regression()   — Step D (optional)
  └── plot_all()            — export figures to out/remittances/figures/
```

---

## Repository setup

- **Branch:** `remittances-spillover` ← **already created**
- **Output folder:** `out/remittances/{figures,tables}/` ← **already created**
- **Tests:** `bases armo/armo/tests/test_spillover_hnd.py` ← **already created, 20/20 passing**

---

## Pre-conditions before running

1. Other session must finish fixing 2024m6 and 2025m7 do-files (bugs #4 and #5)
2. Run all 7 HND Stata scripts to regenerate BID.dta files
3. Verify `remesas_ci`, `remesas_ch`, `ylm_ci` are non-missing in 2024 and 2025 BID files

---

## Tests

Test suite: `bases armo/armo/tests/test_spillover_hnd.py` (pytest, 20 tests)

Synthetic fixtures in `conftest.py` — run without any real DTA files:

| Test | What it checks |
|------|---------------|
| `test_remit_flag` | `remit_hh` flag logic for positive / zero / missing `remesas_ch` |
| `test_area_panel_shape` | `build_area_panel()` returns 1 row per dept × wave |
| `test_no_contamination` | Non-receiver income excludes receiving HH rows |
| `test_weighted_mean` | Weighted mean matches manual numpy calculation |
| `test_fd_sign` | On synthetic data with built-in spillover, β > 0 |
| `test_fd_n_obs` | FD regression has exactly 18 obs per wave pair |
| `test_missing_wave_skipped` | Wave without `remesas_ch` skipped without crash |
| `test_income_variable_no_double_count` | `ylm_ci` used as outcome, not `ytot_ci` |
| `test_output_files_created` | PNG and CSV files exist after `plot_all()` |
| `test_real_data_dept_count` | Real 2023 BID.dta → ≤ 18 depts, N > 0 |

```
py -m pytest "bases armo/armo/tests/test_spillover_hnd.py" -v
```

---

## Verification

1. Area panel: 18 rows per wave, no missing `pct_remit`
2. Scatter plots: positive gradient (high-remittance depts → higher non-receiver wages)
3. FD regression: β > 0 with plausible magnitude; bootstrap CI reported
4. Cross-validate: `avg_remit_dept` × `pct_remit_dept` should correlate with aggregate HH consumption proxies if available
