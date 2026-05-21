*(Versión stata 17)

**# Bookmark #1
clear
set more off

di "File created with the Claude HDMF system — 2026-04-08"

*________________________________________________________________________________________________________________*
* COL GEIH 2018t3 — HDMF harmonization script
* Alternative constructions documented below (dictionary break: 2018–2021 vs 2022+):
*   factor_ci/ch : fex_c_2011  (fex_c18 absent in 2018–2021)
*   condocup_ci  : ini flag     (fft absent in 2018–2021)
*   aedu_ci      : p6210/p6210s1 (p3042 module absent in 2018–2021)
*   migrante_ci  : p6074/p756   (p3373 module absent in 2018–2021)
*   migrantiguo5 : p755          (p3382 absent in 2018–2021)
*   profesion_ci : NOT AVAILABLE (p3042s2 absent)
*   miglac_ci    : p756s3 (LAC categories — migration module dict 2018-2021)
*   mig_pais_ci  : p756s3 (11 country categories — migration module dict 2018-2021)
* Reference: COL_2018t3_variablesBID.do (bases armo/raw/col/alternative_do_files/)
*________________________________________________________________________________________________________________*

local PAIS COL
local ENCUESTA GEIH
local ANO "2018"
local ronda t3

capture log close
cap log off

/***************************************************************************
                 BASES DE DATOS DE ENCUESTA DE HOGARES
*************************************************************************** */

if c(username)=="PABLOCOR" {

use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\col\COL_`ANO'`ronda'.dta", clear
local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'\\`PAIS'_`ANO'`ronda'_BID.dta"
capture mkdir "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'"
}


*****************
***relacion_ci***
*****************
g 		relacion_ci = 1 if p6050 == 1
replace relacion_ci = 2 if p6050 == 2
replace relacion_ci = 3 if p6050 == 3
replace relacion_ci = 4 if inlist(p6050,4,5,6,7,8,9)
replace relacion_ci = 5 if p6050 == 11 | p6050 == 12 | p6050 == 13
replace relacion_ci = 6 if p6050 == 10

*****************
***miembros_ci***
*****************
gen byte miembros_ci=(relacion_ci>=1 & relacion_ci<=5)
replace miembros_ci=. if relacion_ci==.

************
****pais_c****
************
g str3 pais_c = "COL"

***********
***sexo_ci***
***********
g sexo_ci = p6020
* p6020: 1=Hombre, 2=Mujer

**********
***edad***
**********
g edad_ci = p6040

***************
****idh_ch*****
***************
gen idh_ch = idh
tostring idh_ch, replace

**************
****idp_ci****
**************
g idp_ci=orden
tostring idp_ci, replace

**** factor_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): g factor_ci = fex_c18
* Source for this wave (2018–2021): fex_c_2011 — fex_c18 not in dataset
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****
g factor_ci = fex_c_2011
g factor_ch = fex_c_2011


**** condocup_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): oci / dsi / fft
* Source for this wave (2018–2021): oci / dsi / ini — fft not in dataset
* Note: 4-category version (category 4 = edad_ci < 10)
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****
gen byte condocup_ci = .
replace condocup_ci = 1 if oci == 1
replace condocup_ci = 2 if dsi == 1
replace condocup_ci = 3 if ini == 1
replace condocup_ci = 4 if edad_ci < 10
replace condocup_ci = . if !inrange(edad_ci, 15, 64)
label define condocup_ci 1 "Ocupado" 2 "Desocupado" 3 "Inactivo" 4 "Menor que 10"
label value condocup_ci condocup_ci

*******************
***categoinac_ci***
*******************
gen byte categoinac_ci = .
replace categoinac_ci=1 if p7450==5 & condocup_ci==3
replace categoinac_ci=2 if p7450==2 | (p6240==3 & condocup_ci==3)
replace categoinac_ci=3 if p7450==3 | (p6240==4 & condocup_ci==3)
replace categoinac_ci=4 if condocup_ci==3 & categoinac_ci==.

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
***horaspri_ci***
***************
gen int horaspri_ci = p6800
replace horaspri_ci = . if emp_ci == 0

***************
***horastot_ci***
***************
egen horastot_ci = rowtotal(p6800 p7045)
replace horastot_ci = . if p6800 == . & p7045 == .
replace horastot_ci = . if emp_ci == 0

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
replace pea_ci = 1 if inlist(condocup_ci,1,2)
replace pea_ci = 0 if inlist(condocup_ci,3,4)

