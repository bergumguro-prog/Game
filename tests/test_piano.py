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
