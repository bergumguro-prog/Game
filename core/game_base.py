"""The interface every mini-game follows.

A mini-game is a folder in games/ with a routes.py that defines a subclass of
MiniGame. The base class builds a Flask blueprint for it, so every game gets:

    /games/<slug>/          -> the game's page (you write this route)
    /games/<slug>/static/   -> files from the game's own static/ folder

and its templates/ folder is searched for templates.

Example (games/tictactoe/routes.py):

    from flask import render_template
    from core.game_base import MiniGame

    class TicTacToe(MiniGame):
        slug = "tictactoe"
        title = "Tic-tac-toe"

        def register_routes(self, bp):
            @bp.route("/")
            def index():
                return render_template("tictactoe.html", game=self)

    game = TicTacToe()

app.py finds `game` automatically. Then add an object in one of the room
files in room/rooms/ with game="tictactoe".
"""
from abc import ABC, abstractmethod

from flask import Blueprint


class MiniGame(ABC):
    slug: str = ""   # used in the URL, e.g. "chess" -> /games/chess/
    title: str = ""  # human-readable name shown in the room

    def __init__(self):
        if not self.slug or not self.title:
            raise ValueError(f"{type(self).__name__} must set slug and title")
        self.blueprint = Blueprint(
            self.slug,
            type(self).__module__,  # lets Flask find the game's own folder
            template_folder="templates",
            static_folder="static",
            url_prefix=f"/games/{self.slug}",
        )
        self.register_routes(self.blueprint)

    @property
    def url(self):
        return f"/games/{self.slug}/"

    @abstractmethod
    def register_routes(self, bp: Blueprint) -> None:
        """Add the game's routes to its blueprint. Must include "/"."""
