"""Tests for chess: the helpers in logic.py, the pieces and the routes."""
import chess
import pytest

from app import create_app
import random
import time

from games.chess import ai, logic, pieces
from room import sprites


# --- Rules helpers ---

def test_moves_replay_into_a_board():
    board = logic.board_from_moves(["e2e4", "e7e5"])
    assert board.piece_at(chess.E4).symbol() == "P"
    assert board.turn == chess.WHITE


@pytest.mark.parametrize("moves", [["e2e5"], ["zz"], ["e2e4", "e2e4"]])
def test_illegal_or_garbled_moves_are_rejected(moves):
    with pytest.raises(ValueError):
        logic.board_from_moves(moves)


def test_legal_targets_of_a_knight():
    board = chess.Board()
    assert logic.legal_targets(board, chess.G1) == {chess.F3, chess.H3}


def test_pawn_promotes_to_queen():
    board = chess.Board("8/P7/8/8/8/8/8/k6K w - - 0 1")
    move = logic.find_move(board, chess.A7, chess.A8)
    assert move.promotion == chess.QUEEN


def test_castling_and_en_passant_are_found():
    castle = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    assert logic.find_move(castle, chess.E1, chess.G1) is not None
    ep = logic.board_from_moves(["e2e4", "a7a6", "e4e5", "d7d5"])
    move = logic.find_move(ep, chess.E5, chess.D6)
    assert move is not None and ep.is_en_passant(move)


def test_status_check_mate_and_stalemate():
    assert logic.status(chess.Board())["text"] == "White to move"

    check = logic.board_from_moves(["e2e4", "f7f6", "d2d4", "g7g5", "d1h5"])
    s = logic.status(check)
    assert s["text"].startswith("Checkmate! White wins")
    assert s["over"]
    assert s["check_square"] == chess.E8

    stalemate = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert logic.status(stalemate)["text"].startswith("Stalemate")

    in_check = logic.board_from_moves(["e2e4", "d7d5", "f1b5"])
    s = logic.status(in_check)
    assert s["text"] == "Check! Black to move"
    assert not s["over"]


def test_every_piece_has_a_sprite():
    for color in (chess.WHITE, chess.BLACK):
        for kind in chess.PIECE_TYPES:
            name = pieces.sprite_name(chess.Piece(kind, color))
            rows = sprites.SPRITES[name]
            assert len(rows) == 16 and all(len(r) == 16 for r in rows)


# --- Web routes ---

@pytest.fixture
def client():
    """A browser in two-player ("friend") mode."""
    c = create_app().test_client()
    c.post("/games/chess/new", data={"mode": "friend"})
    return c


@pytest.fixture
def computer_client():
    """A browser playing white against the computer (the default)."""
    return create_app().test_client()


def click(client, *squares):
    for sq in squares:
        client.post("/games/chess/click", data={"square": sq})


def state(client):
    with client.session_transaction() as s:
        return s["chess"]


def test_page_shows_64_squares_and_32_pieces(client):
    html = client.get("/games/chess/").data.decode()
    assert html.count('name="square"') == 64
    assert html.count('class="sprite sprite-chess-') == 32
    assert "White to move" in html


def test_select_then_move(client):
    click(client, "e2")
    assert state(client)["selected"] == "e2"
    html = client.get("/games/chess/").data.decode()
    assert html.count("chess-target") == 2  # e3 and e4
    click(client, "e4")
    assert state(client) == {"moves": ["e2e4"], "selected": None, "mode": "friend"}


def test_clicking_elsewhere_clears_or_changes_selection(client):
    click(client, "e2", "e5")  # not a legal target -> deselect
    assert state(client)["selected"] is None
    click(client, "e2", "d2")  # another own piece -> select that one
    assert state(client)["selected"] == "d2"


def test_cannot_select_opponents_pieces(client):
    click(client, "e7")
    assert state(client)["selected"] is None


def test_scholars_mate_ends_the_game(client):
    click(client, "e2", "e4", "e7", "e5", "f1", "c4", "b8", "c6",
          "d1", "h5", "g8", "f6", "h5", "f7")
    html = client.get("/games/chess/").data.decode()
    assert "Checkmate! White wins" in html
    assert "chess-check" in html
    before = state(client)["moves"]
    click(client, "a7", "a6")  # no more moves after the end
    assert state(client)["moves"] == before


def test_garbled_square_is_ignored(client):
    click(client, "z9")
    assert client.get("/games/chess/").status_code == 200


def test_tampered_session_starts_fresh(client):
    with client.session_transaction() as s:
        s["chess"] = {"moves": ["e2e5"], "selected": "nowhere"}
    html = client.get("/games/chess/").data.decode()
    # no mode stored -> back to the default (vs computer), fresh board
    assert "Your move" in html
    assert html.count('class="sprite sprite-chess-') == 32


def test_new_game(client):
    click(client, "e2", "e4")
    client.post("/games/chess/new")
    assert state(client)["moves"] == []


def test_tea_table_opens_chess(client):
    assert 'data-url="/games/chess/"' in client.get("/").data.decode()


# --- Computer opponent (issue #8) ---

def test_ai_returns_a_legal_move_from_the_start():
    board = chess.Board()
    assert ai.choose_move(board) in board.legal_moves


def test_ai_returns_none_when_the_game_is_over():
    mate = logic.board_from_moves(["f2f3", "e7e5", "g2g4", "d8h4"])
    assert ai.choose_move(mate) is None


def test_ai_takes_a_free_queen():
    # The white queen on h5 is hanging to the knight on f6.
    board = chess.Board("rnbqkb1r/pppppppp/5n2/7Q/8/8/PPPPPPPP/RNB1KBNR b KQkq - 0 1")
    assert ai.choose_move(board).uci() == "f6h5"


def test_ai_finds_mate_in_one():
    # Back-rank mate: Ra1#
    board = chess.Board("r5k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1")
    assert ai.choose_move(board).uci() == "a8a1"


def test_ai_does_not_hang_its_queen():
    # Taking the pawn on e4 with the queen loses her to the knight on c3.
    board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/4P1q1/2N5/PPPP1PPP/R1BQKBNR b KQkq - 0 1")
    for _ in range(5):
        assert ai.choose_move(board).uci() != "g4e4"


def test_ai_is_fast_enough():
    # A busy middlegame position should take well under 2 seconds.
    board = chess.Board("r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R2QK2R w KQ - 0 1")
    start = time.perf_counter()
    ai.choose_move(board)
    assert time.perf_counter() - start < 2


def test_ai_plays_full_games_without_errors():
    rng = random.Random(3)
    for _ in range(3):
        board = chess.Board()
        while not board.is_game_over() and board.fullmove_number < 40:
            if board.turn == chess.WHITE:
                move = rng.choice(list(board.legal_moves))
            else:
                move = ai.choose_move(board, rng=rng)
            assert move in board.legal_moves
            board.push(move)


def test_computer_replies_after_your_move(computer_client):
    click(computer_client, "e2", "e4")
    moves = state(computer_client)["moves"]
    assert moves[0] == "e2e4"
    assert len(moves) == 2
    board = logic.board_from_moves(moves)
    assert board.turn == chess.WHITE


def test_computer_mode_texts(computer_client):
    assert "Your move" in computer_client.get("/games/chess/").data.decode()


def test_mode_switch(client):
    client.post("/games/chess/new", data={"mode": "computer"})
    assert state(client)["mode"] == "computer"
    client.post("/games/chess/new", data={"mode": "nonsense"})
    assert state(client)["mode"] == "computer"
