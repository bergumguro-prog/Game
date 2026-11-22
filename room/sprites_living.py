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


def _shade(box, light_rows=2, dark_rows=2):
    """Flat shading on a rounded box: lighter top rows, darker bottom rows."""
    h = len(box)
    for y, row in enumerate(box):
        for x, ch in enumerate(row):
            if ch == "p":
                if 0 < y <= light_rows:
                    row[x] = "l"
                elif y >= h - 1 - dark_rows:
                    row[x] = "P"
    return box


def _sofa_back(width=40, height=17):
    """The pink sofa seen from behind (it faces the card table): a tall,
    rounded back with a soft roll along the top, and small, low arms."""
    c = _canvas(width, height)
    for x0 in (0, width - 7):                      # small, low arms
        _paste(c, _shade(_rounded_box(7, 10, 2, "p"), 1, 2), x0, 4)
    back = _shade(_rounded_box(width - 8, 14, 3, "p"), 2, 3)
    for x in range(3, width - 11):                 # the seam under the top roll
        if back[4][x] == "p":
            back[4][x] = "P"
    _paste(c, back, 4, 0)
    for x in (2, 3, width - 4, width - 3):         # wooden feet
        c[height - 3][x] = c[height - 3][x] if c[height - 3][x] != "." else "o"
        c[height - 2][x] = "B"
        c[height - 1][x] = "o"
    return _rows(c)


def _armchair_side():
    """A pink armchair from the side, facing left: a rounded back, a cushion
    peeking over a soft rolled arm, and little wooden legs."""
    w, h = 17, 17
    c = _canvas(w, h)
    _paste(c, _shade(_rounded_box(6, 15, 2, "p"), 2, 1), 11, 0)       # back
    _paste(c, _shade(_rounded_box(10, 4, 1, "p"), 1, 0), 2, 4)        # cushion
    body = _shade(_rounded_box(13, 9, 3, "p"), 2, 2)                  # arm and side
    body[4][2] = body[5][3] = "P"                                     # where the arm rolls
    _paste(c, body, 0, 6)
    for x in (2, 13):                                                 # legs
        c[15][x] = "B"
        c[16][x] = "o"
    return _rows(c)


def _mirror_rows(rows):
    return [row[::-1] for row in rows]


LIVING_SPRITES = {
    "sofa-back": _sofa_back(),
    "armchair-side": _armchair_side(),                    # faces left
    "armchair-side-right": _mirror_rows(_armchair_side()),  # faces right
    "dresser": _dresser(),
}
