"""
build_population_table_ppt.py
─────────────────────────────────────────────────────────────────────────────
Population table for the HDMF presentation.

For each country (most recent wave), reports by migrant-status group:
  - Native (migrante_ci == 0)
  - Venezuelan migrant (migrante_ci == 1 AND mig_pais_ci == "Venezuela")
  - Other migrant (migrante_ci == 1 AND not Venezuelan)
  - Total (all persons)

Columns: Total (weighted) | Male (weighted) | Female (weighted) | N (obs, unweighted)

Countries: COL (2025t3), CHL (2024a), ECU (2025m12), PER (2024a), USA (2024), ESP (2025a)

Output: out/ppt_population/YYYY-MM-DD/population_table_ppt.xlsx

Generated with the Claude HDMF system — 2026-05-18
"""

import os
from datetime import date

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMO_DIR = os.path.join(BASE_DIR, 'bases armo', 'armo')
DATE_TAG = date.today().strftime('%Y-%m-%d')
OUT_DIR  = os.path.join(BASE_DIR, 'out', 'ppt_population', DATE_TAG)
os.makedirs(OUT_DIR, exist_ok=True)

# ── Wave config ────────────────────────────────────────────────────────────────
# (folder, filename, label, wave_label, sex_var)
# sex_var: raw column name for sex in this BID file (1=Male, 2=Female)
WAVES = {
    'COL': ('col',  'COL_2025t3_BID.dta',  'Colombia',      '2025', 'p3271'),
    'CHL': ('chl',  'CHL_2024a_BID.dta',   'Chile',         '2024', 'sexo'),
    'ECU': ('ecu',  'ECU_2025m12_BID.dta', 'Ecuador',       '2025', 'sexo_ci'),
    'PER': ('per',  'PER_2024a_BID.dta',   'Peru',          '2024', 'p207'),
    'USA': ('usa',  'USA_2024_BID.dta',    'United States', '2024', 'sex'),
    'ESP': ('ESP',  'ESP_2025a_BID.dta',   'Spain',         '2025', 'sexo_ci'),
}
COUNTRY_ORDER = ['COL', 'CHL', 'ECU', 'PER', 'USA', 'ESP']

GROUPS = ['Native', 'Venezuelan migrant', 'Other migrant', 'Total']

# ── Helpers ────────────────────────────────────────────────────────────────────

def _fix_mojibake(s):
    try:
        return s.encode('latin1').decode('utf-8')
    except Exception:
        return s


def _load(iso3):
    folder, fname, _, _, sex_var = WAVES[iso3]
    path = os.path.join(ARMO_DIR, folder, fname)
    if not os.path.exists(path):
        print(f'  [MISSING] {path}')
        return None
    cols = ['migrante_ci', 'mig_pais_ci', sex_var, 'factor_ci']
    df = pd.read_stata(path, columns=cols, convert_categoricals=False)
    df = df.rename(columns={sex_var: 'sexo_ci'})
    # Normalize country name strings
    if 'mig_pais_ci' in df.columns:
        df['mig_pais_ci'] = (
            df['mig_pais_ci']
            .astype(str)
            .apply(_fix_mojibake)
            .str.strip()
            .str.lower()
        )
    return df


def _classify(df):
    """Add 'group' column: Native / Venezuelan migrant / Other migrant."""
    is_migrant  = df['migrante_ci'] == 1
    is_ven      = is_migrant & (df['mig_pais_ci'] == 'venezuela')
    is_other    = is_migrant & ~(df['mig_pais_ci'] == 'venezuela')
    is_native   = df['migrante_ci'] == 0

    df = df.copy()
    df['group'] = np.where(is_native,  'Native',
                  np.where(is_ven,     'Venezuelan migrant',
                  np.where(is_other,   'Other migrant',
                                       'Unknown')))
    return df


def _stats(df):
    """Return dict: total_w, male_w, female_w, n_obs for a (sub)group."""
    total_w = df['factor_ci'].sum()
    male_w  = df.loc[df['sexo_ci'] == 1, 'factor_ci'].sum()
    female_w= df.loc[df['sexo_ci'] == 2, 'factor_ci'].sum()
    n_obs   = len(df)
    return {'total_w': total_w, 'male_w': male_w, 'female_w': female_w, 'n_obs': n_obs}


