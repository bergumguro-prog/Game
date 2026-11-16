"""Tests for tic-tac-toe: the rules in logic.py and the web routes."""
import pytest

from app import create_app
from games.tictactoe import logic


# --- Rules ---

def test_x_starts_and_players_alternate():
    board = logic.EMPTY_BOARD
    assert logic.current_player(board) == "X"
    board = logic.play(board, 4)
    assert board[4] == "X"
    assert logic.current_player(board) == "O"
    board = logic.play(board, 0)
    assert board[0] == "O"


def test_taken_square_cannot_be_played():
    board = logic.play(logic.EMPTY_BOARD, 4)
    with pytest.raises(ValueError):
        logic.play(board, 4)


@pytest.mark.parametrize("index", [-1, 9, 100])
def test_out_of_range_square_is_rejected(index):
    with pytest.raises(ValueError):
        logic.play(logic.EMPTY_BOARD, index)


@pytest.mark.parametrize("line", logic.LINES)
def test_every_line_wins(line):
    board = ["."] * 9
    for i in line:
        board[i] = "X"
    board = "".join(board)
    assert logic.winner(board) == "X"
    assert logic.winning_line(board) == line


def test_no_moves_after_a_win():
    board = "XXXOO...."
    assert logic.is_over(board)
    assert logic.legal_moves(board) == []
    with pytest.raises(ValueError):
        logic.play(board, 8)


def test_draw_is_detected():
    board = "XOXXOOOXX"
    assert logic.winner(board) is None
    assert logic.is_draw(board)
    assert logic.is_over(board)


def test_board_validation():
    assert logic.is_valid_board(logic.EMPTY_BOARD)
    assert logic.is_valid_board("XO.......")
    assert not logic.is_valid_board("XX.......")  # X can't be two ahead
    assert not logic.is_valid_board("O........")  # O can't start
    assert not logic.is_valid_board("XO")
    assert not logic.is_valid_board(None)


# --- Web routes ---

@pytest.fixture
def client():
    return create_app().test_client()


def board_in_session(client):
    with client.session_transaction() as s:
        return s["tictactoe"]["board"]


def test_page_shows_empty_board(client):
    html = client.get("/games/tictactoe/").data.decode()
    assert html.count('class="ttt-cell') == 9
    assert "X&#39;s turn" in html or "X's turn" in html


def test_clicking_squares_plays_moves(client):
    client.post("/games/tictactoe/move", data={"cell": "4"})
    client.post("/games/tictactoe/move", data={"cell": "0"})
    assert board_in_session(client) == "O...X...."


def test_illegal_and_garbled_moves_are_ignored(client):
    client.post("/games/tictactoe/move", data={"cell": "4"})
    client.post("/games/tictactoe/move", data={"cell": "4"})
    client.post("/games/tictactoe/move", data={"cell": "banana"})
    assert board_in_session(client) == "....X...."


def test_win_is_shown_and_scored(client):
    for cell in [0, 3, 1, 4, 2]:  # X takes the top row
        client.post("/games/tictactoe/move", data={"cell": str(cell)})
    html = client.get("/games/tictactoe/").data.decode()
    assert "X wins!" in html
    assert html.count("ttt-cell-winning") == 3
    assert "disabled" in html
    with client.session_transaction() as s:
        assert s["tictactoe"]["score"]["X"] == 1


def test_new_game_clears_board_but_keeps_score(client):
    for cell in [0, 3, 1, 4, 2]:
        client.post("/games/tictactoe/move", data={"cell": str(cell)})
    client.post("/games/tictactoe/new")
    with client.session_transaction() as s:
        assert s["tictactoe"]["board"] == logic.EMPTY_BOARD
        assert s["tictactoe"]["score"]["X"] == 1


def test_broken_session_starts_fresh(client):
    with client.session_transaction() as s:
        s["tictactoe"] = {"board": "nonsense", "score": {}}
    assert client.get("/games/tictactoe/").status_code == 200


def test_room_object_now_opens_the_real_game(client):
    html = client.get("/").data.decode()
    assert 'data-url="/games/tictactoe/"' in html
