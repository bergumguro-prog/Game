# Setup

How to install, run and test the project, and how the code is organized.

## Requirements
- Python 3.11 or newer
- Git and the GitHub CLI (`gh`) if you want to work with issues and PRs

## Install
From the project folder:

```bash
python3 -m venv .venv            # create a virtual environment (first time only)
source .venv/bin/activate        # activate it (every new terminal)
pip install -r requirements.txt  # install Flask, python-chess and pytest
```

## Run the game
```bash
python app.py
```
Then open http://127.0.0.1:5050 in your browser. Stop the server with `Ctrl+C`.

The game runs on port 5050 because macOS uses port 5000 for AirPlay.

## Run the tests
```bash
python -m pytest
```

## Project structure
```
Game/
├── CLAUDE.md                 # project rules, aesthetic and workflow
├── README.md
├── SETUP.md                  # this file
├── requirements.txt
├── .gitignore
├── .claude/
│   └── settings.json
│
├── app.py                    # starts Flask, registers the room + every game
│
├── core/                     # shared code used by everything
│   ├── __init__.py
│   └── game_base.py          # the interface every mini-game must follow
│
├── templates/
│   └── base.html             # shared page skeleton (loads theme + base CSS)
│
├── static/                   # shared frontend files
│   ├── css/
│   │   ├── theme.css         # CSS variables: colors, fonts (change the look here)
│   │   ├── base.css          # shared layout, buttons, transitions
│   │   └── pixels.css        # maps pixel-art letters to theme colors
│   ├── js/
│   │   └── scenes.js         # switching between room and games
│   ├── fonts/                # Pixelify Sans (SIL Open Font License)
│   └── sounds/
│
├── room/                     # the hub world  →  branch: room
│   ├── __init__.py
│   ├── routes.py             # Flask blueprint: "/" and /rooms/<id>
│   ├── world.py              # the Room type; finds every room in rooms/
│   ├── objects.py            # what all rooms share: RoomObject, player settings
│   ├── rooms/                # one file per room: size, look, doors, furniture
│   │   ├── bedroom.py        # where you start (chess, tic-tac-toe, hangman)
│   │   ├── hallway.py        # joins the other rooms; front door
│   │   ├── kitchen.py        # sink, fridge, pantry, table
│   │   └── livingroom.py     # piano, card table
│   ├── sprites.py            # pixel art, drawn as grids of letters
│   ├── templates/
│   │   └── room.html
│   └── static/
│       ├── room.css
│       └── player.js         # movement, collisions, pressing E
│
├── games/
│   ├── tictactoe/            # →  branch: game/tictactoe
│   │   ├── __init__.py
│   │   ├── routes.py         # blueprint: /games/tictactoe
│   │   ├── logic.py          # rules + computer opponent (pure Python)
│   │   ├── templates/
│   │   │   └── tictactoe.html
│   │   └── static/
│   │       ├── tictactoe.css
│   │       └── tictactoe.js
│   │
│   ├── hangman/              # →  branch: game/hangman
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── logic.py
│   │   ├── words.txt
│   │   ├── templates/
│   │   └── static/
│   │
│   └── chess/                # →  branch: game/chess
│       ├── __init__.py
│       ├── routes.py
│       ├── logic.py          # uses python-chess
│       ├── ai.py             # the computer opponent
│       ├── templates/
│       └── static/
│
├── docs/
│   ├── aesthetic/            # mood reference images
│   └── screenshot-room.png
│
└── tests/
    ├── test_room.py
    ├── test_tictactoe.py
    ├── test_hangman.py
    └── test_chess.py
```

## Adding a new mini-game
The full checklist (branches, sprites, sounds) is in CLAUDE.md under
"Adding a new mini-game". In short:

1. Create a folder `games/<name>/` with a `routes.py` that defines a subclass
   of `core.game_base.MiniGame` (see the docstring in that file).
2. Add an interactable object for it in one of the room files in
   `room/rooms/`. If there's already a "coming soon" object waiting for
   it (kitchen: `dishes`, `baking`, `tablesetting`; living room: `piano`, `cards`), use that slug
   for the game and the object opens it automatically.
3. Add tests in `tests/test_<name>.py`.

## Adding a new room
Make one new file in `room/rooms/`, for example `room/rooms/garden.py`, that
defines `room = Room(...)` (copy `livingroom.py` to start). It is found
automatically and shown at `/rooms/garden`. A room has:

- `id`, `name`: the URL name and the name in the browser tab
- `width`, `height`, `wall_height`: the size in art pixels
- `start`: where the player stands if nothing else says where
- `theme`, `floor_tile`, `wall_tile`: its colors (in `theme.css`) and patterns
- `exits`: doors to other rooms, for example
  `Exit("to-garden", "right", 60, to_room="garden", to_exit="to-main")`
  is a door in the right wall, starting 60 art pixels down. The room it
  leads to needs a matching `Exit` that points back.
- `objects`: the furniture, as `RoomObject`s

Then run `python -m pytest`: the tests check that everything is inside the
room, that every door has a partner, and that every game object and door can
be reached on foot.
