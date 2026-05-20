"""
Generate methodology documentation for HDMF pooled indicators as a Word (.docx) file.
Output: out/scl_full/YYYY-MM-DD/HDMF_Pooled_Indicators_Methodology.docx
"""
import os
from datetime import date
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Output path ────────────────────────────────────────────────────────────────
TODAY = date.today().strftime("%Y-%m-%d")
OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "out", "scl_full", TODAY,
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "HDMF_Pooled_Indicators_Methodology.docx")

# ── Colours ────────────────────────────────────────────────────────────────────
NAVY   = RGBColor(0x1D, 0x35, 0x57)
TEAL   = RGBColor(0x21, 0x71, 0xA0)
RED    = RGBColor(0xC0, 0x39, 0x2B)
GRAY   = RGBColor(0x55, 0x55, 0x55)
LGRAY  = RGBColor(0xF0, 0xF0, 0xF0)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
BLACK  = RGBColor(0x00, 0x00, 0x00)
AMBER  = RGBColor(0xFF, 0xC0, 0x00)


def _set_cell_bg(cell, hex_color: str):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def _hdr_cell(cell, text, bg="1D3557", fg=WHITE, bold=True, size=10, center=True):
    _set_cell_bg(cell, bg)
    p = cell.paragraphs[0]
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.color.rgb = fg
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def _data_cell(cell, text, bg="FFFFFF", bold=False, size=10, center=True):
    _set_cell_bg(cell, bg)
    p = cell.paragraphs[0]
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(str(text) if text is not None else "")
    run.bold = bold
    run.font.size = Pt(size)
    run.font.color.rgb = BLACK
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def add_heading(doc, text, level=1, color=NAVY):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        run.font.color.rgb = color
        if level == 1:
            run.font.size = Pt(16)
        elif level == 2:
            run.font.size = Pt(13)
        else:
            run.font.size = Pt(11)
    return p


