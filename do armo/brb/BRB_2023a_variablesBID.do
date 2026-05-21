clear
set more off

di "File created with the Claude HDMF system — 2026-05-13"

* -------------------------------------------------------------------------
* BRB 2023a — Barbados LFS 2023 Annual — HDMF harmonization
* Adapted from: bases armo/raw/brb/alternative_do_files/BRB_2023a_variablesBID.do
* Original authors: Ricardo Sierra, Oscar Jaramillo
* HDMF changes:
*   - Derived migrante_ci from CNTRY_CD / Ntlty (was stub in alt file)
*   - Fixed condocup_ci: inlist(actvstat,31,32,33) — missing comma in alt file
*   - Fixed pea_ci: second replace corrected to pea_ci=0 for condocup_ci 3,4
*   - Fixed ylnm_ci: use rowtotal(...),mi instead of simple addition
*   - Added edu_hdmf from EDUCLEV, edu_isced, inactivo_ci, periodo_c
* -------------------------------------------------------------------------

local base_dir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC"
local base_in  "`base_dir'\bases armo\raw\brb\BRB_2023a.dta"
local base_out "`base_dir'\bases armo\armo\BRB\BRB_2023a_BID.dta"
local log_dir  "`base_dir'\do armo\brb\logs"

capture mkdir "`log_dir'"
capture mkdir "`base_dir'\bases armo\armo\BRB"
capture log close
log using "`log_dir'\BRB_2023a_variablesBID.log", replace

use "`base_in'", clear


**********************************
***VARIABLES DEL IDENTIFICACION***
**********************************

	********************
	*** region_BID_c ****
	********************
	gen byte region_BID_c=2

	***************
	* REGION PAIS *
	***************
	g region_c=PARNO

	***********
	*  PAIS   *
	***********
	gen pais_c="BRB"

	**************
	* periodo_c  *
	**************
	gen str10 periodo_c = "2023a"

	***********
	*  ANIO   *
	***********
	gen anio_c = 2023

	**********************
	* MES DE LA ENCUESTA *
	**********************
	gen mes_c = .

	***************
	*    ZONA     *
	***************
	gen byte zona_c=.

	***************
	* estrato_ci  *
	***************
	gen byte estrato_ci = STRATUM

	**********************
	******** UPM  ********
	**********************
	gen upm_ci = .

******************************
*  IDENTIFICADOR DEL HOGAR   *
******************************
	egen idh_ch = concat(RNDNO EDNO PARNO STRATUM HHNO)
	tostring idh_ch, replace

*******************************
* IDENTIFICADOR DEL INDIVIDUO *
*******************************
	egen idp_ci = concat(RNDNO EDNO PARNO STRATUM HHNO INDIVNO)
	tostring idp_ci, replace

*************************
* factor_ch *
*************************
	gen factor_ch = Wtfactor

	*************************
	* factor_ci *
	*************************
	gen factor_ci = factor_ch


