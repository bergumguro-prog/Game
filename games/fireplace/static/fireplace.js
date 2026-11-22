// The fire in the fireplace scene.
//
// The flames are a tiny "heat" grid the size of the fireplace's opening (in
// art pixels). Each step, the bottom row is fed with fresh heat, and every
// pixel takes its heat from the pixel below it (sometimes a little to the
// side) while cooling down a bit. That makes flames that rise, flicker and
// sway without ever repeating, so the scene can run for as long as you like.
// Each heat level is drawn in one flat color from theme.css. A few sparks
// drift up on top.
(() => {
  const hearth = document.getElementById("hearth");
  const canvas = document.getElementById("fire");
  if (!hearth || !canvas) return;

  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const STEP_MS = reduceMotion ? 120 : 55; // how often the fire moves on

  // --- Size: the biggest whole-number scale that fits the window ---
  const frameW = Number(hearth.dataset.frameW);
  const frameH = Number(hearth.dataset.frameH);
  function fit() {
    const room = 140; // space for the buttons below
    const scale = Math.max(1, Math.floor(Math.min(
      (window.innerWidth - 32) / frameW,
      (window.innerHeight - room) / frameH,
    )));
    hearth.style.setProperty("--scale", scale);
  }
  window.addEventListener("resize", fit);
  fit();

  // --- Colors from theme.css ---
  const theme = getComputedStyle(document.documentElement);
  function color(name) {
    const hex = theme.getPropertyValue(name).trim().replace("#", "");
    const full = hex.length === 3 ? hex.split("").map((c) => c + c).join("") : hex;
    const n = parseInt(full, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  // Coolest to hottest. Index 0 is "no flame": the dark inside shows.
  const FLAME = [null, "--px-cherry", "--px-fire", "--px-yellow", "--px-white"].map(
    (name) => name && color(name));
  const LEVELS = [4, 11, 19, 27]; // heat needed for flame colors 1..4
  const MAX_HEAT = 32;
  const inside = color("--fireplace-inside");
  const insideLine = color("--fireplace-inside-line");
  const sparkHot = color("--px-yellow");
  const sparkCool = color("--px-fire");

  function flameColor(heat) {
    let level = 0;
    while (level < LEVELS.length && heat >= LEVELS[level]) level += 1;
    return FLAME[level];
  }

  // The dark brick back wall of the fireplace, drawn behind the flames.
  function backWall(x, y) {
    const row = Math.floor(y / 3);
    const brickEdge = y % 3 === 2 || (x + (row % 2) * 3) % 6 === 5;
    return brickEdge ? insideLine : inside;
  }

  // --- The heat grid ---
  const heat = new Uint8Array(W * H);
  // Each column of the bottom row has its own slowly wandering strength,
  // which makes separate flame tongues that grow and shrink.
  const feed = Array.from({ length: W }, () => Math.random());

  function feedBottom() {
    const y = H - 1;
    for (let x = 0; x < W; x++) {
      feed[x] = Math.min(1, Math.max(0, feed[x] + (Math.random() - 0.5) * 0.35));
      // hotter in the middle, where the logs are
      const middle = 1 - Math.abs(x - (W - 1) / 2) / (W / 2);
      const strength = Math.max(0, middle * 1.9 - 0.25) * (0.6 + 0.4 * feed[x]);
      heat[y * W + x] = Math.round(Math.min(1, strength) * MAX_HEAT);
    }
  }

  let sway = 0;
  function rise() {
    sway += 0.05;
    const wind = Math.sin(sway) * 0.35; // a slow side-to-side lean
    // Each pixel pulls from below (not pushes up), so no side wins by
    // being written last and the flames don't drift one way.
    for (let y = 0; y < H - 1; y++) {
      for (let x = 0; x < W; x++) {
        const r = Math.random();
        const drift = Math.round((Math.random() - 0.5) * 1.6 - wind * Math.random());
        const sx = Math.min(W - 1, Math.max(0, x + drift));
        const cool = r < 0.3 ? 0 : r < 0.78 ? 1 : 2;
        heat[y * W + x] = Math.max(0, heat[(y + 1) * W + sx] - cool);
      }
    }
  }

  // --- Sparks ---
  const sparks = [];
  function maybeAddSpark() {
    if (reduceMotion || sparks.length > 6 || Math.random() > 0.12) return;
    sparks.push({
      x: W / 2 + (Math.random() - 0.5) * W * 0.5,
      y: H - 8 - Math.random() * 6,
      vx: (Math.random() - 0.5) * 0.25,
      vy: -(0.35 + Math.random() * 0.35),
      life: 1,
      fade: 0.012 + Math.random() * 0.015,
      wobble: Math.random() * 6,
    });
  }
  function moveSparks() {
    for (const s of sparks) {
      s.wobble += 0.3;
      s.x += s.vx + Math.sin(s.wobble) * 0.15;
      s.y += s.vy;
      s.life -= s.fade;
    }
    for (let i = sparks.length - 1; i >= 0; i--) {
      if (sparks[i].life <= 0 || sparks[i].y < 0) sparks.splice(i, 1);
    }
  }

  // --- Drawing ---
  const image = ctx.createImageData(W, H);
  function draw() {
    const px = image.data;
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const c = flameColor(heat[y * W + x]) || backWall(x, y);
        const i = (y * W + x) * 4;
        px[i] = c[0];
        px[i + 1] = c[1];
        px[i + 2] = c[2];
        px[i + 3] = 255;
      }
    }
    for (const s of sparks) {
      // sparks blink out at the end of their life
      if (s.life < 0.25 && Math.random() < 0.5) continue;
      const x = Math.round(s.x);
      const y = Math.round(s.y);
      if (x < 0 || x >= W || y < 0 || y >= H) continue;
      const c = s.life > 0.5 ? sparkHot : sparkCool;
      const i = (y * W + x) * 4;
      px[i] = c[0];
      px[i + 1] = c[1];
      px[i + 2] = c[2];
    }
    ctx.putImageData(image, 0, 0);
  }

  // The warm light follows how big the fire is, in a few flat steps.
  function updateGlow() {
    let total = 0;
    for (let i = 0; i < W * H; i++) total += heat[i];
    const level = Math.min(3, Math.floor((total / (W * H * MAX_HEAT)) * 12));
    hearth.style.setProperty("--glow", level / 3);
  }

  function step() {
    feedBottom();
    rise();
    maybeAddSpark();
    moveSparks();
    draw();
  }

  // Let the fire build up before the first picture, so it doesn't start cold.
  for (let i = 0; i < H * 2; i++) step();

  let last = 0;
  let steps = 0;
  function frame(now) {
    if (now - last >= STEP_MS) {
      last = now;
      step();
      steps += 1;
      if (steps % 8 === 0) updateGlow();
    }
    requestAnimationFrame(frame); // the browser pauses this in hidden tabs
  }
  requestAnimationFrame(frame);

  // --- Crackling sound ---
  // Web Audio loops the sound with no gap. It follows the mute button, and
  // browsers may only allow sound after a click or key press, so it also
  // tries again then.
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  if (!AudioContext) return;
  const audio = new AudioContext();
  const volume = audio.createGain();
  volume.connect(audio.destination);
  const isMuted = () => (window.scenes ? window.scenes.isMuted() : false);

  function applyMute() {
    volume.gain.value = isMuted() ? 0 : 0.9;
    if (!isMuted() && audio.state === "suspended") audio.resume().catch(() => {});
  }
  fetch("/static/sounds/crackle.wav")
    .then((response) => response.arrayBuffer())
    .then((bytes) => audio.decodeAudioData(bytes))
    .then((buffer) => {
      const source = audio.createBufferSource();
      source.buffer = buffer;
      source.loop = true;
      source.connect(volume);
      source.start();
      applyMute();
    })
    .catch(() => { /* no sound: the fire still burns */ });

  document.addEventListener("sound:toggle", applyMute);
  ["keydown", "pointerdown"].forEach((type) =>
    document.addEventListener(type, applyMute, { once: true }));
  // Stop crackling when leaving the page.
  window.addEventListener("pagehide", () => audio.close().catch(() => {}));
})();
