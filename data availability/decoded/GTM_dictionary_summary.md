# Dictionary Summary: GTM — ENEIC 2025

**Source files:** Diccionario_Hogares_ENEIC_II-2025.xlsx, Diccionario_Personas_ENEIC_II-2025.xlsx  
**Variables decoded:** 280  
**Variables with value codes:** 0  
**Tables/modules:** 2 (Dicc Hogares, Dicc Personas)  

---

## HDMF Variable Coverage Pre-Check

Status is based on keyword matching against variable names and labels.
LIKELY_FOUND means a concept keyword appeared — manual verification still required.

| Domain | HDMF Variable | Status |
|--------|---------------|--------|
| Identifiers & weights | `pais_c` | ✗ NOT_FOUND |
| Identifiers & weights | `idh_ch` | ✗ NOT_FOUND |
| Identifiers & weights | `idp_ci` | ✗ NOT_FOUND |
| Identifiers & weights | `factor_ci` | ✗ NOT_FOUND |
| Identifiers & weights | `factor_ch` | ✗ NOT_FOUND |
| Demographics | `edad_ci` | ✓ LIKELY_FOUND |
| Demographics | `sexo_ci` | ✗ NOT_FOUND |
| Demographics | `relacion_ci` | ✓ LIKELY_FOUND |
| Demographics | `miembros_ci` | ✗ NOT_FOUND |
| Migration | `migrante_ci` | ✗ NOT_FOUND |
| Migration | `mig_pais_ci` | ✗ NOT_FOUND |
| Migration | `migrantiguo5_ci` | ✗ NOT_FOUND |
| Employment status | `condocup_ci` | ✓ LIKELY_FOUND |
| Employment status | `emp_ci` | ✓ LIKELY_FOUND |
| Employment status | `desemp_ci` | ✓ LIKELY_FOUND |
| Employment status | `pea_ci` | ✓ LIKELY_FOUND |
| Job characteristics | `formal_ci` | ✓ LIKELY_FOUND |
| Job characteristics | `tipocontrato_ci` | ✗ NOT_FOUND |
| Job characteristics | `horaspri_ci` | ✗ NOT_FOUND |
| Job characteristics | `horastot_ci` | ✗ NOT_FOUND |
| Job characteristics | `cotizando_ci` | ✗ NOT_FOUND |
| Job characteristics | `afiliado_ci` | ✓ LIKELY_FOUND |
| Education | `aedu_ci` | ✗ NOT_FOUND |
| Education | `edu_isced` | ✓ LIKELY_FOUND |
| Education | `edu_hdmf` | ✓ LIKELY_FOUND |
| Income | `ylm_ci` | ✓ LIKELY_FOUND |
| Income | `ylnm_ci` | ✗ NOT_FOUND |
| Income | `ynlm_ci` | ✗ NOT_FOUND |
| Income | `ytot_ci` | ✗ NOT_FOUND |
| Income | `remesas_ci` | ✗ NOT_FOUND |
| Income | `remesas_ch` | ✗ NOT_FOUND |

**Coverage: 11/31 HDMF variables likely found (35%)**

---

## Decode Notes

