"""Entry point: creates the Flask app and registers the room and every mini-game.

Run with:  python app.py
"""
from flask import Flask

from room.routes import room_bp

# Every mini-game is an instance of core.game_base.MiniGame.
# Adding a game = import it here and add it to this list.
GAMES = []


def create_app():
    app = Flask(__name__)
    app.register_blueprint(room_bp)
    for game in GAMES:
        app.register_blueprint(game.blueprint)
    return app


if __name__ == "__main__":
    # Port 5050 because macOS uses port 5000 for AirPlay.
    create_app().run(debug=True, port=5050)
