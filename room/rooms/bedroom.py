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

    # --- Dresser corner ---
    RoomObject("dresser", "dresser", 134, 8, hitbox=(0, 14, 24, 10)),
    RoomObject("dresser-flowers", "flower-pot", 151, 11, layer="on-top", on="dresser"),

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

    # --- Bottom right ---
    RoomObject("flower-stand", "nightstand", 138, 78),
    RoomObject("flower-stand-pot", "flower-pot", 140, 71, layer="on-top", on="flower-stand"),

    # --- By the hallway door ---
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
        # the door in the right wall, below the dresser corner
        Exit("to-hallway", "right", 52, to_room="hallway", to_exit="to-bedroom"),
    ],
)
