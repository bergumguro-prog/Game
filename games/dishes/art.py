"""Pixel art for the dishwashing game: the dishes and the sponge.

Each dish is drawn on its own grid (art pixels) and added to
room.sprites.SPRITES as "dish-<name>". Dirt is placed on top of these by
logic.py, only on the dish's surface (not on its outline or empty space).
"""
from room import sprites


def _canvas(w, h):
    return [["." for _ in range(w)] for _ in range(h)]


def _ellipse(c, cx, cy, rx, ry, fill, outline="o"):
    """Draw a filled ellipse with an outline onto canvas c."""
    def inside(x, y):
        return ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1

    for y in range(len(c)):
        for x in range(len(c[0])):
            if inside(x, y):
                edge = not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                c[y][x] = outline if edge else fill


def _rows(c):
    return ["".join(r) for r in c]


def plate():
    c = _canvas(30, 30)
    _ellipse(c, 15, 15, 15, 15, "c")
    _ellipse(c, 15, 15, 11, 11, "w", outline="C")
    for x, y in ((15, 2), (26, 9), (26, 21), (15, 27), (4, 21), (4, 9)):
        c[y][x] = "p"      # little pink dots around the rim
    return _rows(c)


def cup():
    """A cream cup with a pink band, seen a little from above, and a handle."""
    body = ".o" + "w" * 14 + "o"
    band = ".o" + "p" * 14 + "o"
    return [
        "...oooooooooooo.........",
        ".ooccccccccccccoo.......",
        "occCCCCCCCCCCCCcco......",
        "ocCCCCCCCCCCCCCCco......",
        "occCCCCCCCCCCCCcco......",
        ".ooccccccccccccoo.......",
        body + ".......",
        body + "ooooo..",
        body + "wwwwo..",
        body + "ooowo..",
        band + "..owo..",
        band + "..owo..",
        body + "..owo..",
        body + "ooowo..",
        body + "wwwwo..",
        body + "ooooo..",
        body + ".......",
        body + ".......",
        body + ".......",
        body + ".......",
        ".o" + "C" * 14 + "o.......",
        "..oooooooooooooo........",
    ]


def pot():
    c = _canvas(36, 26)
    for y in range(6, 25):
        for x in range(4, 32):
            edge = x in (4, 31) or y == 24
            c[y][x] = "o" if edge else ("w" if x == 7 else "k")
    _ellipse(c, 18, 6, 14, 6, "K")           # the inside
    for side in ((0, 4), (32, 36)):          # handles
        for y in (9, 10, 11):
            for x in range(*side):
                c[y][x] = "o" if y != 10 or x in side else "K"
    return _rows(c)


def pan():
    c = _canvas(42, 26)
    _ellipse(c, 13, 13, 13, 13, "k")
    _ellipse(c, 13, 13, 10, 10, "K", outline="k")
    for y in range(11, 16):                  # wooden handle
        for x in range(26, 42):
            edge = y in (11, 15) or x == 41
            c[y][x] = "o" if edge else ("n" if y == 12 else "b")
    return _rows(c)


def fork():
    """Three outlined tines on the right, a long handle with a pink tip."""
    edge = "." * 19 + "o" * 16 + "."
    tine = "." * 19 + "o" + "k" * 14 + "o" + "."
    neck = "." * 19 + "o" + "kkkk" + "o" * 11 + "."
    handle_edge = "o" * 20 + "kkkk" + "o" * 11 + "."
    handle = "o" + "pp" + "k" * 31 + "o" + "."
    return [edge, tine, neck, handle_edge, handle, handle_edge, neck, tine, edge]


def spoon():
    c = _canvas(36, 11)
    for y in range(4, 7):
        for x in range(0, 22):
            c[y][x] = "o" if y != 5 or x == 0 else "k"
    c[5][1] = c[5][2] = "p"
    _ellipse(c, 28.5, 5.5, 7.5, 5.5, "k")
    for x in range(24, 30):
        c[3][x] = "w" if c[3][x] == "k" else c[3][x]
    return _rows(c)


def knife():
    c = _canvas(36, 8)
    for y in range(1, 7):                    # pink handle with rivets
        for x in range(0, 13):
            c[y][x] = "o" if y in (1, 6) or x == 0 else "p"
    c[3][4] = c[3][8] = "w"
    for y in range(1, 7):                    # blade, narrowing to a point
        for x in range(13, 36):
            top = 1 + (x - 13) * 3 // 23
            if y >= top:
                c[y][x] = "o" if y in (top, 6) or x == 35 else ("K" if y == 5 else "k")
    return _rows(c)


SPONGE = [
    "oooooooooooo",
    "ojjjjjjjjjjo",
    "ommmmmmmmmmo",
    "oooooooooooo",
    "oylyylyylyyo",
    "oyyyyyyyyyyo",
    "oylyylyylyyo",
    "oCCCCCCCCCCo",
    "oooooooooooo",
]

STAR = [
    "....o....",
    "...oyo...",
    "oooyyyooo",
    "oyyyyyyyo",
    ".oyyyyyo.",
    "..oyyyo..",
    ".oyyoyyo.",
    ".oyo.oyo.",
    ".oo...oo.",
]

SPARKLE = [
    "..w..",
    "..y..",
    "wywyw",
    "..y..",
    "..w..",
]

DISH_ART = {
    "plate": plate(), "cup": cup(), "pot": pot(), "pan": pan(),
    "fork": fork(), "spoon": spoon(), "knife": knife(),
}

sprites.SPRITES.update({f"dish-{name}": rows for name, rows in DISH_ART.items()})
sprites.SPRITES["sponge"] = SPONGE
sprites.SPRITES["star"] = STAR
sprites.SPRITES["star-empty"] = [row.replace("y", "C") for row in STAR]
sprites.SPRITES["sparkle"] = SPARKLE
