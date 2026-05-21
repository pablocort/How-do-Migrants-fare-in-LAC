/*==============================================================================
  CHL_2020a_variablesBID.do
  HDMF — How do Migrants Fare in LAC
  Country : Chile
  Survey  : CASEN (Encuesta de Caracterización Socioeconómica Nacional)
  Wave    : 2020 (annual — COVID-19 round)
  Input   : bases armo/raw/chl/casen_2020.dta
  Output  : bases armo/armo/CHL/CHL_2020a_BID.dta
  Author  : Pablo Cortés Sánchez / HDMF Team — IDB
  Created : 2026-04-16

  Reference wave : CHL_2024a (CHL_2024_variablesBID.do)
  Dictionary check: bases armo/armo/CHL/intermediate_harmo_output/CHL_dictionary_check_2017a_2022a.md

  !! COVID-19 WAVE — IMPORTANT STRUCTURAL DIFFERENCES !!
  The CASEN 2020 was conducted during the COVID-19 pandemic (Nov 2020–Feb 2021).
  Several modules were shortened or removed. Key differences from 2024 reference:

  1. HOURS: o10 (hours last week) ABSENT.
     ALTERNATIVE: horaspri_ci = round(y2_hrs / 4.3)
     (y2_hrs = monthly hours; dividing by 4.3 converts to weekly approximation)
     *** This is a rough approximation. Flag in all analyses using CHL 2020 hours. ***

  2. CONTRACT: o18 (contract type) and o19 (written contract) ABSENT.
     ALTERNATIVE: tipocontrato_ci = . (not collected)

  3. EDUCATION ATTENDANCE: asiste and e3 ABSENT.
     ALTERNATIVE: e2 (1=yes attending, 2=no) used for attendance check.
     e6a_asiste and e6a_no_asiste ABSENT → set to .

  4. HIGHER EDUCATION COMPLETION: e6c_completo ABSENT.
     ALTERNATIVE: edu_hdmf categories 6–8 collapsed:
       - Attending HE (e2==1) → edu_hdmf = 6 (in progress)
       - Not attending HE (e2==2) → edu_hdmf = 7 (any higher ed, complete/incomplete)
       - University-level (e6a==7 or 8) not attending → edu_hdmf = 7 (proxy for completed)
       - Cannot distinguish between 7 (tech complete) and 8 (uni complete) without e6c_completo
       *** Users must note that edu_hdmf categories 7 and 8 are COLLAPSED in CHL 2020 ***

  5. CINEF13 (field of study): cinef13_area and cinef13_subarea ABSENT.

  6. MIGRATION RECENCY: r1cp (years since arrival, numeric) ABSENT.
     ALTERNATIVE: r2 (categorical): 1=<1yr, 2=1-5yr, 3=>5yr
     migrantiguo5_ci: r2==3 → 1 (5+ years); r2==1|r2==2 → 0

  7. LAC COUNTRY CODES: r1b_pais_esp (string name) present in 2020 for mig_pais_ci.
     r1b_p_cod (numeric ISO codes) available for LAC inlist.
     Using r1b_p_cod for LAC flag to match 2017 approach; r1b_pais_esp for mig_pais_ci.

  8. PERSON ID: id_persona PRESENT in 2020 (o also present — use id_persona for consistency).

  9. e6b/e6a missing codes: 99 used in some records → replace with . before using.
==============================================================================*/

clear all
set more off
di "File created with the Claude HDMF system — 2026-04-16"

*------------------------------------------------------------------------------
* Paths & log
*------------------------------------------------------------------------------
local ANO    2020
local base_in  "bases armo/raw/chl/CHL_2020m11_m12_m1.dta"
local base_out "bases armo/armo/CHL/CHL_2020a_BID.dta"
local log_dir  "do armo/chl/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/CHL_2020a_variablesBID.log", replace

use "`base_in'", clear

*------------------------------------------------------------------------------
* 1. IDENTIFIERS & WEIGHTS
*------------------------------------------------------------------------------
gen str pais_c = "CHL"

gen double idh_ch  = folio
gen double idp_ci  = id_persona     /* id_persona PRESENT in 2020 */
gen double factor_ci = expr
gen double factor_ch = expr

*------------------------------------------------------------------------------
* 2. DEMOGRAPHICS
*------------------------------------------------------------------------------
gen byte edad_ci = edad
gen byte sexo_ci = sexo

* Relationship to head
gen byte relacion_ci = .
replace  relacion_ci = 1 if pco1 == 1
replace  relacion_ci = 2 if pco1 == 2
replace  relacion_ci = 3 if pco1 == 3
replace  relacion_ci = 4 if inlist(pco1, 4, 5, 6, 7, 8)
replace  relacion_ci = 5 if pco1 == 9

bysort folio: gen miembros_ci = _N

*------------------------------------------------------------------------------
* 3. EMPLOYMENT STATUS (15–64)
*------------------------------------------------------------------------------
gen byte condocup_ci = .
replace condocup_ci = 1 if (o1 == 1 | o2 == 1 | o3 == 1) & inrange(edad_ci, 15, 64)
replace condocup_ci = 2 if condocup_ci == . & ///
    (o1 == 2 & o2 == 2 & o3 == 2) & o6 == 1 & inrange(edad_ci, 15, 64)
