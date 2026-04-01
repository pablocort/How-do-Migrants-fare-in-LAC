#%load_ext autoreload
#%autoreload 

#%%
import pandas as pd
import numpy as np
from pandas.io.stata import StataReader
import unidecode
import os
from functions import make_weighted_stats_multi, make_weighted_pivot_multi, fix_orthography
from functions import plot_scatter_stats, plot_labor_stats, check_update
import re
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns



pd.options.display.float_format = '{:,.3f}'.format  # Adjust the number of decimal places as needed
np.set_printoptions(suppress=True)  # Suppress scientific notation in NumPy arrays

out_path_descriptive = r'C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out\indicator_descriptive'


#%%
# load data

# Specify the folder path
folder_path = r'C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\bases armo\armo'
# List all files in the folder
files = os.listdir(folder_path)
# Filter the files (e.g., CSV files)
files = [f for f in os.listdir(folder_path) if f.lower().endswith('.dta')]  # Adjust the filter as needed to select the desired
files
# Read each file and store DataFrames in a list
dfs = []
value_labels_by_var = {}
value_labels_by_file = {}
variable_labels_by_file = {}

#create a function to normalize variable names and values (e.g., for education levels)
def _norm_code(x):
    try:
        xf = float(x)
        return int(xf) if xf.is_integer() else xf
    except Exception:
        return x
# create a function to create slugs (e.g., for country names)
def _slug(txt):
    s = str(txt).strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^0-9a-zA-Z]+", "_", s).strip("_").lower()
    return s or "unknown"

for file in files:
    path = os.path.join(folder_path, file)

    with StataReader(path) as reader:
        value_labels = reader.value_labels() or {}
        variable_labels = reader.variable_labels() or {}

        # Persist labels by file and aggregate value labels for all variables.
        value_labels_by_file[file] = value_labels
        variable_labels_by_file[file] = variable_labels
        for var_name, labels in value_labels.items():
            if isinstance(labels, dict):
                value_labels_by_var.setdefault(var_name, {}).update(labels)

        # Key fix: do NOT convert categoricals (prevents duplicate label error)
        df = reader.read(convert_categoricals=False)
        #df.attrs["value_labels"] = value_labels


        # Optional: keep metadata (handy if you later want to map labels)
        df.attrs[f"variable_labels_{file}"] = variable_labels
        df.attrs[f"value_labels_{file}"] = value_labels

        # keep only relevant columns for analysis
        cols_to_keep = [
    'pais_c',
    'mig_pais_ci',
    'migrante_ci',
    'sexo_ci',
    'factor_ci',
    'edad_ci',
    'idh_ch',
    # labor market
    'emp_ci', 'desemp_ci', 'pea_ci', 'condocup_ci',
    'ytot_ci', 'horastot_ci',
    'formal_ci', 'tipocontrato_ci', 'aedu_ci',
     'edu_hdmf'
]

    # Remove duplicated names while preserving order
    cols_to_keep = list(dict.fromkeys(cols_to_keep))

    # Keep available columns and notify missing ones
    missing_cols = [c for c in cols_to_keep if c not in df.columns]
    if missing_cols:
        print(f"[WARN] {file} missing columns: {missing_cols}")

    existing_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[existing_cols].copy()

    # Add missing columns as NaN so all files share the same schema
    for c in missing_cols:
        df[c] = np.nan

    df = df[cols_to_keep]
    dfs.append(df)


#%%
#concat all country datasets into one
concat_data = pd.concat(dfs)
concat_data.attrs["value_labels_by_var"] = value_labels_by_var
concat_data.attrs["value_labels_by_file"] = value_labels_by_file
concat_data.attrs["variable_labels_by_file"] = variable_labels_by_file


#turns all column names to lowercase for easier handling
concat_data.columns = concat_data.columns.str.lower()
concat_data.columns.to_list()

# check missing values in key variables for ECUADOR
concat_data[concat_data['pais_c']=='ECU']['idh_ch'].isna().sum()

