* (Versión Stata 12)
clear
set more off
di "File created with the Claude HDMF system — 2026-04-14"
*________________________________________________________________________________________________________________*
* ECU ENEMDU 2018m12 — HDMF harmonization script
* Reference: ECU_2025m12_variablesBID.do
* Changes vs. reference:
*   1. local ANO = "2018" / gen anio_c = 2018
*   2. region_c: variable ciudad NOT present in ECU 2018m12 — region_c set to missing
*      (confirmed via alternative do file, commented block)
*   3. ID structure: legacy vars vivienda/hogar/p01 used
*      (id_vivienda/id_hogar/id_persona not present in 2018)
*   4. edu_hdmf: added — source vars p10a/p10b/p12a confirmed present
*   5. miembros_ci: added (required by HDMF codebook; missing from 2025 reference)
*   6. cotizando_ci: unified formula (p44f==1 | p61b1<=4) — p61b1 confirmed present in 2018
*   7. No income module
*________________________________________________________________________________________________________________*

global ruta = "${surveysFolder}"
global gitFolder = "${gitFolder}"

local PAIS ECU
local ENCUESTA ENEMDU
local ANO "2018"
local ronda m12

local log_file = "$ruta\harmonized\\`PAIS'\\`ENCUESTA'\log\\`PAIS'_`ANO'`ronda'_variablesBID.log"
local base_in  = "$ruta\survey\\`PAIS'\\`ENCUESTA'\\`ANO'\\`ronda'\data_merge\\`PAIS'_`ANO'`ronda'.dta"
local base_out = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"

if c(username)=="STEFFANNYR" {
use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\ecu\ECU_2018m12.dta", clear
local base_out = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"
}

if c(username)=="PABLOCOR" {
use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\ecu\ECU_2018m12.dta", clear
local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"
}

		*************************
		***VARIABLES DEL HOGAR***
		*************************

**************
* Region_BID *
**************
gen region_BID_c = .
replace region_BID_c = 3
label define region_BID_lbl ///
    1 "Centroamérica (CID)" ///
    2 "Caribe (CCB)" ///
    3 "Andinos (CAN)" ///
    4 "Cono Sur (CSC)"
label values region_BID_c region_BID_lbl
label variable region_BID_c "Regiones BID"

***************
***region_c ***
***************
/* NOT AVAILABLE: variable ciudad not present in ECU 2018m12.
   region_c set to missing for all observations.
   Source: alternative do file ECU_2018m12_variablesBID.do (commented block). */
gen region_c = .
label define region_c_lbl ///
    1 "Azuay" ///
    2 "Bolívar" ///
    3 "Cañar" ///
    4 "Carchi" ///
    5 "Cotopaxi" ///
    6 "Chimborazo" ///
    7 "El Oro" ///
    8 "Esmeraldas" ///
    9 "Guayas" ///
    10 "Imbabura" ///
    11 "Loja" ///
    12 "Los Ríos" ///
    13 "Manabí" ///
    17 "Pichincha" ///
    18 "Tungurahua" ///
    23 "Santo Domingo de los Tsáchilas" ///
    24 "Santa Elena" ///
    89 "Amazonia" ///
    90 "zonas no delimitadas"
label values region_c region_c_lbl
label variable region_c "division politico-administrativa, provincia"

*************
****pais_c***
*************
gen str3 pais_c = "ECU"
label variable pais_c "Pais"

************
***anio_c***
************
gen anio_c = 2018
label variable anio_c "Anio de la encuesta"

***********
***mes_c***
***********
gen mes_c = 12
label var mes_c "Mes de la encuesta"

*************
****zona_c***
*************
gen zona_c = 1 		if area == 1
replace zona_c = 0 	if area == 2
label variable zona_c "Zona del pais"
label define zona_c 1 "Urbana" 0 "Rural"
label value zona_c zona_c

***************
***estrato_ci***
***************
clonevar estrato_ci = estrato
label variable estrato_ci "Estrato"

***************
***upm_ci***
***************
clonevar upm_ci = upm
label variable upm_ci "Unidad Primaria de Muestreo"

*************
****idh_ch***
*************
/* ALTERNATIVE: Legacy ID structure — id_vivienda/id_hogar not present in ECU 2018.
   Household ID via egen group on survey design variables.
   Source: alternative do file ECU_2018m12_variablesBID.do. */
sort area estrato upm vivienda hogar p01
egen idh_ch = group(area estrato upm vivienda hogar)
label variable idh_ch "ID del hogar"

*************
****idp_ci***
*************
/* ALTERNATIVE: Person number p01 used as individual identifier within household. */
gen idp_ci = p01
label variable idp_ci "ID de la persona en el hogar"
tostring idp_ci, replace

