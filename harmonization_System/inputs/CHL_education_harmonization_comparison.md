# CHL — Education Variable Harmonization Comparison
**Survey:** CASEN (Encuesta de Caracterización Socioeconómica Nacional)  
**Waves:** 2017a · 2020a · 2022a · 2024a  
**Date:** 2026-04-16  
**Status:** ⚠️ ACTIVE ERRORS in 2017a, 2020a, 2022a — fix required

---

## HDMF target variables

| Variable | Definition |
|---|---|
| `aedu_ci` | Years of approved schooling (continuous, 0–22+) |
| `edu_hdmf` | 8-category education level (less-than-primary → postgrad) |

---

## Root cause of the problem

**The `e6a` variable in CASEN has 15–17 categories in ALL four waves.** The 2024 reference script correctly handles this structure. The 2017a, 2020a, and 2022a harmonization scripts I wrote used a **wrong 8-category mapping** — treating preschool codes as primary/secondary and treating primary school codes as university. This is a complete structural mismatch.

---

## True `e6a` structure (verified from raw data — same in all four waves)

| `e6a` | Level | Education system | `e6b` range (2022) | Base years for `aedu_ci` |
|---|---|---|---|---|
| 1 | Nunca asistió / sin educación | — | no `e6b` | 0 |
| 2 | Sala cuna / jardín | Pre-school | no `e6b` | 0 |
| 3 | Pre-kínder | Pre-school | no `e6b` | 0 |
| 4 | Kínder | Pre-school | no `e6b` | 0 |
| 5 | Educación especial | Special | no `e6b` | missing |
| 6 | Preparatoria / primaria antigua | Old primary (max 6 yrs) | 1–6 | 0 |
| 7 | **Básica moderna** | Modern basic (max 8 yrs) — **largest group ~50k** | 1–8 | 0 |
| 8 | Humanidades (sistema antiguo) | Old secondary humanist | 1–6 | 6 |
| 9 | **Media científico-humanista** | Modern secondary — **largest group ~52k** | 1–4 | 8 |
| 10 | Técnico profesional (sistema antiguo) | Old secondary vocational | 1–6 | 6 |
| 11 | Media técnico-profesional | Modern secondary vocational | 1–5 | 8 |
| 12 | Técnico superior (CFT/IP) | Post-secondary technical | 1–3 | 12 |
| 13 | Universitaria | University | 1–10 | 12 |
| 14 | Magíster / posgrado | Master's | 1–4 | 16 |
| 15 | Doctorado | Doctoral | 1–6 | 16 |
| 16 | *(2017/2020 only)* Post-título / diploma | Post-degree | 1–10 | 12\* |
| 17 | *(2017/2020 only)* Magíster/Doctorado (old code) | Postgrad (old code) | 1–10 | 12\* |

\* e6a 16,17 (2017/2020 only): in these waves, higher-education and postgrad categories are split differently. e6b for codes 16,17 can reach 10, which is inconsistent with the 2022/2024 postgrad base of 16. Using base 12 for these keeps `aedu_ci` capped near 22, matching the 2022/2024 range. Requires verification against the original questionnaire.

---

## What the wrong scripts assumed (2017a, 2020a, 2022a)

These scripts applied an imaginary 8-category mapping:

| Code in script | Intended meaning | Actual meaning in CASEN | Effect |
|---|---|---|---|
| `e6a==1` → 0 yrs | No education | Correct (no education) | ✅ OK |
| `e6a==2` → `e6b` | Primary | **Pre-school / sala cuna** (no e6b!) | ❌ NaN for all |
| `e6a==3,4` → `6+e6b` | Secondary | **Pre-kínder / kínder** (no e6b!) | ❌ NaN for all |
| `e6a==5,6` → `12+e6b` | Tech superior | **Special ed / old primary** | ❌ Tiny counts get wrong values |
| `e6a==7` → `12+e6b` | **University** | **Básica moderna (PRIMARY)** — 50k people | ❌ 12+e6b = 13–20 yrs WRONG |
| `e6a==8` → `17+e6b` | Postgrad | **Old secondary humanist** | ❌ 17+e6b = 18–23 yrs WRONG |
| `e6a==9–17` | *(not handled)* | Secondary, tech, university, postgrad | ❌ All NaN |

---

## Impact on output indicators (measured from cache)

### `aedu_ci` — years of education