****************************
***VARIABLES DEMOGRAFICAS***
****************************

	***********
	*  SEXO   *
	***********
	gen sexo_ci = LSEX

	***********
	*  EDAD   *
	***********
	gen edad_ci=LAGE

	************************************
	*  RELACION CON EL JEFE DE HOGAR   *
	************************************
	gen relacion_ci = .
	replace relacion_ci = 1 if RELHD == 0
	replace relacion_ci = 2 if RELHD == 1
	replace relacion_ci = 3 if inlist(RELHD, 2, 3)
	replace relacion_ci = 4 if RELHD == 4
	replace relacion_ci = 5 if inlist(RELHD, 5, 6, 8)

	******************
	** miembros_ci **
	*****************
	gen miembros_ci=(relacion_ci>=1 & relacion_ci<=5)
	replace miembros_ci=1 if (relacion_ci>=1 & relacion_ci<=4)

	*********
	*jefe_ci*
	*********
	gen byte jefe_ci=.
	replace jefe_ci = 1 if (relacion_ci==1)
	replace jefe_ci = 0 if (relacion_ci!=1) & (relacion_ci!=.)

	**************
	*nconyuges_ch*
	**************
	by idh_ch, sort: egen nconyuges_ch=sum(relacion_ci==2)
	replace nconyuges_ch =. if relacion_ci==.

	***********
	*nhijos_ch*
	***********
	by idh_ch, sort: egen byte nhijos_ch=sum(relacion_ci==3)
	replace nhijos_ch =. if relacion_ci==.

	**************
	*notropari_ch*
	**************
	by idh_ch, sort: egen byte notropari_ch=sum(relacion_ci==4)
	replace notropari_ch =. if relacion_ci==.

	**************
	*notronopari_ch*
	**************
	by idh_ch, sort: egen byte notronopari_ch=sum(relacion_ci==5)
	replace notronopari_ch=. if relacion_ci==.

	****************
	*nempdom_ch*
	****************
	by idh_ch, sort: egen byte nempdom_ch=sum(relacion_ci==6)
	replace nempdom_ch =. if relacion_ci==.

	*************
	*clasehog_ch*
	*************
	gen byte clasehog_ch=0
	replace clasehog_ch=1 if nhijos_ch==0 & nconyuges_ch==0 & notropari_ch==0 & notronopari_ch==0
	replace clasehog_ch=2 if (nhijos_ch>0| nconyuges_ch>0) & (notropari_ch==0 & notronopari_ch==0)
	replace clasehog_ch=3 if notropari_ch>0 & notronopari_ch==0
	replace clasehog_ch=4 if ((nconyuges_ch>0 | nhijos_ch>0 | notropari_ch>0) & (notronopari_ch>0))
	replace clasehog_ch=5 if nhijos_ch==0 & nconyuges_ch==0 & notropari_ch==0 & notronopari_ch>0

	**************
	*nmiembros_ch*
	**************
	by idh_ch, sort: egen byte nmiembros_ch=sum(relacion_ci>0 & relacion_ci<=5)


	**********************************
	***VARIABLES DE MERCADO LABORAL***
	**********************************

	**************************
	* CONDICION DE OCUPACION *
	**************************
	* Fixed: inlist(actvstat, 31, 32, 33) — alt file was missing comma before 33
	gen condocup_ci = .
	replace condocup_ci = 1 if actvstat == 10
	replace condocup_ci = 2 if actvstat == 20
	replace condocup_ci = 3 if inlist(actvstat, 31, 32, 33)
	replace condocup_ci = 4 if edad_ci < 15

	************
	* OCUPADO  *
	************
	gen emp_ci = (condocup_ci == 1)

	***************
	* DESOCUPADO  *
	***************
	gen desemp_ci = .
	replace desemp_ci = 1 if condocup_ci == 2
	replace desemp_ci = 0 if condocup_ci != 2 & condocup_ci != .

	***************
	* inactivo_ci *
	***************
	gen byte inactivo_ci = .
	replace inactivo_ci = (condocup_ci == 3) if condocup_ci != .

	***********************************
	* POBLACION ECONOMICAMENTE ACTIVA *
	***********************************
	* Fixed: alt file had two replace=1 lines; second should be replace=0 for inactive/below-age
	gen pea_ci = .
	replace pea_ci=1 if inlist(condocup_ci, 1, 2)
	replace pea_ci=0 if inlist(condocup_ci, 3, 4)

	**********************************************
	* HORAS TRABAJADAS EN LA ACTIVIDAD PRINCIPAL *
	**********************************************
	gen horaspri_ci = .
	replace horaspri_ci = 0    if condocup_ci == 1 & HRSWRKD == 1
	replace horaspri_ci = 2.5  if condocup_ci == 1 & HRSWRKD == 2
	replace horaspri_ci = 7    if condocup_ci == 1 & HRSWRKD == 3
	replace horaspri_ci = 12   if condocup_ci == 1 & HRSWRKD == 4
	replace horaspri_ci = 17   if condocup_ci == 1 & HRSWRKD == 5
	replace horaspri_ci = 22   if condocup_ci == 1 & HRSWRKD == 6
	replace horaspri_ci = 27   if condocup_ci == 1 & HRSWRKD == 7
	replace horaspri_ci = 32   if condocup_ci == 1 & HRSWRKD == 8
	replace horaspri_ci = 37   if condocup_ci == 1 & HRSWRKD == 9
	replace horaspri_ci = 42   if condocup_ci == 1 & HRSWRKD == 10
	replace horaspri_ci = 48   if condocup_ci == 1 & HRSWRKD == 11

	**************************
	* TOTAL HORAS TRABAJADAS *
	**************************
	gen horastot_ci = horaspri_ci

	*********************************
	* CATEGORIA OCUPACION PRINCIPAL *
	*********************************
	gen categopri_ci = .
	replace categopri_ci = 1 if condocup_ci == 1 & EMPLSTAT == 1
	replace categopri_ci = 2 if condocup_ci == 1 & EMPLSTAT == 4
	replace categopri_ci = 3 if condocup_ci == 1 & inlist(EMPLSTAT, 2, 3, 6)
	replace categopri_ci = 0 if condocup_ci == 1 & EMPLSTAT == 7

	*********************************
	*  COTIZA A LA SEGURIDAD SOCIAL *
	*********************************
	gen cotizando_ci = .

	**********************************
	* AFILIADO A LA SEGURIDAD SOCIAL *
	**********************************
	gen afiliado_ci = .

	*********************
	* TRABAJADOR FORMAL *
	*********************
	gen byte formal_ci = .
	replace formal_ci = 1 if (cotizando_ci==1|afiliado_ci==1) & condocup_ci==1
	replace formal_ci = 0 if cotizando_ci==0 & (condocup_ci==1 | condocup_ci==2)

	********************
	* TIPO DE CONTRATO *
	********************
	gen tipocontrato_ci = .

	*****************************
	* TIPO DE OCUPACION LABORAL *
	*****************************
	gen ocupa_ci = .
	gen occ1d = floor(OCCUP/1000)
	gen occ2d = floor(OCCUP/100)
	replace ocupa_ci = 1 if condocup_ci == 1 & inlist(occ1d, 2, 3)
	replace ocupa_ci = 2 if condocup_ci == 1 & occ1d == 1
	replace ocupa_ci = 3 if condocup_ci == 1 & occ1d == 4
	replace ocupa_ci = 4 if condocup_ci == 1 & inlist(occ2d, 52)
	replace ocupa_ci = 5 if condocup_ci == 1 & occ1d == 5 & ocupa_ci == .
	replace ocupa_ci = 6 if condocup_ci == 1 & occ1d == 6
	replace ocupa_ci = 7 if condocup_ci == 1 & inlist(occ1d, 7, 8, 9)
	replace ocupa_ci = 8 if condocup_ci == 1 & occ1d == 0
	drop occ1d occ2d

	**************
	* salmm_ci   *
	**************
	gen salmm_ci = .
	label var salmm_ci "Salario minimo legal (no disponible BRB LFS 2023)"

	***************
	* lp_ci / lpe *
	***************
	gen lp_ci  = .
	gen lpe_ci = .


