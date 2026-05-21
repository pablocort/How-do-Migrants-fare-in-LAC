clear
set more off

di "File created with the Claude HDMF system — 2026-05-14"

* -------------------------------------------------------------------------
* GUY 2021t3 — Guyana Labour Force Survey Q3 2021 — HDMF harmonization
* Based on: bases armo/raw/guy/alternative_do_file/GUY_2021t3_variablesBID.do
* Original authors: Fernando Morales, Angela Lopez, Agustina Thailinger,
*                   David Cornejo (IADB SCL/MIG)
* HDMF changes:
*   - Replaced global server paths with absolute locals
*   - Removed external Labels&ExternalVars_Harmonized_DataBank.do call
*   - Added HDMF variables: periodo_c, inactivo_ci, edu_hdmf, edu_isced,
*     mig_pais_ci
*   - Fixed typo: condocup_ci=4 now uses edad_ci (not undefined edad)
*   - Added HDMF standard keep list
* -------------------------------------------------------------------------

local base_dir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC"
local base_in  "`base_dir'\bases armo\raw\guy\GUY_2021t3.dta"
local base_out "`base_dir'\bases armo\armo\GUY\GUY_2021t3_BID.dta"
local log_dir  "`base_dir'\do armo\guy\logs"

capture mkdir "`log_dir'"
capture mkdir "`base_dir'\bases armo\armo\GUY"
capture log close
log using "`log_dir'\GUY_2021t3_variablesBID.log", replace

use "`base_in'", clear


		**********************************
		***VARIABLES DEL IDENTIFICACION***
		**********************************

gen region_BID_c = .
replace region_BID_c = 2
label var region_BID_c "Regiones BID"
label define region_BID_c 1 "Centroamerica_(CID)" 2 "Caribe_(CCB)" 3 "Andinos_(CAN)" 4 "Cono_Sur_(CSC)"
label value region_BID_c region_BID_c

	***************
	***region_c ***
	***************
	destring region, replace
	gen region_c = region
	label define region_c 1 "Barima Waini" 2 "Pomeroon-Supenaam" 3 "Essequibo Islands-West Demerara" ///
	4 "Demerara-Mahaica" 5 "Mahaica-Berbice" 6 "East Berbice-Corentyne" 7 "Cuyuni-Mazaruni" ///
	8 "Potaro-Siparuni" 9 "Upper Takutu-Upper Essequibo" 10 "Upper Demerara-Upper Berbice"
	label value region_c region_c
	label var region_c "division politico-administrativa, region"

*************
* factor_ch *
*************
gen factor_ch = weight
label var factor_ch "Factor de expansion del hogar"

*************
* idh_ch    *
*************
sort hhid
egen idh_ch = group(hhid)
label var idh_ch "ID del hogar"
tostring idh_ch, replace

*************
* idp_ci    *
*************
gen idp_ci = member
duplicates drop idh_ch idp_ci, force
label variable idp_ci "ID de la persona en el hogar"
tostring idp_ci, replace

*************
* zona_c    *
*************
gen zona_c = zone
label variable zona_c "Zona urbana vs. rural"
label define zona_c 1 "Urbana" 0 "Rural"
label value zona_c zona_c

*************
* pais_c    *
*************
gen pais_c = "GUY"
label variable pais_c "Pais"

**************
* periodo_c  *
**************
gen str10 periodo_c = "2021t3"

*************
* anio_c    *
*************
gen anio_c = 2021
label variable anio_c "Anio de la encuesta"

*************
* mes_c     *
*************
gen mes_c = 8

	***************
	* relacion_ci *
	***************
	gen relacion_ci = 1     if q1_02 == 1
	replace relacion_ci = 2 if q1_02 == 2
	replace relacion_ci = 3 if q1_02 == 3 | q1_02 == 4
	replace relacion_ci = 4 if (q1_02 >= 7 & q1_02 <= 8) | q1_02 == 5 | q1_02 == 6
	replace relacion_ci = 5 if q1_02 == 9
	label var relacion_ci "Relacion con el jefe del hogar"
	label def relacion_ci 1 "Jefe" 2 "Conyuge" 3 "Hijo/a" 4 "Otros parientes" 5 "Otros no parientes"
	label val relacion_ci relacion_ci


		**************************
		* VARIABLES DEMOGRAFICAS *
		**************************

***************
* factor_ci   *
***************
gen factor_ci = weight
label variable factor_ci "Factor de expansion del individuo"

