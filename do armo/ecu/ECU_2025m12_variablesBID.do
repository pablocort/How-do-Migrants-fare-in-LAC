* (Versión Stata 12)
clear
set more off
*________________________________________________________________________________________________________________*

 * Activar si es necesario (dejar desactivado para evitar sobreescribir la base y dejar la posibilidad de 
 * utilizar un loop)
 * Los datos se obtienen de las carpetas que se encuentran en el servidor: ${surveysFolder}
 * Se tiene acceso al servidor únicamente al interior del BID.
 * El servidor contiene las bases de datos MECOVI.
* ________________________________________________________________________________________________________________*
 
 
global ruta = "${surveysFolder}"
global gitFolder = "${gitFolder}"

local PAIS ECU
local ENCUESTA ENEMDU
local ANO "2025"
local ronda m12 


local log_file = "$ruta\harmonized\\`PAIS'\\`ENCUESTA'\log\\`PAIS'_`ANO'`ronda'_variablesBID.log"
local base_in  = "$ruta\survey\\`PAIS'\\`ENCUESTA'\\`ANO'\\`ronda'\data_merge\\`PAIS'_`ANO'`ronda'.dta"
local base_out = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'_`ANO'`ronda'_BID.dta"

*capture log close
*log using "`log_file'", replace 