***************
***factor_ci***
***************
gen factor_ci = fexp
label variable factor_ci "Factor de expansion del individuo"

***************
***factor_ch***
***************
gen factor_ch = fexp
label variable factor_ch "Factor de expansion del hogar"


			****************************
			***VARIABLES DEMOGRAFICAS***
			****************************

*************
***sexo_ci***
*************
gen sexo_ci = p02
label var sexo_ci "Sexo del individuo"
label def sexo_ci 1 "Masculino" 2 "Femenino"
label val sexo_ci sexo_ci

*************
***edad_ci***
*************
gen edad_ci = p03 if p03 < 99
label variable edad_ci "Edad del individuo"

*****************
***relacion_ci***
*****************
gen relacion_ci = 1 if p04 == 1
replace relacion_ci = 2 if p04 == 2
replace relacion_ci = 3 if p04 == 3
replace relacion_ci = 4 if inrange(p04, 4, 7)
replace relacion_ci = 5 if p04 == 9
replace relacion_ci = 6 if p04 == 8
label variable relacion_ci "Relacion con el jefe del hogar"
label define relacion_ci_lbl ///
    1 "Jefe/a" ///
    2 "Esposo/a" ///
    3 "Hijo/a" ///
    4 "Otros parientes" ///
    5 "Otros no parientes" ///
    6 "Empleado/a domestico/a"
label values relacion_ci relacion_ci_lbl

***************
***miembros_ci***
***************
/* DERIVED: Added to all HDMF waves — required by codebook. Not in 2025 reference script.
   Threshold <=5 consistent with ECU 2018-2023 alternative scripts. */
gen miembros_ci = (relacion_ci >= 1 & relacion_ci <= 5)
label variable miembros_ci "Miembro del hogar"


		***********************************
		***VARIABLES DEL MERCADO LABORAL***
		***********************************

***************
**condocup_ci**
***************
gen condocup_ci = .
replace condocup_ci = 1 if p20 == 1 | p21 < 12 | p22 == 1
replace condocup_ci = 2 if (p20 == 2 | p21 == 12 | p22 == 2) & p32 < 11
replace condocup_ci = 3 if condocup_ci != 1 & condocup_ci != 2
replace condocup_ci = . if !inrange(edad_ci, 15, 64)
label define condocup_ci 1 "ocupados" 2 "desocupados" 3 "inactivos"
label value condocup_ci condocup_ci
label var condocup_ci "Condicion de ocupacion"

*******************
***categoinac_ci***
*******************
gen categoinac_ci = 1 if (p36 == 2 & condocup_ci == 3)
replace categoinac_ci = 2 if  (p36 == 3 & condocup_ci == 3)
replace categoinac_ci = 3 if  (p36 == 4 & condocup_ci == 3)
replace categoinac_ci = 4 if  ((categoinac_ci != 1 | categoinac_ci != 2 | categoinac_ci != 3) & condocup_ci == 3)
label var categoinac_ci "Categoría de inactividad"
label define categoinac_ci 1 "jubilados o pensionados" 2 "Estudiantes" 3 "Quehaceres domésticos" 4 "Otros"

************
***emp_ci***
************
gen emp_ci = (condocup_ci == 1)
label var emp_ci "1 = ocupados"

***************
***desemp_ci***
***************
gen desemp_ci = (condocup_ci == 2)
label var desemp_ci "Desempleado que buscó empleo en el periodo de referencia"

************
***pea_ci***
************
gen pea_ci = (emp_ci == 1 | desemp_ci == 1)
label var pea_ci "Población Económicamente Activa"

*****************
***horaspri_ci***
*****************
gen horaspri_ci = p51a
replace horaspri_ci = . if p51a == 999
replace horaspri_ci = . if emp_ci == 0
label var horaspri_ci "Horas trabajadas semanalmente en el trabajo principal"

*****************
***horastot_ci***
*****************
egen horastot_ci = rsum(p51a p51b p51c) if emp_ci == 1
replace horastot_ci = . if p51a == . & p51b == . & p51c == .
replace horastot_ci = . if emp_ci == 0
label var horastot_ci "Horas trabajadas semanalmente en todos los empleos"

*****************
***parcial_ci***
*****************
gen byte parcial_ci = .
replace parcial_ci = (horaspri_ci < 35) if emp_ci == 1 & horaspri_ci != .
label define parcial_lb 1 "Parcial (<35h)" 0 "Completo (>=35h)"
label values parcial_ci parcial_lb
label var parcial_ci "1 = trabajador a tiempo parcial (horaspri_ci < 35h)"

