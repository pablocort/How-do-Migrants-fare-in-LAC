# Run Instructions — COL 2023t3 and COL 2024t3

**Status before running:** Dictionary check (`COL_dictionary_check_2023_2024.md`) must be completed first. Do not run until all key variables are verified and any differences are resolved in the scripts.

---

## Pre-run checklist

- [ ] `bases armo/raw/col/COL_2023t3.dta` exists
- [ ] `bases armo/raw/col/COL_2024t3.dta` exists
- [ ] `bases armo/raw/col/mig_pais_code.dta` exists
- [ ] Dictionary check completed and signed off
- [ ] No stale output files blocking the save (or `replace` will overwrite)

---

## Step 1 — Run COL 2024t3 first (closer to reference)

Open Stata and run:

```stata
do "do armo/col/COL_2024t3_variablesBID_local.do"
```

**Expected output:** `bases armo/armo/COL_2024t3_BID.dta`

**Verify immediately after:**
```stata
use "bases armo/armo/COL_2024t3_BID.dta", clear
count                          // expect ~300,000–400,000 obs (3 months)
tab migrante_ci                // expect ~4–5% foreign born
tab condocup_ci if inrange(edad_ci,15,64)   // check labor status distribution
sum factor_ci                  // should be positive, no missing
assert !missing(pais_c)
assert !missing(idh_ch)
```

**Venezuelan share check:**
```stata
count if migrante_ci == 1
local total = r(N)
count if migrante_ci == 1 & mig_pais_ci == "Venezuela"
di "Venezuelan share: " %5.1f r(N)/`total'*100 "%"
* Expected: 50–70% of migrants are Venezuelan
```

---

## Step 2 — Run COL 2023t3

```stata
do "do armo/col/COL_2023t3_variablesBID.do"
```

**Expected output:** `bases armo/armo/COL_2023t3_BID.dta`

**Verify immediately after:**
```stata
use "bases armo/armo/COL_2023t3_BID.dta", clear
count
tab migrante_ci
tab condocup_ci if inrange(edad_ci,15,64)
sum factor_ci
assert !missing(pais_c)
assert !missing(idh_ch)
```

---

## Step 3 — Clean up old file (COL 2024t3 only)

A stale output exists at `bases armo/armo/col/COL_2024t3_BID.dta` (wrong subdirectory). Once the new file at `armo/COL_2024t3_BID.dta` is validated, delete the old one manually to avoid confusion.

---

## Step 4 — Confirm both files are visible to hdmf_2.py

```python
import os
folder = r'bases armo/armo'
[f for f in os.listdir(folder) if f.endswith('.dta')]
# COL_2023t3_BID.dta and COL_2024t3_BID.dta should appear in this list
```

---

## Common errors and fixes

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `variable p3042 not found` | Variable renamed in this wave | Check dictionary; update script block |
| `merge: variable p3373s3 not found` | Variable name changed | Verify with `codebook p3373s3` on raw file |
| `type mismatch` on p3373s3 | destring failed or already numeric | Remove `destring p3373s3` line if already numeric |
| `file not found: mig_pais_code.dta` | Absolute path issue | Check path at line ~498 of script; update if running on different machine |
| Output saved but count is very low | `drop if secuencia_p == .` removed too many obs | Check if `secuencia_p` name is different in this wave |
| `saveold` fails | Stata version < 12 or path doesn't exist | Use `save` instead; confirm `armo/` folder exists |

---

## Notes on income variables

Income (`ylm_ci`, `ylnm_ci`, `ynlm_ci`, `ytot_ci`) is **not harmonized** in either script — those blocks are commented out. Only `remesas_ci` and `remesas_ch` are active. This is expected. Do not treat missing income variables as an error.
