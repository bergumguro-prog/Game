"""Tests for chess: the helpers in logic.py, the pieces and the routes."""
import chess
import pytest

from app import create_app
from games.chess import logic, pieces
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
    assert state(client) == {"moves": ["e2e4"], "selected": None}


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
    assert "White to move" in html


def test_new_game(client):
    click(client, "e2", "e4")
    client.post("/games/chess/new")
    assert state(client)["moves"] == []


def test_tea_table_opens_chess(client):
    assert 'data-url="/games/chess/"' in client.get("/").data.decode()
