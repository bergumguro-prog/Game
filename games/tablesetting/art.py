"""Pixel art for table decorating: everything you can put on the table,
seen from above. Items with color choices are drawn once with the letters
X (main color) and Y (darker shade) and colored per choice.

Sprites are added to room.sprites.SPRITES as "table-<item>-<color>".
"""
from room import sprites


def _canvas(w, h):
    return [["." for _ in range(w)] for _ in range(h)]


def _rows(c):
    return ["".join(r) for r in c]


def _disc(size, rings):
    """A round thing seen from above. `rings` is a list of (radius fraction,
    letter) from the outside in; the outline is added automatically."""
    c = _canvas(size, size)
    r = size / 2
    for y in range(size):
        for x in range(size):
            d = ((x + 0.5 - r) ** 2 + (y + 0.5 - r) ** 2) ** 0.5 / r
            if d > 1:
                continue
            if d > 1 - 1.5 / r:
                c[y][x] = "o"
                continue
            for frac, letter in rings:
                if d <= frac:
                    c[y][x] = letter
    return _rows(c)


PLATE = _disc(16, [(1.0, "X"), (0.78, "Y"), (0.66, "w")])
BOWL = _disc(12, [(1.0, "X"), (0.7, "Y"), (0.45, "w")])
GLASS = _disc(8, [(1.0, "u"), (0.6, "w")])

CUP = [
    "...oooooo...",
    "..oXXXXXXo..",
    ".oXYYYYYYXo.",
    ".oXYbbbbYXooo",
    ".oXYbbbbYXo.o",
    ".oXYbbbbYXooo",
    ".oXYYYYYYXo.",
    "..oXXXXXXo..",
    "...oooooo...",
]
CUP = [row.ljust(13, ".") for row in CUP]

FORK = [
    "o.o.o",
    "okoko",
    "okoko",
    "okkko",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oXo.",
    ".oXo.",
    ".oXo.",
    "..o..",
]

KNIFE = [
    "..o..",
    ".oko.",
    ".okKo",
    ".okKo",
    ".okKo",
    ".okKo",
    ".okKo",
    ".okKo",
    ".oooo",
    ".oXo.",
    ".oXo.",
    ".oXo.",
    ".oXo.",
    "..o..",
]

SPOON = [
    ".ooo.",
    "okwko",
    "okkko",
    "okkko",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oko.",
    ".oXo.",
    ".oXo.",
    ".oXo.",
    "..o..",
]

NAPKIN = [
    "oooooooooo",
    "oXXXXXXXYo",
    "oXXXXXXYYo",
    "oXXXXXYYXo",
    "oXXXXYYXXo",
    "oXXXYYXXXo",
    "oXXYYXXXXo",
    "oXYYXXXXXo",
    "oYYXXXXXXo",
    "oooooooooo",
]

# A candle in a little holder, seen from above: the flame glows in the middle.
CANDLE = _disc(10, [(1.0, "C"), (0.72, "X"), (0.42, "y"), (0.2, "f")])

VASE = [
    "..o..o.o...",
    ".oro.opo...",
    "..ogoGo.ov.",
    ".oogggggovo",
    "..ogGgGgoo.",
    "...oXXXo...",
    "..oXwXXXo..",
    "..oXXXXXo..",
    "..oYXXXYo..",
    "...ooooo...",
]

TEAPOT = [
    ".....oo.........",
    "....oXXo........",
    "...ooooooo......",
    "..oXXXXXXXo..oo.",
    ".oXXwXXXXXXooXo.",
    "ooXXXXYXXXXXXo..",
    "oXXXXXXXXXXXXo..",
    "oXXXXXXXXXXXo...",
    ".oXXXXXXXXXo....",
    "..ooooooooo.....",
]

CAKE_STAND = _disc(16, [(1.0, "c"), (0.85, "w"), (0.62, "P"), (0.5, "p"), (0.3, "w"), (0.14, "e")])

# What each color choice means for X (main) and Y (shade).
COLORS = {
    "pink": ("p", "P"),
    "mint": ("m", "M"),
    "cream": ("c", "C"),
    "lavender": ("v", "V"),
    "white": ("w", "C"),
}


def colored(rows, color):
    x, y = COLORS[color]
    return [row.replace("X", x).replace("Y", y) for row in rows]


SHAPES = {
    "plate": PLATE, "bowl": BOWL, "cup": CUP, "glass": GLASS,
    "fork": FORK, "knife": KNIFE, "spoon": SPOON, "napkin": NAPKIN,
    "candle": CANDLE, "vase": VASE, "teapot": TEAPOT, "cake-stand": CAKE_STAND,
}


def sprite_name(item, color):
    return f"table-{item}-{color}"
