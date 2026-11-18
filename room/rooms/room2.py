"""Room 2 (name to be decided): a game room.

The arcade cabinet and the puzzle desk open "coming soon" until their games
exist. To make one real, create games/<slug>/ with the same slug (for
example games/arcade/ with slug = "arcade"); nothing here has to change.
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- On the back wall ---
    RoomObject("window-left", "window", 42, 6, layer="wall"),
    RoomObject("window-right", "window", 101, 6, layer="wall"),
    RoomObject("hanging-plant-left", "hanging-plant", 62, 0, layer="wall"),
    RoomObject("hanging-plant-right", "hanging-plant", 90, 0, layer="wall"),
    RoomObject("wall-shelf", "wall-shelf", 128, 13, layer="wall"),
    RoomObject("shelf-plant", "plant-small", 132, 6, layer="wall"),
    RoomObject("shelf-flowers", "flower-pot", 142, 4, layer="wall"),

    # --- Rugs and doormats ---
    RoomObject("mat-door", "mat-mint", 70, 27, layer="floor"),
    RoomObject("mat-side-door", "mat-mint-side", 152, 68, layer="floor"),
    RoomObject("rug-puzzle", "rug-mint", 96, 32, layer="floor"),
    RoomObject("rug-round", "round-rug-mint", 40, 72, layer="floor"),

    # --- Plants ---
    RoomObject("plant-top-left", "plant-big", 4, 26, hitbox=(1, 6, 8, 8)),
    RoomObject("plant-top-right", "plant-big", 146, 28, hitbox=(1, 6, 8, 8)),
    RoomObject("plant-bottom-left", "plant-big", 4, 102, hitbox=(1, 6, 8, 8)),
    RoomObject("pot-bottom-right", "flower-pot", 146, 108),

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
    theme="room2",
    floor_tile="plank-tile",
    wall_tile="wallpaper-flowers",
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
