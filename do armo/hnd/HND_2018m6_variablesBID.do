*==============================================================================
* HND_2018m6_variablesBID.do
* Honduras EPHPM — June 2018
* HDMF harmonization script
*==============================================================================
clear
set more off
di "File created with the Claude HDMF system — 2026-05-21"

local log_dir "do armo/hnd/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/HND_2018m6_variablesBID.log", replace

use "bases armo/raw/hnd/HND_2018m6.dta", clear

*------------------------------------------------------------------------------
* Rename loop — lowercase all variables
*------------------------------------------------------------------------------
foreach v of varlist _all {
    capture rename `v' `=lower("`v'")'
}

*------------------------------------------------------------------------------
* Country / time identifiers
*------------------------------------------------------------------------------
gen pais_c  = "HND"
gen anio_c  = 2018
gen mes_c   = 6

* Exchange rate (HNL per USD, June 2018) and minimum wage
local tc_c1   = 23.68
local salmm   = 8910.71

*------------------------------------------------------------------------------
* Region / zone
*------------------------------------------------------------------------------
* depto = department code 1-18
clonevar region_c = depto
label var region_c "Department (1-18)"

* municipio — available only in 2018
gen municipio_c = .
capture clonevar municipio_c = municipio
label var municipio_c "Municipality (2018 only)"

* domi: 1=Tegucigalpa, 2=San Pedro Sula, 3=Other urban, 4=Rural
gen zona_c = .
replace zona_c = 1 if inlist(domi, 1, 2, 3)
replace zona_c = 0 if domi == 4
label var zona_c "Urban=1 Rural=0"

gen upm_ci = .
label var upm_ci "UPM (not available 2018)"

*------------------------------------------------------------------------------
* Household and person identifiers
*------------------------------------------------------------------------------
tostring hogar, gen(idh_str) force
clonevar idh_ch = idh_str
label var idh_ch "Household ID"

tostring nper, gen(idp_str) force
gen idp_ci = idh_ch + "_" + idp_str
label var idp_ci "Person ID"
drop idh_str idp_str

*------------------------------------------------------------------------------
* Weights
*------------------------------------------------------------------------------
clonevar factor_ch = factor
clonevar factor_ci = factor
label var factor_ch "Household expansion factor"
label var factor_ci "Individual expansion factor"

*------------------------------------------------------------------------------
* Demographics
*------------------------------------------------------------------------------
clonevar sexo_ci  = sexo
replace  sexo_ci  = . if sexo_ci < 1 | sexo_ci > 2
label var sexo_ci "Sex: 1=male 2=female"

clonevar edad_ci  = edad
replace  edad_ci  = . if edad_ci < 0 | edad_ci > 120
label var edad_ci "Age in years"

* relacion_ci: 1=head, 2=spouse, 3=child, 4=other relative, 5=non-relative, 6=domestic worker
gen relacion_ci = .
replace relacion_ci = 1 if rela_j == 1
replace relacion_ci = 2 if rela_j == 2
replace relacion_ci = 3 if inlist(rela_j, 3, 4)
replace relacion_ci = 4 if inlist(rela_j, 5, 6, 7, 8)
replace relacion_ci = 5 if rela_j == 9
replace relacion_ci = 6 if rela_j == 10
label var relacion_ci "Relationship to head"

* Household size
bysort idh_ch: gen miembros_ci = _N
label var miembros_ci "Household members"

*------------------------------------------------------------------------------
* Migration
*------------------------------------------------------------------------------
* cd02_4 = country of birth (only in 2018)
gen migrante_ci = 0
replace migrante_ci = 1 if !missing(cd02_4) & cd02_4 != 1
replace migrante_ci = . if missing(edad_ci)
label var migrante_ci "Migrant=1 native=0"

gen mig_pais_ci = .
replace mig_pais_ci = cd02_4 if migrante_ci == 1
label var mig_pais_ci "Country of birth (migrants)"

