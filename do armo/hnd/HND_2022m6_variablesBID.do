*==============================================================================
* HND_2022m6_variablesBID.do
* Honduras EPHPM — June 2022
* HDMF harmonization script
* NEW STRUCTURE: condact; complex concat IDs; day-by-day hours;
*   ynlm_ci=.; remesas_ci=.; dominio 1-4=urban; region_c=.;
*   salmm=12377.73
*==============================================================================
clear
set more off
di "File created with the Claude HDMF system — 2026-05-21"

local log_dir "do armo/hnd/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/HND_2022m6_variablesBID.log", replace

use "bases armo/raw/hnd/HND_2022m6.dta", clear

* No rename loop in 2022 — variables already lowercase

*------------------------------------------------------------------------------
* Country / time identifiers
*------------------------------------------------------------------------------
gen pais_c  = "HND"
gen anio_c  = 2022
gen mes_c   = 6

local salmm = 12377.73
local tc_c1 = 24.49

*------------------------------------------------------------------------------
* Region / zone
*------------------------------------------------------------------------------
* No department variable in 2022
gen region_c = .
label var region_c "Department (not available 2022)"

* dominio 1-4=urban, 5=rural (different from 2021 where 1-3=urban)
gen zona_c = .
replace zona_c = 1 if inlist(dominio, 1, 2, 3, 4)
replace zona_c = 0 if dominio == 5
label var zona_c "Urban=1 Rural=0"

gen upm_ci = .
capture replace upm_ci = dominio
label var upm_ci "UPM / dominio"

*------------------------------------------------------------------------------
* Household and person identifiers
* Complex concat: idh_ch = hogar+num_hog+num_rec; idp_ci uses multiple vars
*------------------------------------------------------------------------------
capture tostring nper cor_pre dominio num_hog hogar num_rec, replace

gen str idh_ch = ""
capture replace idh_ch = hogar + num_hog + num_rec
label var idh_ch "Household ID (concat)"

* Long idp_ci to avoid duplicates; drop exact duplicate person records
gen     edad_ci_str = string(edad)
gen     sex_ci_str  = string(sexo)
gen     rela_ci_str = string(rela_j)
gen str idp_ci = idh_ch + nper + edad_ci_str + sex_ci_str + rela_ci_str
label var idp_ci "Person ID (concat)"
drop edad_ci_str sex_ci_str rela_ci_str

duplicates tag idp_ci, gen(dupIdp_ci)
drop if dupIdp_ci == 1
drop dupIdp_ci

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
* Demographics
*------------------------------------------------------------------------------
gen sexo_ci = .
capture replace sexo_ci = sexo
replace sexo_ci = . if sexo_ci < 1 | sexo_ci > 2
label var sexo_ci "Sex: 1=male 2=female"

gen edad_ci = .
capture replace edad_ci = edad
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
* Migration — NOT available
*------------------------------------------------------------------------------
gen migrante_ci     = .
gen mig_pais_ci     = .
gen migrantiguo5_ci = .

*------------------------------------------------------------------------------
* Employment — condact (lowercase in 2022)
* condact: 1=employed, 2=unemployed cesante, 3=unemployed new entrant, 4=inactive
*------------------------------------------------------------------------------
gen condocup_ci = .
capture replace condocup_ci = condact
replace condocup_ci = . if condocup_ci < 1 | condocup_ci > 4
replace condocup_ci = . if edad_ci < 10
label var condocup_ci "Employment: 1=emp 2=ces 3=new_unem 4=inactive"

gen emp_ci    = (condocup_ci == 1) if !missing(condocup_ci)
gen desemp_ci = (inlist(condocup_ci, 2, 3)) if !missing(condocup_ci)
gen pea_ci    = (inlist(condocup_ci, 1, 2, 3)) if !missing(condocup_ci)

*------------------------------------------------------------------------------
* Job category — oc609
*------------------------------------------------------------------------------
gen categopri_ci = .
capture {
    replace categopri_ci = 1 if inlist(oc609, 1, 2, 3, 10) & emp_ci == 1   // employee
    replace categopri_ci = 2 if inlist(oc609, 5, 7) & emp_ci == 1          // patron
    replace categopri_ci = 3 if inlist(oc609, 4, 9) & emp_ci == 1          // self
    replace categopri_ci = 4 if inlist(oc609, 6, 8, 11) & emp_ci == 1      // unpaid
}
label var categopri_ci "Category primary: 1=emp 2=patron 3=self 4=unpaid"

gen categosec_ci = .
capture {
    replace categosec_ci = 1 if inlist(oc6091, 1, 2, 3, 10) & emp_ci == 1
    replace categosec_ci = 2 if inlist(oc6091, 5, 7) & emp_ci == 1
    replace categosec_ci = 3 if inlist(oc6091, 4, 9) & emp_ci == 1
    replace categosec_ci = 4 if inlist(oc6091, 6, 8, 11) & emp_ci == 1
}

gen categoinac_ci = .
gen tipocontrato_ci = .

*------------------------------------------------------------------------------
* Hours — day-by-day for primary job
*------------------------------------------------------------------------------
* Primary: oc_605_lunes ... oc_605_domingo, adjusted by oc606/oc607
gen horas_trabpri = .
capture gen horas_trabpri = rowtotal(oc_605_lunes oc_605_martes oc_605_miercoles ///
    oc_605_jueves oc_605_viernes oc_605_sabado oc_605_domingo)

