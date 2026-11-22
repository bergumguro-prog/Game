// "Repeat the tune": the piano plays the tune (keys light up mint), then
// listens while you play it back. A wrong note or the last right note sends
// what you played to the server, which decides if it was right.
(() => {
  if (!window.piano) return;
  const GAP_MS = 520; // time between notes when the piano plays

  let expected = [];  // the tune for this round
  let played = [];    // what you've played so far
  let listening = false;
  let timers = [];

  function status(text) {
    const el = document.getElementById("piano-status");
    if (el) el.textContent = text;
  }

  function setListening(on) {
    listening = on;
    window.piano.setEnabled(on);
    const keys = document.getElementById("piano-keys");
    if (keys) keys.classList.toggle("listening", !on);
    const again = document.getElementById("listen-again");
    if (again) again.disabled = !on;
  }

  function playTune() {
    timers.forEach(clearTimeout);
    timers = [];
    played = [];
    setListening(false);
    expected.forEach((note, i) => {
      timers.push(setTimeout(() => {
        window.piano.play(note, { byPlayer: false, style: "showing", ms: GAP_MS - 140 });
      }, 400 + i * GAP_MS));
    });
    timers.push(setTimeout(() => {
      setListening(true);
      status(`Your turn! (0/${expected.length})`);
    }, 400 + expected.length * GAP_MS));
  }

  function send() {
    setListening(false);
    window.piano.setEnabled(false);
    const form = document.getElementById("repeat-answer");
    if (!form) return;
    form.querySelector('[name="notes"]').value = played.join(",");
    // a short pause so the last note can be heard before the answer
    setTimeout(() => form.requestSubmit(), 350);
  }

  window.piano.onNote((note) => {
    if (!listening || !expected.length) return;
    played.push(note);
    const i = played.length - 1;
    if (note !== expected[i] || played.length === expected.length) {
      send(); // wrong note, or the whole tune: let the server judge
    } else {
      status(`Your turn! (${played.length}/${expected.length})`);
    }
  });

  function setUp() {
    timers.forEach(clearTimeout);
    timers = [];
    const tune = document.getElementById("tune");
    expected = tune ? tune.dataset.notes.split(",") : [];
    if (!expected.length) {
      listening = false;
      window.piano.setEnabled(true); // free play, or between games
      return;
    }
    const again = document.getElementById("listen-again");
    if (again) again.addEventListener("click", () => { status("Listen…"); playTune(); });
    playTune();
  }

  setUp();
  document.addEventListener("scene:updated", setUp);
})();
