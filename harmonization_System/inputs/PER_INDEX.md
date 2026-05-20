# PER — Intermediate Harmonization Output Index

Quick navigation for all intermediate files produced during the PER ENAHO harmonization.

---

## Multi-wave files

| File | What it answers |
|------|----------------|
| [PER_dictionary_check_2018a_2024a.md](PER_dictionary_check_2018a_2024a.md) | Which variables changed names/categories between 2018–2024? What are the structural breaks? |
| [PER_2018_2024_run_instructions.md](PER_2018_2024_run_instructions.md) | Step-by-step run instructions, coding decisions, validation checks, troubleshooting |

### Key findings from dictionary check (2018–2024)
- **Zero structural breaks**: all ENAHO target variables exist in all 7 waves
- `p558b2` (year of last pension contribution) present in all waves — stored as string type
- Migration variables (p401g2, p401f, p401g) stable across all years
- Remittances (d5563c, d5563e) stable across all years

### Key coding decisions
- **cotizando_ci (2018–2023)**: uses `p524b1`/`p538b1` (contribution amounts), following MECOVI approach; `p558b2==ANO` is a documented alternative
- **relacion_ci (2018 only)**: no `p203==11` condition (added in ENAHO 2019+)
- **horastot_ci (2019–2022)**: `replace p518=. if p518==99` before rsum
- **Income module**: fully excluded in all waves

---

## Per-wave files

| Wave | Metadata | Run instructions | Dictionary check | Mapping checker | Validation |
|------|----------|-----------------|-----------------|----------------|------------|
| [2018a](2018a/) | — | [multi-wave](PER_2018_2024_run_instructions.md) | (in multi-wave) | — | — |
| [2019a](2019a/) | — | [multi-wave](PER_2018_2024_run_instructions.md) | (in multi-wave) | — | — |
| [2020a](2020a/) | — | [multi-wave](PER_2018_2024_run_instructions.md) | (in multi-wave) | — | — |
| [2021a](2021a/) | — | [multi-wave](PER_2018_2024_run_instructions.md) | (in multi-wave) | — | — |
| [2022a](2022a/) | — | [multi-wave](PER_2018_2024_run_instructions.md) | (in multi-wave) | — | — |
| [2023a](2023a/) | — | [multi-wave](PER_2018_2024_run_instructions.md) | (in multi-wave) | — | — |
| [2024a](2024a/) | [metadata](2024a/PER_2024a_metadata.md) | — | (in multi-wave) | — | — |

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