# ── Build rows ─────────────────────────────────────────────────────────────────
rows = []

for iso3 in COUNTRY_ORDER:
    _, _, country_label, wave_label, _ = WAVES[iso3]
    print(f'Loading {iso3} ...')
    df = _load(iso3)
    if df is None:
        continue
    df = _classify(df)

    for grp in ['Venezuelan migrant']:
        sub = df[df['group'] == grp]
        s   = _stats(sub)
        rows.append({'Country': country_label, 'Wave': wave_label,
                     'Group': grp, **s})


table = pd.DataFrame(rows)

# Console preview
print('\n' + '='*80)
print(f'{"Country":<20} {"Total (w)":>14} {"Male (w)":>14} {"Female (w)":>14} {"N obs":>10}')
print('-'*80)
for _, r in table.iterrows():
    print(f'{r["Country"]:<20} {r["total_w"]:>14,.0f} {r["male_w"]:>14,.0f} '
          f'{r["female_w"]:>14,.0f} {r["n_obs"]:>10,}')
print('='*80)

# ── Excel export ───────────────────────────────────────────────────────────────
HDMF_BLUE    = '1D3557'   # midnight navy — headers
HDMF_MIDBLUE = '2171A0'   # steel blue — total rows
HDMF_LIGHT   = 'EAF0F5'   # panel background
WHITE        = 'FFFFFF'
GRAY_FONT    = '646464'
VEN_FILL     = 'FFF3EE'   # very light warm — Venezuelan rows

thin_gray = Side(style='thin',   color='CCCCCC')
med_navy  = Side(style='medium', color='1D3557')

def bdr(**kw):
    defaults = dict(left=Side(), right=Side(), top=Side(), bottom=Side())
    defaults.update(kw)
    return Border(**defaults)

wb = Workbook()
ws = wb.active
ws.title = 'Population Table'

# ── Column definitions ─────────────────────────────────────────────────────────
HDR = [
    'Country', 'Survey wave',
    'Total\n(weighted)',
    'Male\n(weighted)',
    'Female\n(weighted)',
    'Obs\n(unweighted)',
]
WIDTHS = [18, 13, 18, 18, 18, 16]
DATA_FIELDS = ['Country', 'Wave', 'total_w', 'male_w', 'female_w', 'n_obs']

# header row
for ci, (h, w) in enumerate(zip(HDR, WIDTHS), start=1):
    c = ws.cell(row=1, column=ci, value=h)
    c.font      = Font(bold=True, color=WHITE, size=10)
    c.fill      = PatternFill('solid', fgColor=HDMF_BLUE)
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border    = bdr(left=med_navy, right=med_navy, top=med_navy, bottom=med_navy)
    ws.column_dimensions[get_column_letter(ci)].width = w
ws.row_dimensions[1].height = 36

# data rows
prev_country = None
for ri, (_, row) in enumerate(table.iterrows(), start=2):
    new_ctry = row['Country'] != prev_country and prev_country is not None
    prev_country = row['Country']
    fill_hex = VEN_FILL
    font_kw  = dict(size=10)
    top_s    = med_navy if new_ctry else thin_gray

    for ci, field in enumerate(DATA_FIELDS, start=1):
        v = row[field]
        c = ws.cell(row=ri, column=ci)

        if field in ('total_w', 'male_w', 'female_w', 'n_obs'):
            c.value          = int(round(v)) if pd.notna(v) else 'N/A'
            c.number_format  = '#,##0'
            c.alignment      = Alignment(horizontal='right', vertical='center')
        else:
            c.value     = v
            c.alignment = Alignment(horizontal='left', vertical='center')

        c.fill   = PatternFill('solid', fgColor=fill_hex)
        c.font   = Font(color='000000', **font_kw)
        c.border = bdr(
            left   = med_navy if ci == 1 else thin_gray,
            right  = med_navy if ci == len(DATA_FIELDS) else thin_gray,
            top    = top_s,
            bottom = thin_gray,
        )
    ws.row_dimensions[ri].height = 17

