"""The living room: a fireplace, a piano and a card table.

    fireplace  -> the fireplace scene (games/fireplace)
    card table -> Klondike solitaire (games/solitaire)
    piano      -> the piano (games/piano; "coming soon" until it exists)
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- On the back wall ---
    RoomObject("window", "window", 8, 6, layer="wall"),
    RoomObject("picture", "picture", 82, 8, layer="wall"),
    RoomObject("picture-flower", "picture-flower", 98, 9, layer="wall"),
    RoomObject("clock", "wall-clock", 148, 6, layer="wall"),
    RoomObject("hanging-plant", "hanging-plant", 164, 0, layer="wall"),

    # --- Rugs and doormats ---
    RoomObject("rug-fire", "round-rug-lavender-small", 29, 35, layer="floor"),
    RoomObject("rug-piano", "rug-lavender", 112, 36, layer="floor"),
    RoomObject("rug-cards", "round-rug-lavender", 56, 72, layer="floor"),
    RoomObject("mat-side-door", "mat-lavender-side", 1, 60, layer="floor"),

    # --- Fireplace corner ---
    RoomObject("fireplace", "fireplace", 32, 14, hitbox=(0, 12, 24, 6),
               game="fireplace", prompt="sit by the fire"),
    RoomObject("mantel-lavender", "flower-pot-lavender", 34, 5, layer="on-top", on="fireplace"),
    RoomObject("mantel-flowers", "flower-pot", 48, 5, layer="on-top", on="fireplace"),
    # two armchairs turned toward the fire, one on each side
    RoomObject("armchair-left", "armchair-side-right", 10, 26),
    RoomObject("armchair", "armchair-side", 58, 26),

    # --- Flowers ---
    RoomObject("roses-top-right", "flowers-roses", 164, 28, hitbox=(1, 6, 8, 8)),
    RoomObject("lavender-bottom-right", "flowers-lavender", 162, 100, hitbox=(1, 6, 8, 8)),

    # --- Games ---
    RoomObject("piano", "piano", 112, 12, hitbox=(0, 12, 30, 9),
               game="piano", prompt="play piano"),
    RoomObject("card-table", "card-table", 74, 78, hitbox=(0, 2, 26, 16),
               game="solitaire", prompt="play solitaire"),
    RoomObject("card-pouf-left", "pouf-pink", 61, 84),
    RoomObject("card-pouf-right", "pouf-pink", 103, 84),

    # --- A sofa under the card table, facing it (seen from behind) ---
    RoomObject("sofa", "sofa-back", 66, 98, hitbox=(0, 3, 44, 17)),
]

room = Room(
    id="livingroom",
    name="Living room",
    theme="livingroom",
    floor_tile="checker-tile",
    wall_tile="wallpaper-stripes",
    width=176,
    height=120,
    wall_height=26,
    start=(132, 96),
    objects=OBJECTS,
    exits=[
        Exit("to-hallway", "left", 62, to_room="hallway", to_exit="to-livingroom"),
    ],
)
