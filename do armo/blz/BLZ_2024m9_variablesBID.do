clear
set more off

di "File created with the Claude HDMF system — 2026-05-13"

* -------------------------------------------------------------------------
* BLZ 2024m9 — Belize LFS September 2024 — HDMF harmonization
* Adapted from: bases armo/raw/blz/alternative_do_files/BLZ_2024m9_variablesBID.do
* Original authors: Manuel Marcos (2026)
* -------------------------------------------------------------------------

local base_dir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC"
local base_in  "`base_dir'\bases armo\raw\blz\BLZ_2024m9.dta"
local base_out "`base_dir'\bases armo\armo\BLZ\BLZ_2024m9_BID.dta"
local log_dir  "`base_dir'\do armo\blz\logs"

capture mkdir "`log_dir'"
capture mkdir "`base_dir'\bases armo\armo\BLZ"
capture log close
log using "`log_dir'\BLZ_2024m9_variablesBID.log", replace

use "`base_in'", clear


**********************************
***VARIABLES DEL IDENTIFICACION***
**********************************

	********************
	*** region_BID_c ****
	********************
	gen byte region_BID_c=.
	replace region_BID_c = 1

	********************
	*** region_c ****
	********************
	gen byte region_c = district
	label define region_c   ///
	1 "Corozal" 			///
	2 "Orange Walk"	 		///
	3 "Belize"				///
	4 "Cayo"				///
	5 "Stann Creek"			///
	6 "Toledo"
	label value region_c region_c

	*************
	* pais_c    *
	*************
	gen str3 pais_c = "BLZ"

	**************
	* periodo_c  *
	**************
	gen str10 periodo_c = "2024m9"

	******
	*anio*
	******
	gen anio_c = 2024

	******
	*mes_c*
	******
	gen int mes_c = 9

	******
	*zona*
	******
	gen zona_c= (urban_rural == 1)
	replace zona_c = . if missing(urban_rural)

	*********
	*estrato*
	*********
	gen estrato_ci=.

	 *****************************
	*unidad primaria de muestreo*
	*****************************
	gen upm_ci=.

	******************
	*idh_ch (idhogar)*
	******************
	egen idh_ch=group(_v1)
	tostring idh_ch, replace

	***************
	****idp_ci*****
	***************
	sort interview__key _v1
	by interview__key: gen _seq = _n
	egen idp_ci = concat(idh_ch _seq)
	tostring idp_ci, replace format ("%20.0f")
	drop _seq

	***********
	*factor_ci*
	***********
	gen factor_ci = final_weight

	*******************************************
	*Factor de expansion del hogar (factor_ch)*
	*******************************************
	gen factor_ch = final_weight


****************************
***VARIABLES DEMOGRAFICAS***
****************************

	*********
	*sexo_ci*
	*********
	gen byte sexo_ci = .
	replace sexo_ci = 1 if hl5 == 1
	replace sexo_ci = 2 if hl5 == 2

	*********
	*edad_ci*
	*********
	gen edad_ci = hl3

	**************
	**relacion_ci**
	**************
	gen byte relacion_ci = .
	replace relacion_ci = 1 if hl4new == 1
	replace relacion_ci = 2 if hl4new == 2
	replace relacion_ci = 3 if hl4new == 3
	replace relacion_ci = 4 if hl4new == 4
	replace relacion_ci = 5 if hl4new == 5

	*************
	*miembros_ci*
	*************
	gen miembros_ci=(relacion_ci>=1 & relacion_ci<=5)

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
	replace clasehog_ch=2 if nhijos_ch>0 & notropari_ch==0 & notronopari_ch==0
	replace clasehog_ch=2 if nhijos_ch==0 & nconyuges_ch>0 & notropari_ch==0 & notronopari_ch==0
	replace clasehog_ch=3 if notropari_ch>0 & notronopari_ch==0
	replace clasehog_ch=4 if ((nconyuges_ch>0 | nhijos_ch>0 | notropari_ch>0) & (notronopari_ch>0))
	replace clasehog_ch=5 if nhijos_ch==0 & nconyuges_ch==0 & notropari_ch==0 & notronopari_ch>0

	**************
	*nmiembros_ch*
	**************
	by idh_ch, sort: egen byte nmiembros_ch=sum(relacion_ci>0 & relacion_ci<=5)