gen migrantiguo5_ci = .
label var migrantiguo5_ci "Migrated >5 years ago (not available)"

*------------------------------------------------------------------------------
* Employment — condocup_ci
* cp501=worked last week, cp504=own-account business, cp505=family enterprise
* cp510=looked for work (unemployed)
*------------------------------------------------------------------------------
gen condocup_ci = .
replace condocup_ci = 1 if (cp501==1 | cp504==1 | cp505==1) & edad_ci >= 10
replace condocup_ci = 4 if condocup_ci == . & !missing(cp501) & edad_ci >= 10

* Cesante (previously employed) vs new entrant
replace condocup_ci = 2 if condocup_ci == 4 & cp510 == 1 & !missing(cp514)
replace condocup_ci = 3 if condocup_ci == 4 & cp510 == 1 & missing(cp514)

label var condocup_ci "Employment: 1=emp 2=ces 3=new_unem 4=inactive"

gen emp_ci    = (condocup_ci == 1) if !missing(condocup_ci)
gen desemp_ci = (inlist(condocup_ci, 2, 3)) if !missing(condocup_ci)
gen pea_ci    = (inlist(condocup_ci, 1, 2, 3)) if !missing(condocup_ci)
label var emp_ci    "Employed=1"
label var desemp_ci "Unemployed=1"
label var pea_ci    "Economically active=1"

*------------------------------------------------------------------------------
* Job category (primary)
* cp526: 1=public employee, 2=private employee, 3=domestic worker,
*        4=self-employed, 5=employer, 6=unpaid family, 7=employer(alt),
*        8=cooperative, 9=informal, 10=other employee, 11=other unpaid
*------------------------------------------------------------------------------
gen categopri_ci = .
replace categopri_ci = 1 if inlist(cp526, 1, 2, 3, 10) & emp_ci == 1  // employee
replace categopri_ci = 2 if inlist(cp526, 5, 7) & emp_ci == 1          // employer/patron
replace categopri_ci = 3 if inlist(cp526, 4, 9) & emp_ci == 1          // own-account
replace categopri_ci = 4 if inlist(cp526, 6, 8, 11) & emp_ci == 1      // unpaid
label var categopri_ci "Category primary job: 1=emp 2=patron 3=self 4=unpaid"

gen categosec_ci = .
label var categosec_ci "Category secondary job (not available)"

* Inactivity reason
gen categoinac_ci = .
capture replace categoinac_ci = cp512 if condocup_ci == 4
label var categoinac_ci "Reason inactive"

* Contract
gen tipocontrato_ci = .
label var tipocontrato_ci "Contract type (not available 2018)"

*------------------------------------------------------------------------------
* Hours worked
*------------------------------------------------------------------------------
* Day-of-week hours for primary job
capture {
    gen horaspri_ci = rowtotal(cp522_dom cp522_lun cp522_mar cp522_mie cp522_jue cp522_vie cp522_sab)
    replace horaspri_ci = . if horaspri_ci > 168
    replace horaspri_ci = . if emp_ci != 1
}
if _rc {
    gen horaspri_ci = .
}
label var horaspri_ci "Hours primary job (last week)"

capture {
    gen horassec_ci = rowtotal(cp539dom cp539lun cp539mar cp539mie cp539jue cp539vie cp539sab)
    replace horassec_ci = . if horassec_ci > 168
    replace horassec_ci = . if emp_ci != 1
}
if _rc {
    gen horassec_ci = .
}
label var horassec_ci "Hours secondary job"

gen horastot_ci = .
capture replace horastot_ci = horaspri_ci + horassec_ci if emp_ci == 1
label var horastot_ci "Total hours worked"

