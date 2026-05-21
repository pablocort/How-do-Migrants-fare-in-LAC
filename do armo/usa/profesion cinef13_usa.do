clear all
*cd "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\IPUMS"
*do usa_00004.do


use "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\usa\usa_00008.dta", clear
* Sample restrictions
keep if bpl==300              // SOUTH AMERICA
keep if bpld==30065           // Venezuela
*keep if sample==202303        // 2019–2023, ACS 5-year

* Citizenship
gen byte not_citizen = (citizen==3)
replace not_citizen = . if missing(citizen)

tab degfield [iw=perwt] if degfield!=0 // Field of degree , ALL

*==============================================================================
* 1. profesion3_ci: campo de educación a 3 dígitos ISCED-F (consecutivo 1–29)
*==============================================================================

gen profesion3_ci = .

replace profesion3_ci = 20 if degfield == 11  // Agriculture → Agropecuario
replace profesion3_ci = 13 if degfield == 13  // Environment and Natural Resources → Medio Ambiente
replace profesion3_ci = 19 if degfield == 14  // Architecture → Arquitectura y Construcción
replace profesion3_ci = 6  if degfield == 15  // Area, Ethnic, and Civilization Studies → Humanidades
replace profesion3_ci = 9  if degfield == 19  // Communications → Periodismo e Información
replace profesion3_ci = 9  if degfield == 20  // Communication Technologies → Periodismo e Información
replace profesion3_ci = 16 if degfield == 21  // Computer and Information Sciences → TIC
replace profesion3_ci = 26 if degfield == 22  // Cosmetology Services and Culinary Arts → Servicios personales
replace profesion3_ci = 4  if degfield == 23  // Education Administration and Teaching → Educación
replace profesion3_ci = 17 if degfield == 24  // Engineering → Ingeniería y Profesiones afines
replace profesion3_ci = 17 if degfield == 25  // Engineering Technologies → Ingeniería y Profesiones afines
replace profesion3_ci = 7  if degfield == 26  // Linguistics and Foreign Languages → Idiomas
replace profesion3_ci = 25 if degfield == 29  // Family and Consumer Sciences → Bienestar
replace profesion3_ci = 11 if degfield == 32  // Law → Derecho
replace profesion3_ci = 6  if degfield == 33  // English Language, Literature, and Composition → Humanidades
replace profesion3_ci = 6  if degfield == 34  // Liberal Arts and Humanities → Humanidades
replace profesion3_ci = 9  if degfield == 35  // Library Science → Periodismo e Información (ISCED-F 0322)
replace profesion3_ci = 12 if degfield == 36  // Biology and Life Sciences → Ciencias Biológicas
replace profesion3_ci = 15 if degfield == 37  // Mathematics and Statistics → Matemáticas y Estadística
replace profesion3_ci = 28 if degfield == 38  // Military Technologies → Servicios de seguridad
replace profesion3_ci = 1  if degfield == 40  // Interdisciplinary and Multi-Disciplinary Studies → Programas y certificaciones básicas
replace profesion3_ci = 25 if degfield == 41  // Physical Fitness, Parks, Recreation, and Leisure → Bienestar
replace profesion3_ci = 6  if degfield == 48  // Philosophy and Religious Studies → Humanidades
replace profesion3_ci = 6  if degfield == 49  // Theology and Religious Vocations → Humanidades
replace profesion3_ci = 14 if degfield == 50  // Physical Sciences → Ciencias Físicas
replace profesion3_ci = 17 if degfield == 51  // Nuclear, Industrial Radiology, and Biological Technologies → Ingeniería
replace profesion3_ci = 8  if degfield == 52  // Psychology → Ciencias Sociales y del Comportamiento
replace profesion3_ci = 28 if degfield == 53  // Criminal Justice and Fire Protection → Servicios de seguridad
replace profesion3_ci = 8  if degfield == 54  // Public Affairs, Policy, and Social Work → Ciencias Sociales y del Comportamiento
replace profesion3_ci = 8  if degfield == 55  // Social Sciences → Ciencias Sociales y del Comportamiento
replace profesion3_ci = 19 if degfield == 56  // Construction Services → Arquitectura y Construcción
replace profesion3_ci = 17 if degfield == 57  // Electrical and Mechanic Repairs and Technologies → Ingeniería
replace profesion3_ci = 18 if degfield == 58  // Precision Production and Industrial Arts → Industria y Procesamiento
replace profesion3_ci = 29 if degfield == 59  // Transportation Sciences and Technologies → Servicios de transporte
replace profesion3_ci = 5  if degfield == 60  // Fine Arts → Artes
replace profesion3_ci = 24 if degfield == 61  // Medical and Health Sciences and Services → Salud
replace profesion3_ci = 10 if degfield == 62  // Business → Educación Comercial y Administración
replace profesion3_ci = 6  if degfield == 64  // History → Humanidades

capture label drop lbl_profesion3_ci
label define lbl_profesion3_ci ///
     1 "Programas y certificaciones básicas" ///
     2 "Alfabetización y Aritmética Elemental" ///
     3 "Competencias personales y desarrollo" ///
     4 "Educación" ///
     5 "Artes" ///
     6 "Humanidades (excepto idiomas)" ///
     7 "Idiomas" ///
     8 "Ciencias Sociales y del Comportamiento" ///
     9 "Periodismo e Información" ///
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

tab2xl profesion3_ci [iw=perwt] using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(USA2, replace)

*==============================================================================
* 2. cinef13_ci: campo amplio de educación (ISCED-F 2013, 1 dígito)
*==============================================================================

gen cinef13_ci = .

