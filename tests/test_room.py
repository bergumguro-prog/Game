"""Tests for the rooms: the pages load, the sprites are valid and every
room's layout (room/rooms/) makes sense."""
import pytest

from app import create_app
from core.game_base import MiniGame
from room import objects, sprites, world

MAIN = world.get("main")
ROOMS = list(world.rooms().values())
each_room = pytest.mark.parametrize("room", ROOMS, ids=lambda r: r.id)


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
    for obj in MAIN.objects:
        assert f"object-{obj.id}".encode() in response.data


@each_room
def test_every_room_has_a_page(room):
    response = create_app().test_client().get(f"/rooms/{room.id}")
    assert response.status_code == 200
    assert f'data-room-id="{room.id}"'.encode() in response.data
    for obj in room.objects:
        assert f"object-{obj.id}".encode() in response.data


def test_unknown_room_is_404():
    assert create_app().test_client().get("/rooms/nowhere").status_code == 404


def test_start_with_main_room_then_remember_the_current_room():
    client = create_app().test_client()
    assert b'data-room-id="main"' in client.get("/").data
    client.get("/rooms/room2")
    # "/" is where Esc and "Back to the room" go after a mini-game.
    assert b'data-room-id="room2"' in client.get("/").data


def test_there_are_at_least_three_rooms():
    assert {"main", "room2", "room3"} <= set(world.rooms())


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


@each_room
def test_object_ids_are_unique(room):
    ids = [o.id for o in room.objects]
    assert len(ids) == len(set(ids))


@each_room
def test_objects_use_known_sprites_and_layers(room):
    by_id = {o.id: o for o in room.objects}
    for o in room.objects:
        assert o.sprite in sprites.SPRITES
        assert o.layer in objects.LAYERS
        if o.layer == "on-top":
            assert by_id[o.on].layer == "furniture"


@each_room
def test_room_tiles_are_known_sprites(room):
    assert room.floor_tile in sprites.SPRITES
    assert room.wall_tile in sprites.SPRITES


@each_room
def test_objects_are_inside_the_room(room):
    for o in room.objects:
        w, h = o.size
        assert o.x >= 0 and o.y >= 0, o.id
        assert o.x + w <= room.width, o.id
        assert o.y + h <= room.height, o.id


def is_free(room, x, y):
    """Can the player stand with their sprite's top-left corner at (x, y)?"""
    feet = player_feet(x, y)
    if feet[0] < 0 or feet[1] < room.wall_height:
        return False
    if feet[0] + feet[2] > room.width or feet[1] + feet[3] > room.height:
        return False
    return not any(overlaps(feet, o.hitbox_rect) for o in room.objects if o.solid)


@each_room
def test_player_starts_in_a_free_spot_on_the_floor(room):
    assert is_free(room, *room.start)


def test_lower_furniture_is_drawn_in_front():
    by_id = {o.id: o for o in MAIN.objects}
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


@each_room
def test_interactable_objects_link_to_their_game_or_placeholder(room):
    app = create_app()
    html = app.test_client().get(f"/rooms/{room.id}").data.decode()
    for o in room.objects:
        if o.game:
            assert o.prompt
            if o.game in app.extensions["games"]:
                expected = app.extensions["games"][o.game].url
            else:
                expected = "/games/placeholder/?game="
            assert f'data-url="{expected}' in html, o.id


def test_the_three_games_are_in_the_main_room():
    slugs = {o.game for o in MAIN.objects if o.game}
    assert {"tictactoe", "hangman", "chess"} <= slugs


@each_room
def test_interactable_objects_are_solid_furniture(room):
    for o in room.objects:
        if o.game:
            assert o.solid, o.id


# --- Polish: transitions, hover, sounds (issue #9) ---

SOUND_NAMES = ["open", "back", "select", "move", "win", "lose", "draw", "door"]


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


def walkable_spots(room):
    """Every spot the player can walk to from the start (a flood fill)."""
    from collections import deque

    seen = {room.start}
    queue = deque(seen)
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (x + dx, y + dy)
            if nxt not in seen and is_free(room, *nxt):
                seen.add(nxt)
                queue.append(nxt)
    return seen


def can_reach(spots, rect, reach):
    hx, hy, hw, hh = objects.PLAYER_HITBOX
    return any(
        overlaps((x + hx - reach, y + hy - reach, hw + 2 * reach, hh + 2 * reach), rect)
        for x, y in spots
    )


