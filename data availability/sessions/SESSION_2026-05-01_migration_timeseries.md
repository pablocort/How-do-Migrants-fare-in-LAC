# Session: Migration Variable Time-Series Availability Table
**Session ID:** `2026-05-01_migration_timeseries`
**Date:** 2026-05-01
**Goal:** Extend the existing single-year migration variable availability Excel into a full time series (2015+) for all LAC countries on the IDB network share, plus N observations from HDMF raw microdata.

---

## What was accomplished in this session

### 1. Scoped the network share
- Confirmed `\\sapidbshares.file.core.windows.net\idbshares\SURVEYS\survey` is accessible as UNC path.
- Structure: `[ISO3]/[SURVEY]/[YEAR]/[PERIOD]/docs/` — each `docs/` folder has dictionaries, questionnaires, and codebooks.
- Mapped primary labor force survey for 18 countries with data available 2015+.

### 2. Created `scan_and_decode_network.py`
**Location:** `data availability/scan_and_decode_network.py`

Scans the network share for all 18 countries × years 2015+. For each year/period:
- Picks the best documentation file using a ranked preference: `DICT_XLSX > ODS > XLSX > DICT_PDF > QUESTIONNAIRE_PDF > FICHA_PDF > skip`
- Selects the period with the best file (not just any preferred period — avoids picking a questionnaire PDF in "a" when a DICT_XLSX exists in "t3")
- Decodes the file using existing parsers (`parsers/parse_xlsx.py`, `parse_ods.py`, `parse_pdf.py`)
- Saves to `decoded_ts/[ISO3]_[YEAR][PERIOD]_dictionary.json`

**Country–survey map used:**
| ISO3 | Survey | 2015+ years available |
|------|--------|----------------------|
| ARG | EPHC | 2015–2025 (quarterly) |
| BOL | ECH | 2015–2024 |
| BRA | PNADC | 2016–2025 |
| CHL | CASEN | 2015, 2017, 2020, 2022, 2024 (biennial) |
| COL | GEIH | 2015–2025 |
| CRI | ENAHO | 2015–2025 |
| DOM | ENCFT | 2017–2024 |
| ECU | ENEMDU | 2015–2025 |
| GTM | ENEIC | 2024–2025 only |
| GUY | LFS | 2017–2021 |
| HND | EPHPM | 2015–2025 |
| JAM | LFS | 2016 only |
| MEX | ENOE | 2015–2016 only (docs folder for ENOE is inside a generic `docs/` without year subfolders) |
| PER | ENAHO | 2015–2024 |
| PRY | EPH | 2015–2017 |
| SLV | EHPM | 2015–2025 |
| URY | ECH | 2015–2025 |
| VEN | EHM | no 2015+ data found |

### 3. Created `build_timeseries_table.py`
**Location:** `data availability/build_timeseries_table.py`

Reads all `decoded_ts/*.json`, searches for migration variables using the same keyword logic as `build_migration_table_v2.py`, and adds:
- N observations from HDMF raw `.dta` files (via `pyreadstat.read_dta(metadataonly=True)`)
- N obs available for: COL (2018–2025 t3), ECU (2017–2025 m12), PER (2018–2024 a), CHL (2017, 2020, 2022, 2024 a), MEX (2025 t4), USA (2024 a), ESP (2018–2025 a)

Output: `data availability/migration_timeseries_table.xlsx`
- 13 columns: Country | ISO3 | Survey | Year | Period | Migrant ID? | Variable(s) | Question wording | 5yr Residence? | Variable(s) | Question wording | N Observations | Notes
- Color coding same as existing table (green=found, orange=not found, gray=not decodable)
- Rows grouped by country (alternating shading per country block)
- N obs column with right-aligned numeric format

### 4. Updated CLAUDE.md files
- `data availability/CLAUDE.md` — added full "Time-series availability pipeline" section documenting both new scripts, country map, file ranking, and re-run instructions.
- Main `CLAUDE.md` — updated repository layout to include `data availability/` subproject and document network share path.

### 5. Decode run in progress
**Status at session end:** `scan_and_decode_network.py` was running, processing PER 2022.
- **~103 JSONs saved** to `decoded_ts/` out of ~115 expected total
- **Already completed:** ARG (11), BOL (10), BRA (10), CHL (5), COL (11), CRI (11), DOM (8), ECU (11), GTM (2), GUY (5), HND (9), JAM (1), MEX (2), PER 2015–2021 (7), PRY (partially)...
- **Still running:** PER 2022–2024, PRY, SLV, URY

---

## What still needs to be done next session

### Step 1 — Verify the decode completed (or re-run if interrupted)
```bash
cd "data availability"
python scan_and_decode_network.py --list
# Check all expected JSONs exist in decoded_ts/
# If any are missing, re-run:
python scan_and_decode_network.py --force
```

### Step 2 — Build the Excel
```bash
python build_timeseries_table.py
# Output: migration_timeseries_table.xlsx
```

### Step 3 — Review and QA the Excel
After building, check:
- [ ] Do N obs numbers look plausible?
- [ ] Are any "Yes — found" results actually false positives (keyword matched wrong variable)?
- [ ] Countries with DICT_XLSX available (COL 2022/2025, HND 2021–2025, URY 2015–2022, SLV 2015–2020, DOM 2022/2024, GTM 2024/2025, ECU 2020–2024) should show "Yes — found" with actual variable names.
- [ ] Years where only questionnaire PDFs exist (most COL 2015–2021, most PER 2015–2024) will have 0 vars decoded → "Not decodable" in Excel.

### Step 4 — Optional: improve PER coverage
PER dictionaries are in PDF format (pdfplumber returns few vars). The ODS/XLSX dictionaries that exist in the `raw/per/` HDMF folder or in the INEI website would give better results. Alternatively, manual entries could be added for known-available years.

### Step 5 — Optional: add missing countries to PROCEDURES.md
Update the current results table in `PROCEDURES.md` to reflect the time-series data.

---

## Key file locations
| File | Path |
|------|------|
| Scanner script | `data availability/scan_and_decode_network.py` |
| Excel builder script | `data availability/build_timeseries_table.py` |
| Decoded time-series JSONs | `data availability/decoded_ts/` |
| Output Excel | `data availability/migration_timeseries_table.xlsx` (to be created) |
| Session notes | `data availability/SESSION_2026-05-01_migration_timeseries.md` (this file) |

---

## How to re-run from scratch
```bash
# Re-decode all (overwrites existing JSONs)
python scan_and_decode_network.py --force

# Or re-decode one country only
python scan_and_decode_network.py --country URY --force

# Build Excel (always reads from decoded_ts/ — no re-decode needed)
python build_timeseries_table.py
```
