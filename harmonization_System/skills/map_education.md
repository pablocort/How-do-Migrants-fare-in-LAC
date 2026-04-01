# Skill: Map Education Variables

## Purpose
Map raw household survey education variables to the three HDMF education standards: years of schooling (`aedu_ci`), ISCED level (`edu_isced`), and the project's own classification (`edu_hdmf`).

## HDMF target variables

| HDMF Variable | Type | Description |
|---------------|------|-------------|
| `aedu_ci` | continuous | Years of completed education |
| `edu_isced` | categorical (0–8) | UNESCO ISCED-2011 attainment level |
| `edu_hdmf` | categorical (1–10) | HDMF project education category |

---

## edu_hdmf classification

This is the primary variable used in HDMF analysis.

| Code | Label | Approximate schooling range |
|------|-------|-----------------------------|
| 1 | Less than primary / No schooling | 0 years |
| 2 | Primary incomplete | 1–5 years |
| 3 | Primary complete | 6 years |
| 4 | Lower secondary incomplete | 7–8 years |
| 5 | Lower secondary complete | 9 years |
| 6 | Upper secondary complete | 10–12 years |
| 7 | Technical / vocational (post-secondary) | varies |
| 8 | University incomplete | 13–15 years |
| 9 | University complete | 16 years |
| 10 | Postgraduate | 17+ years |

---

## ISCED-2011 levels

| Code | Level |
|------|-------|
| 0 | Early childhood education |
| 1 | Primary education |
| 2 | Lower secondary |
| 3 | Upper secondary |
| 4 | Post-secondary non-tertiary |
| 5 | Short-cycle tertiary |
| 6 | Bachelor's / equivalent |
| 7 | Master's / equivalent |
| 8 | Doctoral / equivalent |

---

## Mapping checklist

### Step 1: Find the source education variable

Look for variables that capture:
- **Highest level attended** and **completion status** (most common approach)
- **Years of schooling** (direct, less common)
- **Diploma/certificate obtained** (supplement to level)

Common variable names: `escolaridad`, `nivel_edu`, `grado`, `ultimo_nivel`, `niveleduca`, `p3042`, `educ`, `grade`

### Step 2: Map to edu_hdmf

**Pattern A — level + completion:**
```stata
* Assumes source_level codes: 0=none, 1=primary, 2=secondary, 3=university, etc.
* Assumes source_complete: 1=complete, 2=incomplete

gen edu_hdmf = .
replace edu_hdmf = 1 if source_level == 0                                    // None
replace edu_hdmf = 2 if source_level == 1 & source_complete == 2             // Primary incomplete
replace edu_hdmf = 3 if source_level == 1 & source_complete == 1             // Primary complete
replace edu_hdmf = 4 if source_level == 2 & source_complete == 2 & aedu < 9  // Lower sec incomplete
replace edu_hdmf = 5 if source_level == 2 & source_complete == 2 & aedu >= 9 // Lower sec complete
replace edu_hdmf = 6 if source_level == 2 & source_complete == 1             // Upper secondary
replace edu_hdmf = 7 if source_level == 4                                    // Technical
replace edu_hdmf = 8 if source_level == 3 & source_complete == 2             // University incomplete
replace edu_hdmf = 9 if source_level == 3 & source_complete == 1             // University complete
replace edu_hdmf = 10 if source_level == 5                                   // Postgraduate
```

**Pattern B — years of schooling to edu_hdmf:**
```stata
gen edu_hdmf = .
replace edu_hdmf = 1  if aedu_ci == 0
replace edu_hdmf = 2  if aedu_ci >= 1  & aedu_ci <= 5
replace edu_hdmf = 3  if aedu_ci == 6
replace edu_hdmf = 4  if aedu_ci >= 7  & aedu_ci <= 8
replace edu_hdmf = 5  if aedu_ci == 9
replace edu_hdmf = 6  if aedu_ci >= 10 & aedu_ci <= 12
replace edu_hdmf = 8  if aedu_ci >= 13 & aedu_ci <= 15
replace edu_hdmf = 9  if aedu_ci >= 16 & aedu_ci <= 17
replace edu_hdmf = 10 if aedu_ci >= 18
* Note: technical (7) cannot be inferred from years alone — needs level variable
```

### Step 3: Add diploma upgrade (if available)
Some surveys ask separately about diplomas or certificates obtained. Use this to upgrade education level:
```stata
* Example: if diploma indicates completed bachillerato but level says incomplete:
replace edu_hdmf = 6 if diploma_var == [bachillerato_code] & edu_hdmf < 6
replace edu_hdmf = 9 if diploma_var == [university_degree_code] & edu_hdmf < 9
```

### Step 4: Derive years of schooling (aedu_ci)
If the survey does not have years of schooling directly, derive from edu_hdmf using reference values:
```stata
gen aedu_ci = .
replace aedu_ci = 0  if edu_hdmf == 1
replace aedu_ci = 3  if edu_hdmf == 2   // midpoint of primary incomplete
replace aedu_ci = 6  if edu_hdmf == 3
replace aedu_ci = 7  if edu_hdmf == 4
replace aedu_ci = 9  if edu_hdmf == 5
replace aedu_ci = 12 if edu_hdmf == 6
replace aedu_ci = 14 if edu_hdmf == 7
replace aedu_ci = 14 if edu_hdmf == 8
replace aedu_ci = 16 if edu_hdmf == 9
replace aedu_ci = 18 if edu_hdmf == 10
```
Document this imputation in the mapping notes.

### Step 5: Map to edu_isced
```stata
gen edu_isced = .
replace edu_isced = 0 if edu_hdmf == 1
replace edu_isced = 1 if edu_hdmf == 2 | edu_hdmf == 3
replace edu_isced = 2 if edu_hdmf == 4 | edu_hdmf == 5
replace edu_isced = 3 if edu_hdmf == 6
replace edu_isced = 5 if edu_hdmf == 7
replace edu_isced = 6 if edu_hdmf == 8 | edu_hdmf == 9
replace edu_isced = 7 if edu_hdmf == 10
```

---

## Country-specific notes

| Country | Survey | Education variable | Notes |
|---------|--------|--------------------|-------|
| Colombia | GEIH | p3042 (last grade), p3043 (diploma) | Use p3043 to upgrade edu_hdmf |
| Chile | CASEN | educ | Combined level+completion code 0-17 |
| Ecuador | ENEMDU | p10a (level), p10b (grade) | |
| Peru | ENAHO | p301a (level), p301b (grade) | |
| USA | IPUMS | educ99 or educd | Map IPUMS education codes to edu_hdmf |

---

## Output table format

| HDMF Variable | Source Variable(s) | Source Codes | HDMF Codes | Notes |
|---------------|-------------------|-------------|-----------|-------|
| aedu_ci | | | | |
| edu_isced | | | | Derived from edu_hdmf |
| edu_hdmf | | | 1–10 | |
