# Dictionary Check: COL_GEIH (2018t3 – 2025t3)
Date: 2026-05-01
Tool: `harmonization_System/inputs/dictionary_check.py`
Waves checked: 2018t3, 2019t3, 2020t3, 2021t3, 2022t3, 2023t3, 2024t3, 2025t3

---

## Variable existence matrix

| Variable | Domain | 2018t3 | 2019t3 | 2020t3 | 2021t3 | 2022t3 | 2023t3 | 2024t3 | 2025t3 |
|----------|--------|---|---|---|---|---|---|---|---|
| `idh` | IDs & weights | ✅ str | ✅ str | ✅ str | ✅ str | ✅ str | ✅ str | ✅ str | ✅ str |
| `orden` | IDs & weights | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 |
| `fex_c18` | IDs & weights | ❌ | ❌ | ❌ | ❌ | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 |
| `fex_c_2011` | IDs & weights | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ❌ | ❌ | ❌ | ❌ |
| `fex_c` | IDs & weights | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ❌ |
| `fex` | IDs & weights | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `p6050` | Demographics | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 |
| `p6040` | Demographics | ✅ int64 | ✅ int64 | ✅ object | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 |
| `p6020` | Demographics | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ❌ | ❌ | ❌ | ❌ |
| `p3016` | Demographics | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `oci` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `dsi` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `fft` | Employment | ❌ | ❌ | ❌ | ❌ | ✅ object | ✅ object | ✅ object | ✅ object |
| `ini` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ❌ | ❌ | ❌ | ❌ |
| `p6800` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p7045` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p6920` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p6090` | Employment | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 |
| `p6460` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p6450` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p6440` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p7450` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p6240` | Employment | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |
| `p3042` | Education | ❌ | ❌ | ❌ | ❌ | ✅ object | ✅ object | ✅ object | ✅ object |
| `p3042s1` | Education | ❌ | ❌ | ❌ | ❌ | ✅ object | ✅ object | ✅ object | ✅ object |
| `p3042s2` | Education | ❌ | ❌ | ❌ | ❌ | ✅ object | ✅ object | ✅ object | ✅ object |
| `p3043` | Education | ❌ | ❌ | ❌ | ❌ | ✅ object | ✅ object | ✅ object | ✅ object |
| `p6210` | Education | ✅ object | ✅ object | ✅ object | ✅ object | ❌ | ❌ | ❌ | ❌ |
| `p6210s1` | Education | ✅ object | ✅ object | ✅ object | ✅ object | ❌ | ❌ | ❌ | ❌ |
| `p6220` | Education | ✅ object | ✅ object | ✅ object | ✅ object | ❌ | ❌ | ❌ | ❌ |
| `p3373` | Migration | ❌ | ❌ | ❌ | ❌ | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 |
| `p3373s3` | Migration | ❌ | ❌ | ❌ | ❌ | ✅ object | ✅ object | ✅ str | ✅ str |
| `p3382` | Migration | ❌ | ❌ | ❌ | ❌ | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 |
| `p6074` | Migration | ✅ int64 | ✅ int64 | ✅ int64 | ✅ int64 | ❌ | ❌ | ❌ | ❌ |
| `p756` | Migration | ✅ int64 | ✅ int64 | ✅ object | ✅ int64 | ❌ | ❌ | ❌ | ❌ |
| `p755` | Migration | ✅ int64 | ✅ int64 | ✅ object | ✅ int64 | ❌ | ❌ | ❌ | ❌ |
| `impa` | Income | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ❌ |
| `impaes` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `isa` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `isaes` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `imdi` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `imdies` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `ie` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iees` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iof1` | Income | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ❌ |
| `iof2` | Income | ✅ object | ✅ object | ✅ float64 | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iof3h` | Income | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ❌ |
| `iof3i` | Income | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ✅ float64 | ❌ |
| `iof6` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iof1es` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iof2es` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iof3hes` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iof3ies` | Income | ✅ object | ✅ object | ✅ float64 | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `iof6es` | Income | ✅ object | ✅ object | ✅ object | ✅ float64 | ✅ object | ✅ object | ✅ object | ❌ |
| `p7510s2a1` | Income | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object | ✅ object |

## Expansion factor summary

| Wave | N obs | Weight var | Sum | Min | Max |
|------|-------|-----------|-----|-----|-----|
| 2018t3 | 191,041 | `fex_c_2011` | 48,455,854 | 8.780 | 3620.709 |
| 2019t3 | 189,650 | `fex_c_2011` | 48,975,426 | 4.661 | 3620.360 |
| 2020t3 | 190,268 | `fex_c_2011` | 49,491,969 | 2.280 | 4184.013 |
| 2021t3 | 176,532 | `fex_c_2011` | 50,008,962 | 8.639 | 3630.062 |
| 2022t3 | 227,970 | `fex_c18` | 50,559,093 | 2.745 | 5897.404 |
| 2023t3 | 215,059 | `fex_c18` | 51,092,907 | 2.607 | 4327.963 |
| 2024t3 | 207,425 | `fex_c18` | 51,614,439 | 4.035 | 4412.616 |
| 2025t3 | 205,276 | `fex_c18` | 17,375,445 | 1.012 | 1813.876 |

## Categorical variable checks

### `p6050`

**2018t3**

| Value | Label | N | % |
|---|---|---|---|
| 3 | Hijo(a), hijastro(a) | 67,083 | 35.1% |
| 1 | Jefe (a) del hogar | 58,243 | 30.5% |
| 2 | Pareja, esposo(a), cónyuge, compañero(a) | 30,893 | 16.2% |
| 5 | Otro  pariente | 15,850 | 8.3% |
| 4 | Nieto(a) | 14,580 | 7.6% |
| 9 | Otro no pariente | 3,625 | 1.9% |
| 6 | Empleado(a) del servicio  doméstico y sus parientes | 547 | 0.3% |
| 7 | Pensionista | 156 | 0.1% |
| 8 | Trabajador | 64 | 0.0% |

**2019t3**

