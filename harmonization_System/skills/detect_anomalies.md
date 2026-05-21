# Skill: Detect Anomalies

## Purpose
Scan all indicator sheets in an HDMF trend Excel file and flag cells, series, or patterns that look wrong. Produce a structured **Detection Table** that becomes the working document for the QA diagnosis phases.

This skill does not explain why something is wrong — it only flags what looks suspicious. Diagnosis happens in the `diagnose_harmonization` and `diagnose_indicator` skills.

---

## Input
- Path to `hdmf_trends_[ISO3].xlsx` (or the cache `.pkl` for direct Python checks)
- Country ISO3 and list of available waves

---

## Step 1 — Load the trend data

**Option A (preferred): Read from the trend Excel file**

```python
import pandas as pd
xl = pd.ExcelFile("out/indicator_descriptive/[DATE]/hdmf_trends_[ISO3].xlsx")
sheets = xl.sheet_names   # one sheet per indicator group
for sheet in sheets:
    df = xl.parse(sheet)
    print(sheet, df.columns.tolist())
    print(df.head())
```

**Option B: Read directly from cache**

```python
import pickle, pandas as pd
with open("bases armo/armo/_hdmf_cache.pkl", "rb") as f:
    d = pickle.load(f)
data = d["data"]
chl = data[data["pais_c"] == "CHL"]
```

---

## Step 2 — Apply anomaly detection rules

For each indicator × group × wave cell, check all rules below. A cell that triggers one or more rules gets a row in the Detection Table.

### Rule 1 — Boundary rate (SEVERITY: HIGH)
A binary rate (formality, employment, unemployment, migration share) equals **exactly 1.000 or 0.000** for any group×wave cell with N ≥ 30.

Why suspicious: binary rates with no variation almost always indicate a coding error (all-1 or all-0 due to missing zeros, wrong variable construction).

Threshold: `mean == 1.0 or mean == 0.0` and `n >= 30`

### Rule 2 — Implausible value (SEVERITY: HIGH)
A rate or mean is outside the plausible range for that indicator type:

| Indicator | Plausible range | Flag if |
|---|---|---|
| Formality rate | 10% – 98% | < 0.10 or > 0.98 |
| Employment rate (of PEA) | 60% – 99% | < 0.60 or > 0.99 |
| Unemployment rate | 0.5% – 40% | < 0.005 or > 0.40 |
| Inactive rate | 10% – 70% | < 0.10 or > 0.70 |
| Migration share | 0.1% – 30% | < 0.001 or > 0.30 |
| Mean years of schooling | 4 – 18 | < 4 or > 18 |
| Mean weekly hours | 15 – 60 | < 15 or > 60 |

### Rule 3 — Large wave-to-wave jump (SEVERITY: MEDIUM)
For consecutive waves of the same group, the rate changes by more than **20 percentage points** (or 20% of mean for continuous variables).

Formula: `abs(mean_wave_t - mean_wave_t_minus_1) > 0.20`

Flag with `direction` (up/down) and `magnitude`.

### Rule 4 — Group appears/disappears (SEVERITY: MEDIUM)
A group (e.g., `Venezuela`, `Foreign_other`) is present in some waves (N ≥ 30) but absent (N < 10 or NaN) in others, with no obvious survey explanation.

### Rule 5 — Implausible migrant–native gap (SEVERITY: MEDIUM)
The absolute difference between migrant and native means exceeds **35 percentage points** for formality, employment, or education. Gaps this large are almost always a sign that one group has a coding error.

`abs(mean_migrant - mean_native) > 0.35`

### Rule 6 — All-missing wave (SEVERITY: HIGH)
An entire column for a specific wave × variable is NaN. This means the variable was not created in that wave's harmonization script (or was created but all-missing).

### Rule 7 — Sample size anomaly (SEVERITY: MEDIUM)
The weighted N for a wave is less than 50% or more than 200% of the median weighted N across waves for the same country. Could indicate a weight construction error or wrong population restriction.

`n_wave / median(n_all_waves) < 0.5  or  > 2.0`

---

## Step 3 — Build the Detection Table

Format every flagged cell as one row:

