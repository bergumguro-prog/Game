"""Generate the game's sound effects as small WAV files in static/sounds/.

All sounds are synthesized here (soft triangle-wave chiptune blips), so they
are original and can be changed by editing this file and running:

    python tools/make_sounds.py
"""
import math
import random
import struct
import wave
from pathlib import Path

RATE = 22050
VOLUME = 0.35
OUT = Path(__file__).resolve().parent.parent / "static" / "sounds"

# note name -> frequency in Hz
NOTES = {
    "C4": 261.63, "Eb4": 311.13, "E4": 329.63, "G4": 392.00, "A4": 440.00,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99, "A5": 880.00,
    "C6": 1046.50,
}


def triangle(phase):
    return 2 * abs(2 * (phase - math.floor(phase + 0.5))) - 1


def tone(freq, seconds, attack=0.005, release=0.06):
    """A soft triangle tone with a short fade in and out."""
    n = int(RATE * seconds)
    out = []
    for i in range(n):
        t = i / RATE
        env = min(1.0, t / attack) * min(1.0, (seconds - t) / release)
        out.append(triangle(freq * t) * max(env, 0.0))
    return out


def knock(seconds=0.09):
    """A short wooden "tok": a low tone that drops quickly, plus a bit of noise."""
    rng = random.Random(1)
    out = []
    for i in range(int(RATE * seconds)):
        t = i / RATE
        env = math.exp(-t * 45)
        freq = 180 + 400 * math.exp(-t * 60)
        out.append((0.8 * math.sin(2 * math.pi * freq * t) + 0.2 * rng.uniform(-1, 1)) * env)
    return out


def crackle(seconds=8.0, fade=0.5):
    """A soft fireplace crackle that loops without a seam: a quiet, low
    rumble with little wooden pops. The end is blended into the start."""
    rng = random.Random(7)
    total = int(RATE * (seconds + fade))
    out = [0.0] * total
    # low rumble: smoothed noise
    level = 0.0
    for i in range(total):
        level += (rng.uniform(-1, 1) - level) * 0.02
        out[i] = level * 0.9
    # pops: tiny bursts that die away fast, some louder than others
    t = 0.05
    while t < seconds + fade - 0.1:
        start = int(t * RATE)
        size = rng.choice((0.25, 0.4, 0.6, 1.0))
        length = int(RATE * rng.uniform(0.004, 0.02))
        for j in range(length):
            out[start + j] += rng.uniform(-1, 1) * size * math.exp(-j / (length / 4))
        t += rng.expovariate(9)  # about nine pops a second
    # blend the extra bit at the end into the start, so it loops smoothly
    n = int(RATE * seconds)
    f = int(RATE * fade)
    for i in range(f):
        mix = i / f
        out[i] = out[i] * mix + out[n + i] * (1 - mix)
    return [s * 0.55 for s in out[:n]]


def melody(notes, step, length=None):
    samples = []
    for name in notes:
        samples += tone(NOTES[name], length or step)
    return samples


SOUNDS = {
    "open": melody(["C5", "E5", "G5"], 0.07),    # entering a mini-game
    "back": melody(["G5", "E5", "C5"], 0.07),    # returning to the room
    "select": tone(NOTES["A5"], 0.05),           # selecting something
    "move": knock(),                             # placing a piece
    "win": melody(["C5", "E5", "G5"], 0.09) + tone(NOTES["C6"], 0.35, release=0.25),
    "lose": melody(["G4", "Eb4"], 0.16) + tone(NOTES["C4"], 0.4, release=0.3),
    "draw": melody(["E5", "D5"], 0.1) + tone(NOTES["E5"], 0.25, release=0.2),
    # the fireplace scene (loops)
    "crackle": crackle(),
    # walking through a door: a soft wooden "tok" and a little chime
    "door": [0.6 * v for v in knock(0.06)] + tone(NOTES["E5"], 0.06) + tone(NOTES["A5"], 0.16, release=0.14),
}


def piano_note(freq, seconds=1.1):
    """A soft, music-box-like piano note: a quick start, then a slow fade.
    A little of the octave above makes it brighter."""
    n = int(RATE * seconds)
    out = []
    for i in range(n):
        t = i / RATE
        env = min(1.0, t / 0.004) * math.exp(-t * 3.2) * min(1.0, (seconds - t) / 0.05)
        wave_ = (0.75 * math.sin(2 * math.pi * freq * t)
                 + 0.2 * math.sin(2 * math.pi * 2 * freq * t)
                 + 0.12 * triangle(freq * t))
        out.append(wave_ * env)
    return out


def piano_sounds():
    """One sound per piano key, named like "piano-Cs4" (see games/piano)."""
    import sys
    sys.path.insert(0, str(OUT.parent.parent))
    from games.piano import logic
    return {logic.sound_name(note): piano_note(logic.frequency(note)) for note in logic.NOTES}


def write(name, samples):
    path = OUT / f"{name}.wav"
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s * VOLUME)) * 32767)) for s in samples))
    return path


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, samples in {**SOUNDS, **piano_sounds()}.items():
        print("wrote", write(name, samples).relative_to(OUT.parent.parent))