*------------------------------------------------------------------------------
* Occupation — ocupa_ci
* cp518cod: CIUO-88 4-digit codes → ocupa_ci 1-9
*------------------------------------------------------------------------------
gen ocupa_ci = .
replace ocupa_ci = 1 if cp518cod >= 1000 & cp518cod <= 1999 & emp_ci == 1
replace ocupa_ci = 2 if cp518cod >= 2000 & cp518cod <= 2999 & emp_ci == 1
replace ocupa_ci = 3 if cp518cod >= 3000 & cp518cod <= 3999 & emp_ci == 1
replace ocupa_ci = 4 if cp518cod >= 4000 & cp518cod <= 4999 & emp_ci == 1
replace ocupa_ci = 5 if cp518cod >= 5000 & cp518cod <= 5999 & emp_ci == 1
replace ocupa_ci = 6 if cp518cod >= 6000 & cp518cod <= 6999 & emp_ci == 1
replace ocupa_ci = 7 if cp518cod >= 7000 & cp518cod <= 7999 & emp_ci == 1
replace ocupa_ci = 8 if cp518cod >= 8000 & cp518cod <= 8999 & emp_ci == 1
replace ocupa_ci = 9 if cp518cod >= 9000 & cp518cod <= 9999 & emp_ci == 1
label var ocupa_ci "Occupation 1-digit ISCO (1=mgr..9=elem)"

* Industry (rama)
gen ramaop_ci = .
capture clonevar ramaop_ci = ramao
label var ramaop_ci "Industry primary job"

gen ramasec_ci = .
capture clonevar ramasec_ci = ramaos
label var ramasec_ci "Industry secondary job"

gen tamemp_ci = .
label var tamemp_ci "Firm size (not available)"

*------------------------------------------------------------------------------
* Social security / formality
* cp517_1 to cp517_4: 1=IHSS, 2=private insurance, 3=magnifica, 4=other
*------------------------------------------------------------------------------
gen cotizando_ci = 0 if emp_ci == 1
capture replace cotizando_ci = 1 if emp_ci == 1 & ///
    (inrange(cp517_1,1,5) | inrange(cp517_2,1,5) | inrange(cp517_3,1,5) | inrange(cp517_4,1,5))
label var cotizando_ci "Contributing to social security=1"

gen afiliado_ci = .
label var afiliado_ci "Health insurance (not distinguished)"

gen formal_ci = cotizando_ci if emp_ci == 1
label var formal_ci "Formal employment=1"

