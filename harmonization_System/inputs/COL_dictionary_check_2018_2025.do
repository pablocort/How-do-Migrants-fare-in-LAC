*(Versión stata 17)
clear
set more off

di "File created with the Claude HDMF system — 2026-04-08"

*=============================================================================*
* COL GEIH — Cross-wave dictionary check: 2018t3 through 2025t3
* Purpose: verify variable names, types, and category codes are stable
*          across all 8 waves before cloning COL_2023t3_variablesBID.do
* Output:  COL_dictionary_check_2018_2025.log  (same directory as this script)
*=============================================================================*

local root "C:/Users/PABLOCOR/OneDrive - Inter-American Development Bank Group/Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento/Datos/hdmf/How-do-Migrants-fare-in-LAC/bases armo/raw/col"

* Key variables to check in each wave (from COL_2023t3_variablesBID.do)
local vars_ids      "idh orden fex_c18"
local vars_demo     "p6050 p6040 p3016"
local vars_employ   "oci dsi fft p6800 p7045 p6920 p6090 p6460 p6450 p6440 p7450 p6240"
local vars_educ     "p3042 p3042s1 p3042s2 p3043"
local vars_mig      "p3373 p3373s3 p3382"
local vars_income   "impa impaes isa isaes imdi imdies ie iees iof1 iof2 iof3h iof3i iof6 iof1es iof2es iof3hes iof3ies iof6es p7510s2a1"

local allvars `vars_ids' `vars_demo' `vars_employ' `vars_educ' `vars_mig' `vars_income'

local waves "2018t3 2019t3 2020t3 2021t3 2022t3 2023t3 2024t3 2025t3"

*=============================================================================*
* SECTION 1 — Variable existence matrix
* For each wave × variable: 1=exists, 0=missing from dataset
*=============================================================================*

di ""
di "============================================================"
di "SECTION 1: VARIABLE EXISTENCE MATRIX"
di "============================================================"
di "Format: wave | variable | exists (1/0) | type | label"
di "------------------------------------------------------------"

foreach wave of local waves {
    use "`root'/COL_`wave'.dta", clear
    di ""
    di ">>> WAVE: COL_`wave' (N = `=_N')"
    di "    Variables in dataset: `=c(k)'"
    foreach v of local allvars {
        capture confirm variable `v'
        if _rc == 0 {
            local vtype: type `v'
            local vlbl:  variable label `v'
            di "    EXISTS   `v'  [`vtype']  `vlbl'"
        }
        else {
            di "    MISSING  `v'"
        }
    }
}

*=============================================================================*
* SECTION 2 — Categorical checks: key variables with value labels
* Check categories for p6050, p3042, p3373, p3382
*=============================================================================*

di ""
di "============================================================"
di "SECTION 2: CATEGORICAL VARIABLE CODEBOOK (key vars)"
di "============================================================"

foreach wave of local waves {
    use "`root'/COL_`wave'.dta", clear
    di ""
    di ">>> WAVE: COL_`wave'"
    di "--- p6050 (relacion con jefe de hogar) ---"
    capture tab p6050, missing
    di "--- p3042 (nivel educativo) ---"
    capture tab p3042, missing
    di "--- p3373 (lugar nacimiento / migracion) ---"
    capture tab p3373, missing
    di "--- p3382 (tiempo en el pais) ---"
    capture tab p3382, missing
    di "--- p6920 (cotizando pension) ---"
    capture tab p6920, missing
    di "--- p6090 (afiliado salud) ---"
    capture tab p6090, missing
}

*=============================================================================*
* SECTION 3 — Factor weight summary
* Confirm fex_c18 scale across waves (monthly expansion factor)
*=============================================================================*

di ""
di "============================================================"
di "SECTION 3: EXPANSION FACTOR (fex_c18) — summary by wave"
di "============================================================"
di "Expected: monthly weight; N*fex_c18 should approximate monthly pop"

foreach wave of local waves {
    use "`root'/COL_`wave'.dta", clear
    capture confirm variable fex_c18
    if _rc == 0 {
        quietly sum fex_c18
        di "COL_`wave':  N=`=_N'  fex_c18: min=`r(min)'  mean=`r(mean)'  max=`r(max)'  sum=`r(sum)'"
    }
    else {
        di "COL_`wave':  fex_c18 NOT FOUND"
    }
}

*=============================================================================*
* SECTION 4 — Migration variable deep dive
* p3373 categories, p3373s3 (country of origin codes), p3382 (arrival recency)
*=============================================================================*

di ""
di "============================================================"
di "SECTION 4: MIGRATION MODULE DEEP DIVE"
di "============================================================"

foreach wave of local waves {
    use "`root'/COL_`wave'.dta", clear
    di ""
    di ">>> WAVE: COL_`wave'"

    * p3373 — birthplace / migration status
    capture confirm variable p3373
    if _rc == 0 {
        di "  p3373 exists — label: `:variable label p3373'"
        tab p3373, missing
        * Code 3 = born abroad (used in harmonization)
        capture count if p3373 == 3
        if _rc == 0 di "  p3373==3 (born abroad): `r(N)' obs"
    }
    else {
        di "  p3373: NOT FOUND"
    }

    * p3373s3 — country of birth code
    capture confirm variable p3373s3
    if _rc == 0 {
        di "  p3373s3 exists — label: `:variable label p3373s3'"
        * Top 10 most frequent foreign birthplace codes
        di "  Top 10 p3373s3 values among p3373==3:"
        capture {
            preserve
            keep if p3373 == 3
            tab p3373s3, sort missing
            restore
        }
    }
    else {
        di "  p3373s3: NOT FOUND"
    }

    * p3382 — time in country / recency
    capture confirm variable p3382
    if _rc == 0 {
        di "  p3382 exists — label: `:variable label p3382'"
        tab p3382, missing
    }
    else {
        di "  p3382: NOT FOUND"
    }
}

*=============================================================================*
* SECTION 5 — Education variable p3042 category comparison
* Core mapping assumption: categories 1-13 stable across waves
*=============================================================================*

di ""
di "============================================================"
di "SECTION 5: EDUCATION (p3042) CATEGORY DETAIL"
di "============================================================"

foreach wave of local waves {
    use "`root'/COL_`wave'.dta", clear
    capture confirm variable p3042
    if _rc == 0 {
        di ""
        di ">>> WAVE: COL_`wave'  — p3042 value labels:"
        capture label list `: value label p3042'
        tab p3042, missing
    }
    else {
        di "COL_`wave': p3042 NOT FOUND"
    }
}

*=============================================================================*
* SECTION 6 — Income variables availability
* Block is commented out in current scripts; this confirms which vars exist
*=============================================================================*

di ""
di "============================================================"
di "SECTION 6: INCOME VARIABLES AVAILABILITY"
di "============================================================"

foreach wave of local waves {
    use "`root'/COL_`wave'.dta", clear
    di ""
    di ">>> WAVE: COL_`wave'"
    foreach v of local vars_income {
        capture confirm variable `v'
        if _rc == 0 {
            quietly sum `v'
            di "  EXISTS   `v'  (N non-missing: `r(N)'  mean: `r(mean)')"
        }
        else {
            di "  MISSING  `v'"
        }
    }
}

di ""
di "============================================================"
di "DICTIONARY CHECK COMPLETE"
di "============================================================"
