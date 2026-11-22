"""Pixel art for the fireplace scene: the big stone fireplace and the logs.

The fireplace has a see-through opening; the flames are drawn behind it on
a <canvas> (static/fireplace.js), and the logs are drawn in front of them.
All sizes are in art pixels. The sprites are added to room.sprites.SPRITES.
"""
from room import sprites

FRAME_W = 72
FRAME_H = 66
DECOR_H = 10                       # room above the mantel for candles
OPENING = (16, 26, 40, 32)         # (x, y, w, h) of the fire's opening
ARCH = 6                           # how rounded the opening's top corners are
LOGS_W = 30
LOGS_H = 9
LOGS_POS = (OPENING[0] + (OPENING[2] - LOGS_W) // 2, OPENING[1] + OPENING[3] - LOGS_H)


def in_opening(x, y):
    """Is (x, y) inside the opening, where the flames show through?"""
    ox, oy, ow, oh = OPENING
    if not (ox <= x < ox + ow and oy <= y < oy + oh):
        return False
    # round off the top corners into an arch
    for cx in (ox + ARCH, ox + ow - 1 - ARCH):
        cy = oy + ARCH
        far_side = x < cx if cx == ox + ARCH else x > cx
        if y < cy and far_side and (x - cx) ** 2 + (y - cy) ** 2 > ARCH ** 2:
            return False
    return True


def _frame():
    c = [["." for _ in range(FRAME_W)] for _ in range(FRAME_H)]

    # mantel shelf
    for x in range(FRAME_W):
        for y, ch in ((10, "o"), (11, "n"), (12, "n"), (13, "b"), (14, "B"), (15, "o")):
            c[y][x] = ch
    for y in range(10, 16):
        c[y][0] = c[y][FRAME_W - 1] = "o"

    # stone body, laid like bricks
    for y in range(16, 58):
        for x in range(4, FRAME_W - 4):
            if x in (4, FRAME_W - 5):
                c[y][x] = "o"
                continue
            row, line = divmod(y - 16, 4)
            offset = 0 if row % 2 == 0 else 4
            mortar = line == 3 or (x - 5 + offset) % 8 == 7
            c[y][x] = "T" if mortar else "t"

    # the opening (see-through) with an outline around it
    for y in range(FRAME_H):
        for x in range(FRAME_W):
            if in_opening(x, y):
                c[y][x] = "."
    for y in range(16, 58):
        for x in range(5, FRAME_W - 5):
            if c[y][x] != "." and any(in_opening(x + dx, y + dy)
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                c[y][x] = "o"

    # hearth slab in front
    for y in range(58, FRAME_H):
        for x in range(FRAME_W):
            edge = x in (0, FRAME_W - 1) or y in (58, FRAME_H - 1)
            c[y][x] = "o" if edge else ("C" if y == FRAME_H - 2 else ("T" if (x + y) % 9 == 0 else "t"))

    # a green garland with red berries along the mantel's front
    for x in range(2, FRAME_W - 2):
        dip = 1 if (x // 6) % 2 else 0
        c[14 + dip][x] = "g" if x % 3 else "G"
        c[15 + dip][x] = "G" if x % 3 == 0 else c[15 + dip][x]
        if x % 12 == 6:
            c[16 + dip][x] = "e"

    # two candles and a little vase of flowers on the mantel
    def candle(x0):
        c[0][x0 + 1] = "y"
        c[1][x0], c[1][x0 + 1], c[1][x0 + 2] = ".", "f", "."
        c[2][x0 + 1] = "o"
        for y in range(3, 10):
            c[y][x0], c[y][x0 + 1], c[y][x0 + 2] = "o", "w" if y > 3 else "o", "o"
        c[9][x0 - 1] = c[9][x0 + 3] = "o"

    candle(8)
    candle(FRAME_W - 11)
    vase = sprites.SPRITES["flower-pot"]
    for y, row in enumerate(vase):
        for x, ch in enumerate(row):
            if ch != ".":
                c[DECOR_H - len(vase) + y][FRAME_W // 2 - 4 + x] = ch
    return ["".join(row) for row in c]


def _logs():
    """Two logs on a little grate, with glowing embers in the cracks."""
    c = [["." for _ in range(LOGS_W)] for _ in range(LOGS_H)]

    def log(x0, x1, y0):
        for y in range(y0, y0 + 5):
            for x in range(x0, x1 + 1):
                edge = y in (y0, y0 + 4) or x in (x0, x1)
                c[y][x] = "o" if edge else ("n" if y == y0 + 1 else "b")
        # the cut end shows rings
        c[y0 + 2][x1 - 1] = "C"
        c[y0 + 1][x1 - 1] = c[y0 + 3][x1 - 1] = "n"

    log(6, 28, 0)
    log(1, 23, 3)
    for x, y, ember in ((9, 1, "f"), (14, 1, "e"), (20, 2, "y"), (25, 1, "f"),
                        (4, 4, "e"), (8, 5, "f"), (12, 4, "y"), (17, 5, "e"), (21, 4, "f")):
        c[y][x] = ember
    for x in range(LOGS_W):
        c[8][x] = "o" if 0 < x < LOGS_W - 1 else "."
    return ["".join(row) for row in c]


sprites.SPRITES["hearth"] = _frame()
sprites.SPRITES["hearth-logs"] = _logs()
