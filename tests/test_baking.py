"""Tests for baking: ingredients, recipes, the rules in logic.py and the routes."""
import pytest

from app import create_app
from games.baking import ingredients, logic, recipes

MUFFINS = "blueberry-muffins"


def muffins():
    return recipes.get(MUFFINS)


def gathered(bake):
    """Pick every recipe ingredient from the right place, in recipe order."""
    for item in logic.recipe_of(bake).ingredients:
        logic.open_place(bake, ingredients.INGREDIENTS[item].place)
        assert logic.pick(bake, item)
    return bake


def ready_for_oven():
    bake = gathered(logic.new_bake(MUFFINS))
    for item in muffins().ingredients:
        logic.add_to_bowl(bake, item)
    while bake["phase"] == "mix":
        logic.stir(bake)
    logic.pour(bake)
    return bake


# --- Ingredients and recipes ---

def test_blueberry_muffins_recipe():
    r = muffins()
    assert r.name == "Blueberry muffins"
    assert set(r.ingredients) == {"flour", "sugar", "baking-powder", "salt",
                                  "milk", "eggs", "butter", "blueberries"}


def test_ingredients_come_from_the_right_place():
    fridge = {i.id for i in ingredients.kept_in("fridge")}
    pantry = {i.id for i in ingredients.kept_in("pantry")}
    assert {"milk", "eggs", "butter", "blueberries"} <= fridge
    assert {"flour", "sugar", "baking-powder", "salt"} <= pantry


@pytest.mark.parametrize("recipe", list(recipes.recipes().values()), ids=lambda r: r.id)
def test_every_recipe_uses_known_ingredients_and_leaves_extras_to_choose_from(recipe):
    assert all(i in ingredients.INGREDIENTS for i in recipe.ingredients)
    for place in ingredients.PLACES:
        extras = [i for i in ingredients.kept_in(place) if i.id not in recipe.ingredients]
        assert len(extras) >= 2, place
    low, high = recipe.bake
    assert recipe.pale_before < low < high < recipe.burnt_after


# --- Gathering ---

def test_you_can_only_pick_from_the_open_place():
    bake = logic.new_bake(MUFFINS)
    assert not logic.pick(bake, "milk")            # nothing open
    logic.open_place(bake, "pantry")
    assert not logic.pick(bake, "milk")            # milk is in the fridge
    logic.open_place(bake, "fridge")
    assert logic.pick(bake, "milk")
    assert bake["counter"] == ["milk"]
    assert not logic.pick(bake, "milk")            # already out


def test_picking_something_not_in_the_recipe_is_a_mistake_and_it_goes_back():
    bake = logic.new_bake(MUFFINS)
    logic.open_place(bake, "fridge")
    assert logic.pick(bake, "cheese")
    assert bake["counter"] == []
    assert bake["mistakes"] == [["wrong", "cheese"]]


def test_adding_in_recipe_order_is_not_a_mistake():
    bake = gathered(logic.new_bake(MUFFINS))
    for item in muffins().ingredients:
        assert logic.add_to_bowl(bake, item)
    assert bake["mistakes"] == []
    assert bake["phase"] == "mix" and bake["open"] is None


def test_adding_out_of_order_is_a_mistake_but_it_still_goes_in():
    bake = gathered(logic.new_bake(MUFFINS))
    logic.add_to_bowl(bake, "sugar")               # flour should be first
    assert bake["bowl"] == ["sugar"]
    assert bake["mistakes"] == [["order", "sugar"]]
    logic.add_to_bowl(bake, "flour")               # flour is next now, fine
    assert bake["mistakes"] == [["order", "sugar"]]


def test_only_counter_items_go_in_the_bowl():
    bake = logic.new_bake(MUFFINS)
    assert not logic.add_to_bowl(bake, "flour")


# --- Mixing, pouring, baking ---

