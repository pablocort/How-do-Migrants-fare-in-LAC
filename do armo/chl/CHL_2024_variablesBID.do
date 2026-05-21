clear
set more off

di "File created with the Claude HDMF system — 2026-05-01"

*________________________________________________________________________________________________________________*

global surveysFolder "\\sapidbshares.file.core.windows.net\idbshares\SURVEYS"
display "$surveysFolder"

global ruta = "${surveysFolder}"

local PAIS CHL
local ENCUESTA CASEN
local ANO "2024"
local ronda a

local log_file = "$ruta\harmonized\\`PAIS'\\`ENCUESTA'\log\\`PAIS'_`ANO'`ronda'_variablesBID.log"
local base_in  = "$ruta\survey\\`PAIS'\\`ENCUESTA'\\`ANO'\\`ronda'\data_merge\\`PAIS'_`ANO'`ronda'.dta"

/***************************************************************************
                 BASES DE DATOS DE ENCUESTA DE HOGARES
*************************************************************************** */


if c(username)=="STEFFANNYR" {

use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\chl\casen_2024.dta", clear
local base_out = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"
	}


if c(username)=="PABLOCOR" {

use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\chl\casen_2024.dta", clear
local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"
	}



***************
* relacion_ci *
***************
gen relacion_ci=1     if pco1==1
replace relacion_ci=2 if pco1==2 | pco1==3
replace relacion_ci=3 if pco1==4 | pco1==5 | pco1==6
replace relacion_ci=4 if pco1>=7 & pco1<=13
replace relacion_ci=5 if pco1==14
replace relacion_ci=6 if pco1==15
label var relacion_ci "Relación de parentesco con el jefe"
label def relacion_ci 1"Jefe" 2"Conyuge" 3"Hijo/a" 4"Otros parientes" 5"Otros no parientes" 6"Servicio doméstico"
label val relacion_ci relacion_ci	

****************
* miembros_ci   * 
****************
gen miembros_ci=(relacion_ci>=1 & relacion_ci<=5)
label variable miembros_ci "Miembro del hogar"

*************
* pais_c    *
*************
gen pais_c="CHL"
label variable pais_c "Pais"

***************
* edad_ci     * 
***************
gen edad_ci=edad
label var edad_ci "Edad del individuo"

*************
* idh_ch    *
*************
sort folio
egen idh_ch=group(folio) 
label var idh_ch "ID del hogar"
tostring idh_ch, replace

*************
* idp_ci    *
*************
gen idp_ci=id_persona
label variable idp_ci "ID de la persona en el hogar"
tostring idp_ci, replace

***************
* factor_ci   * 
***************
gen factor_ci=expr
label variable factor_ci "Factor de expansion del individuo"

*************
* factor_ch *
*************
gen factor_ch=expr   
label var factor_ch "Factor de expansión el hogar"

****************
****condocup_ci*
****************
gen condocup_ci=.
replace condocup_ci=1 if (o1==1 | o2==1 | o3==1)
replace condocup_ci=2 if ((o1==2 | o2==2 | o3==2) & (o6==1))
recode condocup_ci (.=3) if edad_ci>=15 
replace condocup_ci=. if !inrange(edad_ci, 15,64)
label var condocup_ci "Condicion de ocupación de acuerdo a def de cada pais"
label define condocup_ci 1 "Ocupado" 2 "Desocupado" 3 "Inactivo" 
label value condocup_ci condocup_ci

**************
**categoinac_ci*
**************
gen categoinac_ci=1 if o7==12
replace categoinac_ci=2 if o7==11
replace categoinac_ci=3 if o7==10
replace categoinac_ci=4 if (o7>=1 & o7<=9 ) | (o7>= 13 & o7<=17)
label var categoinac_ci "Condición de inactividad"
label define categoinac_ci 1 "jubilado/pensionado" 2 "estudiante" 3 "quehaceres_domesticos" 4 "otros_inactivos" 
label value categoinac_ci categoinac_ci

************
***emp_ci***
************
gen emp_ci=(condocup_ci==1)

****************
***desemp_ci***
****************
gen desemp_ci=(condocup_ci==2)

