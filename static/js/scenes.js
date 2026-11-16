// Switching between scenes, plus sound effects. Loaded on every page.
//
// - scenes.goTo(url, sound): fade the scene out, then go to `url`. The next
//   page fades in and plays `sound` ("open", "back", ...).
// - Links (<a href>) to other scenes use the same fade automatically.
// - In a mini-game, Esc goes back to the room.
// - Any element with data-sound="name" plays that sound when the page loads
//   (games use it for "win", "lose", "move", ...).
// - The sound button in the corner mutes/unmutes; the choice is remembered.
(() => {
  const ENTER_KEY = "scene-enter";
  const MUTE_KEY = "sound-muted";
  const leaveMs = parseFloat(getComputedStyle(document.documentElement)
    .getPropertyValue("--scene-leave-ms")) || 200;

  // sessionStorage/localStorage can be unavailable (private mode etc.).
  const store = {
    get(area, key) { try { return window[area].getItem(key); } catch (e) { return null; } },
    set(area, key, value) { try { window[area].setItem(key, value); } catch (e) { /* ignore */ } },
    remove(area, key) { try { window[area].removeItem(key); } catch (e) { /* ignore */ } },
  };

  let muted = store.get("localStorage", MUTE_KEY) === "1";

  function play(name) {
    if (muted || !name) return;
    const audio = new Audio(`/static/sounds/${name}.wav`);
    // Browsers may block sound until the player has clicked or pressed a key.
    audio.play().catch(() => {});
  }

  let leaving = false;
  function goTo(url, sound) {
    if (leaving) return;
    leaving = true;
    store.set("sessionStorage", ENTER_KEY, sound || "");
    document.body.classList.add("scene-leave");
    setTimeout(() => { window.location.href = url; }, leaveMs);
  }

  // --- Fade in when we arrived through goTo() ---
  const entered = store.get("sessionStorage", ENTER_KEY);
  if (entered !== null) {
    store.remove("sessionStorage", ENTER_KEY);
    document.body.classList.add("scene-enter");
    play(entered);
  }

  // --- Sounds requested by the page itself ---
  document.querySelectorAll("[data-sound]").forEach((el) => play(el.dataset.sound));

  // --- Links to other scenes fade too ---
  document.addEventListener("click", (e) => {
    const link = e.target.closest("a[href]");
    if (!link || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) return;
    if (link.origin !== window.location.origin || link.target) return;
    e.preventDefault();
    const toRoom = link.pathname === "/";
    goTo(link.href, toRoom ? "back" : "open");
  });

  // --- Esc returns to the room ---
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && document.body.dataset.scene !== "room") {
      goTo("/", "back");
    }
  });

  // --- Mute button ---
  const button = document.getElementById("mute-toggle");
  function showMute() {
    if (!button) return;
    button.setAttribute("aria-pressed", String(muted));
    button.textContent = muted ? "Sound: off" : "Sound: on";
  }
  if (button) {
    button.addEventListener("click", () => {
      muted = !muted;
      store.set("localStorage", MUTE_KEY, muted ? "1" : "0");
      showMute();
      play("select");
      button.blur(); // so Space/Enter don't toggle it again by accident
    });
    showMute();
  }

  window.scenes = { goTo, play };
})();