gen salmm_ci = `salmm'
label var salmm_ci "Monthly minimum wage (HNL)"

*------------------------------------------------------------------------------
* Education
* cp407: level NOT attending (last completed)
*   1=none, 2=prebásica incomplete, 3=prebásica complete,
*   4=primaria/básica(6yr), 5=ciclo común(3yr), 6=ciclo diversificado(3yr),
*   7=técnico incomplete, 8=técnico complete, 9=university, 10=postgrad
* cp410: grade within level (not attending)
* cp412: level currently attending; cp417: grade attending
* cp409: 1=complete 2=incomplete (for tertiary)
*------------------------------------------------------------------------------

* Years of education — not attending (last completed level)
gen aedu_ci = .
replace aedu_ci = 0 if inlist(cp407, 1, 2, 3)
replace aedu_ci = cp410         if cp407 == 4                    // primaria 1-6
replace aedu_ci = cp410 + 6     if cp407 == 5                    // ciclo común 7-9
replace aedu_ci = cp410 + 9     if cp407 == 6                    // diversificado 10-12
replace aedu_ci = cp410 + 11    if inlist(cp407, 7, 8)           // técnico 12-13
replace aedu_ci = cp410 + 11    if cp407 == 9 & cp409 == 2       // univ incomplete 12+
replace aedu_ci = cp410 + 11    if cp407 == 9 & cp409 == 1       // univ complete
replace aedu_ci = cp410 + 15    if cp407 == 10                   // postgrad 16+

* Currently attending — use if no "not attending" info
replace aedu_ci = cp417         if missing(aedu_ci) & cp412 == 4                  // primaria
replace aedu_ci = (cp417 - 1) + 6  if missing(aedu_ci) & cp412 == 5             // ciclo común
replace aedu_ci = (cp417 - 1) + 9  if missing(aedu_ci) & cp412 == 6             // diversificado
replace aedu_ci = (cp417 - 1) + 11 if missing(aedu_ci) & inlist(cp412, 7, 8)    // técnico
replace aedu_ci = (cp417 - 1) + 11 if missing(aedu_ci) & cp412 == 9             // university
replace aedu_ci = (cp417 - 1) + 15 if missing(aedu_ci) & cp412 == 10            // postgrad

replace aedu_ci = . if aedu_ci < 0
label var aedu_ci "Years of education"

* Tertiary education flags
gen eduui_ci = 0
replace eduui_ci = 1 if (inlist(cp407,7,8,9) & cp409==2) | inlist(cp412,7,8,9)
label var eduui_ci "Tertiary incomplete=1"

gen eduuc_ci = 0
replace eduuc_ci = 1 if (inlist(cp407,7,8,9) & cp409==1) | cp407==10 | cp412==10
label var eduuc_ci "Tertiary complete=1"

gen edupre_ci = 0
capture replace edupre_ci = 1 if inlist(cp407,2,3) | inlist(cp412,2,3)
label var edupre_ci "Pre-primary=1"

gen asiste_ci = .
capture clonevar asiste_ci = asiste
label var asiste_ci "Currently attending school=1"

gen repiteult_ci = .
label var repiteult_ci "Repeated last grade (not available)"

gen razonesnoasis_ci = .
label var razonesnoasis_ci "Reason for not attending school"

*------------------------------------------------------------------------------
* edu_hdmf — HDMF 10-level education (from cp407 level codes)
*------------------------------------------------------------------------------
gen edu_hdmf = .
* Use completed level (cp407) first
replace edu_hdmf = 1  if inlist(cp407, 1, 2, 3)                    // None/pre-primary
replace edu_hdmf = 2  if cp407 == 4 & inrange(cp410, 1, 3)        // Primary incomplete (1-3)
replace edu_hdmf = 3  if cp407 == 4 & inrange(cp410, 4, 6)        // Primary complete (4-6)
replace edu_hdmf = 4  if cp407 == 5 & inrange(cp410, 1, 2)        // Lower secondary inc
replace edu_hdmf = 5  if cp407 == 5 & cp410 == 3                   // Lower secondary comp
replace edu_hdmf = 6  if cp407 == 6                                 // Upper secondary
replace edu_hdmf = 7  if inlist(cp407, 7, 8)                       // Post-secondary non-tert
replace edu_hdmf = 8  if cp407 == 9 & cp409 == 2                   // Tertiary incomplete
replace edu_hdmf = 9  if cp407 == 9 & cp409 == 1                   // Tertiary complete
replace edu_hdmf = 10 if cp407 == 10                               // Postgrad

* Fill from currently attending level (cp412)
replace edu_hdmf = 1  if missing(edu_hdmf) & inlist(cp412, 1, 2, 3)
replace edu_hdmf = 2  if missing(edu_hdmf) & cp412 == 4 & inrange(cp417, 1, 3)
replace edu_hdmf = 3  if missing(edu_hdmf) & cp412 == 4 & inrange(cp417, 4, 6)
replace edu_hdmf = 4  if missing(edu_hdmf) & cp412 == 5 & inrange(cp417, 1, 2)
replace edu_hdmf = 5  if missing(edu_hdmf) & cp412 == 5 & cp417 == 3
replace edu_hdmf = 6  if missing(edu_hdmf) & cp412 == 6
replace edu_hdmf = 7  if missing(edu_hdmf) & inlist(cp412, 7, 8)
replace edu_hdmf = 8  if missing(edu_hdmf) & cp412 == 9
replace edu_hdmf = 10 if missing(edu_hdmf) & cp412 == 10
label var edu_hdmf "HDMF education level (1-10)"

*------------------------------------------------------------------------------
* edu_isced — ISCED 2011 from aedu_ci
*------------------------------------------------------------------------------
gen edu_isced = .
replace edu_isced = 0 if aedu_ci == 0
replace edu_isced = 1 if aedu_ci >= 1  & aedu_ci <= 6
replace edu_isced = 2 if aedu_ci >= 7  & aedu_ci <= 9
replace edu_isced = 3 if aedu_ci >= 10 & aedu_ci <= 12
replace edu_isced = 5 if aedu_ci >= 13 & aedu_ci <= 14
replace edu_isced = 6 if aedu_ci >= 15 & aedu_ci <= 16
replace edu_isced = 7 if aedu_ci >= 17 & !missing(aedu_ci)
label var edu_isced "ISCED-2011 level"

*------------------------------------------------------------------------------
* Income — primary job
* ysmop = salary monetary primary (quarterly), ycmop = commission monetary primary
* yseop = salary non-monetary primary, yceop = commission non-monetary primary
* Divide by 3: quarterly → monthly
*------------------------------------------------------------------------------
gen ylmpri_ci = .
capture gen ylmpri_ci = (ysmop + ycmop) / 3
replace ylmpri_ci = 0 if ylmpri_ci < 0 & emp_ci == 1
replace ylmpri_ci = . if emp_ci != 1
label var ylmpri_ci "Labor monetary income primary job (monthly HNL)"

gen ylnmpri_ci = .
capture gen ylnmpri_ci = (yseop + yceop) / 3
replace ylnmpri_ci = 0 if ylnmpri_ci < 0 & emp_ci == 1
replace ylnmpri_ci = . if emp_ci != 1
label var ylnmpri_ci "Labor non-monetary income primary (monthly HNL)"

* Secondary job
gen ylmsec_ci = .
capture gen ylmsec_ci = (ysmos + ycmos) / 3
replace ylmsec_ci = 0 if ylmsec_ci < 0 & emp_ci == 1
replace ylmsec_ci = . if emp_ci != 1
label var ylmsec_ci "Labor monetary income secondary job"

gen ylnmsec_ci = .
capture gen ylnmsec_ci = (yseos + yceos) / 3
replace ylnmsec_ci = 0 if ylnmsec_ci < 0 & emp_ci == 1
replace ylnmsec_ci = . if emp_ci != 1
label var ylnmsec_ci "Labor non-monetary income secondary job"

gen ylm_ci = .
replace ylm_ci = 0 if emp_ci == 1
capture replace ylm_ci = ylmpri_ci + ylmsec_ci if emp_ci == 1
label var ylm_ci "Total labor monetary income"

gen ylnm_ci = .
replace ylnm_ci = 0 if emp_ci == 1
capture replace ylnm_ci = ylnmpri_ci + ylnmsec_ci if emp_ci == 1
label var ylnm_ci "Total labor non-monetary income"

*------------------------------------------------------------------------------
* Income — non-labor (other income)
* oih variables divided by 3 (quarterly→monthly); USD converted via tc_c1
* Naming: *_lps = lempiras, *_us = dollars
*------------------------------------------------------------------------------
local tc = `tc_c1'