***************
*** upm_ci ***
***************
clonevar upm_ci = psu
label variable upm_ci "Unidad Primaria de Muestreo"

***************
*** estrato_ci ***
***************
clonevar estrato_ci = stratum
label variable estrato_ci "Estrato"

***************
* sexo_ci     *
***************
gen sexo_ci = q1_03
label var sexo_ci "Sexo del individuo"
label define sexo_ci 1 "Hombre" 2 "Mujer"
label value sexo_ci sexo_ci

***************
* edad_ci     *
***************
gen edad_ci = q1_04
replace edad_ci = . if edad_ci < 0
label var edad_ci "Edad del individuo"

***************
* civil_ci    *
***************
gen civil_ci = 1     if q1_05 == 1
replace civil_ci = 2 if q1_05 == 2 | q1_05 == 3
replace civil_ci = 3 if q1_05 == 4 | q1_05 == 5
replace civil_ci = 4 if q1_05 == 6
label variable civil_ci "Estado civil"
label define civil_ci 1 "Soltero" 2 "Union formal o informal" 3 "Divorciado o separado" 4 "Viudo"
label value civil_ci civil_ci

***************
* jefe_ci     *
***************
gen jefe_ci = (relacion_ci == 1)
label variable jefe_ci "Jefe de hogar"

****************
* nconyuges_ch *
****************
by idh_ch, sort: egen nconyuges_ch = sum(civil_ci == 2)
label variable nconyuges_ch "Numero de conyuges"

****************
* nhijos_ch    *
****************
by idh_ch, sort: egen nhijos_ch = sum(relacion_ci == 3)
label variable nhijos_ch "Numero de hijos"

****************
* notropari_ch *
****************
by idh_ch, sort: egen notropari_ch = sum(relacion_ci == 4)
label variable notropari_ch "Numero de otros familiares"

******************
* notronopari_ch *
******************
by idh_ch, sort: egen notronopari_ch = sum(relacion_ci == 5)
label variable notronopari_ch "Numero de no familiares"

****************
* nempdom_ch   *
****************
by idh_ch, sort: gen nempdom_ch = 0
label variable nempdom_ch "Numero de empleados domesticos"

****************
* clasehog_ch  *
****************
gen clasehog_ch = 0
replace clasehog_ch = 1 if nhijos_ch == 0 & nconyuges_ch == 0 & notropari_ch == 0 & notronopari_ch == 0
replace clasehog_ch = 2 if nhijos_ch > 0 & notropari_ch == 0 & notronopari_ch == 0
replace clasehog_ch = 2 if nhijos_ch == 0 & nconyuges_ch > 0 & notropari_ch == 0 & notronopari_ch == 0
replace clasehog_ch = 3 if notropari_ch > 0 & notronopari_ch == 0
replace clasehog_ch = 4 if ((nconyuges_ch > 0 | nhijos_ch > 0 | notropari_ch > 0) & (notronopari_ch > 0))
replace clasehog_ch = 5 if nhijos_ch == 0 & nconyuges_ch == 0 & notropari_ch == 0 & notronopari_ch > 0
label variable clasehog_ch "Tipo de hogar"

****************
* nmiembros_ch *
****************
bysort idh_ch: egen byte nmiembros_ch = sum(relacion_ci > 0 & relacion_ci <= 4)
label variable nmiembros_ch "Numero de familiares en el hogar"

****************
* miembros_ci  *
****************
gen miembros_ci = (relacion_ci < 5)
label variable miembros_ci "Miembro del hogar"


		*********************************
		* VARIABLES DEL MERCADO LABORAL *
		*********************************

*******************
**** condocup_ci ****
*******************
gen condocup_ci = .
replace condocup_ci = 1 if q2_04 == 1 | q2_05 == 1 | (q2_06 == 1 | q2_06 == 2) | (q2_07 == 1 & (q2_09 >= 1 & q2_09 <= 3)) | (q2_10 == 1)
replace condocup_ci = 2 if (q2_19 == 1 | q2_19 == 2) & q2_14 == 1 & ((q2_15 >= 1 & q2_15 <= 10) | q2_15 == 99)
replace condocup_ci = 2 if (q2_19 == 1 | q2_19 == 2) & q2_14 == 2 & (q2_17 == 1 | q2_17 == 2)
recode condocup_ci (.=3) if edad_ci >= 15
replace condocup_ci = 4 if edad_ci < 15
label var condocup_ci "Condicion de ocupacion"
label define condocup_ci 1 "Ocupado" 2 "Desocupado" 3 "Inactivo" 4 "Menor de PET"
label value condocup_ci condocup_ci