****************************
***VARIABLES DE INGRESO***
****************************

	*************************************
	* INGRESO MONETARIO MENSUAL LABORAL *
	*************************************
	gen double ylmpri_ci = .
	replace ylmpri_ci = 140    *(52/12) if condocup_ci == 1 & EARNGS == 1
	replace ylmpri_ci = 249.5  *(52/12) if condocup_ci == 1 & EARNGS == 2
	replace ylmpri_ci = 349.5  *(52/12) if condocup_ci == 1 & EARNGS == 3
	replace ylmpri_ci = 449.5  *(52/12) if condocup_ci == 1 & EARNGS == 4
	replace ylmpri_ci = 549.5  *(52/12) if condocup_ci == 1 & EARNGS == 5
	replace ylmpri_ci = 649.5  *(52/12) if condocup_ci == 1 & EARNGS == 6
	replace ylmpri_ci = 749.5  *(52/12) if condocup_ci == 1 & EARNGS == 7
	replace ylmpri_ci = 849.5  *(52/12) if condocup_ci == 1 & EARNGS == 8
	replace ylmpri_ci = 949.5  *(52/12) if condocup_ci == 1 & EARNGS == 9
	replace ylmpri_ci = 1150   *(52/12) if condocup_ci == 1 & EARNGS == 10
	replace ylmpri_ci = 1625   *(52/12) if condocup_ci == 1 & EARNGS == 11
	replace ylmpri_ci = . if condocup_ci == 1 & EARNGS == 99
	replace ylmpri_ci = 0 if categopri_ci == 4
	replace ylmpri_ci = 0 if condocup_ci != 1 & condocup_ci != .

	*************************************************
	* INGRESO MONETARIO MENSUAL ACTIVIDAD SECUNDARIA*
	*************************************************
	gen ylmsec_ci = .

	************************************
	* INGRESO MENSUAL OTRAS ACTIVIDADES*
	************************************
	gen ylmotros_ci=.

	************************************
	* INGRESO MENSUAL TODAS ACTIVIDADES*
	************************************
	egen double ylm_ci = rowtotal(ylmpri_ci ylmsec_ci ylmotros_ci), mi

	*******************************
	* INGRESO MENSUAL NO MONETARIO*
	*******************************
	gen ylnmpri_ci = .
	gen ylnmsec_ci=.
	gen ylnmotros_ci=.

	*************************************************
	* INGRESO MENSUAL NO MONETARIO TODAS ACTIVIDADES*
	* Fixed: use rowtotal(...),mi to handle missing values
	*************************************************
	egen double ylnm_ci = rowtotal(ylnmpri_ci ylnmsec_ci ylnmotros_ci), mi

	*************************************************
	* INGRESO MENSUAL NO LABORAL
	*************************************************
	gen ynlm_ci = .
	gen ynlnm_ci= .

	***********
	* ytot_ci *
	***********
	egen double ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci ynlnm_ci), mi

	************************************
	* INGRESO MENSUAL LABORAL DEL HOGAR*
	************************************
	bysort idh_ch: egen double ylm_ch = total(ylm_ci) if miembros_ci==1

	**************************************************
	* INGRESO MENSUAL LABORAL NO MONETARIO DEL HOGAR *
	**************************************************
	bysort idh_ch: egen double ylnm_ch = total(ylnm_ci) if miembros_ci==1

	**************************************************
	* INGRESO MENSUAL NO LABORAL MONETARIO DEL HOGAR *
	**************************************************
	gen ynlm_ch = .

	*****************************************************
	* INGRESO MENSUAL NO LABORAL NO MONETARIO DEL HOGAR *
	*****************************************************
	bysort idh_ch: egen double ynlnm_ch = total(ynlnm_ci) if miembros_ci==1

	*******************
	*** nrylmpri_ci ***
	*******************
	gen byte nrylmpri_ci = .
	replace nrylmpri_ci = 1 if ylmpri_ci == . & emp_ci == 1
	replace nrylmpri_ci = 0 if ylmpri_ci != . & emp_ci == 1

	*******************
	*** nrylmpri_ch ***
	*******************
	by idh_ch, sort: egen byte nrylmpri_ch = sum(nrylmpri_ci) if miembros_ci==1
	replace nrylmpri_ch = 1 if nrylmpri_ch > 0 & nrylmpri_ch < .

	***************************
	* REMESAS EN MONEDA LOCAL *
	***************************
	gen remesas_ci = .

	************************************
	* REMESAS EN MONEDA LOCAL DEL HOGAR*
	************************************
	by idh_ch, sort: egen byte remesas_ch = sum(remesas_ci) if miembros_ci == 1