gen ynlm_ci = 0
* Pensions and retirement
capture replace ynlm_ci = ynlm_ci + oih01_lps/3 + oih01_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih02_lps/3 + oih02_us*`tc'/3
* Alquiler
capture replace ynlm_ci = ynlm_ci + oih03_lps/3 + oih03_us*`tc'/3
* Interest/dividends
capture replace ynlm_ci = ynlm_ci + oih04/3
* Assistance programs
capture replace ynlm_ci = ynlm_ci + oih05_lps/3 + oih05_us*`tc'/3
* Other transfers
capture replace ynlm_ci = ynlm_ci + oih06_lps/3 + oih06_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih07_lps/3 + oih07_us*`tc'/3
* Bonos/bonifications
capture replace ynlm_ci = ynlm_ci + oih08_lps/3 + oih08_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih09_lps/3 + oih09_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih10_lps/3 + oih10_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih11/3
* Remittances (included in ynlm here; also in remesas_ci below)
capture replace ynlm_ci = ynlm_ci + oih12_lps/3 + oih12_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih13/3
capture replace ynlm_ci = ynlm_ci + oih14/3
capture replace ynlm_ci = ynlm_ci + oih15/3
replace ynlm_ci = . if ynlm_ci == 0 & missing(edad_ci)
label var ynlm_ci "Non-labor income (monthly HNL)"

