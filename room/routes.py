"""Flask blueprint for the room: serves the hub world page at "/"."""
from flask import Blueprint, render_template

from room import objects

room_bp = Blueprint(
    "room",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/room/static",
)


@room_bp.route("/")
def index():
    return render_template(
        "room.html",
        room_width=objects.ROOM_WIDTH,
        room_height=objects.ROOM_HEIGHT,
        player_size=objects.PLAYER_SIZE,
        player_speed=objects.PLAYER_SPEED,
        player_start=objects.PLAYER_START,
        objects=objects.OBJECTS,
    )
