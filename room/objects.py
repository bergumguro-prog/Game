"""The room layout: its size, the player, and every object in the room.

All positions and sizes here are in ART PIXELS. One art pixel is drawn as a
SCALE x SCALE block on screen (see room/sprites.py). (0, 0) is the top-left
corner of the room, including the back wall.

To move or add things, edit OBJECTS below. The page and the collision code
both read from here.
"""
from dataclasses import dataclass

from room import sprites

ROOM_WIDTH = 176
ROOM_HEIGHT = 128
WALL_HEIGHT = 26  # the back wall along the top; the floor starts below it

PLAYER_SPEED = 48           # art pixels per second
PLAYER_START = (82, 66)     # top-left corner of the player sprite
# Only the player's feet collide, so the head can overlap things behind them.
PLAYER_HITBOX = (2, 11, 8, 5)  # (x offset, y offset, width, height)

# How close (in art pixels) the player's feet must be to an object's hitbox
# to interact with it.
INTERACT_REACH = 5

# Layers decide how things are drawn and whether they block the player:
#   "wall"      - hangs on the back wall, never blocks
#   "floor"     - lies flat on the floor (rugs), never blocks
#   "furniture" - stands on the floor and blocks the player
#   "on-top"    - sits on a piece of furniture (set `on`), never blocks
LAYERS = ("wall", "floor", "furniture", "on-top")


@dataclass(frozen=True)
class RoomObject:
    id: str                 # unique name
    sprite: str             # a key in sprites.SPRITES
    x: int
    y: int
    layer: str = "furniture"
    hitbox: tuple = None    # (dx, dy, w, h) inside the sprite; None = all of it
    on: str = None          # for "on-top": the id of the furniture it sits on
    game: str = None        # slug of the mini-game this object opens (press E)
    prompt: str = None      # text shown when near, e.g. "play chess"

    @property
    def size(self):
        return sprites.size(self.sprite)

    @property
    def solid(self):
        return self.layer == "furniture"

    @property
    def hitbox_rect(self):
        """The blocking rectangle in room coordinates: (x, y, w, h)."""
        w, h = self.size
        dx, dy, hw, hh = self.hitbox or (0, 0, w, h)
        return (self.x + dx, self.y + dy, hw, hh)


OBJECTS = [
    # --- On the back wall ---
    RoomObject("wreath", "wreath", 18, 3, layer="wall"),
    RoomObject("window-left", "window", 56, 6, layer="wall"),
    RoomObject("window-right", "window", 78, 6, layer="wall"),
    RoomObject("wall-shelf", "wall-shelf", 102, 13, layer="wall"),
    RoomObject("shelf-plant", "plant-small", 106, 6, layer="wall"),
    RoomObject("shelf-flowers", "flower-pot", 116, 4, layer="wall"),

    # --- Rugs ---
    RoomObject("rug-bed", "rug-bed", 6, 36, layer="floor"),
    RoomObject("doily-top", "doily", 70, 30, layer="floor"),
    RoomObject("rug-tea", "rug-tea", 114, 40, layer="floor"),
    RoomObject("rug-books", "round-rug-small", 22, 74, layer="floor"),
    RoomObject("rug-pink", "rug-pink", 6, 98, layer="floor"),
    RoomObject("doily-door", "doily", 76, 102, layer="floor"),
    RoomObject("rug-round", "round-rug", 130, 104, layer="floor"),

    # --- Bedroom corner ---
    RoomObject("bed", "bed", 12, 16),
    RoomObject("nightstand", "nightstand", 40, 20),
    RoomObject("nightstand-flowers", "flower-pot", 42, 13, layer="on-top", on="nightstand"),

    # --- Game corner ---
    RoomObject("tictactoe-table", "tictactoe-table", 75, 33,
               game="tictactoe", prompt="play tic-tac-toe"),
    RoomObject("pouf-top-pink", "pouf-pink", 62, 40),
    RoomObject("pouf-top-mint", "pouf-mint", 93, 40),

    # --- Poufs ---
    RoomObject("pouf-books", "pouf-mint", 24, 76),
    RoomObject("pouf-corner-pink", "pouf-pink", 12, 104),
    RoomObject("pouf-corner-mint", "pouf-mint", 28, 110),
    RoomObject("pouf-round", "pouf-pink", 137, 109),

    # --- Fireplace corner ---
    RoomObject("fireplace", "fireplace", 134, 14),
    RoomObject("mantel-plant", "plant-small", 138, 7, layer="on-top", on="fireplace"),
    RoomObject("mantel-flowers", "flower-pot", 150, 5, layer="on-top", on="fireplace"),
    RoomObject("plant-fireplace", "plant-big", 163, 18, hitbox=(1, 6, 8, 8)),

    # --- Tea table ---
    RoomObject("bench-left", "bench", 119, 43),
    RoomObject("tea-table", "tea-table", 128, 44,
               game="chess", prompt="play chess"),
    RoomObject("bench-right", "bench", 152, 43),
    RoomObject("cake", "cake", 135, 46, layer="on-top", on="tea-table"),
    RoomObject("teacup", "teacup", 145, 51, layer="on-top", on="tea-table"),

    # --- Reading corner ---
    RoomObject("bookshelf-left", "bookshelf", 6, 62,
               game="hangman", prompt="play hangman"),
    RoomObject("bookshelf-right", "bookshelf", 38, 62),
    RoomObject("plant-books", "plant-big", 56, 100, hitbox=(1, 6, 8, 8)),

    # --- Bottom right ---
    RoomObject("plant-right-a", "plant-big", 124, 76, hitbox=(1, 6, 8, 8)),
    RoomObject("flower-stand", "nightstand", 138, 78),
    RoomObject("flower-stand-pot", "flower-pot", 140, 71, layer="on-top", on="flower-stand"),
    RoomObject("plant-right-b", "plant-big", 156, 76, hitbox=(1, 6, 8, 8)),

    # --- By the door ---
    RoomObject("door-pot-left", "flower-pot", 66, 116),
    RoomObject("door-pot-right", "flower-pot", 102, 116),
]


def z_index(obj, by_id):
    """Drawing order: things lower in the room are drawn in front."""
    if obj.layer == "wall":
        return 2
    if obj.layer == "floor":
        return 1
    if obj.layer == "on-top":
        return z_index(by_id[obj.on], by_id) + 1
    _, h = obj.size
    return 1000 + (obj.y + h) * sprites.SCALE
