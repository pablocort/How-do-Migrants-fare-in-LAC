clear
set more off

di "File created with the Claude HDMF system — 2026-05-01"

*________________________________________________________________________________________________________________*

global surveysFolder "\\sapidbshares.file.core.windows.net\idbshares\SURVEYS"
display "$surveysFolder"

global ruta = "${surveysFolder}"

local PAIS PER
local ENCUESTA ENAHO
local ANO "2024"
local ronda a 

local log_file = "$ruta\harmonized\\`PAIS'\\`ENCUESTA'\log\\`PAIS'_`ANO'`ronda'_variablesBID.log"
local base_in  = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\per\\`PAIS'_`ANO'`ronda'.dta"


/***************************************************************************
                 BASES DE DATOS DE ENCUESTA DE HOGARES
*************************************************************************** */


if c(username)=="STEFFANNYR" {

use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\per\PER_2024a.dta", clear
local base_out = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"

}

if c(username)=="PABLOCOR" {

use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\per\PER_2024a.dta", clear
local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"

}


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
	/* p208a:  �que edad tiene en a�os cumplidos?  (en a�os)
    Va de 0 a 98 años -- tab p208a, m
		*/
	gen int edad_ci=p208a
	replace edad_ci=. if edad_ci==99

	******************
	*idh_ch (idhogar) : Identificador único de hogares *
	******************
	sort conglome vivienda hogar 
	cap egen idh_ch= group(conglome vivienda hogar)
	tostring idh_ch, replace
	bysort idh_ch: egen int nmiembros_ch = total(miembros_ci)

	***************
	****idp_ci (idindividuio) : Identificador único del individuo *****
	***************
	gen idp_ci = codperso
	tostring idp_ci, replace format ("%20.0f") 

	*******************************************
	*Factor de expansion del hogar (factor_ch) : factor de ponderación de los hogares*
	*******************************************
	gen factor_ch= factor07	
	
	***********
	*factor_ci: factor de ponderación a la población total * 
	***********
	gen factor_ci=facpob07
	
	* de nuevo factor07 y facpob07 -- son iguales

	*************
	*condocup_ci: Identifica la condición de ocupación del individuo. *
	*************
	/* Variable de condición de acrividad económica de la encuesta - p501, p502 y p503 
	
	p501:LA SEMANA PASADA, DEL……...........… AL……..…., ¿TUVO UD. ALGÚN TRABAJO? (Sin contar los quehaceres del hogar)
	p502: AUNQUE NO TRABAJÓ LA SEMANA PASADA, ¿TIENE ALGÚN EMPLEO FIJO AL QUE PRÓXIMAMENTE VOLVERÁ?
	p503: AUNQUE NO TRABAJÓ LA SEMANA PASADA, ¿TIENE ALGÚN NEGOCIO PROPIO AL QUE PRÓXIMAMENTE VOLVERÁ?
	
	Categorias de condocup_ci:
			1	Ocupado
			2	Desocupado
			3	Inactivo
			4	Menor que la edad límite de los entrevistados
	*/	

	gen byte condocup_ci = .
	replace condocup_ci = 1 if p501==1 | p502==1 | p503==1    //Ocupados
	replace condocup_ci = 2 if p501==2 & p502==2 & p503==2    //Desocupados
	replace condocup_ci = 3 if condocup_ci == 2 & ( p5041==2 & p5042==2 & p5043==2 & p5044==2 & p5045==2 & p5046==2 & p5047==2 & p5048==2 & p5049==2 & p50410==2 & p50411==2 ) //Inactivos
	replace condocup_ci=. if !inrange(edad_ci, 15,64)

	
	*******************
	***categoinac_ci: Identifica la condición de inactividad de los individuos.***
	*******************
	/*

	�que estuvo haciendo la semana pasada - p546
	
	
	Categorias de categoinac_ci:
			1	Jubilados o pensionados
			2	Estudiantes
			3	Quehaceres domésticos
			4	Otros inactivos
	*/

	gen byte categoinac_ci = .
	replace categoinac_ci = 1 if  (p546==6   & condocup_ci==3) //Jubilado o Pensionado
	replace categoinac_ci = 2 if  (p546 == 4 & condocup_ci == 3) //Estudiante
	replace categoinac_ci = 3 if  (p546 == 5 & condocup_ci == 3) //Quehaceres domesticos
	replace categoinac_ci = 4 if  ((categoinac_ci ~=1 & categoinac_ci ~=2 & categoinac_ci ~=3) & condocup_ci==3) //Otros Inactivos
