"""Pixel-art suit symbols and the bow on the card backs, added to the
shared sprite collection (room.sprites.SPRITES)."""
from room import sprites

HEART = [
    ".oo.oo.",
    "oeeoeeo",
    "oeeeeeo",
    "oeeeeeo",
    ".oeeeo.",
    "..oeo..",
    "...o...",
]

DIAMOND = [
    "...o...",
    "..oeo..",
    ".oeeeo.",
    "oeeeeeo",
    ".oeeeo.",
    "..oeo..",
    "...o...",
]

SPADE = [
    "...o...",
    "..ooo..",
    ".ooooo.",
    "ooooooo",
    "ooooooo",
    ".o.o.o.",
    "..ooo..",
]

CLUB = [
    "..ooo..",
    "..ooo..",
    "oo.o.oo",
    "ooooooo",
    "oo.o.oo",
    "...o...",
    "..ooo..",
]

BOW = [
    ".oo.....oo.",
    "orro...orro",
    "orrrooorrro",
    "orrroeorrro",
    "orrrooorrro",
    "orro.o.orro",
    ".oo.o.o.oo.",
    "....o.o....",
]

SUIT_SPRITES = {"H": "suit-heart", "D": "suit-diamond", "C": "suit-club", "S": "suit-spade"}

sprites.SPRITES.update({
    "suit-heart": HEART,
    "suit-diamond": DIAMOND,
    "suit-club": CLUB,
    "suit-spade": SPADE,
    "card-bow": BOW,
})
