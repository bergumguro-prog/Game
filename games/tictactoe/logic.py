"""Tic-tac-toe rules. Pure Python, no Flask, so it's easy to test.

The board is a string of 9 characters, read left-to-right, top-to-bottom:

     0 | 1 | 2
    ---+---+---
     3 | 4 | 5
    ---+---+---
     6 | 7 | 8

Each character is "X", "O" or "." (empty). X always starts.
"""
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
