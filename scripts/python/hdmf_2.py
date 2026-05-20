#%load_ext autoreload
#%autoreload 2

# =============================================================================
# HDMF — How Do Migrants Fare in LAC
# Weighted indicators by topic: Population | Labor | Formality | Education
# =============================================================================


#%% 0 — IMPORTS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# Loads prepared data from _hdmf_cache.pkl (built by hdmf_build.py).
# To rebuild the cache run:
#   py hdmf_build.py                         (all countries)
#   py hdmf_build.py --countries COL CHL     (subset)
# ─────────────────────────────────────────────────────────────────────────────
import os
import pickle
import time as _time
from datetime import date
_t_start = _time.time()

import numpy as np
import pandas as pd
from scipy.stats import norm as _norm

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.cm as _cm

from functions import (
    make_weighted_stats_multi,
    make_weighted_pivot_multi,
    fix_orthography,
)

pd.options.display.float_format = '{:,.3f}'.format
np.set_printoptions(suppress=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR   = os.path.join(BASE_DIR, 'bases armo', 'armo')
CACHE_FILE = os.path.join(ARMO_DIR, '_hdmf_cache.pkl')
DATE_TAG   = date.today().strftime('%Y-%m-%d')
OUT_DIR    = os.path.join(BASE_DIR, 'out', 'indicator_descriptive', DATE_TAG)
os.makedirs(OUT_DIR, exist_ok=True)

# ── Columns to load from each *_BID.dta ──────────────────────────────────────
COLS_TO_KEEP = list(dict.fromkeys([
    'pais_c', 'mig_pais_ci', 'migrante_ci', 'sexo_ci', 'factor_ci', 'edad_ci', 'idh_ch',
    'emp_ci', 'desemp_ci', 'pea_ci', 'condocup_ci',
    'ytot_ci', 'ylm_ci', 'horastot_ci', 'horaspri_ci',
    'formal_ci', 'tipocontrato_ci', 'parcial_ci', 'aedu_ci', 'edu_hdmf',
]))

# ── Standard labels ───────────────────────────────────────────────────────────
FB_LABELS = {
    'Native':        'Nativos',
    'Venezuela':     'Migrantes de Venezuela',
    'Foreign_other': 'Migrantes de otros países',
}
FB_ORDER = ['Nativos', 'Migrantes de Venezuela', 'Migrantes de otros países']

LABOR_LABELS = {
    'emp_ci':      'Población ocupada',
    'desemp_ci':   'Población desocupada',
    'inactivo_ci': 'Población inactiva',
    'pea_ci':      'Población económicamente activa',
}

EDU_BASICA_CATS = [
    'Menos de primaria', 'Primaria incompleta', 'Primaria completa',
    'Media incompleta',  'Media completa',
]

# ── Utility functions ─────────────────────────────────────────────────────────
def _norm_code(x):
    try:
        xf = float(x)
        return int(xf) if xf.is_integer() else xf
    except Exception:
        return x


def compute_stats(df, group_cols, status_cols, weight_col='factor_ci'):
    return make_weighted_stats_multi(
        df=df, group_cols=group_cols, status_cols=status_cols, weight_col=weight_col,
        include_se=True, include_ci=True, include_neff=True,
        include_n_unweighted=True, include_sum_weights=True, output_format="long",
    )


def apply_fb_labels(df, col='foreign_born'):
    df = df.copy()
    df[col] = df[col].replace(FB_LABELS)
    df[col] = pd.Categorical(df[col], categories=FB_ORDER, ordered=True)
    return df


def make_pivot(df, var_col='variable'):
    val_cols = ['mean', 'std', 'n_unweighted', 'sum_weights',
                'ones_unweighted', 'ones_weights', 'err_lo', 'err_hi']
    return df.pivot_table(index=['pais_c', var_col], values=val_cols, columns=['foreign_born'])


def wavg(g, value_col, weight_col='factor_ci'):
    v = pd.to_numeric(g[value_col], errors='coerce').to_numpy()
    w = pd.to_numeric(g[weight_col], errors='coerce').to_numpy()
    m = np.isfinite(v) & np.isfinite(w) & (w > 0)
    return np.average(v[m], weights=w[m]) if m.sum() else np.nan


#%% 1 — LOAD FROM CACHE
# ─────────────────────────────────────────────────────────────────────────────
if not os.path.exists(CACHE_FILE):
    raise FileNotFoundError(
        f'Cache not found: {CACHE_FILE}\n'
        'Run hdmf_build.py first to build the dataset.'
    )

print(f'Loading cache: {CACHE_FILE}')
with open(CACHE_FILE, 'rb') as fh:
    _cache = pickle.load(fh)
data                = _cache['data']
value_labels_by_var = _cache['value_labels_by_var']
print(f'Loaded {len(data):,} rows, {data["pais_c"].nunique()} countries')

# ── Analytical subsets ────────────────────────────────────────────────────────
wap     = data[data['edad_ci'].between(16, 64)].copy()
emp_lac = data[(data['condocup_ci'] == 1) & ~data['pais_c'].isin(['USA'])].copy()

print('Countries :', data.pais_c.value_counts().to_dict())
print('Migration :', data.migrante_ci.value_counts().to_dict())


#%% 3 — POPULATION
# ─────────────────────────────────────────────────────────────────────────────

# ── 3a. Top-20 countries of migrant origin per host country ───────────────────
host_countries = data['pais_c'].dropna().unique()
origin_tables  = []

for c in host_countries:
    df_c      = data[data['pais_c'] == c]
    total_mig = df_c.loc[df_c['migrante_ci'] == 'Migrant', 'factor_ci'].sum()
    tmp = (
        df_c[df_c['migrante_ci'] == 'Migrant']
        .groupby('mig_pais_ci')['factor_ci'].sum()
        .sort_values(ascending=False).head(20)
        .to_frame(name=c)
    )
    tmp[f'pct_{c}'] = tmp[c] / total_mig if total_mig else 0
    origin_tables.append(tmp)

top_mig_countries = pd.concat(origin_tables, axis=1).fillna(0).reset_index()
cols_ordered = ['mig_pais_ci']
for c in host_countries:
    if c in top_mig_countries.columns:
        cols_ordered += [c, f'pct_{c}']
top_mig_countries = top_mig_countries[cols_ordered]

# ── 3b. Population aggregates (total and working-age 16–64) ──────────────────
population = (
    data.groupby(['pais_c', 'foreign_born'])['factor_ci']
    .sum().reset_index(name='Population')
    .pivot_table(index=[], columns=['pais_c', 'foreign_born'], values='Population')
)
population_16_64 = (
    wap.groupby(['pais_c', 'foreign_born'])['factor_ci']
    .sum().reset_index(name='Population_16_64')
    .pivot_table(index=[], columns=['pais_c', 'foreign_born'], values='Population_16_64')
)
population = pd.concat([population, population_16_64], axis=0)

pop = population.copy()
_zero = pd.Series([0.0] * len(pop), index=pop.index)
for country in pop.columns.get_level_values(0).unique():
    ven = pop.get((country, 'Venezuela'), _zero)
    fot = pop.get((country, 'Foreign_other'), _zero)
    nat = pop.get((country, 'Native'), _zero)
    pop[(country, 'Venezuela+Foreign_other')] = ven + fot
    pop[(country, 'Total')] = nat + fot + ven

ORDER2     = ['Native', 'Venezuela', 'Venezuela+Foreign_other', 'Foreign_other', 'Total']
full_order = [(c, k) for c in pop.columns.get_level_values(0).unique() for k in ORDER2
              if (c, k) in pop.columns]
pop = pop.reindex(columns=pd.MultiIndex.from_tuples(full_order, names=pop.columns.names))

# ── 3c. Population age distribution ──────────────────────────────────────────
pop_by_age = (
    data.groupby(['pais_c', 'foreign_born', 'age_group'])['factor_ci']
    .sum().reset_index(name='Population')
)
pop_by_age['share'] = (
    pop_by_age['Population']
    / pop_by_age.groupby(['pais_c', 'foreign_born'])['Population'].transform('sum')
)


#%% 4 — LABOR MARKET
# ─────────────────────────────────────────────────────────────────────────────

labor_status = compute_stats(
    wap, group_cols=['pais_c', 'foreign_born'],
    status_cols=['emp_ci', 'desemp_ci', 'inactivo_ci', 'pea_ci'],
)
labor_status = apply_fb_labels(labor_status)
labor_status['variable'] = labor_status['variable'].replace(LABOR_LABELS)
labor_status_pivot = make_pivot(labor_status)

labor_wages = (
    wap.groupby(['pais_c', 'foreign_born'])
    .apply(lambda g: pd.Series({
        'ingreso_total_wavg':  wavg(g, 'ytot_ci'),
        'ingreso_laboral_wavg': wavg(g, 'ylm_ci'),   # ylm_ci: NaN for ESP/USA; COL uses all waves with data
        'horas_totales_wavg':  wavg(g, 'horastot_ci'),
    }))
    .reset_index()
)
labor_wages = apply_fb_labels(labor_wages)


#%% 4b — PART-TIME (parcial_ci)
# ─────────────────────────────────────────────────────────────────────────────
# parcial_ci = 1 if employed with horaspri_ci < 35 h/week
# Available: COL, CHL, ECU, PER, ESP (all waves after parcial_ci was added)
# COL 2025t3 income note: GEIH 2025t3 has no income module; ylm_ci is NaN for
#   that wave.  Income stats for COL reflect 2018–2024 data only.
# ─────────────────────────────────────────────────────────────────────────────
parcial_df = emp_lac[emp_lac['parcial_ci'].notna()].copy()
parcial_status = compute_stats(
    parcial_df, group_cols=['pais_c', 'foreign_born'], status_cols=['parcial_ci'],
)
parcial_status = apply_fb_labels(parcial_status)
parcial_pivot  = make_pivot(parcial_status)


#%% 4c — TERTIARY EDUCATION (edusup_ci)
# ─────────────────────────────────────────────────────────────────────────────
# Share with post-secondary education (complete or incomplete), among working-age 15–64.
# edu_hdmf >= 7.  Denominator = working-age population 15–64 with non-null edu_hdmf.
# ─────────────────────────────────────────────────────────────────────────────
wap15_64 = data[data['edad_ci'].between(15, 64)].copy()
_edu_num  = pd.to_numeric(wap15_64['edu_hdmf'], errors='coerce')
wap15_64['edusup_ci'] = np.where(_edu_num.notna(), (_edu_num >= 7).astype(float), np.nan)
edusup_df = wap15_64[wap15_64['edusup_ci'].notna()].copy()

edusup_status = compute_stats(
    edusup_df, group_cols=['pais_c', 'foreign_born'], status_cols=['edusup_ci'],
)
edusup_status = apply_fb_labels(edusup_status)
edusup_pivot  = make_pivot(edusup_status)


#%% 4d — LONG HOURS (lhours_ci)
# ─────────────────────────────────────────────────────────────────────────────
# Share working 50+ hours/week (horastot_ci > 50), among employed population.
# Denominator = employed with non-null horastot_ci.
# ─────────────────────────────────────────────────────────────────────────────
lhours_df = emp_lac.copy()
_hrs_num   = pd.to_numeric(lhours_df['horastot_ci'], errors='coerce')
lhours_df['lhours_ci'] = np.where(_hrs_num.notna(), (_hrs_num > 50).astype(float), np.nan)
lhours_df = lhours_df[lhours_df['lhours_ci'].notna()].copy()

lhours_status = compute_stats(
    lhours_df, group_cols=['pais_c', 'foreign_born'], status_cols=['lhours_ci'],
)
lhours_status = apply_fb_labels(lhours_status)
lhours_pivot  = make_pivot(lhours_status)


#%% 5 — FORMALITY
# ─────────────────────────────────────────────────────────────────────────────

formality_status = compute_stats(
    emp_lac, group_cols=['pais_c', 'foreign_born'], status_cols=['formal_ci'],
)
formality_status = apply_fb_labels(formality_status)
formality_status['variable'] = formality_status['variable'].replace({np.nan: 'Missing'})
formality_pivot = make_pivot(formality_status)

contract_type = make_weighted_pivot_multi(
    df=emp_lac,
    group_cols=['pais_c', 'foreign_born'],
    status_cols=['formal_ci', 'tipocontrato_ci'],
    transpose=False, flatten_cols=True,
).T


#%% 6 — EDUCATION
# ─────────────────────────────────────────────────────────────────────────────

edu_label_map = {
    _norm_code(k): v
    for k, v in value_labels_by_var.get("edu_hdmf", {}).items()
}
edu_codes   = pd.to_numeric(data['edu_hdmf'], errors='coerce')
edu_dummies = pd.get_dummies(edu_codes, dtype=int, dummy_na=True)
edu_dummies = edu_dummies.rename(columns={
    code: f"edu_hdmf_{edu_label_map.get(_norm_code(code), f'code {_norm_code(code)}')}"
    for code in edu_dummies.columns
})
edu_dummies.columns = (
    edu_dummies.columns.str.replace(r"^edu_hdmf_", "", regex=True).map(fix_orthography)
)

data_edu = pd.concat([data[['pais_c', 'foreign_born', 'factor_ci']], edu_dummies], axis=1)

edu_distribution = compute_stats(
    data_edu, group_cols=['pais_c', 'foreign_born'],
    status_cols=edu_dummies.columns.tolist(),
)
edu_distribution = apply_fb_labels(edu_distribution)
edu_distribution['variable'] = edu_distribution['variable'].replace({np.nan: 'Missing'})
edu_cats = edu_distribution['variable'].dropna().unique().tolist()
edu_distribution['variable'] = pd.Categorical(edu_distribution['variable'],
                                               categories=edu_cats, ordered=True)
edu_distribution_pivot = make_pivot(edu_distribution)

edu_years = (
    data.groupby(['pais_c', 'foreign_born'])
    .apply(lambda g: pd.Series({'aedu_wavg': wavg(g, 'aedu_ci')}))
    .reset_index()
)
edu_years = apply_fb_labels(edu_years)


#%% 6b — EDUCATION LEVEL % CHART
# ─────────────────────────────────────────────────────────────────────────────
_EDU_3CAT_MAP = {
    1: "Primary or less", 2: "Primary or less", 3: "Primary or less",
    4: "Secondary",       5: "Secondary",       6: "Secondary",
    7: "Higher education", 8: "Higher education",
}
_EDU_3CAT_ORDER  = ["Primary or less", "Secondary", "Higher education"]
_EDU_3CAT_COLORS = {
    "Primary or less":  "#C9742A",
    "Secondary":        "#2171A0",
    "Higher education": "#1D3557",
}

_GROUP_EN = {
    'Native':        'Natives',
    'Venezuela':     'Venezuelan',
    'Foreign_other': 'Other migr.',
}
_GROUP_ORDER_CHART = ['Native', 'Venezuela', 'Foreign_other']

_e3 = data[['pais_c', 'foreign_born', 'factor_ci', 'edu_hdmf']].copy()
_e3['edu_3cat'] = pd.to_numeric(_e3['edu_hdmf'], errors='coerce').map(_EDU_3CAT_MAP)
_e3 = _e3[_e3['edu_3cat'].notna() & _e3['factor_ci'].notna()].copy()

_e3_agg = (
    _e3.groupby(['pais_c', 'foreign_born', 'edu_3cat'])['factor_ci']
    .sum().reset_index(name='wsum')
)
_e3_totals = _e3_agg.groupby(['pais_c', 'foreign_born'])['wsum'].transform('sum')
_e3_agg['pct'] = _e3_agg['wsum'] / _e3_totals * 100

_e3_wide = _e3_agg.pivot_table(
    index=['pais_c', 'foreign_born'], columns='edu_3cat', values='pct', aggfunc='first'
).reindex(columns=_EDU_3CAT_ORDER).fillna(0)

_countries_edu   = sorted(_e3_wide.index.get_level_values(0).unique())
_n_countries_edu = len(_countries_edu)
_ncols_chart     = 3
_nrows_chart     = (_n_countries_edu + _ncols_chart - 1) // _ncols_chart

fig, axes = plt.subplots(
    _nrows_chart, _ncols_chart,
    figsize=(5 * _ncols_chart, 4 * _nrows_chart),
    sharey=True, squeeze=False,
)
axes_flat = axes.flatten()

for ax_i, country in enumerate(_countries_edu):
    ax = axes_flat[ax_i]
    try:
        _df_c = _e3_wide.loc[country].copy()
    except KeyError:
        ax.set_visible(False)
        continue

    _avail = [g for g in _GROUP_ORDER_CHART if g in _df_c.index]
    if not _avail:
        ax.set_visible(False)
        continue
    _df_c  = _df_c.reindex(_avail)
    x      = np.arange(len(_avail))
    bottom = np.zeros(len(_avail))

    for cat in _EDU_3CAT_ORDER:
        vals = _df_c[cat].fillna(0).values
        ax.bar(x, vals, bottom=bottom, color=_EDU_3CAT_COLORS[cat], width=0.65,
               edgecolor='white', linewidth=0.5)
        bottom += vals

    ax.set_title(country, fontsize=11, fontweight='bold', pad=6)
    ax.set_xticks(x)
    ax.set_xticklabels([_GROUP_EN.get(g, g) for g in _avail], fontsize=8)
    ax.set_ylim(0, 104)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=0))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', labelsize=8)

