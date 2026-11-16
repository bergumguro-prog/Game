"""The room layout: its size, where the player starts, and all furniture.

All positions and sizes are in pixels, measured from the top-left corner of
the floor. To move or add furniture, edit OBJECTS below - the page and the
collision code both read from here.
"""
from dataclasses import dataclass

ROOM_WIDTH = 640
ROOM_HEIGHT = 448

PLAYER_SIZE = 28         # the player is a square hitbox of this size
PLAYER_SPEED = 180       # pixels per second
PLAYER_START = (306, 300)  # (x, y) of the player's top-left corner


@dataclass(frozen=True)
class RoomObject:
    id: str          # unique name, also used as a CSS class (.object-<id>)
    label: str       # text shown on the object
    x: int
    y: int
    width: int
    height: int
    solid: bool = True  # solid objects block the player; rugs etc. don't


OBJECTS = [
    RoomObject("bed",       "Bed",       x=24,  y=24,  width=110, height=160),
    RoomObject("nightstand", "",         x=142, y=24,  width=44,  height=44),
    RoomObject("bookshelf", "Bookshelf", x=250, y=0,   width=150, height=48),
    RoomObject("desk",      "Desk",      x=480, y=24,  width=136, height=72),
    RoomObject("chair",     "",          x=530, y=104, width=36,  height=36),
    RoomObject("table",     "Table",     x=420, y=250, width=120, height=80),
    RoomObject("plant",     "",          x=24,  y=384, width=40,  height=40),
    RoomObject("rug",       "",          x=220, y=200, width=200, height=140, solid=False),
]