replace condocup_ci = 3 if condocup_ci == . & inrange(edad_ci, 15, 64)
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

/* !! COVID ALTERNATIVE for hours !!
   o10 (hours last week) ABSENT in CASEN 2020.
   y2_hrs = total monthly hours; converting to weekly by dividing by 4.3.
   This is an approximation. Weekly and monthly reporting periods differ.
   Flag this variable in any analysis comparing CHL 2020 hours to other waves. */
gen int horaspri_ci = .
replace horaspri_ci = round(y2_hrs / 4.3) if emp_ci == 1 & !missing(y2_hrs) & y2_hrs > 0

gen int horastot_ci = horaspri_ci

* cotizando_ci: o32 present in 2020
gen byte cotizando_ci = .
replace  cotizando_ci = 1 if o32 >= 1 & o32 <= 5 & emp_ci == 1
replace  cotizando_ci = 0 if o32 == 6 & emp_ci == 1

* afiliado_ci: o31 present in 2020
gen byte afiliado_ci = .
replace  afiliado_ci = 1 if o31 == 1 & emp_ci == 1
replace  afiliado_ci = 0 if o31 != 1 & !missing(o31) & emp_ci == 1

* Fill remaining missing with 0 for employed (matching 2024 reference recode approach)
recode cotizando_ci . = 0 if emp_ci == 1
recode afiliado_ci  . = 0 if emp_ci == 1

* FIX-CHL-01 (QA 2026-04-21): o31 captures ALL health affiliates incl. FONASA A/B (subsidized,
* non-contributive); no regime-type variable available in CASEN 2020 to distinguish.
* formal_ci based on pension contribution only (cotizando_ci), which is unambiguous.
gen byte formal_ci = .
replace  formal_ci = 1 if cotizando_ci == 1 & emp_ci == 1
replace  formal_ci = 0 if cotizando_ci == 0 & emp_ci == 1

/* !! COVID ALTERNATIVE for contract type !!
   o18 (contract type) and o19 (written contract) NOT COLLECTED in CASEN 2020.
   tipocontrato_ci set to missing for all observations in this wave. */
gen byte tipocontrato_ci = .   /* CASEN 2020: contract type variables absent (COVID round) */

*------------------------------------------------------------------------------
* 5. EDUCATION
* FIX 2026-04-16: e6a has 17 categories in 2020 (not 8). Same structure as
* 2022/2024 for codes 1-15; codes 16,17 are additional postgrad categories.
* Reference: CHL_education_harmonization_comparison.md (2026-04-16)
*------------------------------------------------------------------------------
* e6c_completo: ABSENT in 2020 (COVID wave) — use e2 as attendance proxy
* e2: 1=currently attending, 2=not attending — PRESENT in 2020
* e6b missing code: 99 (2020)
* WARNING: edu_hdmf categories 7 (uni complete) and 8 (postgrad complete)
* CANNOT BE DISTINGUISHED in CHL 2020 (no e6c_completo). Both collapse to 7.