****************************
***VARIABLES DE MERCADO LABORAL***
****************************

	*************
	*condocup_ci*
	*************
	* status: 1=Under 14, 2=Employed, 3=Unemployed, 4=PNLF, 5=DK/NS
	gen byte condocup_ci = .
	replace condocup_ci = 1 if status == 2
	replace condocup_ci = 2 if status == 3
	replace condocup_ci = 3 if status == 4
	replace condocup_ci = 4 if status == 1
	replace condocup_ci = 3 if status == 5 & edad_ci >= 14
	replace condocup_ci = 4 if status == 5 & edad_ci < 14

	**********
	***emp_ci*
	**********
	gen byte emp_ci = .
	replace emp_ci = (condocup_ci == 1) if condocup_ci != .

	***************
	***desemp_ci***
	***************
	gen byte desemp_ci = .
	replace desemp_ci = (condocup_ci == 2) if condocup_ci != .

	***************
	***inactivo_ci***
	***************
	gen byte inactivo_ci = .
	replace inactivo_ci = (condocup_ci == 3) if condocup_ci != .

	***********
	***pea_ci***
	***********
	gen byte pea_ci = .
	replace pea_ci = 1 if inlist(condocup_ci,1,2)
	replace pea_ci = 0 if inlist(condocup_ci,3,4)

	***************
	***horaspri_ci***
	***************
	gen byte horaspri_ci = .
	replace horaspri_ci = total_hrs_last_week if emp_ci == 1

	***************
	***horastot_ci ***
	***************
	gen byte horastot_ci  = .
	replace horastot_ci  = total_hrs_last_week if emp_ci == 1

	***************
	***categopri_ci ***
	***************
	* ea25: 1=Self-employed w/employees, 2=Self-employed w/o employees,
	*       3=Employee(Govt), 4=Employee(NGO), 5=Employee(Intl Org),
	*       6=Contributing family worker, 7=Domestic worker, 8=Employee(Private), 9=Apprentice
	gen byte categopri_ci = .
	replace categopri_ci = 1 if ea25 == 1 & emp_ci == 1
	replace categopri_ci = 2 if ea25 == 2 & emp_ci == 1
	replace categopri_ci = 3 if inlist(ea25, 3, 4, 5, 7, 8, 9) & emp_ci == 1
	replace categopri_ci = 4 if ea25 == 6 & emp_ci == 1

	***************
	***cotizando_ci***
	***************
	gen byte cotizando_ci = .

	***************
	***afiliado_ci***
	***************
	gen byte afiliado_ci = .

	**************
	***formal_ci***
	**************
	* informalemp: 0=formal, 100=Informally employed
	gen byte formal_ci = .
	replace formal_ci = 1 if informalemp == 0 & condocup_ci == 1
	replace formal_ci = 0 if informalemp == 100 & condocup_ci == 1

	*******************
	***tipocontrato_ci***
	*******************
	gen byte tipocontrato_ci = .

	**************
	***ocupa_ci***
	**************
	* ea23main_occ: 0=Armed Forces, 1=Managers, 2=Professionals, 3=Technicians,
	*   4=Clerical, 5=Services/Sales, 6=Skilled Agri, 7=Craft, 8=Plant/Machine,
	*   9=Elementary, 99=DK/NS
	gen byte ocupa_ci=.
	replace ocupa_ci = 1 if inlist(ea23main_occ, 2, 3) & emp_ci == 1
	replace ocupa_ci = 2 if ea23main_occ == 1 & emp_ci == 1
	replace ocupa_ci = 3 if ea23main_occ == 4 & emp_ci == 1
	replace ocupa_ci = 4 if ea23main_occ == 5 & emp_ci == 1
	replace ocupa_ci = 5 if ea23main_occ == 6 & emp_ci == 1
	replace ocupa_ci = 6 if inlist(ea23main_occ, 7, 8) & emp_ci == 1
	replace ocupa_ci = 7 if ea23main_occ == 0 & emp_ci == 1
	replace ocupa_ci = 8 if ea23main_occ == 9 & emp_ci == 1

	**************
	***salmm_ci***
	**************
	gen salmm_ci = .
	label var salmm_ci "Salario minimo legal (no disponible BLZ LFS 2024)"


