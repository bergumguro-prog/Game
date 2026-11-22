"""Tests for solitaire: the Klondike rules in logic.py and the web routes."""
import pytest

from app import create_app
from games.solitaire import logic
from games.solitaire.logic import Table


def table_with(tableau=None, stock=None, waste=None, foundations=None):
    """A hand-made table. Tableau piles are lists of "card" (face up) or
    "-card" (face down)."""
    piles = [[] for _ in range(7)]
    for i, pile in enumerate(tableau or []):
        piles[i] = [[c.lstrip("-"), not c.startswith("-")] for c in pile]
    found = [list(f) for f in (foundations or [])] + [[] for _ in range(4)]
    return Table(tableau=piles, stock=list(stock or []), waste=list(waste or []),
                 foundations=found[:4])


# --- Dealing ---

def test_deal_lays_out_klondike():
    table = logic.deal(1)
    assert [len(p) for p in table.tableau] == [1, 2, 3, 4, 5, 6, 7]
    for pile in table.tableau:
        assert [up for _, up in pile] == [False] * (len(pile) - 1) + [True]
    assert len(table.stock) == 24 and table.waste == []
    every = [c for p in table.tableau for c, _ in p] + table.stock
    assert sorted(every) == sorted(logic.new_deck())


def test_same_seed_same_deal_and_different_seeds_differ():
    assert logic.deal(5) == logic.deal(5)
    assert logic.deal(5) != logic.deal(6)


# --- Stock and waste ---

def test_draw_moves_one_card_to_the_waste():
    table = table_with(stock=["2H", "9C"])
    logic.apply(table, "D")
    assert table.stock == ["2H"] and table.waste == ["9C"]


def test_empty_stock_turns_the_waste_over():
    table = table_with(waste=["2H", "9C", "KD"])
    logic.apply(table, "D")
    assert table.waste == [] and table.stock == ["KD", "9C", "2H"]
    logic.apply(table, "D")
    assert table.waste == ["2H"]      # same order as the first time round


def test_cannot_draw_from_nothing():
    with pytest.raises(ValueError):
        logic.apply(table_with(), "D")


# --- Tableau ---

def test_card_goes_on_opposite_color_one_lower():
    table = table_with(tableau=[["9C"], ["8H"]])
    logic.apply(table, "T1:0>T0")
    assert [c for c, _ in table.tableau[0]] == ["9C", "8H"]
    assert table.tableau[1] == []


@pytest.mark.parametrize("card", ["8C", "8S", "7H", "TH"])
def test_wrong_color_or_rank_is_refused(card):
    table = table_with(tableau=[["9C"], [card]])
    with pytest.raises(ValueError):
        logic.apply(table, "T1:0>T0")


def test_only_a_king_goes_on_an_empty_pile():
    table = table_with(tableau=[[], ["QH"], ["KS"]])
    with pytest.raises(ValueError):
        logic.apply(table, "T1:0>T0")
    logic.apply(table, "T2:0>T0")
    assert table.tableau[0] == [["KS", True]]


def test_moving_a_stack_and_turning_over_the_card_underneath():
    table = table_with(tableau=[["-4D", "TS", "9H", "8C"], ["JD"]])
    logic.apply(table, "T0:1>T1")
    assert [c for c, _ in table.tableau[1]] == ["JD", "TS", "9H", "8C"]
    assert table.tableau[0] == [["4D", True]]   # turned face up


def test_face_down_cards_and_unordered_stacks_cannot_be_moved():
    table = table_with(tableau=[["-4D", "TS"], ["JD"], ["9H", "7C"], ["8S"]])
    with pytest.raises(ValueError):
        logic.apply(table, "T0:0>T1")            # 4D is face down
    with pytest.raises(ValueError):
        logic.apply(table, "T2:0>T3")            # 9H, 7C isn't in order


def test_waste_to_tableau():
    table = table_with(tableau=[["6S"]], waste=["2C", "5H"])
    logic.apply(table, "W>T0")
    assert table.waste == ["2C"]
    assert table.tableau[0][-1] == ["5H", True]


# --- Foundations ---

def test_aces_start_foundations_and_suits_build_up():
    table = table_with(tableau=[["AH"], ["2H"], ["2S"]])
    logic.apply(table, "T0>F")
    logic.apply(table, "T1>F")
    assert table.foundations[0] == ["AH", "2H"]
    with pytest.raises(ValueError):
        logic.apply(table, "T2>F")               # no spade ace yet


