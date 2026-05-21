"""
Generates a synthetic HDMF-schema dataset for testing and demonstration.
Output: data/synthetic/SYNTH_BID.dta (100 observations, fake values)

All values are randomly generated — this dataset does NOT represent any real
survey or population. It exists solely to allow hdmf_2.py to run without
access to licensed microdata.
"""

import numpy as np
import pandas as pd
import pyreadstat

rng = np.random.default_rng(42)
N = 100

# ── Identifiers ────────────────────────────────────────────────────────────────
pais_c = np.full(N, 170)          # Colombia placeholder
idh_ch = np.arange(1, N + 1)
idp_ci = np.arange(1, N + 1)
factor_ci = rng.uniform(500, 5000, N)
factor_ch = factor_ci.copy()

# ── Demographics ───────────────────────────────────────────────────────────────
edad_ci = rng.integers(15, 70, N).astype(float)
sexo_ci = rng.choice([1, 2], N).astype(float)          # 1=male 2=female
relacion_ci = rng.choice([1, 2, 3, 4], N, p=[0.3, 0.25, 0.25, 0.2]).astype(float)
miembros_ci = rng.integers(1, 7, N).astype(float)

# ── Migration ──────────────────────────────────────────────────────────────────
migrante_ci = rng.choice([0, 1], N, p=[0.8, 0.2]).astype(float)
# mig_pais_ci: country code (NaN for natives)
mig_pais_ci = np.where(migrante_ci == 1, rng.choice([862, 218, 604, 484], N), np.nan)
migrantiguo5_ci = np.where(migrante_ci == 1, rng.choice([0, 1], N, p=[0.4, 0.6]), np.nan)

# ── Employment status ──────────────────────────────────────────────────────────
pea_ci = rng.choice([0, 1], N, p=[0.25, 0.75]).astype(float)
emp_ci = np.where(pea_ci == 1, rng.choice([0, 1], N, p=[0.1, 0.9]), np.nan)
desemp_ci = np.where(pea_ci == 1, 1 - emp_ci, np.nan)
condocup_ci = np.where(
    pea_ci == 0, 3,
    np.where(emp_ci == 1, 1, 2)
).astype(float)

# ── Job characteristics (conditional on employed) ──────────────────────────────
employed_mask = emp_ci == 1
formal_ci = np.full(N, np.nan)
formal_ci[employed_mask] = rng.choice([0, 1], employed_mask.sum(), p=[0.45, 0.55])

tipocontrato_ci = np.full(N, np.nan)
tipocontrato_ci[employed_mask] = rng.choice([1, 2, 3], employed_mask.sum())

horaspri_ci = np.full(N, np.nan)
horaspri_ci[employed_mask] = rng.uniform(20, 60, employed_mask.sum())

horastot_ci = np.full(N, np.nan)
horastot_ci[employed_mask] = horaspri_ci[employed_mask] + rng.uniform(0, 10, employed_mask.sum())

cotizando_ci = np.full(N, np.nan)
cotizando_ci[employed_mask] = rng.choice([0, 1], employed_mask.sum(), p=[0.4, 0.6])

afiliado_ci = np.full(N, np.nan)
afiliado_ci[employed_mask] = rng.choice([0, 1], employed_mask.sum(), p=[0.3, 0.7])

# ── Education ──────────────────────────────────────────────────────────────────
aedu_ci = rng.uniform(0, 18, N)
edu_isced = rng.choice([0, 1, 2, 3, 4, 5, 6, 7, 8], N).astype(float)
edu_hdmf = rng.choice(range(1, 11), N).astype(float)

# ── Income (conditional on employed, local currency units — nominal, fake) ─────
ylm_ci = np.full(N, np.nan)
ylm_ci[employed_mask] = rng.lognormal(13.5, 0.8, employed_mask.sum())

ylnm_ci = np.full(N, np.nan)
ylnm_ci[employed_mask] = rng.lognormal(11, 1.0, employed_mask.sum()) * rng.choice([0, 1], employed_mask.sum(), p=[0.6, 0.4])

ynlm_ci = rng.lognormal(10, 1.2, N) * rng.choice([0, 1], N, p=[0.7, 0.3])
ytot_ci = np.nansum([
    np.where(np.isnan(ylm_ci), 0, ylm_ci),
    np.where(np.isnan(ylnm_ci), 0, ylnm_ci),
    ynlm_ci
], axis=0)

remesas_ci = rng.lognormal(12, 1.0, N) * rng.choice([0, 1], N, p=[0.85, 0.15])
remesas_ch = remesas_ci.copy()

# ── Assemble DataFrame ─────────────────────────────────────────────────────────
df = pd.DataFrame({
    "pais_c": pais_c, "idh_ch": idh_ch, "idp_ci": idp_ci,
    "factor_ci": factor_ci, "factor_ch": factor_ch,
    "edad_ci": edad_ci, "sexo_ci": sexo_ci, "relacion_ci": relacion_ci, "miembros_ci": miembros_ci,
    "migrante_ci": migrante_ci, "mig_pais_ci": mig_pais_ci, "migrantiguo5_ci": migrantiguo5_ci,
    "condocup_ci": condocup_ci, "emp_ci": emp_ci, "desemp_ci": desemp_ci, "pea_ci": pea_ci,
    "formal_ci": formal_ci, "tipocontrato_ci": tipocontrato_ci,
    "horaspri_ci": horaspri_ci, "horastot_ci": horastot_ci,
    "cotizando_ci": cotizando_ci, "afiliado_ci": afiliado_ci,
    "aedu_ci": aedu_ci, "edu_isced": edu_isced, "edu_hdmf": edu_hdmf,
    "ylm_ci": ylm_ci, "ylnm_ci": ylnm_ci, "ynlm_ci": ynlm_ci,
    "ytot_ci": ytot_ci, "remesas_ci": remesas_ci, "remesas_ch": remesas_ch,
})

# ── Write .dta ─────────────────────────────────────────────────────────────────
out_path = "data/synthetic/SYNTH_BID.dta"
pyreadstat.write_dta(df, out_path, version=15)
print(f"Written: {out_path}  ({len(df)} obs, {len(df.columns)} variables)")
print("Migrant share:", df["migrante_ci"].mean().round(2))
print("Employment rate (among PEA):", df.loc[df["pea_ci"]==1, "emp_ci"].mean().round(2))