def add_para(doc, text, bold=False, italic=False, size=10.5, color=BLACK, space_before=0, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    run = p.add_run(text)
    run.bold   = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return p


def add_bullet(doc, text, level=0, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.color.rgb = BLACK
    return p


def add_formula(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.font.name  = "Courier New"
    run.font.size  = Pt(10)
    run.font.color.rgb = RGBColor(0x1D, 0x35, 0x57)
    return p


def add_note(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent  = Cm(0.8)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run("Note: " + text)
    run.font.size  = Pt(9)
    run.font.italic = True
    run.font.color.rgb = GRAY
    return p


# ── Build document ─────────────────────────────────────────────────────────────
doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(3.0)

# Default paragraph font
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(10.5)

# ── Title block ────────────────────────────────────────────────────────────────
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after  = Pt(4)
tr = title_p.add_run("How Do Migrants Fare in LAC?")
tr.bold = True
tr.font.size = Pt(20)
tr.font.color.rgb = NAVY

sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub_p.paragraph_format.space_after = Pt(2)
sr = sub_p.add_run("Methodological Note: Pooled Indicator Estimation")
sr.bold = True
sr.font.size = Pt(14)
sr.font.color.rgb = TEAL

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
date_p.paragraph_format.space_after = Pt(20)
dr = date_p.add_run(date.today().strftime("%B %d, %Y") + "  ·  IDB — SCL Division")
dr.font.size = Pt(10)
dr.font.color.rgb = GRAY
dr.italic = True

doc.add_paragraph()  # spacer

# ── 1. Overview ────────────────────────────────────────────────────────────────
add_heading(doc, "1. Overview", level=1)
add_para(doc,
    "This note describes how the LAC-5 pooled indicators are computed in the HDMF "
    "(How Do Migrants Fare) project. The analysis compares Venezuelan-born migrants "
    "against native-born populations across five countries: Colombia (COL), Peru (PER), "
    "Chile (CHL), Ecuador (ECU), and Spain (ESP). Two aggregation methods are produced "
    "and compared: R4V-weighted (used in the main presentation) and Survey-pooled "
    "(used as a robustness check).")

add_para(doc,
    "All estimates are produced from harmonised household survey microdata "
    "('_BID.dta' files), loaded via a pre-built cache ('_hdmf_cache.pkl'). "
    "The pipeline is implemented in 'scl_presentation.py'.")

# ── 2. Data sources ────────────────────────────────────────────────────────────
add_heading(doc, "2. Data Sources", level=1)

add_heading(doc, "2.1  Household surveys", level=2)

tbl = doc.add_table(rows=1, cols=5)
tbl.style = "Table Grid"
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
hdrs = ["Country", "Survey", "Recent wave", "Early wave", "Sample (Venezuelan, recent)"]
for i, h in enumerate(hdrs):
    _hdr_cell(tbl.rows[0].cells[i], h, bg="1D3557")

rows_data = [
    ("Colombia",  "GEIH",       "2025 Q3",   "2018 Q3",   "~77,000 obs → 2,069,798 exp."),
    ("Peru",      "ENAHO",      "2024",       "2018",       "~10,000 obs → 188,083 exp."),
    ("Chile",     "CASEN",      "2024",       "2017",       "~28,000 obs → 741,208 exp."),
    ("Ecuador",   "ENEMDU",     "2025 Dec",   "2018 Dec",   "~12,000 obs → 440,400 exp."),
    ("Spain",     "EPA",        "2025",       "2018",       "~22,000 obs → 753,859 exp."),
]
for i, (ctry, surv, rec, ear, smp) in enumerate(rows_data):
    row = tbl.add_row()
    bg = "F0F0F0" if i % 2 == 0 else "FFFFFF"
    _data_cell(row.cells[0], ctry,  bg=bg, bold=True, center=False)
    _data_cell(row.cells[1], surv,  bg=bg)
    _data_cell(row.cells[2], rec,   bg=bg)
    _data_cell(row.cells[3], ear,   bg=bg)
    _data_cell(row.cells[4], smp,   bg=bg, center=False)

doc.add_paragraph()
add_note(doc,
    "'Obs' = unweighted number of Venezuelan-born respondents in the survey microdata. "
    "'Exp.' = sum of factor_ci (survey expansion factor) — the weighted population count "
    "that those respondents represent.")

add_heading(doc, "2.2  R4V reference figures", level=2)
add_para(doc,
    "R4V (Plataforma Regional de Coordinación Interagencial para Refugiados y Migrantes de "
    "Venezuela) publishes country-level estimates of the Venezuelan migrant stock. These "
    "figures are used as the country-level weights in the R4V-weighted aggregation method. "
    "Values correspond to the most recent year available at the time of analysis (2025–2026).")

tbl2 = doc.add_table(rows=1, cols=4)
tbl2.style = "Table Grid"
tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(["Country", "R4V weight", "Source", "LAC-5 share (%)"]):
    _hdr_cell(tbl2.rows[0].cells[i], h, bg="1D3557")

r4v_rows = [
    ("Colombia", "2,800,000", "Migración Colombia, Feb 2026",      "45.8%"),
    ("Peru",     "1,600,000", "SUNAMI, Feb 2026",                   "26.2%"),
    ("Chile",      "669,400", "INE Census 2024, May 2025",          "10.9%"),
    ("Spain",      "602,500", "UNDESA IMS 2024 via R4V, May 2025",   "9.9%"),
    ("Ecuador",    "440,400", "MoG, May 2025",                       "7.2%"),
    ("Total",    "6,112,300", "",                                  "100.0%"),
]
for i, (c, w, s, sh) in enumerate(r4v_rows):
    row = tbl2.add_row()
    bg = "F0F0F0" if i % 2 == 0 else "FFFFFF"
    if c == "Total":
        bg = "1D3557"
        for j, v in enumerate([c, w, s, sh]):
            _hdr_cell(row.cells[j], v, bg="1D3557")
    else:
        _data_cell(row.cells[0], c, bg=bg, bold=True, center=False)
        _data_cell(row.cells[1], w, bg=bg)
        _data_cell(row.cells[2], s, bg=bg, center=False)
        _data_cell(row.cells[3], sh, bg=bg)

doc.add_paragraph()

# ── 3. Indicator definitions ───────────────────────────────────────────────────
add_heading(doc, "3. Indicator Definitions", level=1)
add_para(doc,
    "All indicators are binary (0/1) variables defined at the individual level in the "
    "harmonised microdata. Each indicator is computed as a weighted proportion — the "
    "weighted sum of the binary variable over the eligible sub-population.")

add_para(doc,
    "The eligible population (denominator) differs by indicator. The table below lists "
    "the numerator condition, the denominator, and the relevant harmonised variable name.")

tbl3 = doc.add_table(rows=1, cols=4)
tbl3.style = "Table Grid"
tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl3.columns[0].width = Cm(4.5)
tbl3.columns[1].width = Cm(4.5)
tbl3.columns[2].width = Cm(4.5)
tbl3.columns[3].width = Cm(3.5)
for i, h in enumerate(["Indicator", "Numerator condition (yᵢ = 1 when…)", "Denominator (eligible pop.)", "Key variable(s)"]):
    _hdr_cell(tbl3.rows[0].cells[i], h, bg="1D3557")

ind_rows = [
    ("Working age (15–64)",
     "Individual aged 15–64",
     "All ages (total pop.)",
     "edad_ci"),
    ("Labour force participation",
     "Active in the labour force",
     "Working-age pop., 16–64",
     "pea_ci = 1"),
    ("Tertiary education",
     "Post-secondary education or higher",
     "Working-age pop., 16–64",
     "edu_hdmf ≥ 7"),
    ("Unemployment",
     "Unemployed (seeking work, available)",
     "Active pop. (pea_ci = 1, aged 16–64)",
     "desemp_ci = 1"),
    ("Inactivity",
     "Not in the labour force",
     "Working-age pop., 16–64",
     "inactivo_ci = 1"),
    ("Informality",
     "Not in a formal job",
     "Employed (emp_ci = 1)",
     "formal_ci = 0"),
    ("Part-time employment",
     "Working fewer than full-time hours",
     "Employed (emp_ci = 1)",
     "parcial_ci = 1"),
    ("Long hours (50h+/week)",
     "Working more than 50 hours per week",
     "Employed (emp_ci = 1)",
     "horastot_ci > 50"),
]
for i, (ind, num, den, var) in enumerate(ind_rows):
    row = tbl3.add_row()
    bg = "F0F0F0" if i % 2 == 0 else "FFFFFF"
    _data_cell(row.cells[0], ind, bg=bg, bold=True, center=False)
    _data_cell(row.cells[1], num, bg=bg, center=False)
    _data_cell(row.cells[2], den, bg=bg, center=False)
    _data_cell(row.cells[3], var, bg=bg, center=False)

doc.add_paragraph()
add_note(doc,
    "Variable names follow the HDMF harmonisation codebook. "
    "Two variables are derived at runtime: "
    "higher_edu_ci = (edu_hdmf ≥ 7), and longhours_ci = (horastot_ci > 50).")

# ── 4. Estimation process ──────────────────────────────────────────────────────
add_heading(doc, "4. Estimation Process", level=1)
add_para(doc,
    "The LAC-5 pooled estimate is built in two sequential stages. "
    "The same Stage 1 is used by both aggregation methods; they diverge only in Stage 2.")

add_heading(doc, "4.1  Stage 1 — Within-country survey-weighted proportion", level=2)
add_para(doc,
    "For each country c and each group g (Venezuelan / Native), the indicator is computed "
    "as a Horvitz-Thompson weighted proportion over the eligible sub-population E_c :")

add_formula(doc,
    "p̂(c, g) = Σᵢ∈E(c,g)  wᵢ · yᵢ  /  Σᵢ∈E(c,g)  wᵢ")

add_para(doc,
    "where wᵢ = factor_ci (the individual survey expansion factor, i.e. the number of "
    "people in the population that respondent i represents) and yᵢ ∈ {0, 1} is the "
    "binary indicator value. Missing values in either wᵢ or yᵢ are excluded from both "
    "the numerator and denominator.")

add_para(doc,
    "The 'working_age' indicator is a special case: its denominator is the total weighted "
    "population (all ages, not a sub-population), so it is computed as:")

add_formula(doc,
    "working_age(c, g) = Σᵢ∈[15-64](c,g) wᵢ  /  Σᵢ∈all(c,g) wᵢ  × 100")

add_para(doc,
    "This stage produces one scalar per country × indicator × group combination. "
    "For 5 countries × 8 indicators × 2 groups × 2 periods = 160 scalars in total.")

add_heading(doc, "4.2  Stage 2a — R4V-weighted cross-country aggregation (main method)", level=2)
add_para(doc,
    "The LAC-5 estimate is a weighted average of the five country estimates, "
    "using the R4V Venezuelan stock as the country weight:")

add_formula(doc,
    "P̂_LAC(g) = Σ_c  W_c · p̂(c,g)  /  Σ_c  W_c")

add_para(doc,
    "where W_c = COUNTRY_R4V_WEIGHTS[c] (see Section 2.2). This gives Colombia a 45.8% "
    "weight, Peru 26.2%, and so on. The implicit assumption is that the R4V figures "
    "correctly represent the true distribution of Venezuelan migrants across countries.")

add_para(doc,
    "Spain is excluded from the unemployment and informality aggregates "
    "(ESP_MASKED indicators) due to known harmonisation gaps in the EPA scripts for those "
    "two variables. For those indicators, the aggregate is effectively LAC-4 "
    "(COL, PER, CHL, ECU) with weights re-normalised over the four countries.")

add_heading(doc, "4.3  Stage 2b — Survey-pooled aggregation (robustness check)", level=2)
add_para(doc,
    "As an alternative, all individual microdata rows from all five countries are "
    "concatenated into a single dataset, and the survey-weighted proportion is "
    "computed once over the full pool:")

add_formula(doc,
    "P̂_pool(g) = Σ_c Σᵢ∈E(c,g)  wᵢ · yᵢ  /  Σ_c Σᵢ∈E(c,g)  wᵢ")

add_para(doc,
    "In this case, each country's effective weight in the aggregate is determined "
    "by the sum of factor_ci across its Venezuelan-born (or native) survey respondents. "
    "This reflects the in-survey population count rather than the R4V administrative figure.")

add_para(doc,
    "The survey-pooled method implicitly assumes that each household survey faithfully "
    "captures the size (and characteristics) of the Venezuelan migrant population in that "
    "country. In practice, household surveys often undercount migrants — particularly "
    "irregular ones — so the survey-pooled estimates may underweight countries with "
    "large undercoverage gaps.")

# ── 5. Key differences ─────────────────────────────────────────────────────────
add_heading(doc, "5. Comparison: R4V-weighted vs. Survey-pooled", level=1)
add_para(doc,
    "The Excel file 'scl_pooled_weighting_comparison.xlsx' reports both estimates "
    "side by side for all 8 indicators × 2 periods (recent 2024–25, early 2017–18).")

add_heading(doc, "5.1  Why the two methods diverge", level=2)
add_para(doc,
    "The main driver of divergence is the gap between R4V figures and household survey "
    "estimates. The 'Country_Weights' sheet in the comparison workbook shows both sets "
    "of shares. The clearest example is Peru: R4V registers 1,600,000 Venezuelans "
    "(26.2% of LAC-5), but ENAHO only captures ~188,000 (well under 10% of the survey "
    "total). If Peruvian Venezuelan migrants have systematically different outcomes "
    "from Colombian ones, this gap will shift the pooled estimate meaningfully.")

add_para(doc, "Colour coding in the comparison sheet:")
add_bullet(doc, "Yellow cell: R4V-weighted value is more than 0.05 pp higher than Survey-pooled.")
add_bullet(doc, "Blue cell: R4V-weighted value is more than 0.05 pp lower than Survey-pooled.")
add_bullet(doc, "Grey cell: difference is within ±0.05 pp (methods agree).")

add_heading(doc, "5.2  Which method to use and when", level=2)

tbl4 = doc.add_table(rows=1, cols=3)
tbl4.style = "Table Grid"
tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(["Criterion", "R4V-weighted", "Survey-pooled"]):
    _hdr_cell(tbl4.rows[0].cells[i], h,
              bg=("1D3557" if i == 0 else ("C0392B" if i == 1 else "2E7D6B")))

comp_rows = [
    ("Represents",
     "True diaspora distribution (as best estimated by R4V)",
     "In-survey distribution (weighted by survey expansion factors)"),
    ("Preferred when",
     "You want to characterise the average Venezuelan migrant in LAC",
     "You want to characterise the average survey-observed migrant"),
    ("Sensitive to",
     "R4V figure accuracy; country ordering in the diaspora",
     "Survey undercoverage of migrants; survey design differences"),
    ("Spain treatment",
     "Excluded for informality & unemployment (ESP_MASKED)",
     "Excluded for same indicators (same logic applied)"),
    ("Used in",
     "Main presentation slides (pooled_a.png, pooled_b.png)",
     "Robustness check only (comparison workbook)"),
]
for i, (crit, r4v, sur) in enumerate(comp_rows):
    row = tbl4.add_row()
    bg = "F0F0F0" if i % 2 == 0 else "FFFFFF"
    _data_cell(row.cells[0], crit, bg=bg, bold=True, center=False)
    _data_cell(row.cells[1], r4v, bg="FAD4CC", center=False)
    _data_cell(row.cells[2], sur, bg="C8EAE2", center=False)

doc.add_paragraph()

# ── 6. Limitations ─────────────────────────────────────────────────────────────
add_heading(doc, "6. Limitations", level=1)

limitations = [
    ("No cross-country income deflation",
     "All monetary variables are in nominal local currency units. "
     "For the labour market rate indicators (proportions 0–100%) this is irrelevant, "
     "but any income-based indicator would require PPP or CPI adjustment before pooling."),
    ("No design-effect correction",
     "Standard errors are not adjusted for complex survey design (stratification, "
     "clustering, multi-stage sampling). The 95% confidence bands shown in the "
     "trend charts are computed via a linearised Taylor series approximation "
     "(var(p̂) = Σ wᵢ²(yᵢ−p̂)² / W²) but the pooled-indicator point estimates "
     "have no reported standard errors."),
    ("Temporal heterogeneity",
     "The 'recent' period spans waves from 2024 (Peru, Chile) to 2025 Q3 (Colombia) "
     "and 2025 Dec (Ecuador). These are treated as contemporaneous. If labour market "
     "conditions shifted sharply between 2024 and 2025, within-period variation "
     "is absorbed into the cross-country comparison."),
    ("Two-stage estimator is not a meta-analysis",
     "Stage 2 uses country-level point estimates only, ignoring within-country "
     "estimation variance. A formally optimal pooling would weight by the inverse of "
     "variance (precision-weighted meta-analysis), not by population size. The current "
     "approach is easier to interpret and communicate but is not minimum-variance."),
    ("Spain harmonisation gaps",
     "The informality and unemployment variables for Spain (EPA) have known "
     "harmonisation issues and are excluded from both aggregation methods. "
     "This means the LAC-5 aggregate for those two indicators is effectively LAC-4."),
    ("Survey representativeness of migrants",
     "Household surveys are typically designed to represent the resident population "
     "and may undercount irregular or recently arrived migrants. The Venezuelan migrant "
     "population — a large share of whom arrived after 2018 — may be disproportionately "
     "missed in standard household sampling frames, leading to selection bias."),
]

for title, text in limitations:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(5)
    run_bold = p.add_run(title + ": ")
    run_bold.bold = True
    run_bold.font.size = Pt(10.5)
    run_bold.font.color.rgb = NAVY
    run_text = p.add_run(text)
    run_text.font.size = Pt(10.5)
    run_text.font.color.rgb = BLACK

# ── 7. Output files ─────────────────────────────────────────────────────────────
add_heading(doc, "7. Output Files", level=1)

tbl5 = doc.add_table(rows=1, cols=3)
tbl5.style = "Table Grid"
tbl5.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(["File", "Location", "Contents"]):
    _hdr_cell(tbl5.rows[0].cells[i], h, bg="1D3557")

output_rows = [
    ("scl_full_presentation.pdf",
     "out/scl_full/[DATE]/",
     "Beamer PDF with all charts and slides"),
    ("scl_full_data.xlsx",
     "out/scl_full/[DATE]/",
     "Chart-ready data for all presentation slides (8 sheets)"),
    ("scl_pooled_weighting_comparison.xlsx",
     "out/scl_full/[DATE]/",
     "R4V-weighted vs. survey-pooled side-by-side for all 8 indicators × 2 periods"),
    ("pooled_a.png / pooled_b.png",
     "out/scl_full/[DATE]/",
     "LAC-5 pooled indicator charts (R4V-weighted, used in slides 7–8)"),
    ("_hdmf_cache.pkl",
     "bases armo/armo/",
     "Pre-built microdata cache; rebuilt by hdmf_build.py"),
]
for i, (f, loc, cont) in enumerate(output_rows):
    row = tbl5.add_row()
    bg = "F0F0F0" if i % 2 == 0 else "FFFFFF"
    _data_cell(row.cells[0], f,    bg=bg, bold=True, center=False)
    _data_cell(row.cells[1], loc,  bg=bg, center=False)
    _data_cell(row.cells[2], cont, bg=bg, center=False)

doc.add_paragraph()

# ── Footer note ─────────────────────────────────────────────────────────────────
add_note(doc,
    f"Generated automatically by build_methods_doc.py · {date.today().strftime('%B %d, %Y')} · "
    "IDB Social Protection and Labor Division (SCL). "
    "Source code: bases armo/armo/scl_presentation.py.")

# ── Save ─────────────────────────────────────────────────────────────────────
doc.save(OUT_PATH)
print(f"Saved: {OUT_PATH}")
