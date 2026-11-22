"""The baking game's rules, in plain Python.

A bake goes through these phases:

    gather -> mix -> pour -> bake -> baking -> done

- gather: open the fridge or the pantry and pick ingredients onto the
  counter, then add them from the counter to the bowl. Picking something
  that isn't in the recipe is a mistake (it goes back). Adding to the bowl
  out of the recipe's order is a mistake (it still goes in).
- mix: once everything is in the bowl, stir a few times.
- pour: pour the batter into the muffin tin.
- bake: put the tin in the oven...
- baking: ...and take it out. Too early or too late is a mistake; far too
  early or late counts as two.

The game is a plain dict so it can live in the Flask session. Every action
returns True if it did something.
"""
from games.baking import ingredients, recipes

PHASES = ("gather", "mix", "pour", "bake", "baking", "done")


def new_bake(recipe_id):
    return {
        "recipe": recipe_id,
        "phase": "gather",
        "open": None,        # "fridge", "pantry" or None
        "counter": [],       # picked ingredients waiting to go in the bowl
        "bowl": [],          # in the order they were added
        "stirs": 0,
        "oven_start": None,
        "baked_for": None,
        "mistakes": [],      # [kind, detail] pairs, e.g. ["wrong", "cheese"]
    }


def recipe_of(bake):
    return recipes.get(bake["recipe"])


def is_valid(bake):
    """Is this a bake we can trust (e.g. loaded back from the session)?"""
    try:
        recipe = recipe_of(bake)
        return (
            recipe is not None
            and bake["phase"] in PHASES
            and bake["open"] in (None, *ingredients.PLACES)
            and all(i in recipe.ingredients for i in bake["counter"] + bake["bowl"])
            and isinstance(bake["mistakes"], list)
        )
    except (KeyError, TypeError):
        return False


# --- Gathering ---------------------------------------------------------------

def open_place(bake, place):
    if bake["phase"] != "gather" or place not in (*ingredients.PLACES, None):
        return False
    bake["open"] = place
    return True


def pick(bake, item):
    """Take `item` out of the open fridge or pantry."""
    ingredient = ingredients.INGREDIENTS.get(item)
    if bake["phase"] != "gather" or ingredient is None or ingredient.place != bake["open"]:
        return False
    if item in bake["counter"] or item in bake["bowl"]:
        return False
    if item not in recipe_of(bake).ingredients:
        bake["mistakes"].append(["wrong", item])   # not in the recipe: it goes back
        return True
    bake["counter"].append(item)
    return True


def next_for_bowl(bake):
    """The ingredient the recipe wants in the bowl next."""
    return next((i for i in recipe_of(bake).ingredients if i not in bake["bowl"]), None)


def add_to_bowl(bake, item):
    if bake["phase"] != "gather" or item not in bake["counter"]:
        return False
    if item != next_for_bowl(bake):
        bake["mistakes"].append(["order", item])
    bake["counter"].remove(item)
    bake["bowl"].append(item)
    if len(bake["bowl"]) == len(recipe_of(bake).ingredients):
        bake["phase"] = "mix"
        bake["open"] = None
    return True


# --- Mixing, pouring, baking -------------------------------------------------

def stir(bake):
    if bake["phase"] != "mix":
        return False
    bake["stirs"] += 1
    if bake["stirs"] >= recipe_of(bake).stirs:
        bake["phase"] = "pour"
    return True


def pour(bake):
    if bake["phase"] != "pour":
        return False
    bake["phase"] = "bake"
    return True


def put_in_oven(bake, now):
    if bake["phase"] != "bake":
        return False
    bake["phase"] = "baking"
    bake["oven_start"] = now
    return True


def take_out(bake, now):
    if bake["phase"] != "baking":
        return False
    seconds = max(0.0, now - bake["oven_start"])
    bake["baked_for"] = round(seconds, 1)
    recipe = recipe_of(bake)
    low, high = recipe.bake
    if seconds < recipe.pale_before:
        bake["mistakes"] += [["pale", "very"], ["pale", "very"]]
    elif seconds < low:
        bake["mistakes"].append(["pale", "a bit"])
    elif seconds > recipe.burnt_after:
        bake["mistakes"] += [["dark", "very"], ["dark", "very"]]
    elif seconds > high:
        bake["mistakes"].append(["dark", "a bit"])
    bake["phase"] = "done"
    return True


# --- Rating ------------------------------------------------------------------

def stars(bake):
    """3: no mistakes. 2: one or two small ones. 1: several (but there are
    still muffins!)."""
    count = len(bake["mistakes"])
    if count == 0:
        return 3
    if count <= 2:
        return 2
    return 1


def notes(bake):
    """Friendly sentences about what went wrong, for the results."""
    names = ingredients.INGREDIENTS
    out = []
    wrong = [names[d].name for kind, d in bake["mistakes"] if kind == "wrong"]
    if wrong:
        out.append("Not in the recipe: " + ", ".join(wrong) + ".")
    order = [names[d].name for kind, d in bake["mistakes"] if kind == "order"]
    if order:
        out.append("Added out of order: " + ", ".join(order) + ".")
    timing = {tuple(m) for m in bake["mistakes"] if m[0] in ("pale", "dark")}
    if ("pale", "very") in timing:
        out.append("Taken out far too early: they're very pale.")
    elif ("pale", "a bit") in timing:
        out.append("Taken out a little early: they're a bit pale.")
    if ("dark", "very") in timing:
        out.append("Left in far too long: they're quite dark.")
    elif ("dark", "a bit") in timing:
        out.append("Left in a little long: they're a bit dark.")
    return out
