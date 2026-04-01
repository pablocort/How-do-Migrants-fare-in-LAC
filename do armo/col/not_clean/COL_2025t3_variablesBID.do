	*(Versión stata 17)

**# Bookmark #1
clear
set more off

*________________________________________________________________________________________________________________*

 
*global surveysFolder "\\sapidbshares.file.core.windows.net\idbshares\SURVEYS"
*display "$surveysFolder"


local PAIS COL
local ENCUESTA GEIH
local ANO "2025"
local ronda t3 
local log_file = "$ruta\harmonized\\`PAIS'\\`ENCUESTA'\log\\`PAIS'_`ANO'`ronda'_variablesBID.log"
local base_in  = "$ruta\survey\\`PAIS'\\`ENCUESTA'\\`ANO'\\`ronda'\data_merge\\`PAIS'_`ANO'`ronda'.dta"
local base_out = "$ruta\harmonized\\`PAIS'\\`ENCUESTA'\data_arm\\`PAIS'_`ANO'`ronda'_BID.dta"
                        
capture log close
cap log using "`log_file'", replace 

cap log off

/***************************************************************************
                 BASES DE DATOS DE ENCUESTA DE HOGARES
*************************************************************************** */

if c(username)=="PABLOCOR" {

use "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\col\COL_2025t3.dta", clear
local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'_`ANO'`ronda'_BID.dta"
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

***************
***factor_ci***
***************
g factor_ci=fex_c18

***************
***factor_ch***
***************
g factor_ch=fex_c18




*************
*condocup_ci*
*************
gen byte condocup_ci = .
replace condocup_ci=1 if oci==1
replace condocup_ci=2 if dsi==1
replace condocup_ci=3 if fft==1
replace condocup_ci=. if !inrange(edad_ci, 15,64)
label define condocup_ci 1 "Ocupado" 2 "Desocupado" 3 "Inactivo" 
label value condocup_ci condocup_ci

*******************
***categoinac_ci***
*******************
gen byte categoinac_ci = .
replace categoinac_ci=1 if p7450==5 & condocup_ci==3
replace categoinac_ci=2 if p7450==2 | (p6240==3 & condocup_ci==3)
replace categoinac_ci=3 if p7450==3 | (p6240==4 & condocup_ci==3)
replace categoinac_ci=4 if ((categoinac_ci != 1 | categoinac_ci != 2 | categoinac_ci != 3) & condocup_ci == 3)
	
**********
***emp_ci*
**********
gen byte emp_ci = .
replace emp_ci = (condocup_ci == 1) if condocup_ci != .


***************
***desemp_ci***
***************	
gen byte desemp_ci = .
replace desemp_ci = (condocup_ci == 2) if condocup_ci! = .

***************
***horaspri_ci***
***************	
gen  byte horaspri_ci = p6800
replace horaspri_ci = . if emp_ci == 0 
	
***************
***horastot_ci ***
***************	
egen horastot_ci  = rowtotal(p6800 p7045)
replace horastot_ci = . if p6800 == . & p7045 == . 
replace horastot_ci  = . if emp_ci == 0


***********
***pea_ci***
***********
gen byte pea_ci = .
replace pea_ci = 1 if inlist(condocup_ci,1,2)
replace pea_ci = 0 if inlist(condocup_ci,3,4)
		
******************
***cotizando_ci***
******************	
gen  byte cotizando_ci = .
replace cotizando_ci=1 if p6920==1
replace cotizando_ci=0 if p6920==2 | (condocup_ci==2 & p6920!=1)
		
*****************
***afiliado_ci***
*****************
gen  byte afiliado_ci = (p6090==1)
replace afiliado_ci=. if p6090==9
	

**************
***formal_ci***
**************
gen byte formal_ci = .
replace formal_ci  =  1 if (cotizando_ci == 1 | afiliado_ci == 1) & condocup_ci == 1
replace formal_ci = 0 if (cotizando_ci == 0 & afiliado_ci == 0) & (condocup_ci == 1 )
	
*********************
***tipocontrato_ci***
*********************
gen byte tipocontrato_ci = .
replace tipocontrato_ci=1 if p6460==1 & condocup_ci==1
replace tipocontrato_ci=2 if p6460==2 & condocup_ci==1
replace tipocontrato_ci=3 if p6450==1 & condocup_ci==1
replace tipocontrato_ci=3 if p6440==2 & condocup_ci==1
				
		
		
	****************************
**#***VARIABLES DE INGRESO***
	****************************
/*
*************
* ylmpri_ci *
*************
egen ylmpri_ci = rsum(impa impaes) if emp_ci==1, m
replace ylmpri_ci = . if impa==. & impaes==. 

************
* ylmsec_ci *
************
egen ylmsec_ci = rsum(isa isaes) if emp_ci==1, m
replace ylmsec_ci=. if isa==. & isaes==.

**************
* ylmotros_ci *
**************
egen ylmotros_ci= rsum(imdi imdies), m
* REVISAR PORQUE SI LO LIMITO A emp_ci==1 SE GENERA TODO COMO MISSING
 
*********
* ylm_ci *
*********
egen double ylm_ci = rowtotal(ylmpri_ci ylmsec_ci ylmotros_ci), mi

**************
* ylnmpri_ci *
**************
egen ylnmpri_ci = rsum(ie iees) if emp_ci==1, m
replace ylnmpri_ci=. if ie==. & iees==.
replace ylnmpri_ci = . if ylnmpri_ci < 0 & ylnmpri_ci != .

**************
* ylnmsec_ci *
**************
*egen double ylnmsec_ci = rowtotal(...) if emp_ci==1, mi
*replace ylnmsec_ci = . if ylnmsec_ci < 0 & ylnmsec_ci != .
g ylnmsec_ci = . /*No se pregunta ingreso por especies para act secundaria */

****************
* ylnmotros_ci *
****************
*egen double ylnmotros_ci = rowtotal(...) if emp_ci==1, mi
*replace ylnmotros_ci = . if ylnmotros_ci < 0 & ylnmotros_ci != .
g ylnmotros_ci = .

**********
* ylnm_ci *
**********
egen double ylnm_ci = rowtotal(ylnmpri_ci ylnmsec_ci ylnmotros_ci), mi
replace ylnm_ci = . if ylnm_ci < 0 & ylnm_ci != .

**********
* ynlm_ci *
**********
egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m
replace ynlm_ci = 0 if ynlm_ci < 0 & ynlm_ci != .

***********
* ynlnm_ci *
***********
*egen double ynlnm_ci = rowtotal(...), mi
*replace ynlnm_ci = . if ynlnm_ci < 0 & ynlnm_ci != .
g ynlnm_ci = .

**********
* ytot_ci *
**********
egen double ytot_ci = rowtotal(ylm_ci ylnm_ci ynlm_ci ynlnm_ci), mi

*/


		****************************
**# ***VARIABLES DE EDUCACION***
		****************************
			
**************
***aedu_ci***
**************	
// CORREGIDA: Educación superior estaba mal codificada 
// menos de 150 personas de 200.000 tenían grado o más 

/*
1	Ninguno
2	Preescolar 
3	Básica primaria (1o - 5o)
4	Básica secundaria (6o - 9o)
5	Media académica (Bachillerato clásico)
6	Media técnica (Bachillerato técnico)
7	Normalista
8	Técnica profesional
9	Tecnológica 
10	Universitaria
11	Especialización 
12	Maestría 
13	Doctorado 
99	No sabe, no informa
*/

g aedu_ci = . 
* 0 años de educacion 
replace aedu_ci = 0 if p3042 == 1 | p3042 == 2  

* en años
// Primaria
replace aedu_ci = p3042s1 if p3042==3 
// Secundaria 
replace aedu_ci = p3042s1 if inlist(p3042,4, 5, 6) 
replace aedu_ci = 11 + p3042s1 if inlist(p3042,7, 8, 9, 10, 11, 12, 13)
replace aedu_ci = . if  p3042 == .




* ISCED attainment (0–8)
gen byte edu_isced = .

* ISCED 0: less than primary / early childhood
replace edu_isced = 0 if aedu_ci == 0

* ISCED 1: primary
replace edu_isced = 1 if aedu_ci >= 5 & aedu_ci < 9

* ISCED 2: lower secondary
replace edu_isced = 2 if  aedu_ci >= 9 & aedu_ci < 11

* ISCED 3: upper secondary
replace edu_isced = 3 if aedu_ci == 11 

* ISCED 4: post-secondary non-tertiary (Normalista)
replace edu_isced = 4 if p3042 == 7

* ISCED 5: short-cycle tertiary (técnica profesional, tecnológica)
replace edu_isced = 5 if inlist(p3042, 8, 9)

* ISCED 6: bachelor or equivalent (universitaria)
replace edu_isced = 6 if p3042 == 10

* ISCED 7: master or equivalent (especialización, maestría)
replace edu_isced = 7 if inlist(p3042, 11, 12)

* ISCED 8: doctoral
replace edu_isced = 8 if p3042 == 13

* Missing / don't know
replace edu_isced = . if inlist(p3042, ., 99)

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

gen edu_hdmf = .

* 1. menos de primaria
replace edu_hdmf = 1 if inlist(p3042,1,2)
replace edu_hdmf = 1 if p3042==3 & p3042s1==0

* 2. primaria incompleta
replace edu_hdmf = 2 if p3042==3 & inrange(p3042s1,1,4)

* 3. primaria completa
replace edu_hdmf = 3 if p3042==3 & p3042s1==5

* 4. básica secundaria incompleta
replace edu_hdmf = 4 if p3042==4 & inrange(p3042s1,0,8)

* 5. básica secundaria (6°–9°)
replace edu_hdmf = 5 if p3042== 4 & (p3042s1 == 9 )

* 6. media completa (11°)
replace edu_hdmf = 6 if inlist(p3042,5,6) & p3042s1==11
replace edu_hdmf = 6 if p3042==7   // normalista

* 7. técnica completa (terciaria no universitaria)
replace edu_hdmf = 7 if inlist(p3042,8,9) & p3042s1>=2

* 8. universitaria incompleta
replace edu_hdmf = 8 if p3042==10 & p3042s1<5

* 9. universitaria completa
replace edu_hdmf = 9 if p3042==10 & p3042s1>=5

* 10. posgrado
replace edu_hdmf = 10 if inlist(p3042,11,12,13)

* missing
replace edu_hdmf = . if p3042==99

label define edu_hdmf ///
1 "menos de primaria" ///
2 "primaria incompleta" ///
3 "primaria completa" ///
4 "básica secundaria incompleta" ///
5 "básica secundaria" ///
6 "media completa" ///
7 "técnica" ///
8 "universitaria incompleta" ///
9 "universitaria completa" ///
10 "posgrado"

label values edu_hdmf edu_hdmf
label var edu_hdmf "nivel educativo agregado hdmf"
ta edu_hdmf
*------------------------------------------------------------
* refinar edu_hdmf usando p3043 (titulo/diploma recibido)
* regla: p3043 solo "sube" el nivel (no lo baja)
*------------------------------------------------------------

* posgrado: si reporta especializacion/maestria/doctorado
replace edu_hdmf = 10 if inlist(p3043,8,9,10) & p3043!=99

* universitaria completa: si reporta titulo universitario
replace edu_hdmf = 9 if p3043==7 & p3043!=99 & (edu_hdmf<9 | edu_hdmf==.)

* tecnica completa: si reporta tecnico profesional o tecnologico
replace edu_hdmf = 7 if inlist(p3043,5,6) & p3043!=99 & (edu_hdmf<7 | edu_hdmf==.)

* media completa: si reporta diploma de media (academica/tecnica) o normalista
replace edu_hdmf = 6 if inlist(p3043,2,3,4) & p3043!=99 & (edu_hdmf<6 | edu_hdmf==.)

* si no sabe/no informa en p3043, no hacemos nada (se queda como venia)
* si p3043==1 (ninguno), tampoco bajamos: puede tener estudios sin diploma





*************
* remesas_ci *
*************
generate double remesas_ci = p7510s2a1/12 if p7510s2a1>9999 & p7510s2a1!=.

*************
* remesas_ch *
*************
by idh_ch, sort: egen byte remesas_ch = sum(remesas_ci) if miembros_ci == 1


		******************************
		*** VARIABLES DE MIGRACION ***
		******************************
 
*******************
*** migrante_ci ***
*******************	
gen migrante_ci= (p3373==3)
	
**********************
*** migrantiguo5_ci ***
**********************
gen migrantiguo5_ci=(migrante_ci==1 & inlist(p3382,2,3)) if migrante_ci!=. & p3382!=1
replace migrantiguo5_ci = 0 if p3382 == 4 & migrante_ci==1 & migrante_ci!=. & p3382!=1
replace migrantiguo5_ci = . if migrante_ci==0
	
**********************
*** miglac_ci ***
**********************
destring p3373s3, replace

gen miglac_ci=(migrante_ci==1 & inlist(p3373s3, ///
32,   /* Argentina */ ///
68,   /* Bolivia */ ///
76,   /* Brasil */ ///
152,  /* Chile */ ///
170,  /* Colombia */ ///
188,  /* Costa Rica */ ///
192,  /* Cuba */ ///
214,  /* República Dominicana */ ///
218,  /* Ecuador */ ///
222,  /* El Salvador */ ///
320,  /* Guatemala */ ///
332,  /* Haití */ ///
340,  /* Honduras */ ///
484,  /* México */ ///
558,  /* Nicaragua */ ///
591,  /* Panamá */ ///
600,  /* Paraguay */ ///
604,  /* Perú */ ///
630,  /* Puerto Rico */ ///
858,  /* Uruguay */ ///
862,  /* Venezuela */ ///
44,   /* Bahamas */ ///
52,   /* Barbados */ ///
84,   /* Belice */ ///
28,   /* Antigua y Barbuda */ ///
212,  /* Dominica */ ///
308,  /* Granada */ ///
388,  /* Jamaica */ ///
659,  /* Saint Kitts y Nevis */ ///
662,  /* Santa Lucía */ ///
670,  /* San Vicente y las Granadinas */ ///
780,  /* Trinidad y Tabago */ ///
328,  /* Guyana */ ///
740,  /* Suriname */ ///
533,  /* Aruba */ ///
531   /* Curazao */ ///
)) if migrante_ci!=. 


	
**********************
*** mig_pais_code ***
**********************
*pais de migrante (código)
gen mig_pais_code = .
replace mig_pais_code = p3373s3 if migrante_ci==1 & migrante_ci!=.
 
 
**********************
*** mig_pais_ci ***
**********************
destring p3373s3, replace
 
merge m:1 p3373s3 using "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\col\mig_pais_code.dta"
 
gen mig_pais_ci = ""
replace mig_pais_ci = pais if migrante_ci==1 & migrante_ci!=.



*------------------------------------------------------------
* Value label para P3042S2 (códigos numéricos)
*------------------------------------------------------------
gen profesion_ci=p3042s2
label define lbl_p3042s2 ///
11   "Programas y certificaciones básicos" ///
21   "Alfabetización y Aritmética Elemental" ///
31   "Competencias personales y desarrollo" ///
111  "Ciencias de la educación" ///
112  "Formación para docentes de educación preprimaria" ///
113  "Formación para docentes sin asignatura de especialización" ///
114  "Formación para docentes con asignatura de especialización" ///
119  "Educación no clasificada en otra parte" ///
188  "Programas y certificaciones interdisciplinarios relativos a educación" ///
211  "Técnicas Audiovisuales y Producción para Medios de Comunicación" ///
212  "Diseño Industrial, de Moda e Interiores" ///
213  "Bellas Artes" ///
214  "Artesanías" ///
215  "Música y Artes Escénicas" ///
219  "Artes no clasificados en otra parte" ///
221  "Religión y Teología" ///
222  "Historia y Arqueología" ///
223  "Filosofía y Ética" ///
229  "Humanidades (excepto idiomas) no clasificados en otra parte" ///
231  "Adquisición del lenguaje" ///
232  "Literatura y Lingüística" ///
239  "Idiomas no clasificados en otra parte" ///
288  "Programas y certificaciones interdisciplinarios relativos a Artes y Humanidades" ///
311  "Economía" ///
312  "Ciencias Políticas y Educación Cívica" ///
313  "Psicología" ///
314  "Sociología, antropología y estudios culturales" ///
315  "Trabajo Social" ///
319  "Ciencias Sociales y del Comportamiento no clasificados en otra parte" ///
321  "Periodismo y Reportajes" ///
322  "Bibliotecología, Información y Archivística" ///
329  "Periodismo e Información no clasificados en otra parte" ///
388  "Programas y certificaciones interdisciplinarios relativos a Ciencias Sociales, Periodismo e Información" ///
411  "Contabilidad e Impuestos" ///
412  "Gestión Financiera, Administración Bancaria y Seguros" ///
413  "Gestión y administración" ///
414  "Mercadeo y Publicidad" ///
415  "Secretariado y trabajo de oficina" ///
416  "Ventas al por mayor y al por menor" ///
417  "Competencias laborales" ///
419  "Educación Comercial y Administración no clasificados en otra parte" ///
421  "Derecho" ///
488  "Programas y certificaciones interdisciplinarios relativos a Administración de Empresas y Derecho" ///
511  "Biología" ///
512  "Bioquímica" ///
519  "Ciencias Biológicas y afines no clasificados en otra parte" ///
521  "Ciencias del Medio Ambiente" ///
522  "Medio Ambiente Natural y Vida Silvestre" ///
529  "Medio Ambiente no clasificados en otra parte" ///
531  "Química" ///
532  "Ciencias de la Tierra" ///
533  "Física" ///
539  "Ciencias Físicas no clasificadas en otra parte" ///
541  "Matemáticas" ///
542  "Estadística" ///
588  "Programas y certificaciones interdisciplinarios relativos a Ciencias Naturales, Matemáticas y Estadística" ///
611  "Uso de computadores" ///
612  "Diseño y Administración de Redes y Bases de datos" ///
613  "Desarrollo y Análisis de software y Aplicaciones" ///
619  "TIC no clasificados en otra parte" ///
688  "Programas y certificaciones interdisciplinarios relativos a TIC" ///
711  "Ingeniería y Procesos Químicos" ///
712  "Tecnología de protección del medio ambiente" ///
713  "Electricidad y Energía" ///
714  "Electrónica y Automatización" ///
715  "Mecánica y profesiones afines a la Metalistería" ///
716  "Vehículos, Barcos y Aeronaves de motor" ///
719  "Ingeniería y profesiones afines no clasificadas en otra parte" ///
721  "Procesamiento de alimentos" ///
722  "Industria y Procesamiento de Materiales (vidrio, papel, plástico y madera)" ///
723  "Productos textiles (prendas de vestir, calzado y artículos de marroquinería)" ///
724  "Minería y Extracción" ///
729  "Industria y Procesamiento no clasificados en otra parte" ///
731  "Arquitectura y Urbanismo" ///
732  "Construcción e Ingeniería Civil" ///
788  "Programas y certificaciones interdisciplinarios relativos a Ingeniería, Industria y Construcción" ///
811  "Producción Agrícola y Ganadera" ///
812  "Horticultura (técnicas de huertas, invernaderos, viveros y jardines)" ///
819  "Agropecuario no clasificado en otra parte" ///
821  "Silvicultura" ///
831  "Pesca y Acuicultura" ///
841  "Veterinaria" ///
888  "Programas y certificaciones interdisciplinarios relativos a Agropecuario, Silvicultura, Pesca y Veterinaria" ///
911  "Odontología y estudios dentales" ///
912  "Medicina" ///
913  "Enfermería" ///
914  "Tecnología de diagnóstico y tratamiento médico" ///
915  "Fisioterapia, fonoaudiología, nutrición y dietética, optometría, terapia ocupacional y terapia respiratoria" ///
916  "Farmacia" ///
917  "Medicina y terapia alternativa y complementaria, y partería tradicional" ///
918  "Instrumentación quirúrgica" ///
919  "Salud no clasificada en otra parte" ///
921  "Asistencia a adultos, adultos mayores con o sin discapacidad" ///
922  "Asistencia, protección y servicios a la infancia, adolescencia y juventud" ///
929  "Bienestar no clasificado en otra parte" ///
988  "Programas y certificaciones interdisciplinarios relativos a Salud y Bienestar" ///
1011 "Servicios domésticos" ///
1012 "Peluquería y tratamientos de belleza" ///
1013 "Hotelería, restaurantes y servicios de banquetes" ///
1014 "Deportes" ///
1015 "Viajes, turismo y actividades recreativas" ///
1016 "Servicios de tanatopraxia" ///
1019 "Servicios personales no clasificados en otra parte" ///
1021 "Saneamiento de la comunidad" ///
1022 "Salud y protección laboral" ///
1029 "Servicios de Higiene y Salud Ocupacional no clasificados en otra parte" ///
1031 "Educación militar y de defensa" ///
1032 "Protección de las personas y de la propiedad" ///
1039 "Servicios de Seguridad no clasificados en otra parte" ///
1041 "Servicios de transporte" ///
1088 "Programas y certificaciones interdisciplinarios relativos a Servicios", replace

* Asignar el label a la variable
label values profesion_ci lbl_p3042s2
label var profesion_ci "Área/campo de educación (ISCED-F 2013, 4 dígitos sin ceros)"

** A dos digitos
gen byte cinef13_ci = .
replace cinef13_ci = 10 if inrange(p3042s2,1000,1099)
replace cinef13_ci = 9  if inrange(p3042s2, 900, 999)
replace cinef13_ci = 8  if inrange(p3042s2, 800, 899)
replace cinef13_ci = 7  if inrange(p3042s2, 700, 799)
replace cinef13_ci = 6  if inrange(p3042s2, 600, 699)
replace cinef13_ci = 5  if inrange(p3042s2, 500, 599)
replace cinef13_ci = 4  if inrange(p3042s2, 400, 499)
replace cinef13_ci = 3  if inrange(p3042s2, 300, 399)
replace cinef13_ci = 2  if inrange(p3042s2, 200, 299)
replace cinef13_ci = 1  if inrange(p3042s2, 100, 199)
replace cinef13_ci = 0  if inrange(p3042s2,   0,  99)
label values cinef13_ci lbl_cinef13_ci

label define lbl_cinef13_ci ///
0  "Programas y certificaciones genéricos" ///
1  "Educación" ///
2  "Artes y Humanidades" ///
3  "Ciencias Sociales, Periodismo e Información" ///
4  "Administración de Empresas y Derecho" ///
5  "Ciencias Naturales, Matemáticas y Estadística" ///
6  "Tecnología de la Información y la Comunicación (TIC)" ///
7  "Ingeniería, Industria y Construcción" ///
8  "Agropecuario, Silvicultura, Pesca y Veterinaria" ///
9  "Salud y bienestar" ///
10 "Servicios", replace

label values cinef13_ci lbl_cinef13_ci

*** A tres digitos 

*====================================================*
* ISCED-F agregado (3 dígitos) con códigos consecutivos
*====================================================*

capture drop profesion3_ci
gen byte profesion3_ci = .

* 1-3: Programas básicos
replace profesion3_ci = 1 if profesion_ci == 11
replace profesion3_ci = 2 if profesion_ci == 21
replace profesion3_ci = 3 if profesion_ci == 31

* 4: 011 Educación
replace profesion3_ci = 4 if inrange(profesion_ci, 111, 199)

* 5-7: Artes y Humanidades
replace profesion3_ci = 5 if inrange(profesion_ci, 211, 219)   // 021 Artes
replace profesion3_ci = 6 if inrange(profesion_ci, 221, 229)   // 022 Humanidades
replace profesion3_ci = 7 if inrange(profesion_ci, 231, 239)   // 023 Idiomas
replace profesion3_ci = 5 if profesion_ci == 288               // interdisciplinario -> Artes

* 8-9: Sociales, periodismo
replace profesion3_ci = 8 if inrange(profesion_ci, 311, 319)   // 031 Sociales y comportamiento
replace profesion3_ci = 9 if inrange(profesion_ci, 321, 329)   // 032 Periodismo e información
replace profesion3_ci = 8 if profesion_ci == 388               // interdisciplinario -> Sociales

* 10-11: Admin y derecho
replace profesion3_ci = 10 if inrange(profesion_ci, 411, 419)  // 041 Educación comercial y administración
replace profesion3_ci = 11 if profesion_ci == 421              // 042 Derecho
replace profesion3_ci = 10 if profesion_ci == 488              // interdisciplinario -> Admin

* 12-15: Naturales, matemáticas, estadística
replace profesion3_ci = 12 if inrange(profesion_ci, 511, 519)  // 051 Biológicas
replace profesion3_ci = 13 if inrange(profesion_ci, 521, 529)  // 052 Medio ambiente
replace profesion3_ci = 14 if inrange(profesion_ci, 531, 539)  // 053 Físicas
replace profesion3_ci = 15 if inrange(profesion_ci, 541, 542)  // 054 Matemáticas y estadística
replace profesion3_ci = 12 if profesion_ci == 588              // interdisciplinario -> Biológicas

* 16: TIC
replace profesion3_ci = 16 if inrange(profesion_ci, 611, 619) | profesion_ci == 688

* 17-19: Ingeniería, industria, construcción
replace profesion3_ci = 17 if inrange(profesion_ci, 711, 719) | profesion_ci == 788   // 071
replace profesion3_ci = 18 if inrange(profesion_ci, 721, 729)                           // 072
replace profesion3_ci = 19 if inrange(profesion_ci, 731, 732)                           // 073

* 20-23: Agro, silvicultura, pesca, veterinaria
replace profesion3_ci = 20 if inrange(profesion_ci, 811, 819) | profesion_ci == 888    // 081
replace profesion3_ci = 21 if profesion_ci == 821                                        // 082
replace profesion3_ci = 22 if profesion_ci == 831                                        // 083
replace profesion3_ci = 23 if profesion_ci == 841                                        // 084

* 24-25: Salud y bienestar
replace profesion3_ci = 24 if inrange(profesion_ci, 911, 919) | profesion_ci == 988     // 091
replace profesion3_ci = 25 if inrange(profesion_ci, 921, 929)                            // 092

* 26-29: Servicios
replace profesion3_ci = 26 if inrange(profesion_ci, 1011, 1019) | profesion_ci == 1088  // 101
replace profesion3_ci = 27 if inrange(profesion_ci, 1021, 1029)                          // 102
replace profesion3_ci = 28 if inrange(profesion_ci, 1031, 1039)                          // 103
replace profesion3_ci = 29 if profesion_ci == 1041                                       // 104

*----------------------------------------------------*
* Labels (incluyendo el código 3 dígitos en el texto)
*----------------------------------------------------*
capture label drop lbl_profesion3_ci
label define lbl_profesion3_ci ///
    1  "Programas y certificaciones básicas" ///
    2  "Alfabetización y Aritmética Elemental" ///
    3  "Competencias personales y desarrollo" ///
    4  "Educación" ///
    5  "Artes" ///
    6  "Humanidades (excepto idiomas)" ///
    7  "Idiomas" ///
    8  "Ciencias Sociales y del Comportamiento" ///
    9  "Periodismo e Información" ///
    10 "Educación Comercial y Administración" ///
    11 "Derecho" ///
    12 "Ciencias Biológicas y afines" ///
    13 "Medio Ambiente" ///
    14 "Ciencias Físicas" ///
    15 "Matemáticas y Estadística" ///
    16 "Tecnologías de la Información y la Comunicación (TIC)" ///
    17 "Ingeniería y Profesiones afines" ///
    18 "Industria y Procesamiento" ///
    19 "Arquitectura y Construcción" ///
    20 "Agropecuario" ///
    21 "Silvicultura" ///
    22 "Pesca y acuicultura" ///
    23 "Veterinaria" ///
    24 "Salud" ///
    25 "Bienestar" ///
    26 "Servicios personales" ///
    27 "Servicios de Higiene y Salud Ocupacional" ///
    28 "Servicios de seguridad" ///
    29 "Servicios de transporte", replace

label values profesion3_ci lbl_profesion3_ci
label var profesion3_ci "Área/campo de educación (ISCED-F 2013, agregado 3 dígitos, consecutivo)"
/*
001 Programas y certificaciones básicas
002 Alfabetización y Aritmética Elemental
003 Competencias personales y desarrollo
011 Educación
021 Artes
022 Humanidades (excepto idiomas)
023 Idiomas
031 Ciencias Sociales y del Comportamiento
032 Periodismo e Información
041 Educación Comercial y Administración
042 Derecho
051 Ciencias Biológicas y afines
052 Medio Ambiente
053 Ciencias Físicas
054 Matemáticas y Estadística
061 Tecnologías de la Información y la Comunicación (TIC) 
071 Ingeniería y Profesiones afines
072 Industria y Procesamiento
073 Arquitectura y Construcción
081 Agropecuario 
082 Silvicultura
083 Pesca y acuicultura
084 Veterinaria
091 Salud
092 Bienestar
101 Servicios personales
102 Servicios de Higiene y Salud Ocupacional
103 Servicios de seguridad 
104 Servicios de transporte
*/


drop if secuencia_p == .

if c(username)=="PABLOCOR" {

local PAIS COL
local ENCUESTA GEIH
local ANO "2025"
local ronda t3 


local base_out = "C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\\`PAIS'_`ANO'`ronda'_BID.dta"
}

compress
saveold "`base_out'", replace