for ax_i in range(_n_countries_edu, len(axes_flat)):
    axes_flat[ax_i].set_visible(False)

_legend_handles = [plt.Rectangle((0, 0), 1, 1, fc=_EDU_3CAT_COLORS[c], ec='grey', lw=0.3)
                   for c in _EDU_3CAT_ORDER]
fig.legend(
    _legend_handles, _EDU_3CAT_ORDER,
    loc='lower center', ncol=3,
    bbox_to_anchor=(0.5, 0.0), fontsize=9,
    title='Education level', title_fontsize=9, frameon=False,
)
fig.suptitle('Education level distribution (%) by migration status',
             fontsize=13, fontweight='bold')
fig.tight_layout(rect=[0, 0.08, 1, 0.97])

_edu_chart_path = os.path.join(OUT_DIR, 'education_level_pct.png')
fig.savefig(_edu_chart_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f'Education level chart -> {_edu_chart_path}')


#%% 8 — EXPORT (cross-section indicators)
# ─────────────────────────────────────────────────────────────────────────────
out_xlsx = os.path.join(OUT_DIR, 'hdmf_indicators.xlsx')

with pd.ExcelWriter(out_xlsx) as writer:
    top_mig_countries.to_excel(writer,      sheet_name='population_origin',  index=True)
    labor_status_pivot.to_excel(writer,     sheet_name='labor_status',       index=True)
    labor_wages.to_excel(writer,            sheet_name='labor_wages_hours',  index=True)
    parcial_pivot.to_excel(writer,          sheet_name='parttime',           index=True)
    edusup_pivot.to_excel(writer,           sheet_name='tertiary_educ',      index=True)
    lhours_pivot.to_excel(writer,           sheet_name='long_hours',         index=True)
    formality_pivot.to_excel(writer,        sheet_name='formality',          index=True)
    contract_type.to_excel(writer,          sheet_name='contract_type',      index=True)
    edu_distribution_pivot.to_excel(writer, sheet_name='education_level',    index=True)
    edu_years.to_excel(writer,              sheet_name='education_years',     index=True)

