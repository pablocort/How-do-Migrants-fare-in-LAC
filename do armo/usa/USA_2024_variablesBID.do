if c(username) == "STEFFANNYR" {
	use "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\usa\usa_00004.dta", clear
	local base_out "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\USA\USA_2024_BID.dta"
}
if c(username) == "PABLOCOR" {
	use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\usa\usa_00004.dta", clear
	local base_out "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\usa\USA_2024_BID.dta"
}

	************************************************************
	* pais_c: acrónimo ISO del nombre del país de residencia   *
	************************************************************
	gen str3 pais_c="USA"
	
	*********
	*edad_ci: Edad del individuo expresada en número de años*
	*********
	gen int edad_ci=age
	replace edad_ci=. if edad_ci==99


	******************
	*idh_ch (idhogar) : Identificador único de hogares *
	******************
	cap egen idh_ch= serial
	
	***************
	****idp_ci (idindividuio) : Identificador único del individuo *****
	***************
	gen idp_ci = pernum

	*******************************************
	*Factor de expansion del hogar (factor_ch) : factor de ponderación de los hogares*
	*******************************************
	gen factor_ch= .	
	
	***********
	*factor_ci: factor de ponderación a la población total * 
	***********
	gen factor_ci=perwt

	*************
	*condocup_ci: Identifica la condición de ocupación del individuo. *
	*************
	
	/* Variable de condición de acrividad económica de la encuesta 
	
	Categorias de condocup_ci:
			1	Ocupado
			2	Desocupado
			3	Inactivo
			4	Menor que la edad límite de los entrevistados
	*/	

	gen byte condocup_ci = .
	replace condocup_ci = 1 if empstat==1     //Ocupados
	replace condocup_ci = 2 if empstat==2  & (looking==2 & availble==4)   //Desocupados
	replace condocup_ci = 3 if empstat == 3 | (empstat==2  & !(looking==2 & availble==4)) //Inactivos
	replace condocup_ci=. if !inrange(edad_ci, 15,64)

	**********
	***emp_ci: Variable dicotómica que identifica con valor 1 a los ocupados y 0 a los no ocupados y mantiene con valores perdidos a los que se muestran en la encuesta con valores perdidos*
	**********
	*Codigo Extraido del Manual
	gen byte emp_ci = .
	replace emp_ci = (condocup_ci == 1) if condocup_ci != .	
	* Notar de la manera como está definido - niños menores tendrían cero de valor -- no missing -- sino cero
	
	***************
	***desemp_ci: Variable dicotómica que identifica con valor 1 a los desocupados, 0 a los individuos que son parte del grupo de referencia y missing para el resto de la población.***
	***************	
	*Codigo estraído del manual
	gen byte desemp_ci = .
	replace desemp_ci  = (condocup_ci == 2) if condocup_ci! = .
	

	***********
	***pea_ci: Variable dicotómica que indica la población económicamente activa (PEA).***
	***********
	*Codigo extraido del manual
	gen byte pea_ci = .
	replace  pea_ci = 1 if inlist(condocup_ci,1,2) //Ocupados y Desocupados
	replace  pea_ci = 0 if condocup_ci==3 | inrange(edad_ci, 15,64) //Inactivos y menores de 15 años -
	
	**************
*** edu_hdmf ***
**************	

gen edu_hdmf = .

replace edu_hdmf = 1 if inlist(educd, 0, 1, 2, 10, 11, 12, 13, 14, 15, 16, 17)
replace edu_hdmf = 2 if inlist(educd, 20, 21, 22, 23, 24, 25)
replace edu_hdmf = 3 if educd == 26
replace edu_hdmf = 4 if inlist(educd, 30, 40, 50, 60, 61)
replace edu_hdmf = 5 if inlist(educd, 62, 63, 64)
replace edu_hdmf = 6 if inlist(educd, 65, 70, 71, 80, 81, 82, 83, 90)
replace edu_hdmf = 7 if inlist(educd, 100, 101)
replace edu_hdmf = 8 if inlist(educd, 110, 111, 112, 113, 114, 115, 116)

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
/* IPUMS ACS occ (SOC 2010 harmonized) → ISCO-08 major group (1-digit approximation)
   Based on ILO SOC→ISCO-08 crosswalk and IPUMS occupation groupings.
   Ranges verified against IPUMS ACS 2010 occupational classification:
     10-440   Management → ISCO 1
     500-2960 Professional/Scientific/Technical → ISCO 2
     3000-3540 Healthcare practitioners + protective → ISCO 3
     3600-4965 Healthcare support/food/personal care/sales → ISCO 5
     5000-5940 Office/Administrative support → ISCO 4
     6005-6130 Farming/fishing/forestry → ISCO 6
     6200-7630 Construction/extraction/installation → ISCO 7
     7700-8965 Production → ISCO 8
     9000-9750 Transportation/material moving → ISCO 9 */
***********
gen byte ocupa_ci = .
replace ocupa_ci = 1 if emp_ci == 1 & inrange(occ, 10, 440)
replace ocupa_ci = 2 if emp_ci == 1 & inrange(occ, 500, 2960)
replace ocupa_ci = 3 if emp_ci == 1 & inrange(occ, 3000, 3540)
replace ocupa_ci = 5 if emp_ci == 1 & inrange(occ, 3600, 4965)
replace ocupa_ci = 4 if emp_ci == 1 & inrange(occ, 5000, 5940)
replace ocupa_ci = 6 if emp_ci == 1 & inrange(occ, 6005, 6130)
replace ocupa_ci = 7 if emp_ci == 1 & inrange(occ, 6200, 7630)
replace ocupa_ci = 8 if emp_ci == 1 & inrange(occ, 7700, 8965)
replace ocupa_ci = 9 if emp_ci == 1 & inrange(occ, 9000, 9750)
label define ocupa_lbl 1 "Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary"
label values ocupa_ci ocupa_lbl
label var ocupa_ci "ISCO-08 major group (SOC 2010 → ISCO-08 crosswalk, 1-digit approx)"

***********
* overqualified_ci
* edu_hdmf >= 6: técnica (associates/some college+), university complete, postgrad
* NOTE: USA edu_hdmf=6 includes "some college no degree" — approx. includes non-completers
* ocupa_ci >= 4: clerical, service, agriculture, craft, machine, elementary
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified"
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (tertiary educ + low-skill occ, SOC→ISCO-08)"

***********************************************************************
	*****************************
	**** VARIABLES MIGRACIÓN ****
	*****************************
	
*******************
*** migrante_ci ***
*******************
gen migrante_ci = (yrimmig != 9999) & (bpl>150)
label var migrante_ci "=1 si es migrante"
	
**********************
*** migantiguo5_ci ***
**********************
gen migrantiguo5_ci = . // modificar despues con el a;o de migracion
label var migrantiguo5_ci "=1 si es migrante antiguo (5 anos o mas)"
		
**********************
*** miglac_ci ***
**********************
gen miglac_ci = . // limpiar depsues 

label var miglac_ci "=1 si es migrante proveniente de un pais LAC"

**********************
*** mig_pais_code ***
**********************
*pais de migrante (código)
gen mig_pais_code = .
replace mig_pais_code = bpld if migrante_ci==1 & migrante_ci!=.

decode bpld, gen(mig_pais_ci) 
replace mig_pais_ci="" if migrante_ci!=1

* Rellenar según código (confirmar que se abarcan todos los países)

*********************
***relacion_ci***
*********************
* In IPUMS ACS, pernum==1 is always the household head/householder.
* Full relate mapping requires 'relate' variable in the extract;
* if present, use it; otherwise pernum==1 identifies the head.
gen byte relacion_ci = .
capture replace relacion_ci = 1 if relate == 101
capture replace relacion_ci = 2 if relate == 201
capture replace relacion_ci = 3 if inlist(relate, 301, 302, 303)
capture replace relacion_ci = 4 if relate == 501
capture replace relacion_ci = 5 if inlist(relate, 401, 601, 701)
capture replace relacion_ci = 6 if inlist(relate, 801, 901, 1000)
* Fallback: if relate not in extract, use pernum==1 for head
replace relacion_ci = 1 if pernum == 1 & relacion_ci == .
label var relacion_ci "Relacion con jefe del hogar (1=jefe, ...)"

***************
***jefe_ci***
***************
gen jefe_ci = (relacion_ci == 1)
label var jefe_ci "Jefe de hogar"
label def jefe_ci 1 "Si" 0 "No"
label val jefe_ci jefe_ci

************************************************************************


capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\usa"
save "`base_out'", replace
