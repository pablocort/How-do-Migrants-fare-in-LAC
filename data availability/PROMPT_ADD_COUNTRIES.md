# Prompt Template — Add Countries to the Migration Availability Table

Use this prompt when you want to extend the migration variable availability analysis to new countries. Paste it into a new Claude Code session (with the `data availability/` folder open as working directory).

---

## Prompt to copy-paste

```
I'm working on the HDMF "How do Migrants Fare in LAC" project. I need to extend the 
migration variable availability analysis to cover additional countries.

## What already exists

The `data availability/` folder has a complete automated system:

- `decode_dictionaries.py` — CLI that reads PDF/XLSX/XLS/ODS survey dictionaries 
  and outputs standardized JSONs to `decoded/[ISO3]_dictionary.json`
- `parsers/` — auto-detecting parsers for each file format
- `build_migration_table_v2.py` — reads decoded JSONs and produces 
  `migration_variable_availability_v2.xlsx`
- `decoded/` — already contains results for: ARG, BOL, BRA, CHL, COL, CRI, DOM, 
  ECU, GTM, GUY, HND, HTI, MEX (BLZ and JAM have no documentation yet)
- `PROCEDURES.md` — full documentation of the system

## New countries to add

I have placed dictionary/questionnaire files in these country folders:

| ISO3 | Country | Survey | Period | Folder | Files added |
|------|---------|--------|--------|--------|-------------|
| NIC  | Nicaragua | EMNV | 2023 | nic/ | [describe files] |
| PAN  | Panama | ENV | 2023 | pan/ | [describe files] |
| [add more rows as needed] |

## What I need you to do

1. **Read `PROCEDURES.md`** to understand the system before touching anything.

2. **Add each new country to the registries** in both scripts:
   - `decode_dictionaries.py` → `COUNTRY_REGISTRY` dict
   - `build_migration_table_v2.py` → `REGISTRY` dict
   
3. **Run the decoder** for each new country:
   ```
   py decode_dictionaries.py --country [ISO3]
   ```
   Run all new countries in parallel (not sequentially).

4. **Inspect the results**:
   - Check `n_vars` — if 0, the parser didn't recognize the format
   - Check `decode_notes` in the JSON to see what happened
   - If 0 variables: sample the file structure and fix the parser
   - **Do not use general survey knowledge** — only what is in the decoded JSON counts

5. **Check for false positives / missed matches** in the migration keyword search:
   - Print all MIG and TIME keyword hits for each new country
   - If a hit is clearly not a migration variable, add it to `MIG_EXCLUDE` or `TIME_EXCLUDE`
   - If a real migration variable is missed, add the relevant phrase to `MIG_KW` or `TIME_KW`

6. **Rebuild the migration table**:
   ```
   py build_migration_table_v2.py
   ```

7. **Report findings**: For each new country, tell me:
   - How many variables were decoded
   - Which variables were found for migration identification and 5-year filter
   - Any parser issues encountered and how they were resolved
   - Whether any variables require manual review

## Strict rules

- Everything must come from the decoded files in `decoded/`. 
  No general knowledge about what a survey "typically" contains.
- If a variable is not in the decoded JSON, report it as NOT FOUND — do not infer.
- Do not modify existing country results when adding new ones.
- Run independent operations (decoding multiple new countries) in parallel.
```

---

## How to customize the prompt

Before pasting, fill in the table under "New countries to add":

- **ISO3**: 3-letter ISO country code (lowercase for folder, uppercase for registry)
- **Survey**: Name of the survey (e.g., EMNV, ENV, ENCO)
- **Period**: Year/wave identifier (e.g., 2023, 2024t1, 2024m12)
- **Folder**: The subfolder name you created (same as ISO3 lowercase)
- **Files added**: Brief description of what you placed in the folder  
  (e.g., "1 XLSX variable dictionary + 1 PDF questionnaire")

## Tips for better results

- **If files are Excel/ODS**: Place the main variable dictionary first. If there are 
  multiple files (one for variables, one for value codes), include both.
  
- **If files are PDF**: The parser will auto-classify. If the PDF is a complex 
  questionnaire (like DHS), mention it so Claude knows to expect fewer variables.
  
- **If you already know the migration variable names** (from prior work on that survey): 
  Mention them so Claude can verify whether they appear in the decoded output.

- **If the country was already attempted** (e.g., an updated dictionary): Add 
  `--force` to the decode command to overwrite the existing JSON.

## What to expect as output

After running the prompt, Claude should:
1. Show variable counts for each new country
2. Report migration keyword hits (variable name + label)
3. Deliver an updated `migration_variable_availability_v2.xlsx` covering all countries
4. Note any countries where decoding failed and what additional files would be needed
