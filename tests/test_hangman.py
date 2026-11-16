"""Tests for hangman: the rules in logic.py, the word list and the routes."""
import pytest

from app import create_app
from games.hangman import logic


# --- Word list ---

def test_word_list_loads_and_is_clean():
    words = logic.load_words()
    assert len(words) >= 20
    assert all(logic.is_valid_word(w) for w in words)
    assert len(words) == len(set(words)), "duplicate words"


def test_bad_words_are_rejected(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("# comment\ngood\n\nnot ok\n")
    with pytest.raises(ValueError):
        logic.load_words(path)


def test_comments_and_blank_lines_are_skipped(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("# comment\nTea\n\ncake\n")
    assert logic.load_words(path) == ["tea", "cake"]


# --- Rules ---

def test_masked_word_shows_only_guessed_letters():
    assert logic.masked("teapot", "t") == ["t", None, None, None, None, "t"]


def test_correct_and_wrong_guesses():
    guessed = logic.guess("tea", "", "e")
    guessed = logic.guess("tea", guessed, "z")
    assert guessed == "ez"
    assert logic.wrong_letters("tea", guessed) == ["z"]
    assert logic.wrong_count("tea", guessed) == 1


def test_guess_is_case_insensitive():
    assert logic.guess("tea", "", "T") == "t"


@pytest.mark.parametrize("bad", ["", "ab", "1", "é", " ", None])
def test_non_letters_are_rejected(bad):
    with pytest.raises(ValueError):
        logic.guess("tea", "", bad)


def test_repeated_guess_is_rejected_and_not_counted_twice():
    with pytest.raises(ValueError):
        logic.guess("tea", "z", "z")
    assert logic.wrong_count("tea", "z") == 1


def test_win():
    assert logic.is_won("tea", "eat")
    assert logic.is_over("tea", "eat")
    with pytest.raises(ValueError):
        logic.guess("tea", "eat", "b")


def test_lose_after_six_wrong_guesses():
    guessed = "bcdfgh"
    assert logic.wrong_count("tea", guessed) == 6
    assert logic.is_lost("tea", guessed)
    assert not logic.is_lost("tea", guessed[:5])


# --- Web routes ---

@pytest.fixture
def client():
    c = create_app().test_client()
    c.get("/games/hangman/")  # starts a game
    with c.session_transaction() as s:
        s["hangman"] = {"word": "teacup", "guessed": ""}
    return c


def state(client):
    with client.session_transaction() as s:
        return s["hangman"]


def test_page_shows_blanks_and_keyboard(client):
    html = client.get("/games/hangman/").data.decode()
    assert html.count('class="hm-letter') == 6
    assert html.count('class="hm-key ') == 26


def test_guessing_reveals_letters(client):
    client.post("/games/hangman/guess", data={"letter": "t"})
    html = client.get("/games/hangman/").data.decode()
    assert state(client)["guessed"] == "t"
    assert '<span class="hm-letter">t</span>' in html


def test_repeat_and_garbage_guesses_are_ignored(client):
    client.post("/games/hangman/guess", data={"letter": "z"})
    client.post("/games/hangman/guess", data={"letter": "z"})
    client.post("/games/hangman/guess", data={"letter": "<script>"})
    assert state(client)["guessed"] == "z"


def test_winning(client):
    for letter in "teacup":
        client.post("/games/hangman/guess", data={"letter": letter})
    html = client.get("/games/hangman/").data.decode()
    assert "You got it!" in html


def test_losing_reveals_the_word(client):
    for letter in "bdfghi":
        client.post("/games/hangman/guess", data={"letter": letter})
    html = client.get("/games/hangman/").data.decode()
    assert "Out of guesses!" in html
    assert html.count("hm-letter-missed") == len("teacup")
    # no more guesses accepted
    client.post("/games/hangman/guess", data={"letter": "t"})
    assert "t" not in state(client)["guessed"]


def test_new_word_resets_guesses(client):
    client.post("/games/hangman/guess", data={"letter": "t"})
    client.post("/games/hangman/new")
    new = state(client)
    assert new["guessed"] == ""
    assert new["word"] != "teacup"


def test_broken_session_starts_fresh(client):
    with client.session_transaction() as s:
        s["hangman"] = {"word": "NOT VALID", "guessed": 5}
    assert client.get("/games/hangman/").status_code == 200
    assert logic.is_valid_word(state(client)["word"])


def test_room_bookshelf_opens_hangman(client):
    assert 'data-url="/games/hangman/"' in client.get("/").data.decode()


# --- Drawing (issue #6) ---

from games.hangman import drawing  # noqa: E402
from room import sprites  # noqa: E402


def test_there_is_a_picture_for_every_number_of_wrong_guesses():
    for wrong in range(logic.MAX_WRONG + 1):
        rows = sprites.SPRITES[f"hangman-{wrong}"]
        assert len(rows) == drawing.HEIGHT
        assert all(len(r) == drawing.WIDTH for r in rows)


def test_each_wrong_guess_adds_something_to_the_picture():
    pictures = [drawing.picture(w) for w in range(logic.MAX_WRONG + 1)]
    for before, after in zip(pictures, pictures[1:]):
        assert before != after
        filled = lambda rows: sum(ch != "." for row in rows for ch in row)  # noqa: E731
        assert filled(after) > filled(before)


def test_gallows_only_at_the_start():
    start = drawing.picture(0)
    assert not any("s" in row for row in start), "no person before a wrong guess"


def test_page_shows_the_picture_for_the_current_wrong_count(client):
    assert "sprite-hangman-0" in client.get("/games/hangman/").data.decode()
    client.post("/games/hangman/guess", data={"letter": "z"})
    client.post("/games/hangman/guess", data={"letter": "q"})
    assert "sprite-hangman-2" in client.get("/games/hangman/").data.decode()


def test_new_word_resets_the_picture(client):
    client.post("/games/hangman/guess", data={"letter": "z"})
    client.post("/games/hangman/new")
    assert "sprite-hangman-0" in client.get("/games/hangman/").data.decode()
