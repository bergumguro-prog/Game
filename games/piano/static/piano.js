// The piano: plays a note when a key is clicked, touched or typed.
// Sounds are loaded once into Web Audio so notes start instantly and can
// overlap like a real piano. They follow the mute button.
(() => {
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  const audio = AudioContext ? new AudioContext() : null;
  const buffers = {}; // note -> decoded sound
  const isMuted = () => (window.scenes ? window.scenes.isMuted() : false);

  function keyFor(note) {
    return document.querySelector(`.piano-key[data-note="${note}"]`);
  }

  function load() {
    if (!audio) return;
    document.querySelectorAll(".piano-key").forEach((key) => {
      const note = key.dataset.note;
      if (buffers[note]) return;
      buffers[note] = "loading";
      fetch(key.dataset.sound)
        .then((r) => r.arrayBuffer())
        .then((bytes) => audio.decodeAudioData(bytes))
        .then((buffer) => { buffers[note] = buffer; })
        .catch(() => { delete buffers[note]; });
    });
  }

  // Light up a key for a moment. `style` is "pressed" (you) or "showing"
  // (the piano playing a tune to you).
  function light(note, style = "pressed", ms = 220) {
    const key = keyFor(note);
    if (!key) return;
    key.classList.add(style);
    setTimeout(() => key.classList.remove(style), ms);
  }

  function sound(note) {
    if (!audio || isMuted()) return;
    if (audio.state === "suspended") audio.resume().catch(() => {});
    const buffer = buffers[note];
    if (!buffer || buffer === "loading") return;
    const source = audio.createBufferSource();
    source.buffer = buffer;
    const volume = audio.createGain();
    volume.gain.value = 0.8;
    source.connect(volume).connect(audio.destination);
    source.start();
  }

  // Everyone who wants to know about notes being played (repeat mode).
  const listeners = [];
  function play(note, { byPlayer = true, style = "pressed", ms } = {}) {
    sound(note);
    light(note, style, ms);
    if (byPlayer) listeners.forEach((fn) => fn(note));
  }

  // --- Input ---
  let enabled = true;
  document.addEventListener("pointerdown", (e) => {
    const key = e.target.closest(".piano-key");
    if (!key || !enabled) return;
    e.preventDefault();
    play(key.dataset.note);
  });

  document.addEventListener("keydown", (e) => {
    if (e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
    const key = document.querySelector(`.piano-key[data-key="${CSS.escape(e.key.toLowerCase())}"]`);
    if (!key || !enabled) return;
    e.preventDefault();
    play(key.dataset.note);
  });

  load();
  document.addEventListener("scene:updated", load);

  // For repeat mode (piano-repeat.js).
  window.piano = {
    play,
    onNote: (fn) => listeners.push(fn),
    setEnabled: (on) => { enabled = on; },
    ready: () => Object.values(buffers).every((b) => b !== "loading"),
  };
})();
