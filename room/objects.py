"""Things every room shares: the player's settings and the RoomObject type.

Each room's own layout (size, objects, doors) lives in its file in
room/rooms/. All positions and sizes are in ART PIXELS. One art pixel is
drawn as a SCALE x SCALE block on screen (see room/sprites.py). (0, 0) is
the top-left corner of a room, including the back wall.
"""
from dataclasses import dataclass

from room import sprites

PLAYER_SPEED = 48           # art pixels per second
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
