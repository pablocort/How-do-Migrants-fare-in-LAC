import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MIG_KEYWORDS = ["migraci", "nacimiento", "p16", "p17", "s01b", "lugar de nac",
                "pais de nac", "país de nac", "tiempo de resid", "llegada",
                "extranjero", "años en"]

with pdfplumber.open("bol/ddi-documentation-spanish-163.pdf") as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    hits = 0
    for i, page in enumerate(pdf.pages):
        t = page.extract_text() or ""
        if any(kw in t.lower() for kw in MIG_KEYWORDS):
            print(f"\n--- Page {i+1} ---")
            print(t[:1500])
            hits += 1
            if hits >= 12:
                print("... (stopping after 12 matching pages)")
                break
