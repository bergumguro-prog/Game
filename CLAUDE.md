# Hub World Game

A game where the player walks around a room and interacts with objects that open
mini-games (chess, hangman, tic-tac-toe, more later).

## Tech stack
- Python (Flask) backend, HTML/CSS frontend, minimal JavaScript (movement/input only).
- python-chess for chess rules.
- All styling lives in CSS files. Colors and fonts are CSS variables in one
  theme file so the whole look can be changed in one place.

## Aesthetic
Cozy, cute, cottagecore top-down pixel art. Reference images (for mood only):
`docs/aesthetic/cozy-room.jpg` (the main reference for the room),
`docs/aesthetic/cherry-garden.jpg`, `docs/aesthetic/pink-farm.jpg`.

- **Perspective:** top-down with a slight 3/4 view. The room is seen from above,
  with the back wall visible along the top and a thick pastel-pink frame around it.
- **Palette:**
  - Pastel pink and rose: walls, frame, bedding, cushions, tablecloths, bows
  - Mint and sage green: rugs, poufs, plants, hedges, grass
  - Cream and ivory: furniture, benches, tables, fences, panels
  - Warm medium browns: herringbone wood floor, bookshelves, plant stands
  - Small accents: cherry red, warm fireplace orange/yellow, white and lavender flowers
- **Style:** chunky, crisp pixels with soft outlines in dark brown or plum (never
  pure black). Shade with a few flat color steps, not smooth gradients.
  Shapes are soft and rounded.
- **Room contents:** pink back wall with curtained windows, a wreath and plant
  shelves; herringbone wooden floor; a bed with a pink quilt; bookshelves; a
  fireplace; a tea table with benches; rugs and lace doilies; poufs; lots of
  potted plants and flowers. Interactable objects for the mini-games should fit
  in (for example, chess on the tea table).
- **Mini-games:** use the same palette. UI panels are cream cards with a pink
  border, buttons are pink or mint, and boards use pink/cream (chess) or a
  wooden look.
- **Fonts:** a pixel font (for example "Pixelify Sans" or "Press Start 2P"),
  saved in `static/fonts/`.
- **Implementation:** use `image-rendering: pixelated`, draw sprites small and
  scale them up by whole numbers. All colors are variables in `theme.css`.
- **Originality:** all art is our own. The references set the mood. Never copy
  their sprites, characters or layouts.
- **Mood:** warm, wholesome and calm, like a sunny afternoon in a cute cottage.

## Architecture
- Scene system: the room is one scene, each mini-game is its own scene.
- Every mini-game follows the same interface. Adding a game = one new folder in
  games/ + one object in the room.
- Controls: arrow keys/WASD to move, E to interact, Esc to return to the room.

## Git and GitHub workflow
- Code is hosted on GitHub. Use the GitHub CLI (`gh`) for issues and pull requests.
- Never commit directly to `main`.

### Branch structure
- `main`: the stable game. Only finished, tested games get merged here.
- `room`: the hub world (player, movement, collisions, interactable objects).
- One long-lived branch per game, created from `main`:
  `game/tictactoe`, `game/hangman`, `game/chess`, and so on for new games.
- Issue branches are created FROM the branch they affect and merged BACK INTO it:
  - Issue about chess → branch from `game/chess`, PR back into `game/chess`.
  - Issue about the room → branch from `room`, PR back into `room`.
  - Issue name format: `<issue-number>-short-description` (e.g. `12-chess-ai`).

Example:
    main
     ├── room
     │    └── 1-player-movement → PR into room
     ├── game/chess
     │    ├── 10-chess-board     → PR into game/chess
     │    └── 12-chess-ai        → PR into game/chess
     └── game/hangman
          └── 7-word-list        → PR into game/hangman

### Issues
- Every piece of work starts as a GitHub issue with a description and
  acceptance criteria.
- Label each issue with the game it belongs to (e.g. `chess`, `hangman`, `room`)
  so it's clear which branch it goes into.
- Before starting an issue, pull the latest version of its parent branch.

### Commits and pull requests
- Small commits with clear present-tense messages ("Add castling to chess").
- Do NOT add "Co-Authored-By" lines or any AI attribution to commits or PRs.
- Issue PRs target the parent branch (NOT main) and include "Closes #<number>".
- When a game is fully done, open a PR from `game/<name>` into `main`.
- Never merge anything yourself. Wait for me to test and merge.

## Working style
- I'm [a beginner / somewhat experienced], so explain what each new file does.
- Stop after each issue so I can test it before moving on.
- Always tell me exactly how to run the project after changes.

