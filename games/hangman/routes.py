"""Hangman scene: /games/hangman/

The game state (secret word + guessed letters) lives in the Flask session.
The session cookie is signed, not encrypted, so a very curious player could
decode it and peek at the word. That's fine for a cozy local game.

    GET  /games/hangman/        show the game
    POST /games/hangman/guess   guess a letter (form field "letter")
    POST /games/hangman/new     start a new game with a new word
"""
from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.hangman import drawing, logic  # noqa: F401  (drawing registers the pictures)
from room import sprites

SESSION_KEY = "hangman"
SOUND_KEY = "hangman_sound"  # sound to play on the next page load
WORDS = logic.load_words()


def new_state(previous_word=None):
    word = logic.pick_word(WORDS)
    if len(WORDS) > 1:
        while word == previous_word:  # don't repeat the same word twice in a row
            word = logic.pick_word(WORDS)
    return {"word": word, "guessed": ""}


def load_state():
    state = session.get(SESSION_KEY) or {}
    word, guessed = state.get("word"), state.get("guessed", "")
    if not logic.is_valid_word(word) or not isinstance(guessed, str) \
            or any(c not in logic.ALPHABET for c in guessed):
        state = new_state()
        session[SESSION_KEY] = state
        return state
    return {"word": word, "guessed": guessed}


class Hangman(MiniGame):
    slug = "hangman"
    title = "Hangman"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            state = load_state()
            word, guessed = state["word"], state["guessed"]
            won = logic.is_won(word, guessed)
            lost = logic.is_lost(word, guessed)
            over = won or lost
            keys = [
                {
                    "letter": c,
                    "state": ("right" if c in word else "wrong") if c in guessed else "open",
                }
                for c in logic.ALPHABET
            ]
            return render_template(
                "hangman.html",
                game=self,
                # When the game is lost, reveal the whole word.
                letters=list(word) if over else logic.masked(word, guessed),
                missed=[c for c in word if c not in guessed] if lost else [],
                keys=keys,
                wrong=logic.wrong_count(word, guessed),
                figure=sprites.render(f"hangman-{min(logic.wrong_count(word, guessed), logic.MAX_WRONG)}"),
                max_wrong=logic.MAX_WRONG,
                won=won,
                lost=lost,
                over=over,
                sound=session.pop(SOUND_KEY, None),
            )

        @bp.route("/guess", methods=["POST"])
        def guess():
            state = load_state()
            try:
                state["guessed"] = logic.guess(
                    state["word"], state["guessed"], request.form.get("letter"))
            except ValueError:
                pass  # ignore repeats, non-letters and guesses after the end
            else:
                word, guessed = state["word"], state["guessed"]
                if logic.is_won(word, guessed):
                    session[SOUND_KEY] = "win"
                elif logic.is_lost(word, guessed):
                    session[SOUND_KEY] = "lose"
                else:
                    session[SOUND_KEY] = "select" if guessed[-1] in word else "move"
            session[SESSION_KEY] = state
            return redirect(url_for(".index"))

        @bp.route("/new", methods=["POST"])
        def new_game():
            session[SESSION_KEY] = new_state(load_state()["word"])
            return redirect(url_for(".index"))


game = Hangman()