****************
* horaspri_ci  * 
****************
gen horaspri_ci= o10
replace horaspri_ci=. if o10==-88 | emp_ci!=1
label var horaspri_ci "Horas totales trabajadas en la actividad principal"

****************
* horastot_ci  * 
****************
gen horastot_ci=horaspri_ci /*No existen horas totales solo act princ */
label var horastot_ci "Horas totales trabajadas en todas las actividades"

*****************
***parcial_ci***
*****************
gen byte parcial_ci = .
replace parcial_ci = (horaspri_ci < 35) if emp_ci == 1 & horaspri_ci != .
label define parcial_lb 1 "Parcial (<35h)" 0 "Completo (>=35h)"
label values parcial_ci parcial_lb
label var parcial_ci "1 = trabajador a tiempo parcial (horaspri_ci < 35h)"

*************
***pea_ci***
*************
gen pea_ci=(emp_ci==1 | desemp_ci==1)

****************
*cotizando_ci***
****************
gen cotizando_ci=.
replace cotizando_ci=1 if o32>=1 & o32<=5
recode cotizando_ci .=0 if (condocup_ci==1 | condocup_ci==2)
label var cotizando_ci "Cotizante a la Seguridad Social"

****************
*afiliado_ci****
****************
gen afiliado_ci=.	
replace afiliado_ci=1 if o31==1
recode afiliado_ci .=0 
label var afiliado_ci "Afiliado a la Seguridad Social"

***************
***formal_ci***
***************
gen byte formal_ci = .
* FIX-CHL-01 (QA 2026-04-21): o31 captures ALL health affiliates incl. FONASA A/B (subsidized);
* formal_ci based on pension contribution only (cotizando_ci), which is unambiguous.
replace formal_ci  =  1 if cotizando_ci == 1 & condocup_ci == 1
replace formal_ci = 0 if cotizando_ci == 0 & condocup_ci == 1
label var formal_ci "1=cotizante pension (FIX-CHL-01)"

g formal_1=cotizando_ci

****************
*categopri_ci  * 
**************** 
gen categopri_ci=.
replace categopri_ci=1 if o15==1
replace categopri_ci=2 if o15==2
replace categopri_ci=3 if o15>=3 & o15<=8
replace categopri_ci=4 if o15==9
replace categopri_ci=. if emp_ci!=1
label define categopri_ci 1"Patron" 2"Cuenta propia" 0"Otro"
label define categopri_ci 3"Empleado" 4" No remunerado" , add
label value categopri_ci categopri_ci
label variable categopri_ci "Categoria ocupacional en la actividad principal"

*****************
***selfempl_ci***
*****************
gen byte selfempl_ci = .
replace selfempl_ci = (categopri_ci == 2) if emp_ci == 1 & categopri_ci != .
label define selfempl_lb 1 "Cuenta propia" 0 "Otros"
label values selfempl_ci selfempl_lb
label var selfempl_ci "1 = trabajador por cuenta propia (categopri_ci == 2)"

*****************
*tipocontrato_ci*
*****************
gen tipocontrato_ci=. 
replace tipocontrato_ci=1 if  o18==1 & categopri_ci==3
replace tipocontrato_ci=2 if  (o18==2 | o18==3) & categopri_ci==3
replace tipocontrato_ci=3 if (((o19==3) | tipocontrato_ci==.) & categopri_ci==3)
label var tipocontrato_ci "Tipo de contrato segun su duracion"
label define tipocontrato_ci 1 "Permanente/indefinido" 2 "Temporal" 3 "Sin contrato/verbal" 
label value tipocontrato_ci tipocontrato_ci


	****************************
**#***VARIABLES DE INGRESO***
	****************************
****************
* ylmpri_ci    * 
****************
gen ylmpri_ci=yoprcor 
replace ylmpri_ci=. if emp_ci==0
label var ylmpri_ci "Ingreso laboral monetario actividad principal" 

****************
* ylnmpri_ci   * 
**************** 
gen ylnmpri_ci=.
label var ylnmpri_ci "Ingreso laboral NO monetario actividad principal" 

****************
* ylmsec_ci    * 
**************** 
gen ylmsec_ci=ytrabajocor-yoprcor  if emp_ci==1 
replace ylmsec_ci=. if ylmsec_ci==0
label var ylmsec_ci "Ingreso laboral monetario segunda actividad" 
 
