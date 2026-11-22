"""Blueberry muffins: the first recipe."""
from games.baking.recipes import Recipe

recipe = Recipe(
    id="blueberry-muffins",
    name="Blueberry muffins",
    ingredients=(
        "flour", "sugar", "baking-powder", "salt",   # from the pantry
        "eggs", "milk", "butter", "blueberries",     # from the fridge
    ),
    steps=(
        "Gather the ingredients from the fridge and the pantry.",
        "Add them to the bowl in the order on this card.",
        "Mix until smooth.",
        "Pour the batter into the muffin tin.",
        "Bake, and take them out when they're golden.",
    ),
    bake=(8.0, 11.0),
    burnt_after=15.0,
    pale_before=5.0,
)
