"""Tests for the piano: notes, keyboard layout, sounds and the page."""
import pytest

from app import create_app
from games.piano import logic


def test_one_octave_and_a_bit():
    assert logic.NOTES[0] == "C4" and logic.NOTES[-1] == "E5"
    assert len(logic.WHITE) == 10 and len(logic.BLACK) == 7


def test_frequencies_rise_and_a4_is_440():
    assert logic.frequency("A4") == pytest.approx(440.0)
    assert logic.frequency("A#4") == pytest.approx(466.16, abs=0.01)
    freqs = [logic.frequency(n) for n in logic.NOTES]
    assert freqs == sorted(freqs)


def test_every_note_has_its_own_computer_key():
    assert sorted(logic.KEYBOARD.values()) == sorted(logic.NOTES)
    # white keys on the middle row, black keys on the row above
    for key, note in logic.KEYBOARD.items():
        assert (key in "asdfghjkl;") == ("#" not in note)


def test_black_keys_sit_between_white_keys():
    keys = logic.keys()
    for i, k in enumerate(keys):
        if k["black"]:
            assert not keys[i - 1]["black"] and not keys[i + 1]["black"]
            assert k["white_index"] == keys[i - 1]["white_index"]


@pytest.mark.parametrize("note", logic.NOTES)
def test_every_note_sound_is_served(note):
    response = create_app().test_client().get(f"/static/sounds/{logic.sound_name(note)}.wav")
    assert response.status_code == 200
    assert response.data[:4] == b"RIFF"


def test_piano_page_has_every_key():
    html = create_app().test_client().get("/games/piano/").data.decode()
    for note in logic.NOTES:
        assert f'data-note="{note}"' in html
    assert html.count('class="piano-key black"') == 7
    assert "piano.js" in html
    assert 'href="/"' in html and 'data-scene="game"' in html


def test_living_room_piano_opens_the_piano():
    html = create_app().test_client().get("/rooms/livingroom").data.decode()
    assert 'data-url="/games/piano/"' in html


# --- Repeat the tune (issue #74) ---

@pytest.fixture
def client():
    return create_app().test_client()


def state(client):
    with client.session_transaction() as s:
        return s["piano"]


def test_tunes_grow_by_one_note_and_keep_their_start():
    for length in range(1, logic.MAX_LENGTH):
        assert logic.tune(7, length + 1)[:length] == logic.tune(7, length)
    assert all(n in logic.TUNE_NOTES for n in logic.tune(7, logic.MAX_LENGTH))
    assert logic.tune(7, 10) != logic.tune(8, 10)


def test_checking_a_played_tune():
    tune = logic.tune(3, 5)
    assert logic.is_correct(3, 5, tune)
    assert not logic.is_correct(3, 5, tune[:4])
    wrong = tune[:2] + ["E5"] + tune[3:]
    assert not logic.is_correct(3, 5, wrong)
    assert logic.correct_so_far(3, 5, wrong) == 2


def test_free_play_is_the_default_and_modes_switch(client):
    html = client.get("/games/piano/").data.decode()
    assert "Play anything you like!" in html and 'id="tune"' not in html
    client.post("/games/piano/mode", data={"mode": "repeat"})
    assert state(client)["mode"] == "repeat"
    client.post("/games/piano/mode", data={"mode": "jazz"})
    assert state(client)["mode"] == "repeat"


def test_a_right_answer_makes_the_tune_longer(client):
    client.post("/games/piano/repeat/start")
    s = state(client)
    html = client.get("/games/piano/").data.decode()
    tune = logic.tune(s["seed"], logic.START_LENGTH)
    assert f'data-notes="{",".join(tune)}"' in html
    client.post("/games/piano/repeat/answer", data={"notes": ",".join(tune)})
    s = state(client)
    assert s["length"] == logic.START_LENGTH + 1 and s["result"] == "right"
    assert s["best"] == logic.START_LENGTH


def test_a_wrong_note_ends_the_round_and_keeps_the_best(client):
    with client.session_transaction() as sess:
        sess["piano"] = {"mode": "repeat", "seed": 3, "length": 6, "best": 5}
    tune = logic.tune(3, 6)
    played = tune[:3] + ["E5" if tune[3] != "E5" else "C4"]
    client.post("/games/piano/repeat/answer", data={"notes": ",".join(played)})
    s = state(client)
    assert s["result"] == "wrong" and s["reached"] == 5 and s["best"] == 5
    html = client.get("/games/piano/").data.decode()
    assert "tunes of 5 notes" in html and 'id="tune"' not in html
    # answering again after losing does nothing
    client.post("/games/piano/repeat/answer", data={"notes": ",".join(tune)})
    assert state(client)["result"] == "wrong"
    # starting again keeps the best
    client.post("/games/piano/repeat/start")
    assert state(client)["best"] == 5 and state(client)["length"] == logic.START_LENGTH


def test_garbled_answers_are_ignored(client):
    client.post("/games/piano/repeat/start")
    client.post("/games/piano/repeat/answer", data={"notes": "C4,<script>,G9"})
    assert state(client)["result"] is None


def test_playing_the_whole_tune_wins(client):
    with client.session_transaction() as sess:
        sess["piano"] = {"mode": "repeat", "seed": 4, "length": logic.MAX_LENGTH, "best": 0}
    tune = logic.tune(4, logic.MAX_LENGTH)
    client.post("/games/piano/repeat/answer", data={"notes": ",".join(tune)})
    assert state(client)["result"] == "done"
    assert "whole tune" in client.get("/games/piano/").data.decode()
