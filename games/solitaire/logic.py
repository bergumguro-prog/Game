"""Klondike solitaire rules, in plain Python (no Flask).

Cards are two-letter strings: rank then suit, e.g. "AH" (ace of hearts),
"TD" (ten of diamonds), "KS" (king of spades).

A game is a seed (which decides the shuffle) plus the list of moves made so
far. `replay(seed, moves)` rebuilds the table from those, which makes undo
easy (drop the last move) and keeps the saved game tiny.

Moves are short strings:
    "D"         draw a card from the stock (or turn the waste over when the
                stock is empty)
    "W>T3"      waste's top card to tableau pile 3 (piles are 0-6)
    "W>F"       waste's top card to a foundation
    "T2:5>T4"   tableau pile 2, from card 5 down, onto tableau pile 4
    "T2>F"      tableau pile 2's top card to a foundation
    "F1>T3"     foundation 1's top card back onto tableau pile 3
"""
import random
import re
from dataclasses import dataclass, field

RANKS = "A23456789TJQK"
SUITS = "HDCS"           # hearts, diamonds, clubs, spades
RED = set("HD")
PILES = 7
FOUNDATIONS = 4


def rank(card):
    return RANKS.index(card[0]) + 1   # ace = 1 ... king = 13


def suit(card):
    return card[1]


def is_red(card):
    return suit(card) in RED


def new_deck():
    return [r + s for s in SUITS for r in RANKS]


@dataclass
class Table:
    # each tableau pile is a list of [card, face_up] pairs, top card last
    tableau: list = field(default_factory=lambda: [[] for _ in range(PILES)])
    stock: list = field(default_factory=list)       # face down, top card last
    waste: list = field(default_factory=list)       # face up, top card last
    foundations: list = field(default_factory=lambda: [[] for _ in range(FOUNDATIONS)])


def deal(seed):
    """Shuffle with `seed` and lay out a new game."""
    deck = new_deck()
    random.Random(seed).shuffle(deck)
    table = Table()
    for pile in range(PILES):
        for i in range(pile + 1):
            table.tableau[pile].append([deck.pop(), i == pile])
    table.stock = deck
    return table


# --- Which card may go where ------------------------------------------------

def fits_on_tableau(card, pile):
    """Can `card` be put on this tableau pile?"""
    if not pile:
        return rank(card) == 13           # only a king on an empty pile
    top, face_up = pile[-1]
    return face_up and is_red(card) != is_red(top) and rank(card) == rank(top) - 1


def fits_on_foundation(card, foundation):
    if not foundation:
        return rank(card) == 1            # aces start a foundation
    top = foundation[-1]
    return suit(card) == suit(top) and rank(card) == rank(top) + 1


def foundation_for(table, card):
    """The foundation `card` can go on, or None. A card goes on its own
    suit's foundation if there is one, else on the first empty one."""
    for i, foundation in enumerate(table.foundations):
        if foundation and fits_on_foundation(card, foundation):
            return i
    if rank(card) == 1:
        return next((i for i, f in enumerate(table.foundations) if not f), None)
    return None


# --- Making moves -------------------------------------------------------------

MOVE = re.compile(r"^(?:D|W>T[0-6]|W>F|T[0-6]:\d{1,2}>T[0-6]|T[0-6]>F|F[0-3]>T[0-6])$")


def _turn_over_top(pile):
    if pile and not pile[-1][1]:
        pile[-1][1] = True


def apply(table, move):
    """Make `move` on `table` (changing it). Raises ValueError if the move
    isn't allowed."""
    if not isinstance(move, str) or not MOVE.match(move):
        raise ValueError(f"not a move: {move!r}")

    if move == "D":
        if table.stock:
            table.waste.append(table.stock.pop())
        elif table.waste:
            table.stock = list(reversed(table.waste))
            table.waste = []
        else:
            raise ValueError("nothing left to draw")
        return

    source, target = move.split(">")

    # Pick up the moving card(s), checking they can be picked up.
    if source == "W":
        if not table.waste:
            raise ValueError("the waste is empty")
        cards = [table.waste[-1]]
    elif source.startswith("F"):
        foundation = table.foundations[int(source[1])]
        if not foundation:
            raise ValueError("that foundation is empty")
        cards = [foundation[-1]]
    else:
        pile = table.tableau[int(source[1])]
        start = int(source[3:]) if ":" in source else len(pile) - 1
        if not 0 <= start < len(pile) or not pile[start][1]:
            raise ValueError("those cards can't be picked up")
        cards = [card for card, _ in pile[start:]]
        # a picked-up stack must itself be in order
        for upper, lower in zip(cards, cards[1:]):
            if is_red(upper) == is_red(lower) or rank(lower) != rank(upper) - 1:
                raise ValueError("those cards aren't in order")

    # Check the target accepts them.
    if target == "F":
        if len(cards) != 1:
            raise ValueError("only one card at a time goes to a foundation")
        dest = foundation_for(table, cards[0])
        if dest is None:
            raise ValueError("no foundation takes that card")
    else:
        dest = int(target[1])
        if source == target:
            raise ValueError("that's the same pile")
        if not fits_on_tableau(cards[0], table.tableau[dest]):
            raise ValueError("that card doesn't go there")

    # Take them away from where they were...
    if source == "W":
        table.waste.pop()
    elif source.startswith("F"):
        table.foundations[int(source[1])].pop()
    else:
        pile = table.tableau[int(source[1])]
        del pile[len(pile) - len(cards):]
        _turn_over_top(pile)

    # ...and put them down.
    if target == "F":
        table.foundations[dest].append(cards[0])
    else:
        table.tableau[dest].extend([card, True] for card in cards)


def replay(seed, moves):
    """The table after dealing with `seed` and making `moves` in order."""
    table = deal(seed)
    for move in moves:
        apply(table, move)
    return table


def is_legal(table, move):
    """Would `move` be allowed? (Doesn't change the table.)"""
    trial = Table(
        tableau=[[list(c) for c in pile] for pile in table.tableau],
        stock=list(table.stock),
        waste=list(table.waste),
        foundations=[list(f) for f in table.foundations],
    )
    try:
        apply(trial, move)
    except ValueError:
        return False
    return True


def auto_move(table, source):
    """The move that sends the top card of `source` ("W" or "T0".."T6") to a
    foundation, or None if it can't go there (used for double-clicks)."""
    move = f"{source}>F"
    return move if is_legal(table, move) else None


def is_won(table):
    return sum(len(f) for f in table.foundations) == 52


def cards_on_foundations(table):
    return sum(len(f) for f in table.foundations)