# remove missings country information
concat_data = concat_data[concat_data['pais_c'] != '']  
concat_data.shape

# check country  variable for all
concat_data.pais_c.value_counts()

# check migration country variable and correct encoding issues
def _fix_mojibake(s: str) -> str:
    # Try common UTF-8/Latin-1 double-encoding issue: "PerÃº" -> "Perú"
    try:
        repaired = s.encode("latin1").decode("utf-8")
        return repaired
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s

def normalize_country_name(x):
    if pd.isna(x):
        return x

    s = str(x).strip()
    s = _fix_mojibake(s)  # general encoding repair
    s = re.sub(r"\s+", " ", s)  # collapse multiple spaces
    s = unicodedata.normalize("NFC", s)

    # Canonical aliases (true naming variants, not encoding errors)
    aliases = {
        "Estados Unidos": "Estados Unidos de América",
        "EEUU": "Estados Unidos de América",
        "USA": "Estados Unidos de América",
        "U.S.A.": "Estados Unidos de América",
    }
    return aliases.get(s, s)
concat_data["mig_pais_ci"].value_counts(dropna=False)

# apply normalization to migration country variable
concat_data["mig_pais_ci"] = concat_data["mig_pais_ci"].apply(normalize_country_name)



#%%
# process some variables
concat_data['condocup_ci'].value_counts(dropna=False)
#drop observations with missing values in key variables for  migration status
concat_data = concat_data.dropna(subset=['migrante_ci'])  # drop rows with missing values in key variables for labor market status and migration status

concat_data.groupby('pais_c')['condocup_ci'].value_counts(dropna=False).unstack().fillna(0)
concat_data.groupby('pais_c')['migrante_ci'].value_counts(dropna=False).unstack().fillna(0)
concat_data.groupby('pais_c')['factor_ci'].sum()



# create variables for labor market status: inactive
concat_data['inactivo_ci'] = concat_data['condocup_ci'].apply(lambda x: 1 if x == 3 else 0) # create inactive variable


## mig variables
# Recode migrante_ci to more descriptive labels
concat_data['migrante_ci'] = concat_data['migrante_ci'].replace({1: 'Migrant', 0: 'Native'})
concat_data['migrante_ci'].value_counts(dropna=False)
concat_data.groupby(['pais_c','formal_ci'])['factor_ci'].size()

# age groups
concat_data['edad_ci'].describe()
concat_data['age_group'] = pd.cut(concat_data['edad_ci'],
    bins=[0, 18,35, 64, np.inf],
    labels=['0-17', '18-34', '35-64', '65+'],  
    right=False
)
concat_data['age_group'].value_counts(dropna=False)
#%%
##############---------------##############---------------##############---------------##############---------------
# migration and population
concat_data[concat_data['pais_c']=='PER']['mig_pais_ci'].value_counts()

# get top 20 migrant countries of origin for each country of residence (pais_c)
countries = concat_data['pais_c'].dropna().unique()
tables = []

for c in countries:
    df_c = concat_data.loc[concat_data['pais_c'] == c]

    # country-specific denominator (total migrants in that pais_c)
    total_migrants_c = (
        df_c.loc[df_c['migrante_ci'] == 'Migrant', 'factor_ci']
        .sum()
    )

    tmp = (
        df_c.loc[df_c['migrante_ci'] == 'Migrant']
        .groupby('mig_pais_ci')['factor_ci']
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .to_frame(name=c)
    )

    # avoid division by zero just in case
    tmp[f'percentage_{c}'] = tmp[c] / total_migrants_c if total_migrants_c else 0

    tables.append(tmp)

# concatenate all tables into one DataFrame, filling missing values with 0 
# (countries that are not in the top 20 for a given pais_c will have NaN, which we replace with 0)
top_mig_contries = (
    pd.concat(tables, axis=1)
      .fillna(0)
      .reset_index()
)

