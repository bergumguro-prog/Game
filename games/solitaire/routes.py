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
from games.solitaire import logic, pieces
from room import sprites

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


def card_view(card, source=None, index=None, down_above=0, up_above=0, movable=False):
    """What the template needs to draw one face-up card."""
    return {
        "card": card,
        "rank": "10" if card[0] == "T" else card[0],
        "red": logic.is_red(card),
        "suit": sprites.render(pieces.SUIT_SPRITES[card[1]], "suit"),
        "name": card_name(card),
        "source": source,
        "index": index,
        "down_above": down_above,
        "up_above": up_above,
        "movable": movable,
    }


RANK_NAMES = {"A": "Ace", "T": "10", "J": "Jack", "Q": "Queen", "K": "King"}
SUIT_NAMES = {"H": "hearts", "D": "diamonds", "C": "clubs", "S": "spades"}


def card_name(card):
    return f"{RANK_NAMES.get(card[0], card[0])} of {SUIT_NAMES[card[1]]}"


def table_view(table):
    """The table laid out for the template: tableau piles with how far down
    each card is fanned, the waste's top card and each foundation's top."""
    piles = []
    for p, pile in enumerate(table.tableau):
        cards, down, up = [], 0, 0
        for i, (card, face_up) in enumerate(pile):
            if face_up:
                cards.append(card_view(card, f"T{p}", i, down, up, movable=True))
                up += 1
            else:
                cards.append({"face_down": True, "down_above": down, "up_above": up})
                down += 1
        piles.append({"id": f"T{p}", "cards": cards, "down": down, "up": up})
    return {
        "stock": len(table.stock),
        "waste": card_view(table.waste[-1], "W", movable=True) if table.waste else None,
        "waste_under": len(table.waste) > 1,
        "foundations": [
            {"id": f"F{i}", "top": card_view(f[-1], f"F{i}", movable=True) if f else None,
             "count": len(f)}
            for i, f in enumerate(table.foundations)
        ],
        "piles": piles,
    }


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
                view=table_view(table),
                bow=sprites.render("card-bow", "card-bow"),
                moves=len(game["moves"]),
                seconds=seconds,
                time_text=f"{seconds // 60}:{seconds % 60:02d}",
                heart=sprites.render("suit-heart", "win-heart"),
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