* Notar que pueden haber missings
	
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
	
	***************
	***horaspri_ci: Variable continua que indica el número de horas totales trabajadas en la actividad principal en la semana de referencia.***
	***************
	*Horas trabajadas en la actividad principal - p513t: ¿CUÁNTAS HORAS TRABAJÓ LA SEMANA PASADA, EN SU OCUPACIÓN PRINCIPAL
	gen byte horaspri_ci   = .
	replace  horaspri_ci   = p513t if emp_ci==1
	replace  horaspri_ci   = . if emp_ci~=1 //Reemplazando los missings  y los que no trabajan
	
	***************
	***horastot_ci: Variable continua que indica el número de horas totales trabajadas en todas las actividades económicas en una semana.***
	***************	
	* p518: ¿CUÁNTAS HORAS TRABAJÓ LA SEMANA PASADA EN SU(S) OCUPACIÓN(ES) SECUNDARIA(S)?
	egen  horastot_ci   = rsum(horaspri_ci p518) if emp_ci==1
	replace  horastot_ci   = . if emp_ci~=1 //Reemplazando los missings  y los que no trabajan

	*****************
	***parcial_ci***
	*****************
	gen byte parcial_ci = .
	replace parcial_ci = (horaspri_ci < 35) if emp_ci == 1 & horaspri_ci != .
	label define parcial_lb 1 "Parcial (<35h)" 0 "Completo (>=35h)"
	label values parcial_ci parcial_lb
	label var parcial_ci "1 = trabajador a tiempo parcial (horaspri_ci < 35h)"

	***********
	***pea_ci: Variable dicotómica que indica la población económicamente activa (PEA).***
	***********
	*Codigo extraido del manual
	gen byte pea_ci = .
	replace  pea_ci = 1 if inlist(condocup_ci,1,2) //Ocupados y Desocupados
	replace  pea_ci = 0 if inlist(condocup_ci,3,4) //Inactivos y menores de 15 años -
	
	
	***************
	***cotizando_ci: Variable dicotómica que indica con valor 1 si el asalariado o independiente cotiza a la seguridad social, de forma voluntaria o por medio de su empleador, en el periodo de referencia, con 0 a los desocupados o independientes que no responden, si la encuesta no les pregunta y con valores perdidos si la variable original lo tiene. ***
	*Se considera únicamente el sistema de pensiones público o privado (no salud) de la ocupación principal o secundaria*
	***************	
	/* p558a ¿EL SISTEMA DE PENSIONES AL CUAL UD. ESTÁ AFILIADO ES:
		0	Pase
		1	Sistema privado de pensiones (AFP)? 
		2	Sistema Nacional de Pensiones: Ley 19990
		3	Sistema Nacional de Pensiones Ley 20530 (cédula viva)
		4	Otro Sistema Nacional de pensiones
	
	 p558b2 ¿Cuál fue el último año que aportó al Sistema de Pensiones?
	 */
	 
	 
	****************
	gen cotizando_ci=.
	replace cotizando_ci=1 if (p558a1==1 | p558a2==2 | p558a3==3 | p558a4==4) & p558b2==2024 //Está afiliado a un sistema privado/nacional de pensiones y el individuo ha aportado el 2024 (p558b2==2024)
	replace cotizando_ci=0 if cotizando_ci==. //Se coloca cero a los desocupados
	label var cotizando_ci "Cotizante a la Seguridad Social/pension"	

	
	***************
	***afiliado_ci: Variable dicotómica que indica con valor 1 si el trabajador está afiliado a la Seguridad Social (independientemente que haya o no cotizado en el mes de referencia), con 0 al resto del grupo de referencia y mantenemos con valores perdidos si la encuesta los tiene como perdidos***
	***************	
	gen afiliado_ci=.
	replace afiliado_ci=1 if (p558a1==1 | p558a2==2 | p558a3==3 | p558a4==4) //Está afiliado a un sistema privado/nacional de pensiones   
	replace afiliado_ci=0 if afiliado_ci==. //Se coloca cero a los desocupados
	label var afiliado_ci "Afiliado sistema de pensiones"	
	
	
	
	**************
	***formal_ci: Variable dicotómica que indica con valor 1 si el trabajador es formal y con 0 al resto. Un individuo se califica como formal si está afiliado o cotiza a la Seguridad Social. ***
	**************

	gen byte   formal_ci=.

	replace formal_ci  =  1 if (cotizando_ci == 1 | afiliado_ci == 1) & condocup_ci == 1
	replace formal_ci = 0 if (cotizando_ci == 0 & afiliado_ci == 0) & (condocup_ci == 1 )