************
*** emp_ci ***
************
gen emp_ci = (condocup_ci == 1)

****************
*** desemp_ci ***
****************
gen desemp_ci = (condocup_ci == 2)

***************
*** inactivo_ci ***
***************
gen byte inactivo_ci = .
replace inactivo_ci = (condocup_ci == 3) if condocup_ci != .
label var inactivo_ci "Inactivo (condocup_ci==3)"

*************
*** pea_ci ***
*************
gen pea_ci = (emp_ci == 1 | desemp_ci == 1)

****************
* horaspri_ci  *
****************
gen horaspri_ci = q3_03
replace horaspri_ci = . if emp_ci == 0
label var horaspri_ci "Horas trabajadas semanalmente en el trabajo principal"

****************
* horastot_ci  *
****************
gen horastot_ci = q3_05
replace horastot_ci = . if emp_ci == 0
label var horastot_ci "Horas trabajadas semanalmente en todos los empleos"

****************
* desalent_ci  *
****************
gen desalent_ci = (q2_17 == 9 | q2_17 == 10)
label var desalent_ci "Trabajadores desalentados"

****************
* subemp_ci    *
****************
gen subemp_ci = 0
replace subemp_ci = 1 if (horaspri_ci <= 30 & q3_11 == 1)
label var subemp_ci "Personas en subempleo por horas"

****************
*tiempoparc_ci *
****************
gen tiempoparc_ci = (horaspri_ci <= 30 & q3_11 == 2)
replace tiempoparc_ci = . if emp_ci != 1
label var tiempoparc_ci "Personas que trabajan medio tiempo"

****************
*categopri_ci  *
****************
gen categopri_ci = .
replace categopri_ci = 2 if (q3_16 == 3 | q3_16 == 4) & emp_ci == 1
replace categopri_ci = 3 if q3_16 == 1 & emp_ci == 1
replace categopri_ci = 4 if q3_16 == 2 & emp_ci == 1
replace categopri_ci = . if emp_ci != 1
label define categopri_ci 1 "Patron" 2 "Cuenta propia" 3 "Empleado" 4 "No remunerado"
label value categopri_ci categopri_ci
label variable categopri_ci "Categoria ocupacional en la actividad principal"

****************
*categosec_ci  *
****************
gen categosec_ci = .

****************
* contrato_ci  *
****************
gen contrato_ci = (q3_18 == 1)
replace contrato_ci = . if emp_ci != 1

****************
* nempleos_ci  *
****************
gen nempleos_ci = 1 if q3_01 == 2
replace nempleos_ci = 2 if q3_01 == 1

****************
* spublico_ci  *
****************
gen spublico_ci = (q3_34 == 3 | q3_34 == 4)
replace spublico_ci = . if emp_ci != 1
label var spublico_ci "Personas que trabajan en el sector publico"

		********************************
		* VARIABLES DE DEMANDA LABORAL *
		********************************

****************
* ocupa_ci     *
****************
destring isco_code, replace
gen ocupa_ci = .
replace ocupa_ci = 1 if (isco_code >= 2111 & isco_code <= 3522) & emp_ci == 1
replace ocupa_ci = 2 if (isco_code >= 1111 & isco_code <= 1439) & emp_ci == 1
replace ocupa_ci = 3 if (isco_code >= 4110 & isco_code <= 4419 | isco_code >= 410 & isco_code <= 430) & emp_ci == 1
replace ocupa_ci = 4 if ((isco_code >= 5211 & isco_code <= 5249) | (isco_code >= 9510 & isco_code <= 9520)) & emp_ci == 1
replace ocupa_ci = 5 if ((isco_code >= 5111 & isco_code <= 5169) | (isco_code >= 5311 & isco_code <= 5419) | (isco_code >= 9111 & isco_code <= 9129) | (isco_code >= 9611 & isco_code <= 9624)) & emp_ci == 1
replace ocupa_ci = 6 if ((isco_code >= 6111 & isco_code <= 6340) | (isco_code >= 9211 & isco_code <= 9216)) & emp_ci == 1
replace ocupa_ci = 7 if ((isco_code >= 7111 & isco_code <= 8350) | (isco_code >= 9311 & isco_code <= 9412)) & emp_ci == 1
replace ocupa_ci = 8 if (isco_code >= 110 & isco_code <= 310) & emp_ci == 1
replace ocupa_ci = 9 if (isco_code == 9629) & emp_ci == 1
label variable ocupa_ci "Ocupacion laboral"