******************
***categopri_ci***
******************
gen categopri_ci = .
replace categopri_ci = 1 if p42 == 5
replace categopri_ci = 2 if p42 == 6
replace categopri_ci = 3 if (p42 <= 4) | p42 == 10
replace categopri_ci = 4 if (p42 >= 7 & p42 <= 9)
replace categopri_ci = . if emp_ci == 0
label define categopri_ci 1 "Patron" 2 "Cuenta propia" 0 "Otro"
label define categopri_ci 3 "Empleado" 4 "No remunerado" , add
label value categopri_ci categopri_ci
label variable categopri_ci "Categoria ocupacional"

*****************
***selfempl_ci***
*****************
gen byte selfempl_ci = .
replace selfempl_ci = (categopri_ci == 2) if emp_ci == 1 & categopri_ci != .
label define selfempl_lb 1 "Cuenta propia" 0 "Otros"
label values selfempl_ci selfempl_lb
label var selfempl_ci "1 = trabajador por cuenta propia (categopri_ci == 2)"

******************
***categosec_ci***
******************
gen categosec_ci = .
replace categosec_ci = 1 if p54 == 5
replace categosec_ci = 2 if p54 == 6
replace categosec_ci = 3 if (p54 <= 4) | p54 == 10
replace categosec_ci = 4 if (p54 >= 7 & p54 <= 9)
label define categosec_ci 1 "Patron" 2 "Cuenta propia" 0 "Otro"
label define categosec_ci 3 "Empleado" 4 "No remunerado" , add
label value categosec_ci categosec_ci
label variable categosec_ci "Categoria ocupacional en la segunda actividad"

****************
*cotizando_ci***
****************
/* ALTERNATIVE: 2018 alternative script had p61b1 commented out (only p44f==1).
   Standardized to unified 2025 formula — p61b1 confirmed present in ECU 2018m12 raw data. */
gen cotizando_ci = (p44f == 1 | p61b1 <= 4)
label var cotizando_ci "Cotizante a la Seguridad Social"

****************
***afiliado_ci**
****************
gen afiliado_ci = (p05a <= 4) /*IESS, ISSFA e ISSPOL requieren afiliación*/
label var afiliado_ci "Afiliado a la Seguridad Social"

***************
***formal_ci***
***************
gen byte formal_ci = .
replace formal_ci  =  1 if (cotizando_ci == 1 | afiliado_ci == 1) & condocup_ci == 1
replace formal_ci = 0 if (cotizando_ci == 0 & afiliado_ci == 0) & (condocup_ci == 1)
label var formal_ci "1=afiliado o cotizante"

*****************
*tipocontrato_ci*
*****************
gen tipocontrato_ci = .
replace tipocontrato_ci = 1 if (p43 == 1 | p43 == 2) & categopri_ci == 3
replace tipocontrato_ci = 2 if (p43 == 3) & categopri_ci == 3
replace tipocontrato_ci = 3 if (p43 >= 4 & p43 <= 6) & categopri_ci == 3
label var tipocontrato_ci "Tipo de contrato segun su duracion en act principal"
label define tipocontrato_ci 1 "Permanente/indefinido" 2 "Temporal" 3 "Sin contrato/verbal"
label value tipocontrato_ci tipocontrato_ci


			****************************
			***VARIABLES DE EDUCACION***
			****************************

*************
***aedu_ci***
*************
gen aedu_ci = .

replace aedu_ci = 0 if p10a == 1 | p10a == 2 | p10a == 3
replace aedu_ci = p10b if p10a == 4
replace aedu_ci = p10b - 1 if p10a == 5
replace aedu_ci = 0 if p10a == 5 & aedu_ci == -1
replace aedu_ci = p10b + 6  if p10a == 6
replace aedu_ci = p10b + 9  if p10a == 7
replace aedu_ci = p10b + 12 if p10a == 8 | p10a == 9
replace aedu_ci = p10b + 16 if p10a == 10

label var aedu_ci "Anios de educacion aprobados"


**************
*** edu_hdmf ***
**************
/* DERIVED: edu_hdmf added — not present in original 2018 alternative script.
   Construction identical to 2025 reference. Source vars p10a/p10b/p12a confirmed present. */
ta p10a
ta p10b if p10a == 5

gen edu_hdmf = .
* 1. menos de primaria
replace edu_hdmf = 1 if p10a == 1 | p10a == 2

* 2. primaria incompleta
replace edu_hdmf = 2 if  p10a == 4 & (p10b < 6)
replace edu_hdmf = 2 if  p10a == 5 & (p10b < 6)

