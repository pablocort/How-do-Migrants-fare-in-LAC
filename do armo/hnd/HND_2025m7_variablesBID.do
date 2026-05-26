*==============================================================================
* HND_2025m7_variablesBID.do
* Honduras EPHPM — July 2025
* HDMF harmonization script
* Clone of 2024m6: CONDACT uppercase; depmuestra; tothrsop/thoras;
*   ynlm_ci=.; remesas_ci=.
* Differences: anio_c=2025; mes_c=7; updated salmm/tc_c1
*==============================================================================
clear
set more off
di "File created with the Claude HDMF system — 2026-05-21"

local log_dir "do armo/hnd/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/HND_2025m7_variablesBID.log", replace

use "bases armo/raw/hnd/HND_2025m7.dta", clear

*------------------------------------------------------------------------------
* Rename loop — lowercase all variables (2025m7 raw uses uppercase names)
*------------------------------------------------------------------------------
foreach v of varlist _all {
    capture rename `v' `=lower("`v'")'
}

*------------------------------------------------------------------------------
* Country / time identifiers
*------------------------------------------------------------------------------
gen pais_c  = "HND"
gen anio_c  = 2025
gen mes_c   = 7

* TODO: confirm July 2025 minimum wage and exchange rate
local tc_c1 = 26.00
local salmm = 14000.00

*------------------------------------------------------------------------------
* Region / zone
*------------------------------------------------------------------------------
gen region_c = .
capture clonevar region_c = depto
label var region_c "Department (depto)"

gen zona_c = .
replace zona_c = 1 if inlist(dominio, 1, 2, 3, 4)
replace zona_c = 0 if dominio == 5
label var zona_c "Urban=1 Rural=0"

gen upm_ci = .
capture clonevar upm_ci = dominio
label var upm_ci "UPM / dominio"

*------------------------------------------------------------------------------
* Household and person identifiers
* hogar is float64 in 2025 — use force to convert; nper is person number
*------------------------------------------------------------------------------
tostring hogar, gen(hogar_str) force
clonevar idh_ch = hogar_str
label var idh_ch "Household ID"

tostring nper, gen(nper_str) force
gen idp_ci = hogar_str + "_" + nper_str
label var idp_ci "Person ID (hogar+nper)"
drop hogar_str nper_str

*------------------------------------------------------------------------------
* Weights
*------------------------------------------------------------------------------
gen factor_ch = .
gen factor_ci = .
capture clonevar factor_ch = factor
capture clonevar factor_ci = factor
label var factor_ch "Household expansion factor"
label var factor_ci "Individual expansion factor"

*------------------------------------------------------------------------------
* Demographics
*------------------------------------------------------------------------------
gen sexo_ci = .
capture clonevar sexo_ci = sexo
replace sexo_ci = . if sexo_ci < 1 | sexo_ci > 2
label var sexo_ci "Sex: 1=male 2=female"

gen edad_ci = .
capture clonevar edad_ci = edad
replace edad_ci = . if edad_ci < 0 | edad_ci > 120
label var edad_ci "Age in years"

gen relacion_ci = .
capture {
    replace relacion_ci = 1 if rela_j == 1
    replace relacion_ci = 2 if rela_j == 2
    replace relacion_ci = 3 if inlist(rela_j, 3, 4)
    replace relacion_ci = 4 if inlist(rela_j, 5, 6, 7, 8)
    replace relacion_ci = 5 if rela_j == 9
    replace relacion_ci = 6 if rela_j == 10
}
label var relacion_ci "Relationship to head"

bysort idh_ch: gen miembros_ci = _N
label var miembros_ci "Household members"

*------------------------------------------------------------------------------
* Diversity
*------------------------------------------------------------------------------
gen dis_ci = .
capture {
    replace dis_ci = 1 if ch307 == 1
    replace dis_ci = 0 if ch307 == 2 & !missing(ch307)
}
gen afro_ci = .
gen ind_ci  = .
capture {
    replace afro_ci = 1 if inlist(ch308, 4, 5)
    replace afro_ci = 0 if !inlist(ch308, 4, 5) & !missing(ch308)
    replace ind_ci  = 1 if inrange(ch308, 1, 3)
    replace ind_ci  = 0 if !inrange(ch308, 1, 3) & !missing(ch308)
}
label var dis_ci  "Has disability=1"
label var afro_ci "Afro-descendant=1"
label var ind_ci  "Indigenous=1"

*------------------------------------------------------------------------------
* Migration — NOT available in 2025
*------------------------------------------------------------------------------
gen migrante_ci     = .
gen mig_pais_ci     = .
gen migrantiguo5_ci = .

