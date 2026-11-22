"""Tests for dishwashing: dirty dishes in logic.py and the web routes."""
import pytest

from app import create_app
from games.dishes import art, logic


# --- Dirty dishes ---

def test_a_round_has_every_kind_of_dish():
    dishes = logic.new_round(1)
    assert sorted(d["dish"] for d in dishes) == sorted(logic.ROUND)
    assert {"fork", "spoon", "knife", "plate", "cup", "pot", "pan"} <= {d["dish"] for d in dishes}


def test_same_seed_same_dishes():
    assert logic.new_round(4) == logic.new_round(4)
    assert logic.new_round(4) != logic.new_round(5)


@pytest.mark.parametrize("seed", range(20))
def test_dirt_sits_on_the_dish_and_spots_do_not_pile_up(seed):
    for dish in logic.new_round(seed):
        surface = set(logic.surface(dish["dish"]))
        assert len(dish["spots"]) == logic.DISHES[dish["dish"]]["spots"]
        for spot in dish["spots"]:
            assert spot["pixels"], dish["dish"]
            for x, y, color in spot["pixels"]:
                assert (x, y) in surface
                assert color in logic.DIRT[spot["dirt"]].colors


def test_pots_and_pans_get_burnt_food_and_cutlery_never_does():
    for seed in range(10):
        for dish in logic.new_round(seed):
            kinds = [s["dirt"] for s in dish["spots"]]
            if dish["dish"] in ("pot", "pan"):
                assert kinds.count("burnt") >= 2
            if dish["dish"] in ("fork", "spoon", "knife"):
                assert "burnt" not in kinds


def test_tough_dirt_takes_more_scrubbing_than_light_dirt():
    assert logic.DIRT["burnt"].hp >= 5 * logic.DIRT["crumbs"].hp
    assert logic.DIRT["crumbs"].hp < logic.DIRT["sauce"].hp < logic.DIRT["burnt"].hp


def test_dish_art_rows_are_even():
    for name, rows in art.DISH_ART.items():
        assert all(len(r) == len(rows[0]) for r in rows), name


# --- Routes ---

@pytest.fixture
def client():
    return create_app().test_client()


def state(client):
    with client.session_transaction() as s:
        return s.get("dishes")


def test_start_screen_then_first_dish(client):
    html = client.get("/games/dishes/").data.decode()
    assert "Start washing" in html and 'id="sink"' not in html
    client.post("/games/dishes/start")
    html = client.get("/games/dishes/").data.decode()
    first = logic.new_round(state(client)["seed"])[0]
    assert 'id="sink"' in html and f"a dirty {first['dish']}" in html
    assert html.count('class="dirt ') == len(first["spots"])
    assert f'data-hold-rate="{logic.HOLD_RATE}"' in html


def test_cleaning_brings_the_next_dish_and_ignores_repeats(client):
    client.post("/games/dishes/start")
    client.post("/games/dishes/clean", data={"item": "0"})
    assert state(client)["index"] == 1
    client.post("/games/dishes/clean", data={"item": "0"})     # an old page
    client.post("/games/dishes/clean", data={"item": "nope"})
    assert state(client)["index"] == 1


def test_cleaning_every_dish_finishes_the_round(client):
    client.post("/games/dishes/start")
    for i in range(len(logic.ROUND)):
        client.post("/games/dishes/clean", data={"item": str(i)})
    s = state(client)
    assert s["index"] == len(logic.ROUND) and s["finished"] is not None
    assert "All clean!" in client.get("/games/dishes/").data.decode()


def test_kitchen_sink_opens_dishwashing(client):
    html = client.get("/rooms/kitchen").data.decode()
    assert 'data-url="/games/dishes/"' in html


def test_dishes_page_has_a_way_back(client):
    html = client.get("/games/dishes/").data.decode()
    assert 'href="/"' in html and 'data-scene="game"' in html


# --- Drying rack, time and stars (issue #54) ---

def test_dirtier_rounds_get_more_time():
    clean_ish = [{"dish": "fork", "spots": [{"hp": 1.0}]}]
    dirty = [{"dish": "pan", "spots": [{"hp": 7.0}, {"hp": 7.0}]}]
    assert logic.par_seconds(dirty) > logic.par_seconds(clean_ish)


@pytest.mark.parametrize("seconds,expected", [(10, 3), (60, 3), (61, 2), (90, 2), (91, 1), (500, 1)])
def test_star_rating(seconds, expected):
    assert logic.stars(seconds, 60) == expected


def test_stack_and_rack_follow_the_round(client):
    client.post("/games/dishes/start")
    for i in range(3):
        client.post("/games/dishes/clean", data={"item": str(i)})
    html = client.get("/games/dishes/").data.decode()
    assert 'aria-label="Drying rack: 3 clean"' in html
    assert f'aria-label="{len(logic.ROUND) - 4} dirty dishes waiting"' in html
    assert 'id="dish-time"' in html and 'id="rack-next"' in html


def finish_round(client, seconds):
    client.post("/games/dishes/start")
    with client.session_transaction() as s:
        game = dict(s["dishes"])
        game["started"] -= seconds
        s["dishes"] = game          # put it back so the change is saved
    for i in range(len(logic.ROUND)):
        client.post("/games/dishes/clean", data={"item": str(i)})
    return client.get("/games/dishes/").data.decode()


def test_a_quick_round_gets_three_stars_and_the_win_sound(client):
    html = finish_round(client, 5)
    assert 'aria-label="3 out of 3 stars"' in html
    assert 'data-sound="win"' in html
    assert "Wash again" in html


def test_a_slow_round_gets_one_star(client):
    html = finish_round(client, 3600)
    assert 'aria-label="1 out of 3 stars"' in html
    assert 'data-sound="draw"' in html
    assert "60:0" in html                     # shows the time it took


@pytest.mark.parametrize("name", ["scrub", "sparkle"])
def test_dish_sounds_are_served(client, name):
    response = client.get(f"/static/sounds/{name}.wav")
    assert response.status_code == 200 and response.data[:4] == b"RIFF"