****************************
***VARIABLES DE INGRESO***
****************************

	*************
	* ylmpri_ci *
	*************
	generate double ylmpri_ci = income_month if emp_ci == 1

	************
	* ylmsec_ci *
	************
	generate double ylmsec_ci = .

	**************
	* ylmotros_ci *
	**************
	generate double ylmotros_ci=.

	*********
	* ylm_ci *
	*********
	egen double ylm_ci = rowtotal(ylmpri_ci ylmsec_ci ylmotros_ci), mi

	**************
	* ylnmpri_ci *
	**************
	gen double ylnmpri_ci =.

	**************
	* ylnmsec_ci *
	**************
	gen double ylnmsec_ci = .

	****************
	* ylnmotros_ci *
	****************
	gen double ylnmotros_ci=.

	**********
	* ylnm_ci *
	**********
	egen double ylnm_ci = rowtotal(ylnmpri_ci ylnmsec_ci ylnmotros_ci), mi
	replace ylnm_ci = . if ylnm_ci < 0 & ylnm_ci != .

	**********
	* ynlm_ci *
	**********
	gen double ynlm_ci = .

	***********
	* ynlnm_ci *
	***********
	gen double ynlnm_ci = .

	**********
	* ytot_ci *
	**********
	egen double ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci ynlnm_ci), mi

	*********
	* ylm_ch *
	*********
	bysort idh_ch: egen double ylm_ch = total(ylm_ci) if miembros_ci==1

	**********
	* ylnm_ch *
	**********
	bysort idh_ch: egen double ylnm_ch = total(ylnm_ci) if miembros_ci==1

	*********
	* ynlm_ch *
	*********
	gen double ynlm_ch = .

	***********
	* ynlnm_ch *
	***********
	bysort idh_ch: egen double ynlnm_ch = total(ynlnm_ci) if miembros_ci==1

	**************
	* nrylmpri_ci *
	**************
	generate byte nrylmpri_ci = (emp_ci==1 & ylmpri_ci==.)

	**************
	* nrylmpri_ch *
	**************
	bysort idh_ch: egen byte nrylmpri_ch = max(nrylmpri_ci) if miembros_ci==1

	*************
	* remesas_ci *
	*************
	generate double remesas_ci = .

	*************
	* remesas_ch *
	*************
	generate double remesas_ch = .

	***************
	* lp_ci / lpe_ci *
	***************
	gen lp_ci  = .
	gen lpe_ci = .


