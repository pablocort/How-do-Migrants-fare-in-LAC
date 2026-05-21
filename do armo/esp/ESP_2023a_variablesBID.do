*(Stata 17+)
clear
set more off
di "File created with the Claude HDMF system — 2026-05-04"

/*------------------------------------------------------------
  ESP_2023a_variablesBID.do
  Spain (ESP) — Encuesta de Población Activa (EPA), 2023 annual
  Input:  bases armo/raw/esp/ESP_2023a_merged.dta
  Output: bases armo/armo/ESP/ESP_2023a_BID.dta

  SCHEMA: EPA-TRIM-2021 (applies to 2021-2025 waves).
  To clone for another year: change local ANO only.

  NOT AVAILABLE from EPA (labor force survey, no income module):
    ylm_ci / ylnm_ci / ynlm_ci / ytot_ci — no income question
    remesas_ci / remesas_ch               — no remittance question
    cotizando_ci / afiliado_ci            — no social security question
    formal_ci uses SITU proxy (see section 5)
------------------------------------------------------------*/

*------------- Locals & log -------------------------------------------------
local PAIS     ESP
local ENCUESTA EPA
local ANO      2023
local ronda    a

local log_dir "do armo/esp/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/`PAIS'_`ANO'`ronda'_variablesBID.log", replace

*------------- Paths --------------------------------------------------------
* Add a username block for each analyst machine
if c(username) == "PABLOCOR" {
    local proj "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC"
    local base_in  "`proj'\bases armo\raw\esp\ESP_`ANO'`ronda'_merged.dta"
    local base_out "`proj'\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
    capture mkdir "`proj'\bases armo\armo\\`PAIS'"
}

use "`base_in'", clear

/*===========================================================
  SECTION 1 — IDENTIFIERS & WEIGHTS
===========================================================*/

***********
* pais_c
***********
gen str3 pais_c = "ESP"

***********
* idh_ch — unique household ID per household-quarter
* Components: survey year + quarter + CCAA (2-dig) + PROV (2-dig) + NVIVI (5-dig)
* EPA is a rotating panel; same household reappears across quarters.
* Including trimestre makes ID unique within the annual stacked file.
***********
gen idh_ch = string(ano) + "Q" + string(trimestre) + "_" + ///
             string(ccaa,  "%02.0f") + ///
             string(prov,  "%02.0f") + ///
             string(nvivi, "%05.0f")

***********
* idp_ci — person number within household
***********
gen idp_ci = npers
tostring idp_ci, replace

***********
* factor_ci — expansion weight
* FACTOREL stored as integer × 100. Divide to recover actual weight.
* VERIFY: sum factor_ci should approximate Spain's population ~47 million.
***********
gen double factor_ci = factorel / 400
label var factor_ci "Expansion weight (factorel / 400 — verify sum = ~47M)"

***********
* factor_ch — EPA has no separate household weight; use individual weight
***********
gen double factor_ch = factor_ci


/*===========================================================
  SECTION 2 — DEMOGRAPHICS
===========================================================*/

***********
* edad_ci
***********
gen int edad_ci = edad1

***********
* sexo_ci: 1=male, 2=female
* EPA: sexo1 == 1 (hombre), sexo1 == 6 (mujer)
***********
gen byte sexo_ci = .
replace  sexo_ci = 1 if sexo1 == 1
replace  sexo_ci = 2 if sexo1 == 6

***********
* relacion_ci
* EPA RELPP1 codes: 1=reference person, 2=spouse/partner, 3=child,
*                   4=parent/in-law, 5=other relative, 6=non-relative
***********
gen byte relacion_ci = .
replace  relacion_ci = 1 if relpp1 == 1
replace  relacion_ci = 2 if relpp1 == 2
replace  relacion_ci = 3 if relpp1 == 3
replace  relacion_ci = 4 if relpp1 == 4
replace  relacion_ci = 5 if relpp1 == 5
replace  relacion_ci = 6 if relpp1 == 6

label define relacion_lb 1 "Head" 2 "Spouse/partner" 3 "Child" ///
    4 "Parent/in-law" 5 "Other relative" 6 "Non-relative"
label values relacion_ci relacion_lb

***********
* miembros_ci
***********
gen byte miembros_ci = (relacion_ci >= 1 & relacion_ci <= 5)
replace  miembros_ci = . if relacion_ci == .


/*===========================================================
  SECTION 3 — MIGRATION
===========================================================*/