******************
***cotizando_ci***
******************
gen byte cotizando_ci = .
replace cotizando_ci=1 if p6920==1
replace cotizando_ci=0 if p6920==2

*****************
***afiliado_ci***
*****************
* FIX-COL-01 (QA 2026-04-21): restrict to contributive/special health regime only
* p6090==1 includes Regimen Subsidiado (informal), inflating formality; use p6100 instead
gen byte afiliado_ci = inlist(p6100, 1, 2)
replace afiliado_ci=. if p6090==9
replace afiliado_ci=. if emp_ci != 1

**************
***formal_ci***
**************
gen byte formal_ci = .
replace formal_ci = 1 if (cotizando_ci == 1 | afiliado_ci == 1) & condocup_ci == 1
replace formal_ci = 0 if (cotizando_ci == 0 & afiliado_ci == 0) & condocup_ci == 1

*********************
***tipocontrato_ci***
*********************
gen byte tipocontrato_ci = .
replace tipocontrato_ci=1 if p6460==1 & condocup_ci==1
replace tipocontrato_ci=2 if p6460==2 & condocup_ci==1
replace tipocontrato_ci=3 if p6450==1 & condocup_ci==1
replace tipocontrato_ci=3 if p6440==2 & condocup_ci==1


	****************************
**# ***VARIABLES DE INGRESO***
	****************************
/* Income block intentionally omitted — will be added in a future session */


		****************************
**# ***VARIABLES DE EDUCACION***
		****************************

**** aedu_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): p3042 + p3042s1
* Source for this wave (2018–2021): p6210 + p6210s1
* p6210:   1=Ninguno/Preescolar, 2=Primaria (3), 3=Secundaria básica (4),
*           4=Media (5), 5=Superior completo, 6=Universitaria/postgrado
*          (Note: categories differ from p3042 — see dicc2018.pdf)
* p6210s1: último año/grado aprobado dentro del nivel
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****

replace p6210s1 = . if p6210s1 == 99
replace p6210   = . if p6210 == 9

g aedu_ci = .
replace aedu_ci = 0  if p6210 == 1 | p6210 == 2
replace aedu_ci = 0  if p6210 == 3 & p6210s1 == 0
replace aedu_ci = 1  if p6210 == 3 & p6210s1 == 1
replace aedu_ci = 2  if p6210 == 3 & p6210s1 == 2
replace aedu_ci = 3  if p6210 == 3 & p6210s1 == 3
replace aedu_ci = 4  if p6210 == 3 & p6210s1 == 4
replace aedu_ci = 5  if p6210 == 3 & p6210s1 == 5
replace aedu_ci = 5  if p6210 == 4 & p6210s1 == 0
replace aedu_ci = 6  if p6210 == 4 & p6210s1 == 6
replace aedu_ci = 7  if p6210 == 4 & p6210s1 == 7
replace aedu_ci = 8  if p6210 == 4 & p6210s1 == 8
replace aedu_ci = 9  if p6210 == 4 & p6210s1 == 9
replace aedu_ci = 10 if p6210 == 5 & p6210s1 == 10
replace aedu_ci = 11 if p6210 == 5 & p6210s1 == 11
replace aedu_ci = 11 if p6210 == 6 & p6210s1 == 0
replace aedu_ci = 12 if p6210 == 5 & p6210s1 == 12
replace aedu_ci = 13 if p6210 == 5 & p6210s1 == 13
replace aedu_ci = 11 + p6210s1 if p6210 == 6
replace aedu_ci = .  if p6210 == .


* ISCED attainment (0–8)
* Note: ISCED 4 (Normalista) and ISCED 5 (técnica/tecnológica) cannot be
* distinguished without p3042; all post-secondary mapped to ISCED 6 or higher.
gen byte edu_isced = .

* ISCED 0: less than primary / early childhood
replace edu_isced = 0 if aedu_ci == 0

* ISCED 1: primary (complete or incomplete)
replace edu_isced = 1 if aedu_ci >= 1 & aedu_ci < 9

* ISCED 2: lower secondary
replace edu_isced = 2 if aedu_ci >= 9 & aedu_ci < 11

* ISCED 3: upper secondary
replace edu_isced = 3 if aedu_ci == 11

* ISCED 5/6: tertiary (short-cycle and bachelor cannot be distinguished; mapped to 6)
replace edu_isced = 6 if p6210 == 6 & aedu_ci > 11

* ISCED 7/8: postgraduate
replace edu_isced = 7 if p6210 == 6 & aedu_ci >= 16

* Missing
replace edu_isced = . if p6210 == . & aedu_ci == .