replace e6b = . if e6b == 99
replace e6b = . if e6b > 10   /* 2020: values >10 are implausible; cap at 10 (114 obs) */

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
* Note: in 2020, e6a 12=CFT, 13=IP, 14=university (split into 3 codes vs 2022's e6a 12,13)
replace aedu_ci = e6b + 12 if inlist(e6a, 12, 13, 14)

* University (long programs) — e6a 15 in 2020 (base 12)
replace aedu_ci = e6b + 12 if e6a == 15

* Postgrad — e6a 16 (magíster) and 17 (doctoral) only in 2017/2020
* e6b measures cumulative years in university+postgrad; using base 12 → range <= 22
replace aedu_ci = e6b + 12 if inlist(e6a, 16, 17)

label var aedu_ci "Anios de educacion aprobados"

* edu_isced — based on aedu_ci ranges + direct e6a for higher education
gen byte edu_isced = .
replace edu_isced = 0 if aedu_ci == 0
replace edu_isced = 1 if inrange(aedu_ci, 1, 6)
replace edu_isced = 2 if inrange(aedu_ci, 7, 8)
replace edu_isced = 3 if inrange(aedu_ci, 9, 12)
replace edu_isced = 5 if inlist(e6a, 12, 13)      /* tech superior (CFT, IP) */
replace edu_isced = 6 if inlist(e6a, 14, 15)      /* university (2020 codes) */
replace edu_isced = 7 if e6a == 16                /* magíster */
replace edu_isced = 8 if e6a == 17                /* doctoral */

/* !! COVID + e6c_completo ABSENT in 2020 — using e2 as attendance proxy !!
   e2: 1=currently attending, 2=not attending.
   Primary/secondary: determined by e6b year (no e6c_completo needed).
   Higher ed: e2==2 (not attending) treated as completed proxy.
   WARNING: edu_hdmf 7 (uni complete) and 8 (postgrad complete) COLLAPSED INTO 7.
   Category 8 intentionally absent for CHL 2020. */

gen byte edu_hdmf = .

* 1. Less than primary / preschool
replace edu_hdmf = 1 if inlist(e6a, 1, 2, 3, 4)

* 2. Primary incomplete (years 1-5)
replace edu_hdmf = 2 if inlist(e6a, 6, 7) & inrange(e6b, 1, 5)

* 3. Primary complete (year 6)
replace edu_hdmf = 3 if inlist(e6a, 6, 7) & e6b == 6 & e2 == 2

* 4. Secondary incomplete
replace edu_hdmf = 4 if e6a == 7 & inlist(e6b, 7, 8)            /* básica 7°–8° */
replace edu_hdmf = 4 if inlist(e6a, 8, 10) & inrange(e6b, 1, 5) /* old system incomplete */
replace edu_hdmf = 4 if e6a == 9  & inrange(e6b, 1, 3)          /* modern media incomplete */
replace edu_hdmf = 4 if e6a == 11 & inrange(e6b, 1, 3)          /* modern TP incomplete */

* 5. Secondary complete (+ HE attending → proxy for in-progress)
replace edu_hdmf = 5 if inlist(e6a, 8, 10) & e6b == 6
replace edu_hdmf = 5 if e6a == 9  & e6b == 4
replace edu_hdmf = 5 if e6a == 11 & e6b >= 4 & e6b < .
replace edu_hdmf = 5 if inlist(e6a, 12, 13, 14, 15) & e2 == 1   /* attending HE */
replace edu_hdmf = 5 if inlist(e6a, 16, 17)         & e2 == 1   /* attending postgrad */

* 6. Technical complete (proxy: not attending tech sup)
replace edu_hdmf = 6 if inlist(e6a, 12, 13) & e2 == 2            /* tech superior */

* 7. University or higher (proxy: not attending; cats 7+8 collapsed — no e6c_completo)
replace edu_hdmf = 7 if inlist(e6a, 14, 15) & e2 == 2            /* university */
replace edu_hdmf = 7 if inlist(e6a, 16, 17) & e2 == 2            /* postgrad (collapsed to 7) */
/* edu_hdmf = 8 intentionally absent for CHL 2020 (cannot distinguish from 7) */

*------------------------------------------------------------------------------
* 6. MIGRATION
*------------------------------------------------------------------------------
* migrante_ci — 2020: r1b = place of birth
* r1b: 1=same municipality, 2=another municipality in Chile, 3=another country, 9=don't know
* Only r1b==3 ("En otro país") = foreign-born migrants
gen byte migrante_ci = .
replace  migrante_ci = 0 if inlist(r1b, 1, 2)
replace  migrante_ci = 1 if r1b == 3

/* !! ALTERNATIVE for migrantiguo5_ci !!
   r1cp (numeric years since arrival) ABSENT in CASEN 2020.
   Using r2 (categorical): 1=less than 1 year, 2=1–5 years, 3=more than 5 years.
   migrantiguo5_ci = 1 if r2==3 (5+ years in Chile). */
gen byte migrantiguo5_ci = .
replace  migrantiguo5_ci = 0 if migrante_ci == 1 & inlist(r2, 1, 2)
replace  migrantiguo5_ci = 1 if migrante_ci == 1 & r2 == 3

* mig_pais_ci — r1b_pais_esp is already a string variable in 2020
gen str mig_pais_ci = ""
replace mig_pais_ci = r1b_pais_esp if migrante_ci == 1 & !missing(r1b_pais_esp)

* LAC migrant flag — r1b_pais_esp uses ALL-CAPS in 2020 (e.g. "VENEZUELA", "PERU")
gen byte mig_lac_ci = 0 if migrante_ci == 1
replace  mig_lac_ci = 1 if migrante_ci == 1 & ///
    inlist(r1b_pais_esp, "VENEZUELA", "COLOMBIA", "PERU", "BOLIVIA", "ECUADOR", "HAITI", "ARGENTINA")
replace  mig_lac_ci = 1 if migrante_ci == 1 & ///
    inlist(r1b_pais_esp, "BRASIL", "PARAGUAY", "URUGUAY", "CUBA", "MEXICO", "REPUBLICA DOMINICANA")
/* Note: unaccented uppercase forms used for encoding robustness */

*------------------------------------------------------------------------------
* 7. REMITTANCES
*------------------------------------------------------------------------------
gen double remesas_ci = .
gen double remesas_ch = .

*------------------------------------------------------------------------------
* 8. INCOME — EXCLUDED
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

di "CHL 2020a harmonization complete — `base_out'"
log close
di "NOTE: CHL 2020 is the COVID-19 wave. Key limitations:"
di "  - horaspri_ci = round(y2_hrs/4.3) [monthly→weekly approximation; o10 absent]"
di "  - tipocontrato_ci = . [o18/o19 absent]"
di "  - edu_hdmf 7 and 8 collapsed into 7 [e6c_completo absent]"
di "  - migrantiguo5_ci from r2 categorical [r1cp absent]"