* rama_ci (ISIC Rev.4)
destring isic_code, replace
gen rama_ci = .
replace rama_ci = 1 if (isic_code > 0    & isic_code <= 400)   & emp_ci == 1
replace rama_ci = 2 if (isic_code >= 500  & isic_code <= 1000)  & emp_ci == 1
replace rama_ci = 3 if (isic_code >= 1010 & isic_code <= 3400)  & emp_ci == 1
replace rama_ci = 4 if (isic_code >= 3500 & isic_code <= 4000)  & emp_ci == 1
replace rama_ci = 5 if (isic_code >= 4100 & isic_code <= 4400)  & emp_ci == 1
replace rama_ci = 6 if ((isic_code >= 4500 & isic_code <= 4800) | (isic_code >= 5500 & isic_code <= 5700)) & emp_ci == 1
replace rama_ci = 7 if ((isic_code >= 4900 & isic_code <= 5400) | (isic_code >= 6100 & isic_code <= 6199)) & emp_ci == 1
replace rama_ci = 8 if (isic_code >= 6400 & isic_code <= 8300)  & emp_ci == 1
replace rama_ci = 9 if ((isic_code >= 5800 & isic_code <= 6090) | (isic_code >= 6200 & isic_code <= 6399) | (isic_code >= 8400 & isic_code <= 9900)) & emp_ci == 1
label var rama_ci "Rama de actividad de la ocupacion principal"

rename isic_code codindustria
rename isco_code codocupa


		**************
		***INGRESOS***
		**************

* Impute bracket midpoints for income variables that respondents reported as ranges
foreach v of varlist q6_01 q6_06 q6_11 q6_12 q6_13 {
	decode `v'b, gen(_`v'b)
	replace _`v'b = regexr(_`v'b, ",", "")
	replace _`v'b = regexr(_`v'b, ",", "")
	replace _`v'b = regexr(_`v'b, ",", "")
	gen _min`v'b = real(regexs(1)) if regexm(_`v'b, "([0-9]+)")
	replace _min`v'b = . if _min`v'b == 0
	replace _`v'b = regexr(_`v'b, "([0-9]+)", "")
	gen _max`v'b = real(regexs(1)) if regexm(_`v'b, "([0-9]+)")
	egen _mean`v'b = rowmean(_min`v'b _max`v'b)
	replace _mean`v'b = (_min`v'b) * 1.25 if (_max`v'b == . & _min`v'b != .)
	drop _min* _max* _q6_*
}

****************
* ylmpri_ci    *
****************
foreach var of varlist q6_01 q6_06 q6_04a q6_04b q6_04c q6_04d q6_04e q6_04f {
	cap replace `var' = _mean`var'b if `var' == -1
	cap replace `var' = . if `var' < 0
}

cap drop ylmpri_ci
egen ylmpri_ci = rsum(q6_01 q6_06 q6_04a q6_04b q6_04c q6_04d q6_04e q6_04f), missing
replace ylmpri_ci = . if emp_ci == 0
label var ylmpri_ci "Ingreso laboral monetario actividad principal"

****************
* ylnmpri_ci   *
****************
foreach var of varlist q6_05a-q6_05i {
	replace `var' = . if `var' < 0
}
replace q6_09 = . if q6_09 < 0 | q6_08 == 2
replace q6_07 = . if q6_07 < 0

egen ylnmpri_ci = rsum(q6_05a q6_05b q6_05c q6_05d q6_05e q6_05f q6_05g q6_05h q6_05i q6_07 q6_09), missing
label var ylnmpri_ci "Ingreso laboral NO monetario actividad principal"

****************
* ylmsec_ci    *
****************
replace q6_10 = . if q6_10 < 0
gen ylmsec_ci = q6_10
label var ylmsec_ci "Ingreso laboral monetario segunda actividad"

****************
* ylnmsec_ci   *
****************
gen ylnmsec_ci = .

****************
* ylmotros_ci  *
****************
gen ylmotros_ci = .

****************
* ylnmotros_ci *
****************
gen ylnmotros_ci = .

