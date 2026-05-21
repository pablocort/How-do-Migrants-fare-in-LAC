clear
set more off

di "File created with the Claude HDMF system — 2026-05-13"

* -------------------------------------------------------------------------
* SUR 2022a — Suriname SLC 2022 Annual — HDMF harmonization
* Adapted from: bases armo/raw/sur/alternative_do_files/SUR_2022a_variablesBID.do
* Original authors: Eric Torres, Angela Lopez, Pia Locco, Agustina Thailinger
* HDMF changes:
*   - Fixed lp_ci: replaced erroneous `replace lp=` with `replace lp_ci=`
*   - Removed duplicate migantiguo5_ci (kept only migrantiguo5_ci — second definition)
*   - Fixed ynlm_ci: replaced undefined `remesas` variable with `remesasaux`
*   - Removed external do file call (Labels&ExternalVars_Harmonized_DataBank.do)
*   - Added edu_hdmf, edu_isced, inactivo_ci, mig_pais_ci, periodo_c
* -------------------------------------------------------------------------

local base_dir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC"
local base_in  "`base_dir'\bases armo\raw\sur\SUR_2022a.dta"
local base_out "`base_dir'\bases armo\armo\SUR\SUR_2022a_BID.dta"
local log_dir  "`base_dir'\do armo\sur\logs"

capture mkdir "`log_dir'"
capture mkdir "`base_dir'\bases armo\armo\SUR"
capture log close
log using "`log_dir'\SUR_2022a_variablesBID.log", replace

use "`base_in'", clear


		*************************
		***VARIABLES DEL HOGAR***
		*************************

************
* Region_BID *
************
gen region_BID_c=.
replace region_BID_c=2
label var region_BID_c "Regiones BID"
label define region_BID_c 1 "Centroamerica_(CID)" 2 "Caribe_(CCB)" 3 "Andinos_(CAN)" 4 "Cono_Sur_(CSC)"
label value region_BID_c region_BID_c

	***************
	***region_c ***
	***************
	clonevar region_c=domain
	label var region_c "division politico-administrativa, provincia"

	***************
	***factor_ch***
	***************
	gen factor_ch=weight2
	label variable factor_ch "Factor de expansion del hogar"

	*************
	****idh_ch***
	*************
	clonevar idh_ch = hhid
	label variable idh_ch "ID del hogar"
tostring idh_ch, replace

	*************
	****idp_ci***
	*************
	gen idp_ci=memberid
	label variable idp_ci "ID de la persona en el hogar"
