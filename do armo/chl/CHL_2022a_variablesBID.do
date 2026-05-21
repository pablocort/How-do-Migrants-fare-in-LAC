/*==============================================================================
  CHL_2022a_variablesBID.do
  HDMF — How do Migrants Fare in LAC
  Country : Chile
  Survey  : CASEN (Encuesta de Caracterización Socioeconómica Nacional)
  Wave    : 2022 (annual)
  Input   : bases armo/raw/chl/casen_2022.dta
  Output  : bases armo/armo/CHL/CHL_2022a_BID.dta
  Author  : Pablo Cortés Sánchez / HDMF Team — IDB
  Created : 2026-04-16

  Reference wave : CHL_2024a (CHL_2024_variablesBID.do)
  Dictionary check: bases armo/armo/CHL/intermediate_harmo_output/CHL_dictionary_check_2017a_2022a.md

  Differences from 2024 reference:
  - r2 also available for migrantiguo5 cross-check (r1cp present → same logic as 2024)
  - r1b_pais_esp present → same string-based LAC inlist as 2024
  - e6c_completo present → same edu_hdmf construction as 2024
  - e6a_asiste / e6a_no_asiste present → same higher-ed level variables as 2024
  - tipocontrato_ci: o18/o19 PRESENT (verified by Python dict check 2026-04-16)
    despite alt do-file comment implying otherwise
  - o31/o32 present → same afiliado/cotizando as 2024
  - All other variables: identical to 2024 reference
==============================================================================*/

clear all
set more off
di "File created with the Claude HDMF system — 2026-04-16"

*------------------------------------------------------------------------------
* Paths & log
*------------------------------------------------------------------------------
local ANO    2022
local base_in  "bases armo/raw/chl/CHL_2022m11_m12_m1.dta"
local base_out "bases armo/armo/CHL/CHL_2022a_BID.dta"
local log_dir  "do armo/chl/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/CHL_2022a_variablesBID.log", replace

use "`base_in'", clear

*------------------------------------------------------------------------------
* 1. IDENTIFIERS & WEIGHTS
*------------------------------------------------------------------------------
gen str pais_c = "CHL"

gen double idh_ch  = folio
gen double idp_ci  = id_persona
gen double factor_ci = expr
gen double factor_ch = expr

*------------------------------------------------------------------------------
* 2. DEMOGRAPHICS
*------------------------------------------------------------------------------
* Age
gen byte edad_ci = edad

* Sex (1=male, 2=female → HDMF: 1=male, 2=female)
gen byte sexo_ci = sexo

* Relationship to head of household
* pco1: 1=head, 2=spouse/partner, 3=son/daughter, 4=son/daughter-in-law,
*        5=grandchild, 6=parent/parent-in-law, 7=other relative, 8=non-relative, 9=domestic worker
gen byte relacion_ci = .
replace  relacion_ci = 1 if pco1 == 1
replace  relacion_ci = 2 if pco1 == 2
replace  relacion_ci = 3 if pco1 == 3
replace  relacion_ci = 4 if inlist(pco1, 4, 5, 6, 7, 8)
replace  relacion_ci = 5 if pco1 == 9

* Household size
bysort folio: gen miembros_ci = _N

*------------------------------------------------------------------------------
* 3. EMPLOYMENT STATUS
* o1=works, o2=second job, o3=occasional job; o6=looking for work (unemp)
* Age restriction: 15–64
*------------------------------------------------------------------------------
gen byte condocup_ci = .
* Employed
replace condocup_ci = 1 if (o1 == 1 | o2 == 1 | o3 == 1) & inrange(edad_ci, 15, 64)
* Unemployed
replace condocup_ci = 2 if condocup_ci == . & ///
    (o1 == 2 & o2 == 2 & o3 == 2) & o6 == 1 & inrange(edad_ci, 15, 64)
* Inactive
replace condocup_ci = 3 if condocup_ci == . & inrange(edad_ci, 15, 64)
* Out of working-age population
replace condocup_ci = 4 if !inrange(edad_ci, 15, 64)

gen byte emp_ci    = (condocup_ci == 1) if !missing(condocup_ci)
gen byte desemp_ci = (condocup_ci == 2) if !missing(condocup_ci)
gen byte pea_ci    = (inlist(condocup_ci, 1, 2)) if !missing(condocup_ci)

