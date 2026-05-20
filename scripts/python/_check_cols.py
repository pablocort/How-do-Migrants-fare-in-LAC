import warnings, pandas as pd, os
warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for name, rel in [
    ('PER_2024a', r'bases armo\armo\per\PER_2024a_BID.dta'),
    ('COL_2025t3', r'bases armo\armo\col\COL_2025t3_BID.dta'),
]:
    path = os.path.join(BASE, rel)
    cols = list(pd.io.stata.StataReader(path).variable_labels().keys())
    print(name + ' p207=' + str('p207' in cols) + ', p3271=' + str('p3271' in cols)
          + ', sexo_ci=' + str('sexo_ci' in cols) + ', sexo=' + str('sexo' in cols))