| Value | Label | N | % |
|---|---|---|---|
| 3 | Hijo(a), hijastro(a) | 66,221 | 34.9% |
| 1 | Jefe (a) del hogar | 58,619 | 30.9% |
| 2 | Pareja, esposo(a), cónyuge, compañero(a) | 30,826 | 16.3% |
| 5 | Otro  pariente | 15,851 | 8.4% |
| 4 | Nieto(a) | 13,970 | 7.4% |
| 9 | Otro no pariente | 3,499 | 1.8% |
| 6 | Empleado(a) del servicio  doméstico y sus parientes | 484 | 0.3% |
| 7 | Pensionista | 128 | 0.1% |
| 8 | Trabajador | 52 | 0.0% |

**2020t3**

| Value | Label | N | % |
|---|---|---|---|
| 3 | Hijo(a), hijastro(a) | 67,082 | 35.3% |
| 1 | Jefe (a) del hogar | 58,420 | 30.7% |
| 2 | Pareja, esposo(a), cónyuge, compañero(a) | 31,193 | 16.4% |
| 5 | Otro  pariente | 16,870 | 8.9% |
| 4 | Nieto(a) | 13,551 | 7.1% |
| 9 | Otro no pariente | 2,696 | 1.4% |
| 6 | Empleado(a) del servicio  doméstico y sus parientes | 385 | 0.2% |
| 8 | Trabajador | 43 | 0.0% |
| 7 | Pensionista | 28 | 0.0% |

**2021t3**

| Value | Label | N | % |
|---|---|---|---|
| 3 |  | 61,494 | 34.8% |
| 1 |  | 56,646 | 32.1% |
| 2 |  | 28,732 | 16.3% |
| 5 |  | 14,389 | 8.2% |
| 4 |  | 12,438 | 7.0% |
| 9 |  | 2,393 | 1.4% |
| 6 |  | 370 | 0.2% |
| 7 |  | 39 | 0.0% |
| 8 |  | 31 | 0.0% |

**2022t3**

| Value | Label | N | % |
|---|---|---|---|
| 3 |  | 79,448 | 34.9% |
| 1 |  | 75,954 | 33.3% |
| 2 |  | 37,869 | 16.6% |
| 8 |  | 14,030 | 6.2% |
| 9 |  | 5,885 | 2.6% |
| 6 |  | 4,275 | 1.9% |
| 4 |  | 3,684 | 1.6% |
| 13 |  | 2,586 | 1.1% |
| 7 |  | 2,570 | 1.1% |
| 5 |  | 1,081 | 0.5% |
| 10 |  | 469 | 0.2% |
| 11 |  | 92 | 0.0% |
| 12 |  | 27 | 0.0% |

**2023t3**

| Value | Label | N | % |
|---|---|---|---|
| 3 |  | 73,734 | 34.3% |
| 1 |  | 73,459 | 34.2% |
| 2 |  | 35,675 | 16.6% |
| 8 |  | 13,063 | 6.1% |
| 9 |  | 5,426 | 2.5% |
| 6 |  | 3,995 | 1.9% |
| 4 |  | 3,454 | 1.6% |
| 13 |  | 2,413 | 1.1% |
| 7 |  | 2,271 | 1.1% |
| 5 |  | 985 | 0.5% |
| 10 |  | 493 | 0.2% |
| 11 |  | 62 | 0.0% |
| 12 |  | 29 | 0.0% |

**2024t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 72,962 | 35.2% |
| 3 |  | 69,606 | 33.6% |
| 2 |  | 34,309 | 16.5% |
| 8 |  | 12,539 | 6.0% |
| 9 |  | 4,892 | 2.4% |
| 6 |  | 3,929 | 1.9% |
| 4 |  | 3,486 | 1.7% |
| 13 |  | 2,257 | 1.1% |
| 7 |  | 2,147 | 1.0% |
| 5 |  | 869 | 0.4% |
| 10 |  | 359 | 0.2% |
| 11 |  | 44 | 0.0% |
| 12 |  | 26 | 0.0% |

**2025t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 73,679 | 35.9% |
| 3 |  | 67,883 | 33.1% |
| 2 |  | 34,617 | 16.9% |
| 8 |  | 11,971 | 5.8% |
| 9 |  | 4,599 | 2.2% |
| 6 |  | 3,774 | 1.8% |
| 4 |  | 3,425 | 1.7% |
| 13 |  | 2,071 | 1.0% |
| 7 |  | 1,976 | 1.0% |
| 5 |  | 897 | 0.4% |
| 10 |  | 305 | 0.1% |
| 11 |  | 52 | 0.0% |
| 12 |  | 27 | 0.0% |

### `p3042`

**2022t3**

| Value | Label | N | % |
|---|---|---|---|
| 3.0 |  | 55,610 | 24.4% |
| 5.0 |  | 51,015 | 22.4% |
| 4.0 |  | 35,668 | 15.6% |
| 10.0 |  | 27,512 | 12.1% |
| 8.0 |  | 14,423 | 6.3% |
| 1.0 |  | 13,189 | 5.8% |
| nan |  | 8,245 | 3.6% |
| 2.0 |  | 6,160 | 2.7% |
| 9.0 |  | 5,842 | 2.6% |
| 11.0 |  | 4,356 | 1.9% |
| 6.0 |  | 3,716 | 1.6% |
| 12.0 |  | 1,641 | 0.7% |
| 7.0 |  | 359 | 0.2% |
| 13.0 |  | 226 | 0.1% |
| 99.0 |  | 8 | 0.0% |

**2023t3**

| Value | Label | N | % |
|---|---|---|---|
| 3.0 |  | 52,023 | 24.2% |
| 5.0 |  | 49,568 | 23.0% |
| 4.0 |  | 33,167 | 15.4% |
| 10.0 |  | 26,308 | 12.2% |
| 8.0 |  | 13,460 | 6.3% |
| 1.0 |  | 11,277 | 5.2% |
| nan |  | 7,373 | 3.4% |
| 2.0 |  | 5,771 | 2.7% |
| 9.0 |  | 5,579 | 2.6% |
| 11.0 |  | 4,401 | 2.0% |
| 6.0 |  | 3,678 | 1.7% |
| 12.0 |  | 1,846 | 0.9% |
| 7.0 |  | 377 | 0.2% |
| 13.0 |  | 225 | 0.1% |
| 99.0 |  | 6 | 0.0% |

