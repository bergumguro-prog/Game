"""Every ingredient in the kitchen and where it's kept.

Recipes pick from these. The fridge and the pantry show every ingredient
kept there, so there are always some that aren't in the recipe.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ingredient:
    id: str
    name: str
    place: str   # "fridge" or "pantry"


INGREDIENTS = {i.id: i for i in [
    # in the fridge
    Ingredient("milk", "milk", "fridge"),
    Ingredient("eggs", "eggs", "fridge"),
    Ingredient("butter", "butter", "fridge"),
    Ingredient("blueberries", "blueberries", "fridge"),
    Ingredient("cheese", "cheese", "fridge"),
    Ingredient("jam", "strawberry jam", "fridge"),
    Ingredient("carrots", "carrots", "fridge"),
    Ingredient("pickles", "pickles", "fridge"),
    # in the pantry
    Ingredient("flour", "flour", "pantry"),
    Ingredient("sugar", "sugar", "pantry"),
    Ingredient("baking-powder", "baking powder", "pantry"),
    Ingredient("salt", "salt", "pantry"),
    Ingredient("rice", "rice", "pantry"),
    Ingredient("pasta", "pasta", "pantry"),
    Ingredient("cocoa", "cocoa", "pantry"),
    Ingredient("oats", "oats", "pantry"),
]}

PLACES = ("fridge", "pantry")


def kept_in(place):
    return [i for i in INGREDIENTS.values() if i.place == place]
