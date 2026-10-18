"""Foundry's pixel art: an anvil with a glowing ingot and sparks, and a pixel-font banner.

    python tools/make_art.py assets      # writes icon.svg and banner.svg
    rsvg-convert -w 256 assets/icon.svg -o assets/icon-256.png   (etc.)

Same family as Pascaline: flat pop colours, black outlines, a hard drop shadow, drawn on
a pixel grid with no fonts (the 5 × 7 letters are below).
"""

import sys
from pathlib import Path

INK = "#141414"
CYAN = "#2EC4F1"
STEEL = "#8FA3BF"
STEEL_LIGHT = "#D7E0EC"
STEEL_DARK = "#5E7290"
ORANGE = "#FF7A1A"
HOT = "#FFD23F"
PINK = "#FF4F8B"
CREAM = "#FFF6E3"

N = 32


def grid():
    return [[None] * N for _ in range(N)]


def anvil_mask():
    """Side view of an anvil: horn to the left, heel to the right, waist and feet."""
    m = set()

    def span(y, x0, x1):
        m.update((x, y) for x in range(x0, x1 + 1))

    span(15, 3, 26)  # face, with the horn growing out of it
    span(16, 5, 26)
    span(17, 8, 26)
    span(18, 11, 25)
    for y in (19, 20, 21):  # waist
        span(y, 13, 21)
    span(22, 11, 23)  # base
    span(23, 9, 25)
    span(24, 8, 26)  # feet
    return m


def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


SPARKS = [(10, 6), (16, 4), (22, 6)]  # small yellow crosses over the hot metal


def paint_object(g):
    """The anvil with a glowing ingot: one ink outline and a hard 2-px drop shadow round
    the whole shape, then flat colours, then the sparks."""
    anvil, ingot = anvil_mask(), rect(12, 11, 20, 14)
    layers = [
        (anvil, STEEL),
        ({p for p in anvil if p[1] == 15}, STEEL_LIGHT),  # lit top of the face and horn
        ({p for p in anvil if p[1] == 24}, STEEL_DARK),  # the feet in shadow
        (ingot, ORANGE),
        (rect(13, 11, 19, 11), HOT),  # white-hot top
    ]
    body = anvil | ingot
    outline = {(x + a, y + b) for x, y in body for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    outline -= body

    def put(x, y, c):
        if 0 <= x < N and 0 <= y < N:
            g[y][x] = c

    for x, y in outline | body:
        put(x + 2, y + 2, INK)
    for x, y in outline:
        put(x, y, INK)
    for mask, colour in layers:
        for x, y in mask:
            put(x, y, colour)
    for x, y in SPARKS:
        for a, b in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            put(x + a, y + b, HOT)


def paint_icon():
    """The icon: the anvil on a cyan tile with rounded corners."""
    g = grid()
    for y in range(1, 31):
        for x in range(1, 31):
            if (x in (1, 30)) and (y in (1, 30)):
                continue
            g[y][x] = CYAN
    paint_object(g)
    return g


# A 5 × 7 pixel font.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "·": ["00000", "00000", "00000", "00100", "00000", "00000", "00000"],
    " ": ["00000"] * 7,
}


def rects(cells, scale, x0=0, y0=0):
    """Pixels as SVG rects, merging horizontal runs of one colour."""
    out = []
    for y, row in enumerate(cells):
        x = 0
        while x < len(row):
            c = row[x]
            run = 1
            while x + run < len(row) and row[x + run] == c:
                run += 1
            if c:
                out.append(f'<rect x="{x0 + x * scale}" y="{y0 + y * scale}" '
                           f'width="{run * scale}" height="{scale}" fill="{c}"/>')
            x += run
    return "\n  ".join(out)


def text_cells(text, color):
    rows = [[] for _ in range(7)]
    for k, ch in enumerate(text):
        for y in range(7):
            if k:
                rows[y].append(None)  # one pixel between letters
            rows[y].extend(color if b == "1" else None for b in FONT[ch][y])
    return rows


def svg(w, h, body, bg=None):
    back = f'<rect width="{w}" height="{h}" fill="{bg}"/>\n  ' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" shape-rendering="crispEdges">\n  {back}{body}\n</svg>\n')


def icon():
    return svg(N, N, rects(paint_icon(), 1))


def banner():
    """The anvil on the left, wordmark and tagline on the right, centred as a group."""
    art = grid()
    paint_object(art)
    pts = [(x, y) for y, row in enumerate(art) for x, c in enumerate(row) if c]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    crop = [row[x0:x1 + 1] for row in art[y0:y1 + 1]]
    w, h, s = 1280, 320, 7
    mw, mh = (x1 - x0 + 1) * s, (y1 - y0 + 1) * s
    ts, gs, gap = 13, 4, 64  # title and tagline pixel sizes, gap after the anvil
    title, tag = "FOUNDRY", "DESCRIBE · PROVE · BUILD"
    tw = (len(title) * 6 - 1) * ts
    left = (w - (mw + gap + tw)) // 2
    tx, ty = left + mw + gap, (h - (7 * ts + 34 + 7 * gs)) // 2
    body = "\n  ".join([
        rects(crop, s, left, (h - mh) // 2),
        rects(text_cells(title, INK), ts, tx + ts // 2, ty + ts // 2),  # pop shadow
        rects(text_cells(title, ORANGE), ts, tx, ty),
        rects(text_cells(tag, INK), gs, tx + 2, ty + 7 * ts + 34),
    ])
    return svg(w, h, body, bg=CYAN)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "assets")
    out.mkdir(parents=True, exist_ok=True)
    (out / "icon.svg").write_text(icon())
    (out / "banner.svg").write_text(banner())
    print("ok")
