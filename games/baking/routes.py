"""Baking: /games/baking/

Pick a recipe, gather the ingredients from the fridge and the pantry, add
them to the bowl in order, mix, pour, bake and take the muffins out at the
right time. The rules are in logic.py; recipes are files in recipes/.

    GET  /games/baking/              the kitchen counter
    POST /games/baking/start         start a recipe (field "recipe")
    POST /games/baking/open          open the fridge or pantry (field "place", empty to close)
    POST /games/baking/pick          take an ingredient out (field "item")
    POST /games/baking/add           put an ingredient from the counter in the bowl (field "item")
    POST /games/baking/stir          stir the batter
    POST /games/baking/pour          pour it into the muffin tin
    POST /games/baking/oven          put the tin in the oven
    POST /games/baking/take-out      take it out again
"""
import time

from flask import redirect, render_template, request, session, url_for

from core.game_base import MiniGame
from games.baking import ingredients, logic, recipes

SESSION_KEY = "baking"
SOUND_KEY = "baking_sound"


def now():
    """The time in seconds (its own function so tests can fake the oven clock)."""
    return time.time()


def load_bake():
    bake = session.get(SESSION_KEY)
    return bake if isinstance(bake, dict) and logic.is_valid(bake) else None


def act(action, *args, sound="select"):
    """Run a logic action on the saved bake and save it if something changed."""
    bake = load_bake()
    if bake and action(bake, *args):
        session[SESSION_KEY] = bake
        if sound:
            session[SOUND_KEY] = sound
    return redirect(url_for(".index"))


class Baking(MiniGame):
    slug = "baking"
    title = "Baking"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            bake = load_bake()
            return render_template(
                "baking.html",
                game=self,
                bake=bake,
                recipe=logic.recipe_of(bake) if bake else None,
                recipes=list(recipes.recipes().values()),
                ingredients=ingredients.INGREDIENTS,
                sound=session.pop(SOUND_KEY, None),
            )

        @bp.route("/start", methods=["POST"])
        def start():
            recipe_id = request.form.get("recipe", "")
            if recipes.get(recipe_id):
                session[SESSION_KEY] = logic.new_bake(recipe_id)
            return redirect(url_for(".index"))

        @bp.route("/open", methods=["POST"])
        def open_place():
            return act(logic.open_place, request.form.get("place") or None, sound=None)

        @bp.route("/pick", methods=["POST"])
        def pick():
            return act(logic.pick, request.form.get("item", ""))

        @bp.route("/add", methods=["POST"])
        def add():
            return act(logic.add_to_bowl, request.form.get("item", ""), sound="move")

        @bp.route("/stir", methods=["POST"])
        def stir():
            return act(logic.stir, sound="move")

        @bp.route("/pour", methods=["POST"])
        def pour():
            return act(logic.pour, sound="move")

        @bp.route("/oven", methods=["POST"])
        def oven():
            return act(logic.put_in_oven, now(), sound="move")

        @bp.route("/take-out", methods=["POST"])
        def take_out():
            return act(logic.take_out, now(), sound=None)


game = Baking()
