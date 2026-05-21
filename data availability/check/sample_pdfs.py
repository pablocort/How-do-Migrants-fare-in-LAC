"""Sample text and tables from all PDFs returning 0 variables."""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PDFS = {
    "ARG": "arg/EPH_registro_4T2023.pdf",
    "BOL": "bol/ddi-documentation-spanish-163.pdf",
    "GUY": "guy/GLFS_Bulletin_2021_Third-Quarter.pdf",
    "HTI": "hti/DHS7_Household_QRE_EN_16Mar2017_DHSQ7.pdf",
    "MEX": "mex/dicc2024.pdf",
    "CHL": "chl/Cuestionario_Casen_2024.pdf",
}

for iso, path in PDFS.items():
    print(f"\n{'='*60}")
    print(f"=== {iso}: {path} ===")
    try:
        with pdfplumber.open(path) as pdf:
            print(f"    Total pages: {len(pdf.pages)}")
            # Sample pages 1, 2, and one from the middle
            sample_pages = [0, 1, min(5, len(pdf.pages)-1), min(10, len(pdf.pages)-1)]
            for pi in dict.fromkeys(sample_pages):
                page = pdf.pages[pi]
                # Check for tables
                tables = page.extract_tables()
                text = page.extract_text() or ""
                print(f"\n  --- Page {pi+1} ---")
                if tables:
                    print(f"    Tables found: {len(tables)}")
                    for ti, t in enumerate(tables[:2]):
                        print(f"    Table {ti+1} ({len(t)} rows x {len(t[0]) if t else 0} cols):")
                        for row in t[:4]:
                            print(f"      {[str(c)[:30] if c else '' for c in row]}")
                else:
                    print("    No tables")
                if text:
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    print(f"    Text ({len(lines)} lines):")
                    for line in lines[:12]:
                        print(f"      {line[:100]}")
    except Exception as e:
        print(f"    ERROR: {e}")
