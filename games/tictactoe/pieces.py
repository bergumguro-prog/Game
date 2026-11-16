"""Pixel-art X and O pieces, added to the shared sprite collection.

They're generated from simple shapes and outlined automatically, then
registered in room.sprites.SPRITES so sprites.render() can draw them.
"""
from room import sprites

SIZE = 12


def _outlined(inside, fill):
    """Grid where pixels with inside(x, y) get `fill`, with an outline around them."""
    def filled(x, y):
        return 0 <= x < SIZE and 0 <= y < SIZE and inside(x, y)

    rows = []
    for y in range(SIZE):
        row = ""
        for x in range(SIZE):
            if filled(x, y):
                row += fill
            elif any(filled(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                row += "o"
            else:
                row += "."
        rows.append(row)
    return rows


def _in_x(x, y):
    # two thick diagonals, kept away from the edge so the outline fits
    inner = 1 <= x <= SIZE - 2 and 1 <= y <= SIZE - 2
    return inner and (abs(x - y) <= 1 or abs(x + y - (SIZE - 1)) <= 1)


def _in_o(x, y):
    c = (SIZE - 1) / 2
    d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5
    return 2.6 <= d <= 4.6


sprites.SPRITES["tictactoe-x"] = _outlined(_in_x, "r")
sprites.SPRITES["tictactoe-o"] = _outlined(_in_o, "m")
