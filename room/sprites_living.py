"""Pixel art for the living room and bedroom: a sofa, an armchair and a dresser.
Same letters as room/sprites.py; room/sprites.py adds LIVING_SPRITES to
SPRITES.
"""
from room.sprites_kitchen import _canvas, _rounded_box, _rows  # noqa: F401

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


# --- Soft, plump pink furniture ----------------------------------------------
# Built from rounded shapes, each shaded light on top and on its left, darker
# at the bottom and on its right, with rose seams and buttons.

def _plump(w, h, r):
    """A shaded rounded shape: outline, then light / pink / dark pink."""
    box = _rounded_box(w, h, r, "p")
    for y, row in enumerate(box):
        for x, ch in enumerate(row):
            if ch != "p":
                continue
            if y <= 1 or (x <= 1 and y < h - 3):
                row[x] = "l"
            elif y >= h - 3 or x >= w - 3:
                row[x] = "P"
    return box


def _paste(c, box, x0, y0):
    for y, row in enumerate(box):
        for x, ch in enumerate(row):
            if ch != ".":
                c[y0 + y][x0 + x] = ch


def _sofa_back(width=44, height=22):
    """The pink sofa seen from behind (it faces the card table): two plump
    rolled arms and a rounded back with a stitched seam."""
    c = _canvas(width, height)
    back = _plump(width - 16, 17, 4)
    cx = (width - 16) / 2
    for x in range(3, width - 19):                 # a curved seam across the back
        y = 6 + round(((x - cx) / cx) ** 2 * 3)
        if back[y][x] in "pP" and x % 2 == 0:
            back[y][x] = "r"
    for y in range(9, 15):                         # the lower back is in shadow
        for x in range(2, width - 18):
            if back[y][x] == "p":
                back[y][x] = "P"
    _paste(c, back, 8, 3)
    for x0 in (0, width - 11):                     # rolled arms
        arm = _plump(11, 19, 3)
        arm[3][5] = arm[4][5] = "r"                # where the roll curls
        _paste(c, arm, x0, 1)
    for x in (3, 4, width - 5, width - 4):         # wooden feet
        c[height - 2][x] = "B"
        c[height - 1][x] = "o"
    return _rows(c)


def _armchair_side():
    """A plump pink armchair from the side, facing left: a tall buttoned
    back, a rolled arm and a soft base."""
    w, h = 20, 21
    c = _canvas(w, h)
    back = _plump(8, 19, 2)
    back[4][4] = back[3][4] = back[5][4] = back[4][3] = back[4][5] = "r"   # a button
    _paste(c, back, 12, 0)
    _paste(c, _plump(18, 7, 2), 0, 12)             # base
    arm = _plump(15, 8, 3)
    arm[3][2] = arm[4][2] = "r"                    # where the roll curls
    _paste(c, arm, 0, 6)
    for x in (3, 15):                              # wooden legs
        c[19][x] = "B"
        c[20][x] = "o"
    return _rows(c)


def _mirror_rows(rows):
    return [row[::-1] for row in rows]


LIVING_SPRITES = {
    "sofa-back": _sofa_back(),
    "armchair-side": _armchair_side(),                    # faces left
    "armchair-side-right": _mirror_rows(_armchair_side()),  # faces right
    "dresser": _dresser(),
}
