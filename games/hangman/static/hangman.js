// Typing a letter presses the matching on-screen key. Input only: the game
// itself runs on the server.
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey || e.repeat) return;
  const letter = e.key.toLowerCase();
  if (!/^[a-z]$/.test(letter)) return;
  const key = document.querySelector(`#hm-keyboard button[value="${letter}"]`);
  if (key && !key.disabled) key.click();
});
