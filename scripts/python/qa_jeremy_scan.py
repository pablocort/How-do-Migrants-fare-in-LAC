"""
qa_jeremy_scan.py — QA Analyst Phase 1: Detect anomalies in jeremy_caribbean.xlsx
Reads Excel + BID.dta files directly to cross-check all indicator values.
"""

import sys, pickle, warnings
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

BASE = Path(__file__).parent.parent
XL_FILE   = BASE / "out" / "jeremy" / "2026-05-13" / "jeremy_caribbean.xlsx"
CACHE     = BASE / "bases armo" / "armo" / "_hdmf_cache.pkl"
BID_DIR   = BASE / "bases armo" / "armo"

CARIBBEAN = ["BLZ", "BRB", "DOM"]
COUNTRY_LABEL = {"BLZ": "Belize", "BRB": "Barbados", "DOM": "Dominican Republic"}
RECENT_WAVES  = {"BLZ": "2024m9", "BRB": "2023a", "DOM": "2024t4"}

# ===========================================================================
# 1. Read Excel — print all values
# ===========================================================================
print("=" * 70)
print("STEP 1 — EXCEL CONTENTS")
print("=" * 70)

try:
    import shutil, tempfile
    tmp = tempfile.mktemp(suffix=".xlsx")
    shutil.copy2(XL_FILE, tmp)
    xl = pd.ExcelFile(tmp)
    print(f"Sheets: {xl.sheet_names}\n")
    sheet_data = {}
    for sheet in xl.sheet_names:
        df = xl.parse(sheet, header=None)
        sheet_data[sheet] = df
        print(f"--- Sheet: {sheet} ---")
        print(df.to_string())
        print()
except Exception as e:
    print(f"  Could not read Excel (may be locked): {e}")
    print("  Skipping Excel display — using cache for all checks.\n")

# ===========================================================================
# 2. Load cache and compute indicators directly
# ===========================================================================
print("=" * 70)
print("STEP 2 — DIRECT COMPUTATION FROM CACHE (ground truth)")
print("=" * 70)

print("Loading cache...")
with open(CACHE, "rb") as fh:
    _cache = pickle.load(fh)
data = _cache["data"]

df_car = data[data["pais_c"].isin(CARIBBEAN)].copy()
print(f"Caribbean rows in cache: {len(df_car):,}\n")

for c in CARIBBEAN:
    sub = df_car[df_car["pais_c"] == c]
    periods = sorted(sub["periodo_c"].unique())
    print(f"  {c}: {len(sub):,} rows, periods: {periods}")
    for col in ["migrante_ci", "emp_ci", "desemp_ci", "pea_ci", "inactivo_ci", "formal_ci", "edu_hdmf", "factor_ci"]:
        if col in sub.columns:
            vc = sub[col].value_counts(dropna=False).to_dict()
            print(f"    {col}: {vc}")
        else:
            print(f"    {col}: NOT IN CACHE")
    print()

