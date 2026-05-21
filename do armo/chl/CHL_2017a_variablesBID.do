/*==============================================================================
  CHL_2017a_variablesBID.do
  HDMF — How do Migrants Fare in LAC
  Country : Chile
  Survey  : CASEN (Encuesta de Caracterización Socioeconómica Nacional)
  Wave    : 2017 (annual)
  Input   : bases armo/raw/chl/casen_2017.dta
  Output  : bases armo/armo/CHL/CHL_2017a_BID.dta
  Author  : Pablo Cortés Sánchez / HDMF Team — IDB
  Created : 2026-04-16

  Reference wave : CHL_2024a (CHL_2024_variablesBID.do)
  Dictionary check: bases armo/armo/CHL/intermediate_harmo_output/CHL_dictionary_check_2017a_2022a.md

  Differences from 2024 reference:
  1. PERSON ID: id_persona ABSENT → use `o` (numeric person identifier)
  2. SOCIAL SECURITY: o31/o32 ABSENT → use o28 (afiliado) and o29 (cotizando)
  3. CONTRACT: o18/o19 PRESENT (verified by Python dict check) → same as 2024
  4. HE COMPLETION: e6c_completo ABSENT → edu_hdmf 7/8 collapsed (see note below)
     e6a_asiste / e6a_no_asiste ABSENT → set to .
  5. CINEF13 (field of study): ABSENT in 2017
  6. MIGRATION RECENCY: r1cp numeric PRESENT in 2017 → migrantiguo5_ci = (r1cp>=4)
  7. COUNTRY OF ORIGIN: r1b_pais_esp (string) ABSENT in 2017
     ALTERNATIVE: r1b_p_cod (numeric ISO codes) for both mig_pais_ci and LAC inlist
  8. ATTENDANCE: asiste and e3 PRESENT in 2017 → same as 2024
  9. e6b/e6a missing codes: 99 used in some records → replaced before use
==============================================================================*/

clear all
set more off
di "File created with the Claude HDMF system — 2026-04-16"

*------------------------------------------------------------------------------
* Paths & log
*------------------------------------------------------------------------------
local ANO    2017
local base_in  "bases armo/raw/chl/CHL_2017m11_m12_m1.dta"
local base_out "bases armo/armo/CHL/CHL_2017a_BID.dta"
local log_dir  "do armo/chl/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/CHL_2017a_variablesBID.log", replace

use "`base_in'", clear

*------------------------------------------------------------------------------
* 1. IDENTIFIERS & WEIGHTS
*------------------------------------------------------------------------------
gen str pais_c = "CHL"

gen double idh_ch  = folio
/* ALTERNATIVE: id_persona ABSENT in 2017 — use `o` (numeric person ID within household) */
gen double idp_ci  = o
gen double factor_ci = expr
gen double factor_ch = expr

*------------------------------------------------------------------------------
* 2. DEMOGRAPHICS
*------------------------------------------------------------------------------
gen byte edad_ci = edad
gen byte sexo_ci = sexo

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

* Hours — o10 PRESENT in 2017
gen int horaspri_ci = .
replace horaspri_ci = o10 if emp_ci == 1 & o10 != -88 & !missing(o10)
replace horaspri_ci = . if horaspri_ci < 0

gen int horastot_ci = horaspri_ci

/* ALTERNATIVE for social security in 2017:
   o31/o32 (2024 variable names) ABSENT.
   Using o28 (health affiliation) and o29 (pension contribution) */

* cotizando_ci: o29 (pension contribution, 2017 variable name)
* Codes: 1–5 = contributes to AFP/pension; 6–7 = does not contribute
* NOTE: in 2017, code 7 ("No cotiza") is the main non-contribution code (49,902 obs);
*       code 6 has only 46 obs. Using >= 6 captures both.
gen byte cotizando_ci = .
replace  cotizando_ci = 1 if o29 >= 1 & o29 <= 5 & emp_ci == 1
replace  cotizando_ci = 0 if o29 >= 6 & o29 < 9 & emp_ci == 1

