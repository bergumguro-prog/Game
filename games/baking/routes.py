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
from games.baking import art, ingredients, logic, recipes  # noqa: F401  (art adds the icons)
from room import sprites

SESSION_KEY = "baking"
SOUND_KEY = "baking_sound"
MESSAGE_KEY = "baking_message"   # a one-time message for the next page


def mistake_message(kind, detail):
    name = ingredients.INGREDIENTS[detail].name if detail in ingredients.INGREDIENTS else ""
    if kind == "wrong":
        return f"{name.capitalize()} isn't in this recipe. Back it goes!"
    if kind == "order":
        return f"Oops, {name} wasn't next on the recipe card. In it goes anyway!"
    return None


def now():
    """The time in seconds (its own function so tests can fake the oven clock)."""
    return time.time()


def load_bake():
    bake = session.get(SESSION_KEY)
    return bake if isinstance(bake, dict) and logic.is_valid(bake) else None


def act(action, *args, sound="select"):
    """Run a logic action on the saved bake and save it if something changed.
    A new mistake gets a friendly message on the next page."""
    bake = load_bake()
    if bake:
        before = len(bake["mistakes"])
        if action(bake, *args):
            session[SESSION_KEY] = bake
            if sound:
                session[SOUND_KEY] = sound
            if len(bake["mistakes"]) > before:
                message = mistake_message(*bake["mistakes"][-1])
                if message:
                    session[MESSAGE_KEY] = message
                    session[SOUND_KEY] = "back"
    return redirect(url_for(".index"))


def current_step(bake):
    """Which line of the recipe card's steps you're on (0-based)."""
    phase = bake["phase"]
    if phase == "gather":
        return 1 if bake["bowl"] else 0
    return {"mix": 2, "pour": 3, "bake": 4, "baking": 4}.get(phase)


def bowl_sprite(bake):
    """Empty, lumpy (not mixed yet) or smooth (mixed)."""
    if bake["phase"] in ("pour",):
        return "bowl-smooth"
    if bake["phase"] in ("bake", "baking", "done") or not bake["bowl"]:
        return "bowl-empty"
    if bake["phase"] == "mix" and bake["stirs"] * 2 >= logic.recipe_of(bake).stirs:
        return "bowl-smooth"
    return "bowl-lumpy"


def muffin_look(bake):
    """Which muffin picture to show: the color from the oven timing, flat if
    there were lots of mistakes."""
    timing = {tuple(m) for m in bake["mistakes"] if m[0] in ("pale", "dark")}
    if ("dark", "very") in timing:
        look = "very-dark"
    elif ("pale", "very") in timing:
        look = "very-pale"
    elif ("dark", "a bit") in timing:
        look = "dark"
    elif ("pale", "a bit") in timing:
        look = "pale"
    else:
        look = "golden"
    return f"muffin-{look}" + ("-flat" if logic.stars(bake) == 1 else "")


def ingredient_state(bake, item):
    if item in bake["bowl"]:
        return "in-bowl"
    if item in bake["counter"]:
        return "on-counter"
    return "needed"


class Baking(MiniGame):
    slug = "baking"
    title = "Baking"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            bake = load_bake()
            recipe = logic.recipe_of(bake) if bake else None
            icons = {i: sprites.render(f"ing-{i}", "ing-icon") for i in ingredients.INGREDIENTS}
            return render_template(
                "baking.html",
                game=self,
                bake=bake,
                recipe=recipe,
                recipes=list(recipes.recipes().values()),
                ingredients=ingredients.INGREDIENTS,
                icons=icons,
                shelf=ingredients.kept_in(bake["open"]) if bake and bake["open"] else [],
                states={i: ingredient_state(bake, i) for i in recipe.ingredients} if recipe else {},
                step=current_step(bake) if bake else None,
                bowl=sprites.render(bowl_sprite(bake), "bowl-art") if bake else None,
                tin=sprites.render("tin-full" if bake and bake["phase"] in ("bake", "baking", "done") else "tin-empty", "tin-art"),
                oven=sprites.render("oven", "oven-art"),
                oven_muffins=sprites.render("oven-muffins", "oven-muffins-art"),
                oven_seconds=round(now() - bake["oven_start"], 1) if bake and bake["phase"] == "baking" else 0,
                stars=logic.stars(bake) if bake and bake["phase"] == "done" else 0,
                notes=logic.notes(bake) if bake and bake["phase"] == "done" else [],
                muffin=sprites.render(muffin_look(bake), "muffin-art") if bake and bake["phase"] == "done" else None,
                star=sprites.render("bake-star", "bake-star"),
                star_empty=sprites.render("bake-star-empty", "bake-star"),
                fridge=sprites.render("fridge", "storage-art"),
                pantry=sprites.render("pantry", "storage-art"),
                message=session.pop(MESSAGE_KEY, None),
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
            response = act(logic.take_out, now(), sound=None)
            bake = load_bake()
            if bake and bake["phase"] == "done":
                session[SOUND_KEY] = "win" if logic.stars(bake) == 3 else "draw"
            return response


game = Baking()
