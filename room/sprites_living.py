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


def _sofa_back(width=40, height=17):
    """The pink sofa seen from behind (it faces the card table): a rounded,
    buttoned back in three panels, round arms and two lavender pillows
    peeking over the top."""
    c = _canvas(width, height)

    def paste(box, x0, y0):
        for y, row in enumerate(box):
            for x, ch in enumerate(row):
                if ch != ".":
                    c[y0 + y][x0 + x] = ch

    paste(_rounded_box(9, 5, 2, "v"), 9, 0)              # pillows
    paste(_rounded_box(9, 5, 2, "v"), width - 18, 0)
    back = _rounded_box(width - 6, 13, 4, "p")
    inner_w = width - 6
    seams = (inner_w // 3, 2 * inner_w // 3)
    for y, row in enumerate(back):
        for x, ch in enumerate(row):
            if ch != "p":
                continue
            if y == 1:
                row[x] = "l"                              # light along the top
            elif x in seams and 3 <= y <= 9:
                row[x] = "P"                              # seams between panels
            elif y == 6 and any(abs(x - m) == 0 for m in (seams[0] // 2, (seams[0] + seams[1]) // 2,
                                                            (seams[1] + inner_w) // 2)):
                row[x] = "P"                              # a button in each panel
            elif y >= 10:
                row[x] = "P"                              # shade at the bottom
    paste(back, 3, 2)
    for x0 in (0, width - 7):                             # arms
        arm = _rounded_box(7, 12, 3, "p")
        for y, row in enumerate(arm):
            for x, ch in enumerate(row):
                if ch == "p" and y == 1:
                    row[x] = "l"
                elif ch == "p" and y >= 9:
                    row[x] = "P"
        paste(arm, x0, 4)
    for x in (2, 3, width - 4, width - 3):                # little wooden feet
        c[height - 1][x] = "B"
    return _rows(c)


def _armchair_side():
    """The lavender armchair from the side, facing left (toward the fire):
    a tall back on the right, the seat and arm in front of it."""
    w, h = 16, 14
    c = _canvas(w, h)
    regions = [
        # (x0, x1, y0, y1, letter) - inclusive, drawn in order
        (10, 13, 1, 11, "v"),     # back
        (11, 12, 1, 1, "u"),      # light on top of the back
        (2, 10, 7, 8, "p"),       # seat cushion
        (2, 3, 7, 7, "l"),
        (1, 10, 5, 6, "v"),       # the arm
        (1, 9, 5, 5, "u"),
        (1, 13, 9, 11, "V"),      # base
        (2, 2, 12, 12, "B"),      # legs
        (12, 12, 12, 12, "B"),
    ]
    for x0, x1, y0, y1, letter in regions:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c[y][x] = letter
    drawn = {(x, y) for y in range(h) for x in range(w) if c[y][x] != "."}
    for y in range(h):
        for x in range(w):
            if c[y][x] == "." and any((x + dx, y + dy) in drawn
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                c[y][x] = "o"
    # lines that separate the arm from the seat and the seat from the base
    for x in range(2, 10):
        if c[9][x] == "V":
            c[9][x] = "o"
    return _rows(c)


LIVING_SPRITES = {
    "sofa-back": _sofa_back(),
    "armchair-side": _armchair_side(),
    "dresser": _dresser(),
}
