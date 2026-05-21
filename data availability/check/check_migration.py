import json, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MIG_KEYWORDS = [
    "nacimiento", "nacio", "nacido", "born", "birthplace", "birth country",
    "origen", "pais de origen", "lugar de nacimiento", "procedencia",
    "extranjero", "migrante", "migrant", "nacionalidad", "nationality",
    "inmigrante", "immigr",
]

TIME_KEYWORDS = [
    "residencia", "reside", "llegada", "arrival", "tiempo en", "anos en",
    "años en", "cuanto tiempo", "desde cuando", "fecha de llegada",
    "tiempo de residencia", "cuantos anos", "cuántos años", "anos vive",
    "años vive", "how long", "duration", "permanencia", "cuanto lleva",
    "año de llegada",
]

decoded_dir = "decoded"
countries = sorted([
    f.replace("_dictionary.json", "")
    for f in os.listdir(decoded_dir)
    if f.endswith("_dictionary.json")
])

for iso in countries:
    path = os.path.join(decoded_dir, f"{iso}_dictionary.json")
    d = json.load(open(path, encoding="utf-8"))
    mig_hits = []
    time_hits = []
    for v in d["variables"]:
        text = (v.get("name", "") + " " + v.get("label", "")).lower()
        if any(kw in text for kw in MIG_KEYWORDS):
            mig_hits.append((v["name"], v["label"][:70]))
        if any(kw in text for kw in TIME_KEYWORDS):
            time_hits.append((v["name"], v["label"][:70]))
    n = len(d["variables"])
    print(f"=== {iso} ({n} vars) ===")
    print(f"  MIG  ({len(mig_hits)}): {mig_hits[:4]}")
    print(f"  TIME ({len(time_hits)}): {time_hits[:4]}")
    print()