*------------------------------------------------------------------------------
* Employment — CONDACT (check case in 2025 raw data)
*------------------------------------------------------------------------------
gen condocup_ci = .
capture clonevar condocup_ci = CONDACT
capture replace condocup_ci = CONDACT if missing(condocup_ci)
capture replace condocup_ci = condact if missing(condocup_ci)
replace condocup_ci = . if condocup_ci < 1 | condocup_ci > 4
replace condocup_ci = . if edad_ci < 10
label var condocup_ci "Employment: 1=emp 2=ces 3=new_unem 4=inactive"

gen emp_ci    = (condocup_ci == 1) if !missing(condocup_ci)
gen desemp_ci = (inlist(condocup_ci, 2, 3)) if !missing(condocup_ci)
gen pea_ci    = (inlist(condocup_ci, 1, 2, 3)) if !missing(condocup_ci)
label var emp_ci    "Employed=1"
label var desemp_ci "Unemployed=1"
label var pea_ci    "Economically active=1"

gen cesante_ci  = (condocup_ci == 2) if !missing(condocup_ci)
gen desalent_ci = .
capture replace desalent_ci = 1 if ca513 == 6
gen durades_ci = .
capture clonevar durades_ci = mesest

gen categoinac_ci = .
capture clonevar categoinac_ci = CA514

*------------------------------------------------------------------------------
* Job category — oc609
*------------------------------------------------------------------------------
gen categopri_ci = .
capture {
    replace categopri_ci = 1 if inlist(oc609, 1, 2, 3, 10) & emp_ci == 1
    replace categopri_ci = 2 if inlist(oc609, 5, 7) & emp_ci == 1
    replace categopri_ci = 3 if inlist(oc609, 4, 9) & emp_ci == 1
    replace categopri_ci = 4 if inlist(oc609, 6, 8, 11) & emp_ci == 1
}
gen categosec_ci    = .
gen tipocontrato_ci = .

*------------------------------------------------------------------------------
* Hours — tothrsop / thoras
*------------------------------------------------------------------------------
gen horaspri_ci = .
capture clonevar horaspri_ci = tothrsop
replace horaspri_ci = . if horaspri_ci > 168
replace horaspri_ci = . if emp_ci != 1
label var horaspri_ci "Hours primary job"

gen horassec_ci = .
label var horassec_ci "Hours secondary (not available)"

gen horastot_ci = .
capture clonevar horastot_ci = thoras
replace horastot_ci = . if horastot_ci > 336
replace horastot_ci = . if emp_ci != 1
label var horastot_ci "Total hours"

*------------------------------------------------------------------------------
* Occupation — ocupaop (ISCO-08 1-digit)
*------------------------------------------------------------------------------
gen ocupa_ci = .
capture clonevar ocupa_ci = ocupaop
replace ocupa_ci = . if ocupa_ci < 1 | ocupa_ci > 9
replace ocupa_ci = . if emp_ci != 1
label var ocupa_ci "Occupation 1-digit ISCO-08"

gen ramaop_ci  = .
capture clonevar ramaop_ci = ramao
gen ramasec_ci = .
gen tamemp_ci  = .
capture clonevar tamemp_ci = oc_608_cuantas

*------------------------------------------------------------------------------
* Formality — not available
*------------------------------------------------------------------------------
gen cotizando_ci = .
gen afiliado_ci  = .
gen formal_ci    = .