* afiliado_ci: o28 (health affiliation, 2017 variable name)
* Code: 1 = affiliated to health system; other = not affiliated
gen byte afiliado_ci = .
replace  afiliado_ci = 1 if o28 == 1 & emp_ci == 1
replace  afiliado_ci = 0 if o28 != 1 & !missing(o28) & emp_ci == 1

* Fill remaining missing with 0 for employed (matching 2024 reference recode approach)
recode cotizando_ci . = 0 if emp_ci == 1
recode afiliado_ci  . = 0 if emp_ci == 1

* FIX-CHL-01 (QA 2026-04-21): o28 captures ALL health affiliates incl. FONASA A/B (subsidized,
* non-contributive); no regime-type variable available in CASEN 2017 to distinguish.
* formal_ci based on pension contribution only (cotizando_ci), which is unambiguous.
gen byte formal_ci = .
replace  formal_ci = 1 if cotizando_ci == 1 & emp_ci == 1
replace  formal_ci = 0 if cotizando_ci == 0 & emp_ci == 1

* tipocontrato_ci — o18/o19 PRESENT in 2017 (verified by Python dict check)
gen byte tipocontrato_ci = .
replace  tipocontrato_ci = 1 if o18 == 1 & emp_ci == 1                     /* indefinido */
replace  tipocontrato_ci = 2 if inlist(o18, 2, 3, 4, 5) & emp_ci == 1     /* plazo fijo u otro escrito */
replace  tipocontrato_ci = 3 if o19 == 2 & emp_ci == 1                    /* sin contrato escrito */

*------------------------------------------------------------------------------
* 5. EDUCATION
* FIX 2026-04-16: e6a has 17 categories in 2017 (not 8).
* Same structure as 2022/2024 for codes 1-15; codes 16,17 are additional
* higher-ed/postgrad categories present only in 2017/2020.
* Reference: CHL_education_harmonization_comparison.md (2026-04-16)
*------------------------------------------------------------------------------
* e6c_completo: ABSENT in 2017 — use asiste as proxy for completion
* asiste: 1=currently attending, 2=not attending — PRESENT in 2017
* e6b missing code: 99 (2017); e6a missing code: 99 (2017)
* WARNING: edu_hdmf categories 7 (uni complete) and 8 (postgrad complete)
* CANNOT BE DISTINGUISHED in CHL 2017 (no e6c_completo). Both collapse to 7.

