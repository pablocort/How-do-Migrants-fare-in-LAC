clear all
cd "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\IPUMS"
do usa_00004.do

* Sample restrictions
keep if bpl==300              // SOUTH AMERICA
keep if bpld==30065           // Venezuela
keep if sample==202303        // 2019–2023, ACS 5-year

* Citizenship
gen byte not_citizen = (citizen==3)
replace not_citizen = . if missing(citizen)

tab degfield [iw=perwt] if degfield!=0 // Field of degree , ALL

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