# optional: order columns as (count, %) per country
ordered_cols = ['mig_pais_ci']
for c in countries:
    if c in top_mig_contries.columns:
        ordered_cols += [c, f'percentage_{c}']
top_mig_contries = top_mig_contries[ordered_cols]

# check no weighted counts by country of origin and residence
concat_data.groupby(['pais_c','mig_pais_ci']).size().reset_index(name='counts').\
    pivot_table(index='pais_c', columns=['mig_pais_ci'], values='counts').fillna(0).T.\
    sort_values(by='COL', ascending=False)

# create foreign born variable
concat_data['foreign_born'] = concat_data['mig_pais_ci'].apply(lambda x: 'Native' if x == '' else 
                                                               'Venezuela' if x == 'Venezuela' else
                                                                'Foreign_other'
    )

concat_data.groupby(['pais_c','foreign_born'])['factor_ci'].sum().reset_index(name='counts')

#top_mig_contries
#%%
##############---------------##############---------------##############---------------##############---------------
# population aggregates
#total
population = (
    concat_data.groupby(['pais_c','foreign_born'])['factor_ci']
    .sum()
    .reset_index(name='Population')
    .pivot_table(index=[], columns=['pais_c','foreign_born'], values='Population')   
    )
#population by age group 16-64 (working age population)
population_16_64 = (
    concat_data[concat_data['edad_ci'].between(16,64)]
    .groupby(['pais_c','foreign_born'])['factor_ci']
    .sum()
    .reset_index(name='Population_16_64')
    .pivot_table(index=[], columns=['pais_c','foreign_born'], values='Population_16_64')   
    )
# concatenate total population and population 16-64 into one DataFrame (side by side)
population = pd.concat([population, population_16_64], axis=0)#.T.reset_index()
population


# Make a copy to avoid side effects
pop = population.copy()

# Loop over countries
for country in pop.columns.get_level_values(0).unique():
    
    # Native + Foreign_other
    pop[(country, 'Venezuela+Foreign_other')] = (
        pop[(country, 'Venezuela')] + pop[(country, 'Foreign_other')]
    )
    
    # Total population
    pop[(country, 'Total')] = (
        pop[(country, 'Native')]
        + pop[(country, 'Foreign_other')]
        + pop[(country, 'Venezuela')]
    )
    pop.reset_index()
 

# Optional: sort columns nicely
pop = pop.sort_index(axis=1)

countries = pop.columns.get_level_values(0).unique()
order2 = ['Native', 'Venezuela', 'Venezuela+Foreign_other',  'Foreign_other','Total']

full_order = [(c, k) for c in countries for k in order2]

# (optional) keep only those that exist (prevents KeyError)
full_order = [col for col in full_order if col in pop.columns]

pop = pop.reindex(columns=pd.MultiIndex.from_tuples(full_order, names=pop.columns.names))
pop.T.reset_index()

consolidated_ind = concat_data.copy()



#%%
#################################=--------------##############---------------##############---------------##############---------------
# education levels by migration status

'''
# for education level grouping the high school or less categories, we can replace the variable names with more descriptive labels
consolidated_ind['edu_hdmf'] = consolidated_ind['edu_hdmf'].replace({
    'Menos de primaria': 'Media o menos',
    'Primaria incompleta': 'Media o menos',
    'Primaria completa': 'Media o menos',
    'Media incompleta': 'Media o menos',
    'Media completa': 'Media o menos',
    'Universitaria incompleta': 'Universitaria incompleta',
    'Universitaria completa': 'Universitaria completa'
    })
'''

# Build normalized label map once
edu_hdmf_value_labels = value_labels_by_var.get("edu_hdmf", {})
edu_label_map = {_norm_code(k): v for k, v in edu_hdmf_value_labels.items()}

edu_codes = pd.to_numeric(consolidated_ind["edu_hdmf"], errors="coerce")
education_dummies = pd.get_dummies(edu_codes, dtype=int, dummy_na= True)
education_dummies.sum(axis=1).value_counts()