****************
* nrylmpri_ci  *
****************
gen nrylmpri_ci = (emp_ci == 1 & ylmpri_ci == .)
replace nrylmpri_ci = . if emp_ci != 1

****************
* ylm_ci       *
****************
egen ylm_ci = rsum(ylmpri_ci ylmsec_ci), m
replace ylm_ci = . if emp_ci != 1
label var ylm_ci "Ingreso laboral monetario total"

****************
* ylnm_ci      *
****************
gen ylnm_ci = ylnmpri_ci
label var ylnm_ci "Ingreso laboral NO monetario total"

****************
* ynlm_ci      *
****************
* q6_16 (rent, last 3 months) and q6_17 (sale, last 3 months) → monthly
replace q6_16 = q6_16 / 3
replace q6_17 = q6_17 / 3

* q6_18 (alimony, 6m), q6_19 (transfers from GUY, 6m), q6_20a (remit GYD, 6m), q6_20b (remit USD, 6m)
replace q6_18  = q6_18  / 6
replace q6_19  = q6_19  / 6
replace q6_20a = q6_20a / 6
replace q6_20b = q6_20b / 6
replace q6_24b = q6_24b / 6
replace q6_24a = q6_24a / 6

* q6_21 (financial investments, 12m), q6_22 (other income, 12m) → monthly
replace q6_21 = q6_21 / 12
replace q6_22 = q6_22 / 12

foreach var of varlist q6_11 q6_12 q6_13 q6_14 q6_15 q6_16 q6_17 q6_18 q6_19 q6_20a q6_20b q6_21 q6_22 q6_24a q6_24b {
	cap replace `var' = _mean`var'b if `var' == -1
	cap replace `var' = . if `var' < 0
}

* Convert USD to GYD at 2021 official rate (Bank of Guyana, ~208.50 GYD/USD)
replace q6_20b = q6_20b * 208.50
replace q6_24b = q6_24b * 208.50

egen ynlm_ci = rsum(q6_11 q6_12 q6_13 q6_14 q6_15 q6_16 q6_17 q6_18 q6_19 q6_20a q6_20b q6_21 q6_22 q6_24a q6_24b)
label var ynlm_ci "Ingreso no laboral monetario"

****************
* ynlnm_ci     *
****************
gen ynlnm_ci = .

****************
* ytot_ci      *
****************
egen ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci ynlnm_ci)

****************
* nrylmpri_ch  *
****************
by idh_ch, sort: egen nrylmpri_ch = sum(nrylmpri_ci) if miembros_ci == 1
replace nrylmpri_ch = 1 if nrylmpri_ch > 0 & nrylmpri_ch < .
replace nrylmpri_ch = . if nrylmpri_ch == .

****************
* ylm_ch       *
****************
by idh_ch, sort: egen ylm_ch = sum(ylm_ci) if miembros_ci == 1, missing

****************
* ylnm_ch      *
****************
by idh_ch, sort: egen ylnm_ch = sum(ylnm_ci) if miembros_ci == 1, missing

***********
* ynlm_ch *
***********
by idh_ch, sort: egen ynlm_ch = sum(ynlm_ci) if miembros_ci == 1, missing

*************
* ynlnm_ch  *
*************
gen ynlnm_ch = .

*****************
* ylmhopri_ci   *
*****************
gen ylmhopri_ci = ylmpri_ci / (horaspri_ci * 4.3)
label var ylmhopri_ci "Salario monetario de la actividad principal"

*************
* ylmho_ci  *
*************
gen ylmho_ci = ylm_ci / (horastot_ci * 4.3)
label var ylmho_ci "Salario monetario de todas las actividades"

****************
* remesas_ci   *
* Note: GUY remittance amounts reported in ynlm_ci (q6_20a/b); remesas_ci left
* as missing per official alt file to avoid double-counting with ynlm_ci.
****************
gen remesas_ci = .
label var remesas_ci "Remesas mensuales del individuo"

****************
* remesas_ch   *
****************
gen remesas_ch = .
label var remesas_ch "Remesas mensuales del hogar"

****************
* durades_ci   *
****************
gen durades_ci = .
replace durades_ci = (1 + 12.9) / 2 / 4.3 if q2_18 == 1
replace durades_ci = (3 + 5) / 2           if q2_18 == 2
replace durades_ci = (6 + 12) / 2          if q2_18 == 3
replace durades_ci = (12 + 24) / 2         if q2_18 == 4
replace durades_ci = (36 + 48) / 2         if q2_18 == 5
replace durades_ci = (60 + 72) / 2         if q2_18 == 6
label variable durades_ci "Duracion del desempleo en meses"

