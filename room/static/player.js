// Player movement and collisions in the room.
// Everything (room size, hitboxes, speed) comes from the HTML, which gets it
// from room/objects.py, so nothing is hardcoded here. All values are in
// screen pixels.
(() => {
  const room = document.getElementById("room");
  const player = document.getElementById("player");
  const num = (el, key) => Number(el.dataset[key]);

  const roomW = num(room, "width");
  const roomH = num(room, "height");
  const floorTop = num(room, "floorTop");

  const speed = num(player, "speed");
  const spriteH = num(player, "h");
  // The player's hitbox is only the feet, offset inside the sprite.
  const hit = { x: num(player, "hitX"), y: num(player, "hitY"), w: num(player, "hitW"), h: num(player, "hitH") };
  let x = num(player, "x");
  let y = num(player, "y");

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

  document.addEventListener("keydown", (e) => {
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
    // Things lower in the room are drawn in front (same rule as objects.py).
    player.style.zIndex = 1000 + Math.round(y + spriteH);
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
    }
    requestAnimationFrame(frame);
  }

  draw();
  requestAnimationFrame(frame);
})();
