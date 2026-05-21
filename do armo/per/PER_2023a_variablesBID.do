clear
set more off

di "File created with the Claude HDMF system — 2026-04-10"

*________________________________________________________________________________________________________________*

local PAIS PER
local ENCUESTA ENAHO
local ANO "2023"
local ronda a

if c(username)=="PABLOCOR" {
    use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\per\PER_`ANO'`ronda'.dta", clear
    local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\per\PER_`ANO'`ronda'_BID.dta"
    capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\per"
}

/***************************************************************************
             BASES DE DATOS DE ENCUESTA DE HOGARES
             País: Perú | Encuesta: ENAHO | Año: 2023 | Ronda: Annual
             Cloned from PER_2024_variablesBID.do — see differences below:
               [1] cotizando_ci: uses p524b1/p538b1 (p558b2 not available before 2024)
               [2] afiliado_ci: starts with 0 (not .), then overrides
             Income module: EXCLUDED (commented out, same as reference)
*************************************************************************** */


	**************
	**relacion_ci: Variable que indica la relación o parentesco del individuo respecto al jefe de hogar
	**************
	gen byte relacion_ci=.
	replace relacion_ci = 1 if p203 == 1
	replace relacion_ci = 2 if p203 == 2
	replace relacion_ci = 3 if p203 == 3
	replace relacion_ci = 4 if p203 >= 4 & p203 <= 7 | p203 == 11
	replace relacion_ci = 5 if p203 == 9 | p203 == 10
	replace relacion_ci = 6 if p203 == 8

	*************
	*miembros_ci: Variable dicotómica que identifica a los miembros del hogar.
	*************
	gen miembros_ci=(relacion_ci>=1 & relacion_ci<=5)
	replace miembros_ci=. if relacion_ci==.

	************************************************************
	* pais_c: acrónimo ISO del nombre del país de residencia   *
	************************************************************
	gen str3 pais_c="PER"

	*********
	*edad_ci: Edad del individuo expresada en número de años*
	*********
	gen int edad_ci=p208a
	replace edad_ci=. if edad_ci==99

	******************
	*idh_ch: Identificador único de hogares *
	******************
	sort conglome vivienda hogar
	cap egen idh_ch= group(conglome vivienda hogar)
	tostring idh_ch, replace

	***************
	*idp_ci: Identificador único del individuo *
	***************
	gen idp_ci = codperso
	tostring idp_ci, replace format ("%20.0f")

	*******************************************
	*factor_ch: factor de ponderación de los hogares*
	*******************************************
	gen factor_ch= factor07

	***********
	*factor_ci: factor de ponderación a la población total *
	***********
	gen factor_ci=facpob07


	*************
	*condocup_ci: Identifica la condición de ocupación del individuo.
	*************
	gen byte condocup_ci = .
	replace condocup_ci = 1 if p501==1 | p502==1 | p503==1    //Ocupados
	replace condocup_ci = 2 if p501==2 & p502==2 & p503==2    //Desocupados
	replace condocup_ci = 3 if condocup_ci == 2 & ( p5041==2 & p5042==2 & p5043==2 & p5044==2 & p5045==2 & p5046==2 & p5047==2 & p5048==2 & p5049==2 & p50410==2 & p50411==2 ) //Inactivos
	replace condocup_ci=. if !inrange(edad_ci, 15,64)

	*******************
	***categoinac_ci: Identifica la condición de inactividad de los individuos.***
	*******************
	gen byte categoinac_ci = .
	replace categoinac_ci = 1 if  (p546==6   & condocup_ci==3) //Jubilado o Pensionado
	replace categoinac_ci = 2 if  (p546 == 4 & condocup_ci == 3) //Estudiante
	replace categoinac_ci = 3 if  (p546 == 5 & condocup_ci == 3) //Quehaceres domesticos
	replace categoinac_ci = 4 if  ((categoinac_ci ~=1 & categoinac_ci ~=2 & categoinac_ci ~=3) & condocup_ci==3) //Otros Inactivos

	**********
	***emp_ci***
	**********
	gen byte emp_ci = .
	replace emp_ci = (condocup_ci == 1) if condocup_ci != .

	***************
	***desemp_ci***
	***************
	gen byte desemp_ci = .
	replace desemp_ci  = (condocup_ci == 2) if condocup_ci != .

	***************
	***horaspri_ci: Horas trabajadas en la actividad principal***
	***************
	gen byte horaspri_ci   = .
	replace  horaspri_ci   = p513t if emp_ci==1
	replace  horaspri_ci   = . if emp_ci~=1

	***************
	***horastot_ci: Horas totales en todas las actividades***
	***************
	/* NOTE: no p518==99 cleaning needed for 2023 (present in 2019-2022 only) */
	egen  horastot_ci   = rsum(horaspri_ci p518) if emp_ci==1
	replace  horastot_ci   = . if emp_ci~=1

	*****************
	***parcial_ci***
	*****************
	gen byte parcial_ci = .
	replace parcial_ci = (horaspri_ci < 35) if emp_ci == 1 & horaspri_ci != .
	label define parcial_lb 1 "Parcial (<35h)" 0 "Completo (>=35h)"
	label values parcial_ci parcial_lb
	label var parcial_ci "1 = trabajador a tiempo parcial (horaspri_ci < 35h)"

	***********
	***pea_ci***
	***********
	gen byte pea_ci = .
	replace  pea_ci = 1 if inlist(condocup_ci,1,2)
	replace  pea_ci = 0 if inlist(condocup_ci,3,4)

	***************
	***cotizando_ci***
	***************
	/* ALTERNATIVE [dictionary_check_PER 2023a]:
	   p558b2 (año último aporte pensión) not available before 2024.
	   Using actual contribution amounts: p524b1 (primary) and p538b1 (secondary).
	   Source: PER_2023a_variablesBID.do (MECOVI reference, same logic).
	   See: bases armo/raw/per/alternatives_do_files/PER_2023a_variablesBID.do */
	replace p524b1 = . if p524b1 == 999999
	replace p538b1 = . if p538b1 == 999999
	gen cotizando_ci=.
	replace cotizando_ci=0 if condocup_ci==1 | condocup_ci==2
	replace cotizando_ci=1 if ((p524b1>0 & p524b1!=.) | (p538b1>0 & p538b1!=.)) & cotizando_ci==0
	label var cotizando_ci "Cotizante a la Seguridad Social/pension"

	***************
	***afiliado_ci***
	***************
	/* ALTERNATIVE [dictionary_check_PER 2023a]: Initialized with 0 (not .)
	   Same p558a1-p558a4 logic as 2024 reference. */
	gen afiliado_ci=0
	replace afiliado_ci=1 if (p558a1==1 | p558a2==2 | p558a3==3 | p558a4==4)
	replace afiliado_ci=. if condocup_ci==.
	label var afiliado_ci "Afiliado sistema de pensiones"

	**************
	***formal_ci***
	**************
	gen byte formal_ci=.
	replace formal_ci  =  1 if (cotizando_ci == 1 | afiliado_ci == 1) & condocup_ci == 1
	replace formal_ci = 0 if (cotizando_ci == 0 & afiliado_ci == 0) & (condocup_ci == 1 )
	label var formal_ci "1=afiliado o cotizante"

	***************
	***categopri_ci: Categoría ocupacional de la actividad principal***
	***************
	gen categopri_ci=.
	replace categopri_ci=0 if condocup_ci==1 & p507==7
	replace categopri_ci=1 if condocup_ci==1 & p507==1
	replace categopri_ci=2 if condocup_ci==1 & p507==2
	replace categopri_ci=3 if condocup_ci==1 & (p507==3 | p507==4 | p507==6)
	replace categopri_ci=4 if condocup_ci==1 & p507==5
	label var categopri_ci "Categoria ocupacional actividad principal"
	label define categopri_ci 0 "Otra clasificación" 1 "Patrón o Empleador" 2 "Cuenta Propia" 3 "Empleado" 4 "Trabajador no remunerado"
	label value categopri_ci categopri_ci

	*****************
	***selfempl_ci***
	*****************
	gen byte selfempl_ci = .
	replace selfempl_ci = (categopri_ci == 2) if emp_ci == 1 & categopri_ci != .
	label define selfempl_lb 1 "Cuenta propia" 0 "Otros"
	label values selfempl_ci selfempl_lb
	label var selfempl_ci "1 = trabajador por cuenta propia (categopri_ci == 2)"

	*******************
	***tipocontrato_ci: Tipo de contrato laboral***
	*******************
	gen tipocontrato_ci=.
	replace tipocontrato_ci=1 if (p511a==1) & categopri_ci==3
	replace tipocontrato_ci=2 if (p511a>=2 & p511a<=6) & categopri_ci==3
	replace tipocontrato_ci=3 if (p511a==7 | tipocontrato_ci==.) & categopri_ci==3
	label var tipocontrato_ci "Tipo de contrato segun su duracion"
	label define tipocontrato_ci 1 "Permanente/indefinido" 2 "Temporal" 3 "Sin contrato/verbal"
	label value tipocontrato_ci tipocontrato_ci


