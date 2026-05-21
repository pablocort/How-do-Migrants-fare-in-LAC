# Dictionary Summary: DOM — ENFT 2024

**Source files:** Diccionario.xlsx  
**Variables decoded:** 290  
**Variables with value codes:** 262  
**Tables/modules:** 7 (TNFT_COMPROMISOS_ECON, TNFT_COMPROMISOS_ECON_DET, TNFT_HOGARES, TNFT_MIEMBROS, TNFT_OCUPACION, TNFT_VIVIENDAS, tasamoneda)  

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
| Demographics | `sexo_ci` | ✓ LIKELY_FOUND |
| Demographics | `relacion_ci` | ✓ LIKELY_FOUND |
| Demographics | `miembros_ci` | ✓ LIKELY_FOUND |
| Migration | `migrante_ci` | ✓ LIKELY_FOUND |
| Migration | `mig_pais_ci` | ✗ NOT_FOUND |
| Migration | `migrantiguo5_ci` | ✗ NOT_FOUND |
| Employment status | `condocup_ci` | ✓ LIKELY_FOUND |
| Employment status | `emp_ci` | ✓ LIKELY_FOUND |
| Employment status | `desemp_ci` | ✗ NOT_FOUND |
| Employment status | `pea_ci` | ✗ NOT_FOUND |
| Job characteristics | `formal_ci` | ✓ LIKELY_FOUND |
| Job characteristics | `tipocontrato_ci` | ✓ LIKELY_FOUND |
| Job characteristics | `horaspri_ci` | ✗ NOT_FOUND |
| Job characteristics | `horastot_ci` | ✗ NOT_FOUND |
| Job characteristics | `cotizando_ci` | ✓ LIKELY_FOUND |
| Job characteristics | `afiliado_ci` | ✓ LIKELY_FOUND |
| Education | `aedu_ci` | ✗ NOT_FOUND |
| Education | `edu_isced` | ✗ NOT_FOUND |
| Education | `edu_hdmf` | ✗ NOT_FOUND |
| Income | `ylm_ci` | ✓ LIKELY_FOUND |
| Income | `ylnm_ci` | ✗ NOT_FOUND |
| Income | `ynlm_ci` | ✓ LIKELY_FOUND |
| Income | `ytot_ci` | ✗ NOT_FOUND |
| Income | `remesas_ci` | ✓ LIKELY_FOUND |
| Income | `remesas_ch` | ✗ NOT_FOUND |

**Coverage: 14/31 HDMF variables likely found (45%)**

---

## Decode Notes

- Source: Diccionario.xlsx (2 sheet(s))
- Sheet 'Diccionario': DOM_ENFT layout, 11844 rows
-   → 262 variables extracted
- Sheet 'tasamoneda': UNKNOWN layout — best-effort extraction
-   → 39 variables (best-effort — verify manually)
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
-   Duplicate variable '1' — later file takes precedence