# Rename dummy columns using labels from attrs metadata
rename_map = {}
for code in education_dummies.columns:
    key = _norm_code(code)
    label = edu_label_map.get(key, f"code {key}")
    rename_map[code] = f"edu_hdmf_{(label)}"


education_dummies = education_dummies.rename(columns=rename_map)
#remove 'edu_hdmf2' from columns and orthonographically normalize them
education_dummies.columns = (
    education_dummies.columns
    .str.replace(r"^edu_hdmf_", "", regex=True)
    .map(fix_orthography)
)


consolidated_ind = pd.concat([consolidated_ind, education_dummies], axis=1)

#check a random column for consistency
consolidated_ind.groupby(['foreign_born','Media completa'])['factor_ci'].agg(['sum', 'count'])

#apply the function
education = make_weighted_stats_multi(
    df=consolidated_ind,
    group_cols=["pais_c", "foreign_born"],
    status_cols=education_dummies.columns.tolist(),
    weight_col="factor_ci",
    include_se=True,
    include_ci=True,
    include_neff=True,
    include_n_unweighted=True,
    include_sum_weights=True,
    output_format="long",
)
education

education['variable'].value_counts(dropna=False)

# replace values and names for foreign_born 
education['foreign_born'] = education['foreign_born'].replace({'Native': 'Nativos', 
                                                       'Venezuela': 'Migrantes de Venezuela', 
                                                       'Foreign_other': 'Migrantes de otros países'}) 

education['foreign_born'] = pd.Categorical(education['foreign_born'],
                                            categories=['Nativos', 'Migrantes de Venezuela', 'Migrantes de otros países'],
                                            ordered=True)
#replace nan with other missing name
education['variable'] = education['variable'].replace({np.nan: 'Missing'})

categories = education['variable'].dropna().unique().tolist()

education['variable'] = pd.Categorical(education['variable'], 
                                       categories=categories,
                                       ordered=True)

# export the whole table to excel (with MultiIndex columns)
education_output = (education
    .pivot_table(index = ['pais_c','variable'], 
                  values=['mean', 'std', 'n_unweighted', 'sum_weights', 'ones_unweighted', 'ones_weights',
                          'err_lo', 'err_hi'],
                 columns=[ 'foreign_born'])
    )
education_output

#education_output.iloc[:9,6].sum()

#education_output.to_excel(out_path_descriptive + r'\education_by_migration_status_march_9_includeNAN.xlsx')

'''
dfs[0].attrs.keys()
dfs[0].attrs['variable_labels_COL_2025t3_BID.dta']
dfs[0].attrs['value_labels_COL_2025t3_BID.dta']['aedu_ci']

'''
#%%
# labor indicators by migration status: export to latex tables (one per country)

["emp_ci","desemp_ci","inactivo_ci","pea_ci"]

labor = make_weighted_stats_multi(
    df=consolidated_ind[consolidated_ind['edad_ci'].between(16,64)],
    group_cols=["pais_c", "foreign_born"],
    status_cols=["emp_ci","desemp_ci","inactivo_ci","pea_ci"],
    weight_col="factor_ci",
    include_se=True,
    include_ci=True,
    include_neff=True,
    include_n_unweighted=True,
    include_sum_weights=True,
    output_format="long",
)
labor.loc[0:2, 'mean'].sum()


#replace values and names
labor['variable'] = labor['variable'].replace({'emp_ci': 'Población ocupada',
 'desemp_ci': 'Población desocupada',
 'inactivo_ci': 'Población inactiva',
 'pea_ci': 'Población económicamente activa'})

labor['foreign_born'] = labor['foreign_born'].replace({'Native': 'Nativos', 
                                                       'Venezuela': 'Migrantes de Venezuela', 
                                                       'Foreign_other': 'Migrantes de otros países'}) 
  
labor['foreign_born'] = pd.Categorical(labor['foreign_born'],
                                            categories=['Nativos', 'Migrantes de Venezuela', 'Migrantes de otros países'],
                                            ordered=True)