* 3. primaria completa
replace edu_hdmf = 3 if  p10a == 4 & (p10b == 6)
replace edu_hdmf = 3 if  p10a == 5 & (p10b == 6)

* 4. Media incompleta (11°)
replace edu_hdmf = 4 if p10a == 7 & (p10b < 3)
replace edu_hdmf = 4 if p10a == 6 & (p10b < 6)
replace edu_hdmf = 4 if  p10a == 5 & (p10b < 10 & p10b > 6)

* 5. media completa (11°)
replace edu_hdmf = 5 if p10a == 7 & (p10b == 3)
replace edu_hdmf = 5 if p10a == 6 & (p10b == 6)
replace edu_hdmf = 5 if  p10a == 5 & (p10b == 10)

* 6. técnica (terciaria no universitaria)
replace edu_hdmf = 6 if p10a == 8 & p12a == 1   /* técnica completa */
replace edu_hdmf = 5 if p10a == 8 & p12a == 2          /* técnica incompleta → media completa */
replace edu_hdmf = 6 if p10a == 8 & missing(p12a)      /* FIX-ECU-01: p12a missing → default técnica completa */

* 7. universitaria completa
replace edu_hdmf = 7 if p10a == 9 & (p12a == 1)
replace edu_hdmf = 5 if p10a == 9 & (p12a == 2)

* 8. posgrado
replace edu_hdmf = 8 if  p10a == 10 & (p12a == 1)
replace edu_hdmf = 7 if  p10a == 10 & (p12a == 2)

label define edu_hdmf ///
1 "Menos de primaria" ///
2 "Primaria incompleta" ///
3 "Primaria completa" ///
4 "Media incompleta" ///
5 "Media completa" ///
6 "Técnica" ///
7 "Universitaria completa" ///
8 "Posgrado"

label values edu_hdmf edu_hdmf
label var edu_hdmf "nivel educativo agregado hdmf"

ta p10a, m
ta edu_hdmf, m
***********
* ocupa_ci
* p41: CIUO-08 2-digit occupation code; 1-digit major group = first digit of p41
***********
gen byte ocupa_ci = .
replace ocupa_ci = real(substr(string(int(p41)), 1, 1)) if emp_ci == 1 & !missing(p41) & p41 > 0
label define ocupa_lbl 1 "Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary", replace
label values ocupa_ci ocupa_lbl
label var ocupa_ci "ISCO-08 major group (CIUO-08 via p41, 1-digit)"
***********
* overqualified_ci
* edu_hdmf >= 6: técnica or higher (8-level ECU scale)
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified", replace
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (tertiary educ + low-skill occ, ISCO-08 4-9)"


	*****************************
	**** VARIABLES MIGRACIÓN ****
	*****************************

*******************
*** migrante_ci ***
*******************
gen migrante_ci = (p15aa == 3)
label var migrante_ci "=1 si es migrante"

**********************
*** migrantiguo5_ci ***
**********************
gen migrantiguo5_ci = .
label var migrantiguo5_ci "=1 si es migrante antiguo (5 anos o mas)"

**********************
*** miglac_ci ***
**********************
gen miglac_ci = (inlist(p15ab, 32, 44, 52, 68, 76, 84, 152, 170, 188, 214, 222, 320, 328, 332, 340, 388, 484, 558, 591, 600, 604, 740, 780, 858, 862) & migrante_ci == 1) if migrante_ci != .
replace miglac_ci = 0 if !inlist(p15ab, 32, 44, 52, 68, 76, 84, 152, 170, 188, 214, 222, 320, 328, 332, 340, 388, 484, 558, 591, 600, 604, 740, 780, 858, 862) & migrante_ci == 1
replace miglac_ci = . if migrante_ci == 0
label var miglac_ci "=1 si es migrante proveniente de un pais LAC"

**********************
*** mig_pais_code ***
**********************
gen mig_pais_code = .
replace mig_pais_code = p15ab if migrante_ci == 1 & migrante_ci != .

gen str40 mig_pais_ci = ""