gen salmm_ci = `salmm'
label var salmm_ci "Monthly minimum wage (HNL, approx July 2025)"

*------------------------------------------------------------------------------
* Education — ed05/ed08/ed10/ed13
*------------------------------------------------------------------------------
gen aedu_ci = .
capture {
    replace aedu_ci = 0  if ed05 == 0 | ed05 == 1
    replace aedu_ci = ed08          if ed05 == 2 & inrange(ed08, 1, 9)
    replace aedu_ci = ed08 + 9      if ed05 == 3 & inrange(ed08, 1, 3)
    replace aedu_ci = ed08 + 9      if ed05 == 4 & inrange(ed08, 1, 3)
    replace aedu_ci = ed08 + 12     if ed05 == 5 & inrange(ed08, 1, 5)
    replace aedu_ci = ed08 + 17     if ed05 == 6 & inrange(ed08, 1, 3)
}
capture {
    replace aedu_ci = 0             if missing(aedu_ci) & ed10 == 1
    replace aedu_ci = (ed13-1)      if missing(aedu_ci) & ed10 == 2 & inrange(ed13,1,9)
    replace aedu_ci = (ed13-1)+9    if missing(aedu_ci) & ed10 == 3 & inrange(ed13,1,3)
    replace aedu_ci = (ed13-1)+9    if missing(aedu_ci) & ed10 == 4 & inrange(ed13,1,3)
    replace aedu_ci = (ed13-1)+12   if missing(aedu_ci) & ed10 == 5 & inrange(ed13,1,5)
    replace aedu_ci = (ed13-1)+17   if missing(aedu_ci) & ed10 == 6
}
replace aedu_ci = . if aedu_ci < 0
label var aedu_ci "Years of education"

gen eduui_ci = .
capture replace eduui_ci = 1 if (ed05==5 | ed10==5)
capture replace eduui_ci = 0 if missing(eduui_ci) & !missing(edad_ci)
gen eduuc_ci = .
capture replace eduuc_ci = 1 if ed05 == 5 & ed08 >= 4
capture replace eduuc_ci = 1 if ed05 == 6
capture replace eduuc_ci = 0 if missing(eduuc_ci) & !missing(edad_ci)
gen edupre_ci = .
capture replace edupre_ci = 1 if ed05 == 1 | ed10 == 1
capture replace edupre_ci = 0 if missing(edupre_ci) & !missing(edad_ci)
gen asiste_ci = .
capture clonevar asiste_ci = ed01
gen repiteult_ci = .
capture clonevar repiteult_ci = ed11
gen razonesnoasis_ci = .
capture clonevar razonesnoasis_ci = razonesnoasis

*------------------------------------------------------------------------------
* edu_hdmf from aedu_ci thresholds
*------------------------------------------------------------------------------
gen edu_hdmf = .
replace edu_hdmf = 1  if aedu_ci == 0
replace edu_hdmf = 2  if aedu_ci >= 1  & aedu_ci <= 5
replace edu_hdmf = 3  if aedu_ci == 6
replace edu_hdmf = 4  if aedu_ci >= 7  & aedu_ci <= 8
replace edu_hdmf = 5  if aedu_ci == 9
replace edu_hdmf = 6  if aedu_ci >= 10 & aedu_ci <= 12
replace edu_hdmf = 7  if aedu_ci >= 13 & aedu_ci <= 14
replace edu_hdmf = 8  if aedu_ci >= 15 & aedu_ci <= 16
replace edu_hdmf = 9  if aedu_ci >= 17 & aedu_ci <= 21
replace edu_hdmf = 10 if aedu_ci >= 22 & !missing(aedu_ci)
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
* Income — quarterly → /3
*------------------------------------------------------------------------------
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

label var ylmpri_ci "Labor monetary primary (monthly HNL)"
label var ylm_ci    "Total labor monetary"

* Non-labor income — OIH01–OIH21 available in 2025 (OIH21 is new); quarterly → /3
local tc = `tc_c1'
gen ynlm_ci = 0
capture replace ynlm_ci = ynlm_ci + oih01_lps/3 + oih01_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih02_lps/3 + oih02_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih03_lps/3 + oih03_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih04/3
capture replace ynlm_ci = ynlm_ci + oih05_lps/3 + oih05_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih06_lps/3 + oih06_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih06_lps_esp/3 + oih06_us_esp*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih07_lps/3 + oih07_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih07_lps_esp/3 + oih07_us_esp*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih08/3
capture replace ynlm_ci = ynlm_ci + oih09/3
capture replace ynlm_ci = ynlm_ci + oih10/3
capture replace ynlm_ci = ynlm_ci + oih11/3
capture replace ynlm_ci = ynlm_ci + oih12_lps/3 + oih12_us*`tc'/3
capture replace ynlm_ci = ynlm_ci + oih13/3
capture replace ynlm_ci = ynlm_ci + oih14/3
capture replace ynlm_ci = ynlm_ci + oih15/3
capture replace ynlm_ci = ynlm_ci + oih16/3
capture replace ynlm_ci = ynlm_ci + oih17/3
capture replace ynlm_ci = ynlm_ci + oih18/3
capture replace ynlm_ci = ynlm_ci + oih19_lps/3
capture replace ynlm_ci = ynlm_ci + oih20_lps/3
capture replace ynlm_ci = ynlm_ci + oih21_lps/3
replace ynlm_ci = . if ynlm_ci == 0 & missing(edad_ci)
label var ynlm_ci "Non-labor income (monthly HNL)"

gen remesas_ci = .
capture gen remesas_ci = (oih12_lps + oih12_lps_esp + oih12_us*`tc' + oih12_us_esp*`tc') / 3
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
* Overqualified
*------------------------------------------------------------------------------
gen overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4
label var overqualified_ci "Overqualified=1"

*------------------------------------------------------------------------------
* Poverty / tc_c1
*------------------------------------------------------------------------------
gen lpe_ci = .
gen ln_ci  = .
gen pobre_ine_ci       = .
gen bienestar_agregado = .
capture clonevar pobre_ine_ci      = pobreza
capture clonevar bienestar_agregado = yperhg
gen tc_c1 = `tc_c1'
label var tc_c1 "Exchange rate HNL/USD (approx July 2025)"

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

saveold "bases armo/armo/HND/HND_2025m7_BID.dta", replace
di "HND_2025m7_BID.dta saved. N = " _N

log close