****************
* ylnmsec_ci   * 
**************** 
gen ylnmsec_ci=.
label var ylnmsec_ci "Ingreso laboral NO monetario actividad secundaria"

****************
* ylmotros_ci  * 
**************** 
gen ylmotros_ci=.
label var ylmotros_ci "Ingreso laboral monetario de otros trabajos" 

****************
* ylnmotros_ci * 
**************** 
gen ylnmotros_ci=.
label var ylnmotros_ci "Ingreso laboral NO monetario de otros trabajos" 

****************
* nrylmpri_ci  * 
**************** 
gen nrylmpri_ci=(emp_ci==1 & ylmpri_ci==.)
replace nrylmpri_ci=. if emp_ci!=1
label var nrylmpri_ci "Id no respuesta ingreso de la actividad principal"  

****************
* ylm_ci       * 
**************** 
gen ylm_ci= ytrabajocor
replace ylm_ci=. if emp_ci!=1
label var ylm_ci "Ingreso laboral monetario total" 

****************
* ylnm_ci      * 
**************** 
gen ylnm_ci=.
label var ylnm_ci "Ingreso laboral NO monetario total"  

****************
* ynlm_ci      * 
**************** 
gen inglab =  ytrabajocor *-1
egen ynlm_ci = rsum (yautcor  inglab  ysub), missing
replace ynlm_ci=. if yautcor==. & inglab==. & ysub==. 
label var ynlm_ci "Ingreso no laboral monetario"

****************
* ytot_ci      *
****************
egen double ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci), mi
label var ytot_ci "Ingreso total monetario"


************************
* VARIABLES EDUCATIVAS *
************************

*************
***aedu_ci*** 
************* 
replace e6b = . if e6b == -88

gen aedu_ci = .

* Sin educación formal / preescolar
replace aedu_ci = 0 if inlist(e6a,1,2,3,4)

* Educación especial: mejor dejar missing por no equivalencia clara
replace aedu_ci = . if e6a==5

* Primaria / básica
replace aedu_ci = e6b if e6a==6   // primaria o preparatoria antigua (1-6)
replace aedu_ci = e6b if e6a==7   // básica moderna (1-8)

* Secundaria sistema antiguo: base 6
replace aedu_ci = e6b + 6 if inlist(e6a,8,10)

* Secundaria sistema moderno: base 8
replace aedu_ci = e6b + 8 if inlist(e6a,9,11)

* Educación superior
replace aedu_ci = e6b + 12 if inlist(e6a,12,13)

* Posgrado
replace aedu_ci = e6b + 16 if inlist(e6a,14,15)

label var aedu_ci "Anios de educacion aprobados"

*******************************************************************************
gen byte edu_isced = .

* ISCED 0: early childhood / less than primary
replace edu_isced = 0 if aedu_ci == 0

* ISCED 1: primary
replace edu_isced = 1 if inrange(aedu_ci,1,6)

* ISCED 2: lower secondary
replace edu_isced = 2 if inrange(aedu_ci,7,8)

* ISCED 3: upper secondary
replace edu_isced = 3 if inrange(aedu_ci,9,12)

* ISCED 5: short-cycle tertiary
replace edu_isced = 5 if e6a == 12

* ISCED 6: bachelor's or equivalent
replace edu_isced = 6 if e6a == 13

* ISCED 7: master's or equivalent
replace edu_isced = 7 if e6a == 14

* ISCED 8: doctoral or equivalent
replace edu_isced = 8 if e6a == 15

label define edu_isced_lbl ///
  0 "ISCED 0 Early childhood / less than primary" ///
  1 "ISCED 1 Primary" ///
  2 "ISCED 2 Lower secondary" ///
  3 "ISCED 3 Upper secondary" ///
  4 "ISCED 4 Post-secondary non-tertiary" ///
  5 "ISCED 5 Short-cycle tertiary" ///
  6 "ISCED 6 Bachelor's or equivalent" ///
  7 "ISCED 7 Master's or equivalent" ///
  8 "ISCED 8 Doctoral or equivalent", replace

label values edu_isced edu_isced_lbl


**************
*** edu_hdmf ***
**************	

gen edu_hdmf = .

