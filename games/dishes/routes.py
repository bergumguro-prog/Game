"""Dishwashing at the kitchen sink: /games/dishes/

The dirty dishes come one at a time. Scrub the dirt off with the sponge
(drag it, or hold it still over the dirt); when a dish is clean the next one
comes in. The rules and the dirty dishes are made in logic.py; scrubbing
happens in static/dishes.js.

The session keeps only the round's seed, which dish you're on and when you
started; the dishes are made again from the seed.

    GET  /games/dishes/          the sink
    POST /games/dishes/start     start a new stack of dishes
    POST /games/dishes/clean     the current dish is clean (field "item")
"""
import random
import time

from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.dishes import art, logic  # noqa: F401  (art adds the dish sprites)
from room import sprites

SESSION_KEY = "dishes"
SOUND_KEY = "dishes_sound"


def load_state():
    state = session.get(SESSION_KEY) or {}
    try:
        seed = int(state["seed"])
        index = int(state.get("index", 0))
        started = float(state["started"])
        finished = float(state["finished"]) if state.get("finished") is not None else None
    except (TypeError, KeyError, ValueError):
        return None
    if not 0 <= index <= len(logic.ROUND):
        return None
    return {"seed": seed, "index": index, "started": started, "finished": finished}


def save_state(state):
    session[SESSION_KEY] = state


def dish_view(dish):
    w, h = sprites.size(f"dish-{dish['dish']}")
    return {
        "name": dish["dish"],
        "w": w,
        "h": h,
        "svg": sprites.render(f"dish-{dish['dish']}", "dish-art"),
        "spots": [
            {
                "x": s["x"], "y": s["y"], "r": s["r"], "hp": s["hp"], "dirt": s["dirt"],
                "rects": [(x, y, sprites.PALETTE[c]) for x, y, c in s["pixels"]],
            }
            for s in dish["spots"]
        ],
    }


class Dishes(MiniGame):
    slug = "dishes"
    title = "Washing up"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            state = load_state()
            dishes = logic.new_round(state["seed"]) if state else []
            current = dishes[state["index"]] if state and state["index"] < len(dishes) else None
            return render_template(
                "dishes.html",
                game=self,
                state=state,
                dish=dish_view(current) if current else None,
                total=len(logic.ROUND),
                hold_rate=logic.HOLD_RATE,
                drag_pixels=logic.DRAG_PIXELS,
                sponge=sprites.render("sponge", "sponge-art"),
                sound=session.pop(SOUND_KEY, None),
            )

        @bp.route("/start", methods=["POST"])
        def start():
            save_state({"seed": random.randrange(1, 2**31), "index": 0,
                        "started": time.time(), "finished": None})
            return redirect(url_for(".index"))

        @bp.route("/clean", methods=["POST"])
        def clean():
            state = load_state()
            if state and state["finished"] is None:
                try:
                    item = int(request.form.get("item", ""))
                except ValueError:
                    item = -1
                if item == state["index"]:   # ignore repeats and old pages
                    state["index"] += 1
                    if state["index"] == len(logic.ROUND):
                        state["finished"] = time.time()
                    save_state(state)
            return redirect(url_for(".index"))


game = Dishes()
