"""The hallway: the middle of the house.

Doors: left to the bedroom, right to the living room, bottom to the kitchen,
and the front door at the top.

The front door is locked because there is no outside yet. To open it:
make room/rooms/outside.py with a door back, e.g.
    Exit("to-hallway", "bottom", 80, to_room="hallway", to_exit="to-outside")
and give the front door below `to_room="outside", to_exit="to-hallway"`.
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- On the back wall ---
    RoomObject("picture", "picture", 10, 7, layer="wall"),
    RoomObject("lantern-left", "lantern", 46, 9, layer="wall"),
    RoomObject("lantern-right", "lantern", 76, 9, layer="wall"),
    RoomObject("mirror", "mirror", 99, 3, layer="wall"),

    # --- Rugs and doormats ---
    RoomObject("runner", "runner", 55, 32, layer="floor"),
    RoomObject("mat-left-door", "mat-pink-side", 1, 58, layer="floor"),
    RoomObject("mat-right-door", "mat-pink-side", 120, 58, layer="floor"),

    # --- Furniture ---
    RoomObject("shoe-bench", "shoe-bench", 6, 22, hitbox=(0, 4, 24, 10)),
    RoomObject("coat-rack", "coat-rack", 34, 6, hitbox=(2, 25, 8, 4)),
    RoomObject("console-table", "console-table", 92, 20, hitbox=(0, 5, 26, 11)),
    RoomObject("console-flowers", "flower-pot", 101, 13, layer="on-top", on="console-table"),

    # --- Flowers ---
    RoomObject("tulips-bottom-left", "flowers-tulips", 4, 94, hitbox=(1, 6, 8, 8)),
    RoomObject("daisies-bottom-right", "flowers-daisies", 114, 94, hitbox=(1, 6, 8, 8)),
]

room = Room(
    id="hallway",
    name="Hallway",
    theme="hallway",
    floor_tile="plank-tile",
    wall_tile="panelled-wall-tile",
    width=128,
    height=112,
    wall_height=30,
    start=(58, 70),
    objects=OBJECTS,
    exits=[
        Exit("to-bedroom", "left", 60, to_room="bedroom", to_exit="to-hallway"),
        Exit("to-livingroom", "right", 60, to_room="livingroom", to_exit="to-hallway"),
        Exit("to-kitchen", "bottom", 55, to_room="kitchen", to_exit="to-hallway"),
        # the front door: no to_room yet, so it's locked
        Exit("to-outside", "top", 56, sprite="front-door"),
    ],
)
