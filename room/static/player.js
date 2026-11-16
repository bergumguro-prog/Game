// Player movement and collisions in the room.
// The room size, player settings and furniture all come from the HTML
// (which gets them from room/objects.py), so nothing is hardcoded here.
(() => {
  const room = document.getElementById("room");
  const player = document.getElementById("player");

  const roomW = Number(room.dataset.width);
  const roomH = Number(room.dataset.height);
  const size = Number(player.dataset.size);
  const speed = Number(player.dataset.speed);
  let x = Number(player.dataset.x);
  let y = Number(player.dataset.y);

  // Rectangles the player can't walk through.
  const solids = [...room.querySelectorAll(".object.solid")].map((el) => ({
    x: Number(el.dataset.x),
    y: Number(el.dataset.y),
    w: Number(el.dataset.w),
    h: Number(el.dataset.h),
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

  // Would the player overlap a wall or solid object at (px, py)?
  function blocked(px, py) {
    if (px < 0 || py < 0 || px + size > roomW || py + size > roomH) return true;
    return solids.some(
      (o) => px < o.x + o.w && px + size > o.x && py < o.y + o.h && py + size > o.y
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
  }

  let last = performance.now();
  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.05); // cap big jumps after tab switch
    last = now;

    let dx = (held.has("right") ? 1 : 0) - (held.has("left") ? 1 : 0);
    let dy = (held.has("down") ? 1 : 0) - (held.has("up") ? 1 : 0);

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