**2024t3**

| Value | Label | N | % |
|---|---|---|---|
| 3.0 |  | 49,886 | 24.1% |
| 5.0 |  | 48,737 | 23.5% |
| 4.0 |  | 30,956 | 14.9% |
| 10.0 |  | 26,028 | 12.5% |
| 8.0 |  | 12,895 | 6.2% |
| 1.0 |  | 10,925 | 5.3% |
| nan |  | 6,454 | 3.1% |
| 9.0 |  | 5,727 | 2.8% |
| 2.0 |  | 5,282 | 2.5% |
| 11.0 |  | 4,422 | 2.1% |
| 6.0 |  | 3,624 | 1.7% |
| 12.0 |  | 1,866 | 0.9% |
| 7.0 |  | 355 | 0.2% |
| 13.0 |  | 256 | 0.1% |
| 99.0 |  | 12 | 0.0% |

**2025t3**

| Value | Label | N | % |
|---|---|---|---|
| 3.0 |  | 49,483 | 24.1% |
| 5.0 |  | 48,924 | 23.8% |
| 4.0 |  | 29,963 | 14.6% |
| 10.0 |  | 25,719 | 12.5% |
| 8.0 |  | 13,413 | 6.5% |
| 1.0 |  | 10,266 | 5.0% |
| 9.0 |  | 5,954 | 2.9% |
| nan |  | 5,941 | 2.9% |
| 2.0 |  | 5,170 | 2.5% |
| 11.0 |  | 4,206 | 2.0% |
| 6.0 |  | 3,873 | 1.9% |
| 12.0 |  | 1,811 | 0.9% |
| 7.0 |  | 296 | 0.1% |
| 13.0 |  | 257 | 0.1% |

### `p3373`

**2022t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 130,780 | 57.4% |
| 2 |  | 85,953 | 37.7% |
| 3 |  | 11,237 | 4.9% |

**2023t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 121,871 | 56.7% |
| 2 |  | 83,389 | 38.8% |
| 3 |  | 9,799 | 4.6% |

**2024t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 117,257 | 56.5% |
| 2 |  | 81,176 | 39.1% |
| 3 |  | 8,992 | 4.3% |

**2025t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 117,012 | 57.0% |
| 2 |  | 79,915 | 38.9% |
| 3 |  | 8,349 | 4.1% |

### `p3382`

**2022t3**

| Value | Label | N | % |
|---|---|---|---|
| 2 |  | 188,935 | 82.9% |
| 3 |  | 17,191 | 7.5% |
| 1 |  | 13,794 | 6.1% |
| 4 |  | 8,050 | 3.5% |

**2023t3**

| Value | Label | N | % |
|---|---|---|---|
| 2 |  | 180,969 | 84.1% |
| 3 |  | 16,538 | 7.7% |
| 1 |  | 12,378 | 5.8% |
| 4 |  | 5,174 | 2.4% |

**2024t3**

| Value | Label | N | % |
|---|---|---|---|
| 2 |  | 176,724 | 85.2% |
| 3 |  | 16,014 | 7.7% |
| 1 |  | 11,140 | 5.4% |
| 4 |  | 3,547 | 1.7% |

**2025t3**

| Value | Label | N | % |
|---|---|---|---|
| 2 |  | 177,042 | 86.2% |
| 3 |  | 15,110 | 7.4% |
| 1 |  | 10,567 | 5.1% |
| 4 |  | 2,557 | 1.2% |

### `p6920`

**2018t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 103,865 | 54.4% |
| 2.0 | No | 52,320 | 27.4% |
| 1.0 | Sí | 33,264 | 17.4% |
| 3.0 | Ya es pensionado | 1,592 | 0.8% |

**2019t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 105,343 | 55.5% |
| 2.0 | No | 49,680 | 26.2% |
| 1.0 | Sí | 33,057 | 17.4% |
| 3.0 | Ya es pensionado | 1,570 | 0.8% |

**2020t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 119,708 | 62.9% |
| 2.0 | No | 40,758 | 21.4% |
| 1.0 | Sí | 28,667 | 15.1% |
| 3.0 | Ya es pensionado | 1,135 | 0.6% |

**2021t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 103,009 | 58.4% |
| 2.0 |  | 44,635 | 25.3% |
| 1.0 |  | 27,753 | 15.7% |
| 3.0 |  | 1,135 | 0.6% |

**2022t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 132,752 | 58.2% |
| 2.0 |  | 54,962 | 24.1% |
| 1.0 |  | 38,858 | 17.0% |
| 3.0 |  | 1,398 | 0.6% |

**2023t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 122,369 | 56.9% |
| 2.0 |  | 52,782 | 24.5% |
| 1.0 |  | 38,402 | 17.9% |
| 3.0 |  | 1,506 | 0.7% |

**2024t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 118,162 | 57.0% |
| 2.0 |  | 49,972 | 24.1% |
| 1.0 |  | 37,767 | 18.2% |
| 3.0 |  | 1,524 | 0.7% |

**2025t3**

| Value | Label | N | % |
|---|---|---|---|
| nan |  | 114,780 | 55.9% |
| 2.0 |  | 50,328 | 24.5% |
| 1.0 |  | 38,573 | 18.8% |
| 3.0 |  | 1,595 | 0.8% |

### `p6090`

**2018t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 | Sí | 177,792 | 93.1% |
| 2 | No | 13,140 | 6.9% |
| 9 | No sabe, no informa | 109 | 0.1% |

**2019t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 | Sí | 175,228 | 92.4% |
| 2 | No | 14,328 | 7.6% |
| 9 | No sabe, no informa | 94 | 0.0% |

**2020t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 | Sí | 173,888 | 91.4% |
| 2 | No | 16,101 | 8.5% |
| 9 | No sabe, no informa | 279 | 0.1% |

**2021t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 163,533 | 92.6% |
| 2 |  | 12,854 | 7.3% |
| 9 |  | 145 | 0.1% |

**2022t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 215,274 | 94.4% |
| 2 |  | 12,473 | 5.5% |
| 9 |  | 223 | 0.1% |