label var formal_ci "1=afiliado o cotizante"
	
	
	***************
	***categopri_ci: Indica la categoría ocupacional de la actividad principal para los ocupados. (Solo aplica para los trabajadores ocupados emp_ci=1) ***
	***************	
	
	/*p507 - UD. SE DESEMPEÑÓ EN SU OCUPACIÓN PRINCIPAL O NEGOCIO COMO:
		1 -  ¿Empleador o patrono? 
		2-   ¿Trabajador independiente? 
		3-   ¿Empleado? 
		4-   ¿Obrero? 
		5 -  ¿Trabajador familiar no remunerado? 
		6 -  ¿Trabajador del hogar? 
		7 -  ¿Otro? 
	
	Categorias de categopri_ci: 
			0	Otra clasificación
			1	Patrón o empleador
			2	Cuenta Propia o independiente
			3	Empleado o asalariado
			4	Trabajador no remunerado
	*/
	
		gen categopri_ci=.
		replace categopri_ci=0 if condocup_ci==1 & p507==7  // Otra clasificación
		replace categopri_ci=1 if condocup_ci==1 & p507==1  // Patron o empleador
		replace categopri_ci=2 if condocup_ci==1 & p507==2  // Cuenta propia
		replace categopri_ci=3 if condocup_ci==1 & (p507==3 | p507==4 | p507==6) //Empleado
		replace categopri_ci=4 if condocup_ci==1 & p507==5 // Trabajador no remunerado

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
	***tipocontrato_ci: Variable categórica que indica el tipo de contrato laboral de los empleados/asalariados en la actividad principal según su duración (los trabajadores no asalariados deberían identificarse con valor perdido).***
	*******************
	/* BAJO QUÉ TIPO DE CONTRATO - p511a:
		1 - ¿Contrato indefinido, nombrado, permanente? 
		2 - ¿Contrato a plazo fijo (sujeto a modalidad)? 
		3 - ¿Está en período de prueba? 
		4 - ¿Convenios de Formación Laboral Juvenil / Prácticas Pre-Profesionales? 
		5 - ¿Contrato por locación de servicios (Honorarios Profesionales, R.U.C.), SNP? 
		6 - ¿Régimen Especial de Contratación Administrativa (CAS)? 
		7 - ¿Sin Contrato? 
		8 - ¿Otro? 
	
	Categorias de tipocontrato_ci:
			0	Con contrato
			1	Permanente/indefinido.
			2	Temporal/tiempo definido.
			3	Sin contrato/verbal
	*/
	
	*****************
	gen 	tipocontrato_ci=. 
	replace tipocontrato_ci=1 if (p511a==1) & categopri_ci==3 // Permanente/indefinido. - categopri_ci-empleado
	replace tipocontrato_ci=2 if (p511a>=2 & p511a<=6) & categopri_ci==3 // Temporal/tiempo definido. - categopri_ci-empleado
	replace tipocontrato_ci=3 if (p511a==7 | tipocontrato_ci==.) & categopri_ci==3 // Sin contrato/verbal
	
	label var tipocontrato_ci "Tipo de contrato segun su duracion"
	label define tipocontrato_ci 1 "Permanente/indefinido" 2 "Temporal" 3 "Sin contrato/verbal" 
	label value tipocontrato_ci tipocontrato_ci
	

