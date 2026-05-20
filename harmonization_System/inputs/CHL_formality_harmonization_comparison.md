# CHL — Formality Variable Harmonization Comparison
**Survey:** CASEN (Encuesta de Caracterización Socioeconómica Nacional)  
**Waves:** 2017a · 2020a · 2022a · 2024a  
**Date:** 2026-04-16

---

## HDMF target variables

| Variable | Definition | Domain |
|---|---|---|
| `formal_ci` | 1 = formal worker; 0 = informal worker | Employed (emp_ci==1) |
| `cotizando_ci` | 1 = contributes to pension/AFP | Employed |
| `afiliado_ci` | 1 = affiliated to health insurance | Employed |
| `tipocontrato_ci` | 1=indefinite · 2=fixed-term · 3=no written contract | Employed, wage workers |

**Rule:** `formal_ci = 1` if `cotizando_ci == 1` OR `afiliado_ci == 1`

---

## Source variables by wave

| HDMF variable | 2017a | 2020a | 2022a | 2024a |
|---|---|---|---|---|
| `cotizando_ci` | `o29` | `o32` | `o32` | `o32` |
| `afiliado_ci` | `o28` | `o31` | `o31` | `o31` |
| `tipocontrato_ci` | `o18` / `o19` | **not collected** | `o18` / `o19` | `o18` / `o19` + `categopri_ci` |

---

## Wave-by-wave construction detail

### 2017a
Source variables renamed between 2017 and 2022/2024 — the variable content is identical but the names differ.

```stata
* cotizando_ci — o29 (pension contribution, 2017 name for what is o32 in later waves)
* Codes: 1–5 = contributes to AFP/pension; 6 = does not contribute
cotizando_ci = 1  if o29 >= 1 & o29 <= 5 & emp_ci == 1
cotizando_ci = 0  if o29 == 6 & emp_ci == 1

* afiliado_ci — o28 (health affiliation, 2017 name for what is o31 in later waves)
* Code: 1 = affiliated; other = not affiliated
afiliado_ci = 1   if o28 == 1 & emp_ci == 1
afiliado_ci = 0   if o28 != 1 & !missing(o28) & emp_ci == 1

* formal_ci
formal_ci = 1     if (cotizando_ci == 1 | afiliado_ci == 1) & emp_ci == 1
formal_ci = 0     if (cotizando_ci == 0 & afiliado_ci == 0) & emp_ci == 1

* tipocontrato_ci — o18/o19 present (same as 2022/2024)
tipocontrato_ci = 1   if o18 == 1                        /* indefinido */
tipocontrato_ci = 2   if inlist(o18, 2, 3, 4, 5)         /* plazo fijo / otro escrito */
tipocontrato_ci = 3   if o19 == 2                        /* sin contrato escrito */
```

**Comparability with 2022/2024:** ✅ Fully comparable. Variable content and codes are identical; only the source variable names differ (`o28`→`o31`, `o29`→`o32`).

---

### 2020a ⚠️ COVID round
The 2020 CASEN was conducted during the pandemic (Nov 2020–Feb 2021). The contract module was removed from the questionnaire.

```stata
* cotizando_ci — o32 present (same name as 2022/2024)
cotizando_ci = 1  if o32 >= 1 & o32 <= 5 & emp_ci == 1
cotizando_ci = 0  if o32 == 6 & emp_ci == 1

* afiliado_ci — o31 present (same name as 2022/2024)
afiliado_ci = 1   if o31 == 1 & emp_ci == 1
afiliado_ci = 0   if o31 != 1 & !missing(o31) & emp_ci == 1

* formal_ci — same rule
formal_ci = 1     if (cotizando_ci == 1 | afiliado_ci == 1) & emp_ci == 1
formal_ci = 0     if (cotizando_ci == 0 & afiliado_ci == 0) & emp_ci == 1

* tipocontrato_ci — NOT COLLECTED in 2020
tipocontrato_ci = .   /* o18 and o19 absent from COVID questionnaire */
```

**Comparability with 2022/2024:** ✅ `formal_ci`, `cotizando_ci`, `afiliado_ci` fully comparable. ❌ `tipocontrato_ci` = missing for all 2020 observations — cannot be used for trend analysis including 2020.

---