**2023t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 205,724 | 95.7% |
| 2 |  | 9,200 | 4.3% |
| 9 |  | 135 | 0.1% |

**2024t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 199,415 | 96.1% |
| 2 |  | 7,807 | 3.8% |
| 9 |  | 203 | 0.1% |

**2025t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 199,127 | 97.0% |
| 2 |  | 6,082 | 3.0% |
| 9 |  | 67 | 0.0% |

### `p6074`

**2018t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 | Si | 98,943 | 51.8% |
| 2 | No | 92,098 | 48.2% |

**2019t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 | Si | 96,609 | 50.9% |
| 2 | No | 93,041 | 49.1% |

**2020t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 | Si | 127,076 | 66.8% |
| 2 | No | 63,192 | 33.2% |

**2021t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 | Si | 96,129 | 54.5% |
| 2 | No | 80,403 | 45.5% |

### `p756`

**2018t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 107,953 | 56.5% |
| 2 |  | 77,655 | 40.6% |
| 3 |  | 5,433 | 2.8% |

**2019t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 106,042 | 55.9% |
| 2 |  | 75,719 | 39.9% |
| 3 |  | 7,889 | 4.2% |

**2020t3**

| Value | Label | N | % |
|---|---|---|---|
| 1.0 |  | 108,939 | 57.3% |
| 2.0 |  | 72,219 | 38.0% |
| 3.0 |  | 9,109 | 4.8% |
| nan |  | 1 | 0.0% |

**2021t3**

| Value | Label | N | % |
|---|---|---|---|
| 1 |  | 101,801 | 57.7% |
| 2 |  | 65,263 | 37.0% |
| 3 |  | 9,468 | 5.4% |

### `p755`

**2018t3**

| Value | Label | N | % |
|---|---|---|---|
| 2 | En este municipio | 153,291 | 80.2% |
| 3 | En otro municipio | 18,220 | 9.5% |
| 1 | No había nacido | 13,356 | 7.0% |
| 4 |  | 6,174 | 3.2% |

**2019t3**

| Value | Label | N | % |
|---|---|---|---|
| 2 | En este municipio | 151,287 | 79.8% |
| 3 | En otro municipio | 17,267 | 9.1% |
| 1 | No había nacido | 12,939 | 6.8% |
| 4 |  | 8,157 | 4.3% |

**2020t3**

| Value | Label | N | % |
|---|---|---|---|
| 2.0 | En este municipio | 156,500 | 82.3% |
| 3.0 | En otro municipio | 13,203 | 6.9% |
| 1.0 | No había nacido | 12,021 | 6.3% |
| 4.0 | En otro país | 8,536 | 4.5% |
| nan |  | 8 | 0.0% |

**2021t3**

| Value | Label | N | % |
|---|---|---|---|
| 2 | En este municipio | 144,747 | 82.0% |
| 3 | En otro municipio | 12,810 | 7.3% |
| 1 | No había nacido | 10,872 | 6.2% |
| 4 | En otro país | 8,103 | 4.6% |

### `p6210`

**2018t3**

| Value | Label | N | % |
|---|---|---|---|
| 3.0 | Básica primaria (1o - 5o) | 47,429 | 24.8% |
| 6.0 | Superior o universitaria | 45,224 | 23.7% |
| 5.0 | Media (10o - 13o) | 41,839 | 21.9% |
| 4.0 | Básica secundaria (6o - 9o) | 32,957 | 17.3% |
| 1.0 | Ninguno | 10,100 | 5.3% |
| nan |  | 7,868 | 4.1% |
| 2.0 | Preescolar | 5,594 | 2.9% |
| 9.0 | No sabe, no informa | 30 | 0.0% |

**2019t3**

| Value | Label | N | % |
|---|---|---|---|
| 3.0 | Básica primaria (1o - 5o) | 45,497 | 24.0% |
| 6.0 | Superior o universitaria | 45,411 | 23.9% |
| 5.0 | Media (10o - 13o) | 43,350 | 22.9% |
| 4.0 | Básica secundaria (6o - 9o) | 32,398 | 17.1% |
| 1.0 | Ninguno | 9,946 | 5.2% |
| nan |  | 7,548 | 4.0% |
| 2.0 | Preescolar | 5,485 | 2.9% |
| 9.0 | No sabe, no informa | 15 | 0.0% |

**2020t3**

| Value | Label | N | % |
|---|---|---|---|
| 6.0 | Superior o universitaria | 45,802 | 24.1% |
| 3.0 | Básica primaria (1o - 5o) | 45,602 | 24.0% |
| 5.0 | Media (10o - 13o) | 44,927 | 23.6% |
| 4.0 | Básica secundaria (6o - 9o) | 31,945 | 16.8% |
| 1.0 | Ninguno | 10,217 | 5.4% |
| nan |  | 7,090 | 3.7% |
| 2.0 | Preescolar | 4,672 | 2.5% |
| 9.0 | No sabe, no informa | 13 | 0.0% |

**2021t3**

| Value | Label | N | % |
|---|---|---|---|
| 5.0 |  | 43,033 | 24.4% |
| 6.0 |  | 42,145 | 23.9% |
| 3.0 |  | 41,617 | 23.6% |
| 4.0 |  | 29,188 | 16.5% |
| 1.0 |  | 9,646 | 5.5% |
| nan |  | 6,447 | 3.7% |
| 2.0 |  | 4,432 | 2.5% |
| 9.0 |  | 24 | 0.0% |

## Alternative constructions found in reference package

### `fex_c18`

- **COL_2022t3_variablesBID.do** line 127: `g factor_ch=fex_c18`
- **COL_2022t3_variablesBID.do** line 174: `g factor_ci=fex_c18`
- **COL_2023t3_variablesBID.do** line 172: `g factor_ci=fex_c18`
- **COL_2023t3_variablesBID.do** line 178: `g factor_ch=fex_c18`
- **COL_2024t3_variablesBID.do** line 140: `g factor_ci=fex_c18`
- **COL_2024t3_variablesBID.do** line 145: `g factor_ch=fex_c18`

### `fex_c_2011`

