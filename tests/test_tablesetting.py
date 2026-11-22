"""Tests for table decorating: the catalog, the art and the page."""
import pytest

from app import create_app
from games.tablesetting import art, catalog
from room import sprites


def test_catalog_has_everything_for_a_table():
    wanted = {"plate", "bowl", "cup", "glass", "fork", "knife", "spoon",
              "napkin", "candle", "vase"}
    assert wanted <= set(catalog.ITEMS)
    assert len(catalog.CATEGORIES) >= 5


@pytest.mark.parametrize("item", list(catalog.ITEMS.values()), ids=lambda i: i.id)
def test_every_item_has_art_in_every_color_and_fits_the_table(item):
    for color in item.colors:
        name = catalog.sprite_for(item.id, color)
        rows = sprites.SPRITES[name]
        assert all(len(r) == len(rows[0]) for r in rows)
        assert all(ch == "." or ch in sprites.PALETTE for r in rows for ch in r)
    w, h = catalog.size(item.id)
    assert w <= catalog.TABLE_W and h <= catalog.TABLE_H


def test_colored_art_changes_only_the_color_letters():
    pink = art.colored(art.PLATE, "pink")
    mint = art.colored(art.PLATE, "mint")
    assert pink != mint and len(pink) == len(mint)


@pytest.fixture
def client():
    return create_app().test_client()


def test_page_has_the_menu_the_table_and_the_tools(client):
    html = client.get("/games/tablesetting/").data.decode()
    for item in catalog.ITEMS.values():
        assert f'data-item="{item.id}"' in html
        for color in item.colors:
            assert f'id="art-{item.id}-{color}"' in html
    assert 'id="table"' in html and f'data-max="{catalog.MAX_ITEMS}"' in html
    assert 'id="rotate-item"' in html and 'id="remove-item"' in html
    assert "tablesetting.js" in html


def test_kitchen_table_opens_table_decorating(client):
    html = client.get("/rooms/kitchen").data.decode()
    assert 'data-url="/games/tablesetting/"' in html


def test_page_has_a_way_back(client):
    html = client.get("/games/tablesetting/").data.decode()
    assert 'href="/"' in html and 'data-scene="game"' in html


# --- Colors, tablecloths and clear table (issue #60) ---

def test_items_with_several_colors_have_swatches(client):
    html = client.get("/games/tablesetting/").data.decode()
    for item in catalog.ITEMS.values():
        if len(item.colors) > 1:
            for color in item.colors:
                assert f'class="swatch' in html
                assert f'data-item="{item.id}" data-color="{color}"' in html


def test_plates_and_tablecloths_have_several_choices():
    assert len(catalog.ITEMS["plate"].colors) >= 3
    assert len(catalog.CLOTHS) >= 4


def test_page_has_tablecloth_choices_and_clear_table(client):
    html = client.get("/games/tablesetting/").data.decode()
    for key in catalog.CLOTHS:
        assert f'class="cloth-choice' in html and f'data-cloth="{key}"' in html
    assert 'id="clear-table"' in html and 'id="undo-clear"' in html


def test_tablecloth_colors_are_theme_variables():
    theme = open("static/css/theme.css").read()
    for var in ("--cloth-gingham:", "--cloth-mint:", "--cloth-lace:", "--cloth-stripe:"):
        assert var in theme


# --- Saving the table (issue #61) ---

from games.tablesetting import logic  # noqa: E402

GOOD = {"cloth": "lace", "items": [
    {"id": "plate", "color": "mint", "x": 10, "y": 12, "r": 0},
    {"id": "knife", "color": "pink", "x": 30, "y": 12, "r": 1},
]}


def test_a_good_table_is_stored_small():
    assert logic.clean(GOOD) == {"cloth": "lace", "items": [
        ["plate", "mint", 10, 12, 0], ["knife", "pink", 30, 12, 1]]}


@pytest.mark.parametrize("change", [
    {"cloth": "velvet"},
    {"items": [{"id": "sofa", "color": "pink", "x": 0, "y": 0, "r": 0}]},
    {"items": [{"id": "plate", "color": "black", "x": 0, "y": 0, "r": 0}]},
    {"items": [{"id": "plate", "color": "pink", "x": 999, "y": 0, "r": 0}]},
    {"items": [{"id": "plate", "color": "pink", "x": -1, "y": 0, "r": 0}]},
    {"items": [{"id": "plate", "color": "pink", "x": 1.5, "y": 0, "r": 0}]},
    {"items": [{"id": "plate", "color": "pink", "x": 0, "y": 0, "r": 4}]},
    {"items": [{"id": "plate", "color": "pink", "x": 0, "y": 0, "r": 0}] * (catalog.MAX_ITEMS + 1)},
    {"items": "everything"},
])
def test_bad_tables_are_refused(change):
    with pytest.raises(ValueError):
        logic.clean({**GOOD, **change})


def test_saving_and_coming_back(client):
    response = client.post("/games/tablesetting/save", json=GOOD)
    assert response.status_code == 200 and response.get_json() == {"ok": True, "count": 2}
    client.get("/rooms/kitchen")                    # walk away...
    html = client.get("/games/tablesetting/").data.decode()   # ...and come back
    assert 'data-cloth="lace"' in html
    assert "&#34;id&#34;: &#34;plate&#34;" in html or '"id": "plate"' in html


def test_a_bad_save_changes_nothing(client):
    client.post("/games/tablesetting/save", json=GOOD)
    response = client.post("/games/tablesetting/save", json={"cloth": "velvet", "items": []})
    assert response.status_code == 400
    with client.session_transaction() as s:
        assert s["tablesetting"]["cloth"] == "lace"
    assert client.post("/games/tablesetting/save", data="not json").status_code == 400


def test_a_broken_saved_table_starts_empty(client):
    with client.session_transaction() as s:
        s["tablesetting"] = {"cloth": "gingham", "items": [["plate", "pink", 5000, 0, 0]]}
    html = client.get("/games/tablesetting/").data.decode()
    assert 'data-items="[]"' in html
