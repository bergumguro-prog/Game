"""Tests for tic-tac-toe: the rules in logic.py and the web routes."""
import random

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
    """A browser playing in two-player ("friend") mode."""
    c = create_app().test_client()
    c.post("/games/tictactoe/new", data={"mode": "friend"})
    return c


@pytest.fixture
def computer_client():
    """A browser playing against the computer (the default mode)."""
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


# --- Computer opponent (issue #4) ---

def test_computer_takes_a_winning_move():
    # O to move, O has 0 and 1 -> should take 2
    board = "OO.XX...X"
    assert logic.current_player(board) == "O"
    assert logic.computer_move(board) == 2


def test_computer_blocks_the_players_win():
    # X threatens the top row; O must block at 2
    board = "XX..O...."
    assert logic.computer_move(board) == 2


def test_computer_prefers_winning_over_blocking():
    # X threatens the top row (2), but O can win the middle row at 5
    board = "XX.OO.X.."
    assert logic.computer_move(board) == 5


def test_computer_takes_center_then_corner():
    assert logic.computer_move("X........") == 4
    assert logic.computer_move("....X....", rng=random.Random(1)) in logic.CORNERS


def test_computer_never_misses_a_win_or_a_block():
    rng = random.Random(42)
    for _ in range(300):
        board = logic.EMPTY_BOARD
        while not logic.is_over(board):
            if logic.current_player(board) == "X":
                board = logic.play(board, rng.choice(logic.legal_moves(board)))
                continue
            move = logic.computer_move(board, rng)
            after = logic.play(board, move)
            can_win = any(logic.winner(logic.play(board, m)) == "O"
                          for m in logic.legal_moves(board))
            if can_win:
                assert logic.winner(after) == "O", board
            elif not logic.is_over(after):
                # X must not be able to win on the very next move...
                threats = [m for m in logic.legal_moves(board)
                           if logic.winner(board[:m] + "X" + board[m + 1:]) == "X"]
                # ...unless X had two threats at once (a fork), which can't all be blocked.
                if len(threats) == 1:
                    assert move == threats[0], board
            board = after


def test_computer_always_returns_a_legal_move():
    rng = random.Random(7)
    for _ in range(200):
        board = logic.EMPTY_BOARD
        while not logic.is_over(board):
            move = logic.computer_move(board, rng)
            assert move in logic.legal_moves(board)
            board = logic.play(board, move)


def test_computer_answers_after_your_move(computer_client):
    computer_client.post("/games/tictactoe/move", data={"cell": "0"})
    with computer_client.session_transaction() as s:
        board = s["tictactoe"]["board"]
    assert board[0] == "X"
    assert board.count("O") == 1
    assert board[4] == "O"  # it takes the center


def test_computer_mode_is_default_and_labels_change(computer_client):
    html = computer_client.get("/games/tictactoe/").data.decode()
    assert "Your turn" in html
    assert "Computer" in html


def test_switching_mode_resets_score(client):
    for cell in [0, 3, 1, 4, 2]:
        client.post("/games/tictactoe/move", data={"cell": str(cell)})
    client.post("/games/tictactoe/new", data={"mode": "computer"})
    with client.session_transaction() as s:
        assert s["tictactoe"]["mode"] == "computer"
        assert s["tictactoe"]["score"] == {"X": 0, "O": 0, "draw": 0}


# --- Sounds (issue #9) ---

def sound_on_next_page(client):
    html = client.get("/games/tictactoe/").data.decode()
    import re
    found = re.search(r'data-sound="(\w+)"', html)
    return found.group(1) if found else None


def test_move_plays_a_sound_once(client):
    client.post("/games/tictactoe/move", data={"cell": "4"})
    assert sound_on_next_page(client) == "move"
    assert sound_on_next_page(client) is None  # not again on reload


def test_win_and_draw_sounds(client):
    for cell in [0, 3, 1, 4, 2]:
        client.post("/games/tictactoe/move", data={"cell": str(cell)})
    assert sound_on_next_page(client) == "win"
    client.post("/games/tictactoe/new")
    for cell in [0, 1, 2, 4, 3, 5, 7, 6, 8]:  # X O X / X O O / O X X -> draw
        client.post("/games/tictactoe/move", data={"cell": str(cell)})
    assert sound_on_next_page(client) == "draw"


def test_losing_to_the_computer_plays_lose(computer_client):
    with computer_client.session_transaction() as s:
        # X to move; O (computer) threatens the middle column and will win
        s["tictactoe"] = {"board": "XO..O.X..", "mode": "computer",
                          "score": {"X": 0, "O": 0, "draw": 0}}
    computer_client.post("/games/tictactoe/move", data={"cell": "5"})
    assert sound_on_next_page(computer_client) == "lose"
