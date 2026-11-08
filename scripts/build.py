import pathlib,sys
d=pathlib.Path(sys.argv[1])
cards="\n".join((d/"content"/f"{n}.txt").read_text() for n in ["job","alt","code","arch","cyber","quiz"])
assert "</script" not in cards.lower()
(d/"index.html").write_text((d/"template.html").read_text().replace("%%CARDS%%",cards))
