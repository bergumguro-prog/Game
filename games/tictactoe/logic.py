"""Tic-tac-toe rules. Pure Python, no Flask, so it's easy to test.

The board is a string of 9 characters, read left-to-right, top-to-bottom:

     0 | 1 | 2
    ---+---+---
     3 | 4 | 5
    ---+---+---
     6 | 7 | 8

Each character is "X", "O" or "." (empty). X always starts.
"""
import random

X, O, EMPTY = "X", "O", "."

EMPTY_BOARD = EMPTY * 9

# Every row, column and diagonal that wins the game.
LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)


def is_valid_board(board):
    return (
        isinstance(board, str)
        and len(board) == 9
        and set(board) <= {X, O, EMPTY}
        and board.count(X) - board.count(O) in (0, 1)
    )


def winning_line(board):
    """The three winning squares, or None if nobody has won."""
    for line in LINES:
        a, b, c = (board[i] for i in line)
        if a != EMPTY and a == b == c:
            return line
    return None


def winner(board):
    """ "X", "O" or None."""
    line = winning_line(board)
    return board[line[0]] if line else None


def is_draw(board):
    return EMPTY not in board and winner(board) is None


def is_over(board):
    return winner(board) is not None or EMPTY not in board


def current_player(board):
    """Whose turn it is. X starts, then they alternate."""
    return X if board.count(X) == board.count(O) else O


def legal_moves(board):
    if is_over(board):
        return []
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def play(board, index):
    """Return the board after the current player takes square `index`.

    Raises ValueError for an illegal move (taken square, out of range, or
    the game is already over).
    """
    if index not in legal_moves(board):
        raise ValueError(f"illegal move: {index}")
    return board[:index] + current_player(board) + board[index + 1:]


# --- Computer opponent ---

CORNERS = (0, 2, 6, 8)
CENTER = 4


def other(player):
    return O if player == X else X


def _finishing_move(board, player):
    """A square that would complete a line for `player`, or None."""
    for line in LINES:
        cells = [board[i] for i in line]
        if cells.count(player) == 2 and cells.count(EMPTY) == 1:
            return line[cells.index(EMPTY)]
    return None


def computer_move(board, rng=None):
    """Pick a square for the player whose turn it is.

    A simple strategy, in order:
    1. Win if possible.
    2. Block the opponent's win.
    3. Take the center.
    4. Take a free corner.
    5. Take any free square.
    `rng` is a random.Random, so tests can make choices predictable.
    """
    rng = rng or random
    moves = legal_moves(board)
    if not moves:
        raise ValueError("no moves left")
    me = current_player(board)
    for player in (me, other(me)):
        square = _finishing_move(board, player)
        if square is not None:
            return square
    if CENTER in moves:
        return CENTER
    corners = [i for i in CORNERS if i in moves]
    return rng.choice(corners or moves)