tostring idp_ci, replace

	duplicates re idh_ch idp_ci

	*************
	****zona_c***
	*************
	gen zona_c=.

	*************
	****pais_c***
	*************
	gen str3 pais_c="SUR"
	label variable pais_c "Pais"

	**************
	* periodo_c  *
	**************
	gen str10 periodo_c = "2022a"

	************
	***anio_c***
	************
	gen anio_c=2022
	label variable anio_c "Anio de la encuesta"

	***********
	***mes_c***
	***********
	gen mes_c=.
	label var mes_c "Mes de la encuesta"

	*****************
	***relacion_ci***
	*****************
	gen relacion_ci=1     if q01_02==1
	replace relacion_ci=2 if q01_02==2
	replace relacion_ci=3 if q01_02==3
	replace relacion_ci=4 if q01_02>=4 & q01_02<=8
	replace relacion_ci=5 if q01_02==10
	replace relacion_ci=6 if q01_02==9
	label variable relacion_ci "Relacion con el jefe del hogar"


	    ****************************
		***VARIABLES DEMOGRAFICAS***
		****************************

	***************
	***factor_ci***
	***************
	gen factor_ci=weight2
	label variable factor_ci "Factor de expansion del individuo"

	***************
	***upm_ci***
	***************
	clonevar upm_ci=psu
	label variable upm_ci "Unidad Primaria de Muestreo"

	***************
	***estrato_ci***
	***************
	clonevar estrato_ci=stratum
	label variable estrato_ci "Estrato"

	*************
	***sexo_ci***
	*************
	gen sexo_ci=q01_03
	label var sexo_ci "Sexo del individuo"

	**********
	***edad***
	**********
	gen edad_ci=q01_04 if q01_04<99
	label variable edad_ci "Edad del individuo"

	**************
	***civil_ci***
	**************
	gen civil_ci=1 		if q01_09==1
	replace civil_ci=2	if q01_09==2 | q01_09==3
	replace civil_ci=3	if q01_09==4 | q01_09==5
	replace civil_ci=4	if q01_09==6
	label var civil_ci "Estado civil"

	*************
	***jefe_ci***
	*************
	gen jefe_ci=(relacion_ci==1)
	label var jefe_ci "Jefe de hogar"

	******************
	***nconyuges_ch***
	******************
	by idh_ch, sort: egen nconyuges_ch=sum(relacion_ci==2)

	***************
	***nhijos_ch***
	***************
	by idh_ch, sort: egen nhijos_ch=sum(relacion_ci==3)

	******************
	***notropari_ch***
	******************
	by idh_ch, sort: egen notropari_ch=sum(relacion_ci==4)

	********************
	***notronopari_ch***
	********************
	by idh_ch, sort: egen notronopari_ch=sum(relacion_ci==5)

	****************
	***nempdom_ch***
	****************
	by idh_ch, sort: egen nempdom_ch=sum(relacion_ci==6)

	*****************
	***clasehog_ch***
	*****************
	gen byte clasehog_ch=0
	replace clasehog_ch=1 if nhijos_ch==0 & nconyuges_ch==0 & notropari_ch==0 & notronopari_ch==0
	replace clasehog_ch=2 if (nhijos_ch>0| nconyuges_ch>0) & (notropari_ch==0 & notronopari_ch==0)
	replace clasehog_ch=3 if ((clasehog_ch ==2 & notropari_ch>0) & notronopari_ch==0) |(notropari_ch>0 & notronopari_ch==0)
	replace clasehog_ch=4 if ((nconyuges_ch>0 | nhijos_ch>0 | notropari_ch>0) & (notronopari_ch>0))
	replace clasehog_ch=5 if nhijos_ch==0 & nconyuges_ch==0 & notropari_ch==0 & notronopari_ch>0

	******************
	***nmiembros_ch***
	******************
