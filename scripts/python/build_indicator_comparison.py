"""
build_indicator_comparison.py
Compares two versions of hdmf_general_indicators.csv (new vs. previous run),
and optionally validates the new CSV against scl_full_data.xlsx chart values.

Sources:
  NEW_CSV  → out/indicator_descriptive/2026-05-19/hdmf_general_indicators.csv
  OLD_CSV  → out/indicator_descriptive/2026-05-11/hdmf_general_indicators.csv
  SCL_DATA → out/scl_full/2026-05-19/scl_full_data.xlsx  (chart validation)

Output:
  out/indicator_descriptive/2026-05-19/indicator_comparison.xlsx   (full detail)
  out/indicator_descriptive/2026-05-19/indicator_comparison.csv    (diff only)
"""

import os, shutil
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).parent.parent

NEW_DATE = "2026-05-19"
OLD_DATE = "2026-05-11"

NEW_CSV  = BASE / "out" / "indicator_descriptive" / NEW_DATE / "hdmf_general_indicators.csv"
OLD_CSV  = BASE / "out" / "indicator_descriptive" / OLD_DATE / "hdmf_general_indicators.csv"
SCL_DATA = BASE / "out" / "scl_full" / NEW_DATE / "scl_full_data.xlsx"
OUT_DIR  = BASE / "out" / "indicator_descriptive" / NEW_DATE
OUT_FILE = OUT_DIR / "indicator_comparison.xlsx"
OUT_CSV  = OUT_DIR / "indicator_comparison.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# PART A: CSV-to-CSV version comparison (new vs. old)
# ---------------------------------------------------------------------------
print(f"Loading NEW CSV  ({NEW_DATE}) …")
new_df = pd.read_csv(NEW_CSV)
print(f"Loading OLD CSV  ({OLD_DATE}) …")
old_df = pd.read_csv(OLD_CSV)

# Merge on common keys
merge_keys = ["country", "period", "migrant_status", "indicator"]
merged_versions = new_df.merge(
    old_df[merge_keys + ["mean"]].rename(columns={"mean": "mean_old"}),
    on=merge_keys,
    how="outer",
    suffixes=("_new", "_old"),
)
merged_versions["mean_new_pct"] = merged_versions["mean"].round(4) * 100 if "mean" in merged_versions.columns else np.nan
# Support both 'mean' (new) and 'mean_new' column names after merge
if "mean" in merged_versions.columns and "mean_new" not in merged_versions.columns:
    merged_versions.rename(columns={"mean": "mean_new"}, inplace=True)
merged_versions["new_pct"]  = (merged_versions["mean_new"]  * 100).round(2)
merged_versions["old_pct"]  = (merged_versions["mean_old"]  * 100).round(2)
merged_versions["diff_pp"]  = (merged_versions["new_pct"] - merged_versions["old_pct"]).round(2)
merged_versions["abs_diff"] = merged_versions["diff_pp"].abs()

# Flag changes
def flag(row):
    if pd.isna(row["mean_old"]):
        return "New row (not in old)"
    if pd.isna(row["mean_new"]):
        return "Dropped (not in new)"
    if pd.isna(row["diff_pp"]):
        return "Cannot compare"
    if row["abs_diff"] < 0.05:
        return "No change (<0.05 pp)"
    if row["abs_diff"] < 0.5:
        return f"Minor change ({row['diff_pp']:+.2f} pp)"
    return f"CHANGE ({row['diff_pp']:+.2f} pp)"

merged_versions["status"] = merged_versions.apply(flag, axis=1)

version_diff = (
    merged_versions
    .sort_values("abs_diff", ascending=False)
    [["country", "period", "migrant_status", "indicator",
      "new_pct", "old_pct", "diff_pp", "status"]]
    .reset_index(drop=True)
)

# Summary stats
n_changed = (merged_versions["abs_diff"] > 0.05).sum()
print(f"  Total rows (new): {len(new_df)} | old: {len(old_df)}")
print(f"  Changed (>0.05 pp): {n_changed} / {len(merged_versions)}")

# Save CSV output (only rows that changed or are new/dropped)
csv_out = merged_versions[
    (merged_versions["abs_diff"] > 0.05) |
    merged_versions["mean_old"].isna() |
    merged_versions["mean_new"].isna()
][["country", "period", "migrant_status", "indicator",
   "new_pct", "old_pct", "diff_pp", "status"]].sort_values("diff_pp", key=abs, ascending=False)