* 1. Menos de primaria
replace edu_hdmf = 1 if inlist(e6a,1,2,3,4)

* 2. primaria incompleta
replace edu_hdmf = 2 if e6a==6 & inrange(e6b,1,5)
replace edu_hdmf = 2 if e6a==7 & inrange(e6b,1,5)

* 3. primaria completa
replace edu_hdmf = 3 if e6a==7 & e6b==6
replace edu_hdmf = 3 if e6a==6 & e6b==6


************************************************
* 4) Media incompleta
* - Básica 7°–8° (secundaria baja)
* - Media (nuevo) incompleta: e6a==9/11 con e6b<4
* - Secundaria (antiguo) incompleta: e6a==8/10 con e6b<6
************************************************

replace edu_hdmf = 4 if e6a==7 & inlist(e6b,7,8)

replace edu_hdmf = 4 if e6a==9  & inrange(e6b,1,3)
replace edu_hdmf = 4 if e6a==11 & inrange(e6b,1,3)

replace edu_hdmf = 4 if inlist(e6a,8,10) & inrange(e6b,1,5)

************************************************
* 5) Media completa
* - Media (nuevo) completa: e6a==9 con e6b==4
* - Media TP (nuevo) completa: e6a==11 con e6b>=4
* - Secundaria (antiguo) completa: e6a==8/10 con e6b==6
************************************************
replace edu_hdmf = 5 if e6a==9  & e6b==4
replace edu_hdmf = 5 if e6a==11 & e6b>=4 & e6b<.

replace edu_hdmf = 5 if inlist(e6a,8,10) & e6b==6


************************************************
* 6) Técnica (solo si completa; si no -> media)
************************************************
replace edu_hdmf = 6 if e6a==12 & asiste==2 & e6c_completo==1
replace edu_hdmf = 5 if e6a==12 & (asiste==1 | (asiste==2 & e6c_completo==2) | missing(e6c_completo))

************************************************
* 7) Universitaria completa (solo si completa; si no -> media)
************************************************
replace edu_hdmf = 7 if e6a==13 & asiste==2 & e6c_completo==1
replace edu_hdmf = 5 if e6a==13 & (asiste==1 | (asiste==2 & e6c_completo==2) | missing(e6c_completo))

************************************************
* 8) Posgrado (solo si completo; si no -> universitaria)
************************************************
replace edu_hdmf = 8 if inlist(e6a,14,15) & asiste==2 & e6c_completo==1
replace edu_hdmf = 7 if inlist(e6a,14,15) & (asiste==1 | (asiste==2 & e6c_completo==2) | missing(e6c_completo))


label define edu_hdmf ///
1 "Menos de primaria" ///
2 "Primaria incompleta" ///
3 "Primaria completa" ///
4 "Media incompleta" ///
5 "Media completa" ///
6 "Técnica" ///
7 "Universitaria completa" ///
8 "Posgrado", replace

label values edu_hdmf edu_hdmf
label var edu_hdmf "nivel educativo agregado hdmf"
ta edu_hdmf

***********
* ocupa_ci
* CASEN 2024: oficio1_08 = 1-digit CIUO-08 major group; oficio4_08 = 4-digit
* Use oficio1_08 directly (already the ISCO-08 major group 1-9)
***********
gen byte ocupa_ci = .
replace ocupa_ci = oficio1_08 if emp_ci == 1 & !missing(oficio1_08) & oficio1_08 > 0 & oficio1_08 < 10
label define ocupa_lbl 1 "Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary"
label values ocupa_ci ocupa_lbl
label var ocupa_ci "ISCO-08 major group (1-9), occupied only"

***********
* overqualified_ci
* edu_hdmf >= 6: técnica, university complete, or postgrad (8-level CHL scale)
* ocupa_ci >= 4: clerical, service, agriculture, craft, machine, elementary
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified"
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (tertiary educ + low-skill occ, ISCO-08 4-9)"

*********** profesion
gen profesion_ci=e7

