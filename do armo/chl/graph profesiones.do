use "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo\CHL_2024a_BID.dta", clear

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
    horizontal title("CHILE")
	
graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\profesiones_chile.png", replace 	

tab2xl cinef13_ci [iw=factor_ci] if mig_pais_ci=="Venezuela" using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(CHILE, replace)

tab2xl profesion3_ci [iw=factor_ci] if mig_pais_ci=="Venezuela" using "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\cinef13_tab.xlsx", row(1) col(1) sheet(CHILE2, replace)

**# Bookmark #1

* Variable agrupada de nivel educativo (Chile) a partir de e6a
* Educación Especial (5) como missing

capture drop nivel_edu
gen byte nivel_edu = .

* 0 Ninguno
replace nivel_edu = 0 if e6a == 1   // Nunca asistió

* 1 Primaria (incluye inicial/preescolar y primaria)
replace nivel_edu = 1 if inlist(e6a, 2, 3, 4, 6)

* 2 Secundaria (básica / humanidades sistema antiguo)
replace nivel_edu = 2 if inlist(e6a, 7, 8)

* 3 Media (media científico-humanista y media técnica)
replace nivel_edu = 3 if inlist(e6a, 9, 10, 11)

* 4 Superior (técnico superior, profesional, magíster, doctorado)
replace nivel_edu = 4 if inlist(e6a, 12, 13, 14, 15)

* Missing explícito para educación especial
replace nivel_edu = . if e6a == 5

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
	title("CHILE")
	
graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\niveledu_chile.png", replace 	
	