*****************   VARIABLES DE INGRESO   *************************************
********************************************************************************

	*************
	* ylmpri_ci: Ingreso laboral monetario de actividad principal: Variable continua que indica el monto mensual de ingresos monetarios provenientes de la actividad principal. Incluye: sueldos, salarios, jornales, trabajos a destajo, comisiones, propinas, horas extras, aguinaldos (empleados) y ganancia neta (patrones y cuenta propia). *
	*************
/*			i524e1	¿Ingreso líquido (anual) en la ocupación principal
			i530a	En su ocupación principal, ///
					¿Cuál fue la ganancia neta en el  mes anterior ? ///
					(Variable Anualizada)
*/
	gen ylmprid = i524e1 /12 // Ocupacion principal dependiente
	gen ylmprii = i530a  /12 // Ocupacion principal independiente (ganancia)
	egen ylmpri_ci=rsum(ylmprid ylmprii), missing
	label var ylmpri_ci "Ingreso Laboral Monetario de la Actividad Principal"

	************
	* ylmsec_ci: Ingreso laboral monetario de actividad secundaria: Variable continua que indica el monto mensual de ingresos monetarios provenientes de la actividad secundaria. *
	************
/*			i538e1	Ingreso líquido en sus ocupaciónes secundarias?
			i541a	En su(s) ocupación(es) secundaria(s), ///
					¿Cuál fue su ganancia neta en el mes anterior? (Var. Anualizada)
*/
	gen ylmsecd = i538e1/12 // Ocupacion secundaria dependiente
	gen ylmseci = i541a/12 // Ocupacion secundaria independiente (ganancia)
	egen ylmsec_ci=rsum(ylmsecd ylmseci), missing
	drop ylmsecd ylmseci
	label var ylmsec_ci "Ingreso Laboral Monetario de la Actividad Secundaria"
	
	**************
	* ylmotros_ci: Ingreso laboral monetario de otras actividades: Variable continua que indica el monto mensual de ingresos monetarios provenientes de actividades distintas de la principal y secundaria. Incluye ingresos percibidos por desocupados o inactivos derivados de trabajos previos al cese. *
	**************
	*d544t: En los últimos 12 meses ¿ Recibió en Total Ingresos extraordinarios ( Monto total )
	gen ylmotros_ci = d544t/12 //Convirtiendo el monto a mensual
	label var ylmotros_ci "Ingreso laboral monetario de otros trabajos" 

	
	*********
	* ylm_ci:Ingreso laboral monetario total: Variable continua que indica el monto mensual total de ingresos laborales monetarios provenientes de todas las actividades. Esta variable equivale a la suma de las variables ylmpri_ci, ymsec_ci e ylnmotros_ci.*
	*********
	*Codigo extraído del manual
	egen double ylm_ci = rowtotal(ylmpri_ci ylmsec_ci ylmotros_ci), mi
	replace ylm_ci=. if ylmpri_ci==. & ylmsec_ci==. & ylmotros_ci==.
	label var ylm_ci "Ingreso laboral monetario total" 

	
	**************
	* ylnmpri_ci: Ingreso laboral no monetario de actividad principal: Variable continua que representa el monto mensual del ingreso laboral no monetario derivado de la actividad principal de cada miembro del hogar.*
	*************
/*			d529t	¿Con qué frecuencia y en cuánto estima Ud. ///
					el pago Total (Valor estimado por vez)? - Var. Anualizada
			d536	¿En cuánto estima Ud., el valor de los ///
					productos utilizados para su consumo en el mes anterior?
*/	
	gen ylnmprid = d529t /12 // Pago en especie - Ocupacion principal dependiente
	gen ylnmprii = d536  /12 // Autoconsumo - Ocupacion principal independiente
	egen ylnmpri_ci=rsum(ylnmprid ylnmprii), missing
	drop ylnmprid ylnmprii
	label var ylnmpri_ci "Ingreso laboral NO monetario de la actividad principal"

	**************
	* ylnmsec_ci: Ingreso laboral no monetario de actividad secundaria: Variable continua que representa el monto mensual del ingreso laboral no monetario derivado de la actividad secundaria de cada miembro del hogar.*
	**************
