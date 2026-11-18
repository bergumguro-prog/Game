"""The bedroom: where the player starts.

Chess is on the tea table, tic-tac-toe on the little game table and hangman
in the left bookshelf. Positions are in art pixels; see room/objects.py for
what each RoomObject field means.
"""
from room.objects import RoomObject
from room.world import Exit, Room

OBJECTS = [
    # --- On the back wall ---
    RoomObject("wreath", "wreath", 18, 3, layer="wall"),
    RoomObject("window-left", "window", 56, 6, layer="wall"),
    RoomObject("window-right", "window", 78, 6, layer="wall"),
    RoomObject("wall-shelf", "wall-shelf", 102, 13, layer="wall"),
    RoomObject("shelf-plant", "plant-small", 106, 6, layer="wall"),
    RoomObject("shelf-flowers", "flower-pot", 116, 4, layer="wall"),

    # --- Rugs ---
    RoomObject("rug-bed", "rug-bed", 6, 36, layer="floor"),
    RoomObject("doily-top", "doily", 70, 30, layer="floor"),
    RoomObject("rug-tea", "rug-tea", 114, 40, layer="floor"),
    RoomObject("rug-books", "round-rug-small", 22, 74, layer="floor"),
    RoomObject("rug-pink", "rug-pink", 6, 98, layer="floor"),
    RoomObject("doily-bottom", "doily", 76, 102, layer="floor"),
    RoomObject("rug-round", "round-rug", 130, 104, layer="floor"),

    # --- Bedroom corner ---
    RoomObject("bed", "bed", 12, 16),
    RoomObject("nightstand", "nightstand", 40, 20),
    RoomObject("nightstand-flowers", "flower-pot", 42, 13, layer="on-top", on="nightstand"),

    # --- Game corner ---
    RoomObject("tictactoe-table", "tictactoe-table", 75, 33,
               game="tictactoe", prompt="play tic-tac-toe"),
    RoomObject("pouf-top-pink", "pouf-pink", 62, 40),
    RoomObject("pouf-top-mint", "pouf-mint", 93, 40),

    # --- Poufs ---
    RoomObject("pouf-books", "pouf-mint", 24, 76),
    RoomObject("pouf-corner-pink", "pouf-pink", 12, 104),
    RoomObject("pouf-corner-mint", "pouf-mint", 28, 110),
    RoomObject("pouf-round", "pouf-pink", 137, 109),

    # --- Fireplace corner ---
    RoomObject("fireplace", "fireplace", 134, 14),
    RoomObject("mantel-plant", "plant-small", 138, 7, layer="on-top", on="fireplace"),
    RoomObject("mantel-flowers", "flower-pot", 150, 5, layer="on-top", on="fireplace"),
    RoomObject("plant-fireplace", "plant-big", 163, 18, hitbox=(1, 6, 8, 8)),

    # --- Tea table ---
    RoomObject("bench-left", "bench", 119, 43),
    RoomObject("tea-table", "tea-table", 128, 44,
               game="chess", prompt="play chess"),
    RoomObject("bench-right", "bench", 152, 43),
    RoomObject("cake", "cake", 135, 46, layer="on-top", on="tea-table"),
    RoomObject("teacup", "teacup", 145, 51, layer="on-top", on="tea-table"),

    # --- Reading corner ---
    RoomObject("bookshelf-left", "bookshelf", 6, 62,
               game="hangman", prompt="play hangman"),
    RoomObject("bookshelf-right", "bookshelf", 38, 62),
    RoomObject("plant-books", "plant-big", 56, 100, hitbox=(1, 6, 8, 8)),

    # --- Bottom right ---
    RoomObject("plant-right-a", "plant-big", 124, 76, hitbox=(1, 6, 8, 8)),
    RoomObject("flower-stand", "nightstand", 138, 78),
    RoomObject("flower-stand-pot", "flower-pot", 140, 71, layer="on-top", on="flower-stand"),
    RoomObject("plant-right-b", "plant-big", 156, 76, hitbox=(1, 6, 8, 8)),

    # --- Bottom middle ---
    RoomObject("pot-bottom-left", "flower-pot", 66, 116),
    RoomObject("pot-bottom-right", "flower-pot", 102, 116),
    RoomObject("mat-hallway-door", "mat-pink-side", 168, 50, layer="floor"),
]


room = Room(
    id="bedroom",
    name="Bedroom",
    theme="bedroom",
    width=176,
    height=128,
    wall_height=26,
    start=(82, 66),
    objects=OBJECTS,
    exits=[
        # the doorway between the two flower pots at the bottom
        # the door in the right wall, below the fireplace corner
        Exit("to-hallway", "right", 52, to_room="hallway", to_exit="to-bedroom"),
    ],
)
