"""Tic-tac-toe scene: /games/tictactoe/

The game state lives in the Flask session (a signed cookie), so the whole
game works with plain HTML forms and no JavaScript:

    GET  /games/tictactoe/       show the board
    POST /games/tictactoe/move   take a square (form field "cell")
    POST /games/tictactoe/new    start a new game
"""
from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.tictactoe import logic, pieces  # noqa: F401  (pieces registers the X/O sprites)
from room import sprites

SESSION_KEY = "tictactoe"


def load_state():
    state = session.get(SESSION_KEY) or {}
    board = state.get("board", logic.EMPTY_BOARD)
    if not logic.is_valid_board(board):
        board = logic.EMPTY_BOARD
    score = state.get("score") or {}
    return {
        "board": board,
        "score": {k: int(score.get(k, 0)) for k in (logic.X, logic.O, "draw")},
    }


def save_state(state):
    session[SESSION_KEY] = state


def record_result(state):
    """Add the finished game to the score."""
    board = state["board"]
    if logic.winner(board):
        state["score"][logic.winner(board)] += 1
    elif logic.is_draw(board):
        state["score"]["draw"] += 1


def status_text(board):
    win = logic.winner(board)
    if win:
        return f"{win} wins!"
    if logic.is_draw(board):
        return "It's a draw!"
    return f"{logic.current_player(board)}'s turn"


class TicTacToe(MiniGame):
    slug = "tictactoe"
    title = "Tic-tac-toe"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            state = load_state()
            board = state["board"]
            win_line = logic.winning_line(board) or ()
            legal = set(logic.legal_moves(board))
            cells = [
                {
                    "index": i,
                    "piece": board[i],
                    "playable": i in legal,
                    "winning": i in win_line,
                }
                for i in range(9)
            ]
            return render_template(
                "tictactoe.html",
                game=self,
                cells=cells,
                status=status_text(board),
                over=logic.is_over(board),
                score=state["score"],
                x_svg=sprites.render("tictactoe-x"),
                o_svg=sprites.render("tictactoe-o"),
            )

        @bp.route("/move", methods=["POST"])
        def move():
            state = load_state()
            try:
                cell = int(request.form.get("cell", ""))
                state["board"] = logic.play(state["board"], cell)
            except ValueError:
                pass  # ignore illegal or garbled moves
            else:
                if logic.is_over(state["board"]):
                    record_result(state)
            save_state(state)
            return redirect(url_for(".index"))

        @bp.route("/new", methods=["POST"])
        def new_game():
            state = load_state()
            state["board"] = logic.EMPTY_BOARD
            save_state(state)
            return redirect(url_for(".index"))


game = TicTacToe()