replace emp_ci    = . if !inrange(edad_ci, 15, 64)
replace desemp_ci = . if !inrange(edad_ci, 15, 64)
replace pea_ci    = . if !inrange(edad_ci, 15, 64)

*------------------------------------------------------------------------------
* 4. JOB CHARACTERISTICS (employed persons only)
*------------------------------------------------------------------------------

* Hours worked (primary job) — o10 present in 2022
gen int horaspri_ci = .
replace horaspri_ci = o10 if emp_ci == 1 & o10 != -88 & !missing(o10)
replace horaspri_ci = . if horaspri_ci < 0

* Total hours (all jobs) — use horaspri as proxy if no multi-job variable
gen int horastot_ci = horaspri_ci

* Formality: contributes to pension (cotizando) OR has formal contract
* cotizando_ci: o32 = 1–5 → contributes to AFP/pension
gen byte cotizando_ci = .
replace  cotizando_ci = 1 if o32 >= 1 & o32 <= 5 & emp_ci == 1
replace  cotizando_ci = 0 if o32 == 6 & emp_ci == 1

* afiliado_ci: o31 == 1 → affiliated to health system
gen byte afiliado_ci = .
replace  afiliado_ci = 1 if o31 == 1 & emp_ci == 1
replace  afiliado_ci = 0 if o31 != 1 & !missing(o31) & emp_ci == 1

* Fill remaining missing with 0 for employed (matching 2024 reference recode approach)
recode cotizando_ci . = 0 if emp_ci == 1
recode afiliado_ci  . = 0 if emp_ci == 1

* FIX-CHL-01 (QA 2026-04-21): o31 captures ALL health affiliates incl. FONASA A/B (subsidized,
* non-contributive); no regime-type variable available in CASEN 2022 to distinguish.
* formal_ci based on pension contribution only (cotizando_ci), which is unambiguous.
gen byte formal_ci = .
replace  formal_ci = 1 if cotizando_ci == 1 & emp_ci == 1
replace  formal_ci = 0 if cotizando_ci == 0 & emp_ci == 1

* tipocontrato_ci — o18/o19 PRESENT in 2022 (verified)
* o18: 1=indefinite, 2=fixed-term, 3=project, 4=apprentice, 5=other written
* o19: 1=yes written contract, 2=no
gen byte tipocontrato_ci = .
replace  tipocontrato_ci = 1 if o18 == 1 & emp_ci == 1                     /* indefinido */
replace  tipocontrato_ci = 2 if inlist(o18, 2, 3, 4, 5) & emp_ci == 1     /* plazo fijo u otro escrito */
replace  tipocontrato_ci = 3 if o19 == 2 & emp_ci == 1                    /* sin contrato escrito */

*------------------------------------------------------------------------------
* 5. EDUCATION
* FIX 2026-04-16: e6a has 15 categories in ALL CASEN waves (not 8).
* e6a 1-4=preschool/none, 5=special, 6=old primary, 7=modern básica,
* 8,10=old secondary, 9,11=modern secondary, 12=tech sup, 13=university,
* 14=magíster, 15=doctoral.
* Previous scripts used a wrong 8-category mapping; corrected below.
* Reference: CHL_education_harmonization_comparison.md (2026-04-16)
*------------------------------------------------------------------------------
* e6c_completo: 1=completed, 2=did not complete — PRESENT in 2022
* asiste: 1=currently attending, 2=not attending — PRESENT in 2022
* e6b missing code: -88 (2022)

replace e6b = . if e6b == -88

gen int aedu_ci = .

* No formal education / preschool (e6a 1-4: no e6b collected)
replace aedu_ci = 0 if inlist(e6a, 1, 2, 3, 4)

* Special education — not comparable to years-of-schooling scale
replace aedu_ci = . if e6a == 5

* Old primary system (base 0, max 6 years)
replace aedu_ci = e6b if e6a == 6

* Modern básica (base 0, max 8 years)
replace aedu_ci = e6b if e6a == 7

* Old secondary — humanístico and técnico-profesional (base 6)
replace aedu_ci = e6b + 6 if inlist(e6a, 8, 10)

* Modern secondary — científico-humanista and técnico-profesional (base 8)
replace aedu_ci = e6b + 8 if inlist(e6a, 9, 11)

