"""Room 2 (name to be decided). Empty for now."""
from room.world import Exit, Room

room = Room(
    id="room2",
    name="Room 2",
    width=160,
    height=120,
    wall_height=26,
    start=(74, 66),
    objects=[],
    exits=[
        Exit("to-main", "top", 72, to_room="main", to_exit="to-room2"),
        Exit("to-room3", "right", 70, to_room="room3", to_exit="to-room2"),
    ],
)