gen horaspri_ci = .
capture {
    replace horaspri_ci = horas_trabpri              if oc606 == 3
    replace horaspri_ci = horas_trabpri + oc607      if oc606 == 1
    replace horaspri_ci = horas_trabpri - oc607      if oc606 == 2
    replace horaspri_ci = 0                          if oc606 == 4
}
replace horaspri_ci = . if horaspri_ci > 168
replace horaspri_ci = . if emp_ci != 1
drop horas_trabpri
label var horaspri_ci "Hours primary job (last week)"

* Secondary job hours
gen horas_trabsec = .
capture gen horas_trabsec = rowtotal(oc_605_lunes1 oc_605_martes1 oc_605_miercoles1 ///
    oc_605_jueves1 oc_605_viernes1 oc_605_sabado1 oc_605_domingo1)

gen horassec_ci = .
capture {
    replace horassec_ci = horas_trabsec              if oc6061 == 3
    replace horassec_ci = horas_trabsec + oc6071     if oc6061 == 1
    replace horassec_ci = horas_trabsec - oc6071     if oc6061 == 2
    replace horassec_ci = 0                          if oc6061 == 4
}
replace horassec_ci = . if horassec_ci > 168
replace horassec_ci = . if emp_ci != 1
drop horas_trabsec

gen horastot_ci = .
capture replace horastot_ci = horaspri_ci + horassec_ci if emp_ci == 1
label var horaspri_ci "Hours primary job"
label var horassec_ci "Hours secondary job"
label var horastot_ci "Total hours"

*------------------------------------------------------------------------------
* Occupation — ocupaop (ISCO-08 1-digit)
*------------------------------------------------------------------------------
gen ocupa_ci = .
capture replace ocupa_ci = ocupaop
replace ocupa_ci = . if ocupa_ci < 1 | ocupa_ci > 9
replace ocupa_ci = . if emp_ci != 1
label var ocupa_ci "Occupation 1-digit ISCO-08"

gen ramaop_ci = .
capture replace ramaop_ci = ramao
gen ramasec_ci = .
capture replace ramasec_ci = ramaos
gen tamemp_ci = .
capture replace tamemp_ci = oc_608_cuantas

*------------------------------------------------------------------------------
* Formality — not available in 2022
*------------------------------------------------------------------------------
gen cotizando_ci = .
gen afiliado_ci  = .
gen formal_ci    = .
label var cotizando_ci "Social security (not available 2022)"
label var formal_ci    "Formal (not available 2022)"

gen salmm_ci = `salmm'
label var salmm_ci "Monthly minimum wage (HNL)"

*------------------------------------------------------------------------------
* Education — ed05/ed08/ed10/ed13 (9-year básica structure)
* ed05: level not attending; ed08: grade; ed10: level attending; ed13: grade
*------------------------------------------------------------------------------
gen aedu_ci = .
capture {
    * Not attending: ed05 levels
    * 0=none, 1=prebásica, 2=básica(9yr), 3=bachillerato/diversificado(3yr),
    * 4=technical, 5=university, 6=postgrad, 7=other
    replace aedu_ci = 0  if ed05 == 0 | ed05 == 1
    replace aedu_ci = ed08          if ed05 == 2 & inrange(ed08, 1, 9)   // básica 1-9
    replace aedu_ci = ed08 + 9      if ed05 == 3 & inrange(ed08, 1, 3)   // bachillerato 10-12
    replace aedu_ci = ed08 + 9      if ed05 == 4 & inrange(ed08, 1, 3)   // technical 10-12
    replace aedu_ci = ed08 + 12     if ed05 == 5 & inrange(ed08, 1, 5)   // univ 13-17
    replace aedu_ci = ed08 + 17     if ed05 == 6 & inrange(ed08, 1, 3)   // postgrad 18-20
}
capture {
    * Currently attending: ed10/ed13
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
capture replace asiste_ci = ed01
gen repiteult_ci     = .
gen razonesnoasis_ci = .

*------------------------------------------------------------------------------
* edu_hdmf from aedu_ci thresholds (2022+ structure: 9-year básica)
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
* Income — primary job
* ysmop/ycmop + yseos/yceop for primary; ysmos/ycmos secondary
* Quarterly values for 2022 — divide by 3 for monthly
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

label var ylmpri_ci  "Labor monetary primary"
label var ylnmpri_ci "Labor non-monetary primary"
label var ylm_ci     "Total labor monetary"
label var ylnm_ci    "Total labor non-monetary"

* Non-labor income and remittances — NOT calculated in 2022 (follow reference)
gen ynlm_ci    = .
gen remesas_ci = .
gen remesas_ch = .
label var ynlm_ci    "Non-labor income (not calculated 2022)"
label var remesas_ci "Remittances (not calculated 2022)"

gen ytot_ci = .
replace ytot_ci = 0 if emp_ci == 1
capture replace ytot_ci = ylm_ci + ylnm_ci if emp_ci == 1
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

save "bases armo/armo/HND/HND_2022m6_BID.dta", replace
di "HND_2022m6_BID.dta saved. N = " _N

log close
