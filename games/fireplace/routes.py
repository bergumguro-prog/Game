"""The fireplace: /games/fireplace/

Not a game, just a cozy scene to look at: a crackling fire in the living
room's fireplace. The flames, embers and sparks are animated in
static/fireplace.js; the fireplace itself is pixel art from art.py.
"""
from flask import render_template

from core.game_base import MiniGame
from games.fireplace import art
from room import sprites


class Fireplace(MiniGame):
    slug = "fireplace"
    title = "Fireplace"

    def register_routes(self, bp):
        @bp.route("/")
        def index():
            ox, oy, ow, oh = art.OPENING
            lx, ly = art.LOGS_POS
            return render_template(
                "fireplace.html",
                game=self,
                frame={"w": art.FRAME_W, "h": art.FRAME_H},
                opening={"x": ox, "y": oy, "w": ow, "h": oh},
                logs={"x": lx, "y": ly, "w": art.LOGS_W, "h": art.LOGS_H},
                hearth_svg=sprites.render("hearth"),
                logs_svg=sprites.render("hearth-logs"),
            )


game = Fireplace()