### 2022a
```stata
* cotizando_ci — o32
cotizando_ci = 1  if o32 >= 1 & o32 <= 5 & emp_ci == 1
cotizando_ci = 0  if o32 == 6 & emp_ci == 1

* afiliado_ci — o31
afiliado_ci = 1   if o31 == 1 & emp_ci == 1
afiliado_ci = 0   if o31 != 1 & !missing(o31) & emp_ci == 1

* formal_ci
formal_ci = 1     if (cotizando_ci == 1 | afiliado_ci == 1) & emp_ci == 1
formal_ci = 0     if (cotizando_ci == 0 & afiliado_ci == 0) & emp_ci == 1

* tipocontrato_ci — o18/o19 (same as 2017/2024)
tipocontrato_ci = 1   if o18 == 1                        /* indefinido */
tipocontrato_ci = 2   if inlist(o18, 2, 3, 4, 5)         /* plazo fijo / otro escrito */
tipocontrato_ci = 3   if o19 == 2                        /* sin contrato escrito */
```

**Comparability with 2024:** ✅ Fully comparable.

---

### 2024a (reference)
The 2024 reference script adds a `categopri_ci` filter for `tipocontrato_ci` (restricts to wage workers only) and uses `recode` for `cotizando_ci`/`afiliado_ci` instead of explicit `replace` — functionally equivalent.

```stata
* cotizando_ci — o32
cotizando_ci = 1  if o32 >= 1 & o32 <= 5
recode cotizando_ci . = 0  if condocup_ci == 1 | condocup_ci == 2

* afiliado_ci — o31
afiliado_ci = 1   if o31 == 1
recode afiliado_ci . = 0   /* applies to everyone */

* formal_ci
formal_ci = 1     if (cotizando_ci == 1 | afiliado_ci == 1) & condocup_ci == 1
formal_ci = 0     if (cotizando_ci == 0 & afiliado_ci == 0) & condocup_ci == 1

* tipocontrato_ci — o18/o19 + categopri_ci (wage workers only)
tipocontrato_ci = 1   if o18 == 1 & categopri_ci == 3
tipocontrato_ci = 2   if (o18 == 2 | o18 == 3) & categopri_ci == 3
tipocontrato_ci = 3   if (o19 == 3 | tipocontrato_ci == .) & categopri_ci == 3
```

**Note:** 2024 restricts `tipocontrato_ci` to `categopri_ci == 3` (salaried/wage workers). The 2017/2020/2022 scripts do not apply this filter. This may cause minor differences in the distribution of `tipocontrato_ci` across waves, but does not affect `formal_ci`.

---

## Comparability summary

| Variable | 2017a | 2020a | 2022a | 2024a | Cross-wave comparable? |
|---|---|---|---|---|---|
| `formal_ci` | ✅ | ✅ | ✅ | ✅ | ✅ Yes — same rule all waves |
| `cotizando_ci` | ✅ (`o29`) | ✅ (`o32`) | ✅ (`o32`) | ✅ (`o32`) | ✅ Yes — same codes, renamed variable in 2017 |
| `afiliado_ci` | ✅ (`o28`) | ✅ (`o31`) | ✅ (`o31`) | ✅ (`o31`) | ✅ Yes — same codes, renamed variable in 2017 |
| `tipocontrato_ci` | ✅ | ❌ missing | ✅ | ✅ | ⚠️ Partial — absent in 2020; 2024 adds `categopri_ci` filter |

---

## Known caveats

1. **2020 `tipocontrato_ci` missing**: Not collected during the COVID round. Any analysis using contract type must either drop 2020 or treat it as a structural break.

2. **2024 `tipocontrato_ci` wage-worker filter**: The reference script applies `categopri_ci == 3` (wage workers), which the earlier waves do not. If comparing contract type distributions across waves, either apply the same filter to 2017/2022 or note the definitional difference.

3. **2017 variable renaming**: `o28`/`o29` in 2017 are the same questionnaire items as `o31`/`o32` in 2020–2024. The content and codes are identical.

4. **`afiliado_ci` zero-filling in 2024**: The 2024 script uses `recode afiliado_ci . = 0` for the entire dataset (not restricted to employed), which means unemployed persons with health affiliation get `afiliado_ci = 1`. The 2017/2020/2022 scripts restrict to `emp_ci == 1`. This only affects `afiliado_ci` for non-employed persons and does not affect `formal_ci` (which is conditioned on `emp_ci == 1`).
