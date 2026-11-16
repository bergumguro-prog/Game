"""Chess scene: /games/chess/

Works with plain HTML forms: every square is a button. Click one of your
pieces to select it (its legal moves get dots), then click a dot to move.
The game state lives in the Flask session as the list of moves played.

    GET  /games/chess/        show the board
    POST /games/chess/click   click a square (form field "square", e.g. "e2")
    POST /games/chess/new     start a new game
"""
import chess
from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.chess import logic, pieces
from room import sprites

SESSION_KEY = "chess"


def load_state():
    """(board, state). A broken or tampered session starts a fresh game."""
    state = session.get(SESSION_KEY) or {}
    moves = state.get("moves", [])
    try:
        if not isinstance(moves, list):
            raise ValueError("moves must be a list")
        board = logic.board_from_moves(moves)
    except ValueError:
        moves, board = [], chess.Board()
    selected = state.get("selected")
    if not isinstance(selected, str) or selected not in chess.SQUARE_NAMES:
        selected = None
    return board, {"moves": moves, "selected": selected}


def save_state(state):
    session[SESSION_KEY] = state


def handle_click(board, state, square):
    """Select a piece, move the selected piece, or clear the selection."""
    if state["selected"]:
        move = logic.find_move(board, logic.parse_square(state["selected"]), square)
        if move:
            board.push(move)
            state["moves"].append(move.uci())
            state["selected"] = None
            return
    if logic.is_own_piece(board, square) and chess.square_name(square) != state["selected"]:
        state["selected"] = chess.square_name(square)
    else:
        state["selected"] = None


def square_views(board, selected, status):
    """Everything the template needs to draw the 64 squares, top-left first."""
    selected_sq = logic.parse_square(selected) if selected else None
    targets = logic.legal_targets(board, selected_sq) if selected_sq is not None else set()
    last = board.peek() if board.move_stack else None
    views = []
    for rank in range(7, -1, -1):
        for file in range(8):
            sq = chess.square(file, rank)
            piece = board.piece_at(sq)
            views.append({
                "name": chess.square_name(sq),
                "light": (file + rank) % 2 == 1,
                "piece": piece,
                "svg": sprites.render(pieces.sprite_name(piece)) if piece else "",
                "label": chess.piece_name(piece.piece_type).capitalize() if piece else "",
                "selected": sq == selected_sq,
                "target": sq in targets,
                "capture": sq in targets and piece is not None,
                "last": last is not None and sq in (last.from_square, last.to_square),
                "check": sq == status["check_square"],
                "file_label": chess.FILE_NAMES[file] if rank == 0 else "",
                "rank_label": str(rank + 1) if file == 0 else "",
            })
    return views


class Chess(MiniGame):
    slug = "chess"
    title = "Chess"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            board, state = load_state()
            status = logic.status(board)
            return render_template(
                "chess.html",
                game=self,
                squares=square_views(board, state["selected"], status),
                status=status,
                move_count=len(state["moves"]),
            )

        @bp.route("/click", methods=["POST"])
        def click():
            board, state = load_state()
            try:
                square = logic.parse_square(request.form.get("square"))
            except ValueError:
                return redirect(url_for(".index"))
            if not logic.status(board)["over"]:
                handle_click(board, state, square)
            save_state(state)
            return redirect(url_for(".index"))

        @bp.route("/new", methods=["POST"])
        def new_game():
            save_state({"moves": [], "selected": None})
            return redirect(url_for(".index"))


game = Chess()
