"""Recipes for the baking game, one file each, found automatically.

To add a recipe, make a new file here that defines `recipe = Recipe(...)`
(copy blueberry_muffins.py). Ingredients must exist in ingredients.py.
"""
import importlib
import pkgutil
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Recipe:
    id: str
    name: str
    ingredients: tuple   # ingredient ids, in the order they go into the bowl
    steps: tuple         # what the recipe card says, one line per step
    bake: tuple = (8.0, 11.0)   # (from, to): seconds in the oven for a perfect bake
    burnt_after: float = 15.0   # seconds after which it's badly overbaked
    pale_before: float = 5.0    # seconds before which it's badly underbaked
    stirs: int = 6              # how many stirs mixing takes


@lru_cache(maxsize=None)
def recipes():
    """Every recipe, by id."""
    found = {}
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        module = importlib.import_module(f"{__name__}.{info.name}")
        found[module.recipe.id] = module.recipe
    return found


def get(recipe_id):
    return recipes().get(recipe_id)
