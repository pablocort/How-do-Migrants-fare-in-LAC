# Skill: Diagnose Harmonization

## Purpose
Given a specific anomaly from the Detection Table (country, wave, HDMF variable, observed problem), investigate whether the root cause is in the Stata harmonization script or the variable dictionary. Produce a concise **Harmonization Diagnosis Note** that either confirms a harmonization error and describes it precisely, or clears harmonization and escalates to the indicator calculation check.

---

## Input (from Detection Table row)
```
Country:  [ISO3]
Wave:     [period code, e.g. 2017a]
Variable: [HDMF variable, e.g. formal_ci]
Problem:  [description, e.g. "rate = 100% for all groups"]
```

---

## Step 1 — Identify the harmonization script

The script that created `[ISO3]_[period]_BID.dta` is at:
```
do armo/[iso3 lowercase]/[ISO3]_[period]_variablesBID.do
```
Examples:
- `do armo/chl/CHL_2017a_variablesBID.do`
- `do armo/col/COL_2024t3_variablesBID.do`

Read the relevant section of the script — the block that creates the flagged HDMF variable.

---

## Step 2 — Identify the variable construction block

Find the `gen` and `replace` statements for the flagged variable. Pay attention to:

### 2a — Zero-coding completeness
For binary variables (`formal_ci`, `emp_ci`, `migrante_ci`, etc.), check that **both** the 1-condition and the 0-condition are correctly coded.

Common failure modes:
| Symptom | Likely cause |
|---|---|
| Rate = 100%, no zeros | The 0-condition uses wrong code(s) — non-contributing workers get NaN instead of 0 |
| Rate = 0%, no ones | The 1-condition uses wrong code(s) — all affirmative responses are miscategorized |
| Rate = NaN for entire wave | Variable not created in that wave's script, or all `replace` conditions are false |
| Rate correct for one group but wrong for another | Population restriction (`if emp_ci==1`, `if inrange(edad_ci,15,64)`) applied inconsistently |

### 2b — Missing-value handling before binary operations
When a binary variable is computed as a combination of two sub-variables (e.g., `formal_ci = 1 if cotizando OR afiliado`), check whether sub-variables with NaN propagate correctly.

Key check: if `formal_ci = 0 if (cotizando_ci==0 AND afiliado_ci==0)` but either sub-variable can be NaN, the AND condition never fires → formal_ci stays NaN, never 0.

**Solution pattern** (from CHL 2017–2022 fix):
```stata
* After creating sub-variables, fill NaN with 0 for employed before combining:
recode cotizando_ci . = 0 if emp_ci == 1
recode afiliado_ci  . = 0 if emp_ci == 1
* Then compute formal_ci
```

### 2c — Category codes
For variables that depend on specific raw category codes, check that the codes match what is actually in the data. 

To verify: look up the raw category distribution in the dictionary check file:
```
bases armo/armo/[ISO3]/intermediate_harmo_output/[ISO3]_dictionary_check_*.md
```

Or extract directly from the cache:
```python
import pickle, pandas as pd
with open("bases armo/armo/_hdmf_cache.pkl", "rb") as f:
    d = pickle.load(f)
# Note: cache has harmonized variables; for RAW category codes, read the BID.dta or raw .dta
```

For raw variable checks, use Python with `pyreadstat` or `pandas.read_stata`:
```python
import pandas as pd
raw = pd.read_stata("bases armo/raw/[iso3]/[raw_file].dta",
                    columns=["[raw_var]"], convert_categoricals=False)
print(raw["[raw_var]"].value_counts().sort_index())
```

Or read the harmonized BID.dta to check what values ended up in the output:
```python
bid = pd.read_stata("bases armo/armo/[ISO3]/[ISO3]_[period]_BID.dta",
                    columns=["emp_ci", "[hdmf_var]", "[source_var_if_kept]"],
                    convert_categoricals=False)
print(bid[bid["emp_ci"]==1]["[hdmf_var]"].value_counts(dropna=False))
```

### 2d — Population restriction
Check that the variable is constructed for the correct population:
- Labor variables (`formal_ci`, `tipocontrato_ci`, `horastot_ci`): only for `emp_ci==1`
- Employment/unemployment: only for working-age (`inrange(edad_ci,15,64)`)
- Migration variables: all observations

Look for cases where the restriction is missing, too broad, or applied to the wrong sub-variable.

### 2e — Wave-specific differences
Check the script header comments for documented differences from the reference wave. If the comment says a variable is absent or uses an alternative, verify the alternative was implemented correctly.

---

## Step 3 — Cross-check with dictionary

Open the dictionary check file:
```
bases armo/armo/[ISO3]/intermediate_harmo_output/[ISO3]_dictionary_check_*.md
```

Verify:
1. Is the source variable actually present in this wave? (It might be listed as ❌)
2. Do the category codes documented there match what the .do script assumes?
3. Is there a note about a structural change or alternative in this wave?

If no dictionary check file exists, note this as a gap — the diagnosis is less reliable.

---

## Step 4 — Check the harmonized output directly

Use Python to verify counts in the final `_BID.dta`:

```python
import pandas as pd
bid = pd.read_stata("bases armo/armo/[ISO3]/[ISO3]_[period]_BID.dta",
                    convert_categoricals=False)
emp = bid[bid["emp_ci"] == 1]
print("formal_ci distribution (employed only):")
print(emp["formal_ci"].value_counts(dropna=False).sort_index())
print(f"  formal rate: {emp['formal_ci'].mean():.4f}")
```

This confirms whether the error is in the Stata code or downstream (Python).

---

## Output: Harmonization Diagnosis Note

Write one note per anomaly. Format:

```markdown
### Harmonization Diagnosis — [ISO3] [wave] — [HDMF variable]

**Script checked:** `do armo/[iso3]/[ISO3]_[period]_variablesBID.do`  
**Dictionary checked:** `[path or "not found"]`

**Construction code reviewed:**
```stata
[paste the exact lines from the .do file that create this variable]
```

**Problem identified:** [yes / no / partial]

**Description:**
[One paragraph: what is wrong, where exactly in the code, why it produces the observed anomaly]

**Evidence:**
- Raw category check: `[var] == [code]` → [N obs] (expected ~[N])
- Harmonized output: `formal_ci` values = {0: [N], 1: [N], NaN: [N]}
- [any other supporting evidence]

**Root cause:** [HARMONIZATION / CLEAN — escalate to indicator check]

**Proposed fix (brief):** [if root cause is HARMONIZATION — one sentence describing the fix]
[This will be formalized in the propose_fix skill]
```

---

## Escalation rule

If after Steps 1–4 the harmonization code looks correct and the BID.dta values are sensible, write:

```
Root cause: CLEAN — escalate to indicator calculation check
```

And pass the anomaly to the `diagnose_indicator` skill.
