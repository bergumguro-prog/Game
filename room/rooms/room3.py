"""Room 3 (name to be decided). Empty for now."""
from room.world import Exit, Room

room = Room(
    id="room3",
    name="Room 3",
    width=144,
    height=112,
    wall_height=26,
    start=(66, 60),
    objects=[],
    exits=[
        Exit("to-room2", "left", 62, to_room="room2", to_exit="to-room3"),
    ],
)
