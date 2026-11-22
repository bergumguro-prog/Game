"""Pixel art for the baking game: ingredient icons (12x12).

Most ingredients share a few shapes (a sack, a jar, a box, a tin) in their
own colors; a few are drawn on their own. They're added to
room.sprites.SPRITES as "ing-<id>".
"""
from room import sprites


def _recolor(rows, mapping):
    table = str.maketrans(mapping)
    return [row.translate(table) for row in rows]


# Shapes. Letters X (body), L (label) and T (label text) are swapped for
# real colors below.
SACK = [
    "............",
    "....oooo....",
    ".....oo.....",
    "...oooooo...",
    "..oXXXXXXo..",
    ".oXXXXXXXXo.",
    ".oXLLLLLLXo.",
    ".oXLTTTTLXo.",
    ".oXLLLLLLXo.",
    ".oXXXXXXXXo.",
    ".oTTTTTTTTo.",
    "..oooooooo..",
]

JAR = [
    "............",
    "..oooooooo..",
    "..oLLLLLLo..",
    "..oooooooo..",
    ".owXXXXXXXo.",
    ".owXXXXXXXo.",
    ".oXXwwwwXXo.",
    ".oXXwTTwXXo.",
    ".oXXwwwwXXo.",
    ".oXXXXXXXXo.",
    ".oXXXXXXXXo.",
    "..oooooooo..",
]

BOX = [
    "..oooooooo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oLLLLLLo..",
    "..oLTTTTLo..",
    "..oLLLLLLo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oTTTTTTo..",
    "..oooooooo..",
]

TIN = [
    "............",
    "..oooooooo..",
    "..okkkkkko..",
    "..oooooooo..",
    "..oXXXXXXo..",
    "..oXLLLLXo..",
    "..oXLTTLXo..",
    "..oXLLLLXo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oTTTTTTo..",
    "..oooooooo..",
]

MILK = [
    "...oooooo...",
    "..ojjjjjjo..",
    ".ojjjjjjjjo.",
    ".oooooooooo.",
    ".owwwwwwwwo.",
    ".owmmmmmmwo.",
    ".owmwwwwmwo.",
    ".owmmmmmmwo.",
    ".owwwwwwwwo.",
    ".owwwwwwwwo.",
    ".oCCCCCCCCo.",
    ".oooooooooo.",
]

EGGS = [
    "............",
    "............",
    "............",
    ".oo..oo..oo.",
    "occooccoocco",
    "occooccoocco",
    "oooooooooooo",
    "oppppppppppo",
    "opllpllpllpo",
    "oppppppppppo",
    "oPPPPPPPPPPo",
    "oooooooooooo",
]

BUTTER = [
    "............",
    "............",
    "............",
    "............",
    ".oooooooooo.",
    ".oyyyyyyyyo.",
    ".oyyyyyyyyo.",
    ".oooooooooo.",
    ".owwwwwwwwo.",
    ".owppwwppwo.",
    ".owwwwwwwwo.",
    ".oooooooooo.",
]

BLUEBERRIES = [
    "............",
    "............",
    "............",
    "..oo.oo.oo..",
    ".oVVoVVoVVo.",
    ".oVvoVvoVvo.",
    "oooooooooooo",
    "ojjjjjjjjjjo",
    "ojmjmjmjmjmo",
    "ojjjjjjjjjjo",
    "oMMMMMMMMMMo",
    "oooooooooooo",
]

CHEESE = [
    "............",
    "............",
    "............",
    "............",
    "............",
    "..ooooooooo.",
    ".oyyyyyyyyo.",
    "ooooooooooo.",
    "oynyyyynyyo.",
    "oyyyynyyyyo.",
    "oyynyyyyyno.",
    "ooooooooooo.",
]

CARROTS = [
    "....o.o.o...",
    "....ogogo...",
    ".....oGo....",
    "....offfo...",
    "....offfo...",
    "....ofnfo...",
    "....offfo...",
    ".....offo...",
    ".....ofno...",
    ".....ofo....",
    "......o.....",
    "............",
]

