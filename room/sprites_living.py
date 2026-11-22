"""Pixel art for the living room and bedroom: an armchair and a dresser.
Same letters as room/sprites.py; room/sprites.py adds LIVING_SPRITES to
SPRITES.
"""
from room.sprites_kitchen import _canvas, _rounded_box, _rows  # noqa: F401

# A lavender armchair with a pink seat cushion, seen from the front.
ARMCHAIR = [
    "..oooooooooooo..",
    ".ouuuuuuuuuuuuo.",
    ".ouvvvvvvvvvvuo.",
    ".ouvvvvvvvvvvuo.",
    "oooovvvvvvvvoooo",
    "ouuovvvvvvvvouuo",
    "ouvoooooooooovuo",
    "ouvoppppppppovuo",
    "ouvolpppppppovuo",
    "ouvoPPPPPPPPovuo",
    "oVVooooooooooVVo",
    "oVVVVVVVVVVVVVVo",
    "ovvvvvvvvvvvvvvo",
    "oVVVVVVVVVVVVVVo",
    "oooooooooooooooo",
    ".oBo........oBo.",
]


def _dresser(width=24):
    """A cream dresser with four drawers and a round mirror on top."""
    c = _canvas(width, 24)
    mirror = _rounded_box(10, 10, 4, "n")
    glass = _rounded_box(6, 6, 2, "j")
    for y, row in enumerate(glass):
        for x, ch in enumerate(row):
            if ch != ".":
                mirror[2 + y][2 + x] = "w" if (x, y) == (2, 1) else ("b" if ch == "o" else "j")
    for y, row in enumerate(mirror):
        for x, ch in enumerate(row):
            c[y][(width - 10) // 2 + x] = ch
    inner = width - 2
    top = ["o" * width, "o" + "w" * inner + "o", "o" + "c" * inner + "o",
           "o" + "C" * inner + "o", "o" * width]
    for i, row in enumerate(top):
        c[10 + i] = list(row)
    half = width // 2
    for y in range(15, 21):
        row = ["o"] + ["c"] * inner + ["o"]
        for x0, x1 in ((1, half - 1), (half, width - 2)):
            for x in range(x0, x1 + 1):
                if x in (x0, x1) or y in (15, 17, 18, 20):
                    row[x] = "C"
            if y in (16, 19):
                row[(x0 + x1) // 2] = "p"  # knob
        c[y] = row
    c[21] = list("o" * width)
    gap = "." * (width - 8)
    c[22] = list(".oCo" + gap + "oCo.")
    c[23] = list(".ooo" + gap + "ooo.")
    return _rows(c)


def _sofa_back(width=38, height=17):
    """A lavender sofa seen from behind (it faces the fireplace), with two
    pink cushions peeking over the back."""
    c = _canvas(width, height)

    def paste(box, x0, y0):
        for y, row in enumerate(box):
            for x, ch in enumerate(row):
                if ch != ".":
                    c[y0 + y][x0 + x] = ch

    paste(_rounded_box(8, 6, 2, "p"), 8, 0)            # cushions
    paste(_rounded_box(8, 6, 2, "p"), width - 16, 0)
    paste(_rounded_box(8, 14, 3, "V"), 0, 2)           # arms
    paste(_rounded_box(8, 14, 3, "V"), width - 8, 2)
    back = _rounded_box(width - 10, 13, 3, "v")       # the back
    for y, row in enumerate(back):
        for x, ch in enumerate(row):
            if ch == "v" and y == 1:
                row[x] = "u"                           # light along the top
            elif ch == "v" and y in (6, 9) and x % 6 == 3:
                row[x] = "V"                           # buttons
    paste(back, 5, 3)
    for x in (2, 3, width - 4, width - 3):             # little wooden feet
        c[height - 1][x] = "B"
    return _rows(c)


LIVING_SPRITES = {
    "sofa-back": _sofa_back(),
    "armchair": ARMCHAIR,
    "dresser": _dresser(),
}
