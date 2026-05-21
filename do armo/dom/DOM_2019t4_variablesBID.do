clear
set more off
di "File created with the Claude HDMF system — 2026-04-21"

/***************************************************************************
         BASES DE DATOS DE ENCUESTA DE HOGARES
             Script de armonización HDMF
País: República Dominicana (DOM)
Encuesta: ENCFT (Encuesta Nacional Continua de Fuerza de Trabajo)
Año: 2019
Ronda: t4 (Q4)
Clonado desde: DOM_2024t4_variablesBID.do (HDMF)
Referencia SCL: DOM_2019t4_variablesBID.do (alternative_do_files)
Creado con: Claude HDMF system — 2026-04-21

DIFERENCIAS RESPECTO A 2024:
  - idh_ch: group(vivienda hogar) en lugar de concat()
  - idp_ci: miembro en lugar de concat(vivienda hogar miembro)
  - aedu_ci: base secundaria = +8 (sistema anterior)
  - Sin destring en variables de ingreso (variables numéricas en 2019)
  - FX: 1 USD = 52.78 DOP, EUR factor = 0.9, CHF = 51.54 DOP
  - lp_ci/lpe_ci: líneas zona-específicas (urb/rur)
  - salmm_ci = 9411.6
  - recibio_remesa_ext3: puede no requerir destring en 2019
  Nota: migrantiguo5_ci = missing (ENCFT no capta tiempo de residencia).
****************************************************************************/

*________________________________________________*
* Locales de identificacion
*________________________________________________*
local PAIS   DOM
local ENCUESTA ENCFT
local ANO    "2019"
local ronda  t4

*________________________________________________*
* Log
*________________________________________________*
local log_dir "do armo/dom/logs"
capture mkdir "`log_dir'"
log using "`log_dir'/DOM_2019t4_variablesBID.log", replace

*________________________________________________*
* Paths por usuario
*________________________________________________*

if c(username)=="PABLOCOR" {
	use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\dom\DOM_2019t4.dta", clear
	local base_out "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\DOM\DOM_2019t4_BID.dta"
	capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\DOM"
}

