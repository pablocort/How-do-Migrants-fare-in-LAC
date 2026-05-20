# CHL Dictionary Check — CASEN 2017a, 2020a, 2022a vs. Reference 2024a

**Date:** 2026-04-16  
**Reference wave:** CHL 2024a (`do armo/chl/CHL_2024_variablesBID.do`)  
**Target waves:** 2017a, 2020a, 2022a  
**Survey:** CASEN (Encuesta de Caracterización Socioeconómica Nacional)  
**Method:** Python dictionary check across raw DTA files + review of IDB/SCL/MECOVI alternative do-files

---

## Summary of key differences

| Variable | 2024 (ref) | 2022 | 2020 | 2017 | Notes |
|---|---|---|---|---|---|
| **Identifiers** |||||  |
| `id_persona` | ✅ | ✅ | ✅ | ❌ | 2017: use `o` instead |
| `o` (alt person ID) | ❌ | ❌ | ✅ | ✅ | 2017/2020: person ID |
| `folio` (household ID) | ✅ | ✅ | ✅ | ✅ | Stable |
| `expr` (expansion factor) | ✅ | ✅ | ✅ | ✅ | Stable |
| **Labor — hours** |||||  |
| `o10` (hours last week) | ✅ | ✅ | ❌ | ✅ | 2020: COVID — use `y2_hrs / 4.3` |
| `y2_hrs` (monthly hours) | ✅ | ✅ | ✅ | ✅ | Available all waves; used only in 2020 |
| **Labor — contract / social security** |||||  |
| `o18` (contract type part 1) | ✅ | ✅ | ❌ | ✅ | 2020: not asked → tipocontrato_ci = . |
| `o19` (contract written) | ✅ | ✅ | ❌ | ✅ | 2020: not asked → tipocontrato_ci = . |
| `o31` (health affiliation) | ✅ | ✅ | ✅ | ❌ | 2017: use `o28` |
| `o32` (pension contribution) | ✅ | ✅ | ✅ | ❌ | 2017: use `o29` |
| `o28` (affil. 2017 name) | ❌ | ❌ | ❌ | ✅ | 2017 only |
| `o29` (cotiz. 2017 name) | ✅ | ✅ | ✅ | ✅ | Numeric; available all waves but 2017 uses it for cotizando |
| **Education** |||||  |
| `e6c_completo` (HE completed) | ✅ | ✅ | ❌ | ❌ | 2017/2020: derive from attendance proxy |
| `asiste` (attends education) | ✅ | ✅ | ❌ | ✅ | 2020: use `e2` instead |
| `e2` (COVID attendance) | ❌ | ❌ | ✅ | ✅ | 2020: attendance variable |
| `e3` (attend. level) | ✅ | ✅ | ❌ | ✅ | 2020: e3 absent |
| `e6a_asiste` (HE level curr.) | ✅ | ✅ | ❌ | ❌ | 2020/2017: set to . |
| `e6a_no_asiste` (HE level past) | ✅ | ✅ | ❌ | ❌ | 2020/2017: set to . |
| `cinef13_area` | ✅ | ✅ | ❌ | ❌ | 2020/2017: not asked |
| `cinef13_subarea` | ✅ | ✅ | ❌ | ❌ | 2020/2017: not asked |
| **Migration** |||||  |
| `r1b` (country of birth) | ✅ | ✅ | ✅ | ✅ | Stable |
| `r1cp` (years since arrival) | ✅ | ✅ | ❌ | ✅ | 2020: use `r2` categorical |
| `r2` (categorical years) | ❌ | ✅ | ✅ | ✅ | 1=<1yr, 2=1-5yr, 3=>5yr |
| `r1b_pais_esp` (country name) | ✅ | ✅ | ✅ | ❌ | 2017: use `r1b_p_cod` numeric |
| `r1b_pais_esp_cod` (country code) | ❌ | ✅ | ❌ | ❌ | 2022 only |
| `r1b_p_cod` (country code alt) | ❌ | ❌ | ✅ | ✅ | 2017/2020: country numeric code |

---

## Per-wave construction decisions

### CHL 2022a
Nearly identical to 2024. Key adjustments:
- `tipocontrato_ci`: `o18`/`o19` **present** (despite alt do-file comment saying otherwise — verified by Python check). Construct same as 2024.
- `migrantiguo5_ci`: `r2` available — can derive from `r1cp>=4` as in 2024 (r1cp also present).
- `mig_pais_ci`: use `r1b_pais_esp` (same as 2024; decode approach may differ slightly — use `r1b_pais_esp_cod` if `decode` fails).
- `edu_hdmf` cat 8 (higher education completed): `e6c_completo` present → same as 2024.
- `e6a_asiste`/`e6a_no_asiste`: present → same as 2024.
- LAC migration inlist: use `r1b_pais_esp` string values (same as 2024).