csv_out.to_csv(OUT_CSV, index=False)
print(f"  CSV diff saved: {OUT_CSV}  ({len(csv_out)} rows with changes)")

# ---------------------------------------------------------------------------
# PART B: Chart validation (requires scl_full_data.xlsx — skip if not found)
# ---------------------------------------------------------------------------
if not SCL_DATA.exists():
    print(f"\n[SKIP] {SCL_DATA} not found — skipping chart validation.")
    print("Run scl_presentation.py first if you need chart validation.")
    # Write Excel with version diff only
    with pd.ExcelWriter(OUT_FILE, engine="openpyxl") as writer:
        version_diff.to_excel(writer, sheet_name=f"version_diff_{NEW_DATE[:7]}", index=False)
        csv_out.to_excel(writer, sheet_name="changes_only", index=False)
    print(f"\nOutput: {OUT_FILE}")
    import sys; sys.exit(0)

# ---------------------------------------------------------------------------
# Country name → code, and wave mapping (for chart validation)
# ---------------------------------------------------------------------------
COUNTRY_NAME_TO_CODE = {
    "Colombia": "COL", "Peru": "PER", "Chile": "CHL",
    "Ecuador": "ECU", "Spain": "ESP",
}

DB_RECENT_WAVES = {"COL": "2025t3", "PER": "2024a", "CHL": "2024a",
                   "ECU": "2025m12", "ESP": "2025a"}
DB_EARLY_WAVES  = {"COL": "2018t3", "PER": "2018a", "CHL": "2017a",
                   "ECU": "2018m12", "ESP": "2018a"}

# Chart indicator label → canonical key
CHART_LABEL_TO_KEY = {
    "Working age (15–64) % of pop.":        "working_age",
    "Participation rate % of 16–64":        "participation",
    "Tertiary education % of 16–64":        "tertiary",
    "Unemployment % of active pop.":             "unemployment",
    "Inactivity % of 16–64":               "inactivity",
    "Informality % of employed":                 "informality",
    "Part-time % of employed":                   "parttime",
    "Long hours (50+) % of employed":            "long_hours",
}

# CSV indicator name → chart key (note: formal_ci needs inversion)
CSV_TO_CHART = {
    "pea_ci":      "participation",
    "inactivo_ci": "inactivity",
    "desemp_ci":   "unemployment",
    "formal_ci":   "informality",
    "parcial_ci":  "parttime",
    "lhours_ci":   "long_hours",
    "edusup_ci":   "tertiary",
    "wap_ci":      "working_age",
    "emp_ci":      "employment",
}

# ---------------------------------------------------------------------------
# 1. Parse Country_Breakdown from scl_full_data.xlsx
# ---------------------------------------------------------------------------
print("Parsing scl_full_data.xlsx …")
tmp = SCL_DATA.parent / "_tmp_cmp.xlsx"
shutil.copy2(SCL_DATA, tmp)

xl = pd.ExcelFile(tmp)
raw = xl.parse("Country_Breakdown", header=None)
xl.close()
os.remove(tmp)

# Row 0: wide header  (Unnamed: 0, Unnamed: 1, "Recent (2024–25)", …)
# Row 1: sub-header   (Indicator, Country, Venezuelan (%), Native (%), …)
# Rows 2+: data       (indicator label or NaN, country name, values…)
#
# Column layout (0-based):
#  0 = Indicator label (only on first row of each group)
#  1 = Country name
#  2 = Recent Venezuelan %
#  3 = Recent Native %
#  4 = Early Venezuelan %
#  5 = Early Native %
#  (6, 7 = gaps — we ignore)

data_rows = raw.iloc[2:].copy()   # skip header rows
data_rows.columns = range(data_rows.shape[1])

# Forward-fill the indicator label (col 0)
data_rows[0] = data_rows[0].ffill()

# Drop rows where country is NaN (spacer rows and footnote rows)
data_rows = data_rows[data_rows[1].notna()].copy()
data_rows = data_rows[data_rows[1].apply(lambda x: str(x).strip() in COUNTRY_NAME_TO_CODE)].copy()

