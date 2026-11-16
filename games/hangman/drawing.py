"""The hangman picture, drawn as pixel art for each number of wrong guesses.

The gallows is always there; each wrong guess adds one part in this order:
head, body, left arm, right arm, left leg, right leg.

The pictures are generated with a few drawing helpers (rectangles, lines,
a circle) on a grid of letters, then outlined automatically and registered
in room.sprites.SPRITES as "hangman-0" ... "hangman-6".
"""
from room import sprites

WIDTH, HEIGHT = 36, 44
PARTS = ("head", "body", "left arm", "right arm", "left leg", "right leg")


class Canvas:
    def __init__(self):
        self.grid = [["."] * WIDTH for _ in range(HEIGHT)]

    def dot(self, x, y, ch):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.grid[y][x] = ch

    def rect(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.dot(x, y, ch)

    def line(self, x0, y0, x1, y1, ch, thickness=2):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            self.rect(x, y, x + thickness - 1, y + thickness - 1, ch)

    def disc(self, cx, cy, r, ch):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    self.dot(x, y, ch)

    def outlined(self):
        """Rows as strings, with an outline around every filled shape."""
        def filled(x, y):
            return 0 <= x < WIDTH and 0 <= y < HEIGHT and self.grid[y][x] not in ".o"

        rows = []
        for y in range(HEIGHT):
            row = ""
            for x in range(WIDTH):
                ch = self.grid[y][x]
                if ch == "." and any(filled(x + dx, y + dy)
                                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    ch = "o"
                row += ch
            rows.append(row)
        return rows


def picture(wrong):
    """Pixel rows for the picture after `wrong` wrong guesses (0-6)."""
    c = Canvas()
    # Gallows: base, post, top beam, little brace, rope.
    c.rect(2, 40, 33, 42, "b")
    c.rect(2, 42, 33, 42, "B")
    c.rect(6, 2, 9, 39, "b")
    c.rect(9, 2, 9, 39, "B")
    c.rect(6, 2, 26, 4, "b")
    c.rect(10, 4, 26, 4, "B")
    c.line(10, 10, 15, 5, "b")
    c.rect(24, 5, 25, 10, "C")

    if wrong >= 1:  # head with hair and a little bow
        c.disc(25, 15, 4.6, "s")
        c.rect(21, 10, 29, 12, "h")
        c.rect(28, 10, 30, 11, "r")
        c.dot(23, 15, "o")
        c.dot(27, 15, "o")
    if wrong >= 2:  # body: a pink dress
        c.rect(23, 20, 27, 22, "p")
        c.rect(22, 23, 28, 29, "p")
        c.rect(22, 29, 28, 29, "P")
    if wrong >= 3:
        c.line(21, 21, 17, 26, "s")
    if wrong >= 4:
        c.line(28, 21, 32, 26, "s")
    if wrong >= 5:
        c.line(23, 31, 21, 37, "s")
    if wrong >= 6:
        c.line(26, 31, 28, 37, "s")
    return c.outlined()


for _wrong in range(len(PARTS) + 1):
    sprites.SPRITES[f"hangman-{_wrong}"] = picture(_wrong)