- Source: Diccionario_Hogares_ENEIC_II-2025.xlsx (1 sheet(s))
- Sheet 'Dicc Hogares': GTM_ENEIC layout, 122 rows
-   → 24 variables extracted
-   Duplicate variable 'TRIMESTRE' — later file takes precedence
-   Duplicate variable 'DOMINIO' — later file takes precedence
-   Duplicate variable 'P00A10' — later file takes precedence
-   Duplicate variable 'P00B01' — later file takes precedence
-   Duplicate variable 'P00B02' — later file takes precedence
-   Duplicate variable 'P00B03' — later file takes precedence
-   Duplicate variable 'P00B04' — later file takes precedence
-   Duplicate variable 'P01A01' — later file takes precedence
- Source: Diccionario_Personas_ENEIC_II-2025.xlsx (1 sheet(s))
- Sheet 'Dicc Personas': GTM_ENEIC layout, 2460 rows
-   → 483 variables extracted
-   Duplicate variable 'ANIO' — later file takes precedence
-   Duplicate variable 'TRIMESTRE' — later file takes precedence
-   Duplicate variable 'DOMINIO' — later file takes precedence
-   Duplicate variable 'NUM_HOGAR' — later file takes precedence
-   Duplicate variable 'FACTOR' — later file takes precedence
-   Duplicate variable 'P00A10' — later file takes precedence
-   Duplicate variable 'Valores de variable' — later file takes precedence
-   Duplicate variable 'Valor' — later file takes precedence
-   Duplicate variable 'DOMINIO' — later file takes precedence
-   Duplicate variable 'P00A10' — later file takes precedence
-   Duplicate variable 'P02A01C' — later file takes precedence
-   Duplicate variable 'P02A01D' — later file takes precedence
-   Duplicate variable 'P02A01G' — later file takes precedence
-   Duplicate variable 'P02A02' — later file takes precedence
-   Duplicate variable 'P02A05A' — later file takes precedence
-   Duplicate variable 'P02A05B' — later file takes precedence
-   Duplicate variable 'P02A05F' — later file takes precedence
-   Duplicate variable 'P02A06A' — later file takes precedence
-   Duplicate variable 'P02A07' — later file takes precedence
-   Duplicate variable 'P02A08' — later file takes precedence
-   Duplicate variable 'P02A09' — later file takes precedence
-   Duplicate variable 'P02A10' — later file takes precedence
-   Duplicate variable 'P02A11A' — later file takes precedence
-   Duplicate variable 'P02A11B' — later file takes precedence
-   Duplicate variable 'P02A11C' — later file takes precedence
-   Duplicate variable 'P02A11D' — later file takes precedence
-   Duplicate variable 'P02A11E' — later file takes precedence
-   Duplicate variable 'P02A11F' — later file takes precedence
-   Duplicate variable 'P02A12' — later file takes precedence
-   Duplicate variable 'P02A13' — later file takes precedence
-   Duplicate variable 'P03A01' — later file takes precedence
-   Duplicate variable 'P03A02' — later file takes precedence
-   Duplicate variable 'P03A03A' — later file takes precedence
-   Duplicate variable 'P03A04B' — later file takes precedence
-   Duplicate variable 'P04A01' — later file takes precedence
-   Duplicate variable 'P04A02' — later file takes precedence
-   Duplicate variable 'P04A03' — later file takes precedence
-   Duplicate variable 'P04A04' — later file takes precedence
-   Duplicate variable 'P05A02' — later file takes precedence
-   Duplicate variable 'P05A03' — later file takes precedence
-   Duplicate variable 'P05A04' — later file takes precedence
-   Duplicate variable 'P05A05' — later file takes precedence
-   Duplicate variable 'P05A06' — later file takes precedence
-   Duplicate variable 'P05A07' — later file takes precedence
-   Duplicate variable 'P05A08' — later file takes precedence
-   Duplicate variable 'P05A09' — later file takes precedence
-   Duplicate variable 'P05B01' — later file takes precedence
-   Duplicate variable 'P05B02' — later file takes precedence
-   Duplicate variable 'P05B03' — later file takes precedence
-   Duplicate variable 'P05B05' — later file takes precedence
-   Duplicate variable 'P05B06' — later file takes precedence
-   Duplicate variable 'P05B07' — later file takes precedence
-   Duplicate variable 'P05B08' — later file takes precedence
-   Duplicate variable 'P05B09' — later file takes precedence
-   Duplicate variable 'P05B10' — later file takes precedence
-   Duplicate variable 'P05B11' — later file takes precedence
-   Duplicate variable 'P05C01A' — later file takes precedence
-   Duplicate variable 'P05C01' — later file takes precedence
-   Duplicate variable 'P05C02A' — later file takes precedence
-   Duplicate variable 'P05C02_2D' — later file takes precedence
-   Duplicate variable 'P05C02_1D' — later file takes precedence
-   Duplicate variable 'P05C04A' — later file takes precedence
-   Duplicate variable 'P05C04_2D' — later file takes precedence
-   Duplicate variable 'P05C04_1D' — later file takes precedence
-   Duplicate variable 'P05C07B' — later file takes precedence
-   Duplicate variable 'P05C08A' — later file takes precedence
-   Duplicate variable 'P05C09A' — later file takes precedence
-   Duplicate variable 'P05C09B' — later file takes precedence
-   Duplicate variable 'P05C10' — later file takes precedence
-   Duplicate variable 'P05C11A' — later file takes precedence
-   Duplicate variable 'P05C11B' — later file takes precedence
-   Duplicate variable 'P05C11F' — later file takes precedence
-   Duplicate variable 'P05C12' — later file takes precedence
-   Duplicate variable 'P05C13' — later file takes precedence
-   Duplicate variable 'P05C14' — later file takes precedence
-   Duplicate variable 'P05C15A' — later file takes precedence
-   Duplicate variable 'P05C15B' — later file takes precedence
-   Duplicate variable 'P05C15C' — later file takes precedence
-   Duplicate variable 'P05C15D' — later file takes precedence
-   Duplicate variable 'P05C15E' — later file takes precedence
-   Duplicate variable 'P05C15F' — later file takes precedence
-   Duplicate variable 'P05C15G' — later file takes precedence
-   Duplicate variable 'P05C16' — later file takes precedence
-   Duplicate variable 'P05C17' — later file takes precedence
-   Duplicate variable 'P05C18' — later file takes precedence
-   Duplicate variable 'P05C19' — later file takes precedence
-   Duplicate variable 'P05C20' — later file takes precedence
-   Duplicate variable 'P05C21A' — later file takes precedence
-   Duplicate variable 'P05C21B' — later file takes precedence
-   Duplicate variable 'P05C21C' — later file takes precedence
-   Duplicate variable 'P05C22' — later file takes precedence
-   Duplicate variable 'P05C23' — later file takes precedence
-   Duplicate variable 'P05C24A' — later file takes precedence
-   Duplicate variable 'P05C24B' — later file takes precedence
-   Duplicate variable 'P05C24C' — later file takes precedence
-   Duplicate variable 'P05C24D' — later file takes precedence
-   Duplicate variable 'P05C24E' — later file takes precedence
-   Duplicate variable 'P05C24F' — later file takes precedence
-   Duplicate variable 'P05C25' — later file takes precedence
-   Duplicate variable 'P05D02A' — later file takes precedence
-   Duplicate variable 'P05D03A' — later file takes precedence
-   Duplicate variable 'P05D04A' — later file takes precedence
-   Duplicate variable 'P05D05A' — later file takes precedence
-   Duplicate variable 'P05D06A' — later file takes precedence
-   Duplicate variable 'P05D07A' — later file takes precedence
-   Duplicate variable 'P05D08A' — later file takes precedence
-   Duplicate variable 'P05D09A' — later file takes precedence
-   Duplicate variable 'P05D10A' — later file takes precedence
-   Duplicate variable 'P05D11A' — later file takes precedence
-   Duplicate variable 'P05D12A' — later file takes precedence
-   Duplicate variable 'P05D13A' — later file takes precedence
-   Duplicate variable 'P05D14A' — later file takes precedence
-   Duplicate variable 'P05D15' — later file takes precedence
-   Duplicate variable 'P05D16' — later file takes precedence
-   Duplicate variable 'P05D17' — later file takes precedence
-   Duplicate variable 'P05E01' — later file takes precedence
-   Duplicate variable 'P05E02' — later file takes precedence
-   Duplicate variable 'P05E03' — later file takes precedence
-   Duplicate variable 'P05E04' — later file takes precedence
-   Duplicate variable 'P05E05' — later file takes precedence
-   Duplicate variable 'P05E06' — later file takes precedence
-   Duplicate variable 'P05E07' — later file takes precedence
-   Duplicate variable 'P05E08' — later file takes precedence
-   Duplicate variable 'P05E09' — later file takes precedence
-   Duplicate variable 'P05E12A' — later file takes precedence
-   Duplicate variable 'P05F01' — later file takes precedence
-   Duplicate variable 'P05F02' — later file takes precedence
-   Duplicate variable 'P05F03' — later file takes precedence
-   Duplicate variable 'P05F04A' — later file takes precedence
-   Duplicate variable 'P05F04B' — later file takes precedence
-   Duplicate variable 'P05F04C' — later file takes precedence
-   Duplicate variable 'P05F04D' — later file takes precedence
-   Duplicate variable 'P05F04E' — later file takes precedence
-   Duplicate variable 'P05F04F' — later file takes precedence
-   Duplicate variable 'P05F04G' — later file takes precedence
-   Duplicate variable 'P05F05' — later file takes precedence
-   Duplicate variable 'P05F06' — later file takes precedence
-   Duplicate variable 'P05F07' — later file takes precedence
-   Duplicate variable 'P05F08' — later file takes precedence
-   Duplicate variable 'P05F09A' — later file takes precedence
-   Duplicate variable 'P05F09B' — later file takes precedence
-   Duplicate variable 'P05F09C' — later file takes precedence
-   Duplicate variable 'P05F09D' — later file takes precedence
-   Duplicate variable 'P05F09E' — later file takes precedence
-   Duplicate variable 'P05F09F' — later file takes precedence
-   Duplicate variable 'P05F09G' — later file takes precedence
-   Duplicate variable 'P05F09H' — later file takes precedence
-   Duplicate variable 'P05F09I' — later file takes precedence
-   Duplicate variable 'P05F09J' — later file takes precedence
-   Duplicate variable 'P05G01A' — later file takes precedence
-   Duplicate variable 'P05G01' — later file takes precedence
-   Duplicate variable 'P05G02A' — later file takes precedence
-   Duplicate variable 'P05G02_2D' — later file takes precedence
-   Duplicate variable 'P05G02_1D' — later file takes precedence
-   Duplicate variable 'P05G04A' — later file takes precedence
-   Duplicate variable 'P05G04_2D' — later file takes precedence
-   Duplicate variable 'P05G04_1D' — later file takes precedence
-   Duplicate variable 'P05G06A' — later file takes precedence
-   Duplicate variable 'P05G07' — later file takes precedence
-   Duplicate variable 'P05G08' — later file takes precedence
-   Duplicate variable 'P05G09' — later file takes precedence
-   Duplicate variable 'P05G11A' — later file takes precedence
-   Duplicate variable 'P05G12A' — later file takes precedence
-   Duplicate variable 'P05G13A' — later file takes precedence
-   Duplicate variable 'P05G14A' — later file takes precedence
-   Duplicate variable 'P05G15' — later file takes precedence
-   Duplicate variable 'P05G16' — later file takes precedence
-   Duplicate variable 'P05G17' — later file takes precedence
-   Duplicate variable 'P05G18' — later file takes precedence
-   Duplicate variable 'P05G19' — later file takes precedence
-   Duplicate variable 'P05G20' — later file takes precedence
-   Duplicate variable 'P05G21' — later file takes precedence
-   Duplicate variable 'P05G22' — later file takes precedence
-   Duplicate variable 'P05G23' — later file takes precedence
-   Duplicate variable 'P05G24' — later file takes precedence
-   Duplicate variable 'P05G25' — later file takes precedence
-   Duplicate variable 'P05G27A' — later file takes precedence
-   Duplicate variable 'P05G28A' — later file takes precedence
-   Duplicate variable 'P05G29A' — later file takes precedence
-   Duplicate variable 'P05G29B' — later file takes precedence
-   Duplicate variable 'P05G29C' — later file takes precedence
-   Duplicate variable 'P05G29D' — later file takes precedence
-   Duplicate variable 'P05G29E' — later file takes precedence
-   Duplicate variable 'P05G29F' — later file takes precedence
-   Duplicate variable 'P05G29G' — later file takes precedence
-   Duplicate variable 'P05H02' — later file takes precedence
-   Duplicate variable 'P05H03' — later file takes precedence
-   Duplicate variable 'P05H04A' — later file takes precedence
-   Duplicate variable 'P05H04B' — later file takes precedence
-   Duplicate variable 'P05H04C' — later file takes precedence
-   Duplicate variable 'P05H06' — later file takes precedence
-   Duplicate variable 'P05H07' — later file takes precedence
-   Duplicate variable 'P05H08' — later file takes precedence
-   Duplicate variable 'P05H09' — later file takes precedence
-   Duplicate variable 'P05H10' — later file takes precedence
-   Duplicate variable 'P05H11' — later file takes precedence
-   Duplicate variable 'P05H12' — later file takes precedence
-   Duplicate variable 'P06A01A' — later file takes precedence
-   Duplicate variable 'P06A02A' — later file takes precedence
-   Duplicate variable 'P06A03A' — later file takes precedence
-   Duplicate variable 'P06A04A' — later file takes precedence
-   Duplicate variable 'P06A05A' — later file takes precedence
-   Duplicate variable 'P06A06A' — later file takes precedence
-   Duplicate variable 'P06A07A' — later file takes precedence
-   Duplicate variable 'P06B01A' — later file takes precedence
-   Duplicate variable 'P06B02A' — later file takes precedence
-   Duplicate variable 'P06B03A' — later file takes precedence
-   Duplicate variable 'P06B04A' — later file takes precedence
-   Duplicate variable 'P06C01' — later file takes precedence
-   Duplicate variable 'P06C02A' — later file takes precedence
-   Duplicate variable 'P06C03A' — later file takes precedence
-   Duplicate variable 'P06C04A' — later file takes precedence
-   Duplicate variable 'PET' — later file takes precedence
-   Duplicate variable 'PEA' — later file takes precedence
-   Duplicate variable 'OCUPADOS' — later file takes precedence
-   Duplicate variable 'DESOCUPADOS' — later file takes precedence
-   Duplicate variable 'SUBVISIBLES' — later file takes precedence
-   Duplicate variable 'INACTIVOS' — later file takes precedence
-   Duplicate variable 'FORMAL_INFORMAL' — later file takes precedence