****************
* antiguedad_ci*
****************
gen antiguedad_ci = .
replace antiguedad_ci = (1 + 6) / 12  if q3_40 == 1
replace antiguedad_ci = (6 + 11) / 2  if q3_40 == 2
replace antiguedad_ci = (12 + 59) / 2 if q3_40 == 3
replace antiguedad_ci = (60 + 119) / 2 if q3_40 == 4
replace antiguedad_ci = (120 + 132) / 2 if q3_40 == 5
label var antiguedad_ci "Antiguedad en la actividad actual en anos"
replace antiguedad_ci = . if emp_ci != 1 | antiguedad_ci > edad_ci


		************************
		* VARIABLES EDUCATIVAS *
		************************

***************
*** asiste_ci ***
***************
gen asiste_ci = (q1_12 == 1)
label var asiste_ci "Personas que actualmente asisten a centros de ensenanza"

*************
*** aedu_ci ***
*************
* GUY school system: primary 6yr (Grds 1-6), secondary 6yr (Forms 1-6 / Grds 7-12)
* q1_13: 1=Pre-primary, 2=Primary, 3=Secondary, 4=Post-secondary, 5=University/Tertiary
* q1_14: completed grade (1=None, 2=Grds1-2, 3-6=Grds3-6, 7-12=Forms1-6)
* q1_15: post-sec degree (1=None, 2=Tech/Voc, 3=Univ cert, 4=Bachelor, 5=PG cert, 6=Masters, 7=Doctoral)
gen aedu_ci = .
replace aedu_ci = 0   if q1_11 == 2                               // never attended
replace aedu_ci = 0   if q1_13 == 1                               // pre-primary
replace aedu_ci = 0   if q1_13 == 2 & q1_14 == 1                  // primary, none
replace aedu_ci = 1   if q1_13 == 2 & q1_14 == 2                  // Prep A&B (Grds 1-2)
replace aedu_ci = q1_14 if q1_13 == 2 & q1_14 >= 3 & q1_14 <= 6 & q1_14 != .  // primary Grds 3-6
replace aedu_ci = 6   if q1_13 == 3 & q1_14 == 1                  // secondary, none = assume primary complete
replace aedu_ci = q1_14 if q1_13 == 3 & q1_14 >= 7 & q1_14 != .  // secondary Forms 1-6 (Grds 7-12)
replace aedu_ci = 12  if q1_13 == 4 & q1_15 == 1                  // post-sec, no degree = secondary complete
replace aedu_ci = 13  if q1_13 == 4 & q1_15 == 2                  // tech/voc cert (11+2)
replace aedu_ci = 13  if q1_13 == 5 & q1_15 == 2                  // tech/voc (from univ path)
replace aedu_ci = 15  if q1_13 == 5 & q1_15 == 3                  // univ cert/diploma (11+4)
replace aedu_ci = 15  if q1_13 == 5 & q1_15 == 4                  // bachelor's (11+4)
replace aedu_ci = 17  if q1_13 == 5 & q1_15 == 5                  // PG cert (11+6)
replace aedu_ci = 17  if q1_13 == 5 & q1_15 == 6                  // master's (11+6)
replace aedu_ci = 20  if q1_13 == 5 & q1_15 == 7                  // doctoral (11+9)
label var aedu_ci "Anios de educacion aprobados"

**************
*** eduui_ci ***
**************
gen byte eduui_ci = 0
replace eduui_ci = 1 if aedu_ci > 11 & aedu_ci < 15
replace eduui_ci = . if aedu_ci == .
label variable eduui_ci "Terciaria/Universitaria incompleta"

***************
*** eduuc_ci ***
***************
gen byte eduuc_ci = 0
replace eduuc_ci = 1 if aedu_ci >= 15
replace eduuc_ci = . if aedu_ci == .
label variable eduuc_ci "Terciaria/Universitaria completa o mas"