| Wave | Total obs | Non-null | NaN rate | Mean (non-null) | Range | Expected mean |
|---|---|---|---|---|---|---|
| 2017a | 214,717 | 82,590 | **62%** | **15.2 yrs** | 0–23 | ~10–11 yrs |
| 2020a | 182,319 | 61,985 | **66%** | **15.3 yrs** | 0–23 | ~10–11 yrs |
| 2022a | 200,679 | 70,634 | **65%** | **14.8 yrs** | 0–23 | ~10–11 yrs |
| 2024a | 218,367 | 216,430 | **1%** | **10.2 yrs** ✅ | 0–22 | ~10 yrs ✅ |

**2017–2022 mean ~15 years is implausibly high** (would imply almost everyone has university education). The real mean for a country-wide Chilean sample should be around 10–11 years. The inflated mean comes from the biggest group (`e6a==7`, básica moderna, ~50k people) being assigned university-level years instead of primary.

### `edu_hdmf` — education category

| Wave | Cat 1 (none) | Cat 2 (pri-inc) | Cat 3 (pri-comp) | Cat 4 (sec-inc) | Cat 5 (sec-comp) | Cat 6 (tech) | Cat 7 (uni) | Cat 8 (postgrad) | NaN |
|---|---|---|---|---|---|---|---|---|---|
| 2017a | 11,812 | 1,055 | 97 | 8,541 | 173 | 23,862 | 48,568 | — | **120,609 (56%)** |
| 2020a | 8,073 | 466 | 394 | 5,916 | 1,088 | 19,688 | 35,935 | — | **110,759 (61%)** |
| 2022a | 8,263 | 783 | — | 6,676 | — | 22,341 | — | — | **162,616 (81%)** |
| 2024a | 15,126 | 26,365 | 9,697 | 48,469 | 76,085 | 13,986 | 24,580 | 2,237 | 1,822 (1%) ✅ |

2022 is the most broken: 81% missing, only 4 of 8 categories represented, no categories 3 (primary complete), 5 (secondary complete), 7 (university), or 8 (postgrad).

---

## Correct `aedu_ci` construction (same for all four waves)

This is the 2024 reference script logic, which should be applied to all waves:

```stata
* Replace missing codes first
replace e6b = . if e6b == -88   /* 2022/2024 missing code */
replace e6b = . if e6b == 99    /* 2017/2020 missing code */
replace e6a = . if e6a == 99    /* 2017 only */

gen aedu_ci = .

* No formal education / preschool (no e6b in these categories)
replace aedu_ci = 0 if inlist(e6a, 1, 2, 3, 4)

* Special education — not comparable to years-of-schooling scale
replace aedu_ci = . if e6a == 5

* Old primary (6-year system, base 0)
replace aedu_ci = e6b if e6a == 6

* Modern básica (8-year system, base 0)
replace aedu_ci = e6b if e6a == 7

* Old secondary — humanist and vocational (base 6 from old primary)
replace aedu_ci = e6b + 6 if inlist(e6a, 8, 10)

* Modern secondary — científico-humanista and técnico-profesional (base 8 from básica)
replace aedu_ci = e6b + 8 if inlist(e6a, 9, 11)

* Technical superior + university (base 12)
replace aedu_ci = e6b + 12 if inlist(e6a, 12, 13)

* Postgrad (base 16) — 2022/2024 codes
replace aedu_ci = e6b + 16 if inlist(e6a, 14, 15)

* --- 2017 and 2020 only: extra codes ---
* e6a 16/17 appear to be additional higher-ed / postgrad categories
* Using base 12 keeps aedu_ci <= 22, consistent with 2022/2024 range
* !! Requires verification against 2017/2020 CASEN questionnaire !!
replace aedu_ci = e6b + 12 if inlist(e6a, 16, 17)   /* 2017/2020 only */
```

**Expected output after fix:** mean ≈ 10–11 years, <2% missing, range 0–22, all four waves comparable.

---

## Correct `edu_hdmf` construction (same for all four waves)

The 2024 reference script logic is correct. The key mapping (simplified):