replace mig_pais_ci = "Argentina"            if mig_pais_code == 32
replace mig_pais_ci = "Bolivia"              if mig_pais_code == 68
replace mig_pais_ci = "Brasil"               if mig_pais_code == 76
replace mig_pais_ci = "Canadá"               if mig_pais_code == 124
replace mig_pais_ci = "Chile"                if mig_pais_code == 152
replace mig_pais_ci = "Colombia"             if mig_pais_code == 170
replace mig_pais_ci = "Costa Rica"           if mig_pais_code == 188
replace mig_pais_ci = "Cuba"                 if mig_pais_code == 192
replace mig_pais_ci = "República Dominicana" if mig_pais_code == 214
replace mig_pais_ci = "El Salvador"          if mig_pais_code == 222
replace mig_pais_ci = "Alemania"             if mig_pais_code == 276
replace mig_pais_ci = "Honduras"             if mig_pais_code == 340
replace mig_pais_ci = "India"                if mig_pais_code == 356
replace mig_pais_ci = "Italia"               if mig_pais_code == 380
replace mig_pais_ci = "México"               if mig_pais_code == 484
replace mig_pais_ci = "Marruecos"            if mig_pais_code == 504
replace mig_pais_ci = "Perú"                 if mig_pais_code == 604
replace mig_pais_ci = "Filipinas"            if mig_pais_code == 608
replace mig_pais_ci = "Sudáfrica"            if mig_pais_code == 710
replace mig_pais_ci = "Zimbabwe"             if mig_pais_code == 716
replace mig_pais_ci = "España"               if mig_pais_code == 724
replace mig_pais_ci = "Ucrania"              if mig_pais_code == 804
replace mig_pais_ci = "Reino Unido"          if mig_pais_code == 826
replace mig_pais_ci = "Estados Unidos"       if mig_pais_code == 840
replace mig_pais_ci = "Venezuela"            if mig_pais_code == 862

replace mig_pais_ci = "Australia"      if mig_pais_code == 36
replace mig_pais_ci = "Armenia"        if mig_pais_code == 51
replace mig_pais_ci = "China"           if mig_pais_code == 156
replace mig_pais_ci = "Francia"         if mig_pais_code == 250
replace mig_pais_ci = "Haití"           if mig_pais_code == 332
replace mig_pais_ci = "Israel"          if mig_pais_code == 376
replace mig_pais_ci = "Japón"           if mig_pais_code == 392
replace mig_pais_ci = "Nicaragua"       if mig_pais_code == 558
replace mig_pais_ci = "Noruega"         if mig_pais_code == 578
replace mig_pais_ci = "Paraguay"        if mig_pais_code == 600
replace mig_pais_ci = "Polonia"         if mig_pais_code == 616
replace mig_pais_ci = "Puerto Rico"     if mig_pais_code == 630
replace mig_pais_ci = "Rumania"         if mig_pais_code == 642
replace mig_pais_ci = "Rusia"           if mig_pais_code == 643
replace mig_pais_ci = "Países Bajos"    if mig_pais_code == 528
replace mig_pais_ci = "Suiza"           if mig_pais_code == 756
replace mig_pais_ci = "Egipto"          if mig_pais_code == 818
replace mig_pais_ci = "Uruguay"        if mig_pais_code == 858
replace mig_pais_ci = "Panamá"         if mig_pais_code == 591
replace mig_pais_ci = "Guatemala"      if mig_pais_code == 320
replace mig_pais_ci = "Guyana"         if mig_pais_code == 328
replace mig_pais_ci = "Jamaica"        if mig_pais_code == 388
replace mig_pais_ci = "Suriname"       if mig_pais_code == 740
replace mig_pais_ci = "Trinidad y Tobago" if mig_pais_code == 780
replace mig_pais_ci = "Antigua y Barbuda" if mig_pais_code == 44
replace mig_pais_ci = "Barbados"       if mig_pais_code == 52
replace mig_pais_ci = "Belice"         if mig_pais_code == 84
replace mig_pais_ci = "Corea del Sur"  if mig_pais_code == 410
replace mig_pais_ci = "Nigeria"        if mig_pais_code == 566
replace mig_pais_ci = "Afganistán"     if mig_pais_code == 4
replace mig_pais_ci = "Taiwán"         if mig_pais_code == 158
replace mig_pais_ci = "Grecia"         if mig_pais_code == 300
replace mig_pais_ci = "Irán"           if mig_pais_code == 364
replace mig_pais_ci = "Portugal"       if mig_pais_code == 620
replace mig_pais_ci = "Azerbaiyán"     if mig_pais_code == 31
replace mig_pais_ci = "Austria"        if mig_pais_code == 40
replace mig_pais_ci = "Bélgica"        if mig_pais_code == 56
replace mig_pais_ci = "Dinamarca"      if mig_pais_code == 208
replace mig_pais_ci = "Aruba"          if mig_pais_code == 533
replace mig_pais_ci = "Uganda"         if mig_pais_code == 800
replace mig_pais_ci = "Otro"          if mig_pais_ci == "" & mig_pais_code != .
assert mig_pais_ci != "" if mig_pais_code != .

compress

save "`base_out'", replace
