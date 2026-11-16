"""A "coming soon" scene.

Objects in the room whose mini-game isn't built yet lead here, so every
object can already be tried out. It is also the smallest possible example
of a mini-game.
"""
from flask import render_template, request

from core.game_base import MiniGame


class Placeholder(MiniGame):
    slug = "placeholder"
    title = "Coming soon"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            name = request.args.get("game", "This game")
            return render_template("placeholder.html", game=self, name=name)


game = Placeholder()
