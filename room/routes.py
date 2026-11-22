"""Flask blueprint for the rooms of the hub world.

    /               -> the room the player is in (the bedroom at first)
    /rooms/<id>     -> a specific room; also remembers it as the current room
    /rooms/<id>?via=<exit>  -> arrive through a door: the player stands in
                               front of that exit instead of at the start

The current room is kept in the Flask session, so leaving a mini-game
(Esc or "Back to the room", which both go to "/") returns to the right room.

It converts a room's layout (art pixels, see room/world.py and room/rooms/)
into screen pixels for the template, and works out where each interactable
object leads.
"""
from urllib.parse import urlencode

from flask import Blueprint, abort, current_app, render_template, request, session

from room import objects, sprites, world

room_bp = Blueprint(
    "room",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/room/static",
)

S = sprites.SCALE
SESSION_KEY = "room"


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


def _exit_view(exit, room):
    sprite = f"door-{exit.side}"
    x, y = exit.sprite_position(room)
    w, h = sprites.size(sprite)
    tx, ty, tw, th = exit.trigger_rect(room)
    return {
        "id": exit.id,
        "side": exit.side,
        "walk": world.WALK_DIRECTION[exit.side],
        "url": exit.url,
        "x": x * S, "y": y * S, "w": w * S, "h": h * S,
        "hit": (tx * S, ty * S, tw * S, th * S),
        "svg": sprites.render(sprite),
    }


def render_room(room, via=None):
    """The room page. `via` is the exit the player came in through, if any."""
    session[SESSION_KEY] = room.id
    by_id = {o.id: o for o in room.objects}
    arrived = room.exit(via)
    x, y, facing = arrived.arrival(room) if arrived else (*room.start, "down")
    pw, ph = sprites.size("player-down")
    hx, hy, hw, hh = objects.PLAYER_HITBOX
    return render_template(
        "room.html",
        room={
            "id": room.id,
            "name": room.name,
            "theme": room.theme,
            "w": room.width * S,
            "h": room.height * S,
            "wall_h": room.wall_height * S,
            "reach": objects.INTERACT_REACH * S,
        },
        wall_svg=sprites.render_pattern(room.wall_tile, room.width, room.wall_height),
        floor_svg=sprites.render_pattern(room.floor_tile, room.width, room.floor_height),
        player={
            "x": x * S,
            "y": y * S,
            "facing": facing,
            "arrived": bool(arrived),
            "w": pw * S, "h": ph * S,
            "hit": (hx * S, hy * S, hw * S, hh * S),
            "speed": objects.PLAYER_SPEED * S,
            "down": sprites.render("player-down", "player-sprite face-down"),
            "up": sprites.render("player-up", "player-sprite face-up"),
            "side": sprites.render("player-side", "player-sprite face-side"),
        },
        objects=[_object_view(o, by_id) for o in room.objects],
        exits=[_exit_view(e, room) for e in room.exits],
    )


@room_bp.route("/")
def index():
    room = world.get(session.get(SESSION_KEY)) or world.get(world.DEFAULT_ROOM)
    return render_room(room)


@room_bp.route("/rooms/<room_id>")
def show_room(room_id):
    room = world.get(room_id)
    if room is None:
        abort(404)
    return render_room(room, via=request.args.get("via"))
