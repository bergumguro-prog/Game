"""The piano: /games/piano/

Two modes:
- Free play: play anything with the mouse or the computer keyboard.
- Repeat the tune: the piano plays a tune, you play it back; each round
  the tune gets one note longer. Your best length is remembered.

The notes, keyboard layout and tunes are in logic.py; the sounds are made by
tools/make_sounds.py and played by static/piano.js.

    GET  /games/piano/                the piano
    POST /games/piano/mode            "free" or "repeat" (field "mode")
    POST /games/piano/repeat/start    start a new tune
    POST /games/piano/repeat/answer   the notes you played (field "notes": "C4,E4,G4")
"""
import random

from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.piano import logic

SESSION_KEY = "piano"
SOUND_KEY = "piano_sound"
MODES = ("free", "repeat")


def load_state():
    state = session.get(SESSION_KEY) or {}
    mode = state.get("mode") if state.get("mode") in MODES else "free"
    try:
        seed = int(state["seed"]) if state.get("seed") is not None else None
        length = int(state.get("length", logic.START_LENGTH))
        best = int(state.get("best", 0))
    except (TypeError, ValueError):
        seed, length, best = None, logic.START_LENGTH, 0
    length = min(max(length, logic.START_LENGTH), logic.MAX_LENGTH)
    result = state.get("result") if state.get("result") in ("right", "wrong", "done") else None
    return {"mode": mode, "seed": seed, "length": length, "best": max(best, 0),
            "result": result, "reached": int(state.get("reached") or 0)}


def save_state(state):
    session[SESSION_KEY] = state


class Piano(MiniGame):
    slug = "piano"
    title = "Piano"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            state = load_state()
            playing = state["mode"] == "repeat" and state["seed"] is not None \
                and state["result"] in (None, "right")
            return render_template(
                "piano.html",
                game=self,
                keys=logic.keys(),
                white_count=len(logic.WHITE),
                state=state,
                tune=logic.tune(state["seed"], state["length"]) if playing else None,
                sound=session.pop(SOUND_KEY, None),
            )

        @bp.route("/mode", methods=["POST"])
        def mode():
            state = load_state()
            if request.form.get("mode") in MODES:
                state["mode"] = request.form["mode"]
                state["seed"] = None
                state["result"] = None
            save_state(state)
            return redirect(url_for(".index"))

        @bp.route("/repeat/start", methods=["POST"])
        def start():
            state = load_state()
            state.update(mode="repeat", seed=random.randrange(1, 2**31),
                         length=logic.START_LENGTH, result=None, reached=0)
            save_state(state)
            return redirect(url_for(".index"))

        @bp.route("/repeat/answer", methods=["POST"])
        def answer():
            state = load_state()
            if state["mode"] != "repeat" or state["seed"] is None or state["result"] in ("wrong", "done"):
                return redirect(url_for(".index"))
            played = [n for n in request.form.get("notes", "").split(",") if n]
            if not all(n in logic.NOTES for n in played) or len(played) > logic.MAX_LENGTH:
                return redirect(url_for(".index"))
            if logic.is_correct(state["seed"], state["length"], played):
                state["best"] = max(state["best"], state["length"])
                if state["length"] >= logic.MAX_LENGTH:
                    state["result"] = "done"
                    session[SOUND_KEY] = "win"
                else:
                    state["length"] += 1
                    state["result"] = "right"
                    session[SOUND_KEY] = "select"
            else:
                state["result"] = "wrong"
                state["reached"] = state["length"] - 1
                session[SOUND_KEY] = "draw"
            save_state(state)
            return redirect(url_for(".index"))


game = Piano()
