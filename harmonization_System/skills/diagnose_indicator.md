# Skill: Diagnose Indicator Calculation

## Purpose
When harmonization has been cleared (the BID.dta values look correct), investigate whether the anomaly originates in the Python indicator construction code — `hdmf_trends.py`, `hdmf_2.py`, or `functions.py`. Produce a **Indicator Diagnosis Note** that identifies the exact Python line(s) responsible and whether the logic is wrong.

---

## Input (from Detection Table row, after harmonization cleared)
```
Country:  [ISO3]
Wave:     [period code]
Variable: [HDMF variable, e.g. formal_ci]
Sheet:    [Excel sheet name, e.g. "formality"]
Problem:  [description]
BID.dta check: [confirmed OK / not checked]
```

---

## Step 1 — Identify which Python code produces this indicator

The two main scripts are:

| Script | Produces |
|---|---|
| `bases armo/armo/hdmf_trends.py` | Wave-level trend indicators per group, written to `hdmf_trends_[ISO3].xlsx` |
| `bases armo/armo/hdmf_2.py` | Standard cross-section indicators written to `out/indicator_descriptive/` |

For trend anomalies (the primary use case of this QA agent), focus on `hdmf_trends.py`.

Read the script and find the block that computes the flagged indicator:

```python
# Search for the variable name or sheet name
```

Also read `functions.py` — the actual weighted statistics are usually computed there.

---

## Step 2 — Check the population filter

Every indicator should be computed on the correct sub-population. Common filters:

| Indicator | Expected population filter |
|---|---|
| Formality rate | `emp_ci == 1` |
| Employment rate | `pea_ci == 1` (or working-age) |
| Unemployment rate | `pea_ci == 1` |
| Hours worked | `emp_ci == 1` |
| Migration share | All individuals |
| Education rate | Working-age (`inrange(edad_ci, 15, 64)`) or all |

Check the filter applied in `hdmf_trends.py` for the relevant block:
```python
# Look for: df[df['emp_ci'] == 1] or df.query("emp_ci == 1") or similar
```

If the filter is missing or wrong (e.g., computing formality on all persons rather than employed), this is the error.

---

## Step 3 — Check the grouping variable

The trend charts break data by `migrante_ci` (Native / Migrant) or `foreign_born` (Native / Venezuela / Foreign_other).

Check:
- Is the correct grouping column being used?
- Are the group labels defined correctly?
- Is there a wave where the grouping column has unexpected values (e.g., NaN counts as a separate group)?

```python
import pickle, pandas as pd
with open("bases armo/armo/_hdmf_cache.pkl", "rb") as f:
    d = pickle.load(f)
data = d["data"]
iso = "CHL"
sub = data[(data["pais_c"] == iso) & (data["periodo_c"] == "[wave]")]
# Check grouping values
print(sub["migrante_ci"].value_counts(dropna=False))
print(sub["foreign_born"].value_counts(dropna=False))
# Check variable within filter
emp = sub[sub["emp_ci"] == 1]
print(emp["formal_ci"].value_counts(dropna=False))
print(f"formal rate: {emp['formal_ci'].mean():.4f}")
```

---

## Step 4 — Check the weighting logic

All indicators must use `factor_ci` (individual expansion factor) as the weight.

In `functions.py` or `hdmf_trends.py`, find where `np.average` or equivalent is called:

```python
# Correct:
np.average(series, weights=weights)
# Wrong: unweighted mean
series.mean()
# Wrong: wrong weight variable
np.average(series, weights=df["factor_ch"])  # household weight instead of individual
```

Also check for cases where weights are NaN or zero for specific waves — this would cause the weighted mean to be computed over a much smaller population.

```python
sub = data[(data["pais_c"] == iso) & (data["periodo_c"] == "[wave]")]
print(f"factor_ci NaN: {sub['factor_ci'].isna().sum()}")
print(f"factor_ci zero: {(sub['factor_ci'] == 0).sum()}")
print(f"factor_ci min/max: {sub['factor_ci'].min():.2f} / {sub['factor_ci'].max():.2f}")
```

---

## Step 5 — Check the `foreign_born` / `migrante_ci` classification

The cache-build script (`hdmf_build.py`) creates `foreign_born` from `mig_pais_ci`:
```python
data["foreign_born"] = data["mig_pais_ci"].apply(
    lambda x: "Native" if x == "" else ("Venezuela" if x == "Venezuela" else "Foreign_other")
)
```

If country names in `mig_pais_ci` are in a different format (e.g., ALL-CAPS), Venezuela would fall into `Foreign_other` instead of its own group. Check:

```python
sub = data[(data["pais_c"] == iso) & (data["migrante_ci"] == "Migrant")]
print(sub["mig_pais_ci"].value_counts().head(20))
print(sub["foreign_born"].value_counts())
```

---

## Step 6 — Replicate the suspicious value manually

Reproduce the exact number that appears in the anomalous cell:

```python
sub = data[
    (data["pais_c"] == iso) &
    (data["periodo_c"] == "[wave]") &
    (data["emp_ci"] == 1) &
    (data["migrante_ci"] == "[group]")   # e.g., "Migrant"
]
val = np.average(sub["formal_ci"].dropna(),
                 weights=sub.loc[sub["formal_ci"].notna(), "factor_ci"])
print(f"Replicated: {val:.4f}")
```

If this matches the anomalous Excel value, the error is in the Python code (filter, weight, or group). If the replicated value looks correct but the Excel doesn't match, the Excel was generated from a stale cache — rebuild and rerun.

