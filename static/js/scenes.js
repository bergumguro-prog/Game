// Switching between scenes. Loaded on every page.
// In a mini-game, Esc goes back to the room. (The room remembers where the
// player was standing, see room/static/player.js.)
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.body.dataset.scene !== "room") {
    window.location.href = "/";
  }
});
