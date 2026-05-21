# HDMF — Simple Workflow

```mermaid
flowchart TD

    RAW["📁 Raw survey data\n─────────────────\nbases armo/raw/[iso]/"]
    META["📋 Metadata + coding decisions\n─────────────────\nharmonization_System/inputs/\n  [ISO]_[period]_metadata.md"]
    DICT["🔍 Dictionary check\n─────────────────\nbases armo/armo/dictionary_check.py\n→ [ISO]_dictionary_check_[periods].md"]
    MAP["🗺 Map variables\n─────────────────\nagents/survey_mapper.md\nskills/map_labor · map_education\n  map_migration · map_income"]
    DO["⚙️ Generate Stata script\n─────────────────\nagents/stata_generator.md\n→ do armo/[iso]/[ISO]_[period]_variablesBID.do"]
    RUN["▶️ Run in Stata\n─────────────────\n[ISO]_[period]_variablesBID.do\n→ bases armo/armo/[ISO]/[ISO]_[period]_BID.dta"]
    VAL["✅ Validate output\n─────────────────\nagents/validator.md\nskills/diagnose_harmonization.md"]
    BUILD["🔧 Build unified cache\n─────────────────\nbases armo/armo/hdmf_build.py\n→ _hdmf_cache.pkl  (all countries)"]
    PY["📊 Compute indicators\n─────────────────\nbases armo/armo/hdmf_2.py\n→ out/indicator_descriptive/"]
    VIZ["📈 Custom analyses\n─────────────────\nhdmf_venezuela_vs_native.py\n→ out/venezuela_vs_native/"]
    OUT["📄 Outputs\n─────────────────\nout/indicator_descriptive/\nout/venezuela_vs_native/\nout/latex/"]
    INT["💬 Interpret results\n─────────────────\nagents/indicator_analyst.md\nagents/qa_analyst.md\nskills/detect_anomalies.md"]

    RAW --> META
    META --> DICT
    DICT --> MAP
    MAP --> DO
    DO --> RUN
    RUN --> VAL
    VAL -- "Fix & re-run" --> DO
    VAL -- "Pass" --> BUILD
    BUILD --> PY
    BUILD --> VIZ
    PY --> OUT
    VIZ --> OUT
    OUT --> INT
```

---

## Same survey, new wave (fast path)

```mermaid
flowchart LR
    OLD["Existing .do file\ndo armo/[iso]/[ISO]_[prev]_variablesBID.do"]
    CHK["🔍 Dictionary check\ndictionary_check.py\n— confirm variable names unchanged"]
    CLONE["Clone + change 3 lines:\nlocal ANO · input path · output path"]
    RUN["▶️ Run in Stata\n→ [ISO]_[period]_BID.dta"]
    VAL["✅ Validate\nagents/validator.md"]

    OLD --> CHK
    CHK --> CLONE
    CLONE --> RUN
    RUN --> VAL
```

---

## Key scripts at a glance

| Script | Location | Role |
|--------|----------|------|
| `dictionary_check.py` | `bases armo/armo/` | Checks variable existence across waves before harmonization |
| `[ISO]_[period]_variablesBID.do` | `do armo/[iso]/` | Stata harmonization — produces `_BID.dta` |
| `hdmf_build.py` | `bases armo/armo/` | Merges all `_BID.dta` files into `_hdmf_cache.pkl` |
| `hdmf_2.py` | `bases armo/armo/` | Computes weighted indicators, writes trend tables + charts |
| `hdmf_venezuela_vs_native.py` | `bases armo/armo/` | Venezuela vs. native pooled chart + Excel export |
| `functions.py` | `bases armo/armo/` | Shared helpers: `wavg`, `make_weighted_stats_multi`, plot functions |

---

## Country status

| Status | Countries |
|--------|-----------|
| Done | CHL 2024a · COL 2025t3 · ECU 2025m12 · PER 2024a · USA 2024a |
| In progress | COL 2024t3 · ECU 2024m12 · ESP 2025t3 · MEX 2025t4 |
| Not started | COL 2023t3 · BRA 2025 |