#replace nan with other missing name
#labor['variable'] = labor['variable'].replace({np.nan: 'Missing'})



# export the whole table to excel (with MultiIndex columns)
labor_output = (labor
    .pivot_table(index = ['pais_c','variable'], 
                  values=['mean', 'std', 'n_unweighted', 'sum_weights', 'ones_unweighted', 'ones_weights',
                          'err_lo', 'err_hi'],
                 columns=[ 'foreign_born'])
    )
labor_output

labor_output.iloc[:,6:15]


#%%
# apply the function to plot labor market indicators by migration status
check_update()

fig_lab = plot_labor_stats(
    labor,
    x_var="foreign_born",
    hue_var="pais_c",
    filter_variable="Población ocupada",       # bars
    point_variable="Población económicamente activa",        # points overlaid
    title="Población ocupada y económicamente activa según estatus migratorio",
)
fig_lab
fig_lab.savefig(out_path_descriptive + r'\labor_VenPop_march_11.png', dpi=300, bbox_inches='tight')


fig_edu = plot_labor_stats(
    education,
    x_var="foreign_born",
    hue_var="pais_c",
    filter_variable="Media incompleta",       # bars
    point_variable="Universitaria completa",        # points overlaid
    title="Niveles educativos según estatus migratorio",
)
#fig_edu.savefig(out_path_descriptive + r'\education_march_11.png', dpi=300, bbox_inches='tight')
#%%
# apply the function to plot education levels by migration status

fig_edu = plot_scatter_stats(
    education[education['variable'].isin(['Universitaria completa'])],
    x_var   = "pais_c",
    y_var   = "mean",
    hue_var = "foreign_born",
    ylabel  = "Porcentaje",
    xlabel  = "",
    palette = "Blues",
    y_lim=(0, 0.3)
)
plt.show()

fig_edu.savefig(out_path_descriptive + r'\education_march_11.png', dpi=300, bbox_inches='tight')


# educación basicao o menos = sum of categories: 'Menos de primaria', 'Primaria incompleta', 'Primaria completa', 'Media incompleta', 'Media completa'
edu_basica = education[education['variable'].isin(['Menos de primaria', 'Primaria incompleta', 'Primaria completa', 'Media incompleta', 'Media completa'])].copy()
edu_basica = edu_basica.groupby(['pais_c','foreign_born'])['mean'].sum().reset_index(name='mean')#.pivot_table(index='pais_c', columns='foreign_born', values='mean')

fig_basica = plot_scatter_stats(
    edu_basica,
    x_var   = "pais_c",
    y_var   = "mean",
    hue_var = "foreign_born",
    ylabel  = "Porcentaje",
    xlabel  = "",
    palette = "Blues",
    y_lim=(0.3, 1)
)
plt.show()

fig_basica.savefig(out_path_descriptive + r'\education_basica_march_18.png', dpi=300, bbox_inches='tight')


fig_lab = plot_scatter_stats(
    labor[labor['variable'].isin(['Población ocupada'])],
    x_var   = "pais_c",
    y_var   = "mean",
    hue_var = "foreign_born",
    ylabel  = "Porcentaje",
    xlabel  = "",
    palette = "Blues",
    y_lim=(0.55, 0.9)
)
plt.show()

fig_lab.savefig(out_path_descriptive + r'\labor_VenPop_march_18.png', 
                dpi=300, bbox_inches='tight')



fig_lab = plot_scatter_stats(
    labor[labor['variable'].isin(['Población desocupada'])],
    x_var   = "pais_c",
    y_var   = "mean",
    hue_var = "foreign_born",
    ylabel  = "Porcentaje",
    xlabel  = "",
    palette = "Blues",
    y_lim=(0, 0.15)
)
plt.show()

fig_lab.savefig(out_path_descriptive + r'\labor_desem_18.png', 
                dpi=300, bbox_inches='tight')

