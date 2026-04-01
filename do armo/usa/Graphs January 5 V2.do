clear all
cd "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\do armo\usa"
do usa_00004.do

* Sample restrictions
*keep if bpl==300              // SOUTH AMERICA
*keep if bpld==30065           // Venezuela
keep if sample==202303        // 2019–2023, ACS 5-year


save "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\usa\usa_00004.dta" , replace



* Citizenship
gen byte not_citizen = (citizen==3)
replace not_citizen = . if missing(citizen)

tab degfield [iw=perwt] if degfield!=0 // Field of degree , ALL
tab degfield if degfield!=0 & not_citizen ==1 // not-citizen

// Top 5: Business (27.72%), Engineering (20.56%), Education Administration and Teaching (8.26), Social Sciences (5.16%), Medical and Health Sciences and Service(4.82)  
gen field1=degfield==62 if degfield!=0
gen field2=degfield==24 | degfield==25 if degfield!=0
gen field3=degfield==23 if degfield!=0
gen field4=degfield==55 if degfield!=0
gen field5=degfield==61 if degfield!=0

gen byte grp = .
replace grp = 1 if not_citizen==0
replace grp = 2 if not_citizen==1
label define grp 1 "Citizen" 2 "Non-Citizen", replace
label values grp grp

 label var field1 "Business"
 label var field2 "Engineering" 
 label var field3 "Education Administration and Teaching"
 label var field4 "Social Sciences" 
 label var field5 "Medical and Health Sciences and Service"

 ** for graph
preserve
    keep grp perwt field1 field2 field3 field4 field5

    gen long id = _n
    reshape long field, i(id) j(k)

    * Labels de profesiones (ajusta)
    label define k_lbl ///
        1 "Business" ///
        2 "Engineering" ///
        3 "Education Administration" ///
        4 "Social Science" ///
        5 "Medical & Health Sciences", replace
    label values k k_lbl

    *-----------------------------
    collapse (mean) p=field [pw=perwt], by(k grp)
    gen pct = 100*p
    keep k grp pct

    *-----------------------------
    reshape wide pct, i(k) j(grp)

    rename pct1 citizen
    rename pct2 noncitizen
    label var citizen    "Citizen"
    label var noncitizen "Non-Citizen"

    *-----------------------------
