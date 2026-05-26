*==============================================================================
* HND_2021m6_variablesBID.do
* Honduras EPHPM — June 2021
* HDMF harmonization script
* TRANSITIONAL WAVE: ch03/ch04/ch02 demographics; categop employment;
*   aedu_ci=.; edu_hdmf=.; income NOT divided by 3 (already monthly);
*   dominio 1-3=urban (differs from 2022+ where 1-4=urban);
*   idp_ci = string(hogar)+string(nper)
*==============================================================================
clear
set more off
di "File created with the Claude HDMF system — 2026-05-21"

local log_dir "do armo/hnd/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/HND_2021m6_variablesBID.log", replace

use "bases armo/raw/hnd/HND_2021m6.dta", clear

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
gen anio_c  = 2021
gen mes_c   = 6

* TODO: confirm minimum wage; approximate value for 2021
local salmm = 10652.64
local tc_c1 = 24.50

*------------------------------------------------------------------------------
* Region / zone
*------------------------------------------------------------------------------
* dominio in 2021: 1=Francisco Morazan, 2=Cortes, 3=Ciudades medianas,
*   4=Ciudades pequeñas, 5=Rural
* Urban = dominio 1, 2, 3 (differs from 2022+ which treats 1-4 as urban)
gen region_c = .
capture replace region_c = dominio
label var region_c "Domain region (1-5)"

gen zona_c = .
replace zona_c = 1 if inlist(dominio, 1, 2, 3)
replace zona_c = 0 if inlist(dominio, 4, 5)
label var zona_c "Urban=1 Rural=0 (1-3=urban in 2021)"

gen upm_ci = .
capture replace upm_ci = dominio
label var upm_ci "UPM / dominio"

*------------------------------------------------------------------------------
* Household and person identifiers
*------------------------------------------------------------------------------
* idh_ch from hogar (tostring)
tostring hogar, gen(hogar_str)
clonevar idh_ch = hogar_str
label var idh_ch "Household ID"

* idp_ci = concatenate hogar + nper (person within household)
tostring nper, gen(nper_str)
gen idp_ci = hogar_str + nper_str
label var idp_ci "Person ID"
drop hogar_str nper_str

*------------------------------------------------------------------------------
* Weights
*------------------------------------------------------------------------------
gen factor_ch = .
gen factor_ci = .
capture replace factor_ch = factor
capture replace factor_ci = factor
label var factor_ch "Household expansion factor"
label var factor_ci "Individual expansion factor"

*------------------------------------------------------------------------------
* Demographics — 2021 uses ch03/ch04/ch02
*------------------------------------------------------------------------------
gen sexo_ci = .
capture replace sexo_ci = ch03
replace sexo_ci = . if sexo_ci < 1 | sexo_ci > 2
label var sexo_ci "Sex: 1=male 2=female"

gen edad_ci = .
capture replace edad_ci = ch04
replace edad_ci = . if edad_ci < 0 | edad_ci > 120
label var edad_ci "Age in years"

* ch02: relationship to head
gen relacion_ci = .
capture {
    replace relacion_ci = 1 if ch02 == 1
    replace relacion_ci = 2 if ch02 == 2
    replace relacion_ci = 3 if inlist(ch02, 3, 4)
    replace relacion_ci = 4 if inlist(ch02, 5, 6, 7, 8)
    replace relacion_ci = 5 if ch02 == 9
    replace relacion_ci = 6 if ch02 == 10
}
label var relacion_ci "Relationship to head"

bysort idh_ch: gen miembros_ci = _N
label var miembros_ci "Household members"

*------------------------------------------------------------------------------
* Migration — NOT available in 2021
*------------------------------------------------------------------------------
gen migrante_ci     = .
gen mig_pais_ci     = .
gen migrantiguo5_ci = .
label var migrante_ci     "Migrant=1 (not available 2021)"
label var mig_pais_ci     "Country of birth (not available)"
label var migrantiguo5_ci "Migrated >5 years ago (not available)"

*------------------------------------------------------------------------------
* Employment — 2021 uses categop (not condact)
* categop present → employed; cesante via ed043
*------------------------------------------------------------------------------
gen condocup_ci = .
replace condocup_ci = 1 if !missing(categop) & edad_ci >= 10
replace condocup_ci = 4 if condocup_ci == . & edad_ci >= 10

* Cesante: previously employed, now looking for work
capture replace condocup_ci = 2 if condocup_ci == 4 & ed043 == 1
label var condocup_ci "Employment: 1=emp 2=ces 3=new_unem 4=inactive"

