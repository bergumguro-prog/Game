"""Saving the table: checking what the editor sends and storing it small.

The editor sends {"cloth": "gingham", "items": [{"id", "color", "x", "y", "r"}, ...]}.
It's checked here (known things, allowed colors, on the table, not too many)
and stored in the session as short lists: [id, color, x, y, r].
"""
from games.tablesetting import catalog


def clean(data):
    """The checked table as {"cloth", "items"} in the short stored form.
    Raises ValueError if anything in it isn't allowed."""
    if not isinstance(data, dict):
        raise ValueError("not a table")
    cloth = data.get("cloth", catalog.DEFAULT_CLOTH)
    if cloth not in catalog.CLOTHS:
        raise ValueError(f"unknown tablecloth {cloth!r}")
    items = data.get("items", [])
    if not isinstance(items, list) or len(items) > catalog.MAX_ITEMS:
        raise ValueError("too many things on the table")
    stored = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("not a table item")
        kind = catalog.ITEMS.get(item.get("id"))
        if kind is None or item.get("color") not in kind.colors:
            raise ValueError("unknown item or color")
        x, y, r = item.get("x"), item.get("y"), item.get("r", 0)
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in (x, y, r)):
            raise ValueError("positions must be whole numbers")
        w, h = catalog.size(kind.id)
        if not (0 <= x <= catalog.TABLE_W - w and 0 <= y <= catalog.TABLE_H - h and 0 <= r <= 3):
            raise ValueError("that's off the table")
        stored.append([kind.id, item["color"], x, y, r])
    return {"cloth": cloth, "items": stored}


def for_editor(saved):
    """The stored table in the editor's form. Anything broken is dropped."""
    try:
        table = clean({
            "cloth": (saved or {}).get("cloth", catalog.DEFAULT_CLOTH),
            "items": [dict(zip(("id", "color", "x", "y", "r"), i)) for i in (saved or {}).get("items", [])],
        })
    except (ValueError, TypeError):
        return {"cloth": catalog.DEFAULT_CLOTH, "items": []}
    return {
        "cloth": table["cloth"],
        "items": [dict(zip(("id", "color", "x", "y", "r"), i)) for i in table["items"]],
    }
