"""Tests for the room: the page loads, the sprites are valid and the layout
in objects.py makes sense."""
import pytest

from app import create_app
from core.game_base import MiniGame
from room import objects, sprites


def overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def player_feet(x, y):
    dx, dy, w, h = objects.PLAYER_HITBOX
    return (x + dx, y + dy, w, h)


def test_room_page_loads():
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b'id="player"' in response.data
    for obj in objects.OBJECTS:
        assert f"object-{obj.id}".encode() in response.data


def test_static_files_are_served():
    client = create_app().test_client()
    for url in [
        "/room/static/player.js",
        "/room/static/room.css",
        "/static/css/theme.css",
        "/static/css/pixels.css",
        "/static/fonts/PixelifySans.ttf",
    ]:
        assert client.get(url).status_code == 200, url


@pytest.mark.parametrize("name", sorted(sprites.SPRITES))
def test_sprite_rows_have_equal_width_and_known_colors(name):
    rows = sprites.SPRITES[name]
    assert all(len(row) == len(rows[0]) for row in rows)
    for row in rows:
        for ch in row:
            assert ch == "." or ch in sprites.PALETTE, f"unknown letter {ch!r}"


def test_every_palette_color_has_a_css_class_and_variable():
    css = open("static/css/pixels.css").read()
    theme = open("static/css/theme.css").read()
    for color in sprites.PALETTE.values():
        assert f".px-{color} " in css
        assert f"--px-{color}:" in theme


def test_object_ids_are_unique():
    ids = [o.id for o in objects.OBJECTS]
    assert len(ids) == len(set(ids))


def test_objects_use_known_sprites_and_layers():
    by_id = {o.id: o for o in objects.OBJECTS}
    for o in objects.OBJECTS:
        assert o.sprite in sprites.SPRITES
        assert o.layer in objects.LAYERS
        if o.layer == "on-top":
            assert by_id[o.on].layer == "furniture"


def test_objects_are_inside_the_room():
    for o in objects.OBJECTS:
        w, h = o.size
        assert o.x >= 0 and o.y >= 0, o.id
        assert o.x + w <= objects.ROOM_WIDTH, o.id
        assert o.y + h <= objects.ROOM_HEIGHT, o.id


def test_player_starts_in_a_free_spot_on_the_floor():
    feet = player_feet(*objects.PLAYER_START)
    assert feet[1] >= objects.WALL_HEIGHT
    assert feet[0] + feet[2] <= objects.ROOM_WIDTH
    assert feet[1] + feet[3] <= objects.ROOM_HEIGHT
    for o in objects.OBJECTS:
        if o.solid:
            assert not overlaps(feet, o.hitbox_rect), f"player starts inside {o.id}"


def test_lower_furniture_is_drawn_in_front():
    by_id = {o.id: o for o in objects.OBJECTS}
    assert objects.z_index(by_id["bookshelf-left"], by_id) > objects.z_index(by_id["bed"], by_id)
    assert objects.z_index(by_id["cake"], by_id) > objects.z_index(by_id["tea-table"], by_id)


def test_minigame_requires_slug_and_title():
    class Nameless(MiniGame):
        def register_routes(self, bp):
            pass

    with pytest.raises(ValueError):
        Nameless()


# --- Interacting with objects (issue #2) ---

def test_games_are_discovered_automatically():
    app = create_app()
    assert "placeholder" in app.extensions["games"]


def test_placeholder_scene_shows_the_game_name():
    client = create_app().test_client()
    response = client.get("/games/placeholder/?game=Chess")
    assert response.status_code == 200
    assert b"Chess" in response.data
    assert b"js/scenes.js" in response.data  # Esc goes back to the room
    assert b'data-scene="game"' in response.data


def test_room_is_marked_as_the_room_scene():
    client = create_app().test_client()
    assert b'data-scene="room"' in client.get("/").data


def test_interactable_objects_link_to_their_game_or_placeholder():
    app = create_app()
    client = app.test_client()
    html = client.get("/").data.decode()
    for o in objects.OBJECTS:
        if o.game:
            assert o.prompt
            if o.game in app.extensions["games"]:
                expected = app.extensions["games"][o.game].url
            else:
                expected = "/games/placeholder/?game="
            assert f'data-url="{expected}' in html, o.id


def test_every_planned_game_has_an_object_in_the_room():
    slugs = {o.game for o in objects.OBJECTS if o.game}
    assert {"tictactoe", "hangman", "chess"} <= slugs


def test_interactable_objects_are_solid_furniture():
    for o in objects.OBJECTS:
        if o.game:
            assert o.solid, o.id


# --- Polish: transitions, hover, sounds (issue #9) ---

SOUND_NAMES = ["open", "back", "select", "move", "win", "lose", "draw"]


@pytest.mark.parametrize("name", SOUND_NAMES)
def test_sound_files_are_served(name):
    response = create_app().test_client().get(f"/static/sounds/{name}.wav")
    assert response.status_code == 200
    assert response.data[:4] == b"RIFF"


def test_every_page_has_a_mute_button():
    client = create_app().test_client()
    for url in ["/", "/games/placeholder/?game=Chess"]:
        assert b'id="mute-toggle"' in client.get(url).data


def test_motion_timings_are_theme_variables():
    theme = open("static/css/theme.css").read()
    for var in ["--scene-enter-ms", "--scene-leave-ms", "--hover-ms", "--hover-lift"]:
        assert f"{var}:" in theme


def test_every_game_object_can_be_reached_on_foot():
    """Walk the room from the start (flood fill over every free spot) and
    check the player can get close enough to press E at each game object."""
    from collections import deque

    hx, hy, hw, hh = objects.PLAYER_HITBOX
    solids = [o.hitbox_rect for o in objects.OBJECTS if o.solid]

    def free(x, y):
        feet = (x + hx, y + hy, hw, hh)
        if feet[0] < 0 or feet[1] < objects.WALL_HEIGHT:
            return False
        if feet[0] + hw > objects.ROOM_WIDTH or feet[1] + hh > objects.ROOM_HEIGHT:
            return False
        return not any(overlaps(feet, s) for s in solids)

    seen = {objects.PLAYER_START}
    queue = deque(seen)
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (x + dx, y + dy)
            if nxt not in seen and free(*nxt):
                seen.add(nxt)
                queue.append(nxt)

    r = objects.INTERACT_REACH
    for o in objects.OBJECTS:
        if o.game:
            assert any(
                overlaps((x + hx - r, y + hy - r, hw + 2 * r, hh + 2 * r), o.hitbox_rect)
                for x, y in seen
            ), f"can't reach {o.id}"