def test_steps_happen_in_a_sensible_order():
    bake = logic.new_bake(MUFFINS)
    assert not logic.stir(bake)
    assert not logic.pour(bake)
    assert not logic.put_in_oven(bake, 0)
    assert not logic.take_out(bake, 0)
    bake = gathered(bake)
    for item in muffins().ingredients:
        logic.add_to_bowl(bake, item)
    assert not logic.pour(bake)                    # mix first
    for _ in range(muffins().stirs - 1):
        logic.stir(bake)
    assert bake["phase"] == "mix"
    logic.stir(bake)
    assert bake["phase"] == "pour"
    assert logic.pour(bake) and bake["phase"] == "bake"
    assert logic.put_in_oven(bake, 100.0) and bake["phase"] == "baking"
    assert not logic.open_place(bake, "fridge")


@pytest.mark.parametrize("seconds,mistakes", [
    (9.5, []),
    (6.0, [["pale", "a bit"]]),
    (2.0, [["pale", "very"], ["pale", "very"]]),
    (13.0, [["dark", "a bit"]]),
    (30.0, [["dark", "very"], ["dark", "very"]]),
])
def test_oven_timing(seconds, mistakes):
    bake = ready_for_oven()
    logic.put_in_oven(bake, 100.0)
    logic.take_out(bake, 100.0 + seconds)
    assert bake["phase"] == "done"
    assert bake["mistakes"] == mistakes
    assert bake["baked_for"] == seconds


# --- Stars ---

def test_perfect_bake_gets_three_stars():
    bake = ready_for_oven()
    logic.put_in_oven(bake, 0)
    logic.take_out(bake, 9)
    assert logic.stars(bake) == 3 and logic.notes(bake) == []


def test_one_step_out_of_order_gets_two_stars():
    bake = gathered(logic.new_bake(MUFFINS))
    order = list(muffins().ingredients)
    order[0], order[1] = order[1], order[0]
    for item in order:
        logic.add_to_bowl(bake, item)
    assert logic.stars(bake) == 2
    assert any("out of order" in n for n in logic.notes(bake))


def test_several_mistakes_get_one_star_but_still_muffins():
    bake = logic.new_bake(MUFFINS)
    logic.open_place(bake, "fridge")
    logic.pick(bake, "pickles")
    bake = gathered(bake)
    for item in muffins().ingredients:
        logic.add_to_bowl(bake, item)
    while bake["phase"] == "mix":
        logic.stir(bake)
    logic.pour(bake)
    logic.put_in_oven(bake, 0)
    logic.take_out(bake, 40)
    assert bake["phase"] == "done"
    assert logic.stars(bake) == 1
    assert len(logic.notes(bake)) == 2


def test_broken_saved_bakes_are_rejected():
    assert not logic.is_valid({"recipe": "nope"})
    bad = logic.new_bake(MUFFINS)
    bad["bowl"] = ["pickles"]
    assert not logic.is_valid(bad)
    assert logic.is_valid(logic.new_bake(MUFFINS))


# --- Routes ---

@pytest.fixture
def client():
    return create_app().test_client()


def saved(client):
    with client.session_transaction() as s:
        return s.get("baking")


def test_fridge_and_pantry_open_baking(client):
    html = client.get("/rooms/kitchen").data.decode()
    assert html.count('data-url="/games/baking/"') == 2


def test_a_whole_bake_through_the_routes(client, monkeypatch):
    assert client.get("/games/baking/").status_code == 200
    client.post("/games/baking/start", data={"recipe": MUFFINS})
    for item in muffins().ingredients:
        client.post("/games/baking/open", data={"place": ingredients.INGREDIENTS[item].place})
        client.post("/games/baking/pick", data={"item": item})
    for item in muffins().ingredients:
        client.post("/games/baking/add", data={"item": item})
    for _ in range(muffins().stirs):
        client.post("/games/baking/stir")
    client.post("/games/baking/pour")
    clock = [1000.0]
    monkeypatch.setattr("games.baking.routes.now", lambda: clock[0])
    client.post("/games/baking/oven")
    clock[0] += 9.0
    client.post("/games/baking/take-out")
    bake = saved(client)
    assert bake["phase"] == "done" and bake["mistakes"] == []


