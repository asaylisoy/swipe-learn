#!/usr/bin/env python3
"""YouTube otomatik altyazı (.vtt) dosyalarını temiz, zaman damgalı metin parçalarına çevirir.

Kullanım:
    python3 scripts/vtt_to_chunks.py transcripts/raw transcripts/chunks --minutes 15

Her video için transcripts/chunks/<video>__partNN.md dosyaları oluşur.
Her satır "[hh:mm:ss] metin" formatındadır, böylece kartlarda kaynak zamanı gösterilebilir.
"""
import argparse
import pathlib
import re

TS = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.\d{3} --> ")
TAG = re.compile(r"<[^>]+>")


def parse_vtt(path):
    """(saniye, metin) listesi döndürür; otomatik altyazıdaki tekrar eden satırları atar."""
    out, cur_t, seen_last = [], 0, ""
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = TS.match(line)
        if m:
            h, mi, s = map(int, m.groups())
            cur_t = h * 3600 + mi * 60 + s
            continue
        if not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        text = TAG.sub("", line).strip()
        if not text or text == seen_last:
            continue
        if out and text.startswith(out[-1][1]):  # kayan altyazı: önceki satırı uzatıyor
            out[-1] = (out[-1][0], text)
        else:
            out.append((cur_t, text))
        seen_last = text
    return out


def fmt(sec):
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--minutes", type=int, default=15)
    a = ap.parse_args()
    src, dst = pathlib.Path(a.src), pathlib.Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    win = a.minutes * 60
    for vtt in sorted(src.glob("*.vtt")):
        lines = parse_vtt(vtt)
        if not lines:
            continue
        stem = vtt.name.split(".")[0]
        part, buf, start = 1, [], 0
        for t, text in lines:
            if t - start >= win and buf:
                (dst / f"{stem}__part{part:02d}.md").write_text(
                    f"# {stem} — part {part} ({fmt(start)}–{fmt(t)})\n\n" + "\n".join(buf) + "\n", encoding="utf-8")
                part, buf, start = part + 1, [], t
            buf.append(f"[{fmt(t)}] {text}")
        if buf:
            (dst / f"{stem}__part{part:02d}.md").write_text(
                f"# {stem} — part {part} (from {fmt(start)})\n\n" + "\n".join(buf) + "\n", encoding="utf-8")
        print(f"{vtt.name}: {len(lines)} satır -> {part} parça")


if __name__ == "__main__":
    main()