/*			d540t	En su ocupación secundaria, ///
					¿En cuánto estimaría el pago Total de Alimentos, ... , etc?
			d543	¿En cuanto estima Ud., el valor de los productos ///
					utilizados para su consumo en el mes anterior?
*/
	gen ylnmsecd = d540t /12 // Pago en especie - Ocupacion secundaria dependiente
	gen ylnmseci = d543  /12 // Autoconsumo - Ocupacion secundaria independiente
	egen ylnmsec_ci=rsum(ylnmsecd ylnmseci), missing 
	drop ylnmsecd ylnmseci
	label var ylnmsec_ci "Ingreso laboral NO monetario de la actividad secundarioa" 

	****************
	* ylnmotros_ci: Ingresos laboral no monetario de otras actividades: Variable continua que representa el monto mensual del ingreso laboral no monetario derivado de actividades distintas de la principal y/o secundaria de cada miembro del hogar.*
	****************
	gen ylnmotros_ci=. //No hay una variable de ingresos LABORALES no monetarios que haga referencia a otra ocupación que no sea ni la principal ni la secundaria. 
	label var ylnmotros_ci "Ingreso laboral NO monetario de otros trabajos" 
	
	**********
	* ylnm_ci: Ingreso laboral no monetario: Variable continua que indica el monto mensual total de ingresos laborales no monetarios provenientes de todas las actividades. Esta variable equivale a la suma de las variables ylnmpri_ci, ylnmsec_ci e ylnmotros_ci.*
	**********
	*Codigo extraído del manual
	egen double ylnm_ci = rowtotal(ylnmpri_ci ylnmsec_ci ylnmotros_ci), mi
	replace ylnm_ci = . if ylnm_ci < 0 & ylnm_ci != .
	label var ylnm_ci "Ingreso laboral NO monetario total"  

	**********
	* ynlm_ci:  Ingreso no laboral monetario público del individuo. Variable continua que indica el monto mensual del ingreso no laboral MONETARIO proveniente de otras fuentes no laborales.*
	**********