```stata
* 1. No formal education / preschool
replace edu_hdmf = 1 if inlist(e6a, 1, 2, 3, 4)

* 2. Primary incomplete
replace edu_hdmf = 2 if inlist(e6a, 6, 7) & e6c_completo == 2
replace edu_hdmf = 2 if inlist(e6a, 6, 7) & asiste == 1    /* attending */

* 3. Primary complete
replace edu_hdmf = 3 if inlist(e6a, 6, 7) & e6c_completo == 1 & asiste == 2

* 4. Secondary incomplete
replace edu_hdmf = 4 if inlist(e6a, 7) & inlist(e6b, 7, 8)   /* básica 7-8° */
replace edu_hdmf = 4 if inlist(e6a, 8, 9, 10, 11) & e6c_completo == 2
replace edu_hdmf = 4 if inlist(e6a, 8, 9, 10, 11) & asiste == 1

* 5. Secondary complete
replace edu_hdmf = 5 if inlist(e6a, 8, 9, 10, 11) & e6c_completo == 1 & asiste == 2
replace edu_hdmf = 5 if inlist(e6a, 12, 13, 14, 15) & (asiste == 1 | e6c_completo == 2)

* 6. Technical / tertiary (complete)
replace edu_hdmf = 6 if e6a == 12 & e6c_completo == 1 & asiste == 2

* 7. University (complete)
replace edu_hdmf = 7 if e6a == 13 & e6c_completo == 1 & asiste == 2
replace edu_hdmf = 7 if inlist(e6a, 14, 15) & (asiste == 1 | e6c_completo == 2)

* 8. Postgrad (complete)
replace edu_hdmf = 8 if inlist(e6a, 14, 15) & e6c_completo == 1 & asiste == 2

* --- 2017/2020 only ---
* e6a 16,17 → treat as postgrad (category 8 if complete, 7 if not)
replace edu_hdmf = 7 if inlist(e6a, 16, 17) & (asiste == 1 | e6c_completo == 2)   /* 2017/2020 */
replace edu_hdmf = 8 if inlist(e6a, 16, 17) & e6c_completo == 1 & asiste == 2       /* 2017/2020 */
```

**Note for 2020:** `e6c_completo` was absent (COVID wave). Use `e2` (currently attending) as the attendance proxy. Categories 7 and 8 cannot be reliably distinguished without `e6c_completo`. In 2020, collapse both into category 7 (same caveat as the formality COVID limitation).

---

## Wave-by-wave compatibility of `e6c_completo` and `asiste`

| Variable | 2017a | 2020a | 2022a | 2024a |
|---|---|---|---|---|
| `e6c_completo` (HE completion flag) | ❌ absent | ❌ absent (COVID) | ✅ present | ✅ present |
| `asiste` (currently attending) | ✅ present | ✅ `e2` as proxy | ✅ present | ✅ present |

For 2017: `e6c_completo` is absent. Use `asiste` alone to approximate complete/incomplete (same limitation as 2020). Cannot distinguish edu_hdmf 7 vs 8.

---

## Comparability summary

| Variable | 2017a | 2020a | 2022a | 2024a | Cross-wave comparable? |
|---|---|---|---|---|---|
| `aedu_ci` (current) | ❌ WRONG — 62% NaN, mean=15 | ❌ WRONG — 66% NaN, mean=15 | ❌ WRONG — 65% NaN, mean=15 | ✅ mean=10, 1% NaN | No — scripts need fix |
| `aedu_ci` (after fix) | ✅ | ✅ | ✅ | ✅ | Yes — same e6a structure all waves |
| `edu_hdmf` (current) | ❌ WRONG — 56% NaN, missing categories | ❌ WRONG — 61% NaN | ❌ WRONG — 81% NaN, 4 of 8 cats | ✅ | No — scripts need fix |
| `edu_hdmf` (after fix) | ⚠️ cats 7/8 collapsed (no `e6c_completo`) | ⚠️ cats 7/8 collapsed (COVID) | ✅ | ✅ | Partial — 2017/2020 cannot distinguish uni-complete vs postgrad |

---

## Fix required

Apply to: `do armo/chl/CHL_2017a_variablesBID.do`, `CHL_2020a_variablesBID.do`, `CHL_2022a_variablesBID.do`

Replace the entire `aedu_ci` and `edu_hdmf` blocks in each script with the 2024-compatible construction shown above. After the fix, rebuild the cache and rerun trends.

**Re-run plan after fix:**
```
1. Stata: CHL_2017a_variablesBID.do
2. Stata: CHL_2020a_variablesBID.do
3. Stata: CHL_2022a_variablesBID.do
4. py hdmf_build.py --countries CHL
5. py hdmf_trends.py --country CHL
6. py hdmf_trends_charts.py --country CHL
```
