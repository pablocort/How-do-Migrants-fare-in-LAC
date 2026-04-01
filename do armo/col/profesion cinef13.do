use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\COL_2024t3_BID.dta", clear


tab p3042s2

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

*save "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\COL_2024t3_BID.dta", replace


**# Bookmark #1

*use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\COL_2024t3_BID.dta", clear 

gen cinef13=cinef13_ci

label define cinef13 ///
    0  "Programas genéricos" ///
    1  "Educación" ///
    2  "Artes y Humanidades" ///
    3  "Ciencias Sociales, Periodismo" ///
    4  "Adm. de Empresas y Derecho" ///
    5  "Cs. Naturales, Matemáticas, Est." ///
    6  "TIC" ///
    7  "Ing., Industria y Construcción" ///
    8  "Agro, Silvicultura, Pesca, Vet." ///
    9  "Salud y bienestar" ///
    10 "Servicios", replace

label values cinef13 cinef13


graph bar (percent) [pweight=factor_ci] if mig_pais_ci=="Venezuela", ///
    over(cinef13, sort(1) descending label(labsize(small))) ///
    ytitle("Porcentaje") ///
    blabel(bar, format(%4.1f) position(outside)) ///
    bargap(10) ///
    horizontal title("COLOMBIA")
	
	
	
graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\profesiones_col.png", replace 	

tab2xl cinef13_ci [iw=factor_ci] if mig_pais_ci=="Venezuela" using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(COL, replace)


* Variable agrupada de nivel educativo (Colombia) - preescolar con primaria
capture drop nivel_edu
gen byte nivel_edu = .

replace nivel_edu = 0 if p3042 == 1
replace nivel_edu = 1 if inlist(p3042, 2, 3)
replace nivel_edu = 2 if p3042 == 4
replace nivel_edu = 3 if inlist(p3042, 5, 6, 7)
replace nivel_edu = 4 if inlist(p3042, 8, 9, 10, 11, 12, 13)

* No sabe / no informa
replace nivel_edu = . if p3042 == 99

label define nivel_edu_lbl ///
    0 "Ninguno" ///
    1 "Primaria" ///
    2 "Secundaria" ///
    3 "Media" ///
    4 "Superior", replace

label values nivel_edu nivel_edu_lbl
label var nivel_edu "Nivel educativo"


graph bar (percent) [pweight=factor_ci] if mig_pais_ci=="Venezuela", ///
    over(nivel_edu, label(labsize(small))) ///
    ytitle("Porcentaje") ///
    blabel(bar, format(%4.1f) position(outside)) ///
    bargap(10) ///
    bar(1, color(cranberry%70)) ///
	title("COLOMBIA")
	
graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\niveledu_col.png", replace 	
	

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


tab2xl profesion3_ci [iw=factor_ci] if mig_pais_ci=="Venezuela" using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(COL2, replace)