label define edu_isced_lbl ///
  0 "ISCED 0 Early childhood / less than primary" ///
  1 "ISCED 1 Primary" ///
  2 "ISCED 2 Lower secondary" ///
  3 "ISCED 3 Upper secondary" ///
  4 "ISCED 4 Post-secondary non-tertiary" ///
  5 "ISCED 5 Short-cycle tertiary" ///
  6 "ISCED 6 Bachelor's or equivalent" ///
  7 "ISCED 7 Master's or equivalent" ///
  8 "ISCED 8 Doctoral or equivalent"
label values edu_isced edu_isced_lbl


**************
*** edu_hdmf ***
**************
* Note: Without p3042/p3043, técnica (cat 6) and universitaria (cat 7)
* cannot be fully distinguished. All tertiary treated as cat 6+ based on aedu_ci.
gen edu_hdmf = .

* 1. menos de primaria
replace edu_hdmf = 1 if aedu_ci == 0

* 2. primaria incompleta
replace edu_hdmf = 2 if aedu_ci >= 1 & aedu_ci < 5

* 3. primaria completa
replace edu_hdmf = 3 if aedu_ci == 5

* 4. media incompleta
replace edu_hdmf = 4 if aedu_ci >= 6 & aedu_ci < 11

* 5. media completa
replace edu_hdmf = 5 if aedu_ci == 11

* 6. técnica/post-secundaria (proxy: p6210==6 con menos de 16 años)
replace edu_hdmf = 6 if p6210 == 6 & aedu_ci > 11 & aedu_ci < 16

* 7. universitaria completa (proxy: 16+ años de educación)
replace edu_hdmf = 7 if p6210 == 6 & aedu_ci >= 16

* 8. posgrado (proxy: 18+ años de educación)
replace edu_hdmf = 8 if aedu_ci >= 18

replace edu_hdmf = . if p6210 == . & aedu_ci == .

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
* oficio: OLD CIUO-88/CNO coding (2018-2021 GEIH); approximate ISCO-08 mapping
/* WARNING: COL 2018-2021 uses non-ISCO occupation codes. Mapping is approximate.
   VERIFY variable name 'oficio' against raw data dictionary if missing count is high. */
***********
gen byte ocupa_ci = .
replace ocupa_ci = 2 if emp_ci == 1 & oficio >= 1  & oficio <= 19  /* Professionals/tech → ISCO 2 */
replace ocupa_ci = 1 if emp_ci == 1 & oficio >= 20 & oficio <= 21  /* Directors → ISCO 1 */
replace ocupa_ci = 4 if emp_ci == 1 & oficio >= 30 & oficio <= 39  /* Administrative → ISCO 4 */
replace ocupa_ci = 5 if emp_ci == 1 & oficio >= 40 & oficio <= 59  /* Commerce/Services → ISCO 5 */
replace ocupa_ci = 6 if emp_ci == 1 & oficio >= 60 & oficio <= 64  /* Agriculture → ISCO 6 */
replace ocupa_ci = 7 if emp_ci == 1 & oficio >= 65 & oficio <= 98  /* Craft/Production → ISCO 7/8 */
replace ocupa_ci = 9 if emp_ci == 1 & oficio >= 99               /* Elementary → ISCO 9 */
label define ocupa_lbl 1 "Managers" 2 "Professionals" 3 "Technicians" ///
    4 "Clerical" 5 "Service/Sales" 6 "Agriculture" ///
    7 "Craft" 8 "Plant/Machine" 9 "Elementary", replace
label values ocupa_ci ocupa_lbl
label var ocupa_ci "ISCO-08 major group (approx., old CIUO-88/CNO 2018-2021)"

***********
* overqualified_ci
* edu_hdmf >= 6: técnica or higher (8-level COL scale)
* NOTE: COL 2018-2021 occupation mapping is approximate; comparability limited
***********
gen byte overqualified_ci = .
replace overqualified_ci = 0 if emp_ci == 1 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = 1 if emp_ci == 1 & edu_hdmf >= 6 & ocupa_ci >= 4 & !missing(edu_hdmf) & !missing(ocupa_ci)
replace overqualified_ci = . if emp_ci != 1
label define overq_lbl 1 "Overqualified" 0 "Not overqualified", replace
label values overqualified_ci overq_lbl
label var overqualified_ci "Overqualified (approx., old CIUO-88/CNO coding 2018-2021)"


*************
* remesas_ci *
*************
generate double remesas_ci = p7510s2a1/12 if p7510s2a1>9999 & p7510s2a1!=.

