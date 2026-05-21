# Skill: Propose Fix

## Purpose
After harmonization or indicator diagnosis has identified root causes, format the proposed corrections into a structured **Fix Proposal Table** for user review and approval. No code is changed until the user explicitly approves each row.

---

## Input
A list of diagnosed anomalies, each with:
- Root cause type: `HARMONIZATION` or `INDICATOR CALC`
- File path where the fix must be applied
- Description of what is wrong and what the correct version is

---

## Fix Proposal Table format

Present one row per proposed change. Use this exact markdown table format:

```markdown
## Fix Proposal Table — [ISO3] [DATE]

| # | Root cause | File | Lines (approx.) | Current code | Proposed replacement | Expected effect | Approval |
|---|---|---|---|---|---|---|---|
| 1 | HARMONIZATION | `do armo/chl/CHL_2017a_variablesBID.do` | ~104 | `replace cotizando_ci = 0 if o29 == 6` | `replace cotizando_ci = 0 if o29 >= 6 & o29 < 9` | Captures code 7 ("No cotiza", 49,902 obs) → formality rate drops from 100% to ~87% | ☐ |
| 2 | HARMONIZATION | `do armo/chl/CHL_2017a_variablesBID.do` | ~104–115 | *(no recode lines)* | Add `recode cotizando_ci . = 0 if emp_ci == 1` and `recode afiliado_ci . = 0 if emp_ci == 1` before `formal_ci` block | Ensures NaN sub-variables become 0 for employed; formal_ci=0 condition can fire | ☐ |
| 3 | INDICATOR CALC | `bases armo/armo/hdmf_trends.py` | ~88 | `df.groupby(...)["formal_ci"].mean()` | `np.average(grp["formal_ci"].dropna(), weights=grp.loc[grp["formal_ci"].notna(),"factor_ci"])` | Uses expansion weights; currently unweighted | ☐ |
```

### Column definitions

| Column | What to write |
|---|---|
| **#** | Sequential number — matches the Detection Table row |
| **Root cause** | `HARMONIZATION` or `INDICATOR CALC` |
| **File** | Full relative path from project root |
| **Lines (approx.)** | Approximate line numbers from reading the file (helps the user locate the change) |
| **Current code** | Exact current line(s) — use backtick code formatting. If inserting new lines, write *(no existing code)* |
| **Proposed replacement** | Exact new line(s). If multiple lines, use `\n` to separate or write as a code block in a separate section |
| **Expected effect** | What the output will look like after this fix — reference the indicator value if known |
| **Approval** | Leave as `☐` (unchecked). User will mark `☑` to approve or `✗` to reject |

---

## Multi-line fixes

For changes that are too long for a table cell, use this extended format below the table:

```markdown
### Fix #[N] — extended code

**File:** `[path]`

**Current code (lines [X]–[Y]):**
```stata
[paste current lines]
```

**Proposed replacement:**
```stata
[paste proposed lines]
```

**Rationale:** [one paragraph explaining why this is the right fix and why it won't break anything else]
```

---

## Re-run plan

After listing all proposed fixes, always include a **Re-run plan** so the user knows what pipeline steps to execute after approving:

```markdown
## Re-run plan (execute in order after approvals)

| Step | Command | Depends on |
|---|---|---|
| 1 | Re-run Stata: `CHL_2017a_variablesBID.do` | Fix #1, #2 approved |
| 2 | Re-run Stata: `CHL_2020a_variablesBID.do` | Fix #3 approved |
| 3 | Rebuild cache: `py hdmf_build.py --countries CHL` | Steps 1–2 complete |
| 4 | Rerun trends: `py hdmf_trends.py --country CHL` | Step 3 complete |
| 5 | Regenerate charts: `py hdmf_trends_charts.py --country CHL` | Step 4 complete |
| 6 | Verify: re-run detection scan on new Excel | Step 5 complete |
```

---

## After user approves

Once the user marks `☑` on a row:
1. Apply **only the approved changes** — do not touch unapproved rows
2. Make the edit using the Edit tool, showing the exact before/after diff
3. Execute the re-run plan steps that depend on the approved fix
4. Run the detection scan again on the new Excel to confirm the anomaly is resolved
5. Update the Detection Table row status from `Pending` → `Fixed` or `Rejected`

---

## What NOT to do

- Do not apply any fix before user approval — not even "obvious" ones
- Do not combine multiple fixes into a single commit/edit unless they are strictly dependent
- Do not propose refactoring, cleanup, or improvements beyond the detected anomaly
- If a fix has uncertain side effects on other waves or countries, say so explicitly in "Expected effect"