gen emp_ci    = (condocup_ci == 1) if !missing(condocup_ci)
gen desemp_ci = (inlist(condocup_ci, 2, 3)) if !missing(condocup_ci)
gen pea_ci    = (inlist(condocup_ci, 1, 2, 3)) if !missing(condocup_ci)
label var emp_ci    "Employed=1"
label var desemp_ci "Unemployed=1"
label var pea_ci    "Economically active=1"

*------------------------------------------------------------------------------
* Job category (primary) — categop
* Values similar to cp526 in 2018-2019
*------------------------------------------------------------------------------
gen categopri_ci = .
replace categopri_ci = 1 if inlist(categop, 1, 2, 3, 10) & emp_ci == 1
replace categopri_ci = 2 if inlist(categop, 5, 7) & emp_ci == 1
replace categopri_ci = 3 if inlist(categop, 4, 9) & emp_ci == 1
replace categopri_ci = 4 if inlist(categop, 6, 8, 11) & emp_ci == 1
label var categopri_ci "Category primary: 1=emp 2=patron 3=self 4=unpaid"

gen categosec_ci  = .
gen categoinac_ci = .
gen tipocontrato_ci = .

*------------------------------------------------------------------------------
* Hours — NOT available in 2021
*------------------------------------------------------------------------------
gen horaspri_ci  = .
gen horassec_ci  = .
gen horastot_ci  = .
label var horaspri_ci "Hours primary (not available 2021)"
label var horastot_ci "Total hours (not available 2021)"

*------------------------------------------------------------------------------
* Occupation — NOT available in 2021
*------------------------------------------------------------------------------
gen ocupa_ci   = .
gen ramaop_ci  = .
gen ramasec_ci = .
gen tamemp_ci  = .
label var ocupa_ci "Occupation (not available 2021)"

*------------------------------------------------------------------------------
* Social security / formality
* cotizando_ci from oih01_lps or oih01_us presence
*------------------------------------------------------------------------------
gen cotizando_ci = .
capture {
    gen cotizando_ci = 0 if emp_ci == 1
    replace cotizando_ci = 1 if emp_ci == 1 & (oih01_lps > 0 | oih01_us > 0) & ///
        (!missing(oih01_lps) | !missing(oih01_us))
}
label var cotizando_ci "Contributing to social security=1"

gen afiliado_ci = .
capture {
    gen afiliado_ci = 0 if !missing(edad_ci)
    replace afiliado_ci = 1 if !missing(oih01_lps) & oih01_lps > 0
}
label var afiliado_ci "Health insurance affiliation=1"

gen formal_ci = .
replace formal_ci = 0 if emp_ci == 1
replace formal_ci = 1 if emp_ci == 1 & (cotizando_ci == 1 | afiliado_ci == 1)
label var formal_ci "Formal employment=1"