---

## Step 7 — Basic Stats Comparison Table

For every diagnosed anomaly (whether root cause is confirmed or still unclear), produce a **Basic Stats Comparison Table** that summarizes the indicator across all waves and groups. This table is the primary deliverable for the user to review, and is included regardless of whether a root cause was found.

### Standard table format

```markdown
### Basic Stats: [indicator] — [ISO3] — [variable]

| Wave | Group | N (weighted) | Mean | Std Dev | Min | p10 | p50 | p90 | Max | NaN % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2017a | Native | 5,230,000 | 0.871 | 0.335 | 0 | 1 | 1 | 1 | 1 | 0.2% |
| 2017a | Migrant | 280,000 | 0.851 | 0.357 | 0 | 0 | 1 | 1 | 1 | 0.5% |
| 2020a | Native | 4,890,000 | 0.882 | ... | ... | ... |
...
```

### Python script to produce this table

```python
import pickle, pandas as pd, numpy as np

with open("bases armo/armo/_hdmf_cache.pkl", "rb") as f:
    d = pickle.load(f)
data = d["data"]

iso      = "CHL"
variable = "formal_ci"        # ← change to target variable
pop_filt = "emp_ci == 1"      # ← change to correct population filter
grp_col  = "migrante_ci"      # ← "migrante_ci" or "foreign_born"

sub = data.query(f"pais_c == '{iso}' and {pop_filt}").copy()

rows = []
for period in sorted(sub["periodo_c"].unique()):
    for grp in sorted(sub[grp_col].dropna().unique()):
        sel = sub[(sub["periodo_c"] == period) & (sub[grp_col] == grp)]
        s   = sel[variable]
        w   = sel["factor_ci"]
        if s.notna().sum() < 10:
            continue
        # Weighted mean
        s_nona = s.dropna(); w_nona = w[s.notna()]
        wmean  = np.average(s_nona, weights=w_nona) if len(s_nona) > 0 else np.nan
        wn     = w_nona.sum()
        # Unweighted stats for distribution
        pcts = s.quantile([.10, .50, .90]).values
        row = {
            "Wave": period, "Group": grp,
            "N_weighted": round(wn),
            "Mean": round(wmean, 4),
            "Std":  round(s_nona.std(), 4),
            "Min":  s_nona.min(), "p10": pcts[0], "p50": pcts[1], "p90": pcts[2],
            "Max":  s_nona.max(),
            "NaN_pct": round(100 * s.isna().sum() / len(sel), 2),
        }
        rows.append(row)

df_stats = pd.DataFrame(rows)
print(df_stats.to_string(index=False))

# Cross-wave delta (flag if any group jumps > 20pp)
df_stats["delta"] = df_stats.groupby(grp_col)["Mean"].diff().abs()
flags = df_stats[df_stats["delta"] > 0.20]
if len(flags) > 0:
    print("\nFLAGGED JUMPS (>20pp):")
    print(flags[["Wave", "Group", "Mean", "delta"]].to_string(index=False))
```

Run this script for every variable in the Detection Table. Paste the output into the diagnosis note.

### Categorical variable distribution table

For categorical variables (`edu_hdmf`, `tipocontrato_ci`, `condocup_ci`), produce a distribution table instead:

```python
iso      = "CHL"
variable = "edu_hdmf"
grp_col  = "migrante_ci"

sub = data[data["pais_c"] == iso].copy()

for period in sorted(sub["periodo_c"].unique()):
    for grp in sorted(sub[grp_col].dropna().unique()):
        sel = sub[(sub["periodo_c"] == period) & (sub[grp_col] == grp)]
        # Weighted frequency
        freq = sel.groupby(variable)["factor_ci"].sum()
        total = freq.sum()
        pct   = (freq / total * 100).round(1)
        pct_null = 100 * sel[variable].isna().sum() / len(sel)
        print(f"\n{period} | {grp}  (NaN={pct_null:.1f}%)")
        print(pct.to_string())
```

### Output format

The Basic Stats Comparison Table is always included in the QA Detection Table output, even when no anomaly is found. It serves as the reference for cross-wave comparisons in presentations and reports.

---

## Output: Indicator Diagnosis Note

```markdown
### Indicator Diagnosis — [ISO3] [wave] — [indicator] — [group]

**Script checked:** `bases armo/armo/hdmf_trends.py`  
**Functions checked:** `bases armo/armo/functions.py`

**Relevant code:**
```python
[paste the exact lines that compute this indicator]
```

**Problem identified:** [yes / no]

**Description:**
[One paragraph: what Python logic is wrong, which line, what it should be instead]

**Evidence:**
- Cache check: [e.g., "factor_ci has 3,200 NaN in 2017a for CHL — reduces effective N"]
- Manual replication: `formal_ci` weighted mean = [X] (matches / does not match Excel)
- Grouping check: [e.g., "foreign_born 'Venezuela' = 0 for 2017a due to ALL-CAPS mig_pais_ci"]

**Root cause:** [INDICATOR CALC / DATA / UNRESOLVED]

**Proposed fix (brief):** [if root cause found — one sentence]
```

---

## Escalation rule

If the Python code looks correct and manual replication matches the expected value, the anomaly may be genuine data (e.g., COVID affecting employment unusually, or a small migrant subgroup with extreme values). Write:

```
Root cause: DATA — anomaly is plausible given survey context
```

And document the explanation. No fix needed; add a note to the detection table.
