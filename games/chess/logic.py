"""Chess rules, using the python-chess library. No Flask here.

A game is stored as the list of moves played so far in UCI notation
("e2e4", "e7e8q", ...). Replaying them from the start position gives the
current board, so the state is small and can't be tampered with into an
illegal position.
"""
import chess


def board_from_moves(moves):
    """Replay `moves` (UCI strings) from the start. Raises ValueError if any is illegal."""
    board = chess.Board()
    for uci in moves:
        move = chess.Move.from_uci(uci)  # raises ValueError for garbage
        if move not in board.legal_moves:
            raise ValueError(f"illegal move: {uci}")
        board.push(move)
    return board


def parse_square(name):
    """"e4" -> chess.E4. Raises ValueError for anything that isn't a square."""
    if not isinstance(name, str):
        raise ValueError("not a square")
    return chess.parse_square(name.strip().lower())


def legal_targets(board, from_square):
    """Squares the piece on `from_square` can legally move to."""
    return {m.to_square for m in board.legal_moves if m.from_square == from_square}


def find_move(board, from_square, to_square):
    """The legal move from -> to, or None. Pawns always promote to a queen."""
    for promotion in (None, chess.QUEEN):
        move = chess.Move(from_square, to_square, promotion=promotion)
        if move in board.legal_moves:
            return move
    return None


def is_own_piece(board, square):
    piece = board.piece_at(square)
    return piece is not None and piece.color == board.turn


def color_name(color):
    return "White" if color == chess.WHITE else "Black"


def status(board):
    """What to show above the board: {"text", "over", "check_square"}."""
    outcome = board.outcome(claim_draw=True)
    check_square = board.king(board.turn) if board.is_check() else None
    if outcome is None:
        text = f"{color_name(board.turn)} to move"
        if board.is_check():
            text = f"Check! {text}"
        return {"text": text, "over": False, "check_square": check_square}

    if outcome.termination == chess.Termination.CHECKMATE:
        text = f"Checkmate! {color_name(outcome.winner)} wins"
    elif outcome.termination == chess.Termination.STALEMATE:
        text = "Stalemate! It's a draw"
    elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
        text = "Draw: not enough pieces to checkmate"
    else:
        text = "Draw by repetition or the move rule"
    return {"text": text, "over": True, "check_square": check_square}