****************************
***VARIABLES DE EDUCACION***
****************************

	*********
	*aedu_ci*
	*********
	gen aedu_ci = .

	replace aedu_ci = 0 if ed5 == 22  // Never Attended
	replace aedu_ci = 0 if ed5 == 21  // None

	replace aedu_ci = 1 if ed5 == 1   // Infant 1
	replace aedu_ci = 2 if ed5 == 2   // Infant 2
	replace aedu_ci = 3 if ed5 == 3   // Standard 1
	replace aedu_ci = 4 if ed5 == 4   // Standard 2
	replace aedu_ci = 5 if ed5 == 5   // Standard 3
	replace aedu_ci = 6 if ed5 == 6   // Standard 4
	replace aedu_ci = 7 if ed5 == 7   // Standard 5
	replace aedu_ci = 8 if ed5 == 8   // Standard 6

	replace aedu_ci = 9  if ed5 == 9  // 1st Form
	replace aedu_ci = 10 if ed5 == 10 // 2nd Form
	replace aedu_ci = 11 if ed5 == 11 // 3rd Form
	replace aedu_ci = 12 if ed5 == 12 // 4th Form

	replace aedu_ci = 9  if ed5 == 13 // Pre vocational
	replace aedu_ci = 10 if ed5 == 14 // Level 1 vocational
	replace aedu_ci = 11 if ed5 == 15 // Level 2 vocational

	replace aedu_ci = 12 if ed5 == 16 // Level 3 vocational (tertiary)
	replace aedu_ci = 14 if ed5 == 17 // Associate/6th Form
	replace aedu_ci = 16 if ed5 == 18 // Bachelor's
	replace aedu_ci = 18 if ed5 == 19 // Master's or Higher

	***************
	* edu_hdmf    *
	***************
	* HDMF 10-level scale derived from ed5 (Belize LFS education categories)
	gen edu_hdmf = .
	replace edu_hdmf = 1 if inlist(ed5, 21, 22)           // Never attended / none
	replace edu_hdmf = 2 if inrange(ed5, 1, 7)            // Infant 1-2, Standard 1-5 (primary incomplete)
	replace edu_hdmf = 3 if ed5 == 8                      // Standard 6 (primary complete)
	replace edu_hdmf = 4 if inlist(ed5, 9, 10, 11, 13)    // Form 1-3, pre-vocational (lower sec.)
	replace edu_hdmf = 5 if inlist(ed5, 12, 14, 15)       // Form 4, vocational L1-L2 (upper sec. incomplete)
	replace edu_hdmf = 6 if ed5 == 16                     // Vocational L3 (upper secondary complete)
	replace edu_hdmf = 7 if ed5 == 17                     // Associate / 6th Form (short-cycle tertiary)
	replace edu_hdmf = 9 if ed5 == 18                     // Bachelor's (university complete)
	replace edu_hdmf = 10 if ed5 == 19                    // Master's or higher
	label var edu_hdmf "HDMF education level (1-10)"

	***************
	* edu_isced   *
	***************
	gen edu_isced = .
	replace edu_isced = 0 if aedu_ci == 0
	replace edu_isced = 1 if aedu_ci >= 1  & aedu_ci <= 6
	replace edu_isced = 2 if aedu_ci >= 7  & aedu_ci <= 9
	replace edu_isced = 3 if aedu_ci >= 10 & aedu_ci <= 12
	replace edu_isced = 5 if aedu_ci >= 13 & aedu_ci <= 14
	replace edu_isced = 6 if aedu_ci >= 15 & aedu_ci <= 16
	replace edu_isced = 7 if aedu_ci >= 17 & aedu_ci != .
	label var edu_isced "ISCED-2011 level"


****************************
***VARIABLES DE MIGRACION***
****************************

	*****************
	*migrante_ci****
	****************
	* hl7new: 1=Belize-born; any other non-missing, non-DK value = migrant
	gen byte migrante_ci= .
	replace migrante_ci = 0 if hl7new == 1
	replace migrante_ci = 1 if hl7new != 1 & hl7new != . & hl7new != 9
	label var migrante_ci "0=native-born, 1=foreign-born"

	****************
	*migrantiguo5_ci*
	****************
	gen byte migrantiguo5_ci=.
	label var migrantiguo5_ci "=1 si migrante con 5+ anos de residencia (no disponible BLZ)"

	*************
	*mig_pais_ci*
	*************
	* hl7new country code not further identified in BLZ LFS 2024
	gen str30 mig_pais_ci = ""
	label var mig_pais_ci "Pais de nacimiento (stub - no disponible BLZ LFS 2024)"


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
