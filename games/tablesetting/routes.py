"""Table decorating: /games/tablesetting/

A free, creative mode with no score: drag plates, cups, cutlery, napkins,
candles, flowers and treats onto the kitchen table, then move, rotate or
remove them. The items are in catalog.py and the art in art.py; the editor
itself is static/tablesetting.js.
"""
from flask import render_template

from core.game_base import MiniGame
from games.tablesetting import catalog
from room import sprites


def menu():
    """The menu, by category: each item with its art in every color."""
    groups = []
    for category in catalog.CATEGORIES:
        items = []
        for item in catalog.ITEMS.values():
            if item.category != category:
                continue
            w, h = catalog.size(item.id)
            items.append({
                "id": item.id, "name": item.name, "colors": item.colors, "w": w, "h": h,
                "art": {c: sprites.render(catalog.sprite_for(item.id, c), "item-art") for c in item.colors},
            })
        groups.append({"name": category, "entries": items})
    return groups


class TableSetting(MiniGame):
    slug = "tablesetting"
    title = "Decorate the table"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            return render_template(
                "tablesetting.html",
                game=self,
                menu=menu(),
                table={"w": catalog.TABLE_W, "h": catalog.TABLE_H, "max": catalog.MAX_ITEMS},
                cloth=catalog.DEFAULT_CLOTH,
                cloths=catalog.CLOTHS,
            )


game = TableSetting()