chart_rows = []
for _, row in data_rows.iterrows():
    ind_label = str(row[0]).strip()
    country_name = str(row[1]).strip()
    country = COUNTRY_NAME_TO_CODE.get(country_name)
    ind_key  = CHART_LABEL_TO_KEY.get(ind_label)
    if country is None or ind_key is None:
        continue

    for period_lbl, grp, col_idx in [
        ("recent", "Venezuela", 2),
        ("recent", "Native",    3),
        ("early",  "Venezuela", 4),
        ("early",  "Native",    5),
    ]:
        val = row[col_idx]
        try:
            val = float(val)
        except (ValueError, TypeError):
            val = np.nan
        period = DB_RECENT_WAVES[country] if period_lbl == "recent" else DB_EARLY_WAVES[country]
        year   = int(period[:4])
        chart_rows.append({
            "country":         country,
            "period":          period,
            "year":            year,
            "period_in_chart": period_lbl,
            "group":           grp,
            "indicator":       ind_key,
            "chart_value_%":   round(val, 2) if pd.notna(val) else np.nan,
            "source_sheet":    "Country_Breakdown",
        })

# ---------------------------------------------------------------------------
# 2. Parse Pooled_Indicators from scl_full_data.xlsx (LAC-5 aggregate)
# ---------------------------------------------------------------------------
tmp = SCL_DATA.parent / "_tmp_cmp2.xlsx"
shutil.copy2(SCL_DATA, tmp)
xl2 = pd.ExcelFile(tmp)
raw_pool = xl2.parse("Pooled_Indicators", header=None)
xl2.close()
os.remove(tmp)

# Row 0: period header   (NaN, "Recent (2024–25)", NaN, "Early (2017–18)", …)
# Row 1: group header    (Indicator, Venezuelan (%), Native (%), …)
# Rows 2+: data

POOLED_IND_LABEL_TO_KEY = {
    "Working age (15–64) (% of total pop.)":                          "working_age",
    "Participation rate (% of working-age pop., 16–64)":              "participation",
    "Employment rate (% of working-age pop., 16–64)":                 "employment",
    "Tertiary education (% of working-age pop., post-secondary+)":        "tertiary",
    "Unemployment rate (% of active pop., LAC-4)":                        "unemployment",
    "Inactivity rate (% of working-age pop.)":                            "inactivity",
    "Informality (% of employed pop., LAC-4)":                            "informality",
    "Part-time work (% of employed pop.)":                                "parttime",
    "Long hours (50+) (% of employed pop.)":                              "long_hours",
}

pool_rows = []
for _, row in raw_pool.iloc[2:].iterrows():
    ind_label = str(row[0]).strip() if pd.notna(row[0]) else ""
    ind_key = POOLED_IND_LABEL_TO_KEY.get(ind_label)
    if ind_key is None:
        continue
    # Cols: 0=indicator, 1=Ven recent, 2=Nat recent, 3=Ven early, 4=Nat early, ...
    for period_lbl, grp, col_idx in [
        ("recent", "Venezuela", 1),
        ("recent", "Native",    2),
        ("early",  "Venezuela", 3),
        ("early",  "Native",    4),
    ]:
        val = row[col_idx]
        try:
            val = float(val)
        except (ValueError, TypeError):
            val = np.nan
        pool_rows.append({
            "country":         "LAC5_pooled",
            "period":          "2024-25" if period_lbl == "recent" else "2017-18",
            "year":            2024 if period_lbl == "recent" else 2017,
            "period_in_chart": period_lbl,
            "group":           grp,
            "indicator":       ind_key,
            "chart_value_%":   round(val, 2) if pd.notna(val) else np.nan,
            "source_sheet":    "Pooled_Indicators",
        })

all_chart = pd.DataFrame(chart_rows + pool_rows)
print(f"  Chart rows parsed: {len(all_chart)}  "
      f"({len(chart_rows)} country + {len(pool_rows)} pooled)")

# ---------------------------------------------------------------------------
# 3. Load new CSV for chart validation
# ---------------------------------------------------------------------------
print(f"Validating {NEW_DATE} CSV against scl_full_data.xlsx …")
csv = pd.read_csv(NEW_CSV)
csv["indicator_key"] = csv["indicator"].map(CSV_TO_CHART)
csv = csv[csv["indicator_key"].notna()].copy()

# Invert formal_ci → informality
mask_formal = csv["indicator"] == "formal_ci"
csv["csv_value_%"] = csv["mean"] * 100
csv.loc[mask_formal, "csv_value_%"] = 100 - csv.loc[mask_formal, "csv_value_%"]
csv["csv_value_%"] = csv["csv_value_%"].round(2)