# note row
note_row = len(table) + 2
note = (
    'Notes: Weighted counts use factor_ci survey weights. '
    'All ages included (no age restriction). '
    'Venezuelan migrants: migrante_ci == 1 and mig_pais_ci == "Venezuela". '
    'Other migrants: migrante_ci == 1 and born outside survey country (non-Venezuelan). '
    'Waves: Colombia 2025 Q3 (GEIH), Chile 2024 (CASEN), Ecuador Dec 2025 (ENEMDU), '
    'Peru 2024 (ENAHO), United States 2024 (IPUMS ACS), Spain 2025 (EPA). '
    'Generated with the Claude HDMF system — ' + DATE_TAG + '.'
)
ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=len(HDR))
nc = ws.cell(row=note_row, column=1, value=note)
nc.font      = Font(size=8, color=GRAY_FONT, italic=True)
nc.alignment = Alignment(horizontal='left', wrap_text=True)
ws.row_dimensions[note_row].height = 45

out_path = os.path.join(OUT_DIR, 'population_table_ppt.xlsx')
wb.save(out_path)
print(f'\nSaved: {out_path}')

# ── LaTeX Beamer slide ─────────────────────────────────────────────────────────
SURVEY_LABELS = {
    'Colombia':      'GEIH',
    'Chile':         'CASEN',
    'Ecuador':       'ENEMDU',
    'Peru':          'ENAHO',
    'United States': 'IPUMS ACS',
    'Spain':         'EPA',
}

def fmt(n):
    """Format integer with thousands separator for LaTeX."""
    return f'{int(round(n)):,}'

rows_tex = []
for _, r in table.iterrows():
    survey = SURVEY_LABELS.get(r['Country'], '')
    rows_tex.append(
        f"  {r['Country']} & {survey} & {r['Wave']} & "
        f"{fmt(r['total_w'])} & {fmt(r['male_w'])} & {fmt(r['female_w'])} & "
        f"{fmt(r['n_obs'])} \\\\"
    )

table_body = '\n'.join(rows_tex)

