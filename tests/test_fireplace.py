"""Tests for the fireplace scene: the page and its pixel art."""
from app import create_app
from games.fireplace import art
from room import sprites, world


def test_fireplace_page_loads_with_the_fire():
    client = create_app().test_client()
    response = client.get("/games/fireplace/")
    assert response.status_code == 200
    html = response.data.decode()
    assert 'id="fire"' in html
    assert f'width="{art.OPENING[2]}" height="{art.OPENING[3]}"' in html
    assert 'sprite-hearth"' in html and 'sprite-hearth-logs"' in html
    assert "fireplace.js" in html


def test_fireplace_has_a_way_back():
    html = create_app().test_client().get("/games/fireplace/").data.decode()
    assert 'href="/"' in html             # back to the room you came from
    assert 'data-scene="game"' in html    # so Esc goes back too


def test_living_room_fireplace_opens_the_scene():
    html = create_app().test_client().get("/rooms/livingroom").data.decode()
    assert 'data-url="/games/fireplace/"' in html


def test_fireplace_files_are_served():
    client = create_app().test_client()
    for name in ("fireplace.js", "fireplace.css"):
        assert client.get(f"/games/fireplace/static/{name}").status_code == 200


def test_the_opening_is_see_through_and_framed():
    frame = sprites.SPRITES["hearth"]
    assert len(frame) == art.FRAME_H and len(frame[0]) == art.FRAME_W
    ox, oy, ow, oh = art.OPENING
    # the middle of the opening is transparent, the stone around it is not
    assert frame[oy + oh // 2][ox + ow // 2] == "."
    assert frame[oy + oh // 2][ox - 1] == "o"
    for y in range(art.FRAME_H):
        for x in range(art.FRAME_W):
            if art.in_opening(x, y):
                assert frame[y][x] == ".", (x, y)


def test_logs_sit_inside_the_opening():
    lx, ly = art.LOGS_POS
    ox, oy, ow, oh = art.OPENING
    assert ox <= lx and lx + art.LOGS_W <= ox + ow
    assert ly + art.LOGS_H == oy + oh


def test_fireplace_colors_are_theme_variables():
    theme = open("static/css/theme.css").read()
    for var in ("--fireplace-wall", "--fireplace-inside", "--fireplace-inside-line",
                "--fireplace-glow-1"):
        assert f"{var}:" in theme
