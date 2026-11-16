# Hub World Game

A game where the player walks around a room and interacts with objects that open
mini-games (chess, hangman, tic-tac-toe, more later).

## Tech stack
- Python (Flask) backend, HTML/CSS frontend, minimal JavaScript (movement/input only).
- python-chess for chess rules.
- All styling lives in CSS files. Colors and fonts are CSS variables in one
  theme file so the whole look can be changed in one place.

## Aesthetic
[Describe your look here, e.g. "cozy pixel-art bedroom at night, warm lamp light,
muted purples and oranges, retro computer fonts".]

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

