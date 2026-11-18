"""Room 3 (name to be decided): a music and card room.

The piano and the card table open "coming soon" until their games exist.
To make one real, create games/<slug>/ with the same slug (for example
games/cards/ with slug = "cards"); nothing here has to change.
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- Games (coming soon) ---
    RoomObject("piano", "piano", 96, 12, hitbox=(0, 12, 30, 9),
               game="piano", prompt="play piano"),
    RoomObject("card-table", "card-table", 58, 62, hitbox=(0, 2, 26, 16),
               game="cards", prompt="play cards"),
    RoomObject("card-pouf-left", "pouf-pink", 45, 68),
    RoomObject("card-pouf-right", "pouf-pink", 87, 68),
]

room = Room(
    id="room3",
    name="Room 3",
    width=144,
    height=112,
    wall_height=26,
    start=(64, 88),
    objects=OBJECTS,
    exits=[
        Exit("to-room2", "left", 62, to_room="room2", to_exit="to-room3"),
    ],
)