by idh_ch, sort: egen byte nmiembros_ch=sum(relacion_ci>0 & relacion_ci<=5)

	*****************
	***miembros_ci***
	*****************
	gen miembros_ci=(relacion_ci>=1 & relacion_ci<=5)
	label variable miembros_ci "Miembro del hogar"




			***********************************
			***VARIABLES DEL MERCADO LABORAL***
			***********************************

	****************
	****condocup_ci*
	****************
	generat condocup_ci=.
	replace condocup_ci=1 if q09_06==1 | q09_07==1 | q09_08==1
	replace condocup_ci=2 if (q09_06==2 | q09_07==2 | q09_08==2) & q09_29==1
	replace condocup_ci=3 if condocup_ci!=1 & condocup_ci!=2
	replace condocup_ci=4 if edad_ci<15
	label define condocup_ci 1 "ocupados" 2 "desocupados" 3 "inactivos" 4 "menor <15"
	label value condocup_ci condocup_ci
	label var condocup_ci "Condicion de ocupacion"

	****************
	*afiliado_ci****
	****************
	gen afiliado_ci=(q09_16a==1 | q09_36b==1 | q09_36c==1 | q09_36d==1 | q09_36e==1)
	replace afiliado_ci=. if q09_16a==. & q09_36b==. & q09_36c==. & q09_36d==. & q09_36e==.
	label var afiliado_ci "Afiliado a la Seguridad Social"

	****************
	*cotizando_ci***
	****************
	gen cotizando_ci=0     if condocup_ci==1 | condocup_ci==2
	replace cotizando_ci=1 if afiliado_ci==1
	label var cotizando_ci "Cotizante a la Seguridad Social"

	****************
	*instpen_ci*****
	****************
	gen instpen_ci=.
	gen tipopen_ci=.

	********************
	*** instcot_ci *****
	********************
	gen instcot_ci=.

	*************
	*tamemp_ci
	*************
	gen tamemp_ci=.
	replace tamemp_ci=1 if q09_14>=1 & q09_14<=2
	replace tamemp_ci=2 if q09_14>=3 & q09_14<=4
	replace tamemp_ci=3 if q09_14>=5 & q09_14!=.

	*************
	**pension_ci*
	*************
	gen pension_ci=0
	replace pension_ci=1 if q10_08>0 | q10_09>0 | q10_10>0 | q10_11>0 | q10_12>0
	replace pension_ci=. if q10_08==. & q10_09==. & q10_10==. & q10_11==. & q10_12==.

	*************
	*ypen_ci*****
	*************
	egen ypen_ci=rowtotal(q10_08 q10_09 q10_10 q10_11 q10_12) if pension_ci==1
	replace ypen_ci=. if ypen_ci==999999

	***************
	*pensionsub_ci*
	***************
	gen pensionsub_ci=0
	replace pensionsub_ci=(q10_07>0) if q10_07!=.

	*****************
	**  ypensub_ci  *
	*****************
	gen ypensub_ci=q10_07 if pensionsub_ci==1 & q10_07!=.
	replace ypensub_ci=. if ypensub_ci==999999

	*************
	*cesante_ci*
	*************
	cap clonevar trabant = q09_34
	generat cesante_ci=0 if condocup_ci==2 & trabant!=.
	replace cesante_ci=1 if (trabant!=1 & trabant!=.) & condocup_ci==2

	*********
	*lp_ci***
	*********
	* Fixed: original alt file had `replace lp=` (undefined var); corrected to `replace lp_ci=`
	gen lp_ci =.
	replace lp_ci=	733.1	if region_c==	1
	replace lp_ci=	590.23	if region_c==	2
	replace lp_ci=	533.27	if region_c==	3
	label var lp_ci "Linea de pobreza oficial del pais"

	***********
	*lpe_ci ***
	***********
	gen lpe_ci = .
	replace lpe_ci=	265.29	if region_c==	1
	replace lpe_ci=	250.48	if region_c==	2
	replace lpe_ci=	206.69	if region_c==	3
	label var lpe_ci "Linea de indigencia oficial del pais"

	*************
	**salmm_ci***
	*************
	gen salmm_ci= 835
	label var salmm_ci "Salario minimo legal"

	************
	***emp_ci***
	************
	gen byte emp_ci=(condocup_ci==1)
	label var emp_ci "Ocupado (empleado)"

	****************
	***desemp_ci***
	****************
	gen desemp_ci=(condocup_ci==2)
	label var desemp_ci "Desempleado que busco empleo en el periodo de referencia"

	***************
	***inactivo_ci***
	***************
	gen byte inactivo_ci = .
	replace inactivo_ci = (condocup_ci == 3) if condocup_ci != .
	label var inactivo_ci "Inactivo (condocup_ci==3)"

	*************
	***pea_ci***
	*************
	gen pea_ci=0
	replace pea_ci=1 if emp_ci==1 | desemp_ci==1
	label var pea_ci "Poblacion Economicamente Activa"

	*****************
	***desalent_ci***
	*****************
	cap clonevar bustrama=q09_29
	cap clonevar motnobus = q09_30
	gen desalent_ci=(motnobus==6 | motnobus==3)
	label var desalent_ci "Trabajadores desalentados"

	*****************
	***horaspri_ci***
	*****************
	gen horaspri_ci=q09_23h
	replace horaspri_ci=. if q09_23h==999
	replace horaspri_ci=. if emp_ci==0
	label var horaspri_ci "Horas trabajadas semanalmente en el trabajo principal"

	*****************
	***horastot_ci***
	*****************
	gen horastot_ci=horaspri_ci if emp_ci==1
	label var horastot_ci "Horas trabajadas semanalmente en todos los empleos"

	***************
	***subemp_ci***
	***************
	gen subemp_ci=0
	replace subemp_ci=1 if q09_26==1 & q09_25==1 & horastot_ci<=30 & emp_ci==1
	label var subemp_ci "Personas en subempleo por horas"

	*******************
	***tiempoparc_ci***
	*******************
	gen tiempoparc_ci=((horastot_ci>=1 & horastot_ci<30) & q09_25==2 & emp_ci==1)
	replace tiempoparc_ci=. if emp_ci==0

	******************
	***categopri_ci***
	******************
	gen categopri_ci=.
	replace categopri_ci=1 if q09_10==1
	replace categopri_ci=2 if q09_10==2
	replace categopri_ci=3 if (q09_10>=4 & q09_10<=6)
	replace categopri_ci=4 if q09_10==3
	replace categopri_ci=. if emp_ci==0
	replace categopri_ci=0 if q09_10==7

	******************
	***categosec_ci***
	******************
	gen categosec_ci=.

	*****************
	*tipocontrato_ci*
	*****************
	gen tipocontrato_ci=.
	replace tipocontrato_ci=1 if q09_15==1 & categopri_ci==3
	replace tipocontrato_ci=2 if q09_15==2 & categopri_ci==3
	replace tipocontrato_ci=3 if q09_15==3 & categopri_ci==3

	*****************
	***nempleos_ci***
	*****************
	gen nempleos_ci=q09_09
	replace nempleos_ci=. if emp_ci!=1

	*****************
	***spublico_ci***
	*****************
	gen spublico_ci=(q09_10==4 & emp_ci==1)
	replace spublico_ci=. if emp_ci==.

	**************
	***ocupa_ci***
	**************
	generat ocupa_ci=.
	replace ocupa_ci=1 if (q09_19>=2 & q09_19<=3) & emp_ci==1
	replace ocupa_ci=2 if q09_19==1 & emp_ci==1
	replace ocupa_ci=3 if q09_19==3 & emp_ci==1
	replace ocupa_ci=4 if q09_19==5 & emp_ci==1
	replace ocupa_ci=5 if q09_19==7  & emp_ci==1
	replace ocupa_ci=6 if q09_19==6 & emp_ci==1
	replace ocupa_ci=7 if q09_19==8  & emp_ci==1
	replace ocupa_ci=8 if q09_19==10 & emp_ci==1
	replace ocupa_ci=9 if q09_19==97 & emp_ci==1

	*************
	***rama_ci***
	*************
	gen rama_ci=.
	replace rama_ci = 1 if q09_21==12 & emp_ci==1
	replace rama_ci = 2 if q09_21==10 & emp_ci==1
	replace rama_ci = 3 if q09_21==6  & emp_ci==1
	replace rama_ci = 4 if q09_21==13 & emp_ci==1
	replace rama_ci = 5 if q09_21==3  & emp_ci==1
	replace rama_ci = 6 if (q09_21==1 | q09_21==7) & emp_ci==1
	replace rama_ci = 7 if q09_21==9  & emp_ci==1
	replace rama_ci = 8 if q09_21==11 & emp_ci==1
	replace rama_ci = 9 if q09_21==5 & emp_ci==1

	****************
	***durades_ci***
	****************
	gen durades_ci=. if q09_34==.
	replace durades_ci= . if q09_34==1
	replace durades_ci=(1+3)/2 if q09_34==2
	replace durades_ci=(4+6)/2 if q09_34==3
	replace durades_ci=(7+12)/2 if q09_34==4
	replace durades_ci=(12+12)/2 if q09_34==5

	***************
	*antiguedad_ci*
	***************
	gen antiguedad_ci=.
	replace antiguedad_ci=0 if q09_22==1
	replace antiguedad_ci=(1+4)/2 if q09_22==2
	replace antiguedad_ci=(5+9)/2 if q09_22==3
	replace antiguedad_ci=(10+10)/2 if q09_22==4