#%%
# population shares by migration status (for scatter plot)



df = pop.T.reset_index()

# Extract total population per country
totals = df[df['foreign_born'] == 'Total'].set_index('pais_c')['Population']

# Divide all numeric columns by each country's total population
numeric_cols = df.select_dtypes(include='number').columns
df[numeric_cols] = df[numeric_cols].div(df['pais_c'].map(totals), axis=0)

df


fig_foreign = plot_scatter_stats(
    df[~(df['foreign_born'].isin(['Native', 'Total', 'Venezuela+Foreign_other']))],
    x_var   = "pais_c",
    y_var   = "Population",
    hue_var = "foreign_born",
    ylabel  = "Porcentaje",
    xlabel  = "",
    palette = "Blues",
    y_lim=(0, 0.175)
)
plt.show()

fig_foreign.savefig(out_path_descriptive + r'\population_venezuelans.png', 
                   dpi=300, bbox_inches='tight')

# population by sex

population_age = (
    consolidated_ind.groupby(['pais_c', 'foreign_born', 'age_group'])['factor_ci']
    .sum()
    .reset_index(name='Population')
)

# Total population per country × foreign_born group
group_totals = (
    population_age
    .groupby(['pais_c', 'foreign_born'])['Population']
    .transform('sum')
)

population_age['share'] = population_age['Population'] / group_totals

population_age_graph = plot_scatter_stats(
    population_age[population_age['foreign_born'] == 'Venezuela'],
    x_var   = "pais_c",
    y_var   = "share",
    hue_var = "age_group",
    ylabel  = "Porcentaje",
    xlabel  = "",
    palette = "Blues",
    y_lim=(0, 0.6)
)
plt.show()
population_age_graph.savefig(out_path_descriptive + r'\population_venezuelans_age.png', 
                   dpi=300, bbox_inches='tight')




#%%
####################33
# formality status and others
#apply the function

consolidated_ind[consolidated_ind['condocup_ci'] == 1].\
        groupby(['pais_c'])['formal_ci'].value_counts(dropna=False)

consolidated_ind.columns


formal = make_weighted_stats_multi(
    df=consolidated_ind[((consolidated_ind['condocup_ci'] == 1)) &
                        ~(consolidated_ind['pais_c'].isin(['USA']))],
    group_cols=["pais_c", "foreign_born"],
    status_cols=["formal_ci"],
    weight_col="factor_ci",
    include_se=True,
    include_ci=True,
    include_neff=True,
    include_n_unweighted=True,
    include_sum_weights=True,
    output_format="long",
)
formal

formal['variable'].value_counts(dropna=False)

# replace values and names for foreign_born 
formal['foreign_born'] = formal['foreign_born'].replace({'Native': 'Nativos', 
                                                       'Venezuela': 'Migrantes de Venezuela', 
                                                       'Foreign_other': 'Migrantes de otros países'}) 

formal['foreign_born'] = pd.Categorical(formal['foreign_born'],
                                            categories=['Nativos', 'Migrantes de Venezuela', 'Migrantes de otros países'],
                                            ordered=True)
#replace nan with other missing name
formal['variable'] = formal['variable'].replace({np.nan: 'Missing'})

categories = formal['variable'].dropna().unique().tolist()

formal['variable'] = pd.Categorical(formal['variable'], 
                                     categories=categories,
                                     ordered=True)
## create a graph for formality status by migration status
fig_formal = plot_scatter_stats(
    formal[formal['variable'] == 'formal_ci'],
    x_var   = "pais_c",
    y_var   = "mean",
    hue_var = "foreign_born",
    ylabel  = "Porcentaje formalidad",
    xlabel  = "",
    palette = "Blues",
    y_lim=(0, 1)
)






































#%%
# exportation: labor table 1 - one tex per country
#########################

os.makedirs("out_indicators", exist_ok=True)

stats_t = stats.T  # columns: MultiIndex (pais_c, foreign_born)

