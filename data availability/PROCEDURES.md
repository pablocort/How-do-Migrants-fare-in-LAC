# Data Availability — Procedures & System Documentation

## What this system does

Converts heterogeneous survey dictionaries (PDF, XLSX, XLS, ODS) from LAC country folders into standardized JSON files, then searches those JSONs for migration-relevant variables and produces an Excel availability table. **Everything is grounded strictly in decoded files — no general survey knowledge is used.**

---

## Folder structure

```
data availability/
├── CLAUDE.md / PROCEDURES.md / PROMPT_ADD_COUNTRIES.md
├── parsers/              ← PDF/XLSX/ODS parser modules
├── raw/                  ← country documentation files (raw/arg/, raw/col/, …)
├── decoded/              ← single-year decoded JSONs (one per country)
├── decoded_ts/           ← time-series decoded JSONs (one per country-year-period)
├── output/               ← all Excel outputs
├── sessions/             ← session notes
└── check/                ← diagnostic/debug scripts
```

## System components

| File | Purpose |
|------|---------|
| `decode_dictionaries.py` | CLI: decodes all `raw/[iso3]/` folders → `decoded/[ISO3]_dictionary.json` |
| `scan_and_decode_network.py` | Scans IDB network share (Z:\survey) → `decoded_ts/` |
| `decode_caribbean_lastwave.py` | Decodes last wave per Caribbean country via .dta metadata or docs |
| `parsers/parse_xlsx.py` | Handles XLSX/XLS with 5-layout auto-detection |
| `parsers/parse_ods.py` | Handles ODS (Ecuador ENEMDU style) |
| `parsers/parse_pdf.py` | Handles PDF: TABLE_DICT / QUESTIONNAIRE / BULLETIN / ARG-text / DDI |
| `build_migration_table_v2.py` | Reads `decoded/` JSONs → `output/migration_variable_availability_v2.xlsx` |
| `build_timeseries_table.py` | Reads `decoded_ts/` JSONs → `output/migration_timeseries_table.xlsx` |
| `build_caribbean_timeseries_table.py` | Caribbean subset → `output/caribbean_migration_timeseries.xlsx` |

---

## Standard JSON output schema

```json
{
  "iso3": "COL",
  "survey": "GEIH",
  "period": "2025",
  "source_files": ["DICCIONARIO_GEIH_2025.xlsx"],
  "tables": ["Personas", "Hogares"],
  "variables": [
    {
      "name": "P6020",
      "label": "Sexo",
      "type": "NUMBER",
      "table": "Personas",
      "value_codes": {"1": "Hombre", "2": "Mujer"}
    }
  ],
  "decode_notes": ["Sheet 'Plantilla Diccionario de Datos' used", "515 rows processed"]
}
```

---

## How to run

### Decode a single country
```
cd "data availability"
py decode_dictionaries.py --country COL
```

### Decode all countries (overwrites existing)
```
py decode_dictionaries.py --all --force
```

### List current status
```
py decode_dictionaries.py --list
```

### Rebuild migration table (after decoding)
```
py build_migration_table_v2.py
```

---

## Adding a new country

### Step 1 — Create the country folder and add files
```
data availability/
└── raw/
    └── [iso3]/      ← lowercase 3-letter ISO code
        ├── dictionary.xlsx   ← variable dictionary (any format)
        └── questionnaire.pdf ← questionnaire (optional)
```

### Step 2 — Add country to the registry in `decode_dictionaries.py`
```python
COUNTRY_REGISTRY = {
    ...
    "NIC": {"name": "Nicaragua", "survey": "EMNV", "period": "2024", "folder": "nic"},
    ...
}
```

### Step 3 — Add country to the registry in `build_migration_table_v2.py`
```python
REGISTRY = {
    ...
    "NIC": {"name": "Nicaragua", "survey": "EMNV", "period": "2024"},
    ...
}
```

### Step 4 — Decode and check
```
py decode_dictionaries.py --country NIC
```
Verify the JSON has meaningful variable labels (not just question numbers). If `n_vars == 0`, the parser didn't recognize the file format — see Troubleshooting below.

### Step 5 — Rebuild migration table
```
py build_migration_table_v2.py
```

---

## PDF parser classification logic

The parser (`parsers/parse_pdf.py`) classifies each PDF into one of three types before extracting:

| Type | Detection | Extractor |
|------|-----------|-----------|
| `TABLE_DICT` | Embedded tables with dict-like headers (variable/campo/descripcion/label) in first 25 pages | `extract_table_dict()` → pdfplumber table extraction |
| `QUESTIONNAIRE` | P-code patterns / numbered questions / lowercase module codes / section markers | `extract_questionnaire()` → regex on full text |
| `BULLETIN` | Neither of the above | Returns 0 variables with a note |

**Fallback chain within TABLE_DICT:**
1. pdfplumber table extraction
2. If result names look like value codes (all-numeric) → ARG text-block extractor (`VARNAME N(len) Description` lines)
3. If still < 5 vars → DDI table extractor (Bolivia EH style)

**Fallback chain within QUESTIONNAIRE:**
1. Regex variable code extraction
2. If most names are numeric → ARG text-block extractor
3. If still < 5 vars → DDI table extractor

### Known survey-format mappings