- **COL_2018t3_variablesBID.do** line 85: `g factor_ch=fex_c_2011`
- **COL_2018t3_variablesBID.do** line 132: `g factor_ci=fex_c_2011`
- **COL_2019t3_variablesBID.do** line 85: `g factor_ch=fex_c_2011`
- **COL_2019t3_variablesBID.do** line 132: `g factor_ci=fex_c_2011`
- **COL_2020t3_variablesBID.do** line 88: `g factor_ch=fex_c_2011`
- **COL_2020t3_variablesBID.do** line 136: `g factor_ci=fex_c_2011`
- **COL_2021t3_variablesBID.do** line 125: `g factor_ch=fex_c_2011`
- **COL_2021t3_variablesBID.do** line 172: `g factor_ci=fex_c_2011`

### `fft`

- **COL_2022t3_variablesBID.do** line 444: `replace condocup_ci=3 if fft==1`
- **COL_2023t3_variablesBID.do** line 449: `replace condocup_ci=3 if fft==1`
- **COL_2024t3_variablesBID.do** line 387: `replace condocup_ci=3 if fft==1`

### `ie`

- **COL_2018t3_variablesBID.do** line 809: `egen ylnmpri_ci = rsum(ie iees), m`
- **COL_2018t3_variablesBID.do** line 810: `replace ylnmpri_ci=. if ie==. & iees==.`
- **COL_2018t3_variablesBID.do** line 811: `/*YL -> Nota: "ie" and "iees"corresponden al ingreso por especie de la act principal*/`
- **COL_2019t3_variablesBID.do** line 817: `egen ylnmpri_ci = rsum(ie iees), m`
- **COL_2019t3_variablesBID.do** line 818: `replace ylnmpri_ci=. if ie==. & iees==.`
- **COL_2019t3_variablesBID.do** line 819: `/*YL -> Nota: "ie" and "iees"corresponden al ingreso por especie de la act principal*/`
- **COL_2020t3_variablesBID.do** line 761: `egen ylnmpri_ci = rsum(ie iees), m`
- **COL_2020t3_variablesBID.do** line 762: `replace ylnmpri_ci=. if ie==. & iees==.`
- **COL_2020t3_variablesBID.do** line 763: `/*YL -> Nota: "ie" and "iees"corresponden al ingreso por especie de la act principal*/`
- **COL_2021t3_variablesBID.do** line 849: `egen ylnmpri_ci = rsum(ie iees), m`

### `iees`

- **COL_2018t3_variablesBID.do** line 809: `egen ylnmpri_ci = rsum(ie iees), m`
- **COL_2018t3_variablesBID.do** line 810: `replace ylnmpri_ci=. if ie==. & iees==.`
- **COL_2018t3_variablesBID.do** line 811: `/*YL -> Nota: "ie" and "iees"corresponden al ingreso por especie de la act principal*/`
- **COL_2019t3_variablesBID.do** line 817: `egen ylnmpri_ci = rsum(ie iees), m`
- **COL_2019t3_variablesBID.do** line 818: `replace ylnmpri_ci=. if ie==. & iees==.`
- **COL_2019t3_variablesBID.do** line 819: `/*YL -> Nota: "ie" and "iees"corresponden al ingreso por especie de la act principal*/`
- **COL_2020t3_variablesBID.do** line 761: `egen ylnmpri_ci = rsum(ie iees), m`
- **COL_2020t3_variablesBID.do** line 762: `replace ylnmpri_ci=. if ie==. & iees==.`
- **COL_2020t3_variablesBID.do** line 763: `/*YL -> Nota: "ie" and "iees"corresponden al ingreso por especie de la act principal*/`
- **COL_2021t3_variablesBID.do** line 849: `egen ylnmpri_ci = rsum(ie iees), m`

### `imdi`

- **COL_2018t3_variablesBID.do** line 830: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2019t3_variablesBID.do** line 838: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2020t3_variablesBID.do** line 782: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2021t3_variablesBID.do** line 870: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2022t3_variablesBID.do** line 885: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2023t3_variablesBID.do** line 893: `egen ylmotros_ci= rsum(imdi imdies), m`
- **COL_2024t3_variablesBID.do** line 637: `egen ylmotros_ci= rsum(imdi imdies), m`

### `imdies`

- **COL_2018t3_variablesBID.do** line 830: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2019t3_variablesBID.do** line 838: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2020t3_variablesBID.do** line 782: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2021t3_variablesBID.do** line 870: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2022t3_variablesBID.do** line 885: `egen ylmotros_ci= rowtotal(imdi imdies), m`
- **COL_2023t3_variablesBID.do** line 893: `egen ylmotros_ci= rsum(imdi imdies), m`
- **COL_2024t3_variablesBID.do** line 637: `egen ylmotros_ci= rsum(imdi imdies), m`

### `impa`

- **COL_2018t3_variablesBID.do** line 796: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2018t3_variablesBID.do** line 797: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2019t3_variablesBID.do** line 804: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2019t3_variablesBID.do** line 805: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2020t3_variablesBID.do** line 748: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2020t3_variablesBID.do** line 749: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2021t3_variablesBID.do** line 834: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2021t3_variablesBID.do** line 835: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2022t3_variablesBID.do** line 849: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2022t3_variablesBID.do** line 850: `replace ylmpri_ci = . if impa==. & impaes==.`

### `impaes`

- **COL_2018t3_variablesBID.do** line 796: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2018t3_variablesBID.do** line 797: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2019t3_variablesBID.do** line 804: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2019t3_variablesBID.do** line 805: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2020t3_variablesBID.do** line 748: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2020t3_variablesBID.do** line 749: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2021t3_variablesBID.do** line 834: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2021t3_variablesBID.do** line 835: `replace ylmpri_ci = . if impa==. & impaes==.`
- **COL_2022t3_variablesBID.do** line 849: `egen 	ylmpri_ci = rsum(impa impaes), m`
- **COL_2022t3_variablesBID.do** line 850: `replace ylmpri_ci = . if impa==. & impaes==.`

### `ini`