replace cinef13_ci = 0  if inlist(profesion3_ci, 1, 2, 3)   // Programas y certificaciones genéricos
replace cinef13_ci = 1  if profesion3_ci == 4                // Educación
replace cinef13_ci = 2  if inlist(profesion3_ci, 5, 6, 7)   // Artes y Humanidades
replace cinef13_ci = 3  if inlist(profesion3_ci, 8, 9)       // Ciencias Sociales, Periodismo e Información
replace cinef13_ci = 4  if inlist(profesion3_ci, 10, 11)     // Administración de Empresas y Derecho
replace cinef13_ci = 5  if inlist(profesion3_ci, 12, 13, 14, 15) // Ciencias Naturales, Matemáticas y Estadística
replace cinef13_ci = 6  if profesion3_ci == 16               // TIC
replace cinef13_ci = 7  if inlist(profesion3_ci, 17, 18, 19) // Ingeniería, Industria y Construcción
replace cinef13_ci = 8  if inlist(profesion3_ci, 20, 21, 22, 23) // Agropecuario, Silvicultura, Pesca y Veterinaria
replace cinef13_ci = 9  if inlist(profesion3_ci, 24, 25)     // Salud y Bienestar
replace cinef13_ci = 10 if inlist(profesion3_ci, 26, 27, 28, 29) // Servicios

capture label drop lbl_cinef13_ci
label define lbl_cinef13_ci ///
     0 "Programas y certificaciones genéricos" ///
     1 "Educación" ///
     2 "Artes y Humanidades" ///
     3 "Ciencias Sociales, Periodismo e Información" ///
     4 "Administración de Empresas y Derecho" ///
     5 "Ciencias Naturales, Matemáticas y Estadística" ///
     6 "Tecnología de la Información y la Comunicación (TIC)" ///
     7 "Ingeniería, Industria y Construcción" ///
     8 "Agropecuario, Silvicultura, Pesca y Veterinaria" ///
     9 "Salud y bienestar" ///
    10 "Servicios", replace

label values cinef13_ci lbl_cinef13_ci
label var cinef13_ci "Campo amplio de educación (ISCED-F 2013, 1 dígito, consecutivo)"



tab2xl cinef13_ci [iw=perwt] using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(USA, replace)

&

**# Bookmark #2












**# Bookmark #1

*====================================================*
* CINEF-13 (0-10) a partir de degfield
*====================================================*

gen byte cinef13_ci = .

* 0 Programas y certificaciones genéricos
replace cinef13_ci = 0 if inlist(degfield, 38, 40)
* 0 = N/A
* 38 = Military Technologies
* 40 = Interdisciplinary and Multi-Disciplinary Studies (General)

* 1 Educación
replace cinef13_ci = 1 if degfield == 23
* 23 = Education Administration and Teaching

* 2 Artes y Humanidades
replace cinef13_ci = 2 if inlist(degfield, 15, 26, 33, 34, 48, 49, 60, 64)
* 15 Area/Ethnic/Civilization Studies
* 26 Linguistics and Foreign Languages
* 33 English Language, Literature, and Composition
* 34 Liberal Arts and Humanities
* 48 Philosophy and Religious Studies
* 49 Theology and Religious Vocations
* 60 Fine Arts
* 64 History

* 3 Ciencias Sociales, Periodismo e Información
replace cinef13_ci = 3 if inlist(degfield, 19, 35, 52, 53, 54, 55)
* 19 Communications
* 35 Library Science
* 52 Psychology
* 53 Criminal Justice and Fire Protection
* 54 Public Affairs, Policy, and Social Work
* 55 Social Sciences

* 4 Administración de Empresas y Derecho
replace cinef13_ci = 4 if inlist(degfield, 32, 62)
* 32 Law
* 62 Business

* 5 Ciencias Naturales, Matemáticas y Estadística
replace cinef13_ci = 5 if inlist(degfield, 36, 37, 50, 51,13)
* 36 Biology and Life Sciences
* 37 Mathematics and Statistics
* 50 Physical Sciences
* 51 Nuclear, Industrial Radiology, and Biological Technologies
* 13 Environment and Natural Resources

* 6 TIC
replace cinef13_ci = 6 if inlist(degfield, 20, 21)
* 20 Communication Technologies
* 21 Computer and Information Sciences

* 7 Ingeniería, Industria y Construcción
replace cinef13_ci = 7 if inlist(degfield, 14, 24, 25, 56, 57, 58, 59)
* 14 Architecture
* 24 Engineering
* 25 Engineering Technologies
* 56 Construction Services
* 57 Electrical and Mechanic Repairs and Technologies
* 58 Precision Production and Industrial Arts
* 59 Transportation Sciences and Technologies

* 8 Agropecuario, Silvicultura, Pesca y Veterinaria
replace cinef13_ci = 8 if degfield == 11
* 11 Agriculture

* 9 Salud y bienestar
replace cinef13_ci = 9 if degfield == 61
* 61 Medical and Health Sciences and Services

* 10 Servicios
replace cinef13_ci = 10 if inlist(degfield, 22, 29, 41)
* 22 Cosmetology Services and Culinary Arts
* 29 Family and Consumer Sciences
* 41 Physical Fitness, Parks, Recreation, and Leisure

label var cinef13_ci "Campo de educación y formación (CINEF-13), derivado de degfield"

capture label drop lbl_cinef13_ci
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

graph bar (percent) [pweight=perwt], ///
    over(cinef13, sort(1) descending label(labsize(small))) ///
    ytitle("Porcentaje") ///
    blabel(bar, format(%4.1f) position(outside)) ///
    bargap(10) ///
    horizontal title("ESTADOS UNIDOS")
	
graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\profesiones_usa.png", replace 	


tab2xl cinef13_ci [iw=perwt] using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(USA, replace)