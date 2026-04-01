use "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\usa\usa_00004.dta", clear

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
	
************************************************************************
	
	
save "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\USA_2024_BID.dta", replace