- **COL_2018t3_variablesBID.do** line 400: `replace condocup_ci=3 if ini==1`
- **COL_2019t3_variablesBID.do** line 408: `replace condocup_ci=3 if ini==1`
- **COL_2020t3_variablesBID.do** line 352: `replace condocup_ci=3 if ini==1`
- **COL_2021t3_variablesBID.do** line 433: `replace condocup_ci=3 if ini==1`

### `iof1`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `iof1es`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `iof2`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 748: `egen ypen_ci = rsum(iof2 iof2es), m`
- **COL_2024t3_variablesBID.do** line 753: `egen ypensub_ci = rsum(iof2 iof2es) if pensionsub_ci==1, m`

### `iof2es`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 748: `egen ypen_ci = rsum(iof2 iof2es), m`
- **COL_2024t3_variablesBID.do** line 753: `egen ypensub_ci = rsum(iof2 iof2es) if pensionsub_ci==1, m`

### `iof3h`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `iof3hes`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `iof3i`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `iof3ies`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `iof6`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `iof6es`

- **COL_2018t3_variablesBID.do** line 855: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2019t3_variablesBID.do** line 863: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2020t3_variablesBID.do** line 807: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2021t3_variablesBID.do** line 895: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2022t3_variablesBID.do** line 910: `egen ynlm_ci = rowtotal(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2023t3_variablesBID.do** line 921: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`
- **COL_2024t3_variablesBID.do** line 675: `egen ynlm_ci = rsum(iof1 iof2  iof3h iof3i iof6 iof1es iof2es  iof3hes iof3ies iof6es), m`

### `isa`

- **COL_2018t3_variablesBID.do** line 817: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2018t3_variablesBID.do** line 818: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2019t3_variablesBID.do** line 825: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2019t3_variablesBID.do** line 826: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2020t3_variablesBID.do** line 769: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2020t3_variablesBID.do** line 770: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2021t3_variablesBID.do** line 857: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2021t3_variablesBID.do** line 858: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2022t3_variablesBID.do** line 872: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2022t3_variablesBID.do** line 873: `replace ylmsec_ci=. if isa==. & isaes==.`

### `isaes`

- **COL_2018t3_variablesBID.do** line 817: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2018t3_variablesBID.do** line 818: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2019t3_variablesBID.do** line 825: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2019t3_variablesBID.do** line 826: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2020t3_variablesBID.do** line 769: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2020t3_variablesBID.do** line 770: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2021t3_variablesBID.do** line 857: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2021t3_variablesBID.do** line 858: `replace ylmsec_ci=. if isa==. & isaes==.`
- **COL_2022t3_variablesBID.do** line 872: `egen ylmsec_ci = rsum(isa isaes), m`
- **COL_2022t3_variablesBID.do** line 873: `replace ylmsec_ci=. if isa==. & isaes==.`

### `p3042`

- **COL_2022t3_variablesBID.do** line 1022: `replace aedu_ci = 0 if p3042 == 1 | p3042 == 2`
- **COL_2022t3_variablesBID.do** line 1023: `replace aedu_ci = 0 if p3042 == 3 & p3042s1 == 0`
- **COL_2022t3_variablesBID.do** line 1025: `replace aedu_ci = 1 if p3042 == 3 & p3042s1 == 1`
- **COL_2022t3_variablesBID.do** line 1026: `replace aedu_ci = 2 if p3042 == 3 & p3042s1 == 2`
- **COL_2022t3_variablesBID.do** line 1027: `replace aedu_ci = 3 if p3042 == 3 & p3042s1 == 3`
- **COL_2022t3_variablesBID.do** line 1028: `replace aedu_ci = 4 if p3042 == 3 & p3042s1 == 4`
- **COL_2022t3_variablesBID.do** line 1029: `replace aedu_ci = 5 if p3042 == 3 & p3042s1 == 5`
- **COL_2022t3_variablesBID.do** line 1030: `replace aedu_ci = 5 if p3042 == 4 & p3042s1 == 0`
- **COL_2022t3_variablesBID.do** line 1032: `replace aedu_ci = 6  if p3042 == 4 & p3042s1 == 1`
- **COL_2022t3_variablesBID.do** line 1033: `replace aedu_ci = 7  if p3042 == 4 & p3042s1 == 2`

### `p3042s1`

- **COL_2022t3_variablesBID.do** line 1023: `replace aedu_ci = 0 if p3042 == 3 & p3042s1 == 0`
- **COL_2022t3_variablesBID.do** line 1025: `replace aedu_ci = 1 if p3042 == 3 & p3042s1 == 1`
- **COL_2022t3_variablesBID.do** line 1026: `replace aedu_ci = 2 if p3042 == 3 & p3042s1 == 2`
- **COL_2022t3_variablesBID.do** line 1027: `replace aedu_ci = 3 if p3042 == 3 & p3042s1 == 3`
- **COL_2022t3_variablesBID.do** line 1028: `replace aedu_ci = 4 if p3042 == 3 & p3042s1 == 4`
- **COL_2022t3_variablesBID.do** line 1029: `replace aedu_ci = 5 if p3042 == 3 & p3042s1 == 5`
- **COL_2022t3_variablesBID.do** line 1030: `replace aedu_ci = 5 if p3042 == 4 & p3042s1 == 0`
- **COL_2022t3_variablesBID.do** line 1032: `replace aedu_ci = 6  if p3042 == 4 & p3042s1 == 1`
- **COL_2022t3_variablesBID.do** line 1033: `replace aedu_ci = 7  if p3042 == 4 & p3042s1 == 2`
- **COL_2022t3_variablesBID.do** line 1034: `replace aedu_ci = 8  if p3042 == 4 & p3042s1 == 3`

### `p3043`

