# Uygulama ikonlarını üretir (bağımlılıksız): python3 scripts/make_icons.py public
import pathlib, struct, sys, zlib

BG = (14, 15, 19)
BACK = (197, 140, 255)   # --arch
FRONT = (124, 156, 255)  # --acc
LINE = (14, 15, 19)

def rrect(x, y, x0, y0, x1, y1, r):
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r

def color(u, v):
    # u, v ∈ [0,1]; içerik ortadaki ~%60'ta -> maskable güvenli alanı içinde
    if rrect(u, v, .27, .33, .73, .79, .06):        # öndeki kart
        if any(rrect(u, v, .34, y, x, y + .045, .022) for x, y in ((.66, .43), (.60, .53), (.52, .63))):
            return LINE
        return FRONT
    if rrect(u, v, .33, .21, .67, .37, .05):        # arkadaki kart (yukarı kaydırılmış)
        return BACK
    return BG

def png(size, path, ss=4):
    rows = []
    n = size * ss
    for py in range(size):
        row = bytearray([0])
        for px in range(size):
            acc = [0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    c = color((px * ss + sx + .5) / n, (py * ss + sy + .5) / n)
                    acc[0] += c[0]; acc[1] += c[1]; acc[2] += c[2]
            row += bytes(a // (ss * ss) for a in acc)
        rows.append(bytes(row))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")
    path.write_bytes(data)

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "public")
for s, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")):
    png(s, out / name)
