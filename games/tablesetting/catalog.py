"""Everything you can put on the table, by category, with its color choices.
The table's size and the tablecloth patterns are here too."""
from dataclasses import dataclass

from games.tablesetting import art
from room import sprites

TABLE_W = 100     # the table top, in art pixels
TABLE_H = 64
MAX_ITEMS = 40    # keeps the saved table small


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    category: str
    colors: tuple   # color choices; the first is the default


ITEMS = {i.id: i for i in [
    Item("plate", "Plate", "Plates & bowls", ("pink", "mint", "cream", "lavender")),
    Item("bowl", "Bowl", "Plates & bowls", ("pink", "mint", "cream", "lavender")),
    Item("cup", "Teacup", "Cups & glasses", ("pink", "mint", "cream", "lavender")),
    Item("glass", "Glass", "Cups & glasses", ("white",)),
    Item("fork", "Fork", "Cutlery", ("pink", "mint")),
    Item("knife", "Knife", "Cutlery", ("pink", "mint")),
    Item("spoon", "Spoon", "Cutlery", ("pink", "mint")),
    Item("napkin", "Napkin", "Napkins", ("pink", "mint", "lavender", "cream")),
    Item("candle", "Candle", "Candles & flowers", ("cream", "pink", "lavender")),
    Item("vase", "Vase of flowers", "Candles & flowers", ("mint", "pink", "lavender")),
    Item("teapot", "Teapot", "Treats", ("pink", "mint", "cream")),
    Item("cake-stand", "Cake stand", "Treats", ("white",)),
]}

CATEGORIES = list(dict.fromkeys(i.category for i in ITEMS.values()))

# Tablecloths: the CSS in static/tablesetting.css draws each pattern.
CLOTHS = {
    "gingham": "Pink gingham",
    "mint": "Mint",
    "lace": "Cream lace",
    "stripes": "Lavender stripes",
}
DEFAULT_CLOTH = "gingham"


def sprite_for(item_id, color):
    return art.sprite_name(item_id, color)


def size(item_id):
    return sprites.size(sprite_for(item_id, ITEMS[item_id].colors[0]))


# Register a sprite for every item in every color.
for _item in ITEMS.values():
    for _color in _item.colors:
        sprites.SPRITES[art.sprite_name(_item.id, _color)] = art.colored(art.SHAPES[_item.id], _color)
