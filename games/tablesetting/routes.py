"""Table decorating: /games/tablesetting/

A free, creative mode with no score: drag plates, cups, cutlery, napkins,
candles, flowers and treats onto the kitchen table, then move, rotate or
remove them. The items are in catalog.py and the art in art.py; the editor
itself is static/tablesetting.js.

The table is saved in the Flask session after every change, so it's still
there next time you come back to the kitchen.

    GET  /games/tablesetting/       the table, as you left it
    POST /games/tablesetting/save   the whole table as JSON (see logic.py)
"""
import json

from flask import jsonify, render_template, request, session

from core.game_base import MiniGame
from games.tablesetting import catalog, logic
from room import sprites

SESSION_KEY = "tablesetting"


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
            saved = logic.for_editor(session.get(SESSION_KEY))
            return render_template(
                "tablesetting.html",
                game=self,
                menu=menu(),
                table={"w": catalog.TABLE_W, "h": catalog.TABLE_H, "max": catalog.MAX_ITEMS},
                cloth=saved["cloth"],
                cloths=catalog.CLOTHS,
                items_json=json.dumps(saved["items"]),
            )

        @bp.route("/save", methods=["POST"])
        def save():
            try:
                table = logic.clean(request.get_json(silent=True))
            except ValueError as problem:
                return jsonify(ok=False, error=str(problem)), 400
            session[SESSION_KEY] = table
            return jsonify(ok=True, count=len(table["items"]))


game = TableSetting()
