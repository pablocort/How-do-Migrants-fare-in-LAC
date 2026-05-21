"""Check BRA (Portuguese) and CHL variables directly."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# BRA PNADC — Portuguese keywords
bra = json.load(open("decoded/BRA_dictionary.json", encoding="utf-8"))
print("=== BRA all variables ===")
for v in bra["variables"]:
    print(f"  {v['name']:10s}  {v['label'][:90]}")

print("\n\n=== CHL all variables ===")
chl = json.load(open("decoded/CHL_dictionary.json", encoding="utf-8"))
for v in chl["variables"]:
    print(f"  {v['name']:10s}  {v['label'][:90]}")
