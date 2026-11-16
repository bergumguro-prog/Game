"""A simple chess computer opponent.

How it thinks:
1. evaluate(): counts material (pawn 100, knight 320, ...) plus a small bonus
   for pieces near the center. Positive = good for the side to move.
2. search(): looks DEPTH half-moves ahead (its move, your reply) using
   negamax with alpha-beta pruning, which skips lines that can't matter.
   Captures are tried first, which makes the pruning work much better.
3. Checkmate is worth more than any material, and a quicker mate is better.
Among equally good moves it picks one at random, so games vary.
"""
import random

import chess

DEPTH = 2
MATE = 100_000

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Small bonus for standing near the middle of the board (0 on the edge, 3 in the center).
CENTER_BONUS = [
    min(chess.square_file(sq), 7 - chess.square_file(sq), chess.square_rank(sq), 7 - chess.square_rank(sq))
    for sq in chess.SQUARES
]


def evaluate(board):
    """Score from the point of view of the side to move."""
    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        if piece.piece_type in (chess.KNIGHT, chess.BISHOP, chess.PAWN):
            value += 5 * CENTER_BONUS[square]
        score += value if piece.color == board.turn else -value
    return score


def _ordered_moves(board):
    """Captures first (biggest victim first), then everything else."""
    def key(move):
        victim = board.piece_at(move.to_square)
        return -(PIECE_VALUES[victim.piece_type] if victim else 0) - (900 if move.promotion else 0)
    return sorted(board.legal_moves, key=key)


def _negamax(board, depth, alpha, beta, ply):
    if board.is_checkmate():
        return -MATE + ply  # the side to move is mated; sooner is worse
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    if depth == 0:
        return evaluate(board)
    best = -MATE - 1
    for move in _ordered_moves(board):
        board.push(move)
        score = -_negamax(board, depth - 1, -beta, -alpha, ply + 1)
        board.pop()
        best = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break  # the opponent would never allow this line
    return best


def choose_move(board, depth=DEPTH, rng=None):
    """The move the computer plays for the side to move. None if the game is over."""
    rng = rng or random
    moves = _ordered_moves(board)
    if not moves:
        return None
    board = board.copy(stack=False)
    best_score, best_moves = -MATE - 1, []
    for move in moves:
        board.push(move)
        score = -_negamax(board, depth - 1, -MATE - 1, MATE + 1, 1)
        board.pop()
        if score > best_score:
            best_score, best_moves = score, [move]
        elif score == best_score:
            best_moves.append(move)
    return rng.choice(best_moves)