***********
* migrante_ci — born outside Spain
* paina1: ISO 3166-1 numeric code of birth country if born abroad (missing if born in Spain)
* prona1: Spanish province of birth if born in Spain (missing if born abroad)
***********
gen byte migrante_ci = .
replace  migrante_ci = 1 if paina1 != .    // foreign birth country code present
replace  migrante_ci = 0 if prona1 != .    // Spanish province of birth present

***********
* migrantiguo5_ci — migrant resident in Spain 5+ years
* anore: years of residence (0=< 1 year, 1–98=years, 99=not applicable/unknown)
* SCHEMA NOTE: variable named ANORE1/ANORE2 in pre-2021 design docs, but
*   build_epa_annual.py reads from same position 44-45 and names it 'anore' for all years.
***********
gen byte migrantiguo5_ci = .
replace  migrantiguo5_ci = 1 if migrante_ci == 1 & anore >= 5 & anore < 99
replace  migrantiguo5_ci = 0 if migrante_ci == 1 & anore <  5 & anore != .

***********
* mig_pais_ci — country of birth for migrants (string name)
* paina1 uses ISO 3166-1 numeric codes (3-digit).
* VERIFY: run [tab paina1] after the script and cross-check unexpected codes against
*         INE "Clasificación de Países" if any top-origin countries are missing.
***********
gen str40 mig_pais_ci = ""

* LAC origin countries (INE Clasificacion de Paises — NOT ISO 3166-1)
* Corrected 2026-05-01: original script used ISO codes; INE uses a different scheme.
* Reference: DISEÑO REGISTRO EPA-TRIM-2021.xlsx, sheet ANEXO-Codigos de Paises.
replace mig_pais_ci = "Venezuela"           if paina1 == 340 & migrante_ci == 1
replace mig_pais_ci = "Colombia"            if paina1 == 335 & migrante_ci == 1
replace mig_pais_ci = "Ecuador"             if paina1 == 336 & migrante_ci == 1
replace mig_pais_ci = "Bolivia"             if paina1 == 332 & migrante_ci == 1
replace mig_pais_ci = "Peru"                if paina1 == 338 & migrante_ci == 1
replace mig_pais_ci = "Argentina"           if paina1 == 331 & migrante_ci == 1
replace mig_pais_ci = "Dominican Republic"  if paina1 == 321 & migrante_ci == 1
replace mig_pais_ci = "Cuba"                if paina1 == 312 & migrante_ci == 1
replace mig_pais_ci = "Brazil"              if paina1 == 333 & migrante_ci == 1
replace mig_pais_ci = "Chile"               if paina1 == 334 & migrante_ci == 1
replace mig_pais_ci = "Paraguay"            if paina1 == 337 & migrante_ci == 1
replace mig_pais_ci = "Uruguay"             if paina1 == 339 & migrante_ci == 1
replace mig_pais_ci = "Honduras"            if paina1 == 316 & migrante_ci == 1
replace mig_pais_ci = "El Salvador"         if paina1 == 313 & migrante_ci == 1
replace mig_pais_ci = "Guatemala"           if paina1 == 314 & migrante_ci == 1
replace mig_pais_ci = "Nicaragua"           if paina1 == 318 & migrante_ci == 1
replace mig_pais_ci = "Mexico"              if paina1 == 317 & migrante_ci == 1
replace mig_pais_ci = "Costa Rica"          if paina1 == 311 & migrante_ci == 1
replace mig_pais_ci = "Panama"              if paina1 == 319 & migrante_ci == 1
replace mig_pais_ci = "Haiti"               if paina1 == 315 & migrante_ci == 1

* Major non-LAC origin countries (INE codes)
replace mig_pais_ci = "Morocco"             if paina1 == 207 & migrante_ci == 1
replace mig_pais_ci = "Romania"             if paina1 == 139 & migrante_ci == 1
replace mig_pais_ci = "China"               if paina1 == 401 & migrante_ci == 1
replace mig_pais_ci = "Ukraine"             if paina1 == 146 & migrante_ci == 1
replace mig_pais_ci = "Italy"               if paina1 == 123 & migrante_ci == 1
replace mig_pais_ci = "United Kingdom"      if paina1 == 136 & migrante_ci == 1
replace mig_pais_ci = "Germany"             if paina1 == 102 & migrante_ci == 1
replace mig_pais_ci = "France"              if paina1 == 117 & migrante_ci == 1
replace mig_pais_ci = "Portugal"            if paina1 == 135 & migrante_ci == 1
replace mig_pais_ci = "Senegal"             if paina1 == 208 & migrante_ci == 1
replace mig_pais_ci = "Pakistan"            if paina1 == 428 & migrante_ci == 1
replace mig_pais_ci = "Other"  if mig_pais_ci == "" & migrante_ci == 1


