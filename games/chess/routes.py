"""Chess scene: /games/chess/

Works with plain HTML forms: every square is a button. Click one of your
pieces to select it (its legal moves get dots), then click a dot to move.
The game state lives in the Flask session as the list of moves played.

    GET  /games/chess/        show the board
    POST /games/chess/click   click a square (form field "square", e.g. "e2")
    POST /games/chess/new     start a new game (form field "mode")

Two modes: "computer" (you play white, games/chess/ai.py plays black) and
"friend" (two people share the board).
"""
import chess
from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.chess import ai, logic, pieces
from room import sprites

SESSION_KEY = "chess"
SOUND_KEY = "chess_sound"  # sound to play on the next page load
MODES = ("computer", "friend")


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
    mode = state.get("mode") if state.get("mode") in MODES else "computer"
    return board, {"moves": moves, "selected": selected, "mode": mode}


def save_state(state):
    session[SESSION_KEY] = state


def handle_click(board, state, square):
    """Select a piece, move the selected piece, or clear the selection.

    Returns True if a move was played.
    """
    if state["selected"]:
        move = logic.find_move(board, logic.parse_square(state["selected"]), square)
        if move:
            board.push(move)
            state["moves"].append(move.uci())
            state["selected"] = None
            return True
    if state["mode"] == "computer" and board.turn == chess.BLACK:
        state["selected"] = None  # black's pieces belong to the computer
        return False
    if logic.is_own_piece(board, square) and chess.square_name(square) != state["selected"]:
        state["selected"] = chess.square_name(square)
    else:
        state["selected"] = None
    return False


def computer_reply(board, state):
    """In computer mode, let the AI play black's move."""
    if state["mode"] == "computer" and board.turn == chess.BLACK \
            and not logic.status(board)["over"]:
        move = ai.choose_move(board)
        board.push(move)
        state["moves"].append(move.uci())


def move_sound(board, mode):
    """Sound after a move: "move", or win/lose/draw if the game just ended."""
    outcome = board.outcome(claim_draw=True)
    if outcome is None:
        return "move"
    if outcome.winner is None:
        return "draw"
    if mode == "computer" and outcome.winner == chess.BLACK:
        return "lose"
    return "win"


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
            status = logic.status(board, state["mode"])
            return render_template(
                "chess.html",
                game=self,
                squares=square_views(board, state["selected"], status),
                status=status,
                move_count=len(state["moves"]),
                mode=state["mode"],
                sound=session.pop(SOUND_KEY, None),
            )

        @bp.route("/click", methods=["POST"])
        def click():
            board, state = load_state()
            try:
                square = logic.parse_square(request.form.get("square"))
            except ValueError:
                return redirect(url_for(".index"))
            if not logic.status(board)["over"]:
                if handle_click(board, state, square):
                    computer_reply(board, state)
                    session[SOUND_KEY] = move_sound(board, state["mode"])
            save_state(state)
            return redirect(url_for(".index"))

        @bp.route("/new", methods=["POST"])
        def new_game():
            _, state = load_state()
            mode = request.form.get("mode", state["mode"])
            save_state({
                "moves": [],
                "selected": None,
                "mode": mode if mode in MODES else state["mode"],
            })
            return redirect(url_for(".index"))


game = Chess()