SALT = [
    "............",
    "....oooo....",
    "...okkkko...",
    "...okokko...",
    "...oooooo...",
    "...owwwwo...",
    "..owwwwwwo..",
    "..owwwwwwo..",
    "..owwwwwwo..",
    "..owwwwwwo..",
    "..oCCCCCCo..",
    "..oooooooo..",
]

ICONS = {
    "milk": MILK,
    "eggs": EGGS,
    "butter": BUTTER,
    "blueberries": BLUEBERRIES,
    "cheese": CHEESE,
    "jam": _recolor(JAR, {"X": "e", "L": "P", "T": "p"}),
    "carrots": CARROTS,
    "pickles": _recolor(JAR, {"X": "g", "L": "n", "T": "G"}),
    "flour": _recolor(SACK, {"X": "c", "L": "w", "T": "C"}),
    "sugar": _recolor(SACK, {"X": "w", "L": "l", "T": "p"}),
    "baking-powder": _recolor(TIN, {"X": "m", "L": "w", "T": "p"}),
    "salt": SALT,
    "rice": _recolor(BOX, {"X": "w", "L": "m", "T": "M"}),
    "pasta": _recolor(BOX, {"X": "y", "L": "e", "T": "w"}),
    "cocoa": _recolor(TIN, {"X": "b", "L": "c", "T": "B"}),
    "oats": _recolor(BOX, {"X": "n", "L": "c", "T": "b"}),
}

sprites.SPRITES.update({f"ing-{name}": rows for name, rows in ICONS.items()})


# --- Bowl, muffin tin and oven --------------------------------------------------

def _canvas(w, h):
    return [["." for _ in range(w)] for _ in range(h)]


def _rows(c):
    return ["".join(r) for r in c]