# ===========================================================================
# 3. Weighted average helper
# ===========================================================================
def wavg(series, weights):
    v = pd.to_numeric(series, errors="coerce").to_numpy(float)
    w = pd.to_numeric(weights, errors="coerce").to_numpy(float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if mask.sum() < 5:
        return np.nan
    return float(np.dot(w[mask], v[mask]) / w[mask].sum())

# ===========================================================================
# 4. Reproduce each indicator from cache
# ===========================================================================
print("=" * 70)
print("STEP 3 — REPRODUCED INDICATORS (match to Excel)")
print("=" * 70)

wa_mask_all = df_car["edad_ci"].between(16, 64)
df_car["_inact_r"]  = df_car["inactivo_ci"].where(wa_mask_all, np.nan)
df_car["_desemp_r"] = (
    df_car["desemp_ci"]
    .where(wa_mask_all, np.nan)
    .where(df_car["pea_ci"] == 1, np.nan)
)
df_car["_informal"] = np.where(
    df_car["emp_ci"] == 1,
    1 - pd.to_numeric(df_car["formal_ci"], errors="coerce"),
    np.nan
)
df_car["_wap"] = df_car["edad_ci"].between(15, 64).astype(int)

INDICATORS_MAP = {
    "unemployment": "_desemp_r",
    "informality":  "_informal",
    "inactivity":   "_inact_r",
    "wap":          "_wap",
}

results = {}
for ind, col in INDICATORS_MAP.items():
    results[ind] = {}
    print(f"\n  {ind.upper()} (col={col}):")
    for country in CARIBBEAN:
        dfc = df_car[df_car["pais_c"] == country]
        for period in sorted(dfc["periodo_c"].unique()):
            dfp = dfc[dfc["periodo_c"] == period]
            nat_n  = (dfp["migrante_ci"] == 0).sum()
            mig_n  = (dfp["migrante_ci"] == 1).sum()
            nat_mu = wavg(dfp.loc[dfp["migrante_ci"] == 0, col],
                          dfp.loc[dfp["migrante_ci"] == 0, "factor_ci"])
            mig_mu = wavg(dfp.loc[dfp["migrante_ci"] == 1, col],
                          dfp.loc[dfp["migrante_ci"] == 1, "factor_ci"])
            nat_pct = round(nat_mu * 100, 2) if pd.notna(nat_mu) else np.nan
            mig_pct = round(mig_mu * 100, 2) if pd.notna(mig_mu) else np.nan
            results[ind][(country, period)] = {"Native": nat_pct, "Migrant": mig_pct,
                                               "n_nat": nat_n, "n_mig": mig_n}
            print(f"    {country} {period}:  Native={nat_pct}%  Migrant={mig_pct}%  "
                  f"(n_nat={nat_n}, n_mig={mig_n})")

# ===========================================================================
# 5. Education breakdown
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 4 — EDUCATION DISTRIBUTION (most recent wave)")
print("=" * 70)

EDU_3CAT_MAP = {
    1: "Primary or less", 2: "Primary or less", 3: "Primary or less",
    4: "Secondary",       5: "Secondary",       6: "Secondary",
    7: "Higher education", 8: "Higher education",
    9: "Higher education", 10: "Higher education",
}

for country, period in RECENT_WAVES.items():
    dfc = df_car[(df_car["pais_c"] == country) & (df_car["periodo_c"] == period)].copy()
    dfc["edu_3cat"] = pd.to_numeric(dfc["edu_hdmf"], errors="coerce").map(EDU_3CAT_MAP)
    valid = dfc[dfc["edu_3cat"].notna() & dfc["factor_ci"].notna()]
    print(f"\n  {COUNTRY_LABEL[country]} ({period}):")
    for grp_label, grp_code in [("Native", 0), ("Migrant", 1)]:
        dfg   = valid[valid["migrante_ci"] == grp_code]
        total = dfg["factor_ci"].sum()
        print(f"    {grp_label} (N raw={len(dfg)}, total wgt={total:,.0f}):")
        for cat in ["Primary or less", "Secondary", "Higher education"]:
            cat_w = dfg.loc[dfg["edu_3cat"] == cat, "factor_ci"].sum()
            pct   = round(cat_w / total * 100, 2) if total > 0 else np.nan
            print(f"      {cat}: {pct}%")

# ===========================================================================
# 6. Anomaly detection rules
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 5 — ANOMALY DETECTION (7 rules)")
print("=" * 70)

PLAUSIBLE = {
    "unemployment": (0.005, 0.40),
    "informality":  (0.10,  0.98),
    "inactivity":   (0.10,  0.70),
    "wap":          (0.30,  0.80),
}

flags = []
MIN_N = 30  # Rule 1 threshold

for ind, col in INDICATORS_MAP.items():
    lo, hi = PLAUSIBLE.get(ind, (None, None))
    prev_by_group = {}

    for country in CARIBBEAN:
        dfc = df_car[df_car["pais_c"] == country]
        for period in sorted(dfc["periodo_c"].unique()):
            dfp = dfc[dfc["periodo_c"] == period]
            for grp_label, grp_code in [("Native", 0), ("Migrant", 1)]:
                sub = dfp[dfp["migrante_ci"] == grp_code]
                s   = pd.to_numeric(sub[col], errors="coerce")
                w   = pd.to_numeric(sub["factor_ci"], errors="coerce")
                n_raw = len(sub)
                mask_valid = s.notna() & w.notna() & (w > 0)
                n_valid = mask_valid.sum()

                # Rule 6 — all missing
                if n_valid < 5:
                    flags.append({
                        "country": country, "period": period, "indicator": ind,
                        "group": grp_label, "value": np.nan, "n_raw": n_raw,
                        "rule": "Rule 6 — all-missing (n_valid<5)", "severity": "HIGH"
                    })
                    continue

                mu = float(np.dot(w[mask_valid], s[mask_valid]) / w[mask_valid].sum())

                # Rule 1 — boundary
                if n_valid >= MIN_N and (mu == 1.0 or mu == 0.0):
                    flags.append({
                        "country": country, "period": period, "indicator": ind,
                        "group": grp_label, "value": round(mu, 4), "n_raw": n_raw,
                        "rule": "Rule 1 — boundary (0 or 1)", "severity": "HIGH"
                    })

                # Rule 2 — implausible range
                if lo is not None and n_valid >= MIN_N and not (lo <= mu <= hi):
                    flags.append({
                        "country": country, "period": period, "indicator": ind,
                        "group": grp_label, "value": round(mu, 4), "n_raw": n_raw,
                        "rule": f"Rule 2 — out of range [{lo},{hi}]", "severity": "HIGH"
                    })

                # Rule 3 — wave-to-wave jump
                key = (country, ind, grp_label)
                if key in prev_by_group:
                    delta = abs(mu - prev_by_group[key])
                    if delta > 0.20:
                        flags.append({
                            "country": country, "period": period, "indicator": ind,
                            "group": grp_label, "value": round(mu, 4), "n_raw": n_raw,
                            "rule": f"Rule 3 — wave jump {round(delta,3)}", "severity": "MEDIUM"
                        })
                prev_by_group[key] = mu

                # Rule 5 — implausible migrant-native gap
                if grp_label == "Migrant":
                    nat_key = (country, period, ind, "Native")
                    # find native
                    sub_nat = dfp[dfp["migrante_ci"] == 0]
                    s_nat   = pd.to_numeric(sub_nat[col], errors="coerce")
                    w_nat   = pd.to_numeric(sub_nat["factor_ci"], errors="coerce")
                    mask_nat = s_nat.notna() & w_nat.notna() & (w_nat > 0)
                    if mask_nat.sum() >= 5:
                        mu_nat = float(np.dot(w_nat[mask_nat], s_nat[mask_nat]) / w_nat[mask_nat].sum())
                        gap = abs(mu - mu_nat)
                        if gap > 0.35 and n_valid >= MIN_N:
                            flags.append({
                                "country": country, "period": period, "indicator": ind,
                                "group": f"Migrant (gap={round(gap,3)})", "value": round(mu, 4), "n_raw": n_raw,
                                "rule": f"Rule 5 — migrant-native gap {round(gap,3)} > 0.35", "severity": "MEDIUM"
                            })

# ===========================================================================
# 7. Rule 7 — sample size anomaly (DOM only, 7 waves)
# ===========================================================================
for ind, col in INDICATORS_MAP.items():
    for country in ["DOM"]:
        dfc = df_car[df_car["pais_c"] == country]
        ns = {}
        for period in sorted(dfc["periodo_c"].unique()):
            dfp = dfc[dfc["periodo_c"] == period]
            ns[period] = len(dfp)
        if len(ns) < 2:
            continue
        med_n = float(np.median(list(ns.values())))
        for period, n in ns.items():
            if n < 0.5 * med_n or n > 2.0 * med_n:
                flags.append({
                    "country": country, "period": period, "indicator": ind,
                    "group": "all", "value": n, "n_raw": n,
                    "rule": f"Rule 7 — sample size anomaly (n={n}, median={med_n:.0f})", "severity": "MEDIUM"
                })

# ===========================================================================
# 8. Print Detection Table
# ===========================================================================
print(f"\nTotal flags: {len(flags)}")
if flags:
    print("\nDetection Table:")
    print(f"{'#':<4} {'Country':<6} {'Period':<10} {'Indicator':<14} {'Group':<25} "
          f"{'Value':<10} {'N_raw':<8} {'Severity':<8} Rule")
    print("-" * 120)
    for i, f in enumerate(flags, 1):
        print(f"{i:<4} {f['country']:<6} {f['period']:<10} {f['indicator']:<14} "
              f"{f['group']:<25} {str(f['value']):<10} {f['n_raw']:<8} "
              f"{f['severity']:<8} {f['rule']}")
else:
    print("No anomalies found.")

# ===========================================================================
# 9. BID.dta direct cross-check for key variables
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 6 — BID.dta DIRECT CROSS-CHECK")
print("=" * 70)

BID_FILES = {
    "BLZ": BID_DIR / "BLZ" / "BLZ_2024m9_BID.dta",
    "BRB": BID_DIR / "BRB" / "BRB_2023a_BID.dta",
    "DOM": BID_DIR / "DOM" / "DOM_2024t4_BID.dta",
}

for country, bid_path in BID_FILES.items():
    if not bid_path.exists():
        print(f"  {country}: BID file NOT FOUND at {bid_path}")
        continue
    try:
        bid_cols = ["migrante_ci", "emp_ci", "desemp_ci", "pea_ci",
                    "formal_ci", "edu_hdmf", "factor_ci", "edad_ci"]
        # Try to add inactivo_ci
        bid = pd.read_stata(bid_path, columns=[c for c in bid_cols if True],
                            convert_categoricals=False)
        print(f"\n  {country} — {bid_path.name}: {len(bid):,} rows")

        # Check if inactivo_ci is in the file
        try:
            bid2 = pd.read_stata(bid_path, columns=["inactivo_ci"], convert_categoricals=False)
            bid["inactivo_ci"] = bid2["inactivo_ci"]
            print(f"    inactivo_ci: FOUND — {bid['inactivo_ci'].value_counts(dropna=False).to_dict()}")
        except Exception:
            print(f"    inactivo_ci: NOT IN BID FILE")

        for col in ["migrante_ci", "emp_ci", "desemp_ci", "pea_ci", "formal_ci"]:
            if col in bid.columns:
                vc = bid[col].value_counts(dropna=False).to_dict()
                print(f"    {col}: {vc}")

        # Compute key rates from BID
        wa = bid["edad_ci"].between(16, 64)
        print(f"\n    Key rates (from BID, working-age 16-64):")
        for grp_label, grp_code in [("Native", 0), ("Migrant", 1)]:
            grp = bid[(bid["migrante_ci"] == grp_code) & wa]
            pea_sub = grp[grp["pea_ci"] == 1]
            emp_sub = grp[grp["emp_ci"] == 1]
            if len(pea_sub) > 0:
                u_rate = wavg(pea_sub["desemp_ci"], pea_sub["factor_ci"])
                print(f"      {grp_label}: unemp={round(u_rate*100,2) if pd.notna(u_rate) else 'NaN'}%  (n_pea={len(pea_sub)})")
            if len(emp_sub) > 0:
                f_rate = wavg(emp_sub["formal_ci"], emp_sub["factor_ci"])
                print(f"      {grp_label}: formality={round(f_rate*100,2) if pd.notna(f_rate) else 'NaN'}%  (n_emp={len(emp_sub)})")
    except Exception as e:
        print(f"  {country}: ERROR reading BID — {e}")

print("\n" + "=" * 70)
print("SCAN COMPLETE")
print("=" * 70)