- **COL_2022t3_variablesBID.do** line 1070: `g byte eduui_ci = (inlist(p3042, 8, 9, 10, 11, 12, 13) & inlist(p3043, 2, 3, 4))`
- **COL_2022t3_variablesBID.do** line 1079: `g byte eduuc_ci = (inlist(p3042, 8, 9, 10, 11, 12, 13) & inlist(p3043, 5, 6, 7, 8, 9, 10))`
- **COL_2022t3_variablesBID.do** line 1088: `replace eduac_ci = 1 if (inlist(p3042, 10, 11, 12, 13) & inlist(p3043, 7, 8, 9, 10))`
- **COL_2022t3_variablesBID.do** line 1089: `replace eduac_ci = 0 if (inlist(p3042, 8, 9 ) & inlist(p3043, 5, 6))`
- **COL_2023t3_variablesBID.do** line 1088: `g byte eduui_ci = (inlist(p3042, 8, 9, 10, 11, 12, 13) & inlist(p3043, 2, 3, 4))`
- **COL_2023t3_variablesBID.do** line 1098: `g byte eduuc_ci = (inlist(p3042, 8, 9, 10, 11, 12, 13) & inlist(p3043, 5, 6, 7, 8, 9, 10))`
- **COL_2023t3_variablesBID.do** line 1107: `replace eduac_ci = 1 if (inlist(p3042, 10, 11, 12, 13) & inlist(p3043, 7, 8, 9, 10))`
- **COL_2023t3_variablesBID.do** line 1108: `replace eduac_ci = 0 if (inlist(p3042, 8, 9 ) & inlist(p3043, 5, 6))`
- **COL_2024t3_variablesBID.do** line 817: `replace eduui_ci = 1 if inlist(p3042, 8, 9, 10) & p3043<5`
- **COL_2024t3_variablesBID.do** line 824: `g byte eduuc_ci = (inlist(p3042, 8, 9, 10, 11, 12, 13) & inlist(p3043, 5, 6, 7, 8, 9, 10))`

### `p3373`

- **COL_2022t3_variablesBID.do** line 1536: `gen migrante_ci= (p3373==3)`
- **COL_2023t3_variablesBID.do** line 1527: `gen migrante_ci= (p3373==3)`
- **COL_2024t3_variablesBID.do** line 1136: `gen migrante_ci= (p3373==3)`

### `p3373s3`

- **COL_2024t3_variablesBID.do** line 1149: `destring p3373s3, replace`
- **COL_2024t3_variablesBID.do** line 1152: `gen miglac_ci=(migrante_ci==1 & inlist(p3373s3, ///`

### `p3382`

- **COL_2022t3_variablesBID.do** line 1543: `gen migantiguo5_ci=(migrante_ci==1 & inlist(p3382,2,3)) if migrante_ci!=. & p3382!=1`
- **COL_2022t3_variablesBID.do** line 1557: `gen migrantiguo5_ci=(migrante_ci==1 & inlist(p3382,2,3)) if migrante_ci!=. & p3382!=1`
- **COL_2022t3_variablesBID.do** line 1558: `replace migrantiguo5_ci = 0 if p3382 == 4 & migrante_ci==1 & migrante_ci!=. & p3382!=1`
- **COL_2023t3_variablesBID.do** line 1534: `gen migantiguo5_ci=(migrante_ci==1 & inlist(p3382,2,3)) if migrante_ci!=. & p3382!=1`
- **COL_2023t3_variablesBID.do** line 1548: `gen migrantiguo5_ci=(migrante_ci==1 & inlist(p3382,2,3)) if migrante_ci!=. & p3382!=1`
- **COL_2023t3_variablesBID.do** line 1549: `replace migrantiguo5_ci = 0 if p3382 == 4 & migrante_ci==1 & migrante_ci!=. & p3382!=1`
- **COL_2024t3_variablesBID.do** line 1141: `gen migrantiguo5_ci=(migrante_ci==1 & inlist(p3382,2,3)) if migrante_ci!=. & p3382!=1`
- **COL_2024t3_variablesBID.do** line 1142: `replace migrantiguo5_ci = 0 if p3382 == 4 & migrante_ci==1 & migrante_ci!=. & p3382!=1`

### `p6020`

- **COL_2018t3_variablesBID.do** line 170: `g sexo_ci = p6020`
- **COL_2019t3_variablesBID.do** line 171: `g sexo_ci = p6020`
- **COL_2020t3_variablesBID.do** line 175: `g sexo_ci = p6020`
- **COL_2021t3_variablesBID.do** line 201: `g sexo_ci = p6020`

### `p6074`

- **COL_2018t3_variablesBID.do** line 1459: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`
- **COL_2019t3_variablesBID.do** line 1463: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`
- **COL_2020t3_variablesBID.do** line 1370: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`
- **COL_2021t3_variablesBID.do** line 1503: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`

### `p6210`

- **COL_2018t3_variablesBID.do** line 953: `replace p6210=.   if p6210==9`
- **COL_2018t3_variablesBID.do** line 958: `replace aedu_ci = 0 if p6210 == 1 | p6210 == 2`
- **COL_2018t3_variablesBID.do** line 959: `replace aedu_ci = 0 if p6210 == 3 & p6210s1 == 0`
- **COL_2018t3_variablesBID.do** line 961: `replace aedu_ci = 1 if p6210 == 3 & p6210s1 == 1`
- **COL_2018t3_variablesBID.do** line 962: `replace aedu_ci = 2 if p6210 == 3 & p6210s1 == 2`
- **COL_2018t3_variablesBID.do** line 963: `replace aedu_ci = 3 if p6210 == 3 & p6210s1 == 3`
- **COL_2018t3_variablesBID.do** line 964: `replace aedu_ci = 4 if p6210 == 3 & p6210s1 == 4`
- **COL_2018t3_variablesBID.do** line 965: `replace aedu_ci = 5 if p6210 == 3 & p6210s1 == 5`
- **COL_2018t3_variablesBID.do** line 966: `replace aedu_ci = 5 if p6210 == 4 & p6210s1 == 0`
- **COL_2018t3_variablesBID.do** line 968: `replace aedu_ci = 6  if p6210 == 4 & p6210s1 == 6`

### `p6210s1`

