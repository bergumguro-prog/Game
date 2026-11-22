"""Potted flowers for the rooms (they replaced the round green plants).

Each pot is 10x14 art pixels, the same size as the old plants, so they use
the same hitbox: blooms on stems at the top, a pot at the bottom. The
outline around blooms and stems is added automatically. room/sprites.py
adds FLOWER_SPRITES to SPRITES.
"""

# Bloom shapes: (dx, dy, color key) around the bloom's top-left corner.
# "A" is the main petal color, "B" the darker one, "C" the middle.
TULIP = [(0, 0, "A"), (2, 0, "A"), (0, 1, "A"), (1, 1, "B"), (2, 1, "A"), (0, 2, "A"), (1, 2, "A"), (2, 2, "A")]
DAISY = [(1, 0, "A"), (0, 1, "A"), (1, 1, "C"), (2, 1, "A"), (1, 2, "A")]
ROSE = [(0, 0, "A"), (1, 0, "A"), (2, 0, "B"), (0, 1, "B"), (1, 1, "C"), (2, 1, "A"), (0, 2, "A"), (1, 2, "B"), (2, 2, "A")]
SPIKE = [(1, 0, "A"), (1, 1, "B"), (1, 2, "A"), (1, 3, "B")]

POT = [
    ".oooooooo.",
    ".oXXXXXXo.",
    ".oZXXXXYo.",
    "..oXXXXo..",
    "..oYYYYo..",
    "...oooo...",
]

# Where the three blooms go: (x, y) of each bloom's top-left corner.
SPOTS = [(1, 3), (4, 1), (6, 4)]


def _flower_pot(shape, colors, pot):
    w, h = 10, 14
    c = [["." for _ in range(w)] for _ in range(h)]
    for bx, by in SPOTS:
        bottom = by
        for dx, dy, key in shape:
            c[by + dy][bx + dx] = colors[key]
            bottom = max(bottom, by + dy)
        stem_x = bx + 1
        for y in range(bottom + 1, 8):  # the stem, down to the pot
            if c[y][stem_x] == ".":
                c[y][stem_x] = "g"
    c[6][2] = c[6][8] = "G"           # a couple of leaves
    c[5][5] = "G"
    # outline everything that's drawn so far
    drawn = {(x, y) for y in range(8) for x in range(w) if c[y][x] != "."}
    for y in range(8):
        for x in range(w):
            if c[y][x] == "." and any((x + dx, y + dy) in drawn
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                c[y][x] = "o"
    x_main, y_dark, z_light = pot
    for i, row in enumerate(POT):
        c[8 + i] = list(row.replace("X", x_main).replace("Y", y_dark).replace("Z", z_light))
    return ["".join(r) for r in c]


FLOWER_SPRITES = {
    # pink tulips in a mint pot
    "flowers-tulips": _flower_pot(TULIP, {"A": "p", "B": "P"}, ("m", "M", "j")),
    # white daisies in a cream pot
    "flowers-daisies": _flower_pot(DAISY, {"A": "w", "C": "y"}, ("c", "C", "w")),
    # lavender in a pink pot
    "flowers-lavender": _flower_pot(SPIKE, {"A": "v", "B": "V"}, ("p", "P", "l")),
    # red roses in a lavender pot
    "flowers-roses": _flower_pot(ROSE, {"A": "e", "B": "r", "C": "P"}, ("v", "V", "u")),
}
