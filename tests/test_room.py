"""Tests for the room: the page loads and the layout in objects.py makes sense."""
import pytest

from app import create_app
from core.game_base import MiniGame
from room import objects


def overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def rect(obj):
    return (obj.x, obj.y, obj.width, obj.height)


def test_room_page_loads():
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b'id="player"' in response.data
    for obj in objects.OBJECTS:
        assert f"object-{obj.id}".encode() in response.data


def test_room_static_files_are_served():
    client = create_app().test_client()
    assert client.get("/room/static/player.js").status_code == 200
    assert client.get("/room/static/room.css").status_code == 200
    assert client.get("/static/css/theme.css").status_code == 200


def test_object_ids_are_unique():
    ids = [o.id for o in objects.OBJECTS]
    assert len(ids) == len(set(ids))


def test_objects_are_inside_the_room():
    for o in objects.OBJECTS:
        assert o.x >= 0 and o.y >= 0
        assert o.x + o.width <= objects.ROOM_WIDTH
        assert o.y + o.height <= objects.ROOM_HEIGHT


def test_player_starts_in_a_free_spot():
    px, py = objects.PLAYER_START
    player = (px, py, objects.PLAYER_SIZE, objects.PLAYER_SIZE)
    assert px >= 0 and py >= 0
    assert px + objects.PLAYER_SIZE <= objects.ROOM_WIDTH
    assert py + objects.PLAYER_SIZE <= objects.ROOM_HEIGHT
    for o in objects.OBJECTS:
        if o.solid:
            assert not overlaps(player, rect(o)), f"player starts inside {o.id}"


def test_minigame_requires_slug_and_title():
    class Nameless(MiniGame):
        def register_routes(self, bp):
            pass

    with pytest.raises(ValueError):
        Nameless()
