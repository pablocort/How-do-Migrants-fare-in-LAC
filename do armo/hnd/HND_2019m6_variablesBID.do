*==============================================================================
* HND_2019m6_variablesBID.do
* Honduras EPHPM — June 2019
* HDMF harmonization script
* Differs from 2018: ce425cod for occupation, ine01 for region,
*   upm_ci=dominio, salmm=9443.24, migrante_ci=.
*==============================================================================
clear
set more off
di "File created with the Claude HDMF system — 2026-05-21"

local log_dir "do armo/hnd/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/HND_2019m6_variablesBID.log", replace

use "bases armo/raw/hnd/HND_2019m6.dta", clear

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
gen anio_c  = 2019
gen mes_c   = 6

local tc_c1 = 24.08
local salmm = 9443.24

*------------------------------------------------------------------------------
* Region / zone
*------------------------------------------------------------------------------
* depto = department code 1-18 (ine01 is not in 2019 raw data)
gen region_c = .
capture clonevar region_c = depto
label var region_c "Department (depto)"

* domi: 1=Tegucigalpa, 2=San Pedro Sula, 3=Other urban, 4=Rural
gen zona_c = .
replace zona_c = 1 if inlist(domi, 1, 2, 3)
replace zona_c = 0 if domi == 4
label var zona_c "Urban=1 Rural=0"

* upm_ci = dominio (available in 2019)
gen upm_ci = .
capture clonevar upm_ci = dominio
label var upm_ci "UPM / dominio"

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
clonevar sexo_ci = sexo
replace  sexo_ci = . if sexo_ci < 1 | sexo_ci > 2
label var sexo_ci "Sex: 1=male 2=female"

clonevar edad_ci = edad
replace  edad_ci = . if edad_ci < 0 | edad_ci > 120
label var edad_ci "Age in years"

gen relacion_ci = .
replace relacion_ci = 1 if rela_j == 1
replace relacion_ci = 2 if rela_j == 2
replace relacion_ci = 3 if inlist(rela_j, 3, 4)
replace relacion_ci = 4 if inlist(rela_j, 5, 6, 7, 8)
replace relacion_ci = 5 if rela_j == 9
replace relacion_ci = 6 if rela_j == 10
label var relacion_ci "Relationship to head"

bysort idh_ch: gen miembros_ci = _N
label var miembros_ci "Household members"

*------------------------------------------------------------------------------
* Migration — NOT available in 2019
*------------------------------------------------------------------------------
gen migrante_ci       = .
gen mig_pais_ci       = .
gen migrantiguo5_ci   = .
label var migrante_ci     "Migrant=1 (not available 2019)"
label var mig_pais_ci     "Country of birth (not available)"
label var migrantiguo5_ci "Migrated >5 years ago (not available)"

*------------------------------------------------------------------------------
* Employment
*------------------------------------------------------------------------------
gen condocup_ci = .
replace condocup_ci = 1 if (cp501==1 | cp504==1 | cp505==1) & edad_ci >= 10
replace condocup_ci = 4 if condocup_ci == . & !missing(cp501) & edad_ci >= 10
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
* Job category
*------------------------------------------------------------------------------
gen categopri_ci = .
replace categopri_ci = 1 if inlist(cp526, 1, 2, 3, 10) & emp_ci == 1
replace categopri_ci = 2 if inlist(cp526, 5, 7) & emp_ci == 1
replace categopri_ci = 3 if inlist(cp526, 4, 9) & emp_ci == 1
replace categopri_ci = 4 if inlist(cp526, 6, 8, 11) & emp_ci == 1
label var categopri_ci "Category primary: 1=emp 2=patron 3=self 4=unpaid"

gen categosec_ci = .
gen categoinac_ci = .
capture replace categoinac_ci = cp512 if condocup_ci == 4
gen tipocontrato_ci = .
label var tipocontrato_ci "Contract type (not available)"

*------------------------------------------------------------------------------
* Hours
*------------------------------------------------------------------------------
capture {
    gen horaspri_ci = rowtotal(cp522_dom cp522_lun cp522_mar cp522_mie cp522_jue cp522_vie cp522_sab)
    replace horaspri_ci = . if horaspri_ci > 168
    replace horaspri_ci = . if emp_ci != 1
}
if _rc {
    gen horaspri_ci = .
}

capture {
    gen horassec_ci = rowtotal(cp539dom cp539lun cp539mar cp539mie cp539jue cp539vie cp539sab)
    replace horassec_ci = . if horassec_ci > 168
    replace horassec_ci = . if emp_ci != 1
}
if _rc {
    gen horassec_ci = .
}

gen horastot_ci = .
capture replace horastot_ci = horaspri_ci + horassec_ci if emp_ci == 1
label var horaspri_ci  "Hours primary job"
label var horassec_ci  "Hours secondary job"
label var horastot_ci  "Total hours"

