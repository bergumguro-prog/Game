"""Klondike solitaire: /games/solitaire/

The rules are in logic.py. The Flask session keeps only the shuffle's seed,
the list of moves made so far and when the game started; the table is
rebuilt from those on every request, so undo is just "forget the last move".

    GET  /games/solitaire/        show the table
    POST /games/solitaire/move    make a move (form field "move", see logic.py)
    POST /games/solitaire/auto    send a card to a foundation ("from": W or T0-T6)
    POST /games/solitaire/undo    take back the last move
    POST /games/solitaire/new     shuffle and deal a new game
"""
import random
import time

from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.solitaire import logic

SESSION_KEY = "solitaire"
SOUND_KEY = "solitaire_sound"   # sound to play on the next page load
MAX_MOVES = 600                 # keeps the session cookie small


def new_game():
    return {"seed": random.randrange(1, 2**31), "moves": [], "started": time.time(), "won": None}


def load_game():
    """The saved game, checked; a fresh one if it's missing or broken."""
    game = session.get(SESSION_KEY)
    try:
        seed = int(game["seed"])
        moves = [str(m) for m in game["moves"]][:MAX_MOVES]
        table = logic.replay(seed, moves)
        started = float(game.get("started") or time.time())
        won = game.get("won")
        won = float(won) if won is not None else None
    except (TypeError, KeyError, ValueError):
        game = new_game()
        session[SESSION_KEY] = game
        return game, logic.deal(game["seed"])
    return {"seed": seed, "moves": moves, "started": started, "won": won}, table


def save_game(game):
    session[SESSION_KEY] = game


def play_move(game, table, move):
    """Make `move` if it's allowed; returns True if it was made."""
    if game["won"] is not None or len(game["moves"]) >= MAX_MOVES:
        return False
    try:
        logic.apply(table, move)
    except ValueError:
        return False
    game["moves"].append(move)
    if logic.is_won(table):
        game["won"] = time.time()
        session[SOUND_KEY] = "win"
    else:
        session[SOUND_KEY] = "select" if move == "D" else "move"
    save_game(game)
    return True


class Solitaire(MiniGame):
    slug = "solitaire"
    title = "Solitaire"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            game, table = load_game()
            seconds = int((game["won"] or time.time()) - game["started"])
            return render_template(
                "solitaire.html",
                game=self,
                table=table,
                moves=len(game["moves"]),
                seconds=seconds,
                won=game["won"] is not None,
                can_undo=bool(game["moves"]) and game["won"] is None,
                sound=session.pop(SOUND_KEY, None),
            )

        @bp.route("/move", methods=["POST"])
        def move():
            game, table = load_game()
            play_move(game, table, request.form.get("move", ""))
            return redirect(url_for(".index"))

        @bp.route("/auto", methods=["POST"])
        def auto():
            game, table = load_game()
            source = request.form.get("from", "")
            if source == "W" or (len(source) == 2 and source[0] == "T" and source[1] in "0123456"):
                found = logic.auto_move(table, source)
                if found:
                    play_move(game, table, found)
            return redirect(url_for(".index"))

        @bp.route("/undo", methods=["POST"])
        def undo():
            game, _ = load_game()
            if game["moves"] and game["won"] is None:
                game["moves"].pop()
                save_game(game)
            return redirect(url_for(".index"))

        @bp.route("/new", methods=["POST"])
        def new():
            save_game(new_game())
            return redirect(url_for(".index"))


game = Solitaire()