gen byte cinef13_ci = .
replace cinef13_ci = 10 if cinef13_area==4
replace cinef13_ci = 9  if cinef13_area==1
replace cinef13_ci = 8  if cinef13_area==8
replace cinef13_ci = 7  if cinef13_area==2
replace cinef13_ci = 6  if cinef13_area==9
replace cinef13_ci = 5  if cinef13_area==7
replace cinef13_ci = 4  if cinef13_area==5
replace cinef13_ci = 3  if cinef13_area==6
replace cinef13_ci = 2  if cinef13_area==10
replace cinef13_ci = 1  if cinef13_area==3

label values cinef13_ci lbl_cinef13_ci
label define lbl_cinef13_ci ///
0  "Programas y certificaciones genéricos" ///
1  "Educación" ///
2  "Artes y Humanidades" ///
3  "Ciencias Sociales, Periodismo e Información" ///
4  "Administración de Empresas y Derecho" ///
5  "Ciencias Naturales, Matemáticas y Estadística" ///
6  "Tecnología de la Información y la Comunicación (TIC)" ///
7  "Ingeniería, Industria y Construcción" ///
8  "Agropecuario, Silvicultura, Pesca y Veterinaria" ///
9  "Salud y bienestar" ///
10 "Servicios", replace

label values cinef13_ci lbl_cinef13_ci

*====================================================*
* profesion3_ci (ISCED-F agregado 3 dígitos, consecutivo)
* a partir de subárea Chile (variable: cinef13_subarea)
*====================================================*

capture drop profesion3_ci
gen byte profesion3_ci = .

* Missing / no clasifica
replace profesion3_ci = . if inlist(cinef13_subarea, -99, -88, -66)

* Mapeo Chile subárea -> profesion3_ci (consecutiva)
replace profesion3_ci = 24 if cinef13_subarea == 1   // Salud -> 091 Salud
replace profesion3_ci = 17 if cinef13_subarea == 2   // Ingeniería y Profesiones Afines -> 071
replace profesion3_ci = 4  if cinef13_subarea == 3   // Educación -> 011
replace profesion3_ci = 26 if cinef13_subarea == 4   // Servicios personales -> 101
replace profesion3_ci = 10 if cinef13_subarea == 5   // Educación Comercial y Administración -> 041
replace profesion3_ci = 9  if cinef13_subarea == 6   // Periodismo e Información -> 032
replace profesion3_ci = 8  if cinef13_subarea == 7   // Ciencias Sociales y del Comportamiento -> 031
replace profesion3_ci = 14 if cinef13_subarea == 8   // Ciencias Físicas -> 053
replace profesion3_ci = 11 if cinef13_subarea == 9   // Derecho -> 042
replace profesion3_ci = 29 if cinef13_subarea == 10  // Servicios de Transportes -> 104
replace profesion3_ci = 19 if cinef13_subarea == 11  // Arquitectura y Construcción -> 073
replace profesion3_ci = 20 if cinef13_subarea == 12  // Agricultura -> 081 Agropecuario
replace profesion3_ci = 16 if cinef13_subarea == 13  // TIC -> 061
replace profesion3_ci = 15 if cinef13_subarea == 14  // Matemáticas y Estadísticas -> 054
replace profesion3_ci = 25 if cinef13_subarea == 15  // Bienestar -> 092
replace profesion3_ci = 5  if cinef13_subarea == 16  // Artes -> 021
replace profesion3_ci = 23 if cinef13_subarea == 17  // Veterinaria -> 084
replace profesion3_ci = 7  if cinef13_subarea == 18  // Idiomas -> 023
replace profesion3_ci = 28 if cinef13_subarea == 19  // Servicios de Seguridad -> 103
replace profesion3_ci = 12 if cinef13_subarea == 20  // Ciencias Biológicas y Afines -> 051
replace profesion3_ci = 12  if cinef13_subarea == 24  // Ciencias Nat/Mat/Est sin mayor definición (ambiguo)
replace profesion3_ci = 6  if cinef13_subarea == 21  // Humanidades -> 022
replace profesion3_ci = 27 if cinef13_subarea == 22  // Servicios de Higiene y Salud Ocupacional -> 102
replace profesion3_ci = 18 if cinef13_subarea == 23  // Industria y Producción -> 072
replace profesion3_ci = 13 if cinef13_subarea == 25  // Medio Ambiente -> 052
replace profesion3_ci = 22 if cinef13_subarea == 26  // Pesca -> 083
replace profesion3_ci = 21 if cinef13_subarea == 27  // Silvicultura -> 082