*------------------------------------------------------------------------------
* Occupation — ce425cod (CIUO-88 4-digit) — differs from 2018 (cp518cod)
*------------------------------------------------------------------------------
gen ocupa_ci = .
replace ocupa_ci = 1 if ce425cod >= 1000 & ce425cod <= 1999 & emp_ci == 1
replace ocupa_ci = 2 if ce425cod >= 2000 & ce425cod <= 2999 & emp_ci == 1
replace ocupa_ci = 3 if ce425cod >= 3000 & ce425cod <= 3999 & emp_ci == 1
replace ocupa_ci = 4 if ce425cod >= 4000 & ce425cod <= 4999 & emp_ci == 1
replace ocupa_ci = 5 if ce425cod >= 5000 & ce425cod <= 5999 & emp_ci == 1
replace ocupa_ci = 6 if ce425cod >= 6000 & ce425cod <= 6999 & emp_ci == 1
replace ocupa_ci = 7 if ce425cod >= 7000 & ce425cod <= 7999 & emp_ci == 1
replace ocupa_ci = 8 if ce425cod >= 8000 & ce425cod <= 8999 & emp_ci == 1
replace ocupa_ci = 9 if ce425cod >= 9000 & ce425cod <= 9999 & emp_ci == 1
label var ocupa_ci "Occupation 1-digit ISCO"

gen ramaop_ci = .
capture clonevar ramaop_ci = ramao
gen ramasec_ci = .
capture clonevar ramasec_ci = ramaos
gen tamemp_ci = .
label var ramaop_ci  "Industry primary"
label var ramasec_ci "Industry secondary"

*------------------------------------------------------------------------------
* Social security / formality
*------------------------------------------------------------------------------
gen cotizando_ci = 0 if emp_ci == 1
capture replace cotizando_ci = 1 if emp_ci == 1 & ///
    (inrange(cp517_1,1,5) | inrange(cp517_2,1,5) | inrange(cp517_3,1,5) | inrange(cp517_4,1,5))
label var cotizando_ci "Contributing to social security=1"

gen afiliado_ci  = .
gen formal_ci    = cotizando_ci if emp_ci == 1
label var formal_ci "Formal=1"

gen salmm_ci = `salmm'
label var salmm_ci "Monthly minimum wage (HNL)"

*------------------------------------------------------------------------------
* Education (same structure as 2018: cp407/cp410/cp412/cp417/cp409)
*------------------------------------------------------------------------------
gen aedu_ci = .
replace aedu_ci = 0  if inlist(cp407, 1, 2, 3)
replace aedu_ci = cp410         if cp407 == 4
replace aedu_ci = cp410 + 6     if cp407 == 5
replace aedu_ci = cp410 + 9     if cp407 == 6
replace aedu_ci = cp410 + 11    if inlist(cp407, 7, 8)
replace aedu_ci = cp410 + 11    if cp407 == 9
replace aedu_ci = cp410 + 15    if cp407 == 10

replace aedu_ci = cp417         if missing(aedu_ci) & cp412 == 4
replace aedu_ci = (cp417-1)+6   if missing(aedu_ci) & cp412 == 5
replace aedu_ci = (cp417-1)+9   if missing(aedu_ci) & cp412 == 6
replace aedu_ci = (cp417-1)+11  if missing(aedu_ci) & inlist(cp412,7,8)
replace aedu_ci = (cp417-1)+11  if missing(aedu_ci) & cp412 == 9
replace aedu_ci = (cp417-1)+15  if missing(aedu_ci) & cp412 == 10
replace aedu_ci = . if aedu_ci < 0
label var aedu_ci "Years of education"

gen eduui_ci = 0
replace eduui_ci = 1 if (inlist(cp407,7,8,9) & cp409==2) | inlist(cp412,7,8,9)
gen eduuc_ci = 0
replace eduuc_ci = 1 if (inlist(cp407,7,8,9) & cp409==1) | cp407==10 | cp412==10
gen edupre_ci = 0
capture replace edupre_ci = 1 if inlist(cp407,2,3) | inlist(cp412,2,3)
gen asiste_ci = .
capture clonevar asiste_ci = asiste
gen repiteult_ci    = .
gen razonesnoasis_ci = .
label var eduui_ci "Tertiary incomplete"
label var eduuc_ci "Tertiary complete"
label var edupre_ci "Pre-primary"

*------------------------------------------------------------------------------
* edu_hdmf
*------------------------------------------------------------------------------
gen edu_hdmf = .
replace edu_hdmf = 1  if inlist(cp407, 1, 2, 3)
replace edu_hdmf = 2  if cp407 == 4 & inrange(cp410, 1, 3)
replace edu_hdmf = 3  if cp407 == 4 & inrange(cp410, 4, 6)
replace edu_hdmf = 4  if cp407 == 5 & inrange(cp410, 1, 2)
replace edu_hdmf = 5  if cp407 == 5 & cp410 == 3
replace edu_hdmf = 6  if cp407 == 6
replace edu_hdmf = 7  if inlist(cp407, 7, 8)
replace edu_hdmf = 8  if cp407 == 9 & cp409 == 2
replace edu_hdmf = 9  if cp407 == 9 & cp409 == 1
replace edu_hdmf = 10 if cp407 == 10

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
* Income — same quarterly structure as 2018; /3 for monthly
*------------------------------------------------------------------------------
local tc = `tc_c1'

