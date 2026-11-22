"""The piano's notes and keyboard layout, in plain Python.

One octave and a bit: C4 up to E5. Notes are names like "C4" or "F#4".
Each note has a sound file made by tools/make_sounds.py.
"""
import random

NOTES = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
         "C5", "C#5", "D5", "D#5", "E5"]
WHITE = [n for n in NOTES if "#" not in n]
BLACK = [n for n in NOTES if "#" in n]

# Computer keys, laid out like a piano: the middle row is the white keys,
# the row above it the black keys.
KEYBOARD = {
    "a": "C4", "w": "C#4", "s": "D4", "e": "D#4", "d": "E4", "f": "F4", "t": "F#4",
    "g": "G4", "y": "G#4", "h": "A4", "u": "A#4", "j": "B4", "k": "C5", "o": "C#5",
    "l": "D5", "p": "D#5", ";": "E5",
}
KEY_FOR = {note: key for key, note in KEYBOARD.items()}

_SEMITONES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7,
              "G#": 8, "A": 9, "A#": 10, "B": 11}


def frequency(note):
    """Pitch in Hz (A4 = 440)."""
    name, octave = note[:-1], int(note[-1])
    midi = 12 * (octave + 1) + _SEMITONES[name]
    return 440.0 * 2 ** ((midi - 69) / 12)


def sound_name(note):
    """The sound file's name: "C#4" -> "piano-Cs4" ('#' isn't nice in URLs)."""
    return "piano-" + note.replace("#", "s")


def keys():
    """Every key for the template, in order. Black keys know which white
    key they sit after, so CSS can place them between two white keys."""
    out = []
    white_index = -1
    for note in NOTES:
        black = "#" in note
        if not black:
            white_index += 1
        out.append({
            "note": note,
            "black": black,
            "white_index": white_index,   # for a black key: the white key to its left
            "key": KEY_FOR[note],
            "sound": sound_name(note),
        })
    return out


# --- Repeat the tune ---------------------------------------------------------
# The piano plays a tune; you play it back. Each round the same tune gets one
# note longer (it's always the start of one long tune made from the seed).

TUNE_NOTES = WHITE[:8]   # C4 up to C5: tunes stay in a friendly range
START_LENGTH = 3
MAX_LENGTH = 24


def tune(seed, length):
    """The first `length` notes of the tune for `seed`. It walks up and down
    by small steps so it sounds like a melody, not random notes."""
    rng = random.Random(seed)
    notes = [rng.choice(TUNE_NOTES[:5])]
    while len(notes) < MAX_LENGTH:
        i = TUNE_NOTES.index(notes[-1])
        step = rng.choice((-2, -1, -1, 1, 1, 2, 3))
        j = min(len(TUNE_NOTES) - 1, max(0, i + step))
        notes.append(TUNE_NOTES[j])
    return notes[:length]


def correct_so_far(seed, length, played):
    """How many of the played notes match the tune, counting from the start."""
    count = 0
    for want, got in zip(tune(seed, length), played):
        if want != got:
            break
        count += 1
    return count


def is_correct(seed, length, played):
    return list(played) == tune(seed, length)