********************************************************************************
***************   VARIABLES DE INGRESO   *************************************
********************************************************************************
/* EXCLUDED — Income module not included in HDMF PER harmonization.
   See reference: PER_2024_variablesBID.do */


********************************************************************************
***************   VARIABLES DE EDUCACION   *************************************
********************************************************************************

	***************
	*** aedu_ci: Años de educación culminados ***
	***************
	egen grados = rowtotal(p301b p301c), missing

	gen byte aedu_ci=.
	replace aedu_ci=0          if p301a==1 | p301a==2
	replace aedu_ci=grados     if p301a==3
	replace aedu_ci=6          if p301a==4
	replace aedu_ci=6 + grados if p301a==5
	replace aedu_ci=11         if p301a==6
	replace aedu_ci=11 + grados if p301a==7
	replace aedu_ci=13         if p301a==8
	replace aedu_ci=11 + grados if p301a==9
	replace aedu_ci=16         if p301a==10
	replace aedu_ci=16 + grados if p301a==11
	replace aedu_ci=.          if p301a==12

	drop grados

	**************
	*** edu_hdmf ***
	**************
	gen edu_hdmf = .

	replace edu_hdmf = 1 if p301a==1 | p301a==2
	replace edu_hdmf = 2 if p301a==3
	replace edu_hdmf = 3 if p301a==4
	replace edu_hdmf = 4 if p301a==5
	replace edu_hdmf = 5 if p301a==6
	replace edu_hdmf = 5 if p301a==7
	replace edu_hdmf = 5 if p301a==9
	replace edu_hdmf = 6 if p301a==8
	replace edu_hdmf = 7 if p301a==10
	replace edu_hdmf = 8 if p301a==11

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
	ta edu_hdmf