*******************
***categoinac_ci***
*******************
gen categoinac_ci = .
replace categoinac_ci = 1 if  (q09_28==5 & condocup_ci==3)
replace categoinac_ci = 2 if  (q09_28==3 & condocup_ci==3)
replace categoinac_ci = 3 if  (q09_28==4 & condocup_ci==3)
replace categoinac_ci = 4 if  ((categoinac_ci ~=1 & categoinac_ci ~=2 & categoinac_ci ~=3) & condocup_ci==3)

*******************
***formal***
*******************
gen formal_ci=(cotizando_ci==1)
label var formal_ci "1=afiliado o cotizante / PEA"




		**************************
		***VARIABLES DE INGRESO***
		**************************

    ***************
	***ylmpri_ci***
	***************
	egen ylmpri_ci = rsum(q10_02b q10_15) , m
	replace ylmpri_ci =. if q10_02b==. & q10_15==.
	replace ylmpri_ci =. if ylmpri_ci<0

	*****************
	***nrylmpri_ci***
	*****************
	gen nrylmpri_ci=(ylmpri_ci==. & emp_ci==1)

	****************
	***ylnmpri_ci***
	****************
	gen ylnmpri_ci=.

	***************
	***ylmsec_ci***
	***************
	gen ylmsec_ci=q10_04b if q10_04b!=.

	****************
	***ylnmsec_ci***
	****************
	gen ylnmsec_ci=.

	*****************
	***ylmotros_ci***
	*****************
	gen ylmotros_ci= .

	******************
	***ylnmotros_ci***
	******************
	gen ylnmotros_ci=.

	************
	***ylm_ci***
	************
	egen ylm_ci= rsum(ylmpri_ci ylmsec_ci),m
	replace ylm_ci=. if ylmpri_ci==. &  ylmsec_ci==.

	*************
	***ylnm_ci***
	*************
	egen ylnm_ci=rsum(ylnmpri_ci ylnmsec_ci), m
	replace ylnm_ci=. if ylnmpri_ci==. &  ylnmsec_ci==.

	*************
	***ynlm_ci***
	*************
	* remesas in local currency (SRD): USD (q10_17b) * 8.71 + EUR (q10_17c) * 4.47, over 6 months
	gen remesasaux = (q10_17b * 8.71) + (q10_17c * 4.47)
	replace remesasaux = remesasaux / 6
	replace remesasaux = . if q10_17b==. & q10_17c==.

	egen ynlm_aux  = rsum(q10_18 q10_19 q10_20 q10_21 q10_22 q10_23), miss
	replace ynlm_aux = ynlm_aux / 12

	* Fixed: alt file used undefined `remesas`; replaced with `remesasaux`
	egen ynlm_ci = rsum(ynlm_aux remesasaux q10_07 q10_08 q10_09 q10_10 q10_11 q10_12 q10_13), m
	replace ynlm_ci = . if ynlm_aux==. & remesasaux==. & q10_07==. & q10_08==. & q10_09==. & q10_10==. & q10_11==. & q10_13==.

	**************
	***ynlnm_ci***
	**************
	gen ynlnm_ci=.

	************
	***ytot_ci***
	************
	egen ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci ynlnm_ci)

	****************
	***remesas_ci***
	****************
	gen remesas_ci = remesasaux

		************************
		***INGRESOS DEL HOGAR***
		************************

	*****************
	***nrylmpri_ch***
	*****************
	by idh_ch, sort: egen nrylmpri_ch=sum(nrylmpri_ci) if miembros_ci==1
	replace nrylmpri_ch=1 if nrylmpri_ch>0 & nrylmpri_ch<.
	replace nrylmpri_ch=. if nrylmpri_ch==.

	************
	***ylm_ch***
	************
	by idh_ch, sort: egen ylm_ch=sum(ylm_ci) if miembros_ci==1

	*************
	***ylnm_ch***
	*************
	by idh_ch, sort: egen ylnm_ch=sum(ylnm_ci) if miembros_ci==1

	*************
	***ynlm_ch***
	*************
	by idh_ch, sort: egen ynlm_ch=sum(ynlm_ci) if miembros_ci==1

	**************
	***ynlnm_ch***
	**************
	gen ynlnm_ch=.

	*****************
	***ylmhopri_ci***
	*****************
	gen ylmhopri_ci=ylmpri_ci/(4.3*horaspri_ci)
	replace ylmhopri_ci=. if ylmhopri_ci<=0

	**************
	***ylmho_ci***
	**************
	gen ylmho_ci=ylm_ci/(horastot_ci*4.3)

	****************
	***remesas_ch***
	****************
	by idh_ch, sort: egen remesas_ch=sum(remesas_ci) if miembros_ci==1

	drop remesasaux ynlm_aux




		****************************
		***VARIABLES DE EDUCACION***
		****************************

	*************
	***aedu_ci***
	*************
	cap clonevar asis_niv_inst  = q03_04
	cap clonevar asis_ano_inst  = q03_08
	cap clonevar noasis_niv_inst = q03_20
	cap clonevar noasis_ano_inst = q03_23
	cap clonevar finalizo = q03_22

	cap gen aedu_ci = .
	replace aedu_ci = 0 if q03_01 == 2

	* PARA LOS QUE ASISTEN (q03_02==1)
	replace aedu_ci = 0                       if asis_niv_inst == 1 & q03_02 == 1
	replace aedu_ci = asis_ano_inst-1         if asis_niv_inst == 2 & q03_02 == 1
	replace aedu_ci = asis_ano_inst-1+6       if asis_niv_inst == 3 & q03_02 == 1
	replace aedu_ci = asis_ano_inst-1+6+4     if asis_niv_inst == 4 & q03_02 == 1
	replace aedu_ci = asis_ano_inst-1+6+4+3   if asis_niv_inst == 5 & q03_02 == 1
	replace aedu_ci = asis_ano_inst-1+6+4+3+4 if asis_niv_inst == 6 & q03_02 == 1

	* PARA LOS QUE NO ASISTEN PERO ALGUNA VEZ ASISTIERON
	replace aedu_ci = 0                       if noasis_niv_inst == 1 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = noasis_ano_inst         if noasis_niv_inst == 2 & finalizo ==2 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = 6                       if noasis_niv_inst == 2 & finalizo ==1 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = noasis_ano_inst+6       if noasis_niv_inst == 3 & finalizo ==2 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = 6+4                     if noasis_niv_inst == 3 & finalizo ==1 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = noasis_ano_inst+6+4     if noasis_niv_inst == 4 & finalizo ==2 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = 6+4+3                   if noasis_niv_inst == 4 & finalizo ==1 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = noasis_ano_inst+6+4+3   if noasis_niv_inst == 5 & finalizo ==2 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = 6+4+3+4                 if noasis_niv_inst == 5 & finalizo ==1 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = noasis_ano_inst+6+4+3+4 if noasis_niv_inst == 6 & finalizo ==2 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = 6+4+3+4+2              if noasis_niv_inst == 6 & finalizo ==1 & q03_02 == 2 & q03_01 == 1
	replace aedu_ci = 0 if aedu_ci == -1

	* Imputing missing with max years of previous level
	replace aedu_ci=0  if q03_04==1 & q03_08==. & aedu_ci==.
	replace aedu_ci=0  if q03_04==2 & q03_08==. & aedu_ci==.
	replace aedu_ci=6  if q03_04==3 & q03_08==. & aedu_ci==.
	replace aedu_ci=10 if q03_04==4 & q03_08==. & aedu_ci==.
	replace aedu_ci=13 if q03_04==5 & q03_08==. & aedu_ci==.
	replace aedu_ci=17 if q03_04==6 & q03_08==. & aedu_ci==.
	replace aedu_ci=.  if q03_04==7 & q03_08==. & aedu_ci==.

	replace aedu_ci=0  if q03_20==1 & q03_23==. & aedu_ci==.
	replace aedu_ci=0  if q03_20==2 & q03_23==. & aedu_ci==.
	replace aedu_ci=6  if q03_20==3 & q03_23==. & aedu_ci==.
	replace aedu_ci=10 if q03_20==4 & q03_23==. & aedu_ci==.
	replace aedu_ci=13 if q03_20==5 & q03_23==. & aedu_ci==.
	replace aedu_ci=17 if q03_20==6 & q03_23==. & aedu_ci==.
	replace aedu_ci=.  if q03_20==7 & q03_23==. & aedu_ci==.

	**************
	***eduui_ci***
	**************
	gen eduui_ci=(aedu_ci>13 & aedu_ci<17)
	replace eduui_ci=. if aedu_ci==.

	***************
	***eduuc_ci***
	***************
	gen byte eduuc_ci= (aedu_ci>=17)
	replace eduuc_ci=. if aedu_ci==.

	***************
	***asiste_ci***
	***************
	gen asiste_ci=(q03_02==1)
	replace asiste_ci=. if q03_01==.

	***************
	* edu_hdmf    *
	***************
	* HDMF 10-level scale derived from aedu_ci
	* Suriname school structure: primary 6yr, lower sec 4yr, upper sec 3yr, tertiary 4yr, master's 2yr
	gen edu_hdmf = .
	replace edu_hdmf = 1  if aedu_ci == 0
	replace edu_hdmf = 2  if aedu_ci >= 1  & aedu_ci < 6
	replace edu_hdmf = 3  if aedu_ci == 6
	replace edu_hdmf = 4  if aedu_ci >= 7  & aedu_ci < 10
	replace edu_hdmf = 5  if aedu_ci == 10
	replace edu_hdmf = 6  if aedu_ci >= 11 & aedu_ci < 13
	replace edu_hdmf = 7  if aedu_ci == 13
	replace edu_hdmf = 8  if aedu_ci >= 14 & aedu_ci < 17
	replace edu_hdmf = 9  if aedu_ci == 17
	replace edu_hdmf = 10 if aedu_ci > 17  & aedu_ci != .
	label var edu_hdmf "HDMF education level (1-10)"

	***************
	* edu_isced   *
	***************
	gen edu_isced = .
	replace edu_isced = 0 if aedu_ci == 0
	replace edu_isced = 1 if aedu_ci >= 1  & aedu_ci <= 6
	replace edu_isced = 2 if aedu_ci >= 7  & aedu_ci <= 10
	replace edu_isced = 3 if aedu_ci >= 11 & aedu_ci <= 13
	replace edu_isced = 5 if aedu_ci == 14
	replace edu_isced = 6 if aedu_ci >= 15 & aedu_ci <= 17
	replace edu_isced = 7 if aedu_ci >= 18 & aedu_ci != .
	label var edu_isced "ISCED-2011 level"

	drop asis_niv_inst asis_ano_inst noasis_niv_inst noasis_ano_inst finalizo