if c(username)!="PABLOCOR" {
	global ruta = "${surveysFolder}"
	local base_in  = "$ruta\survey\\`PAIS'\\`ENCUESTA'\\`ANO'\\`ronda'\data_merge\\`PAIS'_`ANO'`ronda'.dta"
	local base_out = "$ruta\harmonized\\`PAIS'\\`ENCUESTA'\data_arm\\`PAIS'_`ANO'`ronda'_BID.dta"
	use `base_in', clear
}


		**********************************
		*** VARIABLES DE IDENTIFICACION***
		**********************************

gen anio_c = 2019
label var anio_c "Anio de la encuesta"

gen byte trimestre_c = 4
label var trimestre_c "Trimestre de la encuesta"

gen mes_c = mes
label var mes_c "Mes de la encuesta"

gen str3 pais_c = "DOM"
label var pais_c "Pais"

/* 2019: ID numérico via group() */
sort vivienda hogar
egen idh_ch = group(vivienda hogar)
tostring idh_ch, replace
label var idh_ch "ID del hogar"

gen idp_ci = miembro
tostring idp_ci, replace
label var idp_ci "ID de la persona en el hogar"

duplicates report idp_ci

gen factor_ci = factor_expansion
label var factor_ci "Factor de expansion del individuo"

gen factor_ch = factor_expansion
label var factor_ch "Factor de expansion del hogar"


		****************************
		***VARIABLES DEMOGRAFICAS***
		****************************

gen sexo_ci = sexo
label var sexo_ci "Sexo del individuo"
label define sexo_ci 1 "Hombre" 2 "Mujer"
label value sexo_ci sexo_ci

gen edad_ci = edad
label var edad_ci "Edad del individuo"

gen relacion_ci = 1 if parentesco==1
replace relacion_ci = 2 if parentesco==2
replace relacion_ci = 3 if parentesco==3 | parentesco==4
replace relacion_ci = 4 if parentesco>=5 & parentesco<=11
replace relacion_ci = 5 if parentesco==12
label var relacion_ci "Relacion con el jefe del hogar"
label define relacion_ci 1 "Jefe/a" 2 "Esposo/a" 3 "Hijo/a" 4 "Otros parientes" 5 "Otros no parientes"
label value relacion_ci relacion_ci

gen byte miembros_ci = (relacion_ci>=1 & relacion_ci<=5)
replace miembros_ci = . if relacion_ci==.
label var miembros_ci "Miembro del hogar"


		************************************
		*** VARIABLES DEL MERCADO LABORAL***
		************************************

gen byte condocup_ci = .
replace condocup_ci = 1 if trabajo_semana_pasada==1 | tenia_empleo_negocio==1 | (realizo_actividad!=8 & realizo_actividad!=.)
replace condocup_ci = 2 if (trabajo_semana_pasada==2 | tenia_empleo_negocio==2 | realizo_actividad==8) & (busco_trabajo_establ_negocio==1)
recode condocup_ci (.=3) if edad_ci>=10
replace condocup_ci = 4 if edad_ci<10
label var condocup_ci "Condicion de ocupacion"
label define condocup_ci 1 "Ocupado" 2 "Desocupado" 3 "Inactivo" 4 "Menor que 10"
label value condocup_ci condocup_ci

gen byte emp_ci = (condocup_ci==1)
label var emp_ci "Ocupado (empleado)"

gen byte desemp_ci = (condocup_ci==2)
label var desemp_ci "Desempleado que busco empleo en el periodo de referencia"

gen byte pea_ci = 0
replace pea_ci = 1 if emp_ci==1 | desemp_ci==1
label var pea_ci "Poblacion Economicamente Activa"

*****************
***inactivo_ci***
*****************
gen byte inactivo_ci = (condocup_ci == 3)
label var inactivo_ci "Inactivo (no busca empleo, no empleado)"

gen horaspri_ci = horas_trabaja_semana_principal
replace horaspri_ci = . if emp_ci==0
label var horaspri_ci "Horas trabajadas semanalmente en el trabajo principal"

gen promhora   = horas_trabaja_semana_principal if emp_ci==1
gen promhora1  = horas_trabajo_ocup_secun       if emp_ci==1
egen tothoras  = rowtotal(promhora promhora1)
replace tothoras = . if promhora==. & promhora1==.
replace tothoras = . if tothoras>=168
gen horastot_ci = tothoras if emp_ci==1
label var horastot_ci "Horas trabajadas semanalmente en todos los empleos"
drop promhora promhora1 tothoras

*****************
***parcial_ci***
*****************
gen byte parcial_ci = .
replace parcial_ci = (horaspri_ci < 35) if emp_ci == 1 & horaspri_ci != .
label define parcial_lb 1 "Parcial (<35h)" 0 "Completo (>=35h)"
label values parcial_ci parcial_lb
label var parcial_ci "1 = trabajador a tiempo parcial (horaspri_ci < 35h)"

gen cotizando_ci = .
label var cotizando_ci "Cotizante activo a la Seguridad Social (no disponible en ENCFT)"

gen afiliado_ci = .
replace afiliado_ci = 1 if afiliado_afp_princ==1
replace afiliado_ci = 0 if afiliado_afp_princ==2
replace afiliado_ci = . if afiliado_afp_princ==98
replace afiliado_ci = . if emp_ci==0
label var afiliado_ci "Afiliado a AFP (seguridad social)"

/* 2019: crianza_no_remun_monto es numérica — sin destring */
egen noremunerados = rsum(crianza_no_remun_monto pesca_no_remun_monto alimentos_no_remun_monto), missing
gen categopri_ci = .
replace categopri_ci = 1 if categoria_principal==6
replace categopri_ci = 2 if categoria_principal==7 & noremunerados==.
replace categopri_ci = 3 if inlist(categoria_principal,1,2,3,4,5)
replace categopri_ci = 4 if categoria_principal==8 | grupo_categoria=="Familiar no remunerado" | noremunerados!=.
replace categopri_ci = . if emp_ci==0 & noremunerados==.
label var categopri_ci "Categoria ocupacional actividad principal"
label define categopri_ci 1 "Patron" 2 "Cuenta propia" 3 "Empleado" 4 "No remunerado"
label value categopri_ci categopri_ci

*****************
***selfempl_ci***
*****************
gen byte selfempl_ci = .
replace selfempl_ci = (categopri_ci == 2) if emp_ci == 1 & categopri_ci != .
label define selfempl_lb 1 "Cuenta propia" 0 "Otros"
label values selfempl_ci selfempl_lb
label var selfempl_ci "1 = trabajador por cuenta propia (categopri_ci == 2)"

gen byte formal_ci = .
replace formal_ci = 1 if afiliado_ci==1 & condocup_ci==1
replace formal_ci = 0 if afiliado_ci==0 & condocup_ci==1
label var formal_ci "1=formal (afiliado AFP; cotizando no disponible)"

gen tipocontrato_ci = .
replace tipocontrato_ci = 1 if (tiene_contrato==1 & tipo_contrato==1) & categopri_ci==3
replace tipocontrato_ci = 2 if (tiene_contrato==1 & (tipo_contrato==2 | tipo_contrato==3)) & categopri_ci==3
replace tipocontrato_ci = 3 if (tiene_contrato==2 | tipocontrato_ci==.) & categopri_ci==3
label var tipocontrato_ci "Tipo de contrato segun su duracion"
label define tipocontrato_ci 1 "Permanente/indefinido" 2 "Temporal" 3 "Sin contrato/verbal"
label value tipocontrato_ci tipocontrato_ci


		****************************
		*** VARIABLES DE INGRESO ***
		****************************

/* 2019: tiempo_recibe_pago_dias_ap es numérica — sin destring */
gen ymensual = sueldo_bruto_ap_monto * tiempo_recibe_pago_dias_ap * 4.3 if tiempo_recibe_pago_ap==1
replace ymensual = sueldo_bruto_ap_monto * 4.3  if tiempo_recibe_pago_ap==2
replace ymensual = sueldo_bruto_ap_monto * 2    if tiempo_recibe_pago_ap==3
replace ymensual = sueldo_bruto_ap_monto        if tiempo_recibe_pago_ap==4

gen ymensualindep = ingreso_actividad_in_monto * ingreso_actividad_in_dias * 4.3 if ingreso_actividad_in_periodo==1
replace ymensualindep = ingreso_actividad_in_monto * 4.3 if ingreso_actividad_in_periodo==2
replace ymensualindep = ingreso_actividad_in_monto * 2   if ingreso_actividad_in_periodo==3
replace ymensualindep = ingreso_actividad_in_monto       if ingreso_actividad_in_periodo==4

rename comisiones  otrascomisionesoriginales
rename propinas    otraspropinasoriginales
rename bonificaciones bonificacionesoriginales
gen comisiones   = comisiones_ap_monto
gen propinas     = propinas_ap_monto
gen horasextra   = horas_extra_ap_monto
gen vacaciones   = vacaciones_ap_monto / 12
/* 2019: dividendos_ap_monto es numérica */
gen dividendos   = dividendos_ap_monto / 12
gen bonificaciones = bonificacion_ap_monto / 12
gen regalia      = regalia_ap_monto / 12
/* 2019: utilidad_empresarial_ap_monto es numérica */
gen utilidades   = utilidad_empresarial_ap_monto / 12
/* 2019: beneficios_marginales_ap_monto es numérica */
gen beneficios   = beneficios_marginales_ap_monto / 12
gen bonoantiguedad = incentivo_antiguedad_ap_monto / 12
gen otrosbeneficios = otros_beneficios_ap_monto / 12

gen alimentos  = alimentacion_especie_ap_monto  if alimentacion_especie_ap==1
gen vivienda1  = vivienda_especie_ap_monto      if vivienda_especie_ap==1
gen transporte = transporte_especie_ap_monto    if transporte_especie_ap==1
gen gasolina   = gasolina_especie_ap_monto      if gasolina_especie_ap==1
gen cellular   = celular_especie_ap_monto       if celular_especie_ap==1
gen otros      = otros_especie_ap_monto         if otros_especie_ap==1

gen pension      = pension_nac_monto       if pension_nac==1
gen intereses    = intereses_nac_monto     if intereses_nac==1
gen alquiler     = alquiler_nac_monto      if alquiler_nac==1
gen remesasnales = remesas_nac_monto       if remesas_nac==1
gen otrosing     = ayuda_especie_nac_monto if ayuda_especie_nac==1
egen gobierno = rsum(alimentos_escuela_nac_monto gob_comer_primero_monto gob_inc_asis_escolar_monto ///
	gob_bono_luz_monto gob_bonogas_choferes_monto gob_bonogas_hogares_monto ///
	gob_proteccion_vejez_monto gob_bono_estudiante_prog_monto gob_inc_educacion_sup_monto ///
	gob_inc_policia_prev_monto gob_inc_marina_guerra_monto) if gobierno_nac==1, missing

recode ingreso_asalariado_secun (0=.)
recode ingreso_independientes_secun (0=.)
/* 2019: ganancia_secun_imp_monto es numérica */
egen ymensual2 = rsum(ganancia_secun_imp_monto ingreso_asalariado_secun ingreso_independientes_secun), missing

* Tasa de cambio Q4 2019: 1 USD = 52.78 DOP, EUR factor = 0.9, CHF = 51.54 DOP
gen pension_int = pension_ext_monto                         if pension_ext_moneda=="DOP"
replace pension_int = pension_ext_monto * 52.78             if pension_ext_moneda=="USD"
replace pension_int = (pension_ext_monto * 0.9) * 52.78    if pension_ext_moneda=="EUR"
replace pension_int = pension_ext_monto * 51.54             if pension_ext_moneda=="CHF"
replace pension_int = . if pension_ext==2

/* 2019: loop con chequeo individual de moneda por observación */
forvalues y = 1/6 {
	forvalues x = 1/3 {
		gen remesasaux`y'_`x' = mes`y'_`x'_ext_monto                    if mes`y'_`x'_ext_moneda=="DOP"
		replace remesasaux`y'_`x' = mes`y'_`x'_ext_monto * 52.78        if mes`y'_`x'_ext_moneda=="USD"
		replace remesasaux`y'_`x' = (mes`y'_`x'_ext_monto * 0.9)*52.78  if mes`y'_`x'_ext_moneda=="EUR"
	}
}
capture destring remesasaux1_2 remesasaux2_2 remesasaux3_2 remesasaux4_2 remesasaux5_2 remesasaux6_2, replace
egen remesas_mes = rsum(remesasaux*_*), missing
capture destring recibio_remesa_ext3, replace
replace remesas_mes = . if recibio_remesa_ext1!=1 & recibio_remesa_ext2!=1 & recibio_remesa_ext3!=1
gen remesas_prom = remesas_mes / 6

egen ylmpri_ci = rsum(ymensual comisiones propinas horasextra vacaciones bonificaciones regalia ///
	utilidades beneficios otrosbeneficios bonoantiguedad otros_pagos_ap_monto ymensualindep), missing
replace ylmpri_ci = . if ymensual==. & comisiones==. & propinas==. & horasextra==. & vacaciones==. & ///
	bonificaciones==. & regalia==. & utilidades==. & beneficios==. & otrosbeneficios==. & ///
	bonoantiguedad==. & ymensualindep==.
replace ylmpri_ci = . if emp_ci==0
replace ylmpri_ci = 0 if categopri_ci==4
label var ylmpri_ci "Ingreso laboral monetario actividad principal"

/* 2019: vivienda1, cellular, otros son numéricas */
egen ylnmpri_ci = rsum(alimentos vivienda1 transporte gasolina cellular otros), missing
replace ylnmpri_ci = ylnmpri_ci + noremunerados if categopri_ci==4
replace ylnmpri_ci = . if alimentos==. & vivienda1==. & transporte==. & gasolina==. & cellular==. & otros==. & noremunerados==.
label var ylnmpri_ci "Ingreso laboral NO monetario actividad principal"

gen ylmsec_ci = ymensual2 if emp_ci==1 & cuantos_trabajos_tiene==2
replace ylmsec_ci = . if ymensual2==99999 & emp_ci==1
label var ylmsec_ci "Ingreso laboral monetario segunda actividad"

gen ylnmsec_ci = .
label var ylnmsec_ci "Ingreso laboral NO monetario actividad secundaria"

gen ylmotros_ci = .
label var ylmotros_ci "Ingreso laboral monetario de otros trabajos"

gen ylnmotros_ci = .
label var ylnmotros_ci "Ingreso laboral NO monetario de otros trabajos"

egen ylm_ci = rsum(ylmpri_ci ylmsec_ci), missing
replace ylm_ci = . if ylmpri_ci==. & ylmsec_ci==.
label var ylm_ci "Ingreso laboral monetario total"

egen ylnm_ci = rsum(ylnmpri_ci ylnmsec_ci), missing
replace ylnm_ci = . if ylnmpri_ci==. & ylnmsec_ci==.
label var ylnm_ci "Ingreso laboral NO monetario total"

/* 2019: intereses es numérica */
egen ynlm_ci = rsum(pension intereses alquiler remesasnales otrosing gobierno pension_int remesas_prom dividendos), missing
replace ynlm_ci = . if pension==. & intereses==. & alquiler==. & remesasnales==. & otrosing==. & ///
	gobierno==. & pension_int==. & remesas_prom==.
label var ynlm_ci "Ingreso no laboral monetario"

/* 2019: regalos_ext_monto es numérica */
gen ynlnm_ci = regalos_ext_monto
replace ynlnm_ci = . if regalos_ext_monto==.
label var ynlnm_ci "Ingreso no laboral no monetario"

egen ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci ynlnm_ci), mi
label var ytot_ci "Ingreso mensual total del individuo"

by idh_ch, sort: egen ylm_ch  = sum(ylm_ci)  if miembros_ci==1, missing
by idh_ch, sort: egen ylnm_ch = sum(ylnm_ci) if miembros_ci==1, missing
by idh_ch, sort: egen ynlm_ch = sum(ynlm_ci) if miembros_ci==1, missing
label var ylm_ch  "Ingreso laboral monetario del hogar"
label var ylnm_ch "Ingreso laboral no monetario del hogar"
label var ynlm_ch "Ingreso no laboral monetario del hogar"

gen remesas_ci = remesas_prom
label var remesas_ci "Remesas mensuales reportadas por el individuo"

by idh_ch, sort: egen remesas_ch = sum(remesas_ci) if miembros_ci==1, missing
label var remesas_ch "Remesas mensuales del hogar"

gen nrylmpri_ci = (ylmpri_ci==. & emp_ci==1)
replace nrylmpri_ci = . if emp_ci!=1
label var nrylmpri_ci "Id no respuesta ingreso actividad principal"

by idh_ch, sort: egen nrylmpri_ch = sum(nrylmpri_ci) if miembros_ci==1, missing
replace nrylmpri_ch = 1 if nrylmpri_ch>0 & nrylmpri_ch<.
label var nrylmpri_ch "Hogares con algun miembro sin respuesta de ingresos"


		****************************
		***VARIABLES DE EDUCACION***
		****************************

gen aedu_ci = .
replace aedu_ci = 0  if nivel_ultimo_ano_aprobado==1
replace aedu_ci = 0  if nivel_ultimo_ano_aprobado==9
replace aedu_ci = 0  if nivel_ultimo_ano_aprobado==10
replace aedu_ci = .  if nivel_ultimo_ano_aprobado==99
replace aedu_ci = ultimo_ano_aprobado          if nivel_ultimo_ano_aprobado==2
/* 2019: base +8 para secundaria (ver nota en 2022 donde se corrige a +6) */
replace aedu_ci = ultimo_ano_aprobado + 8      if nivel_ultimo_ano_aprobado==3
replace aedu_ci = ultimo_ano_aprobado + 8      if nivel_ultimo_ano_aprobado==4
replace aedu_ci = ultimo_ano_aprobado + 14     if nivel_ultimo_ano_aprobado==5
replace aedu_ci = ultimo_ano_aprobado + 14 + 4 if nivel_ultimo_ano_aprobado==6 | nivel_ultimo_ano_aprobado==7
replace aedu_ci = ultimo_ano_aprobado + 14 + 4 + 2 if nivel_ultimo_ano_aprobado==8
replace aedu_ci = .  if nivel_ultimo_ano_aprobado==.
label var aedu_ci "Anios de educacion aprobados (base +8 secundaria; discontinuidad en 2022)"

gen edu_hdmf = .
replace edu_hdmf = 1 if inlist(nivel_ultimo_ano_aprobado, 1, 9, 10)
replace edu_hdmf = 2 if nivel_ultimo_ano_aprobado==2 & ultimo_ano_aprobado>=1 & ultimo_ano_aprobado<6
replace edu_hdmf = 3 if nivel_ultimo_ano_aprobado==2 & ultimo_ano_aprobado==6
replace edu_hdmf = 4 if inlist(nivel_ultimo_ano_aprobado,3,4) & ultimo_ano_aprobado>=1 & ultimo_ano_aprobado<6
replace edu_hdmf = 5 if inlist(nivel_ultimo_ano_aprobado,3,4) & ultimo_ano_aprobado==6
replace edu_hdmf = 5 if nivel_ultimo_ano_aprobado==5 & ultimo_ano_aprobado>=1 & ultimo_ano_aprobado<4
replace edu_hdmf = 7 if nivel_ultimo_ano_aprobado==5 & ultimo_ano_aprobado>=4
replace edu_hdmf = 8 if inlist(nivel_ultimo_ano_aprobado, 6, 7, 8)
label define edu_hdmf ///
	1 "Menos de primaria" 2 "Primaria incompleta" 3 "Primaria completa" ///
	4 "Media incompleta" 5 "Media completa" 6 "Tecnica" ///
	7 "Universitaria completa" 8 "Posgrado"
label values edu_hdmf edu_hdmf
label var edu_hdmf "Nivel educativo agregado HDMF"
tab edu_hdmf, m
/*===========================================================
  SECTION — OCCUPATION & OVERQUALIFICATION
  ENCFT (DOM) does not collect occupation codes compatible
  with ISCO-08. Variables set to NOT AVAILABLE.
===========================================================*/
gen byte ocupa_ci = .
label var ocupa_ci "ISCO-08 major group — NOT AVAILABLE from ENCFT"
gen byte overqualified_ci = .
label var overqualified_ci "Overqualified — NOT AVAILABLE (ocupa_ci missing in ENCFT)"

gen byte edu_isced = .
replace edu_isced = 0 if inlist(nivel_ultimo_ano_aprobado, 1, 9, 10)
replace edu_isced = 1 if nivel_ultimo_ano_aprobado==2
replace edu_isced = 2 if inlist(nivel_ultimo_ano_aprobado,3,4) & ultimo_ano_aprobado>=1 & ultimo_ano_aprobado<=3
replace edu_isced = 3 if inlist(nivel_ultimo_ano_aprobado,3,4) & ultimo_ano_aprobado>=4
replace edu_isced = 5 if nivel_ultimo_ano_aprobado==5 & ultimo_ano_aprobado>=1 & ultimo_ano_aprobado<4
replace edu_isced = 6 if nivel_ultimo_ano_aprobado==5 & ultimo_ano_aprobado>=4
replace edu_isced = 7 if inlist(nivel_ultimo_ano_aprobado, 6, 7)
replace edu_isced = 8 if nivel_ultimo_ano_aprobado==8
label define edu_isced_lbl ///
	0 "ISCED 0 Early childhood / less than primary" 1 "ISCED 1 Primary" ///
	2 "ISCED 2 Lower secondary" 3 "ISCED 3 Upper secondary" ///
	5 "ISCED 5 Short-cycle tertiary" 6 "ISCED 6 Bachelor or equivalent" ///
	7 "ISCED 7 Masters or equivalent" 8 "ISCED 8 Doctoral or equivalent"
label values edu_isced edu_isced_lbl
label var edu_isced "Nivel educativo ISCED"
tab edu_isced, m


		*****************************
		*** VARIABLES DE MIGRACION**
		*****************************

gen byte migrante_ci = (pais_nacimiento!=647 & pais_nacimiento!=.)
label var migrante_ci "=1 si es migrante (nacido fuera de DOM)"

gen byte migrantiguo5_ci = .
label var migrantiguo5_ci "=1 si migrante antiguo >=5 anos (no disponible en ENCFT)"

gen str40 mig_pais_ci = ""
replace mig_pais_ci = "Venezuela"         if pais_nacimiento==850  & migrante_ci==1
replace mig_pais_ci = "Cuba"              if pais_nacimiento==105  & migrante_ci==1
replace mig_pais_ci = "Colombia"          if pais_nacimiento==169  & migrante_ci==1
replace mig_pais_ci = "Puerto Rico"       if pais_nacimiento==580  & migrante_ci==1
replace mig_pais_ci = "Estados Unidos"    if pais_nacimiento==845  & migrante_ci==1
replace mig_pais_ci = "España"            if pais_nacimiento==724  & migrante_ci==1
replace mig_pais_ci = "Italia"            if pais_nacimiento==380  & migrante_ci==1
replace mig_pais_ci = "Argentina"         if pais_nacimiento==32   & migrante_ci==1
replace mig_pais_ci = "Bolivia"           if pais_nacimiento==68   & migrante_ci==1
replace mig_pais_ci = "Brasil"            if pais_nacimiento==76   & migrante_ci==1
replace mig_pais_ci = "Chile"             if pais_nacimiento==152  & migrante_ci==1
replace mig_pais_ci = "Ecuador"           if pais_nacimiento==218  & migrante_ci==1
replace mig_pais_ci = "Peru"              if pais_nacimiento==604  & migrante_ci==1
replace mig_pais_ci = "Mexico"            if pais_nacimiento==484  & migrante_ci==1
replace mig_pais_ci = "Panama"            if pais_nacimiento==591  & migrante_ci==1
replace mig_pais_ci = "Guatemala"         if pais_nacimiento==320  & migrante_ci==1
replace mig_pais_ci = "Honduras"          if pais_nacimiento==340  & migrante_ci==1
replace mig_pais_ci = "El Salvador"       if pais_nacimiento==222  & migrante_ci==1
replace mig_pais_ci = "Costa Rica"        if pais_nacimiento==188  & migrante_ci==1
replace mig_pais_ci = "Jamaica"           if pais_nacimiento==388  & migrante_ci==1
replace mig_pais_ci = "Haiti"             if pais_nacimiento==341  & migrante_ci==1
replace mig_pais_ci = "Otro no LAC"       if migrante_ci==1 & mig_pais_ci==""
label var mig_pais_ci "Pais de nacimiento del migrante (texto)"


		***************************************
		*** VARIABLES DE REFERENCIA EXTERNA ***
		***************************************

gen lp_ci = .
replace lp_ci = 5319.5 if zona==1
replace lp_ci = 4736.2 if zona==2
label var lp_ci "Linea de pobreza oficial del pais (DOP mensuales, 2019)"

gen lpe_ci = .
replace lpe_ci = 2395.2 if zona==1
replace lpe_ci = 2295.0 if zona==2
label var lpe_ci "Linea de pobreza extrema del pais (DOP mensuales, 2019)"

gen salmm_ci = 9411.6
label var salmm_ci "Salario minimo legal mensual (DOP, 2019)"


		***************************************
		*** KEEP: solo variables HDMF estandar***
		***************************************

keep ///
	pais_c anio_c trimestre_c mes_c ///
	idh_ch idp_ci factor_ci factor_ch ///
	edad_ci sexo_ci relacion_ci miembros_ci ///
	condocup_ci emp_ci desemp_ci inactivo_ci pea_ci ///
	horaspri_ci horastot_ci ///
	cotizando_ci afiliado_ci formal_ci tipocontrato_ci categopri_ci ///
	ocupa_ci overqualified_ci ///
	ylmpri_ci ylnmpri_ci ylmsec_ci ylnmsec_ci ylmotros_ci ylnmotros_ci ///
	ylm_ci ylnm_ci ynlm_ci ynlnm_ci ytot_ci ///
	ylm_ch ylnm_ch ynlm_ch ///
	remesas_ci remesas_ch ///
	nrylmpri_ci nrylmpri_ch ///
	aedu_ci edu_hdmf edu_isced ///
	migrante_ci migrantiguo5_ci mig_pais_ci ///
	lp_ci lpe_ci salmm_ci

order pais_c anio_c trimestre_c mes_c ///
	idh_ch idp_ci factor_ci factor_ch ///
	edad_ci sexo_ci relacion_ci miembros_ci ///
	migrante_ci migrantiguo5_ci mig_pais_ci ///
	condocup_ci emp_ci desemp_ci inactivo_ci pea_ci ///
	formal_ci tipocontrato_ci horaspri_ci horastot_ci cotizando_ci afiliado_ci ///
	ocupa_ci overqualified_ci ///
	aedu_ci edu_hdmf edu_isced ///
	ylm_ci ylnm_ci ynlm_ci ytot_ci remesas_ci remesas_ch

compress

save "`base_out'", replace

log close
