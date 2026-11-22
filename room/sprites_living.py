"""Pixel art for the living room and bedroom: an armchair and a dresser.
Same letters as room/sprites.py; room/sprites.py adds LIVING_SPRITES to
SPRITES.
"""
from room.sprites_kitchen import _canvas, _rounded_box, _rows

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


LIVING_SPRITES = {
    "armchair": ARMCHAIR,
    "dresser": _dresser(),
}