csv_flat = csv[["country", "period", "migrant_status", "indicator_key", "csv_value_%"]].rename(
    columns={"migrant_status": "group", "indicator_key": "indicator"}
)

# ---------------------------------------------------------------------------
# 4. Merge
# ---------------------------------------------------------------------------
country_chart = all_chart[all_chart["country"] != "LAC5_pooled"].copy()
merged = country_chart.merge(
    csv_flat,
    on=["country", "period", "group", "indicator"],
    how="left",
)

merged["diff_csv_minus_chart"] = (merged["csv_value_%"] - merged["chart_value_%"]).round(2)

def make_note(row):
    if pd.isna(row["chart_value_%"]):
        return "Chart: masked/unavailable"
    if pd.isna(row["csv_value_%"]):
        return "CSV value missing"
    diff = row["diff_csv_minus_chart"]
    return "Match" if abs(diff) < 0.1 else f"Diff {diff:+.2f} pp"

merged["note"] = merged.apply(make_note, axis=1)

all_pairs = merged[[
    "country", "period", "year", "period_in_chart", "group",
    "indicator", "csv_value_%", "chart_value_%", "diff_csv_minus_chart", "note"
]]

# ---------------------------------------------------------------------------
# 5. Summary by indicator
# ---------------------------------------------------------------------------
summary_rows = []
for ind, grp in all_pairs.groupby("indicator"):
    pairs = grp.dropna(subset=["diff_csv_minus_chart", "chart_value_%"])
    perfect = (pairs["diff_csv_minus_chart"].abs() < 0.1).sum()
    summary_rows.append({
        "indicator":        ind,
        "n_pairs":           len(grp),
        "n_matched_lt01":    int(perfect),
        "mean_abs_diff_pp":  round(pairs["diff_csv_minus_chart"].abs().mean(), 2) if len(pairs) else np.nan,
        "max_abs_diff_pp":   round(pairs["diff_csv_minus_chart"].abs().max(), 2)  if len(pairs) else np.nan,
        "n_diff_gt1pp":      int((pairs["diff_csv_minus_chart"].abs() > 1).sum()),
    })
summary_df = pd.DataFrame(summary_rows).sort_values("mean_abs_diff_pp", ascending=False)

# ---------------------------------------------------------------------------
# 6. Top discrepancies
# ---------------------------------------------------------------------------
worst = (
    all_pairs.dropna(subset=["diff_csv_minus_chart"])
    .assign(abs_diff=lambda d: d["diff_csv_minus_chart"].abs())
    .query("abs_diff > 0.1")
    .sort_values("abs_diff", ascending=False)
    .drop(columns="abs_diff")
    .reset_index(drop=True)
)

# ---------------------------------------------------------------------------
# 7. Pivot
# ---------------------------------------------------------------------------
pivot_df = all_pairs.pivot_table(
    index=["indicator", "country", "group"],
    columns=["period_in_chart"],
    values=["chart_value_%", "csv_value_%", "diff_csv_minus_chart"],
    aggfunc="first",
)

# ---------------------------------------------------------------------------
# 8. Write Excel (version diff + chart validation)
# ---------------------------------------------------------------------------
print(f"Writing {OUT_FILE} …")
with pd.ExcelWriter(OUT_FILE, engine="openpyxl") as writer:
    version_diff.to_excel(writer, sheet_name=f"version_diff_{NEW_DATE[:7]}",  index=False)
    csv_out.to_excel(     writer, sheet_name="changes_only",                  index=False)
    all_pairs.to_excel(  writer, sheet_name="chart_validation_pairs",          index=False)
    worst.to_excel(      writer, sheet_name="chart_discrepancies",             index=False)
    summary_df.to_excel( writer, sheet_name="summary_by_indicator",            index=False)
    pivot_df.to_excel(   writer, sheet_name="pivot_country_period")

print("Done.")
print()
print(f"Version comparison ({OLD_DATE} -> {NEW_DATE}):")
print(f"  Changed rows (>0.05 pp): {n_changed}")
if len(csv_out) > 0:
    print("\nTop changes:")
    print(csv_out.head(20)[["country","period","migrant_status","indicator","new_pct","old_pct","diff_pp"]].to_string(index=False))
print()
print("Chart validation summary by indicator:")
print(summary_df.to_string(index=False))
print(f"\nTotal chart discrepancies (>0.1 pp): {len(worst)}")