replace e6a = . if e6a == 99
replace e6b = . if e6b == 99

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
* Note: in 2017, e6a 12=CFT, 13=IP, 14=university (split into 3 codes vs 2022's e6a 12,13)
replace aedu_ci = e6b + 12 if inlist(e6a, 12, 13, 14)

* University (long programs) — e6a 15 in 2017 appears to be university/professional (base 12)
replace aedu_ci = e6b + 12 if e6a == 15

* Postgrad — e6a 16 (magíster) and 17 (doctoral) only in 2017/2020
* e6b here measures cumulative years in university+postgrad (not years at postgrad alone)
* Using base 12 keeps aedu_ci range <= 22, consistent with 2022/2024
replace aedu_ci = e6b + 12 if inlist(e6a, 16, 17)

label var aedu_ci "Anios de educacion aprobados"

* edu_isced — based on aedu_ci ranges + direct e6a for higher education
gen byte edu_isced = .
replace edu_isced = 0 if aedu_ci == 0
replace edu_isced = 1 if inrange(aedu_ci, 1, 6)
replace edu_isced = 2 if inrange(aedu_ci, 7, 8)
replace edu_isced = 3 if inrange(aedu_ci, 9, 12)
replace edu_isced = 5 if inlist(e6a, 12, 13)      /* tech superior (CFT, IP) */
replace edu_isced = 6 if inlist(e6a, 14, 15)      /* university (2017 codes) */
replace edu_isced = 7 if e6a == 16                /* magíster */
replace edu_isced = 8 if e6a == 17                /* doctoral */

/* !! e6c_completo ABSENT in 2017 — using asiste as completion proxy !!
   Primary/secondary: determined by e6b year (same as 2024, no e6c_completo needed).
   Higher ed: asiste==2 (not attending) treated as completed proxy.
   WARNING: edu_hdmf 7 (uni complete) and 8 (postgrad complete) COLLAPSED INTO 7.
   Category 8 intentionally absent for CHL 2017. */

gen byte edu_hdmf = .

* 1. Less than primary / preschool
replace edu_hdmf = 1 if inlist(e6a, 1, 2, 3, 4)

* 2. Primary incomplete (years 1-5)
replace edu_hdmf = 2 if inlist(e6a, 6, 7) & inrange(e6b, 1, 5)

* 3. Primary complete (year 6)
replace edu_hdmf = 3 if inlist(e6a, 6, 7) & e6b == 6 & asiste == 2

* 4. Secondary incomplete
replace edu_hdmf = 4 if e6a == 7 & inlist(e6b, 7, 8)            /* básica 7°–8° */
replace edu_hdmf = 4 if inlist(e6a, 8, 10) & inrange(e6b, 1, 5) /* old system incomplete */
replace edu_hdmf = 4 if e6a == 9  & inrange(e6b, 1, 3)          /* modern media incomplete */
replace edu_hdmf = 4 if e6a == 11 & inrange(e6b, 1, 3)          /* modern TP incomplete */

* 5. Secondary complete (+ HE attending → proxy for in-progress)
replace edu_hdmf = 5 if inlist(e6a, 8, 10) & e6b == 6
replace edu_hdmf = 5 if e6a == 9  & e6b == 4
replace edu_hdmf = 5 if e6a == 11 & e6b >= 4 & e6b < .
replace edu_hdmf = 5 if inlist(e6a, 12, 13, 14, 15) & asiste == 1   /* attending HE */
replace edu_hdmf = 5 if inlist(e6a, 16, 17)         & asiste == 1   /* attending postgrad */

* 6. Technical complete (proxy: not attending tech sup)
replace edu_hdmf = 6 if inlist(e6a, 12, 13) & asiste == 2            /* tech superior */

* 7. University or higher (proxy: not attending; cats 7+8 collapsed — no e6c_completo)
replace edu_hdmf = 7 if inlist(e6a, 14, 15) & asiste == 2            /* university */
replace edu_hdmf = 7 if inlist(e6a, 16, 17) & asiste == 2            /* postgrad (collapsed to 7) */
/* edu_hdmf = 8 intentionally absent for CHL 2017 (cannot distinguish from 7) */

*------------------------------------------------------------------------------
* 6. MIGRATION
*------------------------------------------------------------------------------
* migrante_ci — 2017 uses r1a (nationality variable)
* r1a: 1=Chilena Exclusiva, 2=Chilena y otra (doble), 3=Otra nacionalidad (foreign)
* migrante_ci = foreign nationality only (r1a==3)
gen byte migrante_ci = .
replace  migrante_ci = 0 if r1a == 1
replace  migrante_ci = 1 if r1a == 3

* migrantiguo5_ci: r1cp numeric PRESENT in 2017
gen byte migrantiguo5_ci = .
replace  migrantiguo5_ci = 0 if migrante_ci == 1 & r1cp < 4
replace  migrantiguo5_ci = 1 if migrante_ci == 1 & r1cp >= 4 & !missing(r1cp)

* mig_pais_ci — 2017: r1a_esp is string, values in ALL-CAPS (e.g. "VENEZUELA")
* strtrim() removes surrounding spaces from blank observations
gen str mig_pais_ci = ""
replace mig_pais_ci = strtrim(r1a_esp) if migrante_ci == 1 & !missing(r1a_esp) & strtrim(r1a_esp) != ""

* LAC migrant flag — all-caps names as they appear in r1a_esp (2017)
gen byte mig_lac_ci = 0 if migrante_ci == 1
replace  mig_lac_ci = 1 if migrante_ci == 1 & ///
    inlist(strtrim(r1a_esp), "VENEZUELA", "COLOMBIA", "PERU", "BOLIVIA", "ECUADOR", "HAITI", "ARGENTINA")
replace  mig_lac_ci = 1 if migrante_ci == 1 & ///
    inlist(strtrim(r1a_esp), "BRASIL", "PARAGUAY", "URUGUAY", "CUBA", "MEXICO", "REPUBLICA DOMINICANA")
/* Note: accent characters may differ across Stata encodings — using unaccented forms for robustness */

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

di "CHL 2017a harmonization complete — `base_out'"
log close
