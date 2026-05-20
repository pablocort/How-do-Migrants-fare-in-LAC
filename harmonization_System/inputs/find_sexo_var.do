clear
set more off
di "File created with the Claude HDMF system — 2026-04-08"

local root "C:/Users/PABLOCOR/OneDrive - Inter-American Development Bank Group/Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento/Datos/hdmf/How-do-Migrants-fare-in-LAC/bases armo/raw/col"

* Check sex variable across all waves
foreach wave in 2018t3 2019t3 2020t3 2021t3 2022t3 2023t3 2024t3 2025t3 {
    use "`root'/COL_`wave'.dta", clear
    di ">>> COL_`wave'"
    foreach v in p6020 p3271 p6016 p3016 p6018 {
        capture confirm variable `v'
        if _rc == 0 {
            local vtype: type `v'
            local vlbl:  variable label `v'
            di "  EXISTS `v' [`vtype'] `vlbl'"
            tab `v', missing
        }
    }
    di ""
}