gen ylmpri_ci = .
capture gen ylmpri_ci = (ysmop + ycmop) / 3
replace ylmpri_ci = 0 if ylmpri_ci < 0 & emp_ci == 1
replace ylmpri_ci = . if emp_ci != 1

gen ylnmpri_ci = .
capture gen ylnmpri_ci = (yseop + yceop) / 3
replace ylnmpri_ci = 0 if ylnmpri_ci < 0 & emp_ci == 1
replace ylnmpri_ci = . if emp_ci != 1

gen ylmsec_ci = .
capture gen ylmsec_ci = (ysmos + ycmos) / 3
replace ylmsec_ci = 0 if ylmsec_ci < 0 & emp_ci == 1
replace ylmsec_ci = . if emp_ci != 1

gen ylnmsec_ci = .
capture gen ylnmsec_ci = (yseos + yceos) / 3
replace ylnmsec_ci = 0 if ylnmsec_ci < 0 & emp_ci == 1
replace ylnmsec_ci = . if emp_ci != 1

gen ylm_ci = .
replace ylm_ci = 0 if emp_ci == 1
capture replace ylm_ci = ylmpri_ci + ylmsec_ci if emp_ci == 1

gen ylnm_ci = .
replace ylnm_ci = 0 if emp_ci == 1
capture replace ylnm_ci = ylnmpri_ci + ylnmsec_ci if emp_ci == 1

label var ylmpri_ci  "Labor monetary primary (monthly HNL)"
label var ylnmpri_ci "Labor non-monetary primary"
label var ylmsec_ci  "Labor monetary secondary"
label var ylnmsec_ci "Labor non-monetary secondary"
label var ylm_ci     "Total labor monetary"
label var ylnm_ci    "Total labor non-monetary"

gen ynlm_ci = 0
capture replace ynlm_ci = ynlm_ci + oih01_lps/3 + oih01_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih02_lps/3 + oih02_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih03_lps/3 + oih03_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih04/3
capture replace ynlm_ci = ynlm_ci + oih05_lps/3 + oih05_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih06_lps/3 + oih06_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih07_lps/3 + oih07_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih08_lps/3 + oih08_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih09_lps/3 + oih09_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih10_lps/3 + oih10_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih11/3
capture replace ynlm_ci = ynlm_ci + oih12_lps/3 + oih12_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih13/3
capture replace ynlm_ci = ynlm_ci + oih14/3
capture replace ynlm_ci = ynlm_ci + oih15/3
replace ynlm_ci = . if ynlm_ci == 0 & missing(edad_ci)
label var ynlm_ci "Non-labor income (monthly HNL)"

gen remesas_ci = .
capture gen remesas_ci = (oih12_lps + oih12_lps_esp + oih12_us*`tc' + oih12_us_esp*`tc') / 3
replace remesas_ci = 0 if missing(remesas_ci)
replace remesas_ci = . if missing(edad_ci)

bysort idh_ch: egen remesas_ch = total(remesas_ci)
label var remesas_ci "Remittances (monthly HNL)"
label var remesas_ch "Household remittances"

gen ytot_ci = .
replace ytot_ci = 0 if !missing(edad_ci) & edad_ci >= 10
capture replace ytot_ci = ylm_ci + ylnm_ci + ynlm_ci + remesas_ci if edad_ci >= 10
label var ytot_ci "Total income (monthly HNL)"

*------------------------------------------------------------------------------
* Overqualified
*------------------------------------------------------------------------------
gen overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4
label var overqualified_ci "Overqualified=1"

*------------------------------------------------------------------------------
* Poverty / diversity / tc_c1
*------------------------------------------------------------------------------
gen lpe_ci = .
gen ln_ci  = .
gen pobre_ine_ci = .
gen bienestar_agregado = .
gen afro_ci = .
gen ind_ci  = .
gen dis_ci  = .

gen tc_c1 = `tc_c1'
label var tc_c1 "Exchange rate HNL/USD"

*------------------------------------------------------------------------------
* Order and save
*------------------------------------------------------------------------------
order pais_c anio_c mes_c idh_ch idp_ci factor_ci factor_ch ///
      zona_c region_c upm_ci ///
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
      overqualified_ci lpe_ci ln_ci pobre_ine_ci bienestar_agregado ///
      afro_ci ind_ci dis_ci tc_c1

saveold "bases armo/armo/HND/HND_2019m6_BID.dta", replace
di "HND_2019m6_BID.dta saved. N = " _N

log close