*************
* remesas_ch *
*************
by idh_ch, sort: egen double remesas_ch = sum(remesas_ci) if miembros_ci == 1


		******************************
		*** VARIABLES DE MIGRACION ***
		******************************

**** migrante_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): gen migrante_ci = (p3373 == 3)
* Source for this wave (2018–2021): p6074==2 (born in another country)
*   AND p756==3 (habitual residence abroad) — p3373 not in dataset
* Note: 2018–2021 definition is stricter (requires both birthplace AND residence
*   outside Colombia). Migrant share will be slightly lower than 2022+.
* Reference: COL_2018t3_variablesBID.do, SCL/MIG Fernando Morales
**** END ALTERNATIVE ****
gen migrante_ci = (p6074 == 2 & p756 == 3) if p6074 != . & p756 != .
label var migrante_ci "=1 si es migrante"

**** migrantiguo5_ci — ALTERNATIVE CONSTRUCTION ****
* Standard source (2022+): inlist(p3382, 2, 3)
* Source for this wave (2018–2021): inlist(p755, 2, 3)
* Reference: COL_2018t3_variablesBID.do (alternative_do_files)
**** END ALTERNATIVE ****
gen migrantiguo5_ci = (migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1
replace migrantiguo5_ci = 0 if p755 == 4 & migrante_ci==1 & p755!=1
replace migrantiguo5_ci = . if migrante_ci==0
label var migrantiguo5_ci "=1 si es migrante antiguo (5 anos o mas)"

**** miglac_ci — ALTERNATIVE CONSTRUCTION (p756s3) ****
* Standard source (2022+): inlist(p3373s3, [LAC codes])
* Source for this wave (2018-2021): p756s3 LAC categories
*   LAC: Venezuela(3), Ecuador(4), Panama(5), Peru(6), Costa Rica(7), Argentina(8)
*   Non-LAC: Estados Unidos(1), Espana(2), Francia(9), Italia(10)
*   Unknown: Otro pais(11) -> coded as missing
* Reference: bases armo/raw/col/dicc2018 migration module.pdf
**** END ALTERNATIVE ****
gen miglac_ci = (migrante_ci==1 & inlist(p756s3, 3, 4, 5, 6, 7, 8)) if migrante_ci!=.
replace miglac_ci = . if migrante_ci==0
label var miglac_ci "=1 si migrante de LAC (p756s3, 2018-2021)"

**** mig_pais_ci — ALTERNATIVE CONSTRUCTION (p756s3) ****
* Standard source (2022+): merge on p3373s3 via mig_pais_code.dta
* Source for this wave (2018-2021): p756s3 (11 country categories from migration module)
* Reference: bases armo/raw/col/dicc2018 migration module.pdf
**** END ALTERNATIVE ****
gen str mig_pais_ci = ""
replace mig_pais_ci = "Estados Unidos" if p756s3 == 1  & migrante_ci == 1
replace mig_pais_ci = "Espana"         if p756s3 == 2  & migrante_ci == 1
replace mig_pais_ci = "Venezuela"      if p756s3 == 3  & migrante_ci == 1
replace mig_pais_ci = "Ecuador"        if p756s3 == 4  & migrante_ci == 1
replace mig_pais_ci = "Panama"         if p756s3 == 5  & migrante_ci == 1
replace mig_pais_ci = "Peru"           if p756s3 == 6  & migrante_ci == 1
replace mig_pais_ci = "Costa Rica"     if p756s3 == 7  & migrante_ci == 1
replace mig_pais_ci = "Argentina"      if p756s3 == 8  & migrante_ci == 1
replace mig_pais_ci = "Francia"        if p756s3 == 9  & migrante_ci == 1
replace mig_pais_ci = "Italia"         if p756s3 == 10 & migrante_ci == 1
* p756s3==11 (Otro pais) -> left as empty string (unknown origin)
label var mig_pais_ci "Pais de origen del migrante (p756s3, 2018-2021)"

**** profesion_ci / cinef13_ci / profesion3_ci — NOT AVAILABLE ****
* p3042s2 (field of study code) absent in 2018–2021
gen profesion_ci  = .
gen byte cinef13_ci   = .
gen byte profesion3_ci = .
label var profesion_ci   "Área/campo de educación (NOT AVAILABLE para 2018–2021)"
label var cinef13_ci     "ISCED-F 2 dígitos (NOT AVAILABLE para 2018–2021)"
label var profesion3_ci  "ISCED-F 3 dígitos (NOT AVAILABLE para 2018–2021)"


drop if secuencia_p == .

compress
saveold "`base_out'", replace
