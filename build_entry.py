#!/usr/bin/env python3
"""Render the one-image front page for Saturday 21 November 2026.

Everything is drawn in 1024-px page coordinates and rendered at 2x, then
downsampled to exactly 1024x1024. No randomness, no timestamps: two runs
produce identical bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
W = H = 1024
S = 2  # supersampling factor

NOTO = "/usr/share/fonts/truetype/noto/"
DEJAVU = "/usr/share/fonts/truetype/dejavu/"


def _font_path(name, fallback):
    p = NOTO + name
    if os.path.exists(p):
        return p
    return DEJAVU + fallback


F = {
    "serif_black": _font_path("NotoSerif-Black.ttf", "DejaVuSerif-Bold.ttf"),
    "serif_bold": _font_path("NotoSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"),
    "serif_cbold": _font_path("NotoSerif-CondensedBold.ttf", "DejaVuSerifCondensed-Bold.ttf"),
    "serif_it": _font_path("NotoSerif-Italic.ttf", "DejaVuSerif-Italic.ttf"),
    "sans": _font_path("NotoSans-Regular.ttf", "DejaVuSans.ttf"),
    "sans_bold": _font_path("NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
    "sans_black": _font_path("NotoSans-Black.ttf", "DejaVuSans-Bold.ttf"),
    "sans_c": _font_path("NotoSans-Condensed.ttf", "DejaVuSansCondensed.ttf"),
    "sans_cm": _font_path("NotoSans-CondensedMedium.ttf", "DejaVuSansCondensed.ttf"),
    "sans_csb": _font_path("NotoSans-CondensedSemiBold.ttf", "DejaVuSansCondensed-Bold.ttf"),
    "sans_cb": _font_path("NotoSans-CondensedBold.ttf", "DejaVuSansCondensed-Bold.ttf"),
}
_cache = {}


def font(key, size):
    k = (key, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(F[key], int(round(size * S)))
    return _cache[k]


# ---------------------------------------------------------------- palette
PAPER = (244, 237, 222)
PAPER2 = (236, 227, 207)
INK = (28, 26, 24)
INK2 = (78, 72, 64)
RULE = (150, 140, 124)
RED = (178, 34, 34)
SEA = (196, 214, 222)
LAND = (222, 205, 168)
LAND2 = (205, 186, 148)

REGION = {
    "Europe": (44, 92, 160),
    "Middle East": (190, 64, 40),
    "Americas": (46, 128, 72),
    "East Asia": (118, 70, 150),
    "Global": (24, 128, 128),
    "Africa": (196, 140, 30),
    "SE Asia": (176, 52, 110),
    "Oceania": (40, 150, 190),
    "South Asia": (128, 84, 52),
}
REGION_COUNTS = [("Europe", 9), ("Middle East", 5), ("Americas", 5), ("East Asia", 5),
                 ("Global", 4), ("Africa", 3), ("SE Asia", 3), ("Oceania", 3), ("South Asia", 2)]
BADGE = {"C": ((40, 120, 60), "CONFIRMED"), "O": ((40, 80, 150), "OFFICIAL"), "R": ((190, 120, 20), "REPORTED")}

img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)


# ---------------------------------------------------------------- helpers
def P(v):
    return int(round(v * S))


def rect(x0, y0, x1, y1, fill=None, outline=None, width=1, r=0):
    box = [P(x0), P(y0), P(x1), P(y1)]
    if r:
        d.rounded_rectangle(box, radius=P(r), fill=fill, outline=outline, width=P(width) if outline else 0)
    else:
        d.rectangle(box, fill=fill, outline=outline, width=P(width) if outline else 0)


def line(pts, fill=INK, width=1):
    d.line([(P(x), P(y)) for x, y in pts], fill=fill, width=max(1, P(width)))


def poly(pts, fill=None, outline=None):
    d.polygon([(P(x), P(y)) for x, y in pts], fill=fill, outline=outline)


def ellipse(x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.ellipse([P(x0), P(y0), P(x1), P(y1)], fill=fill, outline=outline, width=P(width) if outline else 0)


def circle(cx, cy, r, fill=None, outline=None, width=1):
    ellipse(cx - r, cy - r, cx + r, cy + r, fill, outline, width)


def tw(text, f):
    return d.textlength(text, font=f) / S


def text(x, y, s, f, fill=INK, anchor="la"):
    d.text((P(x), P(y)), s, font=f, fill=fill, anchor=anchor)


def wrap(s, f, width, max_lines, tag=""):
    words = s.split(" ")
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(t, f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        raise SystemExit(f"text too long ({len(lines)}>{max_lines} lines) [{tag}]: {s}")
    return lines


def para(x, y, s, f, width, max_lines, lh, fill=INK, tag=""):
    for i, ln in enumerate(wrap(s, f, width, max_lines, tag)):
        text(x, y + i * lh, ln, f, fill)
    return y + len(wrap(s, f, width, max_lines, tag)) * lh


def pin(cx, cy, n, color, r=7.5, size=10):
    circle(cx, cy, r, fill=color, outline=PAPER, width=1)
    text(cx, cy + 0.5, str(n), font("sans_cb", size), (255, 255, 255), anchor="mm")


def badge(x, y, code, full=True, size=10):
    col, word = BADGE[code]
    label = word if full else code
    f = font("sans_cb", size)
    wdt = tw(label, f) + 8
    rect(x, y, x + wdt, y + size + 4, fill=col, r=2.5)
    text(x + wdt / 2, y + (size + 4) / 2 + 0.5, label, f, (255, 255, 255), anchor="mm")
    return x + wdt


def hrule(y, x0=10, x1=W - 10, width=1, fill=INK):
    line([(x0, y), (x1, y)], fill, width)


def section_label(x, y, s, color=RED):
    f = font("sans_cb", 10.5)
    text(x, y, s, f, color)
    return tw(s, f)


# ================================================================ STRIP
rect(0, 0, W, 22, fill=INK)
text(W / 2, 11.5, "THE WORLD IN ONE DAY  ·  39 STORIES  ·  9 REGIONS  ·  ALL DATED 21 NOV 2026",
     font("sans_cb", 11.5), PAPER, anchor="mm")

# ================================================================ MASTHEAD
MAST = "Saturday 21 November 2026"
size = 40
while tw(MAST, font("serif_black", size + 1)) <= W - 24:
    size += 1
mf = font("serif_black", size)
bb = d.textbbox((0, 0), MAST, font=mf, anchor="ls")
asc = -bb[1] / S
base = 28 + asc
text(W / 2, base, MAST, mf, INK, anchor="ms")
y = base + 10
hrule(y, width=2.5)
hrule(y + 4, width=0.8)

# ================================================================ DAY IN ONE LINE
y0 = y + 9
rect(10, y0, W - 10, y0 + 34, fill=PAPER2, outline=INK, width=1)
rect(10, y0, 120, y0 + 34, fill=RED)
text(65, y0 + 10, "THE DAY", font("sans_cb", 11.5), (255, 255, 255), anchor="mm")
text(65, y0 + 24, "IN ONE LINE", font("sans_cb", 11.5), (255, 255, 255), anchor="mm")
ONE = ("War reaches the Gulf and the Baltic, COP31 overruns, two big quakes strike, "
       "England rout the All Blacks and BepiColombo reaches Mercury.")
para(128, y0 + 1.5, ONE, font("serif_bold", 13.5), W - 10 - 134, 2, 15.5, INK, "oneline")
y = y0 + 34

# ================================================================ TIMELINE
TL_TOP = y + 4
section_label(10, TL_TOP + 15, "UTC")
tx0, tx1 = 44, W - 14
tly = TL_TOP + 22


def tx(h):
    return tx0 + (tx1 - tx0) * h / 24.0


line([(tx0, tly), (tx1, tly)], INK, 1.6)
for h in range(0, 25, 3):
    line([(tx(h), tly - 3), (tx(h), tly + 3)], INK, 1)
    text(tx(h), tly + 4, f"{h:02d}:00", font("sans_c", 9.5) if False else font("sans_c", 10), INK2, anchor="ma")
# (hour, number, label, region, row: -1 above, +1 below)
TIMELINE = [
    (0.15, 4, "00:09 Peru quake", "Americas", -1),
    (3.0, 5, "~03:00 Basra fire", "Middle East", -1),
    (4.22, 11, "04:13 BTC $55.8k", "Global", 1),
    (7.0, 2, "~07:00 drones hit Sparta II", "Europe", -1),
    (8.25, 38, "08:15 MCG T20", "Oceania", 1),
    (9.7, 35, "09:42 Banda Sea M6.8", "SE Asia", -1),
    (10.0, 6, "~10:00 Java fire", "SE Asia", 1),
    (14.17, 9, "14:10 Eng v NZ", "Europe", -1),
    (18.4, 10, "18:24 BepiColombo", "Global", -1),
    (19.05, 23, "19:03 Bolsonaro ICU", "Americas", 1),
    (21.0, 1, "late Sat: Bahrain attack", "Middle East", -1),
]
lf = font("sans_csb", 10)
last_end = {-1: 0, 1: 0}
for h, n, lab, reg, row in TIMELINE:
    x = tx(h)
    col = REGION[reg]
    circle(x, tly, 3.2, fill=col)
    w_ = tw(lab, lf) + 15
    lx = max(x - 6, last_end[row] + 4)
    lx = min(lx, tx1 - w_)
    ly = tly - 17 if row < 0 else tly + 25
    line([(x, tly), (lx + 6, ly)], col, 0.9)
    pin(lx + 6, ly, n, col, r=6, size=8.5 if n > 9 else 9)
    text(lx + 14, ly + 0.5, lab, lf, INK, anchor="lm")
    last_end[row] = lx + w_
y = tly + 34

# ================================================================ NUMBERS STRIP
hrule(y, width=1)
NUMS = [
    ("37–12", "England's record win", "over New Zealand"),
    ("M6.8", "Banda Sea quake,", "09:42 UTC"),
    ("98.5%", "of EU–Indonesia", "tariffs scrapped"),
    ("$55.1k", "Bitcoin's low, weakest", "since Sept 2024"),
    ("16", "crew evacuated from", "burning Sparta II"),
    ("82,500", "marched in France", "(ministry count)"),
]
cw = (W - 20) / 6
nf = font("serif_black", 22)
cf = font("sans_c", 10)
for i, (num, c1, c2) in enumerate(NUMS):
    x = 10 + i * cw
    if i:
        line([(x, y + 5), (x, y + 33)], RULE, 0.8)
    nw = tw(num, nf)
    text(x + 6, y + 19, num, nf, RED, anchor="lm")
    text(x + 12 + nw, y + 12, c1, cf, INK2, anchor="lm")
    text(x + 12 + nw, y + 25, c2, cf, INK2, anchor="lm")
y += 37

# ================================================================ REGION BAR
bx = 10
unit = (W - 20) / 39.0
for reg, n in REGION_COUNTS:
    wdt = unit * n
    rect(bx, y, bx + wdt, y + 16, fill=REGION[reg])
    lab = f"{reg.upper()} {n}"
    f = font("sans_cb", 10)
    if tw(lab, f) > wdt - 4:
        lab = {"SOUTH ASIA": "S.ASIA", "MIDDLE EAST": "MIDEAST"}.get(reg.upper(), reg.upper()) + f" {n}"
    text(bx + wdt / 2, y + 8.5, lab, f, (255, 255, 255), anchor="mm")
    bx += wdt
y += 16
hrule(y + 3, width=1)

# ================================================================ LEADS
LEAD_TOP = y + 8
LW = (W - 20 - 14) / 3.0
ILL_H = 120


def ill_gulf(x0, y0, w, h):
    rect(x0, y0, x0 + w, y0 + h, fill=SEA)
    # Iran coast (top / right)
    poly([(x0, y0), (x0 + w, y0), (x0 + w, y0 + 70), (x0 + w - 30, y0 + 62), (x0 + 250, y0 + 48),
          (x0 + 205, y0 + 40), (x0 + 150, y0 + 22), (x0 + 90, y0 + 14), (x0 + 30, y0 + 10), (x0, y0 + 12)], fill=LAND2)
    # Arabia (bottom / left), Qatar bump, Musandam horn
    poly([(x0, y0 + h), (x0, y0 + 64), (x0 + 40, y0 + 70), (x0 + 62, y0 + 92), (x0 + 74, y0 + 76),
          (x0 + 90, y0 + 82), (x0 + 120, y0 + 100), (x0 + 170, y0 + 98), (x0 + 205, y0 + 86),
          (x0 + 238, y0 + 66), (x0 + 248, y0 + 60), (x0 + 252, y0 + 74), (x0 + 270, y0 + 96),
          (x0 + w, y0 + 106), (x0 + w, y0 + h)], fill=LAND)
    # Bahrain island + fires and smoke
    bxx, byy = x0 + 70, y0 + 60
    ellipse(bxx - 6, byy - 9, bxx + 6, byy + 9, fill=LAND, outline=INK2, width=0.8)
    for k, (dx, dy, rr) in enumerate([(4, -16, 9), (12, -27, 11), (22, -38, 13), (34, -46, 11)]):
        circle(bxx + dx, byy + dy, rr, fill=(120, 116, 110) if k % 2 else (98, 94, 90))
    for dx in (-3, 3):
        poly([(bxx + dx - 4, byy + 2), (bxx + dx, byy - 12), (bxx + dx + 4, byy + 2)], fill=(232, 96, 30))
        poly([(bxx + dx - 2, byy + 2), (bxx + dx, byy - 6), (bxx + dx + 2, byy + 2)], fill=(250, 200, 60))
    # two tankers near Khasab / Hormuz
    for tx_, ty_ in ((x0 + 262, y0 + 52), (x0 + 288, y0 + 80)):
        poly([(tx_ - 18, ty_), (tx_ + 16, ty_), (tx_ + 20, ty_ - 5), (tx_ - 20, ty_ - 5)], fill=(60, 60, 70))
        rect(tx_ + 8, ty_ - 10, tx_ + 14, ty_ - 5, fill=(230, 230, 230))
        poly([(tx_ - 6, ty_ - 5), (tx_ - 2, ty_ - 17), (tx_ + 2, ty_ - 5)], fill=(232, 96, 30))
        circle(tx_ - 1, ty_ - 22, 5, fill=(110, 106, 100))
    f = font("sans_cb", 10)
    text(x0 + 150, y0 + 16, "IRAN", f, INK2, anchor="mm")
    text(x0 + 96, y0 + 72, "BAHRAIN · SITRA", f, INK, anchor="lm")
    text(x0 + 110, y0 + h - 9, "SAUDI ARABIA / UAE", f, INK2, anchor="mm")
    text(x0 + w - 4, y0 + h - 9, "2 TANKERS HIT", f, RED, anchor="rm")
    text(x0 + 200, y0 + 56, "GULF", font("serif_it", 11), (70, 100, 120), anchor="mm")


def drone(cx, cy, s=1.0):
    line([(cx - 9 * s, cy - 5 * s), (cx + 9 * s, cy + 5 * s)], INK, 2)
    line([(cx - 9 * s, cy + 5 * s), (cx + 9 * s, cy - 5 * s)], INK, 2)
    for ex, ey in ((-9, -5), (9, 5), (-9, 5), (9, -5)):
        ellipse(cx + ex * s - 5, cy + ey * s - 1.5, cx + ex * s + 5, cy + ey * s + 1.5, fill=INK2)
    circle(cx, cy, 3, fill=INK)


def ill_ship(x0, y0, w, h):
    rect(x0, y0, x0 + w, y0 + h, fill=(214, 222, 228))
    rect(x0, y0 + 88, x0 + w, y0 + h, fill=(120, 150, 172))
    for k in range(5):
        line([(x0 + 10 + k * 66, y0 + 100 + (k % 2) * 10), (x0 + 40 + k * 66, y0 + 100 + (k % 2) * 10)], (170, 196, 214), 1.2)
    # Finnish coast
    poly([(x0, y0 + 88), (x0, y0 + 74), (x0 + 30, y0 + 70), (x0 + 60, y0 + 78), (x0 + 74, y0 + 88)], fill=(120, 140, 110))
    text(x0 + 6, y0 + 64, "FINLAND", font("sans_cb", 10), INK2, anchor="lm")
    # smoke plume drifting
    for k in range(7):
        circle(x0 + 180 + k * 16, y0 + 50 - k * 6, 12 + k * 2, fill=(90 + k * 8, 88 + k * 8, 86 + k * 8))
    # cargo ship
    sx, sy = x0 + 120, y0 + 92
    poly([(sx, sy - 16), (sx + 150, sy - 16), (sx + 140, sy), (sx + 10, sy)], fill=(70, 40, 36))
    rect(sx + 116, sy - 34, sx + 140, sy - 16, fill=(236, 236, 230))
    rect(sx + 122, sy - 42, sx + 128, sy - 34, fill=INK)
    for k in range(4):
        rect(sx + 18 + k * 24, sy - 26, sx + 38 + k * 24, sy - 16, fill=(150, 70, 50) if k % 2 else (60, 90, 120))
    # fire
    for fx, fh in ((sx + 60, 30), (sx + 80, 40), (sx + 98, 28)):
        poly([(fx - 9, sy - 16), (fx, sy - 16 - fh), (fx + 9, sy - 16)], fill=(232, 96, 30))
        poly([(fx - 4, sy - 16), (fx, sy - 16 - fh * 0.55), (fx + 4, sy - 16)], fill=(250, 200, 60))
    text(sx + 75, sy - 4, "SPARTA II", font("sans_cb", 10), (240, 230, 220), anchor="mm")
    drone(x0 + 48, y0 + 22)
    drone(x0 + 92, y0 + 38, 0.85)
    line([(x0 + 100, y0 + 44), (sx + 60, sy - 40)], RED, 1)
    text(x0 + w - 4, y0 + h - 9, "16 CREW SAFE", font("sans_cb", 10), (255, 255, 255), anchor="rm")
    text(x0 + 6, y0 + h - 9, "GULF OF FINLAND", font("sans_cb", 10), (230, 238, 244), anchor="lm")


def ill_cop(x0, y0, w, h):
    rect(x0, y0, x0 + w, y0 + h, fill=(222, 232, 218))
    # globe
    gx, gy, gr = x0 + 62, y0 + 56, 44
    circle(gx, gy, gr, fill=(150, 196, 214), outline=INK2, width=1.2)
    poly([(gx - 30, gy - 30), (gx - 6, gy - 38), (gx + 6, gy - 20), (gx - 10, gy - 4), (gx - 30, gy - 8)], fill=(110, 160, 90))
    poly([(gx + 6, gy + 2), (gx + 30, gy - 6), (gx + 36, gy + 20), (gx + 16, gy + 38), (gx + 4, gy + 22)], fill=(110, 160, 90))
    ellipse(gx - gr, gy - 14, gx + gr, gy + 14, outline=(90, 130, 150), width=0.8)
    ellipse(gx - 18, gy - gr, gx + 18, gy + gr, outline=(90, 130, 150), width=0.8)
    # thermometer
    rect(gx + 46, gy - 40, gx + 54, gy + 28, fill=(255, 255, 255), outline=INK2, width=1, r=4)
    circle(gx + 50, gy + 32, 7, fill=RED)
    rect(gx + 48, gy - 18, gx + 52, gy + 30, fill=RED)
    # draft document
    dx, dy = x0 + 132, y0 + 14
    rect(dx, dy, dx + 82, dy + 104, fill=(255, 253, 246), outline=INK2, width=1)
    text(dx + 41, dy + 12, "DRAFT", font("sans_cb", 11), RED, anchor="mm")
    for k in range(7):
        line([(dx + 10, dy + 28 + k * 10), (dx + 72 - (k % 3) * 12, dy + 28 + k * 10)], (150, 145, 135), 1.4)
    line([(dx + 10, dy + 54), (dx + 70, dy + 54)], RED, 1)  # struck-out text
    # clock past deadline
    cx, cy, cr = x0 + 268, y0 + 56, 38
    circle(cx, cy, cr, fill=(255, 253, 246), outline=INK, width=2)
    for k in range(12):
        import math
        a = math.radians(k * 30)
        line([(cx + math.sin(a) * (cr - 6), cy - math.cos(a) * (cr - 6)),
              (cx + math.sin(a) * (cr - 2), cy - math.cos(a) * (cr - 2))], INK, 1.2)
    d.pieslice([P(cx - cr + 3), P(cy - cr + 3), P(cx + cr - 3), P(cy + cr - 3)], start=-90, end=-20, fill=(240, 170, 160))
    line([(cx, cy), (cx + 20, cy - 8)], INK, 2.4)   # hour hand past 12
    line([(cx, cy), (cx + 9, cy - 30)], INK, 1.6)
    circle(cx, cy, 2.5, fill=INK)
    rect(cx - 36, cy + 44, cx + 36, cy + 60, fill=RED, r=3)
    text(cx, cy + 52.5, "OVERTIME", font("sans_cb", 10.5), (255, 255, 255), anchor="mm")
    text(gx, y0 + h - 9, "ANTALYA", font("sans_cb", 10), INK2, anchor="mm")


LEADS = [
    (1, "Middle East · Gulf", ill_gulf,
     "Iran strikes Bahrain; two tankers hit off Oman",
     "Bahrain says an Iranian attack set an industrial site on Sitra ablaze, no casualties. "
     "IRGC claims hits on US positions; UKMTO reports two tankers struck near Khasab. "
     "Bahrain asks the UN Security Council to act.",
     "C", "Al Jazeera · Reuters · AFP · IRNA · UKMTO"),
    (2, "Europe · Baltic", ill_ship,
     "Drones set Russian ship ablaze in Gulf of Finland",
     "Two drones hit Sparta II, a US-sanctioned cargo ship bound for Kaliningrad. It burned and "
     "drifted into Finnish waters; all 16 crew got off. Finland says Ukraine likely behind it; "
     "Stubb calls it \u201cserious\u201d.",
     "C", "Reuters · AP · CNN · Yle"),
    (3, "Global · Climate", ill_cop,
     "COP31 climate talks run into overtime",
     "Talks in Antalya blew past Friday's deadline. EU's Hoekstra: \u201cgood deal or no deal\u201d. "
     "100 civil-society groups sent a letter as a late-night plenary met on Saturday.",
     "C", "Reuters · AP · AFP"),
]
REG_OF_LEAD = {1: "Middle East", 2: "Europe", 3: "Global"}
for i, (n, reg, ill, head, summ, bc, src) in enumerate(LEADS):
    x0 = 10 + i * (LW + 7)
    ill(x0, LEAD_TOP, LW, ILL_H)
    rect(x0, LEAD_TOP, x0 + LW, LEAD_TOP + ILL_H, outline=INK, width=1)
    col = REGION[REG_OF_LEAD[n]]
    pin(x0 + 12, LEAD_TOP + 12, n, col, r=9, size=12)
    yy = LEAD_TOP + ILL_H + 6
    text(x0, yy, reg.upper(), font("sans_cb", 10.5), col)
    yy += 14
    yy = para(x0, yy, head, font("serif_black", 17.5), LW, 2, 21, INK, f"lead{n}")
    yy += 3
    yy = para(x0, yy, summ, font("sans_c", 11), LW, 3, 13.6, INK, f"leadsum{n}")
    yy += 3
    ex = badge(x0, yy, bc)
    text(ex + 5, yy + 7, src, font("sans_c", 10), INK2, anchor="lm")
LEAD_BOTTOM = LEAD_TOP + ILL_H + 6 + 14 + 42 + 3 + 3 * 13.6 + 3 + 14
for i in (1, 2):
    x = 10 + i * (LW + 7) - 3.5
    line([(x, LEAD_TOP), (x, LEAD_BOTTOM)], RULE, 0.8)
y = LEAD_BOTTOM + 5
hrule(y, width=1.6)


# ================================================================ TILE ICONS
def icon(kind, x, y, s=26, col=INK):
    import math
    cx, cy = x + s / 2, y + s / 2
    if kind == "quake":
        pts = [(x, cy), (x + 5, cy), (x + 8, cy - 9), (x + 12, cy + 10), (x + 16, cy - 12), (x + 19, cy + 6), (x + 22, cy), (x + s, cy)]
        line(pts, col, 2)
    elif kind == "fire":
        poly([(cx - 9, y + s), (cx - 10, cy), (cx - 3, y + 4), (cx, cy - 3), (cx + 5, y), (cx + 10, cy + 2), (cx + 9, y + s)], fill=(222, 90, 30))
        poly([(cx - 4, y + s), (cx - 4, cy + 5), (cx + 1, cy - 2), (cx + 4, cy + 6), (cx + 4, y + s)], fill=(250, 196, 60))
    elif kind == "cuffs":
        circle(cx - 6, cy, 6.5, outline=col, width=2.4)
        circle(cx + 6, cy, 6.5, outline=col, width=2.4)
    elif kind == "flag":
        line([(x + 3, y + 1), (x + 3, y + s)], col, 2)
        for r_ in range(3):
            for c_ in range(4):
                if (r_ + c_) % 2 == 0:
                    rect(x + 4 + c_ * 5, y + 2 + r_ * 5, x + 9 + c_ * 5, y + 7 + r_ * 5, fill=col)
        rect(x + 4, y + 2, x + 24, y + 17, outline=col, width=1)
    elif kind == "rugby":
        ellipse(x + 1, y + 6, x + s - 1, y + s - 6, fill=(150, 90, 50), outline=col, width=1.2)
        line([(x + 8, cy), (x + s - 8, cy)], (255, 255, 255), 1.4)
        for k in range(3):
            line([(x + 10 + k * 3, cy - 3), (x + 10 + k * 3, cy + 3)], (255, 255, 255), 1.2)
    elif kind == "planet":
        circle(cx, cy, 7, fill=(150, 140, 130))
        ellipse(x, cy - 5, x + s, cy + 5, outline=col, width=1.4)
        circle(x + s - 3, cy - 1, 2.4, fill=RED)
    elif kind == "btc":
        circle(cx, cy, 12, fill=(232, 150, 40))
        text(cx, cy + 1, "B", font("sans_black", 15), (255, 255, 255), anchor="mm")
        line([(cx - 2, cy - 11), (cx - 2, cy + 11)], (255, 255, 255), 1.2)
        line([(cx + 2, cy - 11), (cx + 2, cy + 11)], (255, 255, 255), 1.2)
    elif kind == "trade":
        rect(x, y + 5, x + 12, y + 21, fill=(40, 70, 150))
        rect(x + 14, y + 5, x + 26, y + 13, fill=(200, 30, 40))
        rect(x + 14, y + 13, x + 26, y + 21, fill=(250, 250, 250), outline=col, width=0.6)
        line([(x + 6, y + 24), (x + 20, y + 24)], col, 1.6)
    elif kind == "placard":
        line([(cx, y + 14), (cx, y + s)], col, 2)
        rect(x + 2, y + 1, x + s - 2, y + 15, fill=(255, 253, 246), outline=col, width=1.6)
        line([(x + 6, y + 6), (x + s - 6, y + 6)], RED, 1.4)
        line([(x + 6, y + 10), (x + s - 9, y + 10)], RED, 1.4)
    elif kind == "robot":
        rect(x + 4, y + 6, x + s - 4, y + s - 2, fill=(130, 140, 150), outline=col, width=1.2, r=3)
        circle(x + 10, y + 14, 2.5, fill=RED)
        circle(x + s - 10, y + 14, 2.5, fill=RED)
        line([(cx, y + 6), (cx, y + 1)], col, 1.4)
        circle(cx, y + 1.5, 1.8, fill=col)
        line([(x + 9, y + 20), (x + s - 9, y + 20)], col, 1.4)
    elif kind == "missile":
        poly([(x + 2, y + s - 2), (x + s - 6, y + 6), (x + s - 2, y + 2), (x + s - 6, y + 10)], fill=col)
        line([(x + 2, y + s - 2), (x + s - 4, y + 4)], col, 3)
        circle(x + s - 6, y + 6, 6, outline=RED, width=1.6)
        line([(x + s - 13, y + 6), (x + s + 1, y + 6)], RED, 1)
        line([(x + s - 6, y - 1), (x + s - 6, y + 13)], RED, 1)


TILES = [
    (4, "Americas", "quake", "M6.7", "Deep quake shakes Peru", "Junín, 00:09 UTC, 108–129 km deep; felt in Lima, minor damage", "C", "USGS·IGP"),
    (5, "Middle East", "fire", "4 dead", "Basra power-plant fire", "Pipeline blaze at Hartha station; 30+ hurt, PM orders probe", "O", "Reuters·INA"),
    (6, "SE Asia", "fire", "3 dead", "Java candy-factory fire", "Cikande, Serang, ~17:00 local; dozens still missing", "C", "Reuters·Antara"),
    (7, "Americas", "cuffs", "$5m", "Sinaloa kingpin captured", "\u201cEl Chapo Isidro\u201d held; 11 dead in Guasave raid", "C", "Reuters·AP"),
    (8, "Americas", "flag", "75th", "Verstappen wins in Las Vegas", "From pole, 0.639s ahead of Norris; Piastri 3rd", "C", "Reuters·F1"),
    (9, "Europe", "rugby", "37–12", "England rout the All Blacks", "Record margin over NZ at Twickenham, five tries", "C", "Reuters·BBC"),
    (10, "Global", "planet", "18:24", "BepiColombo reaches Mercury", "ESA/JAXA orbit burn done after an 8-year cruise", "O", "ESA·Nature"),
    (11, "Global", "btc", "$55.1k", "Bitcoin hits lowest since 2024", "Lowest since Sept 2024; ~$2.4bn liquidated", "R", "Reuters·CoinGecko"),
    (12, "Europe", "trade", "98.5%", "EU and Indonesia sign trade pact", "Tariffs scrapped after 10 years of talks; ~€650m a year", "O", "EU Commission"),
    (13, "Europe", "placard", "82,500", "France marches a 6th Saturday", "Cost-of-living protests (ministry); 144 detained", "C", "Reuters·AFP"),
    (14, "Global", "robot", "128", "No binding killer-robot rules", "States agree only to \u201celaborate\u201d rules by 2028", "C", "Reuters·AP"),
    (15, "Middle East", "missile", "3", "Houthi missiles over Riyadh", "All three intercepted, no injuries", "O", "Reuters·AFP"),
]
TILE_TOP = y + 6
TW_ = (W - 20 - 5 * 6) / 6.0
TH = 122
for i, (n, reg, ic, num, head, one, bc, src) in enumerate(TILES):
    r_, c_ = divmod(i, 6)
    x0 = 10 + c_ * (TW_ + 6)
    y0 = TILE_TOP + r_ * (TH + 6)
    col = REGION[reg]
    rect(x0, y0, x0 + TW_, y0 + TH, fill=PAPER2, outline=RULE, width=0.8)
    rect(x0, y0, x0 + TW_, y0 + 3, fill=col)
    icon(ic, x0 + 6, y0 + 9, 26)
    nf_ = font("serif_black", 21)
    while tw(num, nf_) > TW_ - 40 - 22:
        nf_ = font("serif_black", nf_.size / S - 1)
    text(x0 + 38, y0 + 22, num, nf_, RED, anchor="lm")
    pin(x0 + TW_ - 11, y0 + 14, n, col, r=8, size=9.5)
    yy = y0 + 39
    yy = para(x0 + 6, yy, head, font("serif_cbold", 12.5), TW_ - 10, 2, 15, INK, f"tile{n}")
    yy = max(yy, y0 + 39 + 15) + 2
    para(x0 + 6, yy, one, font("sans_c", 10), TW_ - 10, 2, 12.2, INK2, f"tileone{n}")
    ex = badge(x0 + 6, y0 + TH - 17, bc, full=False, size=9.5)
    text(ex + 4, y0 + TH - 10, src, font("sans_c", 10), INK2, anchor="lm")
y = TILE_TOP + 2 * TH + 6 + 6
hrule(y, width=1.6)

# ================================================================ WORLD MAP
MAP_TOP = y + 18
wl = section_label(10, y + 4, "WHERE IT HAPPENED")
text(16 + wl, y + 4, "off-map: 10 Mercury, 11 Bitcoin", font("sans_c", 10), INK2)
MX0, MX1 = 10, 330
MY0, MY1 = MAP_TOP, MAP_TOP + 136
LON0, LON1, LAT0, LAT1 = -130.0, 160.0, 72.0, -48.0


def mp(lon, lat):
    return (MX0 + (lon - LON0) / (LON1 - LON0) * (MX1 - MX0),
            MY0 + (lat - LAT0) / (LAT1 - LAT0) * (MY1 - MY0))


rect(MX0, MY0, MX1, MY1, fill=SEA)
CONTINENTS = [
    # North America
    [(-130, 58), (-125, 70), (-95, 72), (-80, 68), (-62, 58), (-55, 50), (-66, 44), (-76, 35), (-81, 25),
     (-90, 29), (-97, 26), (-97, 19), (-88, 16), (-83, 9), (-79, 8), (-86, 13), (-105, 20), (-112, 30),
     (-118, 34), (-124, 42), (-125, 50)],
    # Greenland
    [(-55, 72), (-22, 72), (-20, 70), (-40, 62), (-50, 64), (-55, 70)],
    # South America
    [(-79, 8), (-62, 11), (-50, 2), (-35, -6), (-39, -15), (-48, -26), (-58, -36), (-66, -46), (-70, -48),
     (-74, -42), (-72, -30), (-70, -18), (-76, -12), (-81, -4)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (2, 51), (8, 54), (10, 58), (5, 62), (14, 68), (26, 71), (42, 68),
     (40, 60), (30, 60), (24, 58), (22, 55), (28, 46), (28, 41), (24, 38), (20, 40), (16, 38), (12, 44),
     (8, 44), (3, 43), (-2, 37)],
    # UK + Ireland
    [(-5, 50), (1, 51), (0, 53), (-3, 58), (-6, 57), (-5, 54)],
    [(-10, 52), (-6, 52), (-6, 55), (-9, 54)],
    # Africa
    [(-17, 21), (-10, 30), (-6, 36), (10, 37), (20, 32), (32, 31), (34, 28), (43, 12), (51, 12), (40, -3),
     (40, -15), (35, -24), (27, -34), (18, -34), (12, -18), (13, -6), (9, 4), (-8, 4), (-17, 13)],
    # Arabia + Middle East
    [(34, 28), (36, 36), (44, 37), (48, 30), (51, 26), (56, 26), (57, 22), (59, 22), (52, 16), (44, 12), (42, 16), (38, 22)],
    # Asia
    [(42, 68), (60, 72), (100, 72), (140, 72), (160, 66), (160, 60), (142, 52), (135, 43), (127, 40), (122, 31),
     (120, 22), (108, 21), (109, 12), (104, 9), (100, 13), (98, 8), (100, 2), (98, 16), (92, 21), (88, 22),
     (80, 15), (77, 8), (73, 20), (67, 25), (57, 26), (52, 28), (48, 30), (44, 37), (36, 36), (28, 41), (30, 46), (40, 48), (40, 60)],
    # Japan
    [(130, 31), (134, 34), (140, 35), (142, 40), (141, 43), (145, 44), (140, 37), (132, 33)],
    # Sumatra, Java, Borneo, New Guinea
    [(95, 5), (106, -6), (104, -6), (96, 2)],
    [(106, -6), (114, -7), (114, -8.5), (106, -7.5)],
    [(109, 1), (117, 7), (119, 0), (116, -4), (110, -3)],
    [(131, -1), (141, -2), (150, -10), (141, -9), (135, -4)],
    # Australia
    [(114, -22), (122, -18), (131, -12), (137, -12), (142, -11), (146, -18), (153, -26), (150, -37), (141, -38),
     (131, -32), (115, -34)],
    # New Zealand
    [(172, -34), (178, -38), (174, -42), (168, -46), (172, -41)],
]
for c in CONTINENTS:
    poly([mp(lo, la) for lo, la in c], fill=LAND)
rect(MX0, MY0, MX1, MY1, outline=INK, width=1)

# brief locations as small dots (number, region, lon, lat)
BRIEF_LOC = [
    (16, "Middle East", 34.45, 31.5), (17, "Middle East", 35.5, 33.9), (18, "Europe", 30.5, 50.4),
    (19, "Europe", 30.5, 50.4), (20, "Europe", -6.3, 53.3), (21, "Europe", 7.7, 45.1), (22, "Europe", -1.5, 52.5),
    (23, "Americas", -47.9, -15.8), (24, "Americas", -77.0, 38.9), (25, "Africa", 6.1, 4.8), (26, "Africa", 7.5, 9.1),
    (27, "Africa", 19.4, -33.6), (28, "South Asia", 93.9, 24.8), (29, "South Asia", 66.8, 29.8),
    (30, "East Asia", 121.5, 25.0), (31, "East Asia", 135.5, 34.7), (32, "East Asia", 140.4, 37.4),
    (33, "East Asia", 116.4, 39.9), (34, "East Asia", 116.4, 39.9), (35, "SE Asia", 127.5, -7.5),
    (36, "SE Asia", 105.8, 21.0), (37, "Oceania", 174.8, -41.3), (38, "Oceania", 144.98, -37.8),
    (39, "Oceania", 151.2, -33.9),
]
for n, reg, lo, la in BRIEF_LOC:
    lo = min(lo, LON1 - 2)
    x, y_ = mp(lo, la)
    circle(x, y_, 2.4, fill=REGION[reg], outline=PAPER, width=0.5)

# lead/tile pins with leader offsets (number, region, lon, lat, dx, dy)
MAP_PINS = [
    (1, "Middle East", 50.6, 26.1, 10, 14), (5, "Middle East", 47.8, 30.5, 14, -6), (15, "Middle East", 46.7, 24.7, -6, 16),
    (3, "Global", 30.7, 36.9, -2, 14), (2, "Europe", 27.0, 60.0, 10, -8), (9, "Europe", -0.3, 51.4, -14, -10),
    (12, "Europe", 4.4, 50.8, 0, -16), (13, "Europe", 2.3, 48.9, -16, 6), (14, "Europe", 6.1, 46.2, 4, 14),
    (4, "Americas", -75.0, -11.5, -12, 4), (7, "Americas", -108.0, 25.5, -6, 14), (8, "Americas", -115.0, 36.0, -2, -14),
    (6, "SE Asia", 106.4, -6.1, -6, 16),
]
for n, reg, lo, la, dx, dy in MAP_PINS:
    x, y_ = mp(lo, la)
    col = REGION[reg]
    line([(x, y_), (x + dx, y_ + dy)], INK, 0.8)
    circle(x, y_, 1.8, fill=INK)
    pin(x + dx, y_ + dy, n, col, r=6.5, size=8.5 if n > 9 else 9)

# ================================================================ DATE CHECK + KEY (under the map)
yy = MY1 + 6
rect(MX0, yy, MX1, 1000 - 2, fill=PAPER2, outline=RULE, width=0.8)
text(MX0 + 5, yy + 3, "DATE CHECK", font("sans_cb", 10.5), RED)
dc = ("Left out as not 21 Nov: Kryvyi Rih strike and Nikkei \u20135% (Fri 20th); the Bayelsa capsize "
      "itself (Fri; only Saturday's toll used); COP31 final text, India's 720/9 and the ATP final (Sun 22nd).")
para(MX0 + 72, yy + 3, dc, font("sans_c", 10), MX1 - MX0 - 78, 4, 12, INK, "datecheck")
ky = yy + 3 + 4 * 12 + 2
kx = MX0 + 5
for code in ("C", "O", "R"):
    kx = badge(kx, ky, code, full=False, size=9.5)
    word = {"C": "confirmed, 2+ outlets", "O": "official source", "R": "reported/claim"}[code]
    text(kx + 3, ky + 6.5, word, font("sans_c", 10), INK2, anchor="lm")
    kx += tw(word, font("sans_c", 10)) + 9

# ================================================================ ALSO ON 21 NOVEMBER
BX0 = 342
section_label(BX0, y + 4, "ALSO ON 21 NOVEMBER  ·  24 BRIEFS")
BRIEFS = [
    (16, "Gaza City: strike on a food vehicle kills 3, health ministry says"),
    (17, "Beirut: Aoun demands Israeli pull-out; strikes hit the south"),
    (18, "Kyiv: UK deal to build Ukrainian strike drones (reported)"),
    (19, "Kyiv: Zelensky agrees to new US-led talks before Christmas"),
    (20, "Rugby: Ireland 20–17 S. Africa; France 45–17 Argentina"),
    (21, "Turin: Alcaraz and Zverev win ATP Finals semi-finals"),
    (22, "Premier League: Chelsea 1–4 Leeds; Newcastle 2–2 Arsenal"),
    (23, "Brasília: ex-president Bolsonaro in ICU, stable"),
    (24, "Washington: Trump says any Iran deal must be \u201cpermanent\u201d"),
    (25, "Bayelsa, Nigeria: funeral-boat capsize toll rises to 24"),
    (26, "Abuja: all 54 CAF members back FIFA's Infantino"),
    (27, "Worcester, S. Africa: gunmen kill 6, wound 3"),
    (28, "Manipur, India: toxic-liquor deaths rise to 16"),
    (29, "Mastung, Pakistan: 15 militants killed, state media says"),
    (30, "Taipei: short-selling curbs after 17.5% weekly TAIEX fall"),
    (31, "Osaka: BTS win MAMA Album of the Year with \u201cArirang\u201d"),
    (32, "Fukushima: heavy snow cuts off 1,000+ villagers"),
    (33, "Beijing: China and Singapore speed up FTA 4.0 talks"),
    (34, "Beijing: planners order faster local project spending"),
    (35, "Banda Sea: M6.8 quake felt in Dili and Darwin, no damage"),
    (36, "Hanoi: official welcome for Azerbaijan's President Aliyev"),
    (37, "Wellington: India 486/4 lead New Zealand by 118"),
    (38, "Melbourne: Australia's record T20I chase beats England"),
    (39, "Sydney: \u201cunanimous support\u201d for Test captain Cummins"),
]
REG_OF_BRIEF = {n: reg for n, reg, _, _ in BRIEF_LOC}
colw = (W - 10 - BX0 - 10) / 2.0
bf = font("sans_c", 10.5)
row_h = (1000 - MAP_TOP - 4) / 12.0
for i, (n, s) in enumerate(BRIEFS):
    c_, r_ = divmod(i, 12)
    x0 = BX0 + c_ * (colw + 10)
    y0 = MAP_TOP + 2 + r_ * row_h
    col = REGION[REG_OF_BRIEF[n]]
    pin(x0 + 7, y0 + row_h / 2, n, col, r=7, size=8.5)
    place, rest = s.split(":", 1)
    pf = font("sans_cb", 10.5)
    wpl = tw(place + ":", pf)
    if wpl + tw(rest, bf) > colw - 18:
        raise SystemExit(f"brief too long: {s}")
    text(x0 + 17, y0 + row_h / 2 + 0.5, place + ":", pf, INK, anchor="lm")
    text(x0 + 17 + wpl, y0 + row_h / 2 + 0.5, rest, bf, INK, anchor="lm")
    if r_ < 11:
        line([(x0 + 17, y0 + row_h), (x0 + colw, y0 + row_h)], (214, 204, 184), 0.6)
line([(BX0 + colw + 5, MAP_TOP), (BX0 + colw + 5, 998)], RULE, 0.8)

# ================================================================ SOURCES FOOTER
hrule(1001, width=1)
text(W / 2, 1012.5, "Sources: Reuters · AP · AFP · BBC · Al Jazeera · UKMTO · Yle · USGS · ESA · European Commission · "
     "Antara · Kyodo · Yonhap · Xinhua · PTI · national agencies  ·  times in UTC", font("sans_c", 10), INK2, anchor="mm")

# ================================================================ SAVE
out = img.resize((W, H), Image.LANCZOS)
out.save(OUT, format="PNG", optimize=True)
if os.path.getsize(OUT) > 750 * 1024:
    q = out.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(OUT, format="PNG", optimize=True)
print(OUT, os.path.getsize(OUT), "bytes", Image.open(OUT).size)
