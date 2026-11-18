"""Room 2 (name to be decided): a game room.

The arcade cabinet and the puzzle desk open "coming soon" until their games
exist. To make one real, create games/<slug>/ with the same slug (for
example games/arcade/ with slug = "arcade"); nothing here has to change.
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- Games (coming soon) ---
    RoomObject("arcade", "arcade", 20, 10, hitbox=(0, 14, 16, 10),
               game="arcade", prompt="play arcade games"),
    RoomObject("puzzle-desk", "puzzle-desk", 104, 36,
               game="puzzles", prompt="play puzzles"),
    RoomObject("puzzle-pouf", "pouf-mint", 111, 54),
]

room = Room(
    id="room2",
    name="Room 2",
    width=160,
    height=120,
    wall_height=26,
    start=(74, 66),
    objects=OBJECTS,
    exits=[
        Exit("to-main", "top", 72, to_room="main", to_exit="to-room2"),
        Exit("to-room3", "right", 70, to_room="room3", to_exit="to-room2"),
    ],
)
