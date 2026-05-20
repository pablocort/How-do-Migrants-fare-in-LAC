import pandas as pd
import numpy as np

stats = make_weighted_stats_multi(
    df=concat_data,
    group_cols=["pais_c", "foreign_born"],
    status_cols=["emp_ci","desemp_ci","inactivo_ci","pea_ci"],
    weight_col="factor_ci",
    add_dummy_counts=True,
    include_n_unweighted=False,
    include_sum_weights=False,
    flatten_cols=True
)
stats

stats_migrante = make_weighted_stats_multi(
    df=concat_data,
    group_cols=["pais_c", "migrante_ci"],
    status_cols=["emp_ci","desemp_ci","inactivo_ci","pea_ci"],
    weight_col="factor_ci",
    add_dummy_counts=True,
    include_n_unweighted=False,
    include_sum_weights=False,
    flatten_cols=True
)
stats_migrante

stats_total = make_weighted_stats_multi(
    df=concat_data,
    group_cols=['pais_c'],
    status_cols=['emp_ci',  'desemp_ci','inactivo_ci', 'pea_ci'],
    weight_col='factor_ci',
    flatten_cols=True,
    add_dummy_counts=True
)


stats_labor = pd.concat([stats, stats_migrante], axis=0).T



# 2) (Optional but recommended) Inspect which columns are duplicated
dup_cols = stats_labor.columns[stats_labor.columns.duplicated()].unique()
if len(dup_cols) > 0:
    print("Duplicated MultiIndex columns found (showing up to 20):")
    print(list(dup_cols[:20]))

# 3) FIX: remove duplicate MultiIndex columns (keep the first occurrence)
stats_labor = stats_labor.loc[:, ~stats_labor.columns.duplicated(keep="first")]

# 4) Build desired column order
# IMPORTANT: get countries from stats_labor (not from pop), because pop may differ
countries = stats_labor.columns.get_level_values(0).unique()

order2 = ['Native', 'Venezuela', 'Foreign_other','Migrant']
full_order = [(c, k) for c in countries for k in order2]

# Keep only tuples that exist (prevents KeyError)
full_order = [col for col in full_order if col in stats_labor.columns]

# 5) Reindex columns in the desired order
stats_labor = stats_labor.reindex(
    columns=pd.MultiIndex.from_tuples(full_order, names=stats_labor.columns.names)
)
#%%
##############---------------##############---------------##############---------------##############---------------
# labor 1 - market indicators


stats = make_weighted_stats_multi(
    df=concat_data,
    group_cols=["pais_c", "foreign_born"],
    status_cols=["emp_ci","desemp_ci","inactivo_ci","pea_ci"],
    weight_col="factor_ci",
    include_se=True,
    include_ci=True,
    ci_level=0.95,
    include_neff=True,
    flatten_cols=False
)
stats.T

stats = stats.T.rename(columns={
    'emp_ci mean': 'Employment (mean)',
    'emp_ci std': 'Employment (sd)',
    'emp_ci ones_unweighted': 'Employment ($N$)',
    'emp_ci ones_weights': 'Employment (weights)',
    'desemp_ci mean': 'Unemployment (mean)',
    'desemp_ci std': 'Unemployment (sd)',
    'desemp_ci ones_unweighted': 'Unemployment ($N$)',
    'desemp_ci ones_weights': 'Unemployment (weights)',
    'inactivo_ci mean': 'Inactive (mean)',
    'inactivo_ci std': 'Inactive (sd)',
    'inactivo_ci ones_unweighted': 'Inactive ($N$)',
    'inactivo_ci ones_weights': 'Inactive (weights)',
    'pea_ci mean': 'Labor force (mean)',
    'pea_ci std': 'Labor force (sd)',
    'pea_ci ones_unweighted': 'Labor force ($N$)',
    'pea_ci ones_weights': 'Labor force (weights)',
})
stats.T