/*===========================================================
  SECTION 4 — EMPLOYMENT STATUS
  Applied to working-age population 16–64 (HDMF standard).
  EPA collects for all 16+; those 65+ get missing condocup.
===========================================================*/

***********
* condocup_ci
* Employed:    trarem==1 (worked for pay) OR ayudfa==1 (unpaid family)
*              OR ausent==1 (absent but has a job)
* Unemployed:  not employed AND busca==1 (searched last 4 weeks)
*              AND desea==1 (wants to work)
*              NOTE: ILO definition also requires DISP (availability), not extracted
*              by build_epa_annual.py — minor approximation only.
* Inactive:    not employed and not unemployed, within 16-64
***********
gen byte condocup_ci = .
replace  condocup_ci = 1 if (trarem == 1 | ayudfa == 1 | ausent == 1)
* EPA 2021 redesign: busca and desea are mutually exclusive (busca==1 always has desea!=1).
* Using busca==1 alone is the correct ILO criterion for active job search.
replace  condocup_ci = 2 if condocup_ci == . & busca == 1
replace  condocup_ci = 3 if condocup_ci == . & inrange(edad_ci, 16, 64)
replace  condocup_ci = . if !inrange(edad_ci, 16, 64)

label define condocup_lb 1 "Employed" 2 "Unemployed" 3 "Inactive"
label values condocup_ci condocup_lb

***********
* emp_ci
***********
gen byte emp_ci = .
replace  emp_ci = (condocup_ci == 1) if condocup_ci != .

***********
* desemp_ci
***********
gen byte desemp_ci = .
replace  desemp_ci = (condocup_ci == 2) if condocup_ci != .

***********
* pea_ci
***********
gen byte pea_ci = .
replace  pea_ci = 1 if inlist(condocup_ci, 1, 2)
replace  pea_ci = 0 if condocup_ci == 3


/*===========================================================
  SECTION 5 — JOB CHARACTERISTICS (emp_ci == 1 only)
===========================================================*/

***********
* cotizando_ci / afiliado_ci — NOT AVAILABLE from EPA
***********
gen byte cotizando_ci = .
gen byte afiliado_ci  = .
label var cotizando_ci "SS contribution — NOT AVAILABLE from EPA"
label var afiliado_ci  "SS affiliation  — NOT AVAILABLE from EPA"

***********
* formal_ci — structural proxy using SITU (situación profesional)
* EPA 2021+ actual SITU codes (from DISEÑO REGISTRO EPA-TRIM-2021.xlsx):
*   01 = Empresario con asalariados (employer with employees)
*   03 = Trabajador independiente / autónomo (own-account; formally registered in SS)
*   05 = Miembro de cooperativa
*   06 = Ayuda en empresa/negocio familiar (unpaid family worker)
*   07 = Asalariado sector público
*   08 = Asalariado sector privado
*   09 = Otra situación
* NOTE 2026-05-01: Original script used wrong codes (11,12,21... from an older design doc).
*   The merged DTA stores these as 1-digit integers (leading zero dropped by Stata).
*   Corrected to match actual data values.
* Proxy: employer/self-employed/cooperative/employee = formal; unpaid family/other = informal
***********
gen byte formal_ci = .
replace  formal_ci = 1 if emp_ci == 1 & inlist(situ, 1, 3, 5, 7, 8)
replace  formal_ci = 0 if emp_ci == 1 & inlist(situ, 6, 9)
label var formal_ci "Formal employment (SITU proxy: 1/3/5/7/8=formal, 6/9=informal)"

***********
* tipocontrato_ci
* DUCON1: 1=indefinite/permanent, 2=temporary
* Self-employed (11, 12) and unpaid family (41): no written wage contract
***********
gen byte tipocontrato_ci = .
replace  tipocontrato_ci = 1 if emp_ci == 1 & ducon1 == 1                  // permanent
replace  tipocontrato_ci = 2 if emp_ci == 1 & ducon1 == 2                  // temporary
replace  tipocontrato_ci = 3 if emp_ci == 1 & inlist(situ, 3, 6) & ducon1 == .  // no wage contract

label define tcontrato_lb 1 "Permanent/indefinite" 2 "Temporary" 3 "No contract"
label values tipocontrato_ci tcontrato_lb