tex = r"""% ============================================================
%  HDMF -- How Do Migrants Fare in LAC?
%  Generated with the Claude HDMF system — """ + DATE_TAG + r"""
% ============================================================

\documentclass[aspectratio=169, 10pt]{beamer}

% ---------- Minimalist theme --------------------------------
\usetheme{default}
\usecolortheme{default}
\setbeamertemplate{navigation symbols}{}
\setbeamerfont{frametitle}{size=\large, series=\bfseries}

\definecolor{hdmfblue}{RGB}{0,75,135}
\definecolor{hdmfgray}{RGB}{120,120,120}
\definecolor{hdmflight}{RGB}{242,246,250}
\definecolor{hdmfrule}{RGB}{0,75,135}

% Frame title: left-aligned navy text + thin rule below
\setbeamercolor{frametitle}{fg=hdmfblue, bg=white}
\setbeamertemplate{frametitle}{%
  \vspace{0.55em}%
  \insertframetitle\par%
  \vspace{0.15em}%
  {\color{hdmfrule}\rule{\textwidth}{0.6pt}}\par%
  \vspace{0.1em}%
}

% Bullets
\setbeamercolor{itemize item}{fg=hdmfblue}
\setbeamercolor{itemize subitem}{fg=hdmfgray}
\setbeamertemplate{itemize item}{\small$\bullet$}
\setbeamertemplate{itemize subitem}{\footnotesize$-$}

% Minimal footline: right-aligned page number only
\setbeamertemplate{footline}{%
  \hfill%
  {\tiny\color{hdmfgray}%
    HDMF \textbar{} IDB \quad%
    \insertframenumber\,/\,\inserttotalframenumber\quad%
  }%
  \vspace{0.35em}%
}

% ---------- Packages ----------------------------------------
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{array}
\usepackage{colortbl}

% ---------- Metadata ----------------------------------------
\title[HDMF]{How Do Migrants Fare in LAC?}
\author[IDB]{IDB Migration Unit}
\institute{}
\date{""" + date.today().strftime('%B %Y') + r"""}

% ============================================================
\begin{document}
% ============================================================

% ---- Title slide -------------------------------------------
\begin{frame}[plain]
  \vfill
  \centering
  {\color{hdmfrule}\rule{0.55\textwidth}{0.6pt}}\\[1.2em]
  {\Large\bfseries\color{hdmfblue}
    Labor Market and Education Outcomes of Venezuelan\\[0.25em]
    Migrants in LAC: Gaps and Opportunities}\\[1.2em]
  {\normalsize IDB MIG}\\[0.4em]
  {\small\color{hdmfgray}""" + date.today().strftime('%B %Y') + r"""}\\[1.2em]
  {\color{hdmfrule}\rule{0.55\textwidth}{0.6pt}}
  \vfill
\end{frame}

% ---- Slide 1: Context & motivation -------------------------
\begin{frame}{Measuring Migrants in Household Surveys}
  \vspace{0.5em}
  \begin{itemize}\setlength\itemsep{1.2em}
    \item It is critical to understand to what extent national household surveys
          can accurately cover migrant populations --- not just whether a survey
          exists, but how reliably it measures them.
    \item Any country can run a survey. What matters more is whether a
          \textbf{permanent, institutionalized source of data} exists.
          We are working to build that capacity \textbf{within national
          statistical offices}.
  \end{itemize}
\end{frame}

% ---- Slide 2: Population table -----------------------------
\begin{frame}{Venezuelan Migrants: Population Coverage}
  {\small\color{hdmfgray}Household surveys --- most recent wave per country}
  \vspace{0.4em}
  \centering\small
  \begin{tabular}{llr rrr r}
    \toprule
    \textbf{Country} & \textbf{Survey} & \textbf{Year} &
    \textbf{Total} & \textbf{Male} & \textbf{Female} & \textbf{N obs} \\
    \midrule
""" + table_body + r"""
    \bottomrule
  \end{tabular}

  \vspace{0.5em}
  \raggedright{\tiny
    \textbf{Note:} Weighted counts (survey expansion factor). Venezuelan migrants identified
    via country of birth. All ages included.\\[0.15em]
    \textbf{Source:} Data processed by IDB Migration Unit using household national surveys.
  }
\end{frame}

% ---- Slide 3: Informality chart ----------------------------
\begin{frame}{Venezuelan Migrants vs.\ Natives: Informality}
  \begin{center}
    \includegraphics[height=0.68\textheight, keepaspectratio]{informality_chart.png}
  \end{center}
  \vspace{-0.4em}
  {\tiny
    \textbf{Source:} Data processed by IDB Migration Unit using household national surveys.
    COL GEIH 2018t3 \& 2025t3 $|$ PER ENAHO 2018a \& 2024a $|$
    CHL CASEN 2017a \& 2024a $|$ ECU ENEMDU 2018m12 \& 2025m12.
  }
\end{frame}

% ---- Thanks slide ------------------------------------------
\begin{frame}[plain]
  \vfill
  \centering
  {\large\bfseries\color{hdmfblue} Thank you}\\[2em]
  {\normalsize Pablo Cort\'{e}s S\'{a}nchez}\\[0.5em]
  {\normalsize\color{hdmfgray}\texttt{pablocor@iadb.org}}
  \vfill
\end{frame}

\end{document}
"""

latex_dir = os.path.join(BASE_DIR, 'out', 'ppt_population', DATE_TAG)
tex_path  = os.path.join(latex_dir, 'population_slide.tex')
with open(tex_path, 'w', encoding='utf-8') as f:
    f.write(tex)
print(f'Saved: {tex_path}')

# ── Copy informality chart into latex_dir so \includegraphics finds it ────────
import subprocess, shutil
chart_src = os.path.join(BASE_DIR, 'out', 'venezuela_vs_native', DATE_TAG,
                         'venezuela_vs_native_ind_informality.png')
chart_dst = os.path.join(latex_dir, 'informality_chart.png')
if os.path.exists(chart_src):
    shutil.copy2(chart_src, chart_dst)
    print(f'Chart copied: {chart_dst}')
else:
    print(f'WARNING: chart not found at {chart_src} -- slide 2 image will be missing')

# ── Compile PDF ────────────────────────────────────────────────────────────────
pdflatex = shutil.which('pdflatex')
if pdflatex:
    for _ in range(2):   # two passes for page count
        result = subprocess.run(
            [pdflatex, '-interaction=nonstopmode', '-output-directory', latex_dir, tex_path],
            capture_output=True, text=True
        )
    pdf_path = tex_path.replace('.tex', '.pdf')
    if os.path.exists(pdf_path):
        print(f'PDF compiled: {pdf_path}')
    else:
        print('pdflatex ran but PDF not found — check .log for errors')
else:
    print('pdflatex not found — .tex file saved; compile manually')