graph bar citizen noncitizen,  over(k,relabel(1 "Business" 2 "Engineering" 3 `" "Education""Administration and Teaching" "' 4 "Social Science" 5 `" "Medical and Health""Sciences and Service" "') ///
    label(labsize(small)) gap(35)) ///
    blabel(bar, format(%2.0f) pos(outside) size(small) color(black)) ///
    ylabel(0(10)40, angle(horizontal) grid) ///
    ytitle("") ///
    legend(order(1 "Citizen" 2 "Non-Citizen") pos(12) ring(0) col(1)) ///
    bar(1, color(navy)) bar(2, color(maroon)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "Figure5.png", replace 	
restore

*========================
* Graph: Top 5 fields (overall, weighted)
*========================
preserve
    keep perwt field1 field2 field3 field4 field5

    gen long id = _n
    reshape long field, i(id) j(k)

    * Etiquetas (ajusta si quieres)
    label define k_lbl ///
        1 "Business" ///
        2 "Engineering" ///
        3 "Education Administration" ///
        4 "Social Science" ///
        5 "Medical & Health Sciences", replace
    label values k k_lbl

    * Promedio ponderado del dummy = proporción
    collapse (mean) p=field [pw=perwt], by(k)
    gen pct = 100*p

    * Gráfico
    graph hbar pct, over(k, ///
            relabel(1 "Business" 2 "Engineering" ///
                    3 `" "Education""Administration and Teaching" "' ///
                    4 "Social Science" ///
                    5 `" "Medical and Health""Sciences and Service" "') ///
            label(labsize(small)) gap(35)) ///
        blabel(bar, format(%4.1f) pos(outside) size(small) color(black)) ///
        ylabel(0(10)40, angle(horizontal) grid) ///
        ytitle("USA") ///
        legend(off) ///
        graphregion(color(white)) plotregion(color(white))

    graph export "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\profesiones_usa.png", replace
restore



**********************************************************************************


clear all
cd "C:\Users\steffannyr\OneDrive - Inter-American Development Bank Group\IPUMS"
do usa_00002.do

* Sample restrictions
keep if bpl==300              // SOUTH AMERICA
keep if bpld==30065           // Venezuela
keep if sample==202303        // 2019–2023, ACS 5-year

* Citizenship
gen byte not_citizen = (citizen==3)
replace not_citizen = . if missing(citizen)

gen byte grp = .
replace grp = 1 if not_citizen==0
replace grp = 2 if not_citizen==1
label define grp 1 "Citizen" 2 "Non-Citizen", replace
label values grp grp


/********************************************************************
1) Age Distribution (stacked 100%)
********************************************************************/
gen byte edad = .
replace edad = 1 if age < 18
replace edad = 2 if inrange(age,18,64)
replace edad = 3 if age >= 65
label define edad 1 "Under 18" 2 "18 to 64" 3 "65 and Over", replace
label values edad edad
label var edad "Age group"

preserve
keep if !missing(edad) & !missing(grp)

collapse (sum) w=perwt, by(grp edad)
bys grp: egen tot = total(w)
gen pct = 100*w/tot
keep grp edad pct

reshape wide pct, i(grp) j(edad)

graph bar pct*, over(grp) stack asyvars ///
    blabel(bar, format(%2.1f) pos(center) size(small) color(black)) ///
    ylabel(0(20)100) ///
    legend(order(3 "65 and Over" 2 "18 to 64" 1 "Under 18"))
	
graph export "Figure1.png", replace 	
restore


/********************************************************************
2) Educational Attainment (3 categories; 2 bars per category)
educ codes:
0 N/A or no schooling ... 11 5+ years of college, 99 Missing
********************************************************************/
gen byte educacion = .
label define educacion 1 "Less than High School Diploma" ///
                      2 "High School Diploma or Higher" ///
                      3 "Bachelor's Degree or Higher", replace

replace educacion = . if missing(educ) | educ==99
replace educacion = 1 if inrange(educ,0,5)
replace educacion = 2 if inrange(educ,6,11)
replace educacion = 3 if inrange(educ,10,11)
label values educacion educacion

preserve
keep if !missing(educacion) & !missing(grp)
keep if age>=25

collapse (sum) w=perwt, by(grp educacion)
bys grp: egen tot = total(w)
gen pct = 100*w/tot
keep grp educacion pct

reshape wide pct, i(educacion) j(grp)

graph bar pct1 pct2, ///
    over(educacion, ///
        relabel(1 "Less than High School Diploma" ///
                2 "High School Diploma or Higher" ///
                3 "Bachelor's Degree or Higher") ///
        label(labsize(small)) gap(35)) ///
    blabel(bar, format(%2.0f) pos(outside) size(small) color(black)) ///
    ylabel(0(10)60, angle(horizontal) grid) ///
    ytitle("") ///
    legend(order(1 "Citizen" 2 "Non-Citizen") pos(12) ring(0) col(1)) ///
    bar(1, color(navy)) bar(2, color(maroon)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "Figure2.png", replace 	
restore



/********************************************************************
3) Occupation (5 categories OCC 2018+; 2 bars per category)
********************************************************************/
gen byte occ_cat5 = .
label define occ_cat5 ///
    1 "Management, Business, Science, and Arts" ///
    2 "Service Occupations" ///
    3 "Sales and Office" ///
    4 "Natural Resources, Construction, and Maintenance" ///
    5 "Production, Transportation, and Material Moving", replace
label values occ_cat5 occ_cat5

replace occ_cat5 = . if missing(occ) | occ==0
replace occ_cat5 = 1 if inrange(occ, 10, 3550)
replace occ_cat5 = 2 if inrange(occ, 3601, 4655)
replace occ_cat5 = 3 if inrange(occ, 4700, 5940)
replace occ_cat5 = 4 if inrange(occ, 6005, 7640)
replace occ_cat5 = 5 if inrange(occ, 7700, 9760)
replace occ_cat5 = . if inrange(occ,9800,9830) | occ==9920   // optional exclusions

preserve
keep if !missing(occ_cat5) & !missing(grp)

collapse (sum) w=perwt, by(grp occ_cat5)
bys grp: egen tot = total(w)
gen pct = 100*w/tot
keep grp occ_cat5 pct

reshape wide pct, i(occ_cat5) j(grp)

graph bar pct1 pct2, ///
    over(occ_cat5, ///
        relabel(1 `" "Management, Business,""Science, and Arts" "' ///
                2 "Service Occupations" ///
                3 "Sales and Office" ///
                4 `" "Natural Resources,"" Construction, and Maintenance" "' ///
                5 `" "Production, Transportation,""and Material Moving" "') ///
        label(labsize(vsmall)) gap(35)) ///
    blabel(bar, format(%2.0f) pos(outside) size(small) color(black)) ///
    ylabel(0(10)60, angle(horizontal) grid) ///
    ytitle("") ///
    legend(order(1 "Citizen" 2 "Non-Citizen") pos(12) ring(0) col(1)) ///
    bar(1, color(navy)) bar(2, color(maroon)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "Figure3.png", replace 	
restore


/********************************************************************
4) Period of Arrival (3 categories; 2 bars per category)
********************************************************************/
gen byte period_arrival = .
label define period_arrival ///
    1 "Entered Before 2000" ///
    2 "Entered 2000 to 2009" ///
    3 "Entered 2010 or Later", replace
label values period_arrival period_arrival

replace period_arrival = . if missing(yrimmig) | yrimmig==0
replace period_arrival = 1 if yrimmig < 2000
replace period_arrival = 2 if inrange(yrimmig, 2000, 2009)
replace period_arrival = 3 if yrimmig >= 2010

preserve
keep if !missing(period_arrival) & !missing(grp)

collapse (sum) w=perwt, by(grp period_arrival)
bys grp: egen tot = total(w)
gen pct = 100*w/tot
keep grp period_arrival pct

reshape wide pct, i(period_arrival) j(grp)

graph bar pct1 pct2, ///
    over(period_arrival, ///
        relabel(1 "Entered Before 2000" ///
                2 "Entered 2000 to 2009" ///
                3 "Entered 2010 or Later") ///
        label(labsize(vsmall)) gap(35)) ///
    blabel(bar, format(%2.0f) pos(outside) size(small) color(black)) ///
    ylabel(0(10)100, angle(horizontal) grid) ///
    ytitle("") ///
    legend(order(1 "Citizen" 2 "Non-Citizen") pos(12) ring(0) col(1)) ///
    bar(1, color(navy)) bar(2, color(maroon)) ///
    graphregion(color(white)) plotregion(color(white))
graph export "Figure4.png", replace 	
restore