"""Dishwashing rules, in plain Python.

A round is a stack of dirty dishes made from a seed, so the session only
needs the seed and how far you've got. Each dish has a few dirt spots; each
spot needs some scrubbing ("hp") before it's gone. Tough dirt needs much more
scrubbing than light dirt.

Scrubbing itself happens in the browser (static/dishes.js): holding the
sponge over a spot scrubs HOLD_RATE hp per second, and moving it scrubs one
hp per DRAG_PIXELS screen pixels. Both numbers are sent to the page from here.
"""
import random
from dataclasses import dataclass

from games.dishes import art


@dataclass(frozen=True)
class Dirt:
    name: str
    hp: float         # how much scrubbing it takes
    radius: tuple     # (smallest, biggest) spot radius in art pixels
    colors: str       # palette letters (see room/sprites.py)


DIRT = {
    "crumbs": Dirt("crumbs", 1.0, (1, 2), "ny"),     # light: cutlery and plates
    "coffee": Dirt("coffee", 2.0, (2, 3), "bn"),     # cups
    "sauce": Dirt("sauce", 2.5, (2, 3), "re"),
    "burnt": Dirt("burnt", 7.0, (2, 4), "BH"),       # tough: pots and pans
}

# What each dish can get dirty with, and how many spots it gets.
DISHES = {
    "fork":  {"dirt": ("crumbs", "sauce"), "spots": 2, "tough": 0},
    "spoon": {"dirt": ("crumbs", "sauce"), "spots": 2, "tough": 0},
    "knife": {"dirt": ("crumbs", "sauce"), "spots": 2, "tough": 0},
    "plate": {"dirt": ("crumbs", "sauce"), "spots": 4, "tough": 0},
    "cup":   {"dirt": ("coffee", "crumbs"), "spots": 3, "tough": 0},
    "pot":   {"dirt": ("sauce", "burnt"), "spots": 5, "tough": 2},
    "pan":   {"dirt": ("sauce", "burnt"), "spots": 5, "tough": 3},
}
TOUGH_DIRT = "burnt"

ROUND = ["fork", "spoon", "knife", "plate", "plate", "cup", "pot", "pan"]

HOLD_RATE = 1.0      # hp scrubbed per second while holding the sponge still
DRAG_PIXELS = 220    # screen pixels of sponge movement that scrub 1 hp


def surface(dish):
    """The art pixels of a dish that dirt can sit on: not empty, not outline."""
    rows = art.DISH_ART[dish]
    return [(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch not in ".o"]


def _spot(rng, dish, dirt_name, taken):
    """A dirt spot on the dish, not on top of another one."""
    dirt = DIRT[dirt_name]
    cells = surface(dish)
    on_dish = set(cells)
    radius = rng.randint(*dirt.radius)
    for _ in range(60):
        cx, cy = rng.choice(cells)
        if all((cx - x) ** 2 + (cy - y) ** 2 > (radius + r + 1) ** 2 for x, y, r in taken):
            break
    pixels = []
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            # a ragged edge: the outer ring is only partly dirty
            if (x, y) in on_dish and (d <= (radius - 0.5) ** 2 or (d <= radius ** 2 and rng.random() < 0.5)):
                pixels.append((x, y, rng.choice(dirt.colors)))
    if not pixels:
        pixels = [(cx, cy, dirt.colors[0])]
    taken.append((cx, cy, radius))
    return {"dirt": dirt_name, "x": cx, "y": cy, "r": radius, "hp": dirt.hp, "pixels": pixels}


def make_dish(rng, dish):
    rules = DISHES[dish]
    names = [TOUGH_DIRT] * rules["tough"]
    names += [rng.choice(rules["dirt"]) for _ in range(rules["spots"] - len(names))]
    taken = []
    return {"dish": dish, "spots": [_spot(rng, dish, n, taken) for n in names]}


def new_round(seed):
    """The stack of dirty dishes for this seed, in the order they come."""
    rng = random.Random(seed)
    order = list(ROUND)
    rng.shuffle(order)
    return [make_dish(rng, dish) for dish in order]


def total_hp(dishes):
    return sum(spot["hp"] for dish in dishes for spot in dish["spots"])
