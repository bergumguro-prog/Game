// Player movement and collisions in the room.
// Everything (room size, hitboxes, speed) comes from the HTML, which gets it
// from the room's file in room/rooms/, so nothing is hardcoded here. All values are in
// screen pixels.
(() => {
  const room = document.getElementById("room");
  const player = document.getElementById("player");
  const num = (el, key) => Number(el.dataset[key]);

  const roomW = num(room, "width");
  const roomH = num(room, "height");
  const floorTop = num(room, "floorTop");
  const reach = num(room, "reach");
  const prompt = document.getElementById("prompt");
  const promptText = prompt.querySelector(".prompt-text");

  const speed = num(player, "speed");
  const spriteW = player.offsetWidth;
  const spriteH = num(player, "h");
  // The player's hitbox is only the feet, offset inside the sprite.
  const hit = { x: num(player, "hitX"), y: num(player, "hitY"), w: num(player, "hitW"), h: num(player, "hitH") };
  let x = num(player, "x");
  let y = num(player, "y");

  // Objects that open a mini-game when you press E.
  const interactables = [...room.querySelectorAll(".object[data-url]")].map((el) => ({
    el,
    url: el.dataset.url,
    prompt: el.dataset.prompt,
    x: num(el, "hitX"), y: num(el, "hitY"), w: num(el, "hitW"), h: num(el, "hitH"),
  }));
  let nearest = null;
  let started = false;
  let leaving = false;

  // Doors to other rooms. Walking into one (pressing toward it while the
  // feet are in its doorway) goes to the connected room.
  const exits = [...room.querySelectorAll(".exit")].map((el) => ({
    url: el.dataset.url,
    walk: el.dataset.walk, // "up", "down", "left" or "right"
    x: num(el, "hitX"), y: num(el, "hitY"), w: num(el, "hitW"), h: num(el, "hitH"),
  }));

  // Rectangles the player can't walk through.
  const solids = [...room.querySelectorAll(".object.solid")].map((el) => ({
    x: num(el, "hitX"), y: num(el, "hitY"), w: num(el, "hitW"), h: num(el, "hitH"),
  }));

  const KEY_TO_DIRECTION = {
    arrowup: "up", w: "up",
    arrowdown: "down", s: "down",
    arrowleft: "left", a: "left",
    arrowright: "right", d: "right",
  };
  const held = new Set();

  function leave(url, sound, style) {
    if (leaving) return;
    leaving = true;
    savePosition();
    held.clear();
    player.dataset.moving = "false";
    if (window.scenes) window.scenes.goTo(url, sound, style);
    else window.location.href = url;
  }

  document.addEventListener("keydown", (e) => {
    if (leaving) return;
    if (e.key.toLowerCase() === "e" && nearest && !e.repeat) {
      leave(nearest.url, "open");
      return;
    }
    const dir = KEY_TO_DIRECTION[e.key.toLowerCase()];
    if (!dir) return;
    e.preventDefault(); // stop arrow keys from scrolling the page
    held.add(dir);
  });
  document.addEventListener("keyup", (e) => {
    held.delete(KEY_TO_DIRECTION[e.key.toLowerCase()]);
  });
  // Releasing a key while the window is unfocused would leave it "stuck".
  window.addEventListener("blur", () => held.clear());

  // Would the player's feet overlap a wall or solid object at (px, py)?
  function blocked(px, py) {
    const fx = px + hit.x;
    const fy = py + hit.y;
    if (fx < 0 || fy < floorTop || fx + hit.w > roomW || fy + hit.h > roomH) return true;
    return solids.some(
      (o) => fx < o.x + o.w && fx + hit.w > o.x && fy < o.y + o.h && fy + hit.h > o.y
    );
  }

  // Which interactable object (if any) is within reach of the player's feet?
  function findNearest() {
    const fx = x + hit.x - reach;
    const fy = y + hit.y - reach;
    const fw = hit.w + 2 * reach;
    const fh = hit.h + 2 * reach;
    const cx = x + hit.x + hit.w / 2;
    const cy = y + hit.y + hit.h / 2;
    let best = null;
    let bestDist = Infinity;
    for (const o of interactables) {
      if (fx < o.x + o.w && fx + fw > o.x && fy < o.y + o.h && fy + fh > o.y) {
        const dist = Math.hypot(o.x + o.w / 2 - cx, o.y + o.h / 2 - cy);
        if (dist < bestDist) {
          best = o;
          bestDist = dist;
        }
      }
    }
    return best;
  }

  // Is the player walking into a door right now?
  function findExit() {
    const fx = x + hit.x;
    const fy = y + hit.y;
    return exits.find((d) =>
      held.has(d.walk) &&
      fx < d.x + d.w && fx + hit.w > d.x && fy < d.y + d.h && fy + hit.h > d.y
    );
  }

  function updateNearest() {
    const found = findNearest();
    if (found === nearest) return;
    if (nearest) nearest.el.classList.remove("near");
    nearest = found;
    if (nearest) {
      nearest.el.classList.add("near");
      promptText.textContent = nearest.prompt;
      // little blip, but not for the object you're already next to on page load
      if (window.scenes && started) window.scenes.play("select");
    }
    prompt.hidden = !nearest;
  }

  // Remember where the player stood in this room, so coming back from a game
  // puts them in the same spot. sessionStorage is cleared when the tab is closed.
  const STORAGE_KEY = `room-player:${room.dataset.roomId}`;
  function savePosition() {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ x, y, facing: player.dataset.facing }));
    } catch (err) { /* storage unavailable: just start at the default spot */ }
  }
  function restorePosition() {
    try {
      const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
      if (saved && Number.isFinite(saved.x) && Number.isFinite(saved.y) && !blocked(saved.x, saved.y)) {
        x = saved.x;
        y = saved.y;
        player.dataset.facing = saved.facing || "down";
      }
    } catch (err) { /* ignore broken or missing data */ }
  }

  // Move along one axis. If the full step hits something, creep up to it
  // pixel by pixel so the player ends up touching the obstacle.
  function moveAxis(amount, axis) {
    const step = Math.sign(amount);
    let remaining = Math.abs(amount);
    while (remaining > 0) {
      const d = step * Math.min(1, remaining);
      const nx = axis === "x" ? x + d : x;
      const ny = axis === "y" ? y + d : y;
      if (blocked(nx, ny)) return;
      x = nx;
      y = ny;
      remaining -= 1;
    }
  }

  function draw() {
    player.style.transform = `translate(${Math.round(x)}px, ${Math.round(y)}px)`;
    // Things lower in the room are drawn in front (same rule as z_index in objects.py).
    player.style.zIndex = 1000 + Math.round(y + spriteH);
    // Keep the "Press E" bubble centered above the player's head.
    prompt.style.transform =
      `translate(${Math.round(x + spriteW / 2)}px, ${Math.round(y) - 8}px) translate(-50%, -100%)`;
  }

  let last = performance.now();
  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.05); // cap big jumps after tab switch
    last = now;

    let dx = (held.has("right") ? 1 : 0) - (held.has("left") ? 1 : 0);
    let dy = (held.has("down") ? 1 : 0) - (held.has("up") ? 1 : 0);
    player.dataset.moving = dx || dy ? "true" : "false";

    if (dx || dy) {
      // Same speed diagonally as straight.
      const len = Math.hypot(dx, dy);
      dx /= len;
      dy /= len;
      // X and Y are moved separately, so you slide along walls.
      moveAxis(dx * speed * dt, "x");
      moveAxis(dy * speed * dt, "y");

      if (Math.abs(dx) > Math.abs(dy)) player.dataset.facing = dx > 0 ? "right" : "left";
      else player.dataset.facing = dy > 0 ? "down" : "up";
      draw();
      updateNearest();
      const exit = findExit();
      if (exit) leave(exit.url, "door", "door");
    }
    if (!leaving) requestAnimationFrame(frame);
  }

  // Coming in through a door: the server already put the player in front
  // of it. Otherwise (coming back from a game, or a reload) use the saved spot.
  if (player.dataset.arrived) {
    // Tidy the address bar so a reload doesn't count as coming through the door.
    window.history.replaceState(null, "", window.location.pathname);
  } else {
    restorePosition();
  }
  // Also remember the spot when the tab is reloaded or closed.
  window.addEventListener("pagehide", savePosition);
  draw();
  updateNearest();
  started = true;
  requestAnimationFrame(frame);
})();
