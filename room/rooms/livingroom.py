"""The living room: a music and card room.

The piano and the card table open "coming soon" until their games exist.
To make one real, create games/<slug>/ with the same slug (for example
games/cards/ with slug = "cards"); nothing here has to change.
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- On the back wall ---
    RoomObject("window", "window", 16, 6, layer="wall"),
    RoomObject("picture", "picture", 40, 8, layer="wall"),
    RoomObject("picture-flower", "picture-flower", 56, 9, layer="wall"),
    RoomObject("clock", "wall-clock", 74, 6, layer="wall"),
    RoomObject("hanging-plant", "hanging-plant", 132, 0, layer="wall"),

    # --- Rugs and doormats ---
    RoomObject("rug-cards", "round-rug-lavender", 40, 56, layer="floor"),
    RoomObject("rug-piano", "rug-lavender", 96, 36, layer="floor"),
    RoomObject("mat-side-door", "mat-lavender-side", 1, 60, layer="floor"),

    # --- Plants ---
    RoomObject("pot-top-left", "flower-pot-lavender", 4, 28),
    RoomObject("plant-top-right", "plant-big", 130, 28, hitbox=(1, 6, 8, 8)),
    RoomObject("plant-bottom-right", "plant-big", 130, 94, hitbox=(1, 6, 8, 8)),
    RoomObject("pot-bottom-left", "flower-pot-lavender", 4, 100),

    # --- Games (coming soon) ---
    RoomObject("piano", "piano", 96, 12, hitbox=(0, 12, 30, 9),
               game="piano", prompt="play piano"),
    RoomObject("card-table", "card-table", 58, 62, hitbox=(0, 2, 26, 16),
               game="cards", prompt="play cards"),
    RoomObject("card-pouf-left", "pouf-pink", 45, 68),
    RoomObject("card-pouf-right", "pouf-pink", 87, 68),
]

room = Room(
    id="livingroom",
    name="Living room",
    theme="livingroom",
    floor_tile="checker-tile",
    wall_tile="wallpaper-stripes",
    width=144,
    height=112,
    wall_height=26,
    start=(64, 88),
    objects=OBJECTS,
    exits=[
        Exit("to-kitchen", "left", 62, to_room="kitchen", to_exit="to-livingroom"),
    ],
)
