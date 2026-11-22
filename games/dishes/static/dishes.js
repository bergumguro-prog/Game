// Scrubbing dishes. The sponge follows the pointer over the sink. While the
// mouse button (or a finger) is down, every dirt spot under the sponge loses
// "hp": a little each second while holding still, more while moving. The
// rates come from logic.py through data attributes. When every spot on the
// dish is gone, the page tells the server, which sends the next dish.
(() => {
  const SPONGE_RADIUS = 4; // art pixels around the sponge's middle that scrub

  let stage, sink, sponge, spots, holdRate, dragPixels;
  let scrubbing = false;
  let moved = 0;           // screen pixels moved since the last frame
  let pointer = null;      // last pointer position, relative to the sink
  let done = false;
  let lastFoam = 0;

  function setUp() {
    stage = document.getElementById("dish-stage");
    sink = document.getElementById("sink");
    sponge = document.getElementById("sponge");
    if (!stage || !sink) { spots = []; return; }
    holdRate = Number(sink.dataset.holdRate);
    dragPixels = Number(sink.dataset.dragPixels);
    spots = [...stage.querySelectorAll(".dirt")].map((el) => ({
      el,
      x: Number(el.dataset.x) + 0.5,
      y: Number(el.dataset.y) + 0.5,
      r: Number(el.dataset.r),
      hp: Number(el.dataset.hp),
      max: Number(el.dataset.hp),
    }));
    scrubbing = false;
    done = false;
    pointer = null;
  }

  // Where is the sponge, in the dish's art pixels?
  function spongeOnDish() {
    const box = stage.getBoundingClientRect();
    const sinkBox = sink.getBoundingClientRect();
    const scale = box.width / Number(stage.dataset.artW);
    return {
      x: (sinkBox.left + pointer.x - box.left) / scale,
      y: (sinkBox.top + pointer.y - box.top) / scale,
    };
  }

  function placeSponge() {
    if (!pointer) return;
    sponge.hidden = false;
    sponge.style.transform =
      `translate(${Math.round(pointer.x - 24)}px, ${Math.round(pointer.y - 18)}px)`;
    sponge.classList.toggle("scrubbing", scrubbing);
  }

  function foam() {
    const now = performance.now();
    if (now - lastFoam < 120) return;
    lastFoam = now;
    const bubble = document.createElement("span");
    bubble.className = "foam";
    bubble.style.left = `${Math.round(pointer.x + (Math.random() - 0.5) * 40)}px`;
    bubble.style.top = `${Math.round(pointer.y + (Math.random() - 0.5) * 24)}px`;
    sink.appendChild(bubble);
    setTimeout(() => bubble.remove(), 800);
  }

  function level(spot) {
    return spot.hp <= 0 ? 0 : Math.ceil((spot.hp / spot.max) * 3);
  }

  function dishIsClean() {
    done = true;
    scrubbing = false;
    if (window.scenes) window.scenes.play("select");
    setTimeout(() => {
      const form = document.getElementById("dish-clean");
      if (form) form.requestSubmit(); // the server sends the next dish
    }, 450);
  }

  // --- Pointer input (mouse, pen and touch) ---
  function track(e) {
    if (!sink) return;
    const box = sink.getBoundingClientRect();
    const next = { x: e.clientX - box.left, y: e.clientY - box.top };
    if (pointer && scrubbing) moved += Math.hypot(next.x - pointer.x, next.y - pointer.y);
    pointer = next;
    placeSponge();
  }

  document.addEventListener("pointerdown", (e) => {
    if (!sink || !sink.contains(e.target) || done) return;
    e.preventDefault();
    sink.setPointerCapture(e.pointerId);
    scrubbing = true;
    track(e);
  });
  document.addEventListener("pointermove", (e) => {
    if (sink && (sink.contains(e.target) || scrubbing)) track(e);
  });
  const stop = () => { scrubbing = false; if (sponge) sponge.classList.remove("scrubbing"); };
  document.addEventListener("pointerup", stop);
  document.addEventListener("pointercancel", stop);
  document.addEventListener("pointerleave", (e) => {
    if (sink && e.target === sink && !scrubbing && sponge) sponge.hidden = true;
  }, true);

  // --- Scrubbing, every frame ---
  let last = performance.now();
  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    if (scrubbing && pointer && spots.length && !done) {
      const at = spongeOnDish();
      const amount = dt * holdRate + moved / dragPixels;
      let touching = false;
      for (const spot of spots) {
        if (spot.hp <= 0) continue;
        if (Math.hypot(spot.x - at.x, spot.y - at.y) > spot.r + SPONGE_RADIUS) continue;
        touching = true;
        spot.hp -= amount;
        spot.el.dataset.level = level(spot);
      }
      if (touching) foam();
      if (spots.every((s) => s.hp <= 0)) dishIsClean();
    }
    moved = 0;
    requestAnimationFrame(frame);
  }

  setUp();
  requestAnimationFrame(frame);
  document.addEventListener("scene:updated", setUp);
})();