def test_foundation_card_can_come_back_down():
    table = table_with(tableau=[["4C"]], foundations=[["AH", "2H", "3H"]])
    logic.apply(table, "F0>T0")
    assert table.foundations[0] == ["AH", "2H"]
    assert table.tableau[0][-1] == ["3H", True]


def test_auto_move_finds_the_foundation_or_nothing():
    table = table_with(tableau=[["AD"], ["5C"]], waste=["2D"])
    assert logic.auto_move(table, "T0") == "T0>F"
    assert logic.auto_move(table, "T1") is None
    assert logic.auto_move(table, "W") is None   # 2D needs the ace first
    logic.apply(table, "T0>F")
    assert logic.auto_move(table, "W") == "W>F"


@pytest.mark.parametrize("move", ["", "X", "T7>F", "W>T9", "T1:x>T2", "F4>T0", None, 5])
def test_garbled_moves_are_refused(move):
    with pytest.raises(ValueError):
        logic.apply(logic.deal(1), move)


def test_is_legal_does_not_change_the_table():
    table = logic.deal(3)
    before = repr(table)
    logic.is_legal(table, "D")
    assert repr(table) == before


# --- Replay, undo, winning ---

def test_replay_rebuilds_the_same_table():
    moves = ["D", "D", "D"]
    table = logic.deal(9)
    for m in moves:
        logic.apply(table, m)
    assert logic.replay(9, moves) == table
    # undo = replay without the last move
    assert logic.replay(9, moves[:-1]) != table


def test_winning_needs_all_52_cards_on_foundations():
    full = [[r + s for r in logic.RANKS] for s in logic.SUITS]
    assert logic.is_won(table_with(foundations=full))
    almost = [list(f) for f in full]
    king = almost[3].pop()
    table = table_with(tableau=[[king]], foundations=almost)
    assert not logic.is_won(table)
    logic.apply(table, "T0>F")
    assert logic.is_won(table)


# --- Routes ---

@pytest.fixture
def client():
    return create_app().test_client()


def saved(client):
    with client.session_transaction() as s:
        return s["solitaire"]


def test_page_loads_and_starts_a_game(client):
    assert client.get("/games/solitaire/").status_code == 200
    game = saved(client)
    assert game["moves"] == [] and isinstance(game["seed"], int)


def test_card_table_opens_solitaire(client):
    html = client.get("/rooms/livingroom").data.decode()
    assert 'data-url="/games/solitaire/"' in html


def test_moves_are_saved_and_illegal_ones_ignored(client):
    client.get("/games/solitaire/")
    client.post("/games/solitaire/move", data={"move": "D"})
    client.post("/games/solitaire/move", data={"move": "T9>F"})      # garbled
    client.post("/games/solitaire/move", data={"move": "T0:0>T0"})   # same pile
    assert saved(client)["moves"] == ["D"]


def test_undo_forgets_the_last_move(client):
    client.get("/games/solitaire/")
    client.post("/games/solitaire/move", data={"move": "D"})
    client.post("/games/solitaire/move", data={"move": "D"})
    client.post("/games/solitaire/undo")
    assert saved(client)["moves"] == ["D"]


def test_new_game_reshuffles(client):
    client.get("/games/solitaire/")
    client.post("/games/solitaire/move", data={"move": "D"})
    first = saved(client)["seed"]
    client.post("/games/solitaire/new")
    game = saved(client)
    assert game["moves"] == []
    assert game["seed"] != first


def test_auto_sends_an_ace_to_a_foundation(client):
    # find a deal where a tableau pile shows an ace
    for seed in range(1, 500):
        table = logic.deal(seed)
        pile = next((i for i, p in enumerate(table.tableau) if p[-1][0][0] == "A"), None)
        if pile is not None:
            break
    with client.session_transaction() as s:
        s["solitaire"] = {"seed": seed, "moves": [], "started": 0, "won": None}
    client.post("/games/solitaire/auto", data={"from": f"T{pile}"})
    assert saved(client)["moves"] == [f"T{pile}>F"]
    client.post("/games/solitaire/auto", data={"from": "nonsense"})
    assert saved(client)["moves"] == [f"T{pile}>F"]


def test_broken_saved_game_starts_fresh(client):
    with client.session_transaction() as s:
        s["solitaire"] = {"seed": "x", "moves": "oops"}
    assert client.get("/games/solitaire/").status_code == 200
    assert saved(client)["moves"] == []
