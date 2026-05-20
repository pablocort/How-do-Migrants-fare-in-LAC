"""
build_speaker_script.py
Generate a clean PDF speaker script for the HDMF presentation.
Generated with the Claude HDMF system -- 2026-05-18
"""

import os, subprocess, shutil
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE_TAG = date.today().strftime('%Y-%m-%d')
OUT_DIR  = os.path.join(BASE_DIR, 'out', 'ppt_population', DATE_TAG)
os.makedirs(OUT_DIR, exist_ok=True)

tex = r"""
\documentclass[11pt, a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[top=2.8cm, bottom=2.8cm, left=3cm, right=3cm]{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{parskip}
\usepackage{microtype}
\usepackage{enumitem}
\usepackage{mdframed}
\usepackage{hyperref}

\definecolor{hdmfblue}{RGB}{0,75,135}
\definecolor{hdmfgray}{RGB}{100,100,100}
\definecolor{notesbg}{RGB}{245,248,252}

\hypersetup{colorlinks=true, urlcolor=hdmfblue, linkcolor=hdmfblue}

% Section style: slide label
\titleformat{\section}[block]
  {\large\bfseries\color{hdmfblue}}
  {}{0em}{}[\vspace{0.15em}{\color{hdmfblue}\titlerule[0.5pt]}\vspace{0.4em}]

\titleformat{\subsection}[block]
  {\small\bfseries\color{hdmfgray}}
  {}{0em}{}

\setlength{\parskip}{0.65em}
\setlength{\parindent}{0pt}

% Speaker note box
\newmdenv[
  backgroundcolor=notesbg,
  linecolor=hdmfblue,
  linewidth=0.5pt,
  leftline=true, rightline=false, topline=false, bottomline=false,
  leftmargin=0pt, rightmargin=0pt,
  innerleftmargin=10pt, innerrightmargin=6pt,
  innertopmargin=5pt, innerbottommargin=5pt,
  skipabove=4pt, skipbelow=4pt,
]{speakernote}

\begin{document}

% ── Header ───────────────────────────────────────────────────────────────────
{\Large\bfseries\color{hdmfblue}
  Labor Market and Education Outcomes of Venezuelan\\[0.2em]
  Migrants in LAC: Gaps and Opportunities}

\vspace{0.4em}
{\normalsize\color{hdmfgray}
  Speaker script \textbar{} Pablo Cort\'{e}s S\'{a}nchez
  \textbar{} IDB Migration Unit \textbar{} """ + date.today().strftime('%B %Y') + r"""}

\vspace{0.2em}
{\color{hdmfblue}\rule{\textwidth}{0.6pt}}

\vspace{1em}

% ── Slide 1: Title ───────────────────────────────────────────────────────────
\section{Slide 1 \textnormal{\textmd{\color{hdmfgray}--- Title}}}

Hi everyone. My name is Pablo Cort\'{e}s, I work at the IDB as part of the
Knowledge team within the Migration Unit. Today I want to talk about two
things: the importance of having reliable data on migrants, and what we can
actually do with it once we have it.

% ── Slide 2: Measuring migrants ──────────────────────────────────────────────
\section{Slide 2 \textnormal{\textmd{\color{hdmfgray}--- Measuring Migrants in Household Surveys}}}

When you work with household surveys and migration, you immediately run into a
structural problem: most of these surveys were simply not designed to capture
migrant populations. The sampling frames --- the lists and geographic units
used to select households --- were built to represent the resident population
at a given point in time. They struggle to identify migrants accurately, and
even more so when you focus on specific subgroups like returnees, refugees, or
recent arrivals.

So the question is not just ``does your country run a survey?'' The real
question is: does a \textbf{permanent, reliable source of information} exist
--- one that is updated regularly and embedded in the national statistical
system? That is a much higher bar.

In our unit, under Jeremy's lead, we are actively working on
\textbf{capacity building within the national statistical offices} of several
countries in the region. The goal is to help them improve how they measure
migrant populations --- not as a one-time exercise, but as a sustained
institutional capability. And each country is a different case: different
surveys, different legal frameworks, different political contexts.

\begin{speakernote}
\textbf{Delivery note:} Pause after ``That is a much higher bar'' --- it
lands better with a beat.
\end{speakernote}

% ── Slide 3: Population table ────────────────────────────────────────────────
\section{Slide 3 \textnormal{\textmd{\color{hdmfgray}--- Venezuelan Migrants: Population Coverage}}}

Here is an example of what household surveys can give us. This table shows
estimates of the Venezuelan diaspora across six countries --- Colombia, Chile,
Ecuador, Peru, the United States, and Spain --- using the most recent
available wave of each national survey.

Colombia stands out immediately: we estimate around 2 million Venezuelans,
which reflects both the scale of the migration flow and the relatively strong
survey coverage there. Ecuador, by contrast, shows only about 130,000 --- not
necessarily because fewer Venezuelans are there, but partly because the survey
has a harder time reaching them. These numbers are valuable, but we should
always read them with the limitations in mind. They are estimates, not counts.

% ── Slide 4: Informality chart ───────────────────────────────────────────────
\section{Slide 4 \textnormal{\textmd{\color{hdmfgray}--- Venezuelan Migrants vs.\ Natives: Informality}}}

Now, what can we actually learn from this data? Here I bring one concrete
example: labor informality. For each country, I compare the informality rate
of Venezuelan migrants against the native population, and I do this at two
points in time --- an early wave around 2017--18, and a more recent wave from
2024--25.

The pattern is striking and consistent: Venezuelan migrants work informally at
much higher rates than natives in every country, and in most cases that gap
has persisted or widened over time. In Colombia, for example, around
\textbf{71\% of employed Venezuelans} are in informal jobs in the recent wave,
versus 44\% of natives. In Ecuador the gap is even larger --- 90\% versus
67\%.

What is also interesting is Chile, where the story runs in the opposite
direction for the early period: Venezuelans arriving in 2017 actually had
\textit{lower} informality than natives --- reflecting positive selection of
early arrivals. By 2024 that advantage had disappeared. So the data is not
just telling us there is a gap --- it is telling us the gap is \textbf{dynamic},
and that the profile of who is arriving matters a lot.

\begin{speakernote}
\textbf{Transition:} These are the kinds of insights that only become possible
when you have consistent, well-measured data over time. Which brings us back
to the original point --- building that capacity is not a technical nicety, it
is what makes this kind of analysis possible at all.
\end{speakernote}

% ── Slide 5: Closing ─────────────────────────────────────────────────────────
\section{Slide 5 \textnormal{\textmd{\color{hdmfgray}--- Thank You}}}

Thank you. Happy to take any questions.

\vspace{0.3em}
{\small\color{hdmfgray}
  Pablo Cort\'{e}s S\'{a}nchez \textbar{}
  \href{mailto:pablocor@iadb.org}{pablocor@iadb.org}
}

\end{document}
"""

tex_path = os.path.join(OUT_DIR, 'speaker_script.tex')
with open(tex_path, 'w', encoding='utf-8') as f:
    f.write(tex)
print(f'Saved: {tex_path}')

pdflatex = shutil.which('pdflatex')
if pdflatex:
    for _ in range(2):
        result = subprocess.run(
            [pdflatex, '-interaction=nonstopmode', '-output-directory', OUT_DIR, tex_path],
            capture_output=True, text=True
        )
    pdf_path = tex_path.replace('.tex', '.pdf')
    if os.path.exists(pdf_path):
        print(f'PDF compiled: {pdf_path}')
    else:
        print('pdflatex ran but PDF not found -- check .log for errors')
        print(result.stdout[-2000:])
else:
    print('pdflatex not found -- .tex saved; compile manually')