***********
* horaspri_ci — usual hours worked in main job (HORASH1, 2021+ waves)
* QA fix 2026-05-04: horase = effective reference-week hours (inflates parcial_ci to ~36%)
*   horash1 = usual/habitual hours → correct ~16% part-time, matches official ESP rate
***********
gen double horaspri_ci = .
replace    horaspri_ci = horash1 if emp_ci == 1

***********
* horastot_ci — total weekly hours (main + second job)
* traplu==1 flags workers with a second job; horeplu = effective hours in second job
***********
gen double horastot_ci = .
replace    horastot_ci = horase               if emp_ci == 1
replace    horastot_ci = horase + horeplu     if emp_ci == 1 & traplu == 1 & horeplu != .

***********
* parcial_ci
***********
gen byte parcial_ci = .
replace parcial_ci = (horaspri_ci < 35) if emp_ci == 1 & horaspri_ci != .
label define parcial_lb 1 "Parcial (<35h)" 0 "Completo (>=35h)"
label values parcial_ci parcial_lb
label var parcial_ci "1 = trabajador a tiempo parcial (horaspri_ci < 35h)"


/*===========================================================
  SECTION 6 — EDUCATION
  NFORMA: highest completed education level — CNED-2014 codes (2-digit)
  Valid for all 2018-2025 waves (code 38 added in Q2-2016).

  CNED-2014 → HDMF mapping (verify against DISEÑO REGISTRO EPA-TRIM-2021.xlsx
  if unexpected values appear after running — tab nforma):
  ─────────────────────────────────────────────────────────────
  Code │ Description                        │ aedu │ ISCED │ hdmf
  ─────┼────────────────────────────────────┼──────┼───────┼─────
   10  │ Analfabeto / educación preescolar  │  0   │  0    │  1
   11  │ Sin estudios (sabe leer)           │  0   │  0    │  1
   20  │ Primaria incompleta                │  3   │  1    │  2
   21  │ Primaria completa (Grad. Escolar)  │  6   │  1    │  3
   31  │ Primera etapa ESO incompleta       │  8   │  2    │  4
   32  │ ESO completa                       │ 10   │  2    │  5
   35  │ FP básica                          │ 10   │  2    │  5
   38  │ 2ª etapa secundaria sin título     │ 11   │  3    │  6
   41  │ Bachillerato completo              │ 12   │  3    │  6
   43  │ CFGM (ciclo formativo grado medio) │ 12   │  3    │  6
   44  │ Otra 2ª etapa secundaria           │ 12   │  3    │  6
   51  │ Postsecundaria no terciaria        │ 13   │  4    │  7
   54  │ CFGS (ciclo formativo grado sup.)  │ 14   │  5    │  7
   60  │ Grado / Diplomatura / Licenciatura │ 16   │  6    │  9
   70  │ Máster universitario              │ 17   │  7    │ 10
   80  │ Doctorado                          │ 20   │  8    │ 10
  ─────────────────────────────────────────────────────────────
  NOTE: edu_hdmf 8 (university incomplete) is NOT derivable from NFORMA
  (NFORMA captures highest COMPLETED level only). Mark as missing.
===========================================================*/

***********
* aedu_ci — years of completed education
***********
gen byte aedu_ci = .
replace  aedu_ci =  0 if inlist(nforma, 10, 11)
replace  aedu_ci =  3 if nforma == 20
replace  aedu_ci =  6 if nforma == 21
replace  aedu_ci =  8 if nforma == 31
replace  aedu_ci = 10 if inlist(nforma, 32, 35)
replace  aedu_ci = 11 if nforma == 38
replace  aedu_ci = 12 if inlist(nforma, 41, 43, 44)
replace  aedu_ci = 13 if nforma == 51
replace  aedu_ci = 14 if nforma == 54
replace  aedu_ci = 16 if nforma == 60
replace  aedu_ci = 17 if nforma == 70
replace  aedu_ci = 20 if nforma == 80

***********
* edu_isced — ISCED 2011 attainment level
***********
gen byte edu_isced = .
replace  edu_isced = 0 if inlist(nforma, 10, 11)
replace  edu_isced = 1 if inlist(nforma, 20, 21)
replace  edu_isced = 2 if inlist(nforma, 31, 32, 35)
replace  edu_isced = 3 if inlist(nforma, 38, 41, 43, 44)
replace  edu_isced = 4 if nforma == 51
replace  edu_isced = 5 if nforma == 54
replace  edu_isced = 6 if nforma == 60
replace  edu_isced = 7 if nforma == 70
replace  edu_isced = 8 if nforma == 80

