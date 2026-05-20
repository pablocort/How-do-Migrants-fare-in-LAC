"""
build_old_comparison.py
Compares HDMF-tables Old document.xlsx (2021 publication) against
hdmf_general_indicators.csv (2026-05-08, current pipeline).

Output: out/indicator_descriptive/2026-05-08/old_vs_new_comparison.xlsx
"""

import sys, io, shutil, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import numpy as np
from pathlib import Path

BASE    = Path(__file__).parent.parent
OLD_SRC = BASE / "out/indicator_descriptive/2026-05-08/HDMF-tables Old document.xlsx"
NEW_CSV = BASE / "out/indicator_descriptive/2026-05-08/hdmf_general_indicators.csv"
OUT_XL  = BASE / "out/indicator_descriptive/2026-05-08/old_vs_new_comparison.xlsx"

# ---------------------------------------------------------------------------
# 1. Parse old document
# ---------------------------------------------------------------------------
tmp = BASE / "out/indicator_descriptive/2026-05-08/_tmp_old_cmp.xlsx"
shutil.copy2(OLD_SRC, tmp)
xl  = pd.ExcelFile(tmp)
df  = xl.parse('HDMF tables', header=None)
xl.close()
os.remove(tmp)

def _safe_float(v):
    try:
        return round(float(v), 2)
    except Exception:
        return np.nan

# Country → (native_col, foreign_born_col, old_survey_label)
COUNTRY_COLS = {
    'CHL': (10, 11, 'CASEN 2020'),
    'COL': (13, 14, 'GEIH 2021'),
    'ECU': (22, 23, 'ENEMDU 2021'),
    'PER': (34, 35, 'ENAHO 2021'),
}

# (row_idx, readable_label, new_csv_indicator, note_on_definition)
IND_ROWS = [
    (43, 'Share with a job',                     'emp_ci',      'Share of working-age pop (16-64) with a job'),
    (44, 'Participation rate',                   'pea_ci',      'Share of working-age pop (16-64) in active pop'),
    (45, 'Inactivity rate',                      'inactivo_ci', 'Share of working-age pop (16-64) economically inactive'),
    (46, 'Unemployment*',                        'desemp_ci',   '*OLD = share of working-age unemployed / NEW = share of active pop unemployed (rate)'),
    (52, 'Informality (country def)',            'formal_ci',   'OLD = informal share; NEW = 1 - formal_ci (formal contract)'),
    (56, 'Long hours (>=50 hrs/week)',           'lhours_ci',   'Share of employed working 50+ hours'),
    (58, 'Part-time (<30 hrs/week)',             'parcial_ci',  'Share of employed working <30 hours (OLD) vs parcial_ci (NEW)'),
    (67, 'Higher education (ISCED 5-8)',         'edusup_ci',   'Share of working-age with post-secondary education'),
]

old_rows = []
for row_idx, label, new_ind, note in IND_ROWS:
    for country, (nat_col, for_col, survey) in COUNTRY_COLS.items():
        nat_val = _safe_float(df.loc[row_idx, nat_col])
        for_val = _safe_float(df.loc[row_idx, for_col])
        old_rows.append({
            'country':        country,
            'old_survey':     survey,
            'indicator':      new_ind,
            'indicator_label': label,
            'definition_note': note,
            'old_native_%':   nat_val,
            'old_foreignborn_%': for_val,
        })

old_df = pd.DataFrame(old_rows)

# ---------------------------------------------------------------------------
# 2. Load new CSV — most recent wave per country, Native and Venezuela groups
# ---------------------------------------------------------------------------
csv = pd.read_csv(NEW_CSV)

NEW_RECENT = {'CHL': '2024a', 'COL': '2025t3', 'ECU': '2025m12', 'PER': '2024a'}

# Invert formal_ci for informality
csv = csv.copy()
csv.loc[csv['indicator'] == 'formal_ci', 'mean'] = 1 - csv.loc[csv['indicator'] == 'formal_ci', 'mean']

new_pivot = (
    csv[csv['indicator'].isin([r[2] for r in IND_ROWS])]
    .assign(match=lambda d: d.apply(
        lambda r: NEW_RECENT.get(r['country']) == r['period'], axis=1))
    .query('match')
    [['country', 'period', 'migrant_status', 'indicator', 'mean']]
    .pivot_table(index=['country', 'period', 'indicator'],
                 columns='migrant_status', values='mean')
    .reset_index()
)
new_pivot.columns.name = None
new_pivot['new_native_%']    = (new_pivot.get('Native',    np.nan) * 100).round(2)
new_pivot['new_venezuela_%'] = (new_pivot.get('Venezuela', np.nan) * 100).round(2)

# ---------------------------------------------------------------------------
# 3. Merge old vs new
# ---------------------------------------------------------------------------
merged = old_df.merge(
    new_pivot[['country', 'period', 'indicator', 'new_native_%', 'new_venezuela_%']],
    on=['country', 'indicator'],
    how='left',
)

merged['new_survey'] = merged['country'].map({
    'CHL': 'CASEN 2024', 'COL': 'GEIH 2025-t3',
    'ECU': 'ENEMDU 2025-m12', 'PER': 'ENAHO 2024',
})

# Diffs
merged['diff_native_%']    = (merged['new_native_%']    - merged['old_native_%']).round(2)
merged['diff_venezuela_%'] = (merged['new_venezuela_%'] - merged['old_foreignborn_%']).round(2)

# Final column order
out_cols = [
    'country', 'indicator_label', 'indicator',
    'old_survey',    'old_native_%',    'old_foreignborn_%',
    'new_survey',    'new_native_%',    'new_venezuela_%',
    'diff_native_%', 'diff_venezuela_%',
    'definition_note',
]
out_df = merged[out_cols].sort_values(['indicator', 'country'])

# ---------------------------------------------------------------------------
# 4. Summary pivot: indicator × country
# ---------------------------------------------------------------------------
summary_nat = out_df.pivot_table(
    index='indicator_label', columns='country',
    values='diff_native_%', aggfunc='first'
).round(2)
summary_ven = out_df.pivot_table(
    index='indicator_label', columns='country',
    values='diff_venezuela_%', aggfunc='first'
).round(2)

# ---------------------------------------------------------------------------
# 5. Write Excel
# ---------------------------------------------------------------------------
print(f"Writing {OUT_XL} ...")
with pd.ExcelWriter(OUT_XL, engine='openpyxl') as writer:
    out_df.to_excel(writer, sheet_name='all_pairs', index=False)
    summary_nat.to_excel(writer, sheet_name='diff_native_(new-old)')
    summary_ven.to_excel(writer, sheet_name='diff_venezuela_(new-old)')

print("Done.\n")
print("=== Native differences (new - old) ===")
print(summary_nat.to_string())
print("\n=== Venezuela vs Foreign-born differences (new - old) ===")
print(summary_ven.to_string())
