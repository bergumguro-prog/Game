"""The piano: /games/piano/

Play the piano with the mouse or the computer keyboard (free play).
The notes and keyboard layout are in logic.py; the sounds are made by
tools/make_sounds.py and played by static/piano.js.
"""
from flask import render_template

from core.game_base import MiniGame
from games.piano import logic


class Piano(MiniGame):
    slug = "piano"
    title = "Piano"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            keys = logic.keys()
            return render_template(
                "piano.html",
                game=self,
                keys=keys,
                white_count=len(logic.WHITE),
            )


game = Piano()
