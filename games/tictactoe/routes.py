"""Tic-tac-toe scene: /games/tictactoe/

The game state lives in the Flask session (a signed cookie), so the whole
game works with plain HTML forms and no JavaScript:

    GET  /games/tictactoe/       show the board
    POST /games/tictactoe/move   take a square (form field "cell")
    POST /games/tictactoe/new    start a new game (form field "mode")

Two modes: "computer" (you are X, the computer is O) and "friend"
(two people take turns on the same computer).
"""
from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.tictactoe import logic, pieces  # noqa: F401  (pieces registers the X/O sprites)
from room import sprites

SESSION_KEY = "tictactoe"
SOUND_KEY = "tictactoe_sound"  # sound to play on the next page load
MODES = ("computer", "friend")


def load_state():
    state = session.get(SESSION_KEY) or {}
    board = state.get("board", logic.EMPTY_BOARD)
    if not logic.is_valid_board(board):
        board = logic.EMPTY_BOARD
    score = state.get("score") or {}
    mode = state.get("mode") if state.get("mode") in MODES else "computer"
    return {
        "board": board,
        "mode": mode,
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


def result_sound(board, mode):
    """Sound for a finished game: win, lose or draw (from your point of view)."""
    if logic.is_draw(board):
        return "draw"
    if mode == "computer" and logic.winner(board) == logic.O:
        return "lose"
    return "win"


def status_text(board, mode):
    win = logic.winner(board)
    if logic.is_draw(board):
        return "It's a draw!"
    if mode == "computer":
        if win:
            return "You win!" if win == logic.X else "The computer wins!"
        return "Your turn"
    if win:
        return f"{win} wins!"
    return f"{logic.current_player(board)}'s turn"


def score_labels(mode):
    if mode == "computer":
        return {logic.X: "You", logic.O: "Computer"}
    return {logic.X: "X", logic.O: "O"}


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
                status=status_text(board, state["mode"]),
                over=logic.is_over(board),
                score=state["score"],
                labels=score_labels(state["mode"]),
                mode=state["mode"],
                sound=session.pop(SOUND_KEY, None),
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
                # The computer answers right away (it always plays O).
                board = state["board"]
                if state["mode"] == "computer" and logic.current_player(board) == logic.O \
                        and not logic.is_over(board):
                    state["board"] = logic.play(board, logic.computer_move(board))
                if logic.is_over(state["board"]):
                    record_result(state)
                    session[SOUND_KEY] = result_sound(state["board"], state["mode"])
                else:
                    session[SOUND_KEY] = "move"
            save_state(state)
            return redirect(url_for(".index"))

        @bp.route("/new", methods=["POST"])
        def new_game():
            state = load_state()
            mode = request.form.get("mode", state["mode"])
            if mode not in MODES:
                mode = state["mode"]
            if mode != state["mode"]:
                # switching opponent starts the score over
                state["score"] = {logic.X: 0, logic.O: 0, "draw": 0}
            state["mode"] = mode
            state["board"] = logic.EMPTY_BOARD
            save_state(state)
            return redirect(url_for(".index"))


game = TicTacToe()