def test_unknown_recipe_and_garbled_actions_are_ignored(client):
    client.post("/games/baking/start", data={"recipe": "cake-of-lies"})
    assert saved(client) is None
    client.post("/games/baking/start", data={"recipe": MUFFINS})
    client.post("/games/baking/open", data={"place": "attic"})
    client.post("/games/baking/pick", data={"item": "<script>"})
    assert saved(client) == logic.new_bake(MUFFINS)


# --- Gathering page (issue #56) ---

def test_open_fridge_shows_its_items_including_ones_not_in_the_recipe(client):
    client.post("/games/baking/start", data={"recipe": MUFFINS})
    client.post("/games/baking/open", data={"place": "fridge"})
    html = client.get("/games/baking/").data.decode()
    for item in ingredients.kept_in("fridge"):
        assert f'name="item" value="{item.id}"' in html
    assert 'value="flour"' not in html.split('class="shelf')[1].split("</div>")[0]


def test_recipe_card_tracks_each_ingredient(client):
    client.post("/games/baking/start", data={"recipe": MUFFINS})
    client.post("/games/baking/open", data={"place": "pantry"})
    client.post("/games/baking/pick", data={"item": "flour"})
    client.post("/games/baking/pick", data={"item": "sugar"})
    client.post("/games/baking/add", data={"item": "flour"})
    html = client.get("/games/baking/").data.decode()
    card = html.split('class="recipe-card"')[1].split("</aside>")[0]
    assert card.count("ing-in-bowl") == 1 and card.count("ing-on-counter") == 1
    assert card.count("ing-needed") == 6


def test_wrong_pick_says_so_once(client):
    client.post("/games/baking/start", data={"recipe": MUFFINS})
    client.post("/games/baking/open", data={"place": "fridge"})
    client.post("/games/baking/pick", data={"item": "pickles"})
    html = client.get("/games/baking/").data.decode()
    assert "Pickles isn&#39;t in this recipe" in html or "Pickles isn't in this recipe" in html
    assert "isn" not in client.get("/games/baking/").data.decode().split("bake-message")[1][:120]


def test_ingredient_icons_exist_for_everything():
    from games.baking import art
    assert set(art.ICONS) == set(ingredients.INGREDIENTS)


# --- Bowl, mixing, tin and oven page (issue #57) ---

def bake_in_session(client, bake):
    with client.session_transaction() as s:
        s["baking"] = bake


def test_mixing_shows_a_stir_button_with_progress(client):
    bake = gathered(logic.new_bake(MUFFINS))
    for item in muffins().ingredients:
        logic.add_to_bowl(bake, item)
    logic.stir(bake)
    bake_in_session(client, bake)
    html = client.get("/games/baking/").data.decode()
    assert f"Stir (1/{muffins().stirs})" in html
    assert "sprite-bowl-lumpy" in html


def test_bowl_looks_smooth_once_mixed():
    from games.baking import routes
    bake = ready_for_oven()
    bake["phase"] = "pour"
    assert routes.bowl_sprite(bake) == "bowl-smooth"
    assert routes.bowl_sprite(logic.new_bake(MUFFINS)) == "bowl-empty"


def test_oven_page_knows_the_recipe_timing(client):
    bake = ready_for_oven()
    logic.put_in_oven(bake, 0)
    bake_in_session(client, bake)
    html = client.get("/games/baking/").data.decode()
    low, high = muffins().bake
    assert 'id="oven"' in html
    assert f'data-from="{low}"' in html and f'data-to="{high}"' in html
    assert f'data-burnt="{muffins().burnt_after}"' in html
    assert "Take them out!" in html


def test_ding_sound_is_served(client):
    response = client.get("/static/sounds/ding.wav")
    assert response.status_code == 200 and response.data[:4] == b"RIFF"


def test_oven_muffin_colors_are_theme_variables():
    theme = open("static/css/theme.css").read()
    for stage in ("raw", "pale", "golden", "brown", "dark"):
        assert f"--muffin-{stage}:" in theme