* Technical superior + university (base 12)
replace aedu_ci = e6b + 12 if inlist(e6a, 12, 13)

* Postgrad — magíster and doctoral (base 16)
replace aedu_ci = e6b + 16 if inlist(e6a, 14, 15)

label var aedu_ci "Anios de educacion aprobados"

* edu_isced — based on aedu_ci ranges + direct e6a for higher education
gen byte edu_isced = .
replace edu_isced = 0 if aedu_ci == 0
replace edu_isced = 1 if inrange(aedu_ci, 1, 6)
replace edu_isced = 2 if inrange(aedu_ci, 7, 8)
replace edu_isced = 3 if inrange(aedu_ci, 9, 12)
replace edu_isced = 5 if e6a == 12
replace edu_isced = 6 if e6a == 13
replace edu_isced = 7 if e6a == 14
replace edu_isced = 8 if e6a == 15

* edu_hdmf — e6c_completo and asiste PRESENT in 2022: full 8-category classification
* Logic mirrors 2024 reference script exactly.
* Primary/secondary: determined by e6b year within level.
* Higher ed: determined by e6c_completo (completion) and asiste (attendance).
gen byte edu_hdmf = .

* 1. Less than primary / preschool
replace edu_hdmf = 1 if inlist(e6a, 1, 2, 3, 4)

* 2. Primary incomplete (years 1-5 of either system)
replace edu_hdmf = 2 if inlist(e6a, 6, 7) & inrange(e6b, 1, 5)

* 3. Primary complete (year 6 reached)
replace edu_hdmf = 3 if inlist(e6a, 6, 7) & e6b == 6 & asiste == 2

* 4. Secondary incomplete
replace edu_hdmf = 4 if e6a == 7 & inlist(e6b, 7, 8)            /* básica 7°–8° = lower secondary */
replace edu_hdmf = 4 if inlist(e6a, 8, 10) & inrange(e6b, 1, 5) /* old system incomplete */
replace edu_hdmf = 4 if e6a == 9  & inrange(e6b, 1, 3)          /* modern media incomplete */
replace edu_hdmf = 4 if e6a == 11 & inrange(e6b, 1, 3)          /* modern TP incomplete */

* 5. Secondary complete (+ higher ed not yet completed → coded as sec-complete)
replace edu_hdmf = 5 if inlist(e6a, 8, 10) & e6b == 6
replace edu_hdmf = 5 if e6a == 9  & e6b == 4
replace edu_hdmf = 5 if e6a == 11 & e6b >= 4 & e6b < .
replace edu_hdmf = 5 if e6a == 12 & (asiste == 1 | (asiste == 2 & e6c_completo == 2) | missing(e6c_completo))
replace edu_hdmf = 5 if e6a == 13 & (asiste == 1 | (asiste == 2 & e6c_completo == 2) | missing(e6c_completo))

* 6. Technical / tertiary complete
replace edu_hdmf = 6 if e6a == 12 & asiste == 2 & e6c_completo == 1

* 7. University complete (+ postgrad not completed)
replace edu_hdmf = 7 if e6a == 13 & asiste == 2 & e6c_completo == 1
replace edu_hdmf = 7 if inlist(e6a, 14, 15) & (asiste == 1 | (asiste == 2 & e6c_completo == 2) | missing(e6c_completo))

* 8. Postgrad complete
replace edu_hdmf = 8 if inlist(e6a, 14, 15) & asiste == 2 & e6c_completo == 1

*------------------------------------------------------------------------------
* 6. MIGRATION
*------------------------------------------------------------------------------
* r1b: 1=born in Chile, 2=born in another country, 3=foreign-born (some waves use 2/3)
* Treat r1b==2 OR r1b==3 as migrant
* migrante_ci — 2022: r1b = place of birth
* r1b: 1=same municipality, 2=another municipality in Chile, 3=another country, 9=don't know
* Only r1b==3 ("En otro país") = foreign-born migrants
gen byte migrante_ci = .
replace  migrante_ci = 0 if inlist(r1b, 1, 2)
replace  migrante_ci = 1 if r1b == 3