***************
* edu_hdmf    *
***************
* HDMF 10-level scale; GUY: 6yr primary, secondary Forms 1-6 (Grds 7-12=aedu 7-12)
gen edu_hdmf = .
replace edu_hdmf = 1  if aedu_ci == 0
replace edu_hdmf = 2  if aedu_ci >= 1  & aedu_ci < 6
replace edu_hdmf = 3  if aedu_ci == 6
replace edu_hdmf = 4  if aedu_ci >= 7  & aedu_ci < 10
replace edu_hdmf = 5  if aedu_ci >= 10 & aedu_ci <= 12
replace edu_hdmf = 6  if aedu_ci == 13
replace edu_hdmf = 7  if aedu_ci >= 14 & aedu_ci < 15
replace edu_hdmf = 8  if aedu_ci >= 15 & aedu_ci <= 16
replace edu_hdmf = 9  if aedu_ci >= 17 & aedu_ci <= 18
replace edu_hdmf = 10 if aedu_ci >= 19 & aedu_ci != .
label var edu_hdmf "HDMF education level (1-10)"

***************
* edu_isced   *
***************
gen edu_isced = .
replace edu_isced = 0 if aedu_ci == 0
replace edu_isced = 1 if aedu_ci >= 1  & aedu_ci <= 6
replace edu_isced = 2 if aedu_ci >= 7  & aedu_ci <= 9
replace edu_isced = 3 if aedu_ci >= 10 & aedu_ci <= 12
replace edu_isced = 4 if aedu_ci == 13
replace edu_isced = 5 if aedu_ci >= 14 & aedu_ci <= 15
replace edu_isced = 6 if aedu_ci >= 15 & aedu_ci <= 16
replace edu_isced = 7 if aedu_ci >= 17 & aedu_ci <= 20
replace edu_isced = 8 if aedu_ci > 20  & aedu_ci != .
label var edu_isced "ISCED-2011 level"


/************************************************************************************************************
* Security and labor market variables
************************************************************************************************************/

*********
* lp_ci *
*********
gen lp_ci = .
label var lp_ci "Linea de pobreza oficial del pais"

*********
* lpe_ci *
*********
gen lpe_ci = .
label var lpe_ci "Linea de indigencia oficial del pais"

****************
*cotizando_ci  *
****************
gen aux = real(q3_29)
gen cotizando_ci = .
replace cotizando_ci = 1 if (q3_26 == 1 | aux == 1 | aux == 2)
recode cotizando_ci .=0 if (condocup_ci == 1 | condocup_ci == 2)
label var cotizando_ci "Cotizante a la Seguridad Social"
drop aux

****************
*afiliado_ci   *
****************
gen afiliado_ci = .
label var afiliado_ci "Afiliado a la Seguridad Social"

****************
*tipopen_ci    *
****************
gen tipopen_ci = .

****************
*instpen_ci    *
****************
gen instpen_ci = .

****************
*instcot_ci    *
****************
gen instcot_ci = .

*****************
*tipocontrato_ci*
*****************
gen tipocontrato_ci = .
replace tipocontrato_ci = 1 if (q3_19 == 2) & categopri_ci == 3
replace tipocontrato_ci = 2 if (q3_19 == 1) & categopri_ci == 3
replace tipocontrato_ci = 3 if (q3_18 == 2 | tipocontrato_ci == .) & categopri_ci == 3
label var tipocontrato_ci "Tipo de contrato segun su duracion"

*************
*cesante_ci  *
*************
gen cesante_ci = 1 if q4_02 == 1 & (q2_14 == 1 | q2_17 == 1 | q2_17 == 2)
replace cesante_ci = 0 if q4_02 == 2 & (q2_14 == 1 | q2_17 == 1 | q2_17 == 2)

**************
*** tamemp_ci **
**************
gen tamemp_ci = 1 if q3_38 == 1 | q3_38 == 2
replace tamemp_ci = 2 if q3_38 == 3 | q3_38 == 4 | q3_38 == 5
replace tamemp_ci = 3 if q3_38 == 6

*************
** pension_ci *
*************
gen pension_ci = (q6_11 > 0 & q6_11 < .) | (q6_13 > 0 & q6_13 < .)
recode pension_ci .=0
label var pension_ci "1=Recibe pension contributiva"

*************
** ypen_ci *
*************
replace q6_11 = . if q6_11 < 0
replace q6_13 = . if q6_13 < 0
egen ypen_ci = rsum(q6_11 q6_13), missing
replace ypen_ci = . if ypen_ci < 0

***************
*pensionsub_ci*
***************
replace q6_12 = . if q6_12 < 0
gen pensionsub_ci = (q6_12 > 0 & q6_12 < .)

*****************
** ypensub_ci  *
*****************
gen ypensub_ci = q6_12

