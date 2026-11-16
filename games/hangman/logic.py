"""Hangman rules. Pure Python, no Flask, so it's easy to test.

A game is just two things:
    word     - the secret word, lowercase a-z
    guessed  - every letter guessed so far, in order, as a string
Everything else (the blanks, wrong guesses, win/lose) is worked out from those.
"""
import random
import string
from pathlib import Path

MAX_WRONG = 6  # head, body, two arms, two legs
ALPHABET = string.ascii_lowercase
WORDS_FILE = Path(__file__).with_name("words.txt")


def load_words(path=WORDS_FILE):
    """Read the word list: one word per line, # starts a comment."""
    words = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        word = line.strip().lower()
        if word and not word.startswith("#"):
            if not is_valid_word(word):
                raise ValueError(f"bad word in {path}: {word!r}")
            words.append(word)
    return words


def is_valid_word(word):
    return isinstance(word, str) and len(word) > 0 and all(c in ALPHABET for c in word)


def pick_word(words, rng=random):
    return rng.choice(words)


def masked(word, guessed):
    """The word with unguessed letters hidden, as a list: ['t', None, 'a', ...]."""
    return [c if c in guessed else None for c in word]


def wrong_letters(word, guessed):
    return [c for c in guessed if c not in word]


def wrong_count(word, guessed):
    return len(wrong_letters(word, guessed))


def is_won(word, guessed):
    return all(c in guessed for c in word)


def is_lost(word, guessed):
    return wrong_count(word, guessed) >= MAX_WRONG


def is_over(word, guessed):
    return is_won(word, guessed) or is_lost(word, guessed)


def guess(word, guessed, letter):
    """Return `guessed` with `letter` added.

    Raises ValueError if it isn't a single a-z letter, was already guessed,
    or the game is over.
    """
    letter = (letter or "").strip().lower()
    if len(letter) != 1 or letter not in ALPHABET:
        raise ValueError(f"not a letter: {letter!r}")
    if letter in guessed:
        raise ValueError(f"already guessed: {letter}")
    if is_over(word, guessed):
        raise ValueError("the game is over")
    return guessed + letter
