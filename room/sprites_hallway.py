"""Pixel art for the hallway: coat rack, shoe bench, console table, mirror and
a panelled wall. Same letters as room/sprites.py; room/sprites.py adds
HALLWAY_SPRITES to SPRITES.
"""
from room.sprites_kitchen import _canvas, _rounded_box, _rows


def _coat_rack():
    """A wooden coat rack with a pink hat and a mint scarf."""
    c = _canvas(12, 30)
    for y in range(3, 26):
        c[y][4], c[y][5], c[y][6], c[y][7] = "o", "n", "b", "o"
    c[0][5] = c[0][6] = "o"
    for y in (1, 2):
        c[y][4], c[y][5], c[y][6], c[y][7] = "o", "n", "b", "o"
    for x in (2, 3):
        c[5][x] = "o"
    c[4][1] = "o"
    for x in (8, 9):
        c[5][x] = "o"
    c[4][10] = "o"
    hat = _rounded_box(6, 5, 1, "p")
    for y, row in enumerate(hat):
        for x, ch in enumerate(row):
            if ch != ".":
                c[6 + y][x] = ch
    c[7][1] = "l"
    for y in range(6, 18):
        for x in (8, 9, 10):
            edge = x in (8, 10) or y in (6, 17)
            c[y][x] = "o" if edge else ("j" if y % 3 == 0 else "m")
    for x in range(2, 10):
        c[26][x] = c[28][x] = "o"
        c[27][x] = "b"
    c[27][2] = c[27][9] = "o"
    return _rows(c)


def _shoe_bench(width=24):
    """A cream bench with a pink cushion and two pairs of shoes underneath."""
    inner = width - 2
    rows = [
        "o" * width,
        "o" + "l" * inner + "o",
        "o" + "p" * inner + "o",
        "o" + "P" * inner + "o",
        "o" * width,
        "o" + "c" * inner + "o",
        "o" + "C" * inner + "o",
        "o" * width,
    ]
    c = _canvas(width, 6)
    for y in range(5):
        for x, ch in ((1, "o"), (2, "C"), (3, "o"),
                      (width - 4, "o"), (width - 3, "C"), (width - 2, "o")):
            c[y][x] = ch
    for x in range(1, 4):
        c[5][x] = "o"
    for x in range(width - 4, width - 1):
        c[5][x] = "o"
    for x0, color in ((5, "e"), (13, "M")):
        for x in range(x0 + 1, x0 + 6):
            c[2][x] = "o"
        c[3][x0] = c[3][x0 + 6] = "o"
        for x in range(x0 + 1, x0 + 6):
            c[3][x] = color
        c[3][x0 + 3] = "o"  # gap between the two shoes
        for x in range(x0, x0 + 7):
            c[4][x] = "o"
    return rows + _rows(c)


def _console_table(width=26):
    """A slim cream table with a drawer."""
    inner = width - 2
    rows = ["o" * width, "o" + "w" * inner + "o", "o" + "c" * inner + "o",
            "o" + "c" * inner + "o", "o" + "C" * inner + "o", "o" * width]
    front = []
    for y in range(4):
        row = "o"
        for x in range(1, width - 1):
            in_drawer = 6 <= x <= width - 7
            edge = x in (6, width - 7) or y in (0, 3)
            knob = x in (width // 2 - 1, width // 2) and y in (1, 2)
            row += ("y" if knob else "C" if edge else "c") if in_drawer else "c"
        front.append(row + "o")
    legs = []
    for y in range(4):
        row = list("." * width)
        for x0 in (1, width - 4):
            row[x0], row[x0 + 1], row[x0 + 2] = "o", "C" if y < 3 else "o", "o"
        legs.append("".join(row))
    return rows + front + ["o" * width] + legs


def _mirror():
    """An oval mirror in a wooden frame."""
    c = _rounded_box(12, 16, 5, "n")
    glass = _rounded_box(8, 12, 3, "j")
    for y, row in enumerate(glass):
        for x, ch in enumerate(row):
            if ch == "j":
                c[2 + y][2 + x] = "w" if (x + y) in (3, 4) else "j"
            elif ch == "o":
                c[2 + y][2 + x] = "b"
    return _rows(c)


def _panelled_wall_tile(height):
    """Wallpaper on top and wooden panelling below, as tall as the wall."""
    rail = height - 15
    rows = []
    for y in range(height):
        row = ""
        for x in range(8):
            if y < rail:
                row += "5" if (x, y % 6) == (3, 2) else "4"
            elif y == rail:
                row += "o"
            elif y == rail + 1:
                row += "n"
            else:
                row += "b" if x == 7 else "n"
        rows.append(row)
    return rows


def _front_door(width=22, height=27):
    """The front door: a mint door with a window, a wreath and a brass knob,
    in a stone frame with a step in front."""
    c = _canvas(width, height)
    for y in range(height - 2):
        for x in range(width):
            if x in (0, width - 1) or y == 0:
                c[y][x] = "o"
            elif x in (1, 2) or x in (width - 3, width - 2) or y in (1, 2):
                c[y][x] = "T" if x == width - 2 else "t"
    left, right, top = 3, width - 4, 3
    for y in range(top, height - 2):
        for x in range(left, right + 1):
            edge = x in (left, right) or y == top
            c[y][x] = "o" if edge else ("j" if x == left + 1 else "m")
    # window near the top
    for y in range(5, 10):
        for x in range(6, width - 6):
            edge = x in (6, width - 7) or y in (5, 9) or x == width // 2 or y == 7
            c[y][x] = "o" if edge else ("w" if (x, y) == (7, 6) else "j")
    # wreath with a red bow
    cx, cy = width // 2, 14
    for y in range(cy - 3, cy + 4):
        for x in range(cx - 3, cx + 4):
            d = (x - cx + 0.5) ** 2 + (y - cy + 0.5) ** 2
            if 4 <= d <= 12:
                c[y][x] = "G" if (x + y) % 3 == 0 else "g"
    c[cy + 3][cx - 1] = c[cy + 3][cx] = "e"
    c[cy + 2][cx - 2] = c[cy + 2][cx + 1] = "e"
    # lower panels and the knob
    for x0, x1 in ((6, cx - 2), (cx + 1, width - 7)):  # two lower panels
        for y in range(19, height - 4):
            for x in range(x0, x1 + 1):
                if x in (x0, x1) or y in (19, height - 5):
                    c[y][x] = "M"
    c[16][width - 7] = "y"
    for x in range(width):
        c[height - 2][x] = "t" if 0 < x < width - 1 else "o"
        c[height - 1][x] = "o"
    return _rows(c)


LANTERN = [
    "..oo..",
    ".oBBo.",
    "oooooo",
    "oyyyyo",
    "oywyyo",
    "oyyyyo",
    "oooooo",
    ".oBBo.",
    "..oo..",
]


HALLWAY_SPRITES = {
    "front-door": _front_door(),
    "lantern": LANTERN,
    "coat-rack": _coat_rack(),
    "shoe-bench": _shoe_bench(),
    "console-table": _console_table(),
    "mirror": _mirror(),
    "panelled-wall-tile": _panelled_wall_tile(30),
}