* migrantiguo5_ci: been in Chile 5+ years (r1cp = years since arrival, numeric)
* r1cp present in 2022
gen byte migrantiguo5_ci = .
replace  migrantiguo5_ci = 0 if migrante_ci == 1 & r1cp < 4
replace  migrantiguo5_ci = 1 if migrante_ci == 1 & r1cp >= 4 & !missing(r1cp)
/* NOTE: r2 (categorical) also available in 2022: 1=<1yr, 2=1-5yr, 3=>5yr
   Using r1cp (numeric) is preferred for precision. Cross-check:
   r2==3 → migrantiguo5=1; r2==1|r2==2 → migrantiguo5=0 */

* mig_pais_ci — r1b_pais_esp is already a string variable in 2022
gen str mig_pais_ci = ""
replace mig_pais_ci = r1b_pais_esp if migrante_ci == 1 & !missing(r1b_pais_esp)

* LAC migrant flag — using r1b_pais_esp string (same as 2024 reference)
* Split into two replace lines to avoid Stata's expression length limit
gen byte mig_lac_ci = 0 if migrante_ci == 1
replace  mig_lac_ci = 1 if migrante_ci == 1 & ///
    inlist(r1b_pais_esp, "Venezuela", "Colombia", "Perú", "Bolivia", "Ecuador", "Haití", "Argentina")
replace  mig_lac_ci = 1 if migrante_ci == 1 & ///
    inlist(r1b_pais_esp, "Brasil", "Paraguay", "Uruguay", "Cuba", "México", "República Dominicana")

*------------------------------------------------------------------------------
* 7. REMITTANCES
*------------------------------------------------------------------------------
* Remesas — check if available in 2022 CASEN
* NOTE: CASEN 2022 may include remittances module; variable names may differ
* from 2024. Set to missing if not found. Review raw codebook to confirm.
gen double remesas_ci = .   /* individual remittances — verify variable in raw */
gen double remesas_ch = .   /* household remittances — verify variable in raw */
/* TODO: if e.g. s25 or y2_rem available, replace accordingly */

*------------------------------------------------------------------------------
* 8. INCOME — EXCLUDED
*    Income module intentionally excluded from CHL harmonization
*    (ylm_ci, ylnm_ci, ynlm_ci, ytot_ci not computed)
*------------------------------------------------------------------------------
/*
gen double ylm_ci  = .
gen double ylnm_ci = .
gen double ynlm_ci = .
gen double ytot_ci = .
*/

*------------------------------------------------------------------------------
* 8b. OCCUPATION & OVERQUALIFICATION
*------------------------------------------------------------------------------
gen byte ocupa_ci = .
replace ocupa_ci = oficio1 if emp_ci == 1 & !missing(oficio1) & oficio1 > 0
label define ocupa_lbl 1 "Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary", replace
label values ocupa_ci ocupa_lbl
label var ocupa_ci "ISCO-08 major group (CIUO-08 via oficio1, 1-digit direct)"
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified", replace
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (tertiary educ + low-skill occ, ISCO-08 4-9)"

*------------------------------------------------------------------------------
* 9. KEEP HDMF STANDARD VARIABLES
*------------------------------------------------------------------------------
keep pais_c idh_ch idp_ci factor_ci factor_ch ///
     edad_ci sexo_ci relacion_ci miembros_ci ///
     migrante_ci mig_pais_ci migrantiguo5_ci mig_lac_ci ///
     condocup_ci emp_ci desemp_ci pea_ci ///
     formal_ci tipocontrato_ci horaspri_ci horastot_ci ///
     cotizando_ci afiliado_ci ///
     ocupa_ci overqualified_ci ///
     aedu_ci edu_isced edu_hdmf ///
     remesas_ci remesas_ch

order pais_c idh_ch idp_ci factor_ci factor_ch ///
      edad_ci sexo_ci relacion_ci miembros_ci ///
      migrante_ci mig_pais_ci migrantiguo5_ci ///
      condocup_ci emp_ci desemp_ci pea_ci ///
      formal_ci tipocontrato_ci horaspri_ci horastot_ci ///
      cotizando_ci afiliado_ci ///
      ocupa_ci overqualified_ci ///
      aedu_ci edu_isced edu_hdmf ///
      remesas_ci remesas_ch

*------------------------------------------------------------------------------
* 10. SAVE
*------------------------------------------------------------------------------
saveold "`base_out'", replace

di "CHL 2022a harmonization complete — `base_out'"
log close