```markdown
## Detection Table — [ISO3] [DATE]

| # | Sheet/Indicator | Wave | Group | Observed value | Expected range | Rule triggered | Severity | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | formality | 2017a | Migrant | 1.000 (100%) | 10–98% | Rule 1 + Rule 2 | HIGH | Pending diagnosis |
| 2 | formality | 2020a | Native | 1.000 (100%) | 10–98% | Rule 1 + Rule 2 | HIGH | Pending diagnosis |
| 3 | employment | 2020a | all | 0.923 | 60–99% | None — OK | — | Clean |
| 4 | hours_worked | 2020a | Migrant | 38.2 | 15–60 | Rule 3 (jump +22pp from 2017a) | MEDIUM | Pending diagnosis |
...

**Summary:** [N_HIGH] HIGH · [N_MEDIUM] MEDIUM · [N_OK] cells clean
```

Rules:
- Only include rows for flagged cells (SEVERITY HIGH or MEDIUM) in the working table; omit clean cells unless the user asks for the full scan
- If multiple rules fire for the same cell, list all of them in "Rule triggered"
- The `Status` column starts as "Pending diagnosis" and is updated in Phases 2–3

---

## Step 4 — Quick Python scan script

Use this script as a starting point for systematic scanning. Adapt to the actual column names in the Excel:

```python
import pandas as pd, numpy as np

XL_PATH = "out/indicator_descriptive/[DATE]/hdmf_trends_[ISO3].xlsx"
PLAUSIBLE = {
    "formal_rate":      (0.10, 0.98),
    "emp_rate":         (0.60, 0.99),
    "unemp_rate":       (0.005, 0.40),
    "inactive_rate":    (0.10, 0.70),
    "migrant_share":    (0.001, 0.30),
    "mean_aedu":        (4.0, 18.0),
    "mean_hours":       (15.0, 60.0),
}

xl = pd.ExcelFile(XL_PATH)
flags = []
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    if "mean" not in df.columns:
        continue
    for _, row in df.iterrows():
        val = row.get("mean")
        n   = row.get("n", row.get("N", np.nan))
        if pd.isna(val) or pd.isna(n):
            flags.append({"sheet": sheet, "wave": row.get("periodo_c"), "group": row.get("migrante_ci", row.get("foreign_born")), "value": val, "n": n, "rule": "Rule 6 — all-missing"})
            continue
        # Rule 1 + 2
        if (val == 1.0 or val == 0.0) and n >= 30:
            flags.append({"sheet": sheet, "wave": row.get("periodo_c"), "group": row.get("migrante_ci"), "value": val, "n": n, "rule": "Rule 1 boundary rate"})
        # Rule 2 — plausible range (match sheet name to PLAUSIBLE dict)
        for kw, (lo, hi) in PLAUSIBLE.items():
            if kw.lower() in sheet.lower():
                if not (lo <= val <= hi) and n >= 30:
                    flags.append({"sheet": sheet, "wave": row.get("periodo_c"), "group": row.get("migrante_ci"), "value": round(val,4), "n": n, "rule": f"Rule 2 out-of-range [{lo},{hi}]"})

# Rule 3 — wave jumps (requires sorting by periodo_c within group)
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    if "mean" not in df.columns or "periodo_c" not in df.columns:
        continue
    grp_col = "migrante_ci" if "migrante_ci" in df.columns else "foreign_born"
    if grp_col not in df.columns:
        continue
    for g, gdf in df.groupby(grp_col):
        gdf = gdf.sort_values("periodo_c")
        gdf["delta"] = gdf["mean"].diff().abs()
        for _, row in gdf[gdf["delta"] > 0.20].iterrows():
            flags.append({"sheet": sheet, "wave": row["periodo_c"], "group": g, "value": round(row["mean"],4), "n": row.get("n"), "rule": f"Rule 3 jump {round(row['delta'],2)}"})

print(f"\n{'='*60}")
print(f"Total flags: {len(flags)}")
for f in flags:
    print(f"  {f['sheet']:30s}  {str(f['wave']):10s}  {str(f['group']):15s}  {str(f['value']):8s}  n={f['n']}  {f['rule']}")
```

---

## After completing this skill

Hand the Detection Table to the `qa_analyst` agent. It will:
1. Show the table to the user for review/prioritization
2. Invoke `diagnose_harmonization` for each flagged row
3. Invoke `diagnose_indicator` for rows where harmonization is clean