print(f"Indicators exported -> {out_xlsx}")


#%% 9 — LATEX EXPORT (one table per country)
# ─────────────────────────────────────────────────────────────────────────────
latex_dir = os.path.join(OUT_DIR, 'latex_tables')
os.makedirs(latex_dir, exist_ok=True)

stats_t = labor_status_pivot.T

for country in stats_t.columns.get_level_values(0).unique():
    df_c          = stats_t.loc[:, stats_t.columns.get_level_values(0) == country].copy()
    df_c.columns  = df_c.columns.droplevel(0)
    colfmt        = "l" + "S" * df_c.shape[1]

    latex_table = df_c.to_latex(
        index=True, escape=False, float_format="%.3f", column_format=colfmt,
        multicolumn=False,
        caption=f"Indicadores del mercado laboral – {country}",
        label=f"tab:labor_{country.lower()}",
    )

    lines = latex_table.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == r"\toprule":
            parts = [p.strip() for p in lines[i + 1].split("&")]
            new_parts = [parts[0]] + [
                rf"\multicolumn{{1}}{{c}}{{{p.replace(r'\\', '').strip()}}}"
                for p in parts[1:]
            ]
            lines[i + 1] = " & ".join(new_parts)
            break

    with open(os.path.join(latex_dir, f"labor_market_{country}.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

print(f"LaTeX tables -> {latex_dir}/")


#%% 10 — GENERAL INDICATORS (long-format panel: COL, CHL, ECU, PER)
# ─────────────────────────────────────────────────────────────────────────────
# Groups by foreign_born (Native / Venezuela / Foreign_other) so that the
# indicator summary can distinguish Venezuelan vs other migrants.
# ytot_ci excluded (missing from most waves).
# ─────────────────────────────────────────────────────────────────────────────

LAC4 = ['COL', 'CHL', 'ECU', 'PER', 'ESP']

lac4 = data[data['pais_c'].isin(LAC4)].copy()
lac4['year'] = lac4['periodo_c'].str.extract(r'(\d{4})').astype(int)

# Working-age population share (15–64) — matches chart definition "Working age (15–64)"
lac4['wap_ci'] = lac4['edad_ci'].between(15, 64).astype(int)

# Age-group dummies — mean of each = share of total population in that bracket
_AGE_GROUPS = {
    'age_0_15':   (0,   15),
    'age_16_24':  (16,  24),
    'age_25_34':  (25,  34),
    'age_35_44':  (35,  44),
    'age_45_54':  (45,  54),
    'age_55_64':  (55,  64),
    'age_65plus': (65, 150),
}
for _col, (_lo, _hi) in _AGE_GROUPS.items():
    lac4[_col] = lac4['edad_ci'].between(_lo, _hi).astype(int)

lac4['child_0_17'] = lac4['edad_ci'].between(0, 17).astype(int)
lac4['child_0_12'] = lac4['edad_ci'].between(0, 12).astype(int)

# nonven_head_child: non-Venezuelan child (0–17) living with a Venezuelan-born household head
# Step 1: identify Venezuelan-born household heads
# Use jefe_ci per row where not NaN, fall back to relacion_ci — handles COL (no jefe_ci)
_jefe     = pd.to_numeric(lac4['jefe_ci'],     errors='coerce') if 'jefe_ci'     in lac4.columns else pd.Series(np.nan, index=lac4.index)
_relacion = pd.to_numeric(lac4['relacion_ci'], errors='coerce') if 'relacion_ci' in lac4.columns else pd.Series(np.nan, index=lac4.index)
_is_head  = pd.Series(np.where(_jefe.notna(), _jefe == 1, _relacion == 1), index=lac4.index)
_is_ven   = lac4['foreign_born'] == 'Venezuela'
lac4['_head_ven'] = (_is_head & _is_ven).astype(int)
# Step 2: propagate to all household members
lac4['hhd_ven_head'] = lac4.groupby(['pais_c', 'periodo_c', 'idh_ch'])['_head_ven'].transform('max')
lac4.drop(columns=['_head_ven'], inplace=True)
# Step 3: flag non-Venezuelan children in those households (NaN for Venezuelan-born)
lac4['nonven_head_child'] = np.where(
    lac4['foreign_born'] == 'Venezuela',
    np.nan,
    np.where((lac4['edad_ci'] < 18) & (lac4['hhd_ven_head'] == 1), 1.0, 0.0),
)

# ── Denominator fix ──────────────────────────────────────────────────────────
# CHL and ECU code labor variables as 0 (not NaN) for children/elderly, so the
# weighted mean in _gen_indicators() would use total population as denominator
# instead of working-age population — producing rates 15–29 pp below the correct
# value. Force these variables to NaN outside 16–64 so all countries use the
# same denominator (working-age population), matching the chart methodology.
_wa_mask = lac4['edad_ci'].between(16, 64)
for _col in ['pea_ci', 'emp_ci', 'inactivo_ci', 'desemp_ci']:
    if _col in lac4.columns:
        lac4[_col] = lac4[_col].where(_wa_mask, other=np.nan)
# Fix 2: unemployment denominator — desemp_ci must be NaN for inactive (pea_ci=0)
# so the weighted mean uses PEA (active population) as denominator, not all working-age.
if 'desemp_ci' in lac4.columns and 'pea_ci' in lac4.columns:
    lac4['desemp_ci'] = lac4['desemp_ci'].where(lac4['pea_ci'] == 1, other=np.nan)

# edusup_ci: share with tertiary education (complete or incomplete), denom = working-age 16-64
# Matches chart definition (wapc = edad_ci.between(16, 64)), consistent with other labor indicators.
_edu_codes = pd.to_numeric(lac4['edu_hdmf'], errors='coerce')
lac4['edusup_ci'] = np.where(
    lac4['edad_ci'].between(16, 64) & _edu_codes.notna(),
    (_edu_codes >= 7).astype(float),
    np.nan,
)

# lhours_ci: share working 50+ hours/week, denom = employed
lac4['lhours_ci'] = np.where(
    lac4['emp_ci'] == 1,
    (pd.to_numeric(lac4['horastot_ci'], errors='coerce') > 50).astype(float),
    np.nan,
)
lac4.loc[lac4['emp_ci'] == 1, 'lhours_ci'] = np.where(
    pd.to_numeric(lac4.loc[lac4['emp_ci'] == 1, 'horastot_ci'], errors='coerce').notna(),
    (pd.to_numeric(lac4.loc[lac4['emp_ci'] == 1, 'horastot_ci'], errors='coerce') > 50).astype(float),
    np.nan,
)

GEN_BINARY     = [
    'emp_ci', 'desemp_ci', 'pea_ci', 'inactivo_ci', 'formal_ci', 'parcial_ci',
    'edusup_ci', 'lhours_ci',
    'wap_ci',
    'child_0_17', 'child_0_12', 'nonven_head_child',
    'age_0_15', 'age_16_24', 'age_25_34', 'age_35_44',
    'age_45_54', 'age_55_64', 'age_65plus',
]
GEN_CONTINUOUS = ['aedu_ci', 'horastot_ci', 'ylm_ci']
GEN_ALL        = GEN_BINARY + GEN_CONTINUOUS

# Group by foreign_born to distinguish Native / Venezuela / Foreign_other
GEN_GROUP_COLS = ['pais_c', 'year', 'periodo_c', 'foreign_born']
_Z95 = _norm.ppf(0.975)


def _gen_indicators(df, group_cols, indicators, weight_col='factor_ci'):
    """
    Weighted descriptive stats (mean, median, SE, SD, 95% CI) per group × indicator.
    Uses explicit iteration to avoid groupby.apply() pandas version issues.
    """
    rows = []
    for group_keys, g in df.groupby(group_cols, dropna=False):
        if not isinstance(group_keys, tuple):
            group_keys = (group_keys,)
        base = dict(zip(group_cols, group_keys))

        for ind in indicators:
            v = pd.to_numeric(g[ind], errors='coerce').to_numpy(dtype=float)
            w = pd.to_numeric(g[weight_col], errors='coerce').to_numpy(dtype=float)
            mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
            n = int(mask.sum())

            row = {**base, 'indicator': ind}
            if n == 0:
                row.update(mean=np.nan, median=np.nan, se=np.nan, sd=np.nan,
                           ci_lo=np.nan, ci_hi=np.nan,
                           n_unweighted=0, sum_weights=0.0, n_eff=0.0)
                rows.append(row)
                continue

            v_, w_ = v[mask], w[mask]
            wsum   = w_.sum()
            mu     = np.dot(w_, v_) / wsum
            sd_val = float(np.sqrt(np.dot(w_, (v_ - mu) ** 2) / wsum))
            neff   = float((wsum ** 2) / np.dot(w_, w_))
            se_val = float(np.sqrt(np.sum((w_ ** 2) * (v_ - mu) ** 2) / (wsum ** 2)))

            idx  = np.argsort(v_)
            cumw = np.cumsum(w_[idx])
            med  = float(v_[idx][np.searchsorted(cumw, cumw[-1] / 2.0)])

            row.update(
                mean=float(mu), median=med, sd=sd_val, se=se_val,
                ci_lo=float(mu - _Z95 * se_val),
                ci_hi=float(mu + _Z95 * se_val),
                n_unweighted=n, sum_weights=float(wsum), n_eff=neff,
            )
            rows.append(row)

    return pd.DataFrame(rows)


print("Computing general indicators (mean, median, SE, SD, CI) for COL/CHL/ECU/PER...")
general_db = _gen_indicators(lac4, GEN_GROUP_COLS, GEN_ALL)

general_db = general_db.rename(columns={
    'pais_c':       'country',
    'periodo_c':    'period',
    'foreign_born': 'migrant_status',
})

EXPORT_COLS = [
    'country', 'year', 'period', 'migrant_status', 'indicator',
    'mean', 'median', 'se', 'sd', 'ci_lo', 'ci_hi',
    'n_unweighted', 'sum_weights', 'n_eff',
]
EXPORT_COLS = [c for c in EXPORT_COLS if c in general_db.columns]

general_db = (
    general_db[EXPORT_COLS]
    .sort_values(['country', 'year', 'indicator', 'migrant_status'])
    .reset_index(drop=True)
)

gen_csv = os.path.join(OUT_DIR, 'hdmf_general_indicators.csv')
general_db.to_csv(gen_csv, index=False)
print(f"General indicators CSV -> {gen_csv}  ({len(general_db):,} rows)")

gen_dta = os.path.join(OUT_DIR, 'hdmf_general_indicators.dta')
general_db.to_stata(gen_dta, write_index=False, version=118)
print(f"General indicators DTA -> {gen_dta}")


#%% 11 — INDICATOR SUMMARY (pivot: country × year × indicator vs migrant status)
# ─────────────────────────────────────────────────────────────────────────────
# Index:   (country, year, indicator)          — period dropped
# Columns: two-level  (migrant_status, stat)
#          migrant_status: Native | Venezuela | Foreign_other
#          stat:           mean | median | se | sd | ci_lo | ci_hi
# ─────────────────────────────────────────────────────────────────────────────
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

SUMMARY_STATS = ['mean', 'median', 'se', 'sd', 'ci_lo', 'ci_hi']
MS_ORDER      = ['Native', 'Venezuela', 'Foreign_other']

summary_long = (
    general_db[['country', 'year', 'migrant_status', 'indicator'] + SUMMARY_STATS]
    .copy()
)

summary_wide = summary_long.pivot_table(
    index=['country', 'year', 'indicator'],
    columns='migrant_status',
    values=SUMMARY_STATS,
    aggfunc='first',
)

# Swap so outer level = migrant_status, inner = stat
summary_wide = summary_wide.swaplevel(axis=1)

ms_present = [m for m in MS_ORDER if m in summary_wide.columns.get_level_values(0)]
col_tuples  = [(ms, st) for ms in ms_present for st in SUMMARY_STATS
               if (ms, st) in summary_wide.columns]
summary_wide = summary_wide.reindex(columns=pd.MultiIndex.from_tuples(col_tuples))
summary_wide = summary_wide.sort_index()

summary_xlsx = os.path.join(OUT_DIR, 'hdmf_indicator_summary.xlsx')
with pd.ExcelWriter(summary_xlsx, engine='openpyxl') as writer:
    summary_wide.to_excel(writer, sheet_name='indicator_summary')

# ── Formatting ────────────────────────────────────────────────────────────────
# Muted palette: header (level-0) | subheader (level-1) | odd/even data rows
PALETTE = {
    'Native':        {'h1': 'B8CCE4', 'h2': 'D6E4F0', 'odd': 'EEF4FB', 'even': 'F7FAFD'},
    'Venezuela':     {'h1': 'E6AAAA', 'h2': 'F4C8C8', 'odd': 'FCEAEA', 'even': 'FEF4F4'},
    'Foreign_other': {'h1': 'A8C5A0', 'h2': 'C8DEC5', 'odd': 'EAF3E8', 'even': 'F3FAF2'},
    'index':         {'h1': 'BFBFBF', 'h2': 'D9D9D9', 'odd': 'F5F5F5', 'even': 'FFFFFF'},
}

N_IDX    = 3                       # index columns: country, year, indicator
N_STATS  = len(SUMMARY_STATS)      # 6 stat columns per group
N_HEADER = 2                       # two header rows written by pandas

def _fill(hex_col):
    return PatternFill('solid', fgColor=hex_col)

def _side(style='thin', color='BFBFBF'):
    return Side(style=style, color=color)

wb = load_workbook(summary_xlsx)
ws = wb.active
ws.title = 'indicator_summary'

max_col = ws.max_column
max_row = ws.max_row

# ── Column widths ─────────────────────────────────────────────────────────────
ws.column_dimensions[get_column_letter(1)].width = 10   # country
ws.column_dimensions[get_column_letter(2)].width = 6    # year
ws.column_dimensions[get_column_letter(3)].width = 15   # indicator
for c in range(N_IDX + 1, max_col + 1):
    ws.column_dimensions[get_column_letter(c)].width = 10

# ── Map each data column → its migrant-status group ──────────────────────────
col_group = {}
for col_i in range(N_IDX + 1, N_IDX + 1 + len(ms_present) * N_STATS):
    group_i = (col_i - N_IDX - 1) // N_STATS
    col_group[col_i] = ms_present[group_i]

# ── Helper: border with a thick left edge at group starts ─────────────────────
def _border(col_i, top=None, bottom=None):
    is_group_start = (col_i - N_IDX - 1) % N_STATS == 0
    left = _side('medium', '888888') if is_group_start else _side('thin', 'D9D9D9')
    return Border(left=left, top=top, bottom=bottom,
                  right=_side('thin', 'D9D9D9'))

# ── Style row 1 (level-0 headers: migrant-status group names) ─────────────────
ws.row_dimensions[1].height = 22
for col_i in range(1, max_col + 1):
    cell = ws.cell(row=1, column=col_i)
    if col_i <= N_IDX:
        cell.fill      = _fill(PALETTE['index']['h1'])
        cell.font      = Font(bold=True, size=10, color='333333')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = Border(bottom=_side('medium', '888888'),
                                right=_side('thin', 'D9D9D9'))
    elif col_i in col_group:
        grp = col_group[col_i]
        cell.fill      = _fill(PALETTE[grp]['h1'])
        cell.font      = Font(bold=True, size=10, color='1A1A1A')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        is_start = (col_i - N_IDX - 1) % N_STATS == 0
        cell.border    = Border(
            left   = _side('medium', '666666') if is_start else _side('thin', 'D0D0D0'),
            bottom = _side('thin', 'D0D0D0'),
            right  = _side('thin', 'D0D0D0'),
        )

# ── Style row 2 (level-1 headers: stat names) ────────────────────────────────
ws.row_dimensions[2].height = 18
for col_i in range(1, max_col + 1):
    cell = ws.cell(row=2, column=col_i)
    if col_i <= N_IDX:
        cell.fill      = _fill(PALETTE['index']['h2'])
        cell.font      = Font(bold=True, size=9, color='333333')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = Border(bottom=_side('medium', '888888'),
                                right=_side('thin', 'D9D9D9'))
    elif col_i in col_group:
        grp = col_group[col_i]
        cell.fill      = _fill(PALETTE[grp]['h2'])
        cell.font      = Font(bold=True, size=9, color='1A1A1A')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        is_start = (col_i - N_IDX - 1) % N_STATS == 0
        cell.border    = Border(
            left   = _side('medium', '666666') if is_start else _side('thin', 'D0D0D0'),
            bottom = _side('medium', '888888'),
            right  = _side('thin', 'D0D0D0'),
        )

# ── Style data rows ───────────────────────────────────────────────────────────
for row_i in range(N_HEADER + 1, max_row + 1):
    is_odd = (row_i - N_HEADER) % 2 == 1
    tone   = 'odd' if is_odd else 'even'
    ws.row_dimensions[row_i].height = 14

    # Index columns
    for col_i in range(1, N_IDX + 1):
        cell = ws.cell(row=row_i, column=col_i)
        cell.fill      = _fill(PALETTE['index'][tone])
        cell.font      = Font(size=9)
        cell.alignment = Alignment(horizontal='left', vertical='center')
        cell.border    = Border(right=_side('thin', 'D0D0D0'),
                                bottom=_side('thin', 'EBEBEB'))

    # Data columns
    for col_i, grp in col_group.items():
        cell = ws.cell(row=row_i, column=col_i)
        cell.fill           = _fill(PALETTE[grp][tone])
        cell.font           = Font(size=9)
        cell.alignment      = Alignment(horizontal='right', vertical='center')
        cell.number_format  = '0.0000'
        is_start = (col_i - N_IDX - 1) % N_STATS == 0
        cell.border = Border(
            left   = _side('medium', '888888') if is_start else _side('thin', 'D9D9D9'),
            right  = _side('thin', 'D9D9D9'),
            bottom = _side('thin', 'EBEBEB'),
        )

# ── Freeze panes: lock header rows and index columns ─────────────────────────
ws.freeze_panes = ws.cell(row=N_HEADER + 1, column=N_IDX + 1)

wb.save(summary_xlsx)

print(f"Indicator summary -> {summary_xlsx}  ({len(summary_wide):,} rows)")
print(f"  Columns: {ms_present}  x  {SUMMARY_STATS}")


_elapsed = _time.time() - _t_start
print(f"Total time: {_elapsed/60:.1f} min ({_elapsed:.0f} s)")
