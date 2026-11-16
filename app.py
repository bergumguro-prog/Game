"""Entry point: creates the Flask app and registers the room and every mini-game.

Run with:  python app.py

Mini-games are found automatically: every folder in games/ with a routes.py
that defines `game = SomeMiniGame()` is registered. Adding a game never
requires changing this file.
"""
import importlib
import pkgutil

from flask import Flask

import games
from room.routes import room_bp


def discover_games():
    """Import games/<name>/routes.py for every game folder and collect `game`."""
    found = []
    for info in sorted(pkgutil.iter_modules(games.__path__), key=lambda i: i.name):
        if not info.ispkg:
            continue
        module = importlib.import_module(f"games.{info.name}.routes")
        found.append(module.game)
    return found


def create_app():
    app = Flask(__name__)
    app.register_blueprint(room_bp)
    registry = {}
    for game in discover_games():
        app.register_blueprint(game.blueprint)
        registry[game.slug] = game
    # The room looks games up here to know where each object leads.
    app.extensions["games"] = registry
    return app


if __name__ == "__main__":
    # Port 5050 because macOS uses port 5000 for AirPlay.
    create_app().run(debug=True, port=5050)