*************
** salmm_ci **
*************
gen salmm_ci = 44200
label var salmm_ci "Salario minimo legal (GYD, 2016 onwards)"

**************
*categoinac_ci*
**************
gen categoinac_ci = .
replace categoinac_ci = 1 if q2_20 == 4 & condocup_ci == 3
replace categoinac_ci = 2 if q2_20 == 1 & condocup_ci == 3
replace categoinac_ci = 3 if q2_20 == 2 & condocup_ci == 3
replace categoinac_ci = 4 if (categoinac_ci != 1 & categoinac_ci != 2 & categoinac_ci != 3) & condocup_ci == 3

***************
*** formal_ci ***
***************
gen byte formal_ci = 1 if cotizando_ci == 1 & (condocup_ci == 1 | condocup_ci == 2)
recode formal_ci .=0 if (condocup_ci == 1 | condocup_ci == 2)
label var formal_ci "1=afiliado o cotizante / PEA"


******************************
*** VARIABLES DE MIGRACION ***
******************************

	*******************
	*** migrante_ci ***
	*******************
	gen migrante_ci = inrange(q1_07, 2, 10) if q1_07 != .
	label var migrante_ci "=1 si es migrante (nacido fuera de Guyana)"

	**********************
	*** migrantiguo5_ci ***
	**********************
	* q1_10: 1-3=in Guyana 5yrs ago (old migrant); 4=in another country (recent migrant)
	gen migrantiguo5_ci = (migrante_ci == 1 & inlist(q1_10, 1, 2, 3)) if migrante_ci != . & !inrange(edad_ci, 0, 4) & q1_10 != 5
	replace migrantiguo5_ci = 0 if migrantiguo5_ci != 1 & migrante_ci == 1
	replace migrantiguo5_ci = . if migrante_ci == 0
	label var migrantiguo5_ci "=1 si es migrante antiguo (5 anos o mas)"

	*************
	*mig_pais_ci*
	*************
	* q1_07 reports region, not individual country
	gen str30 mig_pais_ci = ""
	replace mig_pais_ci = "Other Caribbean"       if q1_07 == 2  & migrante_ci == 1
	replace mig_pais_ci = "South/Central America" if q1_07 == 3  & migrante_ci == 1
	replace mig_pais_ci = "USA"                   if q1_07 == 4  & migrante_ci == 1
	replace mig_pais_ci = "Canada"                if q1_07 == 5  & migrante_ci == 1
	replace mig_pais_ci = "Great Britain"         if q1_07 == 6  & migrante_ci == 1
	replace mig_pais_ci = "Other Europe"          if q1_07 == 7  & migrante_ci == 1
	replace mig_pais_ci = "Asia"                  if q1_07 == 8  & migrante_ci == 1
	replace mig_pais_ci = "Africa"                if q1_07 == 9  & migrante_ci == 1
	replace mig_pais_ci = "Other"                 if q1_07 == 10 & migrante_ci == 1
	label var mig_pais_ci "Region de origen del migrante (q1_07)"

	**********************
	*** miglac_ci ***
	**********************
	gen miglac_ci = .
	label var miglac_ci "=1 si es migrante proveniente de un pais LAC (not constructible from q1_07 region codes)"


compress


/*_____________________________________________________________________________*/
* HDMF KEEP: retener solo variables estandar
/*_____________________________________________________________________________*/

keep ///
	pais_c periodo_c anio_c mes_c ///
	idh_ch idp_ci factor_ci factor_ch ///
	edad_ci sexo_ci relacion_ci miembros_ci ///
	condocup_ci emp_ci desemp_ci inactivo_ci pea_ci ///
	horaspri_ci horastot_ci categopri_ci ///
	cotizando_ci afiliado_ci formal_ci tipocontrato_ci ///
	ocupa_ci ///
	ylmpri_ci ylnmpri_ci ylmsec_ci ylnmsec_ci ylmotros_ci ylnmotros_ci ///
	ylm_ci ylnm_ci ynlm_ci ynlnm_ci ytot_ci ///
	ylm_ch ylnm_ch ynlm_ch ///
	remesas_ci remesas_ch ///
	nrylmpri_ci nrylmpri_ch ///
	aedu_ci edu_hdmf edu_isced ///
	migrante_ci migrantiguo5_ci mig_pais_ci ///
	lp_ci lpe_ci salmm_ci

save "`base_out'", replace

log close
