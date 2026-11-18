"""The world: every room in the game and how to find them.

Each room is one file in room/rooms/ that defines `room = Room(...)`.
Rooms are found automatically, the same way mini-games are found in games/,
so adding a room never needs changes to the routes, the JavaScript or app.py.

All positions and sizes are in ART PIXELS (see room/objects.py).
"""
import importlib
import pkgutil
from dataclasses import dataclass, field
from functools import lru_cache

from room import objects, sprites

DEFAULT_ROOM = "main"  # where a new player starts

# --- Doors -----------------------------------------------------------------

SIDES = ("top", "bottom", "left", "right")
DOOR_WIDTH = 16  # how wide a doorway is, along its wall
DOOR_DEPTH = 3   # how far into the room the "walk into me" area reaches

# Which way the player walks to go through a door on each side, and which
# way they face when they come in through it.
WALK_DIRECTION = {"top": "up", "bottom": "down", "left": "left", "right": "right"}
ARRIVE_FACING = {"top": "down", "bottom": "up", "left": "right", "right": "left"}


@dataclass(frozen=True)
class Exit:
    """A door in one of the room's walls that leads to a door in another room.

        Exit("to-room2", "bottom", 80, to_room="room2", to_exit="to-main")

    `at` is where along the wall the doorway starts: its x for a door in the
    top (back) or bottom wall, its y for a door in the left or right wall.
    The door on the other side must point back to this one.
    """
    id: str
    side: str          # "top", "bottom", "left" or "right"
    at: int
    to_room: str
    to_exit: str

    @property
    def url(self):
        return f"/rooms/{self.to_room}?via={self.to_exit}"

    def trigger_rect(self, room):
        """Where the player's feet must be (while walking toward the door)
        to go through it: (x, y, w, h)."""
        inner = DOOR_WIDTH - 4  # a little narrower than the doorway
        if self.side == "top":
            return (self.at + 2, room.wall_height, inner, DOOR_DEPTH)
        if self.side == "bottom":
            return (self.at + 2, room.height - DOOR_DEPTH, inner, DOOR_DEPTH)
        if self.side == "left":
            return (0, self.at + 2, DOOR_DEPTH, inner)
        return (room.width - DOOR_DEPTH, self.at + 2, DOOR_DEPTH, inner)

    def arrival(self, room):
        """Where the player appears when coming in through this door:
        (x, y, facing), just in front of it so they don't walk straight back."""
        fx, fy, fw, fh = objects.PLAYER_HITBOX
        middle = self.at + DOOR_WIDTH // 2
        if self.side == "top":
            feet = (middle - fw // 2, room.wall_height + DOOR_DEPTH + 1)
        elif self.side == "bottom":
            feet = (middle - fw // 2, room.height - DOOR_DEPTH - 1 - fh)
        elif self.side == "left":
            feet = (DOOR_DEPTH + 1, middle - fh // 2)
        else:
            feet = (room.width - DOOR_DEPTH - 1 - fw, middle - fh // 2)
        return (feet[0] - fx, feet[1] - fy, ARRIVE_FACING[self.side])

    def sprite_position(self, room):
        """Top-left of the door's sprite. Doors in the back wall stand on the
        floor line; the others sit on the room's edge, over its outline."""
        if self.side == "top":
            return (self.at, room.wall_height - sprites.size("door-top")[1] + 1)
        if self.side == "bottom":
            return (self.at - 1, room.height - 2)
        if self.side == "left":
            return (-3, self.at - 1)
        return (room.width - 2, self.at - 1)


# --- Rooms -----------------------------------------------------------------


@dataclass(frozen=True)
class Room:
    id: str                  # used in the URL: /rooms/<id>
    name: str                # shown in the browser tab
    width: int               # size of the whole room, back wall included
    height: int
    wall_height: int         # the back wall along the top; the floor starts below it
    start: tuple             # (x, y) top-left of the player when nothing else says where
    objects: list = field(default_factory=list)  # RoomObjects (room/objects.py)
    exits: list = field(default_factory=list)    # doors to other rooms
    theme: str = "main"      # picks the room's colors in theme.css (data-room-theme)
    floor_tile: str = "floor-tile"         # sprite repeated over the floor
    wall_tile: str = "wallpaper-tile"      # sprite repeated over the back wall

    @property
    def floor_height(self):
        return self.height - self.wall_height

    def exit(self, exit_id):
        """The exit with this id, or None."""
        return next((e for e in self.exits if e.id == exit_id), None)


@lru_cache(maxsize=None)
def rooms():
    """Every room, by id. Imports each module in room/rooms/ and collects its
    `room` (only once; later calls reuse the result)."""
    from room import rooms as package

    found = {}
    for info in sorted(pkgutil.iter_modules(package.__path__), key=lambda i: i.name):
        module = importlib.import_module(f"room.rooms.{info.name}")
        room = module.room
        if room.id in found:
            raise ValueError(f"two rooms use the id {room.id!r}")
        found[room.id] = room
    return found


def get(room_id):
    """The room with this id, or None."""
    return rooms().get(room_id)