*------------------------------------------------------------------------------
* Remittances
*------------------------------------------------------------------------------
gen remesas_ci = .
capture gen remesas_ci = (oih12_lps + oih12_lps_esp + oih12_us*`tc' + oih12_us_esp*`tc') / 3
replace remesas_ci = 0 if missing(remesas_ci)
replace remesas_ci = . if missing(edad_ci)
label var remesas_ci "Remittances received (monthly HNL)"

* Household-level remittances
bysort idh_ch: egen remesas_ch = total(remesas_ci)
label var remesas_ch "Household total remittances"

*------------------------------------------------------------------------------
* Total income
*------------------------------------------------------------------------------
gen ytot_ci = .
replace ytot_ci = 0 if !missing(edad_ci) & edad_ci >= 10
capture replace ytot_ci = ylm_ci + ylnm_ci + ynlm_ci + remesas_ci if edad_ci >= 10
label var ytot_ci "Total individual income (monthly HNL)"

*------------------------------------------------------------------------------
* Overqualified
*------------------------------------------------------------------------------
gen overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4
label var overqualified_ci "Overqualified: tertiary+ in low-skill job=1"

*------------------------------------------------------------------------------
* Poverty / welfare
*------------------------------------------------------------------------------
gen lpe_ci = .
gen ln_ci  = .
gen pobre_ine_ci = .
gen bienestar_agregado = .
label var lpe_ci            "Extreme poverty line (HNL/month per capita)"
label var ln_ci             "Poverty line (HNL/month per capita)"
label var pobre_ine_ci      "Poor by INE criterion"
label var bienestar_agregado "Welfare aggregate per capita"

*------------------------------------------------------------------------------
* Diversity
*------------------------------------------------------------------------------
gen afro_ci = .
gen ind_ci  = .
gen dis_ci  = .
label var afro_ci "Afro-descendant=1"
label var ind_ci  "Indigenous=1"
label var dis_ci  "Has disability=1"

*------------------------------------------------------------------------------
* tc_c1 scalar
*------------------------------------------------------------------------------
gen tc_c1 = `tc_c1'
label var tc_c1 "Exchange rate HNL/USD"

*------------------------------------------------------------------------------
* Drop and reorder
*------------------------------------------------------------------------------
order pais_c anio_c mes_c idh_ch idp_ci factor_ci factor_ch ///
      zona_c region_c municipio_c upm_ci ///
      edad_ci sexo_ci relacion_ci miembros_ci ///
      migrante_ci mig_pais_ci migrantiguo5_ci ///
      condocup_ci emp_ci desemp_ci pea_ci ///
      categopri_ci categosec_ci categoinac_ci tipocontrato_ci ///
      horaspri_ci horassec_ci horastot_ci ///
      cotizando_ci afiliado_ci formal_ci salmm_ci ///
      ocupa_ci ramaop_ci ramasec_ci tamemp_ci ///
      aedu_ci eduui_ci eduuc_ci edupre_ci asiste_ci edu_hdmf edu_isced ///
      ylmpri_ci ylnmpri_ci ylmsec_ci ylnmsec_ci ylm_ci ylnm_ci ///
      ynlm_ci remesas_ci remesas_ch ytot_ci ///
      overqualified_ci ///
      lpe_ci ln_ci pobre_ine_ci bienestar_agregado ///
      afro_ci ind_ci dis_ci tc_c1

*------------------------------------------------------------------------------
* Save
*------------------------------------------------------------------------------
save "bases armo/armo/HND/HND_2018m6_BID.dta", replace
di "HND_2018m6_BID.dta saved. N = " _N

log close