| Country | Format | Outcome |
|---------|--------|---------|
| ARG EPH | PDF: text-flow `VARNAME N(len) Description` | ARG text extractor → 220 vars |
| BOL EH | PDF: DDI format with variable tables from page 19 | DDI table extractor → 372 vars |
| BRA PNADC | XLS: fixed-width with question-number labels only | 448 vars, POOR_LABELS status |
| CHL CASEN | PDF: questionnaire with lowercase module codes (`r1a`, `h7a`) | QUESTIONNAIRE extractor → 201 vars |
| COL GEIH | XLSX: "Plantilla Diccionario de Datos" sheet, COL_GEIH layout | 515 vars |
| CRI ENAHO | PDF: questionnaire with letter+number codes (`B1.`, `C2a.`) | QUESTIONNAIRE extractor → 161 vars |
| DOM ENFT | XLSX: CAMPO/VALOR/DESCRIPCION layout | 290 vars |
| ECU ENEMDU | ODS: multi-sheet, metadata header block before variable table | 210 vars |
| GTM ENEIC | XLSX: variable/etiqueta/nivel layout | 280 vars |
| GUY GLFS | PDF: statistical bulletin, no variable list | 0 vars (BULLETIN) |
| HND EPHPM | XLSX: two-sheet pattern (Variables + Valores) | 474 vars |
| HTI DHS | PDF: multi-column DHS questionnaire, complex layout | 26 vars (POOR_LABELS) |
| MEX ENOE | PDF: 300-page ENIGH database description with table TOC | TABLE_DICT extractor → 1073 vars |

---

## Migration table — keyword logic

The migration table (`build_migration_table_v2.py`) searches decoded variables using two keyword sets with exclusion lists.

### Migration identification (`MIG_KW`)
Keywords that signal place/country of birth, nationality, or explicit migrant status:
- "lugar de nac", "pais de nac", "país de nac"
- "donde nació", "dónde nació", "¿dónde nació"
- "entidad o país de nac" (MEX style)
- "país de nacionalidad", "pais de nacionalidad" (CHL style)
- "zona de nacimiento" (DOM style)
- "migrante", "inmigrante", "migrant"
- "nascimento", "naturalidade", "estrangeiro" (Portuguese)
- "born abroad", "foreign born"

### 5-year residence filter (`TIME_KW`)
Keywords that signal time-of-residence or 5-year retrospective questions:
- "tiempo de resid", "cuánto tiempo reside"
- "vivía hace", "hace 5 años"
- "año de llegada", "mes de llegada", "fecha de llegada"
- "desde qué año vive", "desde qué año y mes vive" (BOL style)
- "período llegó", "llegó a vivir" (CHL style)
- "tempo de resid", "morando há", "chegada ao" (Portuguese)

### Status codes in the Excel output

| Color | Code | Meaning |
|-------|------|---------|
| Green | Yes — found | Variable keyword-matched in decoded JSON |
| Orange | Not found | Dictionary decoded but no matching variable |
| Gray | Not decodable | Decoder returned 0 vars or labels are question numbers |
| Gray | No documentation | No dictionary/questionnaire file in country folder |

---

## Troubleshooting

**0 variables extracted from a PDF:**
1. Run `sample_pdfs.py` (or write an inline script) to inspect page text and tables
2. Check which classification was used: look at `decode_notes` in the JSON
3. If BULLETIN but should be TABLE_DICT: the variable tables start after page 25 — extend `scan_indices` in `_classify_pdf_type()`
4. If QUESTIONNAIRE but variable names are all digits: ARG text fallback should trigger — check that the `VARNAME N(len) Description` pattern matches your format
5. If DDI format: check that the header row contains "name", "nombre", "variable", "label", or "etiqueta"

**False positives in migration keyword search:**
- Add the false-positive phrase to `MIG_EXCLUDE` or `TIME_EXCLUDE` in `build_migration_table_v2.py`
- Run `py build_migration_table_v2.py` to rebuild (does not re-decode)

**BRA PNADC labels are just question numbers:**
- Status is `POOR_LABELS` — no keyword search is performed
- To fix: obtain the actual data dictionary (not the XLS with question numbers) and add it to `bra/`

---

## Current results (as of April 2026)

| Country | Survey | Vars decoded | Migrant ID | 5+ years |
|---------|--------|-------------|------------|----------|
| Argentina | EPH 2023 | 220 | CH15 (¿Dónde nació?) | CH16 (hace 5 años) |
| Belize | — | — | No documentation | No documentation |
| Bolivia | EH 2024 | 372 | Not found | s01b_11a (hace 5 años) |
| Brazil | PNADC 2025 | 448 | Not decodable | Not decodable |
| Chile | CASEN 2024 | 201 | r1a (nacionalidad + llegada) | r1a (período llegó) |
| Colombia | GEIH 2025 | 515 | P3373 (Dónde nació) | P3382 (hace 5 años) |
| Costa Rica | ENAHO 2025 | 161 | Not found | Not found |
| Dominican Rep. | ENFT 2024 | 290 | ZONA_NACIMIENTO | TIEMPO_RESIDENCIA |
| Ecuador | ENEMDU 2025 | 210 | p15aa/p15ab (Lugar de nacimiento) | Not found |
| Guatemala | ENEIC 2025 | 280 | Not found | Not found |
| Guyana | GLFS 2021 | 0 | Bulletin | Bulletin |
| Honduras | EPHPM 2025 | 474 | Not found | Not found |
| Haiti | DHS 2017 | 26 | Not decodable | Not decodable |
| Jamaica | — | — | No documentation | No documentation |
| Mexico | ENOE 2024 | 1073 | pais_nac (País de nacimiento) | Not found |

---

## Libraries required

```
pip install pdfplumber openpyxl odfpy xlrd
```
pandas is assumed already installed. All others: `pip install <name>`.
