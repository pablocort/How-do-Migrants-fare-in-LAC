import pandas as pd
import numpy as np

import os

pd.options.display.float_format = '{:,.2f}'.format  # Adjust the number of decimal places as needed
np.set_printoptions(suppress=True)  # Suppress scientific notation in NumPy arrays
#%%
# load data

# Specify the folder path
folder_path = r'C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\bases armo\armo'
# List all files in the folder
files = os.listdir(folder_path)
# Filter the files (e.g., CSV files)
files = [f for f in files if f.endswith('.dta')]
# Read each file and store the DataFrames in a list
dfs = []
for file in files:
    df = pd.read_stata(folder_path + f'\\{file}') 
    dfs.append(df)



concat_data = pd.concat(dfs)
concat_data.columns = concat_data.columns.str.lower()
concat_data.columns.to_list()

concat_data[concat_data['pais_c']=='ECU']['idh_ch'].isna().sum()

#%%
##############---------------##############---------------##############---------------##############---------------
# migration and population

concat_data.mig_pais_ci.value_counts()
top_mig_contries = (
concat_data.groupby(['pais_c', 'mig_pais_ci'])['factor_ci']
    .sum()
    .reset_index(name='counts')
    .pivot(index='mig_pais_ci', columns='pais_c', values='counts')
    .fillna(0)
    .reset_index()
)
name = top_mig_contries.columns.to_list()[1]
# sort by top countries
top_mig_contries.sort_values(by=name, ascending=False, inplace=True)
# keep top 8 countries
top_mig_contries = top_mig_contries.head(8)

total_migrants = concat_data.groupby('migrante_ci')['factor_ci'].sum()[1]
#create table
top_mig_contries['percentage'] = (top_mig_contries[name] / total_migrants) 

# replace total migrants % in first row

top_mig_contries.loc[top_mig_contries.index[0], 'percentage'] = (total_migrants/top_mig_contries.iloc[0,1] )
concat_data['mig_pais_ci'].value_counts()

# create foreign born variable
concat_data['foreign_born'] = concat_data['mig_pais_ci'].apply(lambda x: 'Native' if x == '' else 
                                                               'Foreign_common' if x == top_mig_contries.iloc[1,0] else
                                                                'Foreign_other'
)
concat_data['foreign_born'].value_counts()
#%%
# population aggregates

population = (
    concat_data.groupby(['pais_c','foreign_born'])['factor_ci']
    .sum()
    .reset_index(name='Population')
    .pivot_table(index=[], columns=['pais_c','foreign_born'], values='Population')   
    )

population_16_64 = (
    concat_data[concat_data['edad_ci'].between(16,64)]
    .groupby(['pais_c','foreign_born'])['factor_ci']
    .sum()
    .reset_index(name='Population_16_64')
    .pivot_table(index=[], columns=['pais_c','foreign_born'], values='Population_16_64')   
    )

population = pd.concat([population, population_16_64], axis=0)

#%%
# labor market indicators

labor_1 = (
concat_data.groupby(['pais_c','foreign_born','emp_ci', 'desemp_ci', 'pea_ci'])['factor_ci']
    .sum()
    .reset_index(name='counts')
    .pivot(index=['emp_ci', 'desemp_ci', 'pea_ci'], columns=['pais_c','foreign_born'], values='counts')
    
)
labor_1.index

# Create a mapping from index tuples to labels
status_map = {
    (0.0, 0.0, 0.0): 'Inactive',
    (0.0, 1.0, 1.0): 'Unemployed',
    (1.0, 0.0, 1.0): 'Occupied'
}

# Replace the index
labor_1.index = labor_1.index.map(status_map)

# (Optional) give the index a name
labor_1.index.name = 'labor_status'

pd.concat([population, labor_1], axis=0)

#%%
# labor market rates : wages and hours
concat_data[['ytot_ci', 'horastot_ci', 'factor_ci']].describe()
concat_data[['ytot_ci', 'horastot_ci', 'factor_ci']].info()



cols = ['pais_c','foreign_born','ytot_ci','horastot_ci','factor_ci']

diag = (concat_data[cols]
        .groupby(['pais_c','foreign_born'])
        .agg(
            n=('factor_ci','size'),
            w_sum=('factor_ci','sum'),
            w_na=('factor_ci', lambda s: s.isna().sum()),
            y_na=('ytot_ci', lambda s: s.isna().sum()),
            h_na=('horastot_ci', lambda s: s.isna().sum()),
            y_dtype=('ytot_ci', lambda s: s.dtype),
            h_dtype=('horastot_ci', lambda s: s.dtype),
        )
        .reset_index()
)

diag

def wavg(g, value_col, weight_col='factor_ci'):
    v = pd.to_numeric(g[value_col], errors='coerce').to_numpy()
    w = pd.to_numeric(g[weight_col], errors='coerce').to_numpy()
    m = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if m.sum() == 0:
        return np.nan
    return np.average(v[m], weights=w[m])

labor_2 = (
    concat_data
      .groupby(['pais_c','foreign_born'])
      .apply(lambda g: pd.Series({
          'ytot_ci_wavg': wavg(g, 'ytot_ci'),
          'horastot_ci_wavg': wavg(g, 'horastot_ci'),
          'w_sum_used': pd.to_numeric(g['factor_ci'], errors='coerce')
                         .where(pd.to_numeric(g['factor_ci'], errors='coerce') > 0)
                         .sum()
      }))
      .reset_index()
)

labor_2
