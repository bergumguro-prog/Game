"""Flask blueprint for the room: serves the hub world page at "/".

It converts the layout in objects.py (art pixels) into screen pixels for
the template, and works out where each interactable object leads.
"""
from urllib.parse import urlencode

from flask import Blueprint, current_app, render_template

from room import objects, sprites

room_bp = Blueprint(
    "room",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/room/static",
)

S = sprites.SCALE


def game_url(slug, prompt):
    """URL of a mini-game, or the "coming soon" scene if it isn't built yet."""
    games = current_app.extensions.get("games", {})
    if slug in games:
        return games[slug].url
    name = prompt.removeprefix("play ").capitalize() if prompt else slug
    return "/games/placeholder/?" + urlencode({"game": name})


def _object_view(obj, by_id):
    w, h = obj.size
    hx, hy, hw, hh = obj.hitbox_rect
    return {
        "id": obj.id,
        "layer": obj.layer,
        "solid": obj.solid,
        "x": obj.x * S, "y": obj.y * S, "w": w * S, "h": h * S,
        "hit": (hx * S, hy * S, hw * S, hh * S),
        "z": objects.z_index(obj, by_id),
        "svg": sprites.render(obj.sprite),
        "url": game_url(obj.game, obj.prompt) if obj.game else None,
        "prompt": obj.prompt or (f"play {obj.game}" if obj.game else None),
    }


@room_bp.route("/")
def index():
    by_id = {o.id: o for o in objects.OBJECTS}
    pw, ph = sprites.size("player-down")
    hx, hy, hw, hh = objects.PLAYER_HITBOX
    return render_template(
        "room.html",
        room={
            "w": objects.ROOM_WIDTH * S,
            "h": objects.ROOM_HEIGHT * S,
            "wall_h": objects.WALL_HEIGHT * S,
            "reach": objects.INTERACT_REACH * S,
        },
        wall_svg=sprites.render_pattern(
            "wallpaper-tile", objects.ROOM_WIDTH, objects.WALL_HEIGHT),
        floor_svg=sprites.render_pattern(
            "floor-tile", objects.ROOM_WIDTH, objects.ROOM_HEIGHT - objects.WALL_HEIGHT),
        player={
            "x": objects.PLAYER_START[0] * S,
            "y": objects.PLAYER_START[1] * S,
            "w": pw * S, "h": ph * S,
            "hit": (hx * S, hy * S, hw * S, hh * S),
            "speed": objects.PLAYER_SPEED * S,
            "down": sprites.render("player-down", "player-sprite face-down"),
            "up": sprites.render("player-up", "player-sprite face-up"),
            "side": sprites.render("player-side", "player-sprite face-side"),
        },
        objects=[_object_view(o, by_id) for o in objects.OBJECTS],
    )