label define isced_lb ///
  0 "ISCED 0 Less than primary"          1 "ISCED 1 Primary" ///
  2 "ISCED 2 Lower secondary"            3 "ISCED 3 Upper secondary" ///
  4 "ISCED 4 Post-secondary non-tert."   5 "ISCED 5 Short-cycle tertiary" ///
  6 "ISCED 6 Bachelor or equivalent"     7 "ISCED 7 Master or equivalent" ///
  8 "ISCED 8 Doctoral or equivalent"
label values edu_isced isced_lb

***********
* edu_hdmf — HDMF education classification
***********
gen byte edu_hdmf = .
replace  edu_hdmf =  1 if inlist(nforma, 10, 11)         // no schooling
replace  edu_hdmf =  2 if nforma == 20                   // primary incomplete
replace  edu_hdmf =  3 if nforma == 21                   // primary complete
replace  edu_hdmf =  4 if nforma == 31                   // lower sec. incomplete
replace  edu_hdmf =  5 if inlist(nforma, 32, 35)         // lower sec. complete
replace  edu_hdmf =  6 if inlist(nforma, 38, 41, 43, 44) // upper secondary
replace  edu_hdmf =  7 if inlist(nforma, 51, 54)         // technical / post-secondary
* edu_hdmf = 8 (university incomplete): NOT DERIVABLE from NFORMA — left as missing
replace  edu_hdmf =  9 if nforma == 60                   // university complete
replace  edu_hdmf = 10 if inlist(nforma, 70, 80)         // postgraduate

label define edu_hdmf_lb ///
  1 "No schooling"            2 "Primary incomplete"  3 "Primary complete" ///
  4 "Lower sec. incomplete"   5 "Lower sec. complete" 6 "Upper secondary" ///
  7 "Technical/post-sec."     8 "University incompl." 9 "University complete" ///
  10 "Postgraduate"
label values edu_hdmf edu_hdmf_lb
label var edu_hdmf "HDMF education level (note: cat. 8 missing — not in NFORMA)"

/*===========================================================
  SECTION 6b — OCCUPATION & OVERQUALIFICATION
  cno11: CNO-2011 (Spanish occupational classification)
  Maps 1-to-1 with ISCO-08 at 1-digit level.
===========================================================*/

***********
* ocupa_ci
* cno11: CNO-2011 occupation code; maps 1-to-1 with ISCO-08 at 1-digit level
***********
gen byte ocupa_ci = .
replace ocupa_ci = real(substr(string(int(ocup)), 1, 1)) if emp_ci == 1 & !missing(ocup) & ocup > 0
label define ocupa_lbl 1 "Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary", replace
label values ocupa_ci ocupa_lbl
label var ocupa_ci "ISCO-08 major group (CNO-2011/ISCO-08 1-digit, 1-to-1 map)"

***********
* overqualified_ci
* edu_hdmf >= 7: ISCED5+ (10-level ESP scale: 7=technical, 9=university complete, 10=postgrad)
* NOTE: ESP edu_hdmf uses 10-level scale; threshold differs from LAC 8-level scale
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 7 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified", replace
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (ISCED5+ educ + low-skill occ, CNO-2011/ISCO-08 4-9)"


/*===========================================================
  SECTION 7 — INCOME
  EPA is a labor force survey; no income, remittance, or
  social security contribution data are collected.
  All income variables are set to missing.
===========================================================*/

gen double ylm_ci     = .
gen double ylnm_ci    = .
gen double ynlm_ci    = .
gen double ytot_ci    = .
gen double remesas_ci = .
gen double remesas_ch = .

label var ylm_ci     "Monthly labor income — NOT AVAILABLE from EPA"
label var ylnm_ci    "Non-monetary labor income — NOT AVAILABLE from EPA"
label var ynlm_ci    "Non-labor income — NOT AVAILABLE from EPA"
label var ytot_ci    "Total monthly income — NOT AVAILABLE from EPA"
label var remesas_ci "Individual remittances — NOT AVAILABLE from EPA"
label var remesas_ch "Household remittances — NOT AVAILABLE from EPA"


/*===========================================================
  SECTION 8 — CLEANUP & SAVE
===========================================================*/

* Drop records with missing household identifier (corrupt/filler rows)
drop if ccaa == . | prov == . | nvivi == .

compress
saveold "`base_out'", replace

log close
