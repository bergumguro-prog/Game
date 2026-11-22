"""The kitchen: a cozy kitchen with three mini-games.

    sink          -> dishwashing      (games/dishes, slug "dishes")
    fridge/pantry -> baking           (games/baking, slug "baking")
    kitchen table -> table decorating (games/tablesetting, slug "tablesetting")

Until a game exists, its object opens "coming soon". When the game is added
with the same slug, the object opens it automatically.
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- On the back wall ---
    RoomObject("jar-shelf", "wall-shelf", 30, 12, layer="wall"),
    RoomObject("jar-honey", "jar-honey", 33, 5, layer="wall"),
    RoomObject("jar-jam", "jar-jam", 40, 5, layer="wall"),
    RoomObject("jar-pickles", "jar-pickles", 47, 5, layer="wall"),
    RoomObject("window", "window", 56, 1, layer="wall"),
    RoomObject("pan-rail", "pan-rail", 90, 1, layer="wall"),
    RoomObject("hanging-plant", "hanging-plant", 79, 0, layer="wall"),

    # --- Rugs and doormats ---
    RoomObject("mat-door", "mat-pink", 6, 29, layer="floor"),
    RoomObject("rug-table", "rug-kitchen", 54, 62, layer="floor"),

    # --- Counters along the back wall ---
    RoomObject("counter-left", "counter", 28, 14, hitbox=(0, 12, 24, 12)),
    RoomObject("sink", "sink", 52, 14, hitbox=(0, 12, 24, 12),
               game="dishes", prompt="wash the dishes"),
    RoomObject("counter-middle", "counter-short", 76, 14, hitbox=(0, 12, 16, 12)),
    RoomObject("stove", "stove", 92, 14, hitbox=(0, 12, 24, 12)),
    RoomObject("fridge", "fridge", 120, 0, hitbox=(0, 26, 20, 12),
               game="baking", prompt="bake muffins"),
    # the counter carries on past the fridge, round the corner and down
    # the right wall; its cupboards are the pantry
    RoomObject("counter-corner", "counter-corner", 140, 14, hitbox=(0, 12, 36, 12)),
    RoomObject("pantry", "counter-side", 156, 25,
               game="baking", prompt="bake muffins"),

    # --- Kitchen table ---
    RoomObject("chair-left", "chair", 52, 70),
    RoomObject("kitchen-table", "kitchen-table", 64, 66, hitbox=(0, 2, 40, 17),
               game="tablesetting", prompt="decorate the table"),
    RoomObject("chair-right", "chair", 106, 70),

    # --- Plants ---
    RoomObject("daisies-bottom-left", "flowers-daisies", 4, 106, hitbox=(1, 6, 8, 8)),
    RoomObject("tulips-bottom-right", "flowers-tulips", 144, 106, hitbox=(1, 6, 8, 8)),
]

room = Room(
    id="kitchen",
    name="Kitchen",
    theme="kitchen",
    floor_tile="kitchen-floor-tile",
    wall_tile="subway-tile",
    width=176,
    height=128,
    wall_height=28,
    start=(80, 92),
    objects=OBJECTS,
    exits=[
        Exit("to-hallway", "top", 8, to_room="hallway", to_exit="to-kitchen"),
    ],
)