gen salmm_ci = `salmm'
label var salmm_ci "Monthly minimum wage (HNL)"

*------------------------------------------------------------------------------
* Education — NOT available in 2021 (no cp407/ed05 equivalent found)
* Use ed05x / ed08 / ed10 / ed13 if present
*------------------------------------------------------------------------------
gen aedu_ci = .
label var aedu_ci "Years of education (not available 2021)"

* Tertiary flags from 2021 education variables
gen eduui_ci = .
capture replace eduui_ci = 1 if ed053 == 1 & ed054 == 0
capture replace eduui_ci = 0 if (ed053 == 0 | ed054 == 1) & !missing(edad_ci)

gen eduuc_ci = .
capture replace eduuc_ci = 1 if ed054 == 1
capture replace eduuc_ci = 0 if ed054 == 0 & !missing(edad_ci)

gen edupre_ci = .
capture replace edupre_ci = 1 if ed051 == 1
capture replace edupre_ci = 0 if ed051 == 0 & !missing(edad_ci)

gen asiste_ci = .
capture replace asiste_ci = ed03
gen repiteult_ci     = .
gen razonesnoasis_ci = .
label var eduui_ci "Tertiary incomplete"
label var eduuc_ci "Tertiary complete"
label var edupre_ci "Pre-primary"

*------------------------------------------------------------------------------
* edu_hdmf — NOT available (aedu_ci missing)
*------------------------------------------------------------------------------
gen edu_hdmf = .
label var edu_hdmf "HDMF education level (not available 2021)"

gen edu_isced = .
label var edu_isced "ISCED-2011 (not available 2021)"

*------------------------------------------------------------------------------
* Income — 2021: already monthly (no /3 division)
* ysmop/ycmop for primary; ysmos/ycmos for secondary
*------------------------------------------------------------------------------
gen ylmpri_ci = .
capture gen ylmpri_ci = ysmop + ycmop
replace ylmpri_ci = 0 if ylmpri_ci < 0 & emp_ci == 1
replace ylmpri_ci = . if emp_ci != 1
label var ylmpri_ci "Labor monetary primary (monthly HNL)"

gen ylnmpri_ci = .
capture gen ylnmpri_ci = yseop + yceop
replace ylnmpri_ci = 0 if ylnmpri_ci < 0 & emp_ci == 1
replace ylnmpri_ci = . if emp_ci != 1
label var ylnmpri_ci "Labor non-monetary primary"

gen ylmsec_ci = .
capture gen ylmsec_ci = ysmos + ycmos
replace ylmsec_ci = 0 if ylmsec_ci < 0 & emp_ci == 1
replace ylmsec_ci = . if emp_ci != 1
label var ylmsec_ci "Labor monetary secondary"

gen ylnmsec_ci = .
capture gen ylnmsec_ci = yseos + yceos
replace ylnmsec_ci = 0 if ylnmsec_ci < 0 & emp_ci == 1
replace ylnmsec_ci = . if emp_ci != 1
label var ylnmsec_ci "Labor non-monetary secondary"

gen ylm_ci = .
replace ylm_ci = 0 if emp_ci == 1
capture replace ylm_ci = ylmpri_ci + ylmsec_ci if emp_ci == 1

gen ylnm_ci = .
replace ylnm_ci = 0 if emp_ci == 1
capture replace ylnm_ci = ylnmpri_ci + ylnmsec_ci if emp_ci == 1

label var ylm_ci  "Total labor monetary"
label var ylnm_ci "Total labor non-monetary"

* Non-labor income — 2021: already monthly (no /3); add USD variants via tc_c1
local tc = `tc_c1'
gen ynlm_ci = 0
capture replace ynlm_ci = ynlm_ci + oih01_lps + oih01_us*`tc'
capture replace ynlm_ci = ynlm_ci + oih02_lps + oih02_us*`tc'
capture replace ynlm_ci = ynlm_ci + oih03_lps + oih03_us*`tc'
capture replace ynlm_ci = ynlm_ci + oih04
capture replace ynlm_ci = ynlm_ci + oih05_lps + oih05_us*`tc'
capture replace ynlm_ci = ynlm_ci + oih06_lps + oih06_us*`tc'
capture replace ynlm_ci = ynlm_ci + oih07_lps + oih07_us*`tc'
capture replace ynlm_ci = ynlm_ci + oih11
capture replace ynlm_ci = ynlm_ci + oih12_lps + oih12_us*`tc'
capture replace ynlm_ci = ynlm_ci + oih13
capture replace ynlm_ci = ynlm_ci + oih14
capture replace ynlm_ci = ynlm_ci + oih15
capture replace ynlm_ci = ynlm_ci + oih16_lps + oih16_us*`tc'
replace ynlm_ci = . if ynlm_ci == 0 & missing(edad_ci)
label var ynlm_ci "Non-labor income (monthly HNL)"

* Remittances — 2021: already monthly (no /3); add USD variants
gen remesas_ci = .
capture replace remesas_ci =oih12_lps + oih12_lps_esp + oih12_us*`tc_c1' + oih12_us_esp*`tc_c1'
replace remesas_ci = 0 if missing(remesas_ci) & !missing(edad_ci)
replace remesas_ci = . if missing(edad_ci)

bysort idh_ch: egen remesas_ch = total(remesas_ci)
label var remesas_ci "Remittances (monthly HNL)"
label var remesas_ch "Household remittances"

gen ytot_ci = .
replace ytot_ci = 0 if !missing(edad_ci) & edad_ci >= 10
capture replace ytot_ci = ylm_ci + ylnm_ci + ynlm_ci + remesas_ci if edad_ci >= 10
label var ytot_ci "Total income (monthly HNL)"

*------------------------------------------------------------------------------
* Overqualified — not available (aedu_ci missing)
*------------------------------------------------------------------------------
gen overqualified_ci = .
label var overqualified_ci "Overqualified (not available 2021)"

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
label var tc_c1 "Exchange rate HNL/USD (approx 2021)"

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

save "bases armo/armo/HND/HND_2021m6_BID.dta", replace
di "HND_2021m6_BID.dta saved. N = " _N

log close