*----------------------------------------------------*
* Labels de profesion3_ci 
*----------------------------------------------------*
capture label drop lbl_profesion3_ci
label define lbl_profesion3_ci ///
    1  "Programas y certificaciones básicas" ///
    2  "Alfabetización y Aritmética Elemental" ///
    3  "Competencias personales y desarrollo" ///
    4  "Educación" ///
    5  "Artes" ///
    6  "Humanidades (excepto idiomas)" ///
    7  "Idiomas" ///
    8  "Ciencias Sociales y del Comportamiento" ///
    9  "Periodismo e Información" ///
    10 "Educación Comercial y Administración" ///
    11 "Derecho" ///
    12 "Ciencias Biológicas y afines" ///
    13 "Medio Ambiente" ///
    14 "Ciencias Físicas" ///
    15 "Matemáticas y Estadística" ///
    16 "Tecnologías de la Información y la Comunicación (TIC)" ///
    17 "Ingeniería y Profesiones afines" ///
    18 "Industria y Procesamiento" ///
    19 "Arquitectura y Construcción" ///
    20 "Agropecuario" ///
    21 "Silvicultura" ///
    22 "Pesca y acuicultura" ///
    23 "Veterinaria" ///
    24 "Salud" ///
    25 "Bienestar" ///
    26 "Servicios personales" ///
    27 "Servicios de Higiene y Salud Ocupacional" ///
    28 "Servicios de seguridad" ///
    29 "Servicios de transporte", replace

label values profesion3_ci lbl_profesion3_ci
label var profesion3_ci "Área/campo de educación (ISCED-F 2013, agregado 3 dígitos, consecutivo)"


****************
* remesas_ci   * 
**************** 
gen remesas_ci=.
label var remesas_ci "Remesas mensuales reportadas por el individuo" 

****************
* remesas_ch   * 
**************** 
gen remesas_ch=.
label var remesas_ch "Remesas mensuales del hogar"


		******************************
		*** VARIABLES DE MIGRACION ***
		******************************
 

	*******************
	*** migrante_ci ***
	*******************
	
	gen migrante_ci=(r1b==3) if r1b!=9 & !mi(r1b)
	label var migrante_ci "=1 si es migrante"
	
	**********************
	*** migrantiguo5_ci ***
	**********************
	
	gen migrantiguo5_ci=(migrante_ci==1 & r1cp>=4) if migrante_ci!=. & r1cp!=. & r1cp!=-99 & r1cp!=-88
	label var migrantiguo5_ci "=1 si es migrante antiguo (5 anos o mas)"
	

	**********************
	*** migrantelac_ci ***
	**********************
	
	gen migrantelac_ci=(inlist(r1b_pais_esp,406,408,409,412,413,414,416,417,418,420,501,502,503,505,506,508,509,512,513) & migrante_ci==1) if migrante_ci==1 & r1b_pais_esp!=999 & r1b_pais_esp!=888
	label var migrantelac_ci "=1 si es migrante proveniente de un pais LAC"
	
		
	**********************
	*** miglac_ci ***
	**********************
	
	gen miglac_ci= 1 if inlist(r1b_pais_esp,406,408,409,412,413,414,416,417,418,420,501,502,503,505,506,508,509,512,513) & migrante_ci == 1
	replace miglac_ci = 0 if miglac_ci != 1 & migrante_ci == 1
	label var miglac_ci "=1 si es migrante proveniente de un pais LAC"

	** Pais
	gen long mig_pais_code = r1b_pais_esp if migrante_ci==1
	decode r1b_pais_esp, gen(mig_pais_ci)

	*Versión 12 no acepta labels con más de 79 caracteres

	 foreach i of varlist _all {
	local longlabel: var label `i'
	local shortlabel = substr(`"`longlabel'"',1,79)
	label var `i' `"`shortlabel'"'
	}

	***************
	***jefe_ci***
	***************
	gen jefe_ci = (relacion_ci == 1)
	label var jefe_ci "Jefe de hogar"
	label def jefe_ci 1 "Si" 0 "No"
	label val jefe_ci jefe_ci

	saveold "`base_out'", replace