******************************
*** VARIABLES DE MIGRACION ***
******************************

	*******************
	*** migrante_ci ***
	*******************
	gen migrante_ci=(q02_01!=1) if q02_01!=.
	label var migrante_ci "=1 si es migrante (q02_01!=1)"

	**********************
	*** migrantiguo5_ci ***
	**********************
	* Using second (corrected) definition from alt file; first duplicate removed
	gen migrantiguo5_ci=(migrante_ci==1 & q02_07>4) if migrante_ci!=. & !inrange(edad_ci,0,4)
	replace migrantiguo5_ci = 0 if migrantiguo5_ci != 1 & migrante_ci==1
	replace migrantiguo5_ci=. if (q02_07==. & q02_03==1) | migrante_ci == 0
	label var migrantiguo5_ci "=1 si es migrante antiguo (5 anos o mas)"

	*************
	*mig_pais_ci*
	*************
	* q02_01 numeric country codes; map LAC countries by known codes
	gen str30 mig_pais_ci = ""
	replace mig_pais_ci = "Venezuela"  if q02_01 == 3
	replace mig_pais_ci = "Brazil"     if q02_01 == 4
	* String-based matching for other cases (using q02_02 country name string)
	capture replace mig_pais_ci = q02_02 if mig_pais_ci == "" & migrante_ci == 1 & q02_02 != ""
	label var mig_pais_ci "Pais de origen (derivado de q02_01/q02_02)"

	**********************
	*** miglac_ci ***
	**********************
	gen miglac_ci=(migrante_ci==1 & (inlist(q02_01,3,4) | inlist(q02_02,"Argentinie","Haiti","Haitie","Colombia","JAMAICA","Jamaica") | inlist(q02_02,"dominicaanse republi","Trinidad","VENEZUELA","haiti","venezuela"))) if migrante_ci!=.
	replace miglac_ci = 0 if miglac_ci != 1 & migrante_ci==1
	replace miglac_ci=. if (q02_01==7 & mi(q02_02)) | migrante_ci == 0
	label var miglac_ci "=1 si es migrante proveniente de un pais LAC"


rename q09_19 codocupa
rename q09_21 codindustria

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