def _bowl(contents):
    """A mint mixing bowl seen a little from above. `contents` is a function
    (x, y) -> letter for what's inside, or None for an empty bowl."""
    w, h = 32, 17
    c = _canvas(w, h)
    cx, cy, rx, ry = 16.0, 4.0, 15.5, 4.0
    # the body: a bowl shape narrowing toward the bottom
    for y in range(4, h - 1):
        half = rx - (y - 4) * 0.75
        for x in range(w):
            dx = abs(x + 0.5 - cx)
            if dx <= half:
                edge = dx > half - 1 or y == h - 2
                c[y][x] = "o" if edge else ("j" if x + 0.5 < cx - half + 3 else "m")

    def in_rim(x, y, shrink=0.0):
        return ((x + 0.5 - cx) / (rx - shrink)) ** 2 + ((y + 0.5 - cy) / (ry - shrink * 0.4)) ** 2 <= 1

    # the rim and what's inside, drawn over the top of the body
    for y in range(0, 9):
        for x in range(w):
            if not in_rim(x, y):
                continue
            outside = any(not in_rim(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if outside:
                c[y][x] = "o"
            elif in_rim(x, y, shrink=2.5):
                c[y][x] = contents(x, y) if contents else "M"
            else:
                c[y][x] = "j"
    for x in range(11, 21):
        c[h - 1][x] = "o"   # a little foot
    return _rows(c)


def _lumpy(x, y):
    """Not mixed yet: lumps of flour, butter and berries."""
    spots = {(9, 4): "c", (13, 3): "y", (18, 5): "V", (21, 4): "c", (15, 5): "w",
             (11, 5): "V", (23, 4): "y", (7, 4): "c", (19, 3): "w", (16, 3): "y"}
    return spots.get((x, y), "C")


def _smooth(x, y):
    """Mixed: smooth batter with a few blueberries."""
    return "V" if (x, y) in {(10, 4), (16, 5), (21, 4), (13, 3), (19, 5)} else "c"


def _tin(filled):
    """A steel muffin tin with six cups, seen from above."""
    w, h = 36, 14
    c = _canvas(w, h)
    for y in range(h):
        for x in range(w):
            edge = x in (0, w - 1) or y in (0, h - 1)
            c[y][x] = "o" if edge else ("w" if y == 1 else "k")
    for row in range(2):
        for col in range(3):
            cx, cy = 6 + col * 12, 4 + row * 6
            for y in range(cy - 2, cy + 3):
                for x in range(cx - 4, cx + 5):
                    d = ((x - cx) / 4.5) ** 2 + ((y - cy) / 2.6) ** 2
                    if d <= 1:
                        if filled:
                            c[y][x] = "o" if d > 0.75 else ("V" if (x + y) % 5 == 0 else "y")
                        else:
                            c[y][x] = "o" if d > 0.75 else "K"
    return _rows(c)


def _oven():
    """A cream oven with knobs and a big window (the muffins are drawn on
    top of the window by the page)."""
    w, h = 44, 34
    c = _canvas(w, h)
    for y in range(h):
        for x in range(w):
            if x in (0, w - 1) or y in (0, h - 1):
                c[y][x] = "o"
            elif y <= 6:
                c[y][x] = "C" if y == 6 else "c"
            else:
                c[y][x] = "c"
    for kx in (6, 12, 31, 37):                     # knobs
        c[3][kx] = c[3][kx + 1] = "P"
        c[2][kx] = c[2][kx + 1] = "o"
    for x in range(17, 27):                       # clock
        c[2][x] = c[4][x] = "o"
    for x in range(18, 26):
        c[3][x] = "j"
    for x in range(5, w - 5):                     # handle
        c[9][x] = "w"
        c[10][x] = "o"
    for y in range(13, h - 4):                    # window
        for x in range(6, w - 6):
            edge = x in (6, w - 7) or y in (13, h - 5)
            c[y][x] = "o" if edge else ("f" if y == h - 6 else "B")
    for x in range(1, w - 1):
        c[h - 2][x] = "C"
    return _rows(c)


def _oven_muffins():
    """Four domed muffins in pink paper cases on a tin, seen through the oven
    window. Their tops are "y"; the page colors them by how baked they are."""
    muffin = [
        "..ooo..",
        ".oyyyo.",
        "oyyyyyo",
        "oyyyyyo",
        "opPpPpo",
        ".oPpPo.",
    ]
    w = 30
    c = _canvas(w, 9)
    for i in range(4):
        x0 = 1 + i * 7
        for dy, row in enumerate(muffin):
            for dx, ch in enumerate(row):
                if ch != ".":
                    c[dy][x0 + dx] = ch
    for x in range(w):                    # the tin underneath
        c[6][x] = c[8][x] = "o"
        c[7][x] = "k"
    return _rows(c)


BIG_ART = {
    "bowl-empty": _bowl(None),
    "bowl-lumpy": _bowl(_lumpy),
    "bowl-smooth": _bowl(_smooth),
    "tin-empty": _tin(False),
    "tin-full": _tin(True),
    "oven": _oven(),
    "oven-muffins": _oven_muffins(),
}
sprites.SPRITES.update(BIG_ART)


# --- Finished muffins and stars --------------------------------------------------

def _muffin(domed, top):
    """A big muffin for the results. `top` is the color letter of its top;
    flat muffins (lots of mistakes) have a low top."""
    case = [
        "oooooooooooooo",
        ".opPpPpPpPpPo.",
        ".opPpPpPpPpPo.",
        "..opPpPpPpPo..",
        "..opPpPpPpPo..",
        "..oooooooooo..",
    ]
    if domed:
        dome = [
            "....oooooo....",
            "..ooTTTTTToo..",
            ".oTTTVTTTTTTo.",
            "oTTTTTTTVTTTTo",
            "oTTVTTTTTTTVTo",
            "oTTTTTTTTTTTTo",
        ]
    else:
        dome = [
            "..............",
            "..............",
            "..............",
            "..oooooooooo..",
            ".oTTTVTTTTVTo.",
            "oTTTTTTTTTTTTo",
        ]
    return [row.replace("T", top) for row in dome] + case


# top colors: how the muffins were baked
MUFFIN_TOPS = {"golden": "n", "pale": "y", "very-pale": "c", "dark": "b", "very-dark": "B"}

for look, letter in MUFFIN_TOPS.items():
    sprites.SPRITES[f"muffin-{look}"] = _muffin(True, letter)
    sprites.SPRITES[f"muffin-{look}-flat"] = _muffin(False, letter)

BAKE_STAR = [
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
sprites.SPRITES["bake-star"] = BAKE_STAR
sprites.SPRITES["bake-star-empty"] = [row.replace("y", "C") for row in BAKE_STAR]
