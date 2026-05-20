# COL — Intermediate Harmonization Output Index

Quick navigation for all intermediate files produced during the COL GEIH harmonization.

---

## Multi-wave files

| File | What it answers |
|------|----------------|
| [COL_dictionary_check_2018_2025.md](COL_dictionary_check_2018_2025.md) | Which variables changed names/categories between 2018–2025? What are the structural breaks? |
| [COL_dictionary_check_2023_2024.md](COL_dictionary_check_2023_2024.md) | Earlier dictionary check covering 2023–2024 only (superseded by 2018–2025) |

### Key findings from dictionary check (2018–2025)
- **Structural break at 2021→2022**: 6 variable name changes
  - Weight: `fex_c_2011` → `fex_c18`
  - Inactive flag: `ini` → `fft`
  - Education: `p6210` / `p6210s1` → `p3042` / `p3042s1`
  - Migration birthplace: `p6074` / `p756` → `p3373`
  - Migration duration: `p755` → `p3382`
  - Sex: `p6020` → `p3271`

---

## Per-wave files

| Wave | Metadata | Run instructions | Dictionary check | Mapping checker | Validation |
|------|----------|-----------------|-----------------|----------------|------------|
| [2018t3](2018t3/) | — | — | (in multi-wave) | — | — |
| [2019t3](2019t3/) | — | — | (in multi-wave) | — | — |
| [2020t3](2020t3/) | — | — | (in multi-wave) | — | — |
| [2021t3](2021t3/) | — | — | (in multi-wave) | — | — |
| [2022t3](2022t3/) | — | — | (in multi-wave) | — | — |
| [2023t3](2023t3/) | [metadata](2023t3/COL_2023t3_metadata.md) | [run instructions](2023t3/COL_2023_2024_run_instructions.md) | (in multi-wave) | — | — |
| [2024t3](2024t3/) | [metadata](2024t3/COL_2024t3_metadata.md) | — | (in multi-wave) | — | — |
| [2025t3](2025t3/) | — | — | (in multi-wave) | — | — |

> To add a new file: save it in `intermediate_harmo_output/{wave}/` and add a row to the table above.

---

## File type guide

| Type | When created | Content |
|------|-------------|---------|
| `*_metadata.md` | Before harmonization | Survey design, weight variable, migration/education/labor modules, known issues |
| `*_dictionary_check*.md` | Before harmonization (Python) | Variable existence matrix, category codes, structural breaks |
| `*_run_instructions.md` | During harmonization | Step-by-step instructions for running the script; issues found during run |
| `*_mapping_checker.md` | After mapping (AI agent) | HIGH/MEDIUM/LOW risk flags on each variable mapping decision |
| `*_validation.md` | After Stata run | Observation counts, population totals, share checks |