/*Las siguientes variables están anualizadas:	
		d556t1	Los últimos 6 meses, ¿ Recibió Ud. ingresos por ///
				el Total de Transferencias Corrientes ?
		d556t2	Los últimos 6 meses, ¿ Recibió Ud. ingresos por ///
				el Total de Transferencias Corrientes ?
		d557t	Los últimos 12 meses el Monto Total por Rentas de la Propiedad
		d558t	Los últimos 12 meses, el Monto Total por Otros Ingresos Extraordinarios
*/
	gen trans_corr_loc = d556t1/12 //Transferencias corrientes mensuales NACIONALES
	gen trans_corr_ext = d556t2/12 //Transferencias corrientes mensuales EXTRANJERAS
	gen rentas = d557t/12 //Rentas
	gen otros_ing = d558t/12 //Otros Ingresos	
	egen ynlm_ci  = rowtotal(trans_corr_loc trans_corr_ext rentas otros_ing), missing 
	
	***********
	* ynlnm_ci:Ingreso no laboral no monetario. Variable continua que indica el monto mensual del ingreso no laboral no monetario (otras fuentes). En esta categoría se encuentran otros beneficios y transferencias no monetarias como las donaciones en alimentos, útiles escolares, becas, entre otros.*
	***********
	gen ynlnm_ci = (ig06hd+ig08hd+sig24+sig26+gru13hd1+gru13hd2+gru13hd3+gru23hd1+gru23hd2+gru23hd3+gru24hd+gru33hd1+gru33hd2+gru33hd3+(gru34hd-ga04hd)+gru43hd1+gru43hd2+gru43hd3+gru44hd+gru53hd1+gru53hd2+gru53hd3+gru54hd+gru63hd1+gru63hd2+gru63hd3+gru64hd+gru73hd1+gru73hd2+gru73hd3+gru74hd+gru83hd1+gru83hd2+gru83hd3+gru84hd+gru14hd3+gru14hd4+gru14hd5+sg42d+sg42d1+sg42d2+sg42d3) /(12 * nmiembros_ch)
	label var ynlnm_ci "Ingreso No Laboral No Monetario" 
	
	**********
	* ytot_ci: Ingreso mensual total del individuo que incluye las variables ylm_ci ylnm_ci ynlm_ci ynlnm_ci*
	**********
	*Codigo extraído del manual
	egen double ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci ynlnm_ci), mi
	label var ytot_ci "Ingreso No Laboral No Monetario" 
	
	*********
	* ylm_ch: Ingreso laboral monetario del hogar. Variable continua que indica el monto mensual del ingreso laboral monetario del hogar, ignora las `No respuesta'.  *
	*********
	*Codigo extraido del manual
	bysort idh_ch: egen double ylm_ch = total(ylm_ci) if miembros_ci == 1, mi
	label var ylm_ch "Ingreso laboral monetario del hogar"

	**********
	* ylnm_ch: Ingreso laboral no monetario del hogar. Variable continua que indica el monto del ingreso laboral no monetario del hogar.*
	**********
	*Codigo extraído del manual
	bysort idh_ch: egen double ylnm_ch = total(ylnm_ci) if miembros_ci == 1, mi
	label var ylnm_ch "Ingreso laboral no monetario del hogar"

	***********
	* ynlnm_ch: Ingreso no laboral no monetario del hogar. Variable continua que indica el monto mensual del ingreso no laboral no monetario del hogar (otras fuentes).*
	***********
	*Codigo extraído del manual
	bysort idh_ch: egen double ynlnm_ch = total(ynlnm_ci) if miembros_ci == 1, mi

	*********
	* ynlm_ch: Ingreso no laboral monetario del hogar. Variable continua que indica el monto mensual del ingreso no laboral monetario del hogar (otras fuentes). Es la suma de ynlm_publico_ch y ynlm_privado_ch.*
	*********
	*Suma de los ingresos laborales no monetarios de todos los miembros del hogar
	by idh_ch, sort: egen ynlm_ch=sum(ynlm_ci) if miembros_ci==1, missing 
	label var ynlm_ch "Ingreso no laboral monetario del hogar"
	
	**********
	* ytot_ch: Ingreso mensual total del hogar*
	**********
	*Codigo extraído del manual
	egen double ytot_ch= rowtotal(ylm_ch ylnm_ch ynlm_ch ynlnm_ch), mi

	***************
	* ylmhopri_ci: Variable continua que indica el monto del salario horario monetario de la actividad principal.*
	***************
	*Codigo extraído del manual
    gen byte ylmhopri_ci = ylmpri_ci / (4.3 * horaspri_ci)
	replace ylmhopri_ci = . if ylmhopri_ci <= 0
	label var ylmhopri_ci "Salario monetario de la actividad principal" 
 
	**********
	* ylmho_ci: Variable continua que indica el monto del salario horario monetario de todas las actividades.*
	**********
	*Codigo extraído del manual
	gen byte ylmho_ci = ylm_ci / (4.3 * horastot_ci)
	replace ylmho_ci = . if ylmho_ci <= 0
  
	**************
	* nrylmpri_ci: No respuesta a nivel individuo. Indica la no respuesta ingreso de la actividad principal. Para construir esta variable, se tiene en cuenta que no reporte ingresos laborales (ylmpri_ci==. ) y además la persona reporte estar ocupado (emp_ci==1)*
	**************
/*		1: Indica que tiene empleo, pero no reporta el ingreso 
		0: Caso contrario
*/
	*Codigo extraído del manual
	gen byte nrylmpri_ci = .
	replace nrylmpri_ci = 1 if ylmpri_ci == . & emp_ci == 1 //Ocupado y no declara ingresos
	replace nrylmpri_ci = 0 if ylmpri_ci != . & emp_ci == 1 //Ocupado y si declara impuestos

	**************
	* nrylmpri_ch: No respuesta a nivel hogar. Hogares con algún miembro que no respondió por ingresos*
	**************
/*		1: Indica que tiene empleo, pero no reporta el ingreso 
		0: De lo contrario
*/
	*Codigo extraído del manual
	by idh_ch, sort: egen byte nrylmpri_ch = sum(nrylmpri_ci) if miembros_ci==1
	replace nrylmpri_ch = 1 if nrylmpri_ch > 0 & nrylmpri_ch < .
	
********************************************************************************
***************   VARIABLES DE EDUCACION   *************************************
********************************************************************************


	***************
	*** aedu_ci: Variable numérica que indica el número de años de educación culminados de las personas encuestadas.
	***************
	egen grados = rowtotal(p301b  p301c), missing // necesaria temporalmente
		
	gen byte aedu_ci=.
	replace aedu_ci=0  			if p301a==1 | p301a==2 // Sin nivel o educación inicial o prescolar
	replace aedu_ci=grados 		if p301a==3 // Primaria incompleta
	replace aedu_ci=6 			if p301a==4 // Primaria completa - 6 años
	replace aedu_ci=6 + grados 	if p301a==5 // Secundaria incompleta
	replace aedu_ci=11 			if p301a==6 // Secundaria completa - 11 años
	replace aedu_ci=11 + grados if p301a==7 // Superior no universitaria incompleta
	replace aedu_ci=13			if p301a==8 // Superior no universitaria completa
	replace aedu_ci=11 + grados if p301a==9 // Superior universitaria incompleta
	replace aedu_ci=16			if p301a==10 // Superior universitaria completa
	replace aedu_ci=16 + grados if p301a==11 // Maestria y/o Doctorador
	replace aedu_ci=. 			if p301a==12 // Básica Especial - Se considera missing
	
    drop grados

**************
*** edu_hdmf ***
**************	

gen edu_hdmf = .

* 1. menos de primaria
replace edu_hdmf = 1 if p301a==1 | p301a==2

* 2. primaria incompleta
replace edu_hdmf = 2 if  p301a==3

* 3. primaria completa
replace edu_hdmf = 3 if  p301a==4

* 4. Media incompleta (11°)
replace edu_hdmf = 4 if p301a==5

* 5. media completa (11°)
replace edu_hdmf = 5 if p301a==6
replace edu_hdmf = 5 if p301a==7 // superior no universitaria incompleta
replace edu_hdmf = 5 if p301a==9 // superior universitaria incompleta
 
 
* 6. técnica completa (terciaria no universitaria)
replace edu_hdmf = 6 if p301a==8

* 7. universitaria completa
replace edu_hdmf = 7 if p301a==10

* 8	. posgrado
replace edu_hdmf = 8 if   p301a==11 


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
/* p508: expected to be CIUO-88 3-digit occupation code in ENAHO 2024.
   VERIFY: tab p508 if emp_ci==1 — expected range 100-999 (3-digit) or 1000-9999 (4-digit).
   If 4-digit, the first digit still gives the correct CIUO-88 major group.
   NOTE: PER uses CIUO-88 (not ISCO-08); groups 1-5 and 9 are comparable;
   groups 6-8 differ slightly. Caveat documented in overqualified_ci label. */
***********
gen byte ocupa_ci = .
replace ocupa_ci = real(substr(string(int(p508)), 1, 1)) if emp_ci == 1 & !missing(p508) & p508 > 0
label define ocupa_lbl 1 "Directors/Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary"
label values ocupa_ci ocupa_lbl
label var ocupa_ci "CIUO-88 major group (1-9) — VERIFY variable p508 in ENAHO 2024"

***********
* overqualified_ci
* edu_hdmf >= 6: técnica, university complete, or postgrad (8-level PER scale)
* ocupa_ci >= 4: clerical, service, agriculture, craft, machine, elementary
* NOTE: CIUO-88 vs ISCO-08 caveat — groups 6-8 not directly comparable
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified"
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (tertiary educ + low-skill occ, CIUO-88 4-9; verify p508)"




	*************
	* remesas_ci: Variable continua que indica el monto mensual por remesas reportadas por el individuo en moneda local corriente. *
	*************
/*	Las siguientes variables están anualizadas:
	d5563c	¿Recibió Ud., ingresos por ...: Pensión por remesas ///
			de otros hogares o personas (Monto en S/. del pais)
	d5563e	¿Recibió Ud., ingresos por ...: Pensión ///
			por remesas de otros hogares o personas (Monto en S/. del extranjero)
*/
	gen remesas_loc = d5563c/12 //Monto mensual de remesas nacionales
	gen remesas_ext = d5563e/12 //Monto mensual de remesas extranjeras
	egen remesas_ci=rowtotal(remesas_loc remesas_ext), missing
	
	*************
	* remesas_ch: Variable continua que indica el monto mensual por remesas del hogar. Esta variable se genera a partir de la variable remesas_ci.*
	*************
	*Codigo extraído del manual 
	by idh_ch, sort: egen byte remesas_ch = sum(remesas_ci) if miembros_ci == 1

********************************************************************************
***************   VARIABLES DE MIGRACION   *************************************
********************************************************************************	
			
/* Variables de migracion */
* La información proviene del Modulo 400 de  SALUD **
	*******************
	*** migrante_ci: Si el individuo nació en otro país ***
	*******************	
	* p401g2 en que distrito y provincia vivia su madre?
	gen migrante_ci=(p401g2<10000) if p401g2!=. & p401g2!=999999
		
	**********************
	*** migantiguo5_ci: si el migrante ha estado viviendo 5 años o más en el país de la encuesta***
	**********************
	*p401f hace 5 aos,... vivia en este distrito?
	gen migrantiguo5_ci=(migrante_ci==1 & (p401f==1 | (p401g>10000 & p401g!=.))) if migrante_ci!=. & p401f!=3 & p401g!=999999 & p401f!=. & !inrange(edad_ci,0,4)		
	
	
	*pais de migrante (código)
	gen mig_pais_code = .
	replace mig_pais_code = p401g2 if migrante_ci==1

	gen str40 mig_pais_ci = ""

	* Rellenar según código (confirmar que se abarcan todos los países)
	/*
	replace mig_pais_ci = "Argentina" if mig_pais_code==
	replace mig_pais_ci = "Bolivia"   if mig_pais_code==
	replace mig_pais_ci = "Brasil"    if mig_pais_code==
	replace mig_pais_ci = "Canadá"    if mig_pais_code==
	replace mig_pais_ci = "Chile"     if mig_pais_code==
	replace mig_pais_ci = "Colombia"  if mig_pais_code==
	replace mig_pais_ci = "Costa Rica" if mig_pais_code==
	replace mig_pais_ci = "Cuba"      if mig_pais_code==
	replace mig_pais_ci = "República Dominicana" if mig_pais_code==
	replace mig_pais_ci = "El Salvador" if mig_pais_code==
	replace mig_pais_ci = "Alemania"  if mig_pais_code==
	replace mig_pais_ci = "Honduras"  if mig_pais_code==
	replace mig_pais_ci = "India"     if mig_pais_code==
	replace mig_pais_ci = "Italia"    if mig_pais_code==
	replace mig_pais_ci = "México"    if mig_pais_code==
	replace mig_pais_ci = "Marruecos" if mig_pais_code==
	replace mig_pais_ci = "Perú"      if mig_pais_code==
	replace mig_pais_ci = "Filipinas" if mig_pais_code==
	replace mig_pais_ci = "Sudáfrica" if mig_pais_code==
	replace mig_pais_ci = "Zimbabwe"  if mig_pais_code==
	replace mig_pais_ci = "España"    if mig_pais_code==
	replace mig_pais_ci = "Ucrania"   if mig_pais_code==
	replace mig_pais_ci = "Reino Unido" if mig_pais_code==
	replace mig_pais_ci = "Estados Unidos" if mig_pais_code==
	*/
	replace mig_pais_ci = "Venezuela" if mig_pais_code==4037
	replace mig_pais_ci = "Otro" if mig_pais_ci=="" &  migrante_ci==1
	
	
		
local PAIS PER
local ENCUESTA ENAHO
local ANO "2024"
local ronda a 

if c(username)=="STEFFANNYR" {

local base_out = "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"

}

if c(username)=="PABLOCOR" {

local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"

}

***************
***jefe_ci***
***************
gen jefe_ci = (relacion_ci == 1)
label var jefe_ci "Jefe de hogar"
label def jefe_ci 1 "Si" 0 "No"
label val jefe_ci jefe_ci

save "`base_out'", replace

	
	