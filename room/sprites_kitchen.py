"""Pixel art for the kitchen: counters, sink, stove, fridge, pantry, table.

Same letters as room/sprites.py (see PALETTE there). Most pieces are built
by small functions on a grid ("canvas") so their sizes are easy to change.
room/sprites.py adds KITCHEN_SPRITES to SPRITES.
"""


def _canvas(width, height, fill="."):
    return [[fill] * width for _ in range(height)]


def _rows(canvas):
    return ["".join(row) for row in canvas]


def _rounded_box(width, height, radius, color, outline="o"):
    """A filled box with rounded corners and an outline."""
    c = _canvas(width, height)

    def inside(x, y):
        cx = min(max(x, radius), width - 1 - radius)
        cy = min(max(y, radius), height - 1 - radius)
        return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2 + 0.5

    for y in range(height):
        for x in range(width):
            if inside(x, y):
                edge = any(not (0 <= nx < width and 0 <= ny < height and inside(nx, ny))
                           for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
                c[y][x] = outline if edge else color
    return c


# --- Counters ----------------------------------------------------------------
# Every counter piece is 24 rows tall: 4 rows above the worktop (for a tap or
# the stove's knobs), the cream worktop, then pink cupboard doors.

COUNTER_HEIGHT = 24


def _counter_base(width):
    c = _canvas(width, COUNTER_HEIGHT)
    for x in range(width):
        c[4][x] = c[11][x] = c[23][x] = "o"
    for y in range(5, 23):
        c[y][0] = c[y][width - 1] = "o"
    for y in range(5, 10):
        for x in range(1, width - 1):
            c[y][x] = "w" if y == 5 else "c"
    for x in range(1, width - 1):
        c[10][x] = "C"
        c[22][x] = "P"
    # cupboard doors, about 11 pixels wide each
    inner = width - 2
    doors = max(1, round(inner / 11))
    door_w = inner / doors
    for y in range(12, 22):
        for x in range(1, width - 1):
            lx = (x - 1) % door_w
            edge = lx < 1 or lx >= door_w - 1 or y in (12, 21)
            c[y][x] = "P" if edge else "p"
    for d in range(doors):
        knob_x = int(1 + d * door_w + (door_w - 3 if d % 2 == 0 else 2))
        c[16][knob_x] = "y"
    return c


def _counter(width):
    return _rows(_counter_base(width))


def _sink(width=24):
    """A counter with a stone basin, a little water and a tap."""
    c = _counter_base(width)
    for y in range(6, 10):
        for x in range(4, width - 4):
            edge = x in (4, width - 5) or y == 6
            c[y][x] = "o" if edge else ("T" if y == 7 else "j")
    c[8][7] = c[9][width - 8] = "w"  # shine on the water
    tap = width // 2 - 1
    for x in range(tap - 1, tap + 3):
        c[0][x] = "o"
    c[1][tap - 1], c[1][tap], c[1][tap + 1], c[1][tap + 2] = "o", "w", "w", "o"
    for y in (2, 3, 4, 5):
        c[y][tap - 1], c[y][tap], c[y][tap + 1] = "o", "w", "o"
    c[6][tap] = "w"
    return _rows(c)


def _stove(width=24):
    """A cream stove: knobs at the back, two burners, an oven door with a window."""
    c = _counter_base(width)
    for x in range(width):
        c[0][x] = "o"
    for y in (1, 2, 3):
        c[y][0] = c[y][width - 1] = "o"
        for x in range(1, width - 1):
            c[y][x] = "c"
    for kx in (4, 9, 14, 19):
        if kx < width - 1:
            c[2][kx] = "P"
    for y in range(5, 10):
        for x in range(1, width - 1):
            c[y][x] = "T" if y > 5 else "t"
    for bx in (width // 4, 3 * width // 4 - 1):
        for dx, dy in ((-2, 0), (2, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            c[7 + dy][bx + dx] = "o"
        c[7][bx] = "B"
    # oven door instead of cupboards
    for y in range(12, 22):
        for x in range(1, width - 1):
            c[y][x] = "c"
    for x in range(3, width - 3):
        c[13][x] = "w"  # handle
    for y in range(15, 21):
        for x in range(4, width - 4):
            edge = x in (4, width - 5) or y in (15, 20)
            c[y][x] = "o" if edge else ("f" if y == 19 else "B")
    for x in range(1, width - 1):
        c[22][x] = "C"
    return _rows(c)


# --- Tall furniture ------------------------------------------------------------

def _fridge(width=20, height=38):
    """A rounded retro fridge in mint, with a heart magnet and a note."""
    c = _rounded_box(width, height - 2, 3, "m")
    for y in range(1, height - 3):
        for x in range(1, width - 1):
            if c[y][x] == "m":
                if x <= 2:
                    c[y][x] = "j"
                elif x >= width - 3:
                    c[y][x] = "M"
    for x in range(1, width - 1):
        c[11][x] = "o"  # gap between freezer and fridge doors
        c[12][x] = "M"
    for y in list(range(4, 9)) + list(range(15, 26)):
        c[y][width - 5] = "w"
        c[y][width - 4] = "o"
    c[18][5], c[18][7] = "r", "r"  # heart magnet
    c[19][5], c[19][6], c[19][7] = "r", "r", "r"
    c[20][6] = "r"
    for y in range(22, 27):
        for x in range(4, 10):
            c[y][x] = "o" if y in (22, 26) or x in (4, 9) else "c"
    c[24][6] = c[24][7] = "C"
    gap = "." * (width - 8)
    return _rows(c) + [".oBo" + gap + "oBo.", ".ooo" + gap + "ooo."]


def _pantry(width=24, height=38):
    """A tall cream pantry cupboard: glass doors on top with jars inside,
    solid doors below."""
    c = _canvas(width, height)
    for y in range(height):
        for x in range(width):
            if y in (0, height - 1) or x in (0, width - 1):
                c[y][x] = "o"
            elif y <= 2:
                c[y][x] = "n" if y == 1 else "b"   # wooden crown
            elif y == 3:
                c[y][x] = "o"
            else:
                c[y][x] = "C" if x == width - 2 else "c"
    half = width // 2
    jar_colors = "yegvrjy"
    for door, x0 in enumerate((2, half + 1)):
        x1 = x0 + half - 4
        # glass doors with two shelves of jars
        for y in range(5, 20):
            for x in range(x0, x1 + 1):
                edge = x in (x0, x1) or y in (5, 19)
                c[y][x] = "o" if edge else "u"
        for shelf_y in (11, 18):
            for x in range(x0 + 1, x1):
                c[shelf_y][x] = "n"
            for i, jx in enumerate(range(x0 + 2, x1 - 1, 3)):
                color = jar_colors[(i + door * 2 + shelf_y) % len(jar_colors)]
                c[shelf_y - 1][jx] = c[shelf_y - 2][jx] = color
                c[shelf_y - 3][jx] = "o"
        # solid doors below
        for y in range(22, height - 3):
            for x in range(x0, x1 + 1):
                edge = x in (x0, x1) or y in (22, height - 4)
                c[y][x] = "C" if edge else "c"
        knob_x = x1 - 1 if door == 0 else x0 + 1
        c[27][knob_x] = "P"
        c[12][knob_x] = "P"
    for x in range(1, width - 1):
        c[height - 2][x] = "C"
    return _rows(c)


def _pantry_wall(width=18, height=96):
    """Open pantry shelves along a side wall, seen from above: a wooden
    frame with shelves, and on them jars (colored lids), flour sacks and
    little boxes. The front edge (toward the room) is on the left."""
    c = _canvas(width, height)
    for y in range(height):
        for x in range(width):
            if x in (0, width - 1) or y in (0, height - 1):
                c[y][x] = "o"
            elif x in (1, 2):
                c[y][x] = "b" if x == 1 else "B"       # the front edge
            elif x == width - 2:
                c[y][x] = "B"                          # against the wall
            else:
                c[y][x] = "n"                          # shelf boards
    for y in range(24, height - 1, 24):                # the shelf sections
        for x in range(1, width - 1):
            c[y][x] = "o"
            if y + 1 < height - 1:
                c[y + 1][x] = "b"

    def jar(x0, y0, lid):
        for dy, row in enumerate([".ooo.", "o" + lid * 3 + "o", "o" + lid + "w" + lid + "o",
                                  "o" + lid * 3 + "o", ".ooo."]):
            for dx, ch in enumerate(row):
                if ch != ".":
                    c[y0 + dy][x0 + dx] = ch

    def sack(x0, y0):
        for dy, row in enumerate(["..oo..", ".occo.", "occcco", "ocCcco", "occcco", ".oooo."]):
            for dx, ch in enumerate(row):
                if ch != ".":
                    c[y0 + dy][x0 + dx] = ch

    def box(x0, y0, color):
        for dy, row in enumerate(["ooooo", "o" + color * 3 + "o", "o" + color + "w" + color + "o",
                                  "o" + color * 3 + "o", "ooooo"]):
            for dx, ch in enumerate(row):
                c[y0 + dy][x0 + dx] = ch

    # what's on each shelf (fixed, so the art always looks the same)
    jar(4, 3, "e"); jar(10, 3, "y"); sack(5, 10); box(11, 13, "m"); jar(4, 17, "P")
    sack(4, 28); jar(11, 28, "g"); box(4, 37, "p"); jar(10, 37, "v"); jar(6, 43, "y")
    jar(4, 52, "M"); jar(10, 52, "e"); sack(10, 59); box(4, 61, "y")
    box(5, 76, "m"); jar(11, 76, "P"); sack(4, 84); jar(11, 86, "y")
    return _rows(c)


# --- Table and chairs ----------------------------------------------------------

def _kitchen_table(width=40):
    """A wooden kitchen table seen from above, with legs at the front."""
    inner = width - 2
    rows = ["o" * width]
    for y in range(12):
        plank = "b" if y in (4, 8) else "n"
        rows.append("o" + plank * inner + "o")
    rows += [
        "o" + "b" * inner + "o",
        "o" + "B" * inner + "o",
        "o" * width,
    ]
    leg = ".oBo" + "." * (width - 8) + "oBo."
    rows += [leg] * 4 + [".ooo" + "." * (width - 8) + "ooo."]
    return rows


CHAIR = [
    ".oooooooo.",
    ".onnnnnno.",
    ".obbbbbbo.",
    ".oooooooo.",
    "..ob..bo..",
    "..ob..bo..",
    "oooooooooo",
    "oppppppppo",
    "olpppppppo",
    "oPPPPPPPPo",
    "oooooooooo",
    ".ob....bo.",
    ".ob....bo.",
    ".oo....oo.",
]


# --- On the walls --------------------------------------------------------------

def _pan_rail(width=28):
    """A wooden rail with copper pans and a ladle hanging from it."""
    c = _canvas(width, 13)
    for x in range(width):
        c[0][x] = c[2][x] = "o"
        c[1][x] = "n"
    c[1][0] = c[1][width - 1] = "o"

    def pan(cx, top, r):
        for y in range(3, top):
            c[y][cx] = "o"  # hook / handle
        cy = top + r
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if d <= r * r + 0.5:
                    inner = d <= (r - 1) ** 2 + 0.5
                    c[y][x] = ("n" if (x - cx) < 0 and (y - cy) < 0 else "b") if inner else "o"

    pan(5, 5, 3)
    pan(20, 4, 4)
    for y in range(3, 9):
        c[y][12] = "o"
        c[y][13] = "C"
    for x in range(11, 15):
        c[9][x] = "o"
    c[10][11], c[10][12], c[10][13], c[10][14] = "o", "T", "T", "o"
    c[11][12] = c[11][13] = "o"
    return _rows(c)


def _jar(color):
    return [
        ".oooo.",
        "oPPPPo",
        "oooooo",
        "ow" + color * 3 + "o",
        "o" + color * 4 + "o",
        "o" + color * 4 + "o",
        ".oooo.",
    ]


# --- Floor and wall patterns -------------------------------------------------

def _kitchen_floor_tile(size=12):
    """Big square tiles in two soft shades with grout lines."""
    rows = []
    for y in range(2 * size):
        row = ""
        for x in range(2 * size):
            if x % size == size - 1 or y % size == size - 1:
                row += "3"
            else:
                row += "2" if (x // size + y // size) % 2 else "1"
        rows.append(row)
    return rows


def _subway_tile():
    """Wall tiles laid like bricks."""
    rows = []
    for y in range(8):
        band, line = divmod(y, 4)
        seam = 7 if band == 0 else 3
        rows.append("".join("5" if line == 3 or x == seam else "4" for x in range(8)))
    return rows


KITCHEN_SPRITES = {
    "counter": _counter(24),
    "counter-short": _counter(16),
    "sink": _sink(),
    "stove": _stove(),
    "fridge": _fridge(),
    "pantry": _pantry(),
    "pantry-wall": _pantry_wall(),
    "kitchen-table": _kitchen_table(),
    "chair": CHAIR,
    "pan-rail": _pan_rail(),
    "jar-honey": _jar("y"),
    "jar-jam": _jar("e"),
    "jar-pickles": _jar("g"),
    "kitchen-floor-tile": _kitchen_floor_tile(),
    "subway-tile": _subway_tile(),
}