@each_room
def test_every_game_object_can_be_reached_on_foot(room):
    """Walk the room from the start and check the player can get close
    enough to press E at each game object."""
    spots = walkable_spots(room)
    for o in room.objects:
        if o.game:
            assert can_reach(spots, o.hitbox_rect, objects.INTERACT_REACH), f"can't reach {o.id}"


# --- Doors between rooms (issue #45) ---

ALL_EXITS = [(room, exit) for room in ROOMS for exit in room.exits]
each_exit = pytest.mark.parametrize(
    "room,exit", ALL_EXITS, ids=lambda v: getattr(v, "id", None))


@each_room
def test_exit_ids_are_unique(room):
    ids = [e.id for e in room.exits]
    assert len(ids) == len(set(ids))


@each_exit
def test_every_door_leads_to_a_door_that_leads_back(room, exit):
    other_room = world.get(exit.to_room)
    assert other_room is not None, f"{exit.to_room} doesn't exist"
    other = other_room.exit(exit.to_exit)
    assert other is not None, f"{exit.to_room} has no exit {exit.to_exit}"
    assert (other.to_room, other.to_exit) == (room.id, exit.id)


@each_exit
def test_doors_sit_in_a_wall(room, exit):
    assert exit.side in world.SIDES
    if exit.side in ("top", "bottom"):
        assert 1 <= exit.at and exit.at + world.DOOR_WIDTH <= room.width - 1
    else:  # side doors open onto the floor, below the back wall
        assert room.wall_height <= exit.at and exit.at + world.DOOR_WIDTH <= room.height - 1


@each_exit
def test_arriving_through_a_door_puts_the_player_in_a_free_spot(room, exit):
    x, y, _ = exit.arrival(room)
    assert is_free(room, x, y)
    # ...and not already in the doorway, so they don't bounce straight back.
    assert not overlaps(player_feet(x, y), exit.trigger_rect(room))


@each_exit
def test_every_door_can_be_reached_on_foot(room, exit):
    assert can_reach(walkable_spots(room), exit.trigger_rect(room), 0), exit.id


def test_every_room_can_be_reached_from_the_main_room():
    seen, todo = {"main"}, ["main"]
    while todo:
        for exit in world.get(todo.pop()).exits:
            if exit.to_room not in seen:
                seen.add(exit.to_room)
                todo.append(exit.to_room)
    assert seen == set(world.rooms())


def test_rooms_show_their_doors():
    html = create_app().test_client().get("/rooms/room2").data.decode()
    for exit in world.get("room2").exits:
        assert f'data-exit="{exit.id}"' in html
        assert f'data-url="{exit.url}"' in html


def test_coming_through_a_door_stands_in_front_of_it():
    client = create_app().test_client()
    exit = world.get("room2").exit("to-main")
    x, y, facing = exit.arrival(world.get("room2"))
    html = client.get("/rooms/room2?via=to-main").data.decode()
    S = sprites.SCALE
    assert f'data-x="{x * S}" data-y="{y * S}"' in html
    assert f'data-facing="{facing}"' in html
    assert 'data-arrived="true"' in html
    # A made-up exit just uses the room's normal start spot.
    html = client.get("/rooms/room2?via=nowhere").data.decode()
    assert 'data-arrived' not in html


def test_walking_through_a_door_changes_the_current_room():
    client = create_app().test_client()
    client.get("/rooms/room3?via=to-room2")
    assert b'data-room-id="room3"' in client.get("/").data


def test_door_fade_timings_are_theme_variables():
    theme = open("static/css/theme.css").read()
    for var in ["--door-enter-ms", "--door-leave-ms"]:
        assert f"{var}:" in theme


# --- Placeholder games in the new rooms (issue #46) ---

@pytest.mark.parametrize("room_id", ["room2", "room3"])
def test_new_rooms_have_one_or_two_game_objects(room_id):
    games = [o for o in world.get(room_id).objects if o.game]
    assert 1 <= len(games) <= 2


def test_placeholder_object_opens_coming_soon_until_its_game_exists():
    """Swapping a placeholder for a real game only needs a game with the
    same slug: the room links to it automatically."""
    class Arcade(MiniGame):
        slug = "arcade"
        title = "Arcade"

        def register_routes(self, bp):
            pass

    app = create_app()
    client = app.test_client()
    assert 'data-url="/games/placeholder/?game=Arcade+games"' in client.get("/rooms/room2").data.decode()
    app.extensions["games"]["arcade"] = Arcade()
    assert 'data-url="/games/arcade/"' in client.get("/rooms/room2").data.decode()