- **COL_2018t3_variablesBID.do** line 952: `replace p6210s1=. if p6210s1==99`
- **COL_2018t3_variablesBID.do** line 959: `replace aedu_ci = 0 if p6210 == 3 & p6210s1 == 0`
- **COL_2018t3_variablesBID.do** line 961: `replace aedu_ci = 1 if p6210 == 3 & p6210s1 == 1`
- **COL_2018t3_variablesBID.do** line 962: `replace aedu_ci = 2 if p6210 == 3 & p6210s1 == 2`
- **COL_2018t3_variablesBID.do** line 963: `replace aedu_ci = 3 if p6210 == 3 & p6210s1 == 3`
- **COL_2018t3_variablesBID.do** line 964: `replace aedu_ci = 4 if p6210 == 3 & p6210s1 == 4`
- **COL_2018t3_variablesBID.do** line 965: `replace aedu_ci = 5 if p6210 == 3 & p6210s1 == 5`
- **COL_2018t3_variablesBID.do** line 966: `replace aedu_ci = 5 if p6210 == 4 & p6210s1 == 0`
- **COL_2018t3_variablesBID.do** line 968: `replace aedu_ci = 6  if p6210 == 4 & p6210s1 == 6`
- **COL_2018t3_variablesBID.do** line 969: `replace aedu_ci = 7  if p6210 == 4 & p6210s1 == 7`

### `p6220`

- **COL_2018t3_variablesBID.do** line 954: `replace p6220=. if p6220==9`
- **COL_2018t3_variablesBID.do** line 1003: `g byte eduui_ci = (p6210 == 6 & inlist(p6220, 2, 6))`
- **COL_2018t3_variablesBID.do** line 1012: `g byte eduuc_ci = (p6210 == 6 & inlist(p6220, 3, 4, 5))`
- **COL_2018t3_variablesBID.do** line 1021: `replace eduac_ci = 1 if (p6210 == 6 & inlist(p6220, 4, 5))`
- **COL_2018t3_variablesBID.do** line 1022: `replace eduac_ci = 0 if p6210 == 6 & p6220 == 3`
- **COL_2019t3_variablesBID.do** line 961: `replace p6220=. if p6220==9`
- **COL_2019t3_variablesBID.do** line 1010: `g byte eduui_ci = (p6210 == 6 & inlist(p6220, 2, 6))`
- **COL_2019t3_variablesBID.do** line 1019: `g byte eduuc_ci = (p6210 == 6 & inlist(p6220, 3, 4, 5))`
- **COL_2019t3_variablesBID.do** line 1028: `replace eduac_ci = 1 if (p6210 == 6 & inlist(p6220, 4, 5))`
- **COL_2019t3_variablesBID.do** line 1029: `replace eduac_ci = 0 if p6210 == 6 & p6220 == 3`

### `p755`

- **COL_2018t3_variablesBID.do** line 1466: `gen migantiguo5_ci=(migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1`
- **COL_2018t3_variablesBID.do** line 1480: `gen migrantiguo5_ci=(migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1`
- **COL_2018t3_variablesBID.do** line 1481: `replace migrantiguo5_ci = 0 if p755 == 4 & migrante_ci==1 & migrante_ci!=. & p755!=1`
- **COL_2019t3_variablesBID.do** line 1470: `gen migantiguo5_ci=(migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1`
- **COL_2019t3_variablesBID.do** line 1484: `gen migrantiguo5_ci=(migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1`
- **COL_2019t3_variablesBID.do** line 1485: `replace migrantiguo5_ci = 0 if p755 == 4 & migrante_ci==1 & migrante_ci!=. & p755!=1`
- **COL_2020t3_variablesBID.do** line 1377: `gen migantiguo5_ci=(migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1`
- **COL_2020t3_variablesBID.do** line 1391: `gen migrantiguo5_ci=(migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1`
- **COL_2020t3_variablesBID.do** line 1392: `replace migrantiguo5_ci = 0 if p755 == 4 & migrante_ci==1 & migrante_ci!=. & p755!=1`
- **COL_2021t3_variablesBID.do** line 1510: `gen migantiguo5_ci=(migrante_ci==1 & inlist(p755,2,3)) if migrante_ci!=. & p755!=1`

### `p756`

- **COL_2018t3_variablesBID.do** line 1459: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`
- **COL_2019t3_variablesBID.do** line 1463: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`
- **COL_2020t3_variablesBID.do** line 1370: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`
- **COL_2021t3_variablesBID.do** line 1503: `gen migrante_ci=(p6074==2 & p756==3) if p6074!=. & p756!=.`

## Structural break detection

Variables that appear in some waves but not others (candidate break points):

| Variable | First present | Last present | Absent waves |
|---|---|---|---|
| `fex_c18` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `fex_c_2011` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `fex_c` | 2018t3 | 2024t3 | 2025t3 |
| `p6020` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `fft` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `ini` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `p3042` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `p3042s1` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `p3042s2` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `p3043` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `p6210` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `p6210s1` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `p6220` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `p3373` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `p3373s3` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `p3382` | 2022t3 | 2025t3 | 2018t3, 2019t3, 2020t3, 2021t3 |
| `p6074` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `p756` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `p755` | 2018t3 | 2021t3 | 2022t3, 2023t3, 2024t3, 2025t3 |
| `impa` | 2018t3 | 2024t3 | 2025t3 |
| `impaes` | 2018t3 | 2024t3 | 2025t3 |
| `isa` | 2018t3 | 2024t3 | 2025t3 |
| `isaes` | 2018t3 | 2024t3 | 2025t3 |
| `imdi` | 2018t3 | 2024t3 | 2025t3 |
| `imdies` | 2018t3 | 2024t3 | 2025t3 |
| `ie` | 2018t3 | 2024t3 | 2025t3 |
| `iees` | 2018t3 | 2024t3 | 2025t3 |
| `iof1` | 2018t3 | 2024t3 | 2025t3 |
| `iof2` | 2018t3 | 2024t3 | 2025t3 |
| `iof3h` | 2018t3 | 2024t3 | 2025t3 |
| `iof3i` | 2018t3 | 2024t3 | 2025t3 |
| `iof6` | 2018t3 | 2024t3 | 2025t3 |
| `iof1es` | 2018t3 | 2024t3 | 2025t3 |
| `iof2es` | 2018t3 | 2024t3 | 2025t3 |
| `iof3hes` | 2018t3 | 2024t3 | 2025t3 |
| `iof3ies` | 2018t3 | 2024t3 | 2025t3 |
| `iof6es` | 2018t3 | 2024t3 | 2025t3 |

