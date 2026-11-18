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

DEFAULT_ROOM = "main"  # where a new player starts


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
