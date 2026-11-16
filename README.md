hub-world-game/
├── CLAUDE.md
├── README.md
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
│   │   └── base.css          # shared layout, buttons, transitions
│   ├── js/
│   │   └── scenes.js         # switching between room and games
│   ├── fonts/
│   └── sounds/
│
├── room/                     # the hub world  →  branch: room
│   ├── __init__.py
│   ├── routes.py             # Flask blueprint for the room
│   ├── objects.py            # furniture, positions, which object opens which game
│   ├── templates/
│   │   └── room.html
│   └── static/
│       ├── room.css
│       ├── player.js         # movement, collisions, pressing E
│       └── sprites/
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
└── tests/
    ├── test_room.py
    ├── test_tictactoe.py
    ├── test_hangman.py
    └── test_chess.py