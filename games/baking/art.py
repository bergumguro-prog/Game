"""Pixel art for the baking game: ingredient icons (12x12).

Most ingredients share a few shapes (a sack, a jar, a box, a tin) in their
own colors; a few are drawn on their own. They're added to
room.sprites.SPRITES as "ing-<id>".
"""
from room import sprites


def _recolor(rows, mapping):
    table = str.maketrans(mapping)
    return [row.translate(table) for row in rows]


# Shapes. Letters X (body), L (label) and T (label text) are swapped for
# real colors below.
SACK = [
    "............",
    "....oooo....",
    ".....oo.....",
    "...oooooo...",
    "..oXXXXXXo..",
    ".oXXXXXXXXo.",
    ".oXLLLLLLXo.",
    ".oXLTTTTLXo.",
    ".oXLLLLLLXo.",
    ".oXXXXXXXXo.",
    ".oTTTTTTTTo.",
    "..oooooooo..",
]

JAR = [
    "............",
    "..oooooooo..",
    "..oLLLLLLo..",
    "..oooooooo..",
    ".owXXXXXXXo.",
    ".owXXXXXXXo.",
    ".oXXwwwwXXo.",
    ".oXXwTTwXXo.",
    ".oXXwwwwXXo.",
    ".oXXXXXXXXo.",
    ".oXXXXXXXXo.",
    "..oooooooo..",
]

BOX = [
    "..oooooooo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oLLLLLLo..",
    "..oLTTTTLo..",
    "..oLLLLLLo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oTTTTTTo..",
    "..oooooooo..",
]

TIN = [
    "............",
    "..oooooooo..",
    "..okkkkkko..",
    "..oooooooo..",
    "..oXXXXXXo..",
    "..oXLLLLXo..",
    "..oXLTTLXo..",
    "..oXLLLLXo..",
    "..oXXXXXXo..",
    "..oXXXXXXo..",
    "..oTTTTTTo..",
    "..oooooooo..",
]

MILK = [
    "...oooooo...",
    "..ojjjjjjo..",
    ".ojjjjjjjjo.",
    ".oooooooooo.",
    ".owwwwwwwwo.",
    ".owmmmmmmwo.",
    ".owmwwwwmwo.",
    ".owmmmmmmwo.",
    ".owwwwwwwwo.",
    ".owwwwwwwwo.",
    ".oCCCCCCCCo.",
    ".oooooooooo.",
]

EGGS = [
    "............",
    "............",
    "............",
    ".oo..oo..oo.",
    "occooccoocco",
    "occooccoocco",
    "oooooooooooo",
    "oppppppppppo",
    "opllpllpllpo",
    "oppppppppppo",
    "oPPPPPPPPPPo",
    "oooooooooooo",
]

BUTTER = [
    "............",
    "............",
    "............",
    "............",
    ".oooooooooo.",
    ".oyyyyyyyyo.",
    ".oyyyyyyyyo.",
    ".oooooooooo.",
    ".owwwwwwwwo.",
    ".owppwwppwo.",
    ".owwwwwwwwo.",
    ".oooooooooo.",
]

BLUEBERRIES = [
    "............",
    "............",
    "............",
    "..oo.oo.oo..",
    ".oVVoVVoVVo.",
    ".oVvoVvoVvo.",
    "oooooooooooo",
    "ojjjjjjjjjjo",
    "ojmjmjmjmjmo",
    "ojjjjjjjjjjo",
    "oMMMMMMMMMMo",
    "oooooooooooo",
]

CHEESE = [
    "............",
    "............",
    "............",
    "............",
    "............",
    "..ooooooooo.",
    ".oyyyyyyyyo.",
    "ooooooooooo.",
    "oynyyyynyyo.",
    "oyyyynyyyyo.",
    "oyynyyyyyno.",
    "ooooooooooo.",
]

CARROTS = [
    "....o.o.o...",
    "....ogogo...",
    ".....oGo....",
    "....offfo...",
    "....offfo...",
    "....ofnfo...",
    "....offfo...",
    ".....offo...",
    ".....ofno...",
    ".....ofo....",
    "......o.....",
    "............",
]

SALT = [
    "............",
    "....oooo....",
    "...okkkko...",
    "...okokko...",
    "...oooooo...",
    "...owwwwo...",
    "..owwwwwwo..",
    "..owwwwwwo..",
    "..owwwwwwo..",
    "..owwwwwwo..",
    "..oCCCCCCo..",
    "..oooooooo..",
]

ICONS = {
    "milk": MILK,
    "eggs": EGGS,
    "butter": BUTTER,
    "blueberries": BLUEBERRIES,
    "cheese": CHEESE,
    "jam": _recolor(JAR, {"X": "e", "L": "P", "T": "p"}),
    "carrots": CARROTS,
    "pickles": _recolor(JAR, {"X": "g", "L": "n", "T": "G"}),
    "flour": _recolor(SACK, {"X": "c", "L": "w", "T": "C"}),
    "sugar": _recolor(SACK, {"X": "w", "L": "l", "T": "p"}),
    "baking-powder": _recolor(TIN, {"X": "m", "L": "w", "T": "p"}),
    "salt": SALT,
    "rice": _recolor(BOX, {"X": "w", "L": "m", "T": "M"}),
    "pasta": _recolor(BOX, {"X": "y", "L": "e", "T": "w"}),
    "cocoa": _recolor(TIN, {"X": "b", "L": "c", "T": "B"}),
    "oats": _recolor(BOX, {"X": "n", "L": "c", "T": "b"}),
}

sprites.SPRITES.update({f"ing-{name}": rows for name, rows in ICONS.items()})