if c(username)=="STEFFANNYR" {
use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\ecu\ECU_2025m12.dta", clear
local base_out = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'_`ANO'`ronda'_BID.dta"
}

if c(username)=="PABLOCOR" {

use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\ecu\ECU_2025m12.dta", clear
local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'_`ANO'`ronda'_BID.dta"
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
destring ciudad, gen(_ciudad)
gen region_c = .
replace region_c = int(_ciudad / 10000)
gen canton = int(_ciudad / 100)
recode region_c (14/16 = 89) (19/22 = 89)
replace region_c = 23 if canton == 1706
replace region_c = 24 if inlist(canton, 917, 915, 926)
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
drop canton _ciudad 
label variable region_c "division politico-administrativa, provincia"

*************
****pais_c***
*************
gen str3 pais_c = "ECU"
label variable pais_c "Pais"

************
***anio_c***
************
gen anio_c = 2025
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
duplicates report id_vivienda id_hogar id_persona
gen idh_ch = id_vivienda+id_hogar
label variable idh_ch "ID del hogar"

*************
****idp_ci***
*************
gen idp_ci =  id_vivienda+id_hogar+ id_persona
label variable idp_ci "ID de la persona en el hogar"

duplicates report id_vivienda id_hogar id_persona

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




		***********************************
		***VARIABLES DEL MERCADO LABORAL***
		***********************************
	
***************
**condocup_ci**
***************
*al cambiar la categoria 4 a <5 toca generar nuevamente la variable condocup caso contrario el grupo 6-9 se van a inactivos
gen condocup_ci = .
replace condocup_ci = 1 if p20 == 1 | p21 < 12 | p22 == 1 
replace condocup_ci = 2 if (p20 == 2 | p21 == 12 | p22 == 2) & p32 < 11
replace condocup_ci = 3 if condocup_ci != 1 & condocup_ci != 2
replace condocup_ci=. if !inrange(edad_ci, 15,64)
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
*Modficación SGR 15 de julio de 2018. Desde la encuesta 2017 existe una pregunta a los de 15 años y más. 
/*gen cotizando_ci=0     if condocup_ci==1 | condocup_ci==2 
replace cotizando_ci=1 if (p44f==1)  & cotizando_ci==0 /*solo a emplead@s y asalariad@s, difiere con los otros paises*/
replace cotizando_ci=1 if (p44f==1)  & p61b1<=4  & cotizando_ci==0
label var cotizando_ci "Cotizante a la Seguridad Social"
*/
gen cotizando_ci = (p44f == 1 | p61b1 <= 4) 
label var cotizando_ci "Cotizante a la Seguridad Social"


****************
***afiliado_ci**
****************
gen afiliado_ci = (p05a <= 4) /*IESS, ISSFA e ISSPOL requieren afiliación*/
label var afiliado_ci "Afiliado a la Seguridad Social"
*Nota: seguridad social comprende solo los que en el futuro me ofrecen una pension.

***************
***formal_ci***
***************
gen byte formal_ci = .

replace formal_ci  =  1 if (cotizando_ci == 1 | afiliado_ci == 1) & condocup_ci == 1
replace formal_ci = 0 if (cotizando_ci == 0 & afiliado_ci == 0) & (condocup_ci == 1 )
label var formal_ci "1=afiliado o cotizante"

*****************
*tipocontrato_ci*
*****************
gen tipocontrato_ci = . /* Solo disponible para asalariados*/
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
replace aedu_ci = p10b if p10a == 4 // Años primaria
replace aedu_ci = p10b - 1 if p10a ==5 // Años educacion básica 1 a 10 nuevos sistema - se resta uno porque considera un año de educacion inicial  
replace aedu_ci = 0 if p10a == 5 & aedu_ci == -1 // para que no queden en -1 los de 0 años aprobados 
replace aedu_ci = p10b + 6  if p10a == 6 // secundaria
replace aedu_ci = p10b + 9  if p10a == 7 // bachillerato
replace aedu_ci = p10b + 12 if p10a == 8 | p10a == 9 //superior
replace aedu_ci = p10b + 16 if p10a == 10 // posgrado

label var aedu_ci "Anios de educacion aprobados"



**************
*** edu_hdmf ***
**************	
*------------------------------------------------------------
* refinar edu_hdmf usando p3043 (titulo/diploma recibido)
* regla: p3043 solo "sube" el nivel (no lo baja)
*------------------------------------------------------------
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
replace edu_hdmf = 3 if  p10a == 5 & (p10b== 6)

* 4. Media incompleta (11°)
replace edu_hdmf = 4 if p10a == 7 & (p10b < 3)
replace edu_hdmf = 4 if p10a == 6 & (p10b < 6)
replace edu_hdmf = 4 if  p10a == 5 & (p10b < 10 & p10b > 6)

* 5. media completa (11°)
replace edu_hdmf = 5 if p10a == 7 & (p10b == 3)
replace edu_hdmf = 5 if p10a == 6 & (p10b == 6)
replace edu_hdmf = 5 if  p10a == 5 & (p10b == 10)

* 6. técnica completa (terciaria no universitaria)
replace edu_hdmf = 6 if p10a == 8 
replace edu_hdmf = 5 if p10a == 8 

* 7. universitaria completa
replace edu_hdmf = 7 if p10a == 9 & (p12a == 1)
replace edu_hdmf = 5 if p10a == 9 & (p12a == 2)

* 8	. posgrado
replace edu_hdmf = 8 if  p10a == 10 & (p12a == 1)
replace edu_hdmf = 7 if  p10a == 10 & (p12a == 2)

* missing


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


	*****************************
	**** VARIABLES MIGRACIÓN ****
	*****************************
	
*******************
*** migrante_ci ***
*******************
gen migrante_ci = (p15aa == 3)
label var migrante_ci "=1 si es migrante"
	
**********************
*** migantiguo5_ci ***
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
*pais de migrante (código)
gen mig_pais_code = .
replace mig_pais_code = p15ab if migrante_ci==1 & migrante_ci!=.

gen str40 mig_pais_ci = ""

* Rellenar según código (confirmar que se abarcan todos los países)
replace mig_pais_ci = "Argentina" if mig_pais_code==32
replace mig_pais_ci = "Bolivia"   if mig_pais_code==68
replace mig_pais_ci = "Brasil"    if mig_pais_code==76
replace mig_pais_ci = "Canadá"    if mig_pais_code==124
replace mig_pais_ci = "Chile"     if mig_pais_code==152
replace mig_pais_ci = "Colombia"  if mig_pais_code==170
replace mig_pais_ci = "Costa Rica" if mig_pais_code==188
replace mig_pais_ci = "Cuba"      if mig_pais_code==192
replace mig_pais_ci = "República Dominicana" if mig_pais_code==214
replace mig_pais_ci = "El Salvador" if mig_pais_code==222
replace mig_pais_ci = "Alemania"  if mig_pais_code==276
replace mig_pais_ci = "Honduras"  if mig_pais_code==340
replace mig_pais_ci = "India"     if mig_pais_code==356
replace mig_pais_ci = "Italia"    if mig_pais_code==380
replace mig_pais_ci = "México"    if mig_pais_code==484
replace mig_pais_ci = "Marruecos" if mig_pais_code==504
replace mig_pais_ci = "Perú"      if mig_pais_code==604
replace mig_pais_ci = "Filipinas" if mig_pais_code==608
replace mig_pais_ci = "Sudáfrica" if mig_pais_code==710
replace mig_pais_ci = "Zimbabwe"  if mig_pais_code==716
replace mig_pais_ci = "España"    if mig_pais_code==724
replace mig_pais_ci = "Ucrania"   if mig_pais_code==804
replace mig_pais_ci = "Reino Unido" if mig_pais_code==826
replace mig_pais_ci = "Estados Unidos" if mig_pais_code==840
replace mig_pais_ci = "Venezuela" if mig_pais_code==862


* (opcional) chequeo
assert  mig_pais_ci!="" if mig_pais_code!=.

 
	

/*Homologar nombre del identificador de ocupaciones (isco, ciuo, etc.) y de industrias y dejarlo en base armonizada 
para análisis de trends (en el marco de estudios sobre el futuro del trabajo)*/
*rename p41 codocupa
*rename p40 codindustria

compress

save "`base_out'", replace


