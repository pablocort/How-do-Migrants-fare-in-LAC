* (Versi�n Stata 12)
clear
set more off

*Última Modificación: Alvaro Altamirano / Octubre 2019.
*________________________________________________________________________________________________________________*

 * Activar si es necesario (dejar desactivado para evitar sobreescribir la base y dejar la posibilidad de 
 * utilizar un loop)
 * Los datos se obtienen de las carpetas que se encuentran en el servidor: ${surveysFolder}
 * Se tiene acceso al servidor �nicamente al interior del BID.
 * El servidor contiene las bases de datos MECOVI.
 *________________________________________________________________________________________________________________*
 
global ruta = "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\mex"

local PAIS MEX
local ENCUESTA ENOE
local ANO "2025"
local ronda t4

*local log_file = "${surveysFolder}\harmonized\\`PAIS'\\`ENCUESTA'\\log\\`PAIS'_`ANO'`ronda'_mergeBID.log"
local base_out = "C:\Users\STEFFANNYR\OneDrive - Inter-American Development Bank Group\Paraiso Pinto Furtado Luzes, Marta's files - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\raw\mex\\`PAIS'_`ANO'`ronda'.dta"

*capture log close
*log using "`log_file'", replace 


// bases a nivel individual
use "$ruta\ENOE_COE1T425.dta", clear
isid cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren
sort cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren
save "$ruta\ENOE_COE1T425.dta", replace

use "$ruta\ENOE_COE2T425.dta", clear
isid cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren
sort cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren
save "$ruta\ENOE_COE2T425.dta", replace

use "$ruta\ENOE_SDEMT425.dta", clear
isid cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren

// bases a nivel de hogar
use "$ruta\ENOE_VIVT425.dta", clear
isid cd_a cve_ent con upm d_sem n_pro_viv v_sel 

use "$ruta\ENOE_HOGT425.dta", clear
isid cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog 

// Pegar las  bases a nivel individual 

use "$ruta\ENOE_SDEMT425.dta", clear
drop if r_def!=0 // quedarnos solo con entrevistas completas
sort cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren
merge cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren using "$ruta\ENOE_COE1T425.dta"
tab _merge
drop _merge

sort  cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren	
merge cd_a cve_ent con upm d_sem n_pro_viv v_sel n_hog h_mud n_ent per n_ren   using "$ruta\ENOE_COE2T425.dta"
tab _merge
drop _merge

foreach i of varlist _all {
local longlabel: var label `i'
local shortlabel = substr(`"`longlabel'"',1,79)
label var `i' `"`shortlabel'"'
}
save "`base_out'", replace
