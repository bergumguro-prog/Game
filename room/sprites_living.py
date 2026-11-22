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


def _sofa(width=40, height=20):
    """A pink sofa seen from the front: a buttoned back, round arms, two seat
    cushions and two lavender pillows."""
    c = _canvas(width, height)

    def paste(box, x0, y0):
        for y, row in enumerate(box):
            for x, ch in enumerate(row):
                if ch != ".":
                    c[y0 + y][x0 + x] = ch

    back = _rounded_box(width - 6, 12, 4, "p")
    for y, row in enumerate(back):
        for x, ch in enumerate(row):
            if ch == "p" and y == 1:
                row[x] = "l"                     # light along the top
            elif ch == "p" and y in (4, 7) and x % 7 == 3:
                row[x] = "P"                     # buttons
    paste(back, 3, 0)
    for x0 in (0, width - 8):                    # arms
        arm = _rounded_box(8, 13, 3, "p")
        for x in range(1, 7):
            if arm[1][x] == "p":
                arm[1][x] = "l"
        paste(arm, x0, 6)
    paste(_rounded_box(7, 6, 2, "v"), 8, 5)      # pillows
    paste(_rounded_box(7, 6, 2, "v"), width - 15, 5)
    half = (width - 14) // 2
    paste(_rounded_box(half + 1, 6, 2, "l"), 7, 9)            # seat cushions
    paste(_rounded_box(half + 1, 6, 2, "l"), 7 + half, 9)
    for y in range(9, 15):                       # close the seam between cushions
        if c[y][7 + half] == ".":
            c[y][7 + half] = "o"
    for y in range(14, 18):                      # the front, under the cushions
        for x in range(6, width - 6):
            c[y][x] = "o" if y == 17 else "P"
    for x in (3, 4, width - 5, width - 4):       # little wooden feet
        c[18][x] = "B"
        c[19][x] = "o"
    return _rows(c)


LIVING_SPRITES = {
    "sofa": _sofa(),
    "armchair": ARMCHAIR,
    "dresser": _dresser(),
}