for country in stats_t.columns.get_level_values(0).unique():

    # 1) subset columns for this country
    df_country = stats_t.loc[:, stats_t.columns.get_level_values(0) == country].copy()

    # 2) keep only foreign_born as column labels (so columns are: Native, Venezuela, ...)
    df_country.columns = df_country.columns.droplevel(0)

    # 3) build LaTeX column format: first col = text, rest = numeric via siunitx
    colfmt = "l" + "S" * df_country.shape[1]

    # 4) export to latex
    latex_table = df_country.to_latex(
        index=True,
        escape=False,
        float_format="%.3f",      # keeps numeric formatting before siunitx renders
        column_format=colfmt,
        multicolumn=False,        # IMPORTANT: we'll handle headers ourselves
        caption=f"Indicadores del mercado laboral – {country}",
        label=f"tab:labor_{country.lower()}"
    )

    # 5) Fix header row so it displays column names even with S columns
    # Replace the header line (the one with column names) by wrapping each header
    # in \multicolumn{1}{c}{...} so LaTeX treats it as text.
    lines = latex_table.splitlines()

    # Find the header row: it's usually right after \toprule
    # Example pattern: " & Native & Venezuela & ... \\"
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip() == r"\toprule":
            header_idx = i + 1
            break

    if header_idx is not None and header_idx < len(lines):
        header_line = lines[header_idx]
        parts = [p.strip() for p in header_line.split("&")]

        # parts[0] is the index name cell (often empty). Keep it as-is.
        new_parts = [parts[0]]
        for p in parts[1:]:
            # keep the trailing "\\" if present in last element
            p_clean = p.replace(r"\\", "").strip()
            suffix = r" \\" if p.strip().endswith(r"\\") else ""
            new_parts.append(rf"\multicolumn{{1}}{{c}}{{{p_clean}}}{suffix}".strip())

        # rebuild header line with proper & spacing
        # ensure only last cell has the \\ (already included)
        # remove any accidental \\ from earlier cells
        for j in range(1, len(new_parts)-1):
            new_parts[j] = new_parts[j].replace(r"\\", "").strip()

        lines[header_idx] = " & ".join(new_parts)

    latex_table_fixed = "\n".join(lines)

    # 6) save
    out_path = f"out_indicators/labor_market_stats_{country}.tex"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(latex_table_fixed)

print("Done: wrote one .tex per country in out_indicators/")


#%%
##############---------------##############---------------##############---------------##############---------------
# labor 2 - market rates : wages and hours
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

#%%
##############---------------##############---------------##############---------------##############---------------
# formality status and others

concat_data['tipocontrato_ci'].replace({'Sin_contrato/verbal':'Sin contrato/verbal'}, inplace=True)


concat_data['formal_ci'].value_counts()



formality = make_weighted_pivot_multi(
    df=concat_data,
    group_cols=['pais_c', 'foreign_born'],
    status_cols=['formal_ci', 'tipocontrato_ci'],
    transpose=False,
    flatten_cols=True
).T
formality

education = make_weighted_pivot_multi(
    df=concat_data,
    group_cols=['pais_c', 'foreign_born'],
    status_cols=[ 'aedu_ci'],
    transpose=False,
    flatten_cols=True
).T
education



# %%
################---------------##############---------------##############---------------##############---------------
# save data

output_folder = r'C:\Users\PABLOCOR\OneDrive - Inter-American Development Bank Group\Archivos de Paraiso Pinto Furtado Luzes, Marta - Equipo Conocimiento\Datos\hdmf\How-do-Migrants-fare-in-LAC\out'

with pd.ExcelWriter(output_folder + r'\hdmf_indicators_labor_FEB6.xlsx') as writer:
    top_mig_contries.to_excel(writer, sheet_name='top_mig_contries', index=True)
    labor_1.to_excel(writer, sheet_name='labor_1', index=True)
    stats.to_excel(writer, sheet_name='labor_2', index=True)


