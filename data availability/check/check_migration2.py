"""Detailed migration variable check for BRA and CHL, and residency check for COL."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BROAD_MIG = ["nasc", "natur", "migr", "estrang", "foreign", "pais", "país", "country",
             "birth", "born", "nacim", "extran", "nationality", "nacion"]
BROAD_TIME = ["resid", "arriv", "chegad", "morando", "tempo", "time", "anos", "años",
              "meses", "permanec", "quanto tempo", "cuanto", "desde"]

def search(iso, keywords, label=""):
    d = json.load(open(f"decoded/{iso}_dictionary.json", encoding="utf-8"))
    hits = []
    for v in d["variables"]:
        text = (v.get("name","") + " " + v.get("label","")).lower()
        if any(kw in text for kw in keywords):
            hits.append(f"  {v['name']:20s}  {v['label'][:80]}")
    print(f"\n=== {iso} — {label} ({len(hits)} hits) ===")
    for h in hits[:10]:
        print(h)

# BRA PNADC — has migration module (V1027 etc.)
search("BRA", BROAD_MIG, "migration identifiers")
search("BRA", BROAD_TIME, "residence time")

# CHL — 47 extracted variables
search("CHL", BROAD_MIG, "migration identifiers")
search("CHL", BROAD_TIME, "residence time")

# COL — check for birthplace and residence time more broadly
search("COL", ["nacim", "nacer", "nacido", "birth", "pais de", "país de",
               "lugar de", "extranje", "extran", "inmigrante"], "migration broad")
search("COL", ["tiempo", "cuanto", "cuánto", "años lleva", "reside",
               "permanenc", "llegó", "llego", "llegada"], "residence time broad")

# DOM
search("DOM", BROAD_MIG, "migration broad")
search("DOM", BROAD_TIME, "residence time broad")

# ECU
search("ECU", BROAD_MIG, "migration broad")
search("ECU", BROAD_TIME, "residence time broad")