***********
* ocupa_ci
* p508: CIUO-88 3-digit occupation code; 1-digit major group = first digit of p508
* NOTE: PER uses CIUO-88 (p508, 3-digit); approximate ISCO-08 mapping.
*       Groups 6-8 not fully comparable across classification systems.
***********
gen byte ocupa_ci = .
replace ocupa_ci = real(substr(string(int(p508)), 1, 1)) if emp_ci == 1 & !missing(p508) & p508 > 0
label define ocupa_lbl 1 "Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary", replace
label values ocupa_ci ocupa_lbl
label var ocupa_ci "ISCO-08 major group (approx. CIUO-88 via p508, 1-digit)"
***********
* overqualified_ci
* edu_hdmf >= 6: técnica or higher (8-level PER scale)
* NOTE: CIUO-88 to ISCO-08 mapping is approximate; comparability limited
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified", replace
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (approx., CIUO-88 PER coding)"


	*************
	* remesas_ci *
	*************
	gen remesas_loc = d5563c/12
	gen remesas_ext = d5563e/12
	egen remesas_ci=rowtotal(remesas_loc remesas_ext), missing
	drop remesas_loc remesas_ext

	*************
	* remesas_ch *
	*************
	by idh_ch, sort: egen byte remesas_ch = sum(remesas_ci) if miembros_ci == 1


********************************************************************************
***************   VARIABLES DE MIGRACION   *************************************
********************************************************************************

	*******************
	*** migrante_ci: Si el individuo nació en otro país ***
	*******************
	* p401g2: código de distrito/país donde vivía la madre al nacer el individuo
	* códigos < 10000 = país extranjero
	gen migrante_ci=(p401g2<10000) if p401g2!=. & p401g2!=999999

	**********************
	*** migrantiguo5_ci ***
	**********************
	gen migrantiguo5_ci=(migrante_ci==1 & (p401f==1 | (p401g>10000 & p401g!=.))) ///
	    if migrante_ci!=. & p401f!=3 & p401g!=999999 & p401f!=. & !inrange(edad_ci,0,4)

	*pais de migrante (código)
	gen mig_pais_code = .
	replace mig_pais_code = p401g2 if migrante_ci==1

	gen str40 mig_pais_ci = ""
	replace mig_pais_ci = "Venezuela" if mig_pais_code==4037
	replace mig_pais_ci = "Otro" if mig_pais_ci=="" & migrante_ci==1


compress
save "`base_out'", replace
