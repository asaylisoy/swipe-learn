import json,pathlib,sys
d=pathlib.Path(sys.argv[1])
cards="\n".join((d/"content"/f"{n}.txt").read_text() for n in ["job","alt","code","arch","cyber","quiz"])
# Tez bölümü JSON'dan gelir: frage -> başlık, antwort -> A, merksatz -> SAY, typ -> TAG
tez=json.loads((d/"content"/"tez.json").read_text())
for c in tez["karten"]:
    assert "|" not in c["frage"] and "\n" not in c["antwort"]+c.get("merksatz",""), c["id"]
    cards+=f"\n@@ tez | {c['kategorie']} | {c['frage']}\nTAG: {c['typ']}\nA: {c['antwort']}\n"+(f"SAY: {c['merksatz']}\n" if c.get("merksatz") else "")
assert "</script" not in cards.lower()
(d/"index.html").write_text((d/"template.html").read_text().replace("%%CARDS%%",cards))