****************************
***VARIABLES DE EDUCACION***
****************************

	*************
	***aedu_ci***
	*************
	gen aedu_ci = .
	replace aedu_ci = 0  if EDUCLEV == 0   // No schooling
	replace aedu_ci = 3  if EDUCLEV == 1   // Primary (complete)
	replace aedu_ci = 9  if EDUCLEV == 2   // Secondary
	replace aedu_ci = 13 if EDUCLEV == 3   // Post-secondary / A-levels
	replace aedu_ci = 14 if EDUCLEV == 4   // University+
	replace aedu_ci = .  if EDUCLEV == 5
	replace aedu_ci = .  if EDUCLEV == 9

	***************
	* edu_hdmf    *
	***************
	* HDMF 10-level scale — coarse (BRB LFS has only 5 education categories)
	gen edu_hdmf = .
	replace edu_hdmf = 1 if EDUCLEV == 0   // No schooling
	replace edu_hdmf = 3 if EDUCLEV == 1   // Primary complete
	replace edu_hdmf = 5 if EDUCLEV == 2   // Secondary complete
	replace edu_hdmf = 6 if EDUCLEV == 3   // Post-secondary / A-levels
	replace edu_hdmf = 9 if EDUCLEV == 4   // University+
	replace edu_hdmf = . if inlist(EDUCLEV, 5, 9)
	label var edu_hdmf "HDMF education level (1-10, coarse — BRB has 5 categories only)"

	***************
	* edu_isced   *
	***************
	gen edu_isced = .
	replace edu_isced = 0 if EDUCLEV == 0
	replace edu_isced = 1 if EDUCLEV == 1
	replace edu_isced = 2 if EDUCLEV == 2 & aedu_ci < 11
	replace edu_isced = 3 if EDUCLEV == 2 & aedu_ci >= 11
	replace edu_isced = 3 if EDUCLEV == 3
	replace edu_isced = 6 if EDUCLEV == 4
	replace edu_isced = . if inlist(EDUCLEV, 5, 9)
	label var edu_isced "ISCED-2011 level (coarse — BRB 5-cat education)"


****************************
***VARIABLES DE MIGRACION***
****************************

	*****************
	*migrante_ci****
	****************
	* Derived from CNTRY_CD (0=Barbadian national) and Ntlty (0=Barbados, 9=not stated)
	* Nationality proxy — birthplace variable not available in BRB LFS 2023
	gen byte migrante_ci = .
	replace migrante_ci = 0 if CNTRY_CD == 0
	replace migrante_ci = 1 if CNTRY_CD != 0 & CNTRY_CD != .
	replace migrante_ci = . if Ntlty == 9
	label var migrante_ci "0=Barbadian national, 1=foreign national (nationality proxy)"

	****************
	*migrantiguo5_ci*
	****************
	gen byte migrantiguo5_ci=.
	label var migrantiguo5_ci "=1 si migrante con 5+ anos de residencia (no disponible BRB)"

	*************
	*mig_pais_ci*
	*************
	* CNTRY_CD_OTHER contains country of origin as string for non-BRB nationals
	gen str30 mig_pais_ci = ""
	capture replace mig_pais_ci = CNTRY_CD_OTHER if migrante_ci == 1 & CNTRY_CD_OTHER != ""
	label var mig_pais_ci "Pais de origen (string, de CNTRY_CD_OTHER)"


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