### CHL 2020a (COVID — extra care required)
Major questionnaire changes:
- **Hours**: `o10` absent → `horaspri_ci = round(y2_hrs / 4.3)` (monthly → weekly approximation)
- **Contract**: `o18`/`o19` absent → `tipocontrato_ci = .` (not asked)
- **Education attendance**: `asiste`/`e3` absent → use `e2` (1=yes, 2=no in 2020 coding)
- **Higher education**: `e6c_completo` absent → derive: if currently attending HE, mark as not-completed; if left HE, mark as completed-proxy only if prior level suggests graduation. **Safest approach**: if `asiste`-equivalent (`e2==1`) and HE level → edu_hdmf = 7 (in progress); if `e2==2` and HE level → edu_hdmf = 8 (completed, as proxy). Document clearly.
- **`e6a_asiste`/`e6a_no_asiste`**: absent → set to `.`; `cinef13_area/subarea`: absent.
- **Migration recency**: `r1cp` absent → use `r2` (1=<1yr → migrantiguo5=0; 2=1-5yr → migrantiguo5=0; 3=>5yr → migrantiguo5=1)
- **LAC codes**: use `r1b_p_cod` numeric (not `r1b_pais_esp`)
- **Person ID**: `id_persona` present in 2020 (Python confirmed `o` also present; use `id_persona` as in 2024 for consistency)
- **e6b/e6a missing code**: 99 in 2017 and 2020 alt do-files (replace with `.` before using)

### CHL 2017a
Key adjustments:
- **Person ID**: `id_persona` absent → use `o`
- **Social security**: `o31`/`o32` absent → use `o28` (afiliado) and `o29` (cotizando)
- **Contract**: `o18`/`o19` present (Python confirmed) → construct same as 2024
- **Education attendance**: `asiste` present, `e3` present → same logic as 2024
- **Higher education**: `e6c_completo` absent → same proxy approach as 2020
- **e6a_asiste/e6a_no_asiste**: absent → set to `.`; `cinef13`: absent
- **Migration recency**: `r1cp` present (Python confirmed) → `migrantiguo5_ci = (r1cp >= 4)`
- **LAC codes**: `r1b_pais_esp` absent → use `r1b_p_cod` numeric inlist
- **mig_pais_ci**: `r1b_pais_esp` absent → use numeric `r1b_p_cod` with recode/label approach
- **e6b/e6a missing code**: replace 99 with `.`

---

## LAC country codes by wave

| Country | 2024 (r1b_pais_esp string) | 2022 (r1b_pais_esp) | 2020 (r1b_p_cod numeric) | 2017 (r1b_p_cod numeric) |
|---|---|---|---|---|
| Bolivia | "Bolivia" | "Bolivia" | 68 | 68 |
| Brazil | "Brasil" | "Brasil" | 76 | 76 |
| Colombia | "Colombia" | "Colombia" | 170 | 170 |
| Cuba | "Cuba" | "Cuba" | 192 | 192 |
| Dominican Rep. | "República Dominicana" | "República Dominicana" | 214 | 214 |
| Ecuador | "Ecuador" | "Ecuador" | 218 | 218 |
| Haiti | "Haití" | "Haití" | 332 | 332 |
| Mexico | "México" | "México" | 484 | 484 |
| Peru | "Perú" | "Perú" | 604 | 604 |
| Venezuela | "Venezuela" | "Venezuela" | 862 | 862 |
| Argentina | "Argentina" | "Argentina" | 32 | 32 |
| Paraguay | "Paraguay" | "Paraguay" | 600 | 600 |
| Uruguay | "Uruguay" | "Uruguay" | 858 | 858 |

*Numeric codes for 2017/2020 derived from IDB/SCL alternative do-files and ISO 3166-1 numeric.*

---

## edu_hdmf construction (2017 and 2020)

Since `e6c_completo`, `e6a_asiste`, and `e6a_no_asiste` are absent in 2017 and 2020:

| edu_hdmf | Label | Construction in 2017/2020 |
|---|---|---|
| 1 | No education | e6a==1 (or missing/DK) |
| 2 | Primary incomplete | e6a==2 & e6b<6 |
| 3 | Primary complete | e6a==2 & e6b>=6 |
| 4 | Secondary incomplete | (e6a==3\|e6a==4) & e6b<3 |
| 5 | Secondary complete | (e6a==3\|e6a==4) & e6b>=3 |
| 6 | Technical/tertiary incomplete | (e6a>=5 & e6a<=8) & asiste/e2==yes |
| 7 | Technical/tertiary complete | (e6a>=5 & e6a<=8) & asiste/e2==no |
| 8 | University complete | set to . (cannot distinguish 7 vs 8 without e6c_completo) |

**Decision for 2017/2020**: Collapse HE into single category (edu_hdmf=7 for any higher education). Users should note that the distinction between incomplete (6), technical complete (7), and university complete (8) is not available in these waves. Add a prominent comment block in the .do file